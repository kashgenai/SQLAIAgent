#!/usr/bin/env python3
"""
SQL Multi-Agent Dashboard using Streamlit
Interactive UI to visualize workflow, results, and agent performance
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import sqlite3
from SQLMultiAgent import run_sql_multi_agent, AgentState
import time
import sys

# Page configuration
st.set_page_config(
    page_title="SQL Multi-Agent Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .agent-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .metric-card {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .workflow-step {
        background-color: #e8f4fd;
        padding: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

def connect_to_database():
    """Connect to SQLite database"""
    try:
        conn = sqlite3.connect('my_database.db')
        return conn
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

def get_table_data(conn, table_name):
    """Get data from a specific table"""
    try:
        query = f"SELECT * FROM {table_name} LIMIT 100"
        df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        st.error(f"Error fetching data from {table_name}: {e}")
        return pd.DataFrame()

def create_workflow_visualization(agent_logs):
    """Create a timeline visualization of the workflow"""
    if not agent_logs:
        return None
    
    # Create timeline data
    timeline_data = []
    for log in agent_logs:
        if 'timestamp' in log and 'step' in log:
            timeline_data.append({
                'timestamp': log['timestamp'],
                'step': log['step'],
                'details': log.get('details', ''),
                'duration': 1  # Placeholder for duration
            })
    
    if not timeline_data:
        return None
    
    df_timeline = pd.DataFrame(timeline_data)
    
    # Create timeline chart
    fig = px.timeline(df_timeline, 
                     x_start='timestamp', 
                     y='step',
                     title='Agent Workflow Timeline',
                     color='step',
                     hover_data=['details'])
    
    fig.update_layout(
        height=400,
        showlegend=False,
        xaxis_title="Time",
        yaxis_title="Agent Steps"
    )
    
    return fig

def create_metrics_dashboard():
    """Create metrics dashboard"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>Total Queries</h3>
            <h2>📊 15</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>Success Rate</h3>
            <h2>✅ 93%</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>Avg Response Time</h3>
            <h2>⏱️ 25s</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>Confidence Score</h3>
            <h2>🎯 85%</h2>
        </div>
        """, unsafe_allow_html=True)

def main():
    """Main dashboard function"""
    
    # Header
    st.markdown('<h1 class="main-header">🤖 SQL Multi-Agent Dashboard</h1>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["🏠 Overview", "🔍 Query Interface", "📊 Database Explorer", "📈 Analytics", "⚙️ Settings"]
    )
    
    if page == "🏠 Overview":
        show_overview_page()
    elif page == "🔍 Query Interface":
        show_query_interface()
    elif page == "📊 Database Explorer":
        show_database_explorer()
    elif page == "📈 Analytics":
        show_analytics_page()
    elif page == "⚙️ Settings":
        show_settings_page()

def show_overview_page():
    """Show the overview page"""
    st.header("📊 System Overview")
    
    # Metrics dashboard
    create_metrics_dashboard()
    
    # Recent activity
    st.subheader("🔄 Recent Activity")
    
    # Placeholder for recent queries
    recent_queries = [
        {"query": "show all customers", "status": "✅ Success", "time": "2 min ago", "confidence": "85%"},
        {"query": "count total products", "status": "✅ Success", "time": "5 min ago", "confidence": "92%"},
        {"query": "find premium customers", "status": "✅ Success", "time": "8 min ago", "confidence": "78%"},
    ]
    
    for query in recent_queries:
        with st.expander(f"{query['query']} - {query['status']}"):
            col1, col2, col3 = st.columns(3)
            col1.write(f"**Query:** {query['query']}")
            col2.write(f"**Status:** {query['status']}")
            col3.write(f"**Confidence:** {query['confidence']}")
    
    # Agent status
    st.subheader("🤖 Agent Status")
    
    agents = [
        {"name": "Schema Analyzer", "status": "🟢 Online", "last_used": "2 min ago"},
        {"name": "SQL Generator", "status": "🟢 Online", "last_used": "2 min ago"},
        {"name": "Query Validator", "status": "🟢 Online", "last_used": "2 min ago"},
        {"name": "Query Executor", "status": "🟢 Online", "last_used": "2 min ago"},
        {"name": "Result Formatter", "status": "🟢 Online", "last_used": "2 min ago"},
        {"name": "Quality Assessor", "status": "🟢 Online", "last_used": "2 min ago"},
    ]
    
    for agent in agents:
        st.markdown(f"""
        <div class="agent-card">
            <strong>{agent['name']}</strong> - {agent['status']}<br>
            <small>Last used: {agent['last_used']}</small>
        </div>
        """, unsafe_allow_html=True)

def show_query_interface():
    """Show the query interface page"""
    st.header("🔍 Query Interface")
    
    # Query input
    query = st.text_area(
        "Enter your SQL question:",
        placeholder="e.g., show all customers with their email addresses",
        height=100
    )
    
    col1, col2 = st.columns([1, 4])
    
    with col1:
        if st.button("🚀 Run Query", type="primary"):
            if query.strip():
                run_query_with_ui(query)
            else:
                st.warning("Please enter a query first.")
    
    with col2:
        if st.button("📋 Load Example"):
            st.session_state.example_query = "show all customers with their email addresses"
            st.rerun()
    
    # Load example query if set
    if hasattr(st.session_state, 'example_query'):
        st.text_area("Example Query:", st.session_state.example_query, disabled=True)
        if st.button("Use This Example"):
            run_query_with_ui(st.session_state.example_query)

def run_query_with_ui(query):
    """Run query and display results with UI"""
    
    # Create progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Create containers for results
    result_container = st.container()
    workflow_container = st.container()
    
    try:
        # Update progress
        status_text.text("🔍 Analyzing question...")
        progress_bar.progress(10)
        time.sleep(0.5)
        
        status_text.text("📝 Generating SQL...")
        progress_bar.progress(30)
        time.sleep(0.5)
        
        status_text.text("✅ Validating query...")
        progress_bar.progress(50)
        time.sleep(0.5)
        
        status_text.text("🚀 Executing query...")
        progress_bar.progress(70)
        time.sleep(0.5)
        
        status_text.text("📊 Formatting results...")
        progress_bar.progress(90)
        
        # Run the actual query
        result = run_sql_multi_agent(query, verbose=False)
        
        progress_bar.progress(100)
        status_text.text("✅ Complete!")
        
        # Display results
        with result_container:
            st.subheader("📊 Query Results")
            
            if result.get("formatted_output"):
                st.markdown(result["formatted_output"])
            elif result.get("results"):
                st.write(result["results"])
            
            # Show metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Execution Time", f"{result.get('execution_time', 0):.2f}s")
            with col2:
                st.metric("Confidence Score", f"{result.get('confidence_score', 0)}%")
            with col3:
                st.metric("Status", "✅ Success" if not result.get("error") else "❌ Error")
        
        # Display workflow
        with workflow_container:
            st.subheader("🔄 Workflow Steps")
            
            if result.get("agent_logs"):
                for log in result["agent_logs"]:
                    if "step" in log:
                        st.markdown(f"""
                        <div class="workflow-step">
                            <strong>{log['step']}</strong><br>
                            <small>{log.get('details', '')}</small>
                        </div>
                        """, unsafe_allow_html=True)
        
        # Show timeline if available
        if result.get("agent_logs"):
            st.subheader("📈 Workflow Timeline")
            timeline_fig = create_workflow_visualization(result["agent_logs"])
            if timeline_fig:
                st.plotly_chart(timeline_fig, use_container_width=True)
    
    except Exception as e:
        st.error(f"❌ Error running query: {str(e)}")
        progress_bar.progress(0)
        status_text.text("❌ Failed")

def show_database_explorer():
    """Show the database explorer page"""
    st.header("📊 Database Explorer")
    
    # Connect to database
    conn = connect_to_database()
    if not conn:
        return
    
    # Get table names
    try:
        tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table'", conn)
        st.subheader("🗂️ Available Tables")
        
        for table_name in tables['name']:
            with st.expander(f"📋 {table_name}"):
                # Show table data
                df = get_table_data(conn, table_name)
                if not df.empty:
                    st.dataframe(df, use_container_width=True)
                    
                    # Show basic statistics
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Rows:** {len(df)}")
                        st.write(f"**Columns:** {len(df.columns)}")
                    with col2:
                        st.write(f"**Memory Usage:** {df.memory_usage(deep=True).sum() / 1024:.2f} KB")
                    
                    # Show data types
                    st.subheader("📋 Column Information")
                    dtype_df = pd.DataFrame({
                        'Column': df.columns,
                        'Type': df.dtypes.astype(str),
                        'Non-Null Count': df.count(),
                        'Null Count': df.isnull().sum()
                    })
                    st.dataframe(dtype_df, use_container_width=True)
    
    except Exception as e:
        st.error(f"Error exploring database: {e}")
    finally:
        conn.close()

def show_analytics_page():
    """Show the analytics page"""
    st.header("📈 Analytics")
    
    # Sample analytics data
    st.subheader("📊 Query Performance")
    
    # Performance chart
    performance_data = {
        'Date': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05'],
        'Queries': [15, 23, 18, 31, 27],
        'Avg_Time': [25, 22, 28, 19, 24],
        'Success_Rate': [93, 96, 89, 94, 91]
    }
    
    df_perf = pd.DataFrame(performance_data)
    
    # Queries over time
    fig1 = px.line(df_perf, x='Date', y='Queries', title='Daily Query Volume')
    st.plotly_chart(fig1, use_container_width=True)
    
    # Performance metrics
    col1, col2 = st.columns(2)
    
    with col1:
        fig2 = px.bar(df_perf, x='Date', y='Avg_Time', title='Average Response Time (seconds)')
        st.plotly_chart(fig2, use_container_width=True)
    
    with col2:
        fig3 = px.bar(df_perf, x='Date', y='Success_Rate', title='Success Rate (%)')
        st.plotly_chart(fig3, use_container_width=True)
    
    # Agent performance
    st.subheader("🤖 Agent Performance")
    
    agent_performance = {
        'Agent': ['Schema Analyzer', 'SQL Generator', 'Query Validator', 'Query Executor', 'Result Formatter', 'Quality Assessor'],
        'Success_Rate': [98, 95, 97, 99, 96, 94],
        'Avg_Time': [2.1, 3.5, 1.8, 15.2, 2.3, 1.5]
    }
    
    df_agent = pd.DataFrame(agent_performance)
    
    fig4 = px.bar(df_agent, x='Agent', y='Success_Rate', title='Agent Success Rates')
    st.plotly_chart(fig4, use_container_width=True)

def show_settings_page():
    """Show the settings page"""
    st.header("⚙️ Settings")
    
    st.subheader("🔧 System Configuration")
    
    # Database settings
    st.write("**Database Configuration:**")
    db_host = st.text_input("Database Host", value="localhost")
    db_port = st.number_input("Database Port", value=5432)
    db_name = st.text_input("Database Name", value="my_database.db")
    
    # Agent settings
    st.write("**Agent Configuration:**")
    max_retries = st.slider("Max Retries", 1, 5, 3)
    timeout = st.slider("Timeout (seconds)", 10, 120, 60)
    confidence_threshold = st.slider("Confidence Threshold (%)", 50, 95, 75)
    
    # LLM settings
    st.write("**LLM Configuration:**")
    model_name = st.selectbox("Model", ["gemini-1.5-flash", "gemini-1.5-pro", "gpt-4"])
    temperature = st.slider("Temperature", 0.0, 1.0, 0.0, 0.1)
    
    # Save settings
    if st.button("💾 Save Settings"):
        st.success("Settings saved successfully!")
    
    # System info
    st.subheader("ℹ️ System Information")
    st.write(f"**Python Version:** {sys.version}")
    st.write(f"**Streamlit Version:** {st.__version__}")
    st.write(f"**Database:** SQLite")
    st.write(f"**LLM Provider:** Google Gemini")

if __name__ == "__main__":
    main() 