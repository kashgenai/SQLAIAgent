#!/usr/bin/env python3
"""
Enhanced Web Dashboard for SQLAgent.py
Features: Table format results, persistent data, proper formatting
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
import json
from datetime import datetime
import os
from SQLAgent import main, format_agent_response
import sys
import pandas as pd
import io

app = Flask(__name__)

# Global variable to store recent queries and results
recent_queries = []
query_results = {}  # Store results by query ID
query_counter = 0

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

def get_foreign_keys():
    """Get foreign key relationships"""
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
    except Exception as e:
        print(f"Error getting foreign keys: {e}")
        conn.close()
        return []

def parse_sql_result_to_table(result_text):
    """Parse SQL result text into table format"""
    try:
        # Try to extract data from the result
        lines = result_text.strip().split('\n')
        
        # Look for table-like patterns
        data_lines = []
        for line in lines:
            if '|' in line and not line.startswith('|') and not line.endswith('|'):
                # This might be a data row
                data_lines.append(line)
        
        if data_lines:
            # Parse the data
            table_data = []
            for line in data_lines:
                cells = [cell.strip() for cell in line.split('|') if cell.strip()]
                if cells:
                    table_data.append(cells)
            
            if table_data:
                # Use first row as headers if it looks like headers
                headers = table_data[0]
                data = table_data[1:] if len(table_data) > 1 else []
                return headers, data
        
        # Fallback: return as single column
        return ['Result'], [[result_text]]
        
    except Exception as e:
        print(f"Error parsing result: {e}")
        return ['Result'], [[result_text]]

def format_results_to_table(results):
    """
    Convert results (list of dicts, list of tuples, or string) to a pandas DataFrame and return HTML table.
    """
    if not results:
        return None
    if isinstance(results, str):
        # Try to parse markdown table
        if results.strip().startswith("|"):
            try:
                df = pd.read_csv(io.StringIO(results), sep="|").dropna(axis=1, how="all")
                return df.to_html(classes="result-table", index=False)
            except Exception:
                return f'<div class="no-results">{results}</div>'
        return f'<div class="no-results">{results}</div>'
    if isinstance(results, list):
        if all(isinstance(row, dict) for row in results):
            df = pd.DataFrame(results)
        elif all(isinstance(row, (list, tuple)) for row in results):
            df = pd.DataFrame(results)
        else:
            return f'<div class="no-results">{results}</div>'
        return df.to_html(classes="result-table", index=False)
    if isinstance(results, pd.DataFrame):
        return results.to_html(classes="result-table", index=False)
    return f'<div class="no-results">{results}</div>'

@app.route('/')
def index():
    """Main dashboard page"""
    tables = get_table_names()
    relationships = get_foreign_keys()
    return render_template('enhanced_dashboard.html', 
                         tables=tables, 
                         recent_queries=recent_queries[-10:],
                         relationships=relationships)

@app.route('/query', methods=['POST'])
def run_query():
    """Run a SQL query using the SQL Agent"""
    global query_counter
    
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
        
        # Parse result into table format
        headers, data = parse_sql_result_to_table(formatted_result)
        
        # Generate unique query ID
        query_counter += 1
        query_id = f"query_{query_counter}"
        
        # Store in recent queries
        query_record = {
            'id': query_id,
            'question': question,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'Success',
            'headers': headers,
            'data': data,
            'raw_result': formatted_result
        }
        recent_queries.append(query_record)
        
        # Store result for persistence
        query_results[query_id] = query_record
        
        # Keep only last 20 queries
        if len(recent_queries) > 20:
            old_query = recent_queries.pop(0)
            if old_query['id'] in query_results:
                del query_results[old_query['id']]
        
        return jsonify({
            'success': True,
            'query_id': query_id,
            'question': question,
            'headers': headers,
            'data': data,
            'raw_result': formatted_result,
            'timestamp': query_record['timestamp']
        })
        
    except Exception as e:
        print(f"Error running query: {e}")
        return jsonify({'error': f'Error running query: {str(e)}'})

@app.route('/clear_results', methods=['POST'])
def clear_results():
    """Clear all stored results"""
    global recent_queries, query_results
    recent_queries = []
    query_results = {}
    return jsonify({'success': True, 'message': 'All results cleared'})

@app.route('/tables')
def tables():
    """Show all tables"""
    tables = get_table_names()
    relationships = get_foreign_keys()
    return render_template('enhanced_tables.html', tables=tables, relationships=relationships)

@app.route('/table/<table_name>')
def table_view(table_name):
    """Show data for a specific table"""
    data, columns = get_table_data(table_name)
    schema = get_table_schema(table_name)
    relationships = get_foreign_keys()
    return render_template('enhanced_table_view.html', 
                         table_name=table_name, 
                         data=data, 
                         columns=columns, 
                         schema=schema,
                         relationships=relationships)

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
        'recent_queries': len(recent_queries),
        'total_relationships': len(get_foreign_keys())
    })

def create_enhanced_html_templates():
    """Create the enhanced HTML template files"""
    
    # Enhanced dashboard template
    dashboard_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SQL AI Agent Dashboard</title>
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
            max-width: 1400px;
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
            margin-right: 10px;
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
        
        .btn-danger {
            background: linear-gradient(90deg, #dc3545 0%, #c82333 100%);
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
        
        .result-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .result-table th {
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }
        
        .result-table td {
            padding: 12px;
            border-bottom: 1px solid #e9ecef;
        }
        
        .result-table tr:hover {
            background: #f8f9fa;
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
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
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
            margin-top: 30px;
        }
        
        .query-item {
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 15px;
            background: #f8f9fa;
        }
        
        .query-item h4 {
            color: #333;
            margin-bottom: 10px;
            font-size: 1.1rem;
        }
        
        .query-item p {
            color: #666;
            font-size: 0.9rem;
            margin-bottom: 10px;
        }
        
        .query-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
            background: white;
            border-radius: 4px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .query-table th {
            background: #667eea;
            color: white;
            padding: 8px 12px;
            text-align: left;
            font-size: 0.9rem;
        }
        
        .query-table td {
            padding: 8px 12px;
            border-bottom: 1px solid #e9ecef;
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
        
        .relationships-section {
            background: white;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            margin-top: 30px;
        }
        
        .relationship-item {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 10px;
            border-left: 4px solid #667eea;
        }
        
        .relationship-item strong {
            color: #667eea;
        }
        
        .footer {
            background: #f8f9fa;
            padding: 15px 30px;
            text-align: center;
            border-top: 1px solid #e9ecef;
            color: #666;
            font-size: 0.8rem;
        }
        
        .footer a {
            color: #667eea;
            text-decoration: none;
        }
        
        .footer a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 SQL AI Agent Dashboard</h1>
            <p>Interactive interface with table results and data relationships</p>
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
                <div class="stat-card">
                    <h3 id="total-relationships">-</h3>
                    <p>Relationships</p>
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
                <button id="clear-results-btn" class="btn btn-danger">🗑️ Clear Results</button>
            </div>
            
            <!-- Results -->
            <div id="result-section" class="result-section">
                <h3>📊 Results</h3>
                <div id="result-content"></div>
            </div>
            
            <!-- Recent Queries -->
            <div class="recent-queries">
                <h2>🔄 Recent Queries</h2>
                <div id="recent-queries-list">
                    {% for query in recent_queries %}
                    <div class="query-item">
                        <h4>{{ query.question }}</h4>
                        <p><strong>Time:</strong> {{ query.timestamp }} | <strong>Status:</strong> {{ query.status }}</p>
                        {% if query.headers and query.data %}
                        <table class="query-table">
                            <thead>
                                <tr>
                                    {% for header in query.headers %}
                                    <th>{{ header }}</th>
                                    {% endfor %}
                                </tr>
                            </thead>
                            <tbody>
                                {% for row in query.data[:5] %}
                                <tr>
                                    {% for cell in row %}
                                    <td>{{ cell }}</td>
                                    {% endfor %}
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                        {% if query.data|length > 5 %}
                        <p><em>Showing first 5 rows of {{ query.data|length }} total rows</em></p>
                        {% endif %}
                        {% else %}
                        <p>{{ query.raw_result[:200] }}...</p>
                        {% endif %}
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>
        
        <div class="footer">
            Built by <a href="#" onclick="return false;">Prakash</a> | SQL Agent Dashboard v2.0
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
        
        // Clear results
        document.getElementById('clear-results-btn').addEventListener('click', function() {
            if (confirm('Are you sure you want to clear all results?')) {
                clearResults();
            }
        });
        
        function loadStats() {
            fetch('/api/stats')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('total-tables').textContent = data.total_tables;
                    document.getElementById('total-rows').textContent = data.total_rows;
                    document.getElementById('recent-queries-count').textContent = data.recent_queries;
                    document.getElementById('total-relationships').textContent = data.total_relationships;
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
                    // Create table from results
                    let tableHTML = '<div class="success">✅ Query executed successfully!</div><br>';
                    tableHTML += '<table class="result-table">';
                    
                    // Headers
                    tableHTML += '<thead><tr>';
                    data.headers.forEach(header => {
                        tableHTML += `<th>${header}</th>`;
                    });
                    tableHTML += '</tr></thead>';
                    
                    // Data rows
                    tableHTML += '<tbody>';
                    data.data.forEach(row => {
                        tableHTML += '<tr>';
                        row.forEach(cell => {
                            tableHTML += `<td>${cell}</td>`;
                        });
                        tableHTML += '</tr>';
                    });
                    tableHTML += '</tbody></table>';
                    
                    resultContent.innerHTML = tableHTML;
                    
                    // Reload stats
                    loadStats();
                    
                    // Reload page after a delay to show new query in recent queries
                    setTimeout(() => {
                        window.location.reload();
                    }, 3000);
                }
            })
            .catch(error => {
                btn.disabled = false;
                btn.textContent = '🚀 Run Query';
                resultContent.innerHTML = '<div class="error">❌ Error: ' + error.message + '</div>';
            });
        }
        
        function clearResults() {
            fetch('/clear_results', {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    window.location.reload();
                }
            })
            .catch(error => {
                console.error('Error clearing results:', error);
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
    
    # Write template to file
    with open('templates/enhanced_dashboard.html', 'w') as f:
        f.write(dashboard_html)
    
    print("✅ Enhanced HTML templates created successfully!")

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # Create the enhanced HTML templates
    create_enhanced_html_templates()
    
    print("🚀 Starting Enhanced SQL Agent Web Dashboard...")
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