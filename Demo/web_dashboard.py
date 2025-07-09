#!/usr/bin/env python3
"""
Web Dashboard for SQLAgent.py
Simple Flask-based web interface to interact with the SQL Agent
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
import json
from datetime import datetime
import os
from SQLAgent import main, format_agent_response
import sys

app = Flask(__name__)

# Global variable to store recent queries
recent_queries = []

def get_database_connection():
    """Create a database connection"""
    try:
        conn = sqlite3.connect('my_database.db')
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def get_table_names():
    """Get list of table names from database"""
    conn = get_database_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        return tables
    except Exception as e:
        print(f"Error getting table names: {e}")
        conn.close()
        return []

def get_table_data(table_name, limit=50):
    """Get data from a specific table"""
    conn = get_database_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        
        data = []
        for row in rows:
            data.append(dict(zip(columns, row)))
        
        conn.close()
        return data, columns
    except Exception as e:
        print(f"Error getting table data: {e}")
        conn.close()
        return [], []

def get_table_schema(table_name):
    """Get schema information for a table"""
    conn = get_database_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        schema = cursor.fetchall()
        conn.close()
        return schema
    except Exception as e:
        print(f"Error getting table schema: {e}")
        conn.close()
        return []

@app.route('/')
def index():
    """Main dashboard page"""
    tables = get_table_names()
    return render_template('dashboard.html', tables=tables, recent_queries=recent_queries[-5:])

@app.route('/query', methods=['POST'])
def run_query():
    """Run a SQL query using the SQL Agent"""
    try:
        question = request.form.get('question', '').strip()
        
        if not question:
            return jsonify({'error': 'Please provide a question'})
        
        # Run the query using SQLAgent
        print(f"Running query: {question}")
        
        # Get components from SQLAgent
        components = main(question3=question)
        
        # Get the response from the agent
        response = components['agent_executor'].invoke({'input': question})
        
        # Format the response
        formatted_result = format_agent_response(response, question)
        
        # Store in recent queries
        query_record = {
            'question': question,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'Success',
            'result': formatted_result[:200] + '...' if len(formatted_result) > 200 else formatted_result
        }
        recent_queries.append(query_record)
        
        # Keep only last 10 queries
        if len(recent_queries) > 10:
            recent_queries.pop(0)
        
        return jsonify({
            'success': True,
            'question': question,
            'result': formatted_result,
            'raw_result': response.get('output', ''),
            'timestamp': query_record['timestamp']
        })
        
    except Exception as e:
        print(f"Error running query: {e}")
        return jsonify({'error': f'Error running query: {str(e)}'})

@app.route('/tables')
def tables():
    """Show all tables"""
    tables = get_table_names()
    return render_template('tables.html', tables=tables)

@app.route('/table/<table_name>')
def table_view(table_name):
    """Show data for a specific table"""
    data, columns = get_table_data(table_name)
    schema = get_table_schema(table_name)
    return render_template('table_view.html', 
                         table_name=table_name, 
                         data=data, 
                         columns=columns, 
                         schema=schema)

@app.route('/api/table/<table_name>')
def api_table_data(table_name):
    """API endpoint to get table data"""
    data, columns = get_table_data(table_name)
    return jsonify({
        'table_name': table_name,
        'data': data,
        'columns': columns,
        'row_count': len(data)
    })

@app.route('/api/stats')
def api_stats():
    """API endpoint for dashboard statistics"""
    tables = get_table_names()
    total_tables = len(tables)
    
    # Get total rows across all tables
    total_rows = 0
    conn = get_database_connection()
    if conn:
        try:
            cursor = conn.cursor()
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                total_rows += count
            conn.close()
        except:
            conn.close()
    
    return jsonify({
        'total_tables': total_tables,
        'total_rows': total_rows,
        'recent_queries': len(recent_queries)
    })

def create_html_templates():
    """Create the HTML template files"""
    
    # Main dashboard template
    dashboard_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SQL Agent Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }
        
        .nav {
            background: #f8f9fa;
            padding: 15px 30px;
            border-bottom: 1px solid #e9ecef;
        }
        
        .nav a {
            color: #667eea;
            text-decoration: none;
            margin-right: 20px;
            padding: 8px 16px;
            border-radius: 20px;
            transition: all 0.3s ease;
        }
        
        .nav a:hover, .nav a.active {
            background: #667eea;
            color: white;
        }
        
        .content {
            padding: 30px;
        }
        
        .query-section {
            background: #f8f9fa;
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 30px;
        }
        
        .query-section h2 {
            color: #333;
            margin-bottom: 20px;
        }
        
        .query-input {
            width: 100%;
            padding: 15px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 16px;
            margin-bottom: 15px;
            resize: vertical;
            min-height: 100px;
        }
        
        .query-input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .btn {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            transition: all 0.3s ease;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .result-section {
            background: white;
            border: 1px solid #e9ecef;
            border-radius: 10px;
            padding: 25px;
            margin-top: 20px;
            display: none;
        }
        
        .result-section h3 {
            color: #333;
            margin-bottom: 15px;
        }
        
        .result-content {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            white-space: pre-wrap;
            font-family: 'Courier New', monospace;
            max-height: 400px;
            overflow-y: auto;
        }
        
        .loading {
            text-align: center;
            padding: 20px;
            color: #667eea;
        }
        
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 15px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            text-align: center;
        }
        
        .stat-card h3 {
            color: #667eea;
            font-size: 2rem;
            margin-bottom: 10px;
        }
        
        .stat-card p {
            color: #666;
            font-size: 1.1rem;
        }
        
        .recent-queries {
            background: white;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .query-item {
            border-bottom: 1px solid #e9ecef;
            padding: 15px 0;
        }
        
        .query-item:last-child {
            border-bottom: none;
        }
        
        .query-item h4 {
            color: #333;
            margin-bottom: 5px;
        }
        
        .query-item p {
            color: #666;
            font-size: 0.9rem;
        }
        
        .error {
            background: #fee;
            color: #c33;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #c33;
        }
        
        .success {
            background: #efe;
            color: #363;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #363;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 SQL Agent Dashboard</h1>
            <p>Interactive interface for your SQL Multi-Agent system</p>
        </div>
        
        <div class="nav">
            <a href="/" class="active">🏠 Dashboard</a>
            <a href="/tables">📊 Database Tables</a>
        </div>
        
        <div class="content">
            <!-- Statistics -->
            <div class="stats-grid" id="stats">
                <div class="stat-card">
                    <h3 id="total-tables">-</h3>
                    <p>Total Tables</p>
                </div>
                <div class="stat-card">
                    <h3 id="total-rows">-</h3>
                    <p>Total Rows</p>
                </div>
                <div class="stat-card">
                    <h3 id="recent-queries-count">-</h3>
                    <p>Recent Queries</p>
                </div>
            </div>
            
            <!-- Query Interface -->
            <div class="query-section">
                <h2>🔍 Ask Your Database</h2>
                <textarea 
                    id="question-input" 
                    class="query-input" 
                    placeholder="Enter your question here...&#10;Examples:&#10;- show all customers with their email addresses&#10;- count total number of products&#10;- find premium customers with expired offers"
                ></textarea>
                <button id="run-query-btn" class="btn">🚀 Run Query</button>
            </div>
            
            <!-- Results -->
            <div id="result-section" class="result-section">
                <h3>📊 Results</h3>
                <div id="result-content" class="result-content"></div>
            </div>
            
            <!-- Recent Queries -->
            <div class="recent-queries">
                <h2>🔄 Recent Queries</h2>
                <div id="recent-queries-list">
                    {% for query in recent_queries %}
                    <div class="query-item">
                        <h4>{{ query.question }}</h4>
                        <p><strong>Time:</strong> {{ query.timestamp }} | <strong>Status:</strong> {{ query.status }}</p>
                        <p>{{ query.result }}</p>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Load statistics on page load
        document.addEventListener('DOMContentLoaded', function() {
            loadStats();
        });
        
        // Query execution
        document.getElementById('run-query-btn').addEventListener('click', function() {
            const question = document.getElementById('question-input').value.trim();
            if (!question) {
                alert('Please enter a question');
                return;
            }
            
            runQuery(question);
        });
        
        function loadStats() {
            fetch('/api/stats')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('total-tables').textContent = data.total_tables;
                    document.getElementById('total-rows').textContent = data.total_rows;
                    document.getElementById('recent-queries-count').textContent = data.recent_queries;
                })
                .catch(error => console.error('Error loading stats:', error));
        }
        
        function runQuery(question) {
            const btn = document.getElementById('run-query-btn');
            const resultSection = document.getElementById('result-section');
            const resultContent = document.getElementById('result-content');
            
            // Show loading state
            btn.disabled = true;
            btn.textContent = '⏳ Processing...';
            resultSection.style.display = 'block';
            resultContent.innerHTML = '<div class="loading"><div class="spinner"></div>Processing your query...</div>';
            
            // Send request
            fetch('/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: 'question=' + encodeURIComponent(question)
            })
            .then(response => response.json())
            .then(data => {
                btn.disabled = false;
                btn.textContent = '🚀 Run Query';
                
                if (data.error) {
                    resultContent.innerHTML = '<div class="error">❌ ' + data.error + '</div>';
                } else {
                    resultContent.innerHTML = '<div class="success">✅ Query executed successfully!</div><br>' + data.result;
                    
                    // Reload stats and recent queries
                    loadStats();
                    setTimeout(() => {
                        window.location.reload();
                    }, 2000);
                }
            })
            .catch(error => {
                btn.disabled = false;
                btn.textContent = '🚀 Run Query';
                resultContent.innerHTML = '<div class="error">❌ Error: ' + error.message + '</div>';
            });
        }
        
        // Allow Enter key to submit
        document.getElementById('question-input').addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && e.ctrlKey) {
                document.getElementById('run-query-btn').click();
            }
        });
    </script>
</body>
</html>
    '''
    
    # Tables list template
    tables_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Database Tables - SQL Agent Dashboard</title>
    <style>
        /* Same CSS as dashboard.html */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .nav {
            background: #f8f9fa;
            padding: 15px 30px;
            border-bottom: 1px solid #e9ecef;
        }
        
        .nav a {
            color: #667eea;
            text-decoration: none;
            margin-right: 20px;
            padding: 8px 16px;
            border-radius: 20px;
            transition: all 0.3s ease;
        }
        
        .nav a:hover, .nav a.active {
            background: #667eea;
            color: white;
        }
        
        .content {
            padding: 30px;
        }
        
        .table-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
        }
        
        .table-card {
            background: white;
            border: 1px solid #e9ecef;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }
        
        .table-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        }
        
        .table-card h3 {
            color: #667eea;
            margin-bottom: 10px;
        }
        
        .table-card p {
            color: #666;
            margin-bottom: 15px;
        }
        
        .btn {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 20px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            transition: all 0.3s ease;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Database Tables</h1>
            <p>Explore your database structure and data</p>
        </div>
        
        <div class="nav">
            <a href="/">🏠 Dashboard</a>
            <a href="/tables" class="active">📊 Database Tables</a>
        </div>
        
        <div class="content">
            <div class="table-grid">
                {% for table in tables %}
                <div class="table-card">
                    <h3>📋 {{ table }}</h3>
                    <p>Click to view table data and schema</p>
                    <a href="/table/{{ table }}" class="btn">View Table</a>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
</body>
</html>
    '''
    
    # Table view template
    table_view_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ table_name }} - SQL Agent Dashboard</title>
    <style>
        /* Same base CSS */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .nav {
            background: #f8f9fa;
            padding: 15px 30px;
            border-bottom: 1px solid #e9ecef;
        }
        
        .nav a {
            color: #667eea;
            text-decoration: none;
            margin-right: 20px;
            padding: 8px 16px;
            border-radius: 20px;
            transition: all 0.3s ease;
        }
        
        .nav a:hover, .nav a.active {
            background: #667eea;
            color: white;
        }
        
        .content {
            padding: 30px;
        }
        
        .data-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .data-table th {
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
        }
        
        .data-table td {
            padding: 12px;
            border-bottom: 1px solid #e9ecef;
        }
        
        .data-table tr:hover {
            background: #f8f9fa;
        }
        
        .schema-section {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        
        .schema-table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .schema-table th {
            background: #667eea;
            color: white;
            padding: 10px;
            text-align: left;
        }
        
        .schema-table td {
            padding: 10px;
            border-bottom: 1px solid #e9ecef;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📋 {{ table_name }}</h1>
            <p>Table data and schema information</p>
        </div>
        
        <div class="nav">
            <a href="/">🏠 Dashboard</a>
            <a href="/tables">📊 Database Tables</a>
            <a href="/tables" class="active">📋 {{ table_name }}</a>
        </div>
        
        <div class="content">
            <!-- Schema Information -->
            <div class="schema-section">
                <h2>📋 Schema Information</h2>
                <table class="schema-table">
                    <thead>
                        <tr>
                            <th>Column</th>
                            <th>Type</th>
                            <th>Not Null</th>
                            <th>Default</th>
                            <th>Primary Key</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for column in schema %}
                        <tr>
                            <td>{{ column[1] }}</td>
                            <td>{{ column[2] }}</td>
                            <td>{{ "Yes" if column[3] else "No" }}</td>
                            <td>{{ column[4] if column[4] else "-" }}</td>
                            <td>{{ "Yes" if column[5] else "No" }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            
            <!-- Data Table -->
            <h2>📊 Table Data ({{ data|length }} rows)</h2>
            {% if data %}
            <table class="data-table">
                <thead>
                    <tr>
                        {% for column in columns %}
                        <th>{{ column }}</th>
                        {% endfor %}
                    </tr>
                </thead>
                <tbody>
                    {% for row in data %}
                    <tr>
                        {% for column in columns %}
                        <td>{{ row[column] if row[column] is not none else "-" }}</td>
                        {% endfor %}
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <p>No data available in this table.</p>
            {% endif %}
        </div>
    </div>
</body>
</html>
    '''
    
    # Write templates to files
    with open('templates/dashboard.html', 'w') as f:
        f.write(dashboard_html)
    
    with open('templates/tables.html', 'w') as f:
        f.write(tables_html)
    
    with open('templates/table_view.html', 'w') as f:
        f.write(table_view_html)
    
    print("✅ HTML templates created successfully!")

if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    create_html_templates()
    print("🚀 Starting SQL Agent Web Dashboard...")
    # Default port
    port = 5000
    # If a port is provided as a command-line argument, use it
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except Exception:
            print(f"Invalid port argument: {sys.argv[1]}, using default port 5000.")
    print(f"📊 Dashboard will be available at: http://localhost:{port}")
    print("🔍 Press Ctrl+C to stop the server")
    app.run(debug=True, host='0.0.0.0', port=port) 