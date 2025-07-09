# RAG + SQL Agent Integration for Notebook

from langchain_google_genai import ChatGoogleGenerativeAI

# 1. Setup RAG Chain (add this to your notebook)
def setup_rag_for_sql():
    """Setup RAG chain that provides schema context to SQL agent"""
    
    # Load and process schema
    from langchain_community.document_loaders import TextLoader
    loader = TextLoader("SchemaDDL.txt")
    pages = loader.load()
    
    # Split documents
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    split_docs = splitter.split_documents(pages)
    
    # Create vector store
    from langchain_openai import OpenAIEmbeddings
    from langchain_community.vectorstores import FAISS
    from langchain_community.docstore.in_memory import InMemoryDocstore
    import faiss
    
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    index = faiss.IndexFlatL2(1536)
    
    vector_store = FAISS(
        embedding_function=embeddings,
        index=index,
        docstore=InMemoryDocstore(),
        index_to_docstore_id={}
    )
    
    vector_store.add_documents(split_docs)
    
    # Create RAG chain
    from langchain import hub
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.runnables import RunnablePassthrough
    
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

# 2. Enhanced SQL Agent with RAG Context
def create_rag_enhanced_sql_agent():
    """Create SQL agent enhanced with RAG context"""
    
    # Setup RAG
    rag_chain = setup_rag_for_sql()
    
    # Setup SQL Agent
    from langchain.agents.agent_toolkits import SQLDatabaseToolkit
    from langchain.agents import create_sql_agent
    from langchain_community.utilities import SQLDatabase
    
    db = SQLDatabase.from_uri("sqlite:///my_database.db")
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
    
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    agent_executor = create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        verbose=True,
        agent_type="openai-tools"
    )
    
    def enhanced_agent(question):
        """Agent that uses RAG for schema context before SQL execution"""
        # Get relevant schema context
        schema_context = rag_chain.invoke(f"Database schema information for: {question}")
        
        # Create enhanced prompt
        enhanced_prompt = f"""
        Database Schema Context:
        {schema_context}
        
        User Question: {question}
        
        Please use the schema context above to understand the database structure and write the correct SQL query.
        """
        
        # Execute with SQL agent
        return agent_executor.invoke({"input": enhanced_prompt})
    
    return enhanced_agent

# 3. Usage in Notebook
# Add this to your notebook:

# # Setup the enhanced agent
# enhanced_agent = create_rag_enhanced_sql_agent()

# # Use the agent
# response = enhanced_agent("Show all customers with all offers today.")
# print(response) 