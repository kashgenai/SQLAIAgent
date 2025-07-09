import sqlite3
import os

def create_tables():
    """Create the tables based on the schema"""
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()
    
    # Create Customer table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Customer (
            customer_id TEXT PRIMARY KEY,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone_number TEXT,
            address TEXT,
            customer_segment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create Product table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Product (
            product_id TEXT PRIMARY KEY,
            product_name TEXT NOT NULL,
            sku TEXT UNIQUE NOT NULL,
            category TEXT,
            price REAL NOT NULL,
            description TEXT,
            available BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create Offer table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Offer (
            offer_id TEXT PRIMARY KEY,
            offer_title TEXT NOT NULL,
            offer_description TEXT,
            offer_type TEXT,
            discount_percentage REAL,
            fixed_discount_amount REAL,
            effective_date DATE NOT NULL,
            expiration_date DATE NOT NULL,
            status TEXT NOT NULL,
            customer_id TEXT,
            product_id TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES Customer (customer_id) ON DELETE SET NULL,
            FOREIGN KEY (product_id) REFERENCES Product (product_id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Tables created successfully")

def populate_database():
    """Populate the database with sample data"""
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()
    
    # Read and execute the SQL file
    with open('insert_data.sql', 'r') as file:
        sql_content = file.read()
    
    # Split by semicolon and execute each statement
    statements = sql_content.split(';')
    
    for statement in statements:
        statement = statement.strip()
        if statement and not statement.startswith('--') and not statement.startswith('SELECT'):
            try:
                cursor.execute(statement)
                print(f"✅ Executed: {statement[:50]}...")
            except Exception as e:
                print(f"❌ Error executing: {statement[:50]}... - {e}")
    
    conn.commit()
    conn.close()
    print("✅ Database populated successfully")

def verify_data():
    """Verify the data was inserted correctly"""
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()
    
    print("\n" + "="*60)
    print("📊 DATABASE VERIFICATION")
    print("="*60)
    
    # Count records in each table
    tables = ['Customer', 'Product', 'Offer']
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"📋 {table}: {count} records")
    
    print("\n" + "-"*60)
    print("👥 CUSTOMER SEGMENTS")
    print("-"*60)
    
    # Show customer segments
    cursor.execute('''
        SELECT customer_segment, COUNT(*) as count 
        FROM Customer 
        GROUP BY customer_segment
    ''')
    segments = cursor.fetchall()
    for segment, count in segments:
        print(f"  {segment}: {count} customers")
    
    print("\n" + "-"*60)
    print("🏷️  PRODUCT CATEGORIES")
    print("-"*60)
    
    # Show product categories
    cursor.execute('''
        SELECT category, COUNT(*) as count, AVG(price) as avg_price
        FROM Product 
        GROUP BY category
    ''')
    categories = cursor.fetchall()
    for category, count, avg_price in categories:
        print(f"  {category}: {count} products (avg price: ${avg_price:.2f})")
    
    print("\n" + "-"*60)
    print("🎯 OFFER TYPES")
    print("-"*60)
    
    # Show offer types
    cursor.execute('''
        SELECT offer_type, COUNT(*) as count
        FROM Offer 
        GROUP BY offer_type
    ''')
    offer_types = cursor.fetchall()
    for offer_type, count in offer_types:
        print(f"  {offer_type}: {count} offers")
    
    print("\n" + "-"*60)
    print("🔗 RELATIONSHIP VERIFICATION")
    print("-"*60)
    
    # Check relationships
    cursor.execute('''
        SELECT 
            COUNT(DISTINCT c.customer_id) as customers_with_offers,
            COUNT(DISTINCT p.product_id) as products_with_offers
        FROM Customer c
        LEFT JOIN Offer o ON c.customer_id = o.customer_id
        LEFT JOIN Product p ON o.product_id = p.product_id
    ''')
    result = cursor.fetchone()
    print(f"  Customers with offers: {result[0]}")
    print(f"  Products with offers: {result[1]}")
    
    conn.close()

def show_sample_data():
    """Show sample data from each table"""
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()
    
    print("\n" + "="*60)
    print("📋 SAMPLE DATA")
    print("="*60)
    
    # Show sample customers
    print("\n👥 Sample Customers:")
    cursor.execute('SELECT full_name, email, customer_segment FROM Customer LIMIT 3')
    customers = cursor.fetchall()
    for name, email, segment in customers:
        print(f"  {name} ({email}) - {segment}")
    
    # Show sample products
    print("\n🏷️  Sample Products:")
    cursor.execute('SELECT product_name, category, price FROM Product LIMIT 3')
    products = cursor.fetchall()
    for name, category, price in products:
        print(f"  {name} ({category}) - ${price}")
    
    # Show sample offers
    print("\n🎯 Sample Offers:")
    cursor.execute('''
        SELECT o.offer_title, o.offer_type, c.full_name, p.product_name
        FROM Offer o
        LEFT JOIN Customer c ON o.customer_id = c.customer_id
        LEFT JOIN Product p ON o.product_id = p.product_id
        LIMIT 3
    ''')
    offers = cursor.fetchall()
    for title, offer_type, customer, product in offers:
        customer_name = customer if customer else "General"
        print(f"  {title} ({offer_type}) - {customer_name} → {product}")
    
    conn.close()

if __name__ == "__main__":
    print("🚀 Starting Database Population")
    print("="*60)
    
    # Create tables
    create_tables()
    
    # Populate with data
    populate_database()
    
    # Verify the data
    verify_data()
    
    # Show sample data
    show_sample_data()
    
    print("\n" + "="*60)
    print("✅ Database population complete!")
    print("="*60) 