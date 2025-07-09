import sys
import os
import pandas as pd
import streamlit as st
from datetime import datetime
import typing

# Ensure Demo/SQLAgent.py is importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from SQLAgent import main, format_agent_response
import sqlite3

# --- Ensure session state for recent queries is initialized ---
if 'recent_queries' not in st.session_state:
    st.session_state['recent_queries'] = []

st.set_page_config(page_title="Enhanced SQL Agent Streamlit Dashboard", layout="wide")

# --- Helper functions ---
def get_database_connection():
    try:
        conn = sqlite3.connect('my_database.db')
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        return None

def get_table_names():
    conn = get_database_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        return tables
    except:
        conn.close()
        return []

def get_total_rows():
    conn = get_database_connection()
    if not conn:
        return 0
    try:
        cursor = conn.cursor()
        total = 0
        for table in get_table_names():
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            total += cursor.fetchone()[0]
        conn.close()
        return total
    except:
        conn.close()
        return 0

def get_foreign_keys():
    conn = get_database_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        relationships = []
        for table in tables:
            cursor.execute(f"PRAGMA foreign_key_list({table})")
            fks = cursor.fetchall()
            for fk in fks:
                relationships.append({
                    'table': table,
                    'column': fk[3],
                    'ref_table': fk[2],
                    'ref_column': fk[4]
                })
        conn.close()
        return relationships
    except:
        conn.close()
        return []

def parse_sql_result_to_table(result_text):
    try:
        lines = result_text.strip().split('\n')
        data_lines = [line for line in lines if '|' in line and not line.startswith('|---')]
        if data_lines:
            table_data = []
            for line in data_lines:
                cells = [cell.strip() for cell in line.split('|') if cell.strip()]
                if cells:
                    table_data.append(cells)
            if table_data:
                headers = table_data[0]
                data = table_data[1:] if len(table_data) > 1 else []
                return headers, data
        return ['Result'], [[result_text]]
    except:
        return ['Result'], [[result_text]]

# --- Streamlit UI ---
# Custom CSS for larger font sizes and centered header
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.8em !important;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0.2em;
        letter-spacing: 0.04em;
    }
    .stApp, .stMarkdown, .stDataFrame, .stTextInput, .stForm, .stExpander, .stMetric, .stButton, .stTextArea, .stSelectbox, .stNumberInput, .stRadio, .stCheckbox, .stSlider, .stDateInput, .stTimeInput, .stFileUploader, .stColorPicker, .stJson, .stTable, .stDataEditor, .stTabs, .stTab, .stCaption, .stSubheader, .stHeader, .stText, .stCode, .stAlert, .stInfo, .stWarning, .stError, .stSuccess, .stException, .stHelp, .stTooltip, .stProgress, .stSpinner, .stSidebar, .stSidebarContent, .stSidebarHeader, .stSidebarFooter, .stSidebarSection, .stSidebarTabs, .stSidebarTab, .stSidebarCaption, .stSidebarSubheader, .stSidebarHeader, .stSidebarText, .stSidebarCode, .stSidebarAlert, .stSidebarInfo, .stSidebarWarning, .stSidebarError, .stSidebarSuccess, .stSidebarException, .stSidebarHelp, .stSidebarTooltip, .stSidebarProgress, .stSidebarSpinner {
        font-size: 2.5em !important;
        text-align: center !important;
    }
    .stDataFrame th, .stDataFrame td {
        font-size: 2.36em !important;
        text-align: center !important;
    }
    .stat-header {
        font-size: 1.2em !important;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.1em;
    }
    .stat-value {
        font-size: 2.5em !important;
        font-weight: 600;
        text-align: center;
        margin-bottom: 0.5em;
    }
    .question-label {
        font-size: 2.6em !important;
        font-weight: 700;
        text-align: left;
        margin-bottom: 0.1em;
        margin-left: 0;
    }
    .question-row {
        display: flex;
        flex-direction: row;
        align-items: flex-start;
        justify-content: flex-start;
        gap: 0.7em;
        margin-bottom: 0.7em;
        margin-left: 0;
        width: fit-content;
    }
    .question-input {
        width: 900px !important;
        min-width: 600px !important;
        height: 4.5em !important;
        padding: 0.5em 1em !important;
    }
    /* Force font size for text area input */
    textarea, .stTextArea textarea, .stTextArea > div > textarea {
        font-size: 2.1em !important;
        line-height: 1.2 !important;
    }
    /* Ultra-compact Run Query button with very thin border to fit tightly with text */
    .stButton > button {
        font-size: 0.9em !important;
        padding: 0.05em 0.4em !important;
        height: 1.2em !important;
        min-height: 0 !important;
        min-width: 0 !important;
        line-height: 1 !important;
        box-sizing: border-box !important;
        border-radius: 0.08em !important;
        border: 1px solid #2563eb !important;
        background: #fff !important;
        color: #2563eb !important;
        font-weight: 700 !important;
        margin-top: 0.05em !important;
        margin-bottom: 0.05em !important;
        vertical-align: middle !important;
        box-shadow: none !important;
        transition: background 0.2s, color 0.2s;
    }
    .stButton > button:hover {
        background: #2563eb !important;
        color: #fff !important;
    }
    .example-placeholder::placeholder {
        font-size: 2.8em !important;
        color: #888 !important;
        font-style: italic;
    }
    /* Double the font size for the results table */
    .stDataFrame, .stTable, .stTable table, .stTable td, .stTable th {
        font-size: 2em !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="main-header">SQL AI Agent Dashboard</div>', unsafe_allow_html=True)

# --- Centered stats with values below headers ---
stat_cols = st.columns(3)
with stat_cols[0]:
    st.markdown('<div class="stat-header">Total Tables</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="stat-value">{len(get_table_names())}</div>', unsafe_allow_html=True)
with stat_cols[1]:
    st.markdown('<div class="stat-header">Total Rows</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="stat-value">{get_total_rows()}</div>', unsafe_allow_html=True)
with stat_cols[2]:
    st.markdown('<div class="stat-header">Relationships</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="stat-value">{len(get_foreign_keys())}</div>', unsafe_allow_html=True)

# Centered description, single line
st.markdown("""
<div style='font-size:1.18em; color:#444; margin-bottom:1.2em; text-align:center;'>
Ask natural language questions about your database. Results and recent queries are shown below.
</div>
""", unsafe_allow_html=True)

# --- Question input row ---
st.markdown('<div class="question-label">Ask your Database:</div>', unsafe_allow_html=True)

# Only one example with Ex: prefix
placeholder_text = "Ex: Show all customers with their email addresses"

# Custom input row with button beside
st.markdown('<div class="question-row">', unsafe_allow_html=True)
question = st.text_area(
    label="Your Question",  # For accessibility, but will be hidden
    value="",
    height=90,
    placeholder=placeholder_text,
    key="question_input",
    help="Type your natural language question here.",
    label_visibility="collapsed"
)
submit = st.button("Run Query", key="run_query_btn")
st.markdown('</div>', unsafe_allow_html=True)

if submit and question.strip():
    with st.spinner("Processing your query..."):
        try:
            components = main(question3=question)
            response = components['agent_executor'].invoke({'input': question})
            formatted_result = format_agent_response(response, question)
            headers, data = parse_sql_result_to_table(formatted_result)
            # Ensure headers is a list of strings and data is a list of lists
            if not (isinstance(headers, list) and all(isinstance(h, str) for h in headers)):
                headers = ['Result']
            if not (isinstance(data, list) and all(isinstance(row, list) for row in data)):
                data = [[str(formatted_result)]]
            headers = typing.cast(list[str], headers)
            data = typing.cast(list[list[str]], data)
            df = pd.DataFrame(data, columns=pd.Index(headers))
            st.session_state['recent_queries'].append({
                'question': question,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'headers': headers,
                'data': data,
                'raw_result': formatted_result
            })
            st.success("Query executed successfully!")
            st.dataframe(df, use_container_width=True, height=400)
        except Exception as e:
            st.error(f"Error running query: {e}")

# Show recent queries
with st.expander("Recent Queries", expanded=True):
    for q in reversed(st.session_state['recent_queries'][-10:]):
        st.markdown(f"**{q['question']}**  ")
        st.caption(f"{q['timestamp']}")
        headers = q['headers'] if isinstance(q['headers'], list) and all(isinstance(h, str) for h in q['headers']) else ['Result']
        data = q['data'] if isinstance(q['data'], list) and all(isinstance(row, list) for row in q['data']) else [[str(q['raw_result'])]]
        headers = typing.cast(list[str], headers)
        data = typing.cast(list[list[str]], data)
        if headers and data:
            df = pd.DataFrame(data, columns=pd.Index(headers))
            st.dataframe(df, use_container_width=True, height=200)
        else:
            st.text(q['raw_result'])
        st.markdown("---") 