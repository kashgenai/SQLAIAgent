import sys
import os
import pandas as pd
import re
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Demo.SQLMultiAgent import run_sql_multi_agent

import streamlit as st

st.set_page_config(page_title="SQL Multi-Agent Streamlit UI", layout="centered")

# Global CSS for font sizes, alignment, and input/button styling
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.1em !important;
        font-weight: 700;
        margin-bottom: 0.2em;
        text-align: left;
    }
    .desc-text {
        font-size: 1.08em;
        color: #444;
        margin-bottom: 1.2em;
        line-height: 1.5em;
        text-align: left;
        max-width: 700px;
        padding-left: 2px;
    }
    .query-row {
        display: flex;
        align-items: center;
        gap: 0.5em;
        margin-bottom: 1.2em;
    }
    .query-input-box input {
        width: 480px !important;
        font-size: 1.2em !important;
    }
    .run-query-btn button {
        font-size: 1.0em !important;
        padding: 0.4em 1.2em !important;
        margin-left: 0.5em;
        margin-top: 0 !important;
        margin-bottom: 0 !important;
    }
    html, body, [class*="css"]  {
        font-size: 22px !important;
    }
    .stDataFrame th, .stDataFrame td {
        font-size: 22px !important;
    }
    .built-by-prakash {
        position: fixed;
        right: 20px;
        bottom: 10px;
        font-size: 1.1em;
        color: #888;
        z-index: 100;
    }
    </style>
    <div class='built-by-prakash'>Built by Prakash</div>
    """,
    unsafe_allow_html=True
)

# Custom header
st.markdown("<div class='main-header'>SQL Multi-Agent Dashboard</div>", unsafe_allow_html=True)

# Description in two lines, left-aligned
st.markdown(
    """
    <div class='desc-text'>
    This app allows you to ask natural language questions about your database.<br/>
    The multi-agent system will analyze your question, generate SQL, execute it, and return results.
    </div>
    """,
    unsafe_allow_html=True
)

# Query input and button in a single row with custom classes
st.markdown('<div class="query-row">', unsafe_allow_html=True)
query = st.text_input("Enter your question:", "show all customers with their email addresses", key="query_input", label_visibility="visible",
    placeholder="Type your question here...", help=None)
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('<style>.stTextInput input {width: 480px !important;}</style>', unsafe_allow_html=True)
run_query = st.button("Run Query", key="run_query_btn")
st.markdown('<style>.stButton button {font-size: 1.0em !important;}</style>', unsafe_allow_html=True)

# Tabs for Results and Query Details
results_tab, details_tab = st.tabs(["Final Results", "Query Details"])

# Only run query and update results when button is pressed
if run_query:
    with st.spinner("Processing your query with SQL Multi-Agent..."):
        result = run_sql_multi_agent(query, verbose=False)

        # Final Results Tab
        with results_tab:
            st.subheader("Final Results")
            if result.get("formatted_output"):
                # Try to parse markdown table to DataFrame
                def markdown_table_to_df(md_table):
                    lines = [line.strip() for line in md_table.strip().splitlines() if line.strip()]
                    if len(lines) < 2:
                        return None
                    header = [h.strip('` ') for h in lines[0].strip('|').split('|')]
                    data = []
                    for row in lines[2:]:
                        data.append([cell.strip('` ') for cell in row.strip('|').split('|')])
                    return pd.DataFrame(data, columns=header)
                df = markdown_table_to_df(result["formatted_output"])
                if df is not None:
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.markdown(result["formatted_output"])
            elif result.get("results"):
                st.code(str(result["results"]))
            else:
                st.warning("No results returned.")

        # Query Details Tab
        with details_tab:
            st.subheader("Query Details")
            # Show workflow logs
            if "agent_logs" in result and result["agent_logs"]:
                for log in result["agent_logs"]:
                    st.markdown(f"**{log['timestamp']}** - *{log['step']}*  ")
                    if log.get("details"):
                        st.markdown(f"> {log['details']}")
                    if log.get("state_summary"):
                        st.code(str(log["state_summary"]))
                    st.markdown("---")
            else:
                st.info("No logs available.")
            # Show errors
            if result.get("error"):
                st.error(result["error"]) 
            # Show confidence score
            if result.get("confidence_score") is not None:
                st.success(f"Confidence Score: {result['confidence_score']}") 