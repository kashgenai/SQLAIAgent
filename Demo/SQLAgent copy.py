"""
SQLAgent.py - Text-to-SQL Agent with RAG Integration
Converted from texttosql3.ipynb
"""

from dotenv import load_dotenv
import os
import faiss
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.prompts.chat import SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.agents import create_sql_agent
from langchain_community.utilities import SQLDatabase

def load_environment():
    """Load environment variables"""
    load_dotenv()

def setup_vector_store():
    """Setup FAISS vector store with schema documents"""
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    index = faiss.IndexFlatL2(1536)
    
    vector_store = FAISS(
        embedding_function=embeddings,
        index=index,
        docstore=InMemoryDocstore(),
        index_to_docstore_id={}
    )
    
    # Load schema text
    with open("SchemaText.txt", "r") as f:
        text = f.read()
    
    # Split by table
    chunks = text.strip().split("\n\n")  # one per table
    vector_store.add_texts(chunks)
    
    return vector_store

def load_schema_documents():
    """Load and split schema documents"""
    filepath = "SchemaText.txt"
    loader = TextLoader(filepath)
    pages = loader.load()
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,  # hyperparameter
        chunk_overlap=50  # hyperparameter
    )
    
    split_docs = splitter.split_documents(pages)
    return split_docs

def setup_retriever(vector_store):
    """Setup document retriever"""
    retriever = vector_store.as_retriever(
        search_kwargs={"k": 10}  # hyperparameter
    )
    return retriever

def setup_llm():
    """Setup the language model"""
    model = ChatGoogleGenerativeAI(model='gemini-1.5-flash')
    return model

def create_sql_prompt():
    """Create SQL generation prompt template"""
    sql_chat_prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(
            "You are a helpful AI assistant that generates SQL queries based on user questions and a database schema."
        ),
        HumanMessagePromptTemplate.from_template("""
You will receive:
1. A database schema
2. A user question

Use the schema to generate a valid SQL query that answers the question.

### Format Instructions:
- Only return the SQL query. Do NOT include explanations or preambles.
- Format the SQL using proper line breaks and indentation.
- Use table aliases where appropriate.
- Use ANSI SQL syntax.
- If the schema is insufficient to answer the question, respond with: `-- Cannot answer with the given schema.`

### Schema:
{context}

### Question:
{question}

### SQL:
""")
    ])
    return sql_chat_prompt

def create_rag_chain(retriever, sql_prompt, model):
    """Create RAG chain for SQL generation"""
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)
    
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | sql_prompt
        | model
        | StrOutputParser()
    )
    
    return rag_chain

def setup_database():
    """Setup SQLite database connection"""
    db_path = "my_database.db"
    if os.path.exists(db_path):
        print(f"Database exists at: {os.path.abspath(db_path)}")
    else:
        print("Database will be created")
    
    db = SQLDatabase.from_uri("sqlite:///my_database.db")
    print(f"Database tables: {db.get_table_names()}")
    return db

def setup_sql_agent(db, llm):
    """Setup SQL agent with database"""
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    
    agent_executor = create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        verbose=True,
        agent_type="openai-tools"
    )
    
    return agent_executor

def create_table_formatter():
    """Create table formatting chain"""
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
    
    table_prompt = PromptTemplate(
        input_variables=["sql_result"],
        template="Format this SQL result as a table with column headers: {sql_result}"
    )
    
    table_formatter = table_prompt | llm | StrOutputParser()
    return table_formatter

def format_agent_response(response, question):
    """Format agent response as table"""
    table_formatter = create_table_formatter()
    formatted_table = table_formatter.invoke({"sql_result": response['output']})
    return formatted_table

def query_with_rag(rag_chain, question):
    """Query using RAG chain for SQL generation"""
    response = rag_chain.invoke(question)
    return response

def query_with_sql_agent(agent_executor, question):
    """Query using SQL agent directly"""
    response = agent_executor.invoke({"input": question})
    return response

def query_with_rag_enhanced_sql(rag_chain, agent_executor, question):
    """Query using RAG-enhanced SQL agent"""
    # Get schema context from RAG
    schema_context = rag_chain.invoke(f"Database schema for: {question}")
    
    # Create enhanced prompt with context
    enhanced_question = f"""
Schema Context: {schema_context}
        
Question: {question}
        
Please use the schema context above to write the correct SQL query.
"""
    
    # Execute with SQL agent
    response = agent_executor.invoke({"input": enhanced_question})
    return response

def main(question3=None):
    """Main function to demonstrate the SQL Agent"""
    print("🚀 Initializing SQL Agent...")
    
    # Load environment
    load_environment()
    
    # Setup components
    vector_store = setup_vector_store()
    split_docs = load_schema_documents()
    retriever = setup_retriever(vector_store)
    llm = setup_llm()
    sql_prompt = create_sql_prompt()
    rag_chain = create_rag_chain(retriever, sql_prompt, llm)
    db = setup_database()
    agent_executor = setup_sql_agent(db, llm)
    
    print("✅ SQL Agent initialized successfully!")
    
    # Example queries
    print("\n" + "="*60)
    print("📋 EXAMPLE QUERIES")
    print("="*60)
    
    # Example 1: RAG-only query
    print("\n1. RAG-only SQL generation:")
    question1 = "how many customers are available with active offers that are loaded today"
    response1 = query_with_rag(rag_chain, question1)
    print(f"Question: {question1}")
    print(f"Generated SQL: {response1}")
    
    # Example 2: Direct SQL agent query
    print("\n2. Direct SQL agent query:")
    question2 = "Show all customers with all offers expired and expired date as well."
    response2 = query_with_sql_agent(agent_executor, question2)
    print(f"Question: {question2}")
    print(f"Response: {response2['output']}")
    
    # Example 3: RAG-enhanced SQL agent query
    print("\n3. RAG-enhanced SQL agent query:")
    if question3 is None:
        question3 = "show all customers with firstnames and associated offer details"
    response3 = query_with_rag_enhanced_sql(rag_chain, agent_executor, question3)
    print(f"Question: {question3}")
    print(f"Response: {response3['output']}")
    
    # Example 4: Formatted table output
    print("\n4. Formatted table output:")
    formatted_table = format_agent_response(response3, question3)
    print(formatted_table)
    
    return {
        'rag_chain': rag_chain,
        'agent_executor': agent_executor,
        'db': db,
        'llm': llm
    }

if __name__ == "__main__":
    # Example 1: Run with default question 3
    print("Running with default question 3...")
    components = main()
    
    # Example 2: Run with custom question 3
    print("\n" + "="*60)
    print("Running with custom question 3...")
    custom_question = "show all products with their prices and available offers"
    components = main(question3=custom_question)
    
    # Interactive mode
    print("\n" + "="*60)
    print("🎯 INTERACTIVE MODE")
    print("="*60)
    print("You can now use the components:")
    print("- components['rag_chain']: For RAG-based SQL generation")
    print("- components['agent_executor']: For direct SQL queries")
    print("- components['db']: For database operations")
    print("- components['llm']: For language model operations")
    
    # Example usage
    print("\nExample usage:")
    print("response = components['agent_executor'].invoke({'input': 'Show all customers'})")
    print("formatted = format_agent_response(response, 'Show all customers')")
    print("print(formatted)")
    
    print("\nTo run with a custom question 3:")
    print("components = main(question3='your custom question here')") 