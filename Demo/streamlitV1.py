import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime

# Ensure Demo/SQLAgent.py is importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
from SQLAgent import main, format_agent_response
import sqlite3

# --- Helper functions ---
def get_database_connection():
    try:
        conn = sqlite3.connect('my_database.db')
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        return None

def parse_sql_result_to_table(result):
    # Try to parse markdown or grid table to DataFrame
    try:
        if isinstance(result, pd.DataFrame):
            return result.columns.tolist(), result.values.tolist()
        if isinstance(result, str) and result.strip().startswith("|"):
            import io
            df = pd.read_csv(io.StringIO(result), sep="|", engine="python").dropna(axis=1, how="all")
            return df.columns.tolist(), df.values.tolist()
    except Exception:
        pass
    return [], []

# --- Streamlit UI ---
st.set_page_config(page_title="SQL AI Agent Dashboard", layout="wide")

# Add custom CSS for larger input box and table font
st.markdown("""
<style>
/* Increase input text box size and font */
.stTextInput > div > div > input {
    font-size: 1.5em !important;
    height: 3em !important;
    min-width: 600px !important;
    width: 80% !important;
}
/* Increase font size of results table */
.stDataFrame th, .stDataFrame td {
    font-size: 1.4em !important;
}
</style>
""", unsafe_allow_html=True)

st.title("SQL AI Agent Dashboard")

if 'recent_queries' not in st.session_state:
    st.session_state['recent_queries'] = []

st.header("Ask Your Database")
question = st.text_input("Enter your question", "", key="question_input")
run_query = st.button("Run Query")

if run_query and question.strip():
    with st.spinner("Running query..."):
        components = main(question3=question)
        response = components['agent_executor'].invoke({'input': question})
        formatted_result = format_agent_response(response, question)
        headers, data = parse_sql_result_to_table(formatted_result)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        query_record = {
            'question': question,
            'timestamp': timestamp,
            'status': 'Success',
            'headers': headers,
            'data': data,
            'raw_result': formatted_result
        }
        st.session_state['recent_queries'].append(query_record)
        if len(st.session_state['recent_queries']) > 20:
            st.session_state['recent_queries'].pop(0)

# Show results
def show_table(headers, data):
    if headers and data:
        df = pd.DataFrame(data, columns=headers)
        st.dataframe(df, use_container_width=True)
    elif isinstance(data, str):
        st.write(data)
    else:
        st.info("No results to display.")

if st.session_state['recent_queries']:
    st.subheader("Query Results")
    last_query = st.session_state['recent_queries'][-1]
    show_table(last_query['headers'], last_query['data'])
    st.caption(f"Question: {last_query['question']} | Time: {last_query['timestamp']}") 