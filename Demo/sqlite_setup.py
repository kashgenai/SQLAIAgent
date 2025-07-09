import os
import sqlite3
from pathlib import Path

def setup_sqlite_database():
    """Set up SQLite database and show proper path information"""
    
    # Get the current working directory
    current_dir = os.getcwd()
    print(f"Current working directory: {current_dir}")
    
    # Define database path - you can change this to your preferred location
    db_path = "my_database.db"
    
    # Get absolute path
    abs_db_path = os.path.abspath(db_path)
    print(f"Database will be created at: {abs_db_path}")
    
    # Check if database exists
    if os.path.exists(db_path):
        print(f"✅ Database exists at: {abs_db_path}")
        print(f"File size: {os.path.getsize(db_path)} bytes")
    else:
        print(f"❌ Database does not exist yet")
        
        # Create the database
        try:
            conn = sqlite3.connect(db_path)
            print(f"✅ Database created successfully at: {abs_db_path}")
            
            # Create a simple table to test
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS test_table (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insert a test record
            cursor.execute("INSERT INTO test_table (name) VALUES (?)", ("Test Record",))
            conn.commit()
            
            print("✅ Test table created and populated")
            print(f"✅ Database file size: {os.path.getsize(db_path)} bytes")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Error creating database: {e}")
    
    return abs_db_path

def list_database_contents(db_path):
    """List contents of the database"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"\n📋 Database contains {len(tables)} table(s):")
        for table in tables:
            table_name = table[0]
            print(f"  - {table_name}")
            
            # Show table structure
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            print(f"    Columns: {[col[1] for col in columns]}")
            
            # Show sample data
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
            rows = cursor.fetchall()
            print(f"    Sample data: {rows}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error reading database: {e}")

if __name__ == "__main__":
    print("🔧 SQLite Database Setup")
    print("=" * 50)
    
    # Setup database
    db_path = setup_sqlite_database()
    
    # List contents
    list_database_contents(db_path)
    
    print("\n" + "=" * 50)
    print("✅ Setup complete!") 