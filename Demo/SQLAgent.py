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
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.utilities import SQLDatabase
import pandas as pd
from tabulate import tabulate

# --- GLOBAL INITIALIZATION (run once) ---
load_dotenv()

# Setup vector store and retriever (RAG)
SCHEMA_FILE = "SchemaDDL.txt" if os.path.exists("SchemaDDL.txt") else "SchemaText.txt"
if os.path.exists(SCHEMA_FILE):
    loader = TextLoader(SCHEMA_FILE)
    pages = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    split_docs = splitter.split_documents(pages)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    index = faiss.IndexFlatL2(1536)
    vector_store = FAISS(
        embedding_function=embeddings,
        index=index,
        docstore=InMemoryDocstore(),
        index_to_docstore_id={}
    )
    vector_store.add_documents(split_docs)
    retriever = vector_store.as_retriever(search_kwargs={"k": 10})
else:
    retriever = None

# Setup LLM, DB, SQL Agent
llm = ChatGoogleGenerativeAI(model='gemini-1.5-flash', temperature=0)
db = SQLDatabase.from_uri("sqlite:///my_database.db")
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
agent_executor = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    agent_type="openai-tools"
)

# Setup RAG chain
if retriever is not None:
    sql_prompt = hub.pull("rlm/rag-prompt")
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | sql_prompt
        | llm
        | StrOutputParser()
    )
else:
    rag_chain = None

# --- END GLOBAL INITIALIZATION ---

def setup_sql_agent(db, llm):
    """Setup SQL agent with database (kept for compatibility, but uses global agent_executor)"""
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
    """Format agent response as table (original version)"""
    table_formatter = create_table_formatter()
    formatted_table = table_formatter.invoke({"sql_result": response['output']})
    return formatted_table

def query_with_rag(rag_chain_arg, question):
    """Query using RAG chain for SQL generation (uses global rag_chain if arg is None)"""
    chain = rag_chain_arg if rag_chain_arg is not None else rag_chain
    if chain is None:
        return {"error": "RAG chain not initialized"}
    response = chain.invoke(question)
    return response

def query_with_sql_agent(agent_executor_arg, question):
    """Query using SQL agent directly (uses global agent_executor if arg is None)"""
    agent = agent_executor_arg if agent_executor_arg is not None else agent_executor
    response = agent.invoke({"input": question})
    return response

def query_with_rag_enhanced_sql(rag_chain_arg, agent_executor_arg, question):
    """Query using RAG-enhanced SQL agent (uses global objects if args are None)"""
    chain = rag_chain_arg if rag_chain_arg is not None else rag_chain
    agent = agent_executor_arg if agent_executor_arg is not None else agent_executor
    if chain is None:
        return {"error": "RAG chain not initialized"}
    schema_context = chain.invoke(f"Database schema for: {question}")
    enhanced_question = f"""
Schema Context: {schema_context}

Question: {question}

Please use the schema context above to write the correct SQL query.
"""
    response = agent.invoke({"input": enhanced_question})
    return response

def main(question3=None):
    """Main function to demonstrate the SQL Agent (uses global objects for speed)"""
    print("🚀 Initializing SQL Agent (fast global mode)...")
    print(f"Database tables: {db.get_usable_table_names()}")
    print("✅ SQL Agent initialized successfully!")
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
    print("Running with default question 3...")
    components = main()
    print("\n" + "="*60)
    print("Running with custom question 3...")
    custom_question = "show all products with their prices and available offers"
    components = main(question3=custom_question)
    print("\n" + "="*60)
    print("🎯 INTERACTIVE MODE")
    print("="*60)
    print("You can now use the components:")
    print("- components['rag_chain']: For RAG-based SQL generation")
    print("- components['agent_executor']: For direct SQL queries")
    print("- components['db']: For database operations")
    print("- components['llm']: For language model operations")
    print("\nExample usage:")
    print("response = components['agent_executor'].invoke({'input': 'Show all customers'})")
    print("formatted = format_agent_response(response, 'Show all customers')")
    print("print(formatted)")
    print("\nTo run with a custom question 3:")
    print("components = main(question3='your custom question here')") 