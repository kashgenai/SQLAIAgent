#!/usr/bin/env python3
"""
SQLMultiAgent.py - Multi-Agent SQL System using LangGraph
End-to-end implementation with specialized agents for different tasks
"""

import os
import sys
from typing import TypedDict, Annotated, List, Dict, Any, Optional
from dotenv import load_dotenv
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
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.utilities import SQLDatabase
from langgraph.graph import StateGraph  # type: ignore
import json
from datetime import datetime

# Load environment variables
load_dotenv()

class AgentState(TypedDict):
    """State for the multi-agent workflow"""
    question: str
    schema_context: Optional[str]
    sql_query: Optional[str]
    optimized_sql: Optional[str]
    results: Optional[Any]  # Changed from List to Any to handle both list and string
    formatted_output: Optional[str]
    error: Optional[str]
    agent_logs: List[Dict[str, Any]]
    execution_time: Optional[float]
    confidence_score: Optional[float]

def print_flow_step(step_name: str, state: AgentState, details: str = ""):
    """Print the current flow step with visual indicators"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"\n{'='*60}")
    print(f"🔄 [{timestamp}] {step_name}")
    print(f"{'='*60}")
    
    if details:
        print(f"📝 Details: {details}")
    
    # Print current state summary
    state_summary = {}
    for key, value in state.items():
        if key != 'agent_logs' and value is not None:
            if isinstance(value, str) and len(value) > 100:
                state_summary[key] = value[:100] + "..."
            else:
                state_summary[key] = value
    
    print(f"📊 State: {json.dumps(state_summary, indent=2, default=str)}")
    
    # Log the step
    state["agent_logs"].append({
        "timestamp": timestamp,
        "step": step_name,
        "details": details,
        "state_summary": state_summary
    })

def setup_environment():
    """Setup environment and load dependencies"""
    # Create a minimal state for environment setup
    env_state = AgentState(
        question="",
        schema_context=None,
        sql_query=None,
        optimized_sql=None,
        results=None,
        formatted_output=None,
        error=None,
        agent_logs=[],
        execution_time=None,
        confidence_score=None
    )
    print_flow_step("ENVIRONMENT_SETUP", env_state, "Initializing environment and dependencies")
    
    # Setup vector store
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
    
    chunks = text.strip().split("\n\n")
    vector_store.add_texts(chunks)
    
    # Setup retriever
    retriever = vector_store.as_retriever(search_kwargs={"k": 10})
    
    # Setup LLM
    llm = ChatGoogleGenerativeAI(model='gemini-1.5-flash', temperature=0)
    
    # Setup database
    db = SQLDatabase.from_uri("sqlite:///my_database.db")
    
    # Setup SQL agent
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    agent_executor = create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        verbose=False,
        agent_type="openai-tools"
    )
    
    return {
        "retriever": retriever,
        "llm": llm,
        "db": db,
        "agent_executor": agent_executor
    }

def schema_analyzer_agent(state: AgentState) -> AgentState:
    """Agent 1: Schema Analysis Agent - Analyzes the question and retrieves relevant schema context"""
    print_flow_step("SCHEMA_ANALYZER", state, "Analyzing question and retrieving schema context")
    
    try:
        components = setup_environment()
        retriever = components["retriever"]
        
        # Get schema context using RAG
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)
        
        schema_context = format_docs(retriever.get_relevant_documents(state["question"]))
        
        state["schema_context"] = schema_context
        print_flow_step("SCHEMA_ANALYZER_COMPLETE", state, f"Retrieved {len(schema_context)} characters of schema context")
        
    except Exception as e:
        state["error"] = f"Schema analysis failed: {str(e)}"
        print_flow_step("SCHEMA_ANALYZER_ERROR", state, f"Error: {str(e)}")
    
    return state

def sql_generator_agent(state: AgentState) -> AgentState:
    """Agent 2: SQL Generation Agent - Generates SQL query based on question and schema context"""
    print_flow_step("SQL_GENERATOR", state, "Generating SQL query from question and schema context")
    
    try:
        components = setup_environment()
        llm = components["llm"]
        
        # Create SQL generation prompt
        sql_prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                "You are an expert SQL generator. Generate valid SQL queries based on the question and schema context."
            ),
            HumanMessagePromptTemplate.from_template("""
Schema Context:
{schema_context}

Question: {question}

Generate a valid SQL query that answers this question. Only return the SQL query, no explanations.
""")
        ])
        
        # Generate SQL
        sql_chain = sql_prompt | llm | StrOutputParser()
        sql_query = sql_chain.invoke({
            "schema_context": state.get("schema_context", ""),
            "question": state["question"]
        })
        
        # Clean up the SQL query (remove markdown if present)
        if sql_query.startswith("```sql"):
            sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
        
        state["sql_query"] = sql_query
        print_flow_step("SQL_GENERATOR_COMPLETE", state, f"Generated SQL: {sql_query[:100]}...")
        
    except Exception as e:
        state["error"] = f"SQL generation failed: {str(e)}"
        print_flow_step("SQL_GENERATOR_ERROR", state, f"Error: {str(e)}")
    
    return state

def query_validator_agent(state: AgentState) -> AgentState:
    """Agent 3: Query Validator Agent - Validates and optimizes the SQL query"""
    print_flow_step("QUERY_VALIDATOR", state, "Validating and optimizing SQL query")
    
    try:
        components = setup_environment()
        llm = components["llm"]
        
        # Create validation prompt
        validation_prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                "You are an SQL query validator and optimizer. Review the SQL query and provide improvements."
            ),
            HumanMessagePromptTemplate.from_template("""
Schema Context:
{schema_context}

Original SQL Query:
{sql_query}

Please:
1. Validate the SQL syntax
2. Suggest optimizations
3. Return the optimized query

Return only the optimized SQL query, no explanations.
""")
        ])
        
        # Validate and optimize
        validation_chain = validation_prompt | llm | StrOutputParser()
        optimized_sql = validation_chain.invoke({
            "schema_context": state.get("schema_context", ""),
            "sql_query": state.get("sql_query", "")
        })
        
        # Clean up the optimized SQL
        if optimized_sql.startswith("```sql"):
            optimized_sql = optimized_sql.replace("```sql", "").replace("```", "").strip()
        
        state["optimized_sql"] = optimized_sql
        print_flow_step("QUERY_VALIDATOR_COMPLETE", state, f"Optimized SQL: {optimized_sql[:100]}...")
        
    except Exception as e:
        state["error"] = f"Query validation failed: {str(e)}"
        print_flow_step("QUERY_VALIDATOR_ERROR", state, f"Error: {str(e)}")
    
    return state

def query_executor_agent(state: AgentState) -> AgentState:
    """Agent 4: Query Executor Agent - Executes the SQL query and handles errors"""
    print_flow_step("QUERY_EXECUTOR", state, "Executing SQL query on database")
    
    try:
        components = setup_environment()
        agent_executor = components["agent_executor"]
        
        # Use the optimized SQL if available, otherwise use the original
        sql_to_execute = state.get("optimized_sql") or state.get("sql_query")
        
        if not sql_to_execute:
            raise ValueError("No SQL query available for execution")
        
        # Execute the query
        response = agent_executor.invoke({"input": f"Execute this SQL query: {sql_to_execute}"})
        
        # Extract results from the response
        if "output" in response:
            state["results"] = response["output"]
        else:
            state["results"] = str(response)
        
        print_flow_step("QUERY_EXECUTOR_COMPLETE", state, f"Query executed successfully")
        
    except Exception as e:
        state["error"] = f"Query execution failed: {str(e)}"
        print_flow_step("QUERY_EXECUTOR_ERROR", state, f"Error: {str(e)}")
    
    return state

def result_formatter_agent(state: AgentState) -> AgentState:
    """Agent 5: Result Formatter Agent - Formats the results into a readable table"""
    print_flow_step("RESULT_FORMATTER", state, "Formatting results into readable table")
    
    try:
        components = setup_environment()
        llm = components["llm"]
        
        # Create formatting prompt
        format_prompt = PromptTemplate(
            input_variables=["question", "results"],
            template="""
Question: {question}

Results: {results}

Please format these results as a well-structured table with proper column headers and alignment.
Use markdown table format.
"""
        )
        
        # Format results
        format_chain = format_prompt | llm | StrOutputParser()
        formatted_output = format_chain.invoke({
            "question": state["question"],
            "results": state.get("results", "")
        })
        
        state["formatted_output"] = formatted_output
        print_flow_step("RESULT_FORMATTER_COMPLETE", state, "Results formatted successfully")
        
    except Exception as e:
        state["error"] = f"Result formatting failed: {str(e)}"
        print_flow_step("RESULT_FORMATTER_ERROR", state, f"Error: {str(e)}")
    
    return state

def quality_assessor_agent(state: AgentState) -> AgentState:
    """Agent 6: Quality Assessor Agent - Assesses the quality and confidence of the results"""
    print_flow_step("QUALITY_ASSESSOR", state, "Assessing result quality and confidence")
    
    try:
        components = setup_environment()
        llm = components["llm"]
        
        # Create quality assessment prompt
        quality_prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                "You are a quality assessor. Evaluate the SQL query and results for accuracy and completeness."
            ),
            HumanMessagePromptTemplate.from_template("""
Question: {question}
SQL Query: {sql_query}
Results: {results}

Rate the confidence level (0-100) and provide a brief assessment.
Return only a JSON object with 'confidence_score' and 'assessment'.
""")
        ])
        
        # Assess quality
        quality_chain = quality_prompt | llm | StrOutputParser()
        assessment = quality_chain.invoke({
            "question": state["question"],
            "sql_query": state.get("optimized_sql") or state.get("sql_query", ""),
            "results": state.get("results", "")
        })
        
        # Parse the assessment
        try:
            assessment_data = json.loads(assessment)
            state["confidence_score"] = assessment_data.get("confidence_score", 50)
        except:
            state["confidence_score"] = 75  # Default confidence
        
        print_flow_step("QUALITY_ASSESSOR_COMPLETE", state, f"Confidence score: {state['confidence_score']}")
        
    except Exception as e:
        state["error"] = f"Quality assessment failed: {str(e)}"
        print_flow_step("QUALITY_ASSESSOR_ERROR", state, f"Error: {str(e)}")
    
    return state

def create_sql_multi_agent_workflow():
    """Create the LangGraph workflow for the SQL Multi-Agent system"""
    
    # Create the state graph
    workflow = StateGraph(AgentState)
    
    # Add nodes (agents)
    workflow.add_node("schema_analyzer", schema_analyzer_agent)
    workflow.add_node("sql_generator", sql_generator_agent)
    workflow.add_node("query_validator", query_validator_agent)
    workflow.add_node("query_executor", query_executor_agent)
    workflow.add_node("result_formatter", result_formatter_agent)
    workflow.add_node("quality_assessor", quality_assessor_agent)
    
    # Define the workflow edges
    workflow.set_entry_point("schema_analyzer")
    workflow.add_edge("schema_analyzer", "sql_generator")
    workflow.add_edge("sql_generator", "query_validator")
    workflow.add_edge("query_validator", "query_executor")
    workflow.add_edge("query_executor", "result_formatter")
    workflow.add_edge("result_formatter", "quality_assessor")
    
    # Compile the workflow
    return workflow.compile()

def print_workflow_diagram():
    """Print a visual representation of the workflow"""
    print("\n" + "="*80)
    print("🔗 SQL MULTI-AGENT WORKFLOW DIAGRAM")
    print("="*80)
    print("""
    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
    │  Schema Analyzer│───▶│ SQL Generator   │───▶│ Query Validator │
    │  Agent          │    │ Agent           │    │ Agent           │
    └─────────────────┘    └─────────────────┘    └─────────────────┘
           │                        │                        │
           ▼                        ▼                        ▼
    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
    │ Query Executor  │───▶│ Result Formatter│───▶│ Quality Assessor│
    │ Agent           │    │ Agent           │    │ Agent           │
    └─────────────────┘    └─────────────────┘    └─────────────────┘
    """)
    print("="*80)

def run_sql_multi_agent(question: str, verbose: bool = True):
    """Run the complete SQL Multi-Agent workflow"""
    
    if verbose:
        print_workflow_diagram()
    
    # Initialize state
    initial_state = AgentState(
        question=question,
        schema_context=None,
        sql_query=None,
        optimized_sql=None,
        results=None,
        formatted_output=None,
        error=None,
        agent_logs=[],
        execution_time=None,
        confidence_score=None
    )
    
    # Create and run the workflow
    workflow = create_sql_multi_agent_workflow()
    
    start_time = datetime.now()
    
    try:
        # Run the workflow
        final_state = workflow.invoke(initial_state)
        
        # Calculate execution time
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        final_state["execution_time"] = execution_time
        
        if verbose:
            print("\n" + "="*80)
            print("✅ WORKFLOW COMPLETED SUCCESSFULLY")
            print("="*80)
            print(f"⏱️  Total execution time: {execution_time:.2f} seconds")
            print(f"🎯 Confidence score: {final_state.get('confidence_score', 'N/A')}")
            
            if final_state.get("formatted_output"):
                print(f"\n📊 FINAL RESULTS:")
                print(f"{'='*40}")
                print(final_state["formatted_output"])
            
            if final_state.get("error"):
                print(f"\n⚠️  WARNINGS/ERRORS:")
                print(f"{'='*40}")
                print(final_state["error"])
        
        return final_state
        
    except Exception as e:
        print(f"\n❌ WORKFLOW FAILED: {str(e)}")
        return {"error": str(e), "agent_logs": initial_state["agent_logs"]}

def main():
    """Main function to demonstrate the SQL Multi-Agent system"""
    
    print("🚀 SQL MULTI-AGENT SYSTEM")
    print("="*60)
    
    # Example questions to test
    example_questions = [
        "show all customers with their email addresses",
        "count total number of products",
        "show all active offers with discount percentages",
        "find premium customers with expired offers"
    ]
    
    # Run with default question
    default_question = "show all customers with their email addresses"
    print(f"\n🔍 Running with default question: '{default_question}'")
    
    result = run_sql_multi_agent(default_question, verbose=True)
    
    # Interactive mode
    print("\n" + "="*60)
    print("🎮 INTERACTIVE MODE")
    print("="*60)
    print("Type your questions (or 'quit' to exit):")
    
    while True:
        try:
            user_question = input("\n❓ Your question: ").strip()
            
            if user_question.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not user_question:
                continue
            
            print(f"\n🔍 Processing: {user_question}")
            result = run_sql_multi_agent(user_question, verbose=True)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Check if a question was provided as command line argument
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
        print(f"🔍 Running with question: '{question}'")
        result = run_sql_multi_agent(question, verbose=True)
    else:
        main() 