# Enhanced SQL Agent with Table Output Formatting

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.agents import create_sql_agent
from langchain_community.utilities import SQLDatabase
import pandas as pd
from tabulate import tabulate

def create_table_formatted_agent():
    """Create SQL agent that returns results in table format"""
    
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
        """Agent that formats output as table"""
        # Execute SQL query
        response = agent_executor.invoke({"input": question})
        
        # Extract SQL query from response
        if 'query' in response and response['query']:
            sql_query = response['query']
        else:
            # Try to extract SQL from the output text
            output_text = response.get('output', '')
            # Look for SQL in the response
            if 'SELECT' in output_text.upper():
                # Extract the SQL part
                sql_start = output_text.upper().find('SELECT')
                sql_end = output_text.find(';') + 1 if ';' in output_text else len(output_text)
                sql_query = output_text[sql_start:sql_end]
            else:
                return response
        
        # Execute SQL directly to get structured data
        try:
            result = db.run(sql_query)
            
            # Convert to pandas DataFrame for better formatting
            if result and isinstance(result, str):
                # Parse the result string into a DataFrame
                lines = result.strip().split('\n')
                if len(lines) > 1:
                    # Extract column names from first line
                    columns = [col.strip() for col in lines[0].split('|') if col.strip()]
                    # Extract data rows
                    data_rows = []
                    for line in lines[1:]:
                        if line.strip() and '|' in line:
                            row = [cell.strip() for cell in line.split('|') if cell.strip()]
                            if len(row) == len(columns):
                                data_rows.append(row)
                    
                    if data_rows:
                        df = pd.DataFrame(data_rows, columns=columns)
                        
                        # Format as table
                        table_output = tabulate(df, headers='keys', tablefmt='grid', showindex=False)
                        
                        # Return enhanced response
                        enhanced_response = {
                            'question': question,
                            'sql_query': sql_query,
                            'table_output': table_output,
                            'dataframe': df,
                            'row_count': len(df)
                        }
                        
                        return enhanced_response
            
            # Fallback to original response if parsing fails
            return response
            
        except Exception as e:
            print(f"Error executing SQL: {e}")
            return response
    
    return enhanced_agent

# Alternative: Direct SQL execution with table formatting
def execute_sql_with_table_format(sql_query):
    """Execute SQL and return formatted table"""
    import sqlite3
    
    conn = sqlite3.connect('my_database.db')
    
    try:
        # Execute query
        df = pd.read_sql_query(sql_query, conn)
        
        # Format as table
        table_output = tabulate(df, headers='keys', tablefmt='grid', showindex=False)
        
        return {
            'sql_query': sql_query,
            'table_output': table_output,
            'dataframe': df,
            'row_count': len(df)
        }
        
    except Exception as e:
        return {'error': str(e)}
    finally:
        conn.close()

# Enhanced RAG + SQL Agent with table output
def create_rag_table_agent():
    """Create RAG-enhanced SQL agent with table output"""
    
    # Import RAG setup
    from rag_sql_integration import setup_rag_for_sql
    
    # Setup RAG
    rag_chain = setup_rag_for_sql()
    
    # Setup SQL Agent
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
        """Agent that uses RAG for context and returns table format"""
        # Get schema context from RAG
        schema_context = rag_chain.invoke(f"Database schema for: {question}")
        
        # Create enhanced prompt
        enhanced_prompt = f"""
        Database Schema Context:
        {schema_context}
        
        Question: {question}
        
        Please write a SQL query to answer this question. 
        Make sure to include column names in the SELECT statement.
        """
        
        # Execute with SQL agent
        response = agent_executor.invoke({"input": enhanced_prompt})
        
        # Extract and execute SQL for table formatting
        if 'query' in response and response['query']:
            sql_query = response['query']
        else:
            # Try to extract SQL from output
            output_text = response.get('output', '')
            if 'SELECT' in output_text.upper():
                sql_start = output_text.upper().find('SELECT')
                sql_end = output_text.find(';') + 1 if ';' in output_text else len(output_text)
                sql_query = output_text[sql_start:sql_end]
            else:
                return response
        
        # Execute SQL and format as table
        table_result = execute_sql_with_table_format(sql_query)
        
        if 'error' not in table_result:
            return {
                'question': question,
                'schema_context': schema_context,
                'sql_query': sql_query,
                'table_output': table_result['table_output'],
                'row_count': table_result['row_count']
            }
        else:
            return response
    
    return enhanced_agent

# Usage example
if __name__ == "__main__":
    # Install required packages if not available
    try:
        import tabulate
    except ImportError:
        print("Installing tabulate...")
        import subprocess
        subprocess.check_call(["pip3", "install", "tabulate"])
        import tabulate
    
    # Create enhanced agent
    agent = create_rag_table_agent()
    
    # Test with table output
    question = "Show all customers with their names and segments"
    result = agent(question)
    
    print(f"Question: {question}")
    print(f"SQL Query: {result.get('sql_query', 'N/A')}")
    print(f"Row Count: {result.get('row_count', 'N/A')}")
    print("\nTable Output:")
    print(result.get('table_output', result.get('output', 'No table output available'))) 