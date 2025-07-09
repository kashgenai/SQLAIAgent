from dotenv import load_dotenv
import os
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.agents import create_sql_agent
from langchain_community.utilities import SQLDatabase
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
import faiss

load_dotenv()

# 1. Setup RAG Chain
def setup_rag_chain():
    """Setup RAG chain with schema context"""
    # Load schema document
    from langchain_community.document_loaders import TextLoader
    loader = TextLoader("SchemaDDL.txt")
    pages = loader.load()
    
    # Split documents
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    split_docs = splitter.split_documents(pages)
    
    # Create vector store
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    index = faiss.IndexFlatL2(1536)
    
    vector_store = FAISS(
        embedding_function=embeddings,
        index=index,
        docstore=InMemoryDocstore(),
        index_to_docstore_id={}
    )
    
    # Add documents to vector store
    vector_store.add_documents(split_docs)
    
    # Create RAG chain
    retriever = vector_store.as_retriever(search_kwargs={"k": 5})
    prompt = hub.pull("rlm/rag-prompt")
    
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)
    
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | ChatGoogleGenerativeAI(model='gemini-1.5-flash')
        | StrOutputParser()
    )
    
    return rag_chain

# 2. Setup SQL Agent
def setup_sql_agent():
    """Setup SQL agent with database"""
    db = SQLDatabase.from_uri("sqlite:///my_database.db")
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
    
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    agent_executor = create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        verbose=True,
        agent_type="openai-tools"
    )
    
    return agent_executor, db

# 3. Combined Agent with RAG Context
def create_enhanced_agent():
    """Create agent that uses RAG for context and SQL for queries"""
    rag_chain = setup_rag_chain()
    sql_agent, db = setup_sql_agent()
    
    def enhanced_agent(question):
        # Get schema context from RAG
        schema_context = rag_chain.invoke(f"Database schema for: {question}")
        
        # Create enhanced prompt with context
        enhanced_question = f"""
        Schema Context: {schema_context}
        
        Question: {question}
        
        Please use the schema context above to write the correct SQL query.
        """
        
        # Execute with SQL agent
        response = sql_agent.invoke({"input": enhanced_question})
        return response
    
    return enhanced_agent

# 4. Usage Example
if __name__ == "__main__":
    print("🚀 Setting up Enhanced RAG + SQL Agent...")
    
    # Create the enhanced agent
    agent = create_enhanced_agent()
    
    # Test the agent
    question = "Show all customers with all offers today."
    print(f"\n❓ Question: {question}")
    
    response = agent(question)
    print(f"\n✅ Response: {response}") 