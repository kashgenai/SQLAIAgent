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

def insert_customers():
    """Insert customer data"""
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()
    
    customers = [
        ('550e8400-e29b-41d4-a716-446655440001', 'John Smith', 'john.smith@email.com', '+1-555-0101', '123 Main St, New York, NY 10001', 'Premium'),
        ('550e8400-e29b-41d4-a716-446655440002', 'Sarah Johnson', 'sarah.johnson@email.com', '+1-555-0102', '456 Oak Ave, Los Angeles, CA 90210', 'Standard'),
        ('550e8400-e29b-41d4-a716-446655440003', 'Michael Brown', 'michael.brown@email.com', '+1-555-0103', '789 Pine Rd, Chicago, IL 60601', 'Premium'),
        ('550e8400-e29b-41d4-a716-446655440004', 'Emily Davis', 'emily.davis@email.com', '+1-555-0104', '321 Elm St, Houston, TX 77001', 'Standard'),
        ('550e8400-e29b-41d4-a716-446655440005', 'David Wilson', 'david.wilson@email.com', '+1-555-0105', '654 Maple Dr, Phoenix, AZ 85001', 'Premium'),
        ('550e8400-e29b-41d4-a716-446655440006', 'Lisa Anderson', 'lisa.anderson@email.com', '+1-555-0106', '987 Cedar Ln, Philadelphia, PA 19101', 'Standard'),
        ('550e8400-e29b-41d4-a716-446655440007', 'Robert Taylor', 'robert.taylor@email.com', '+1-555-0107', '147 Birch Way, San Antonio, TX 78201', 'Premium'),
        ('550e8400-e29b-41d4-a716-446655440008', 'Jennifer Martinez', 'jennifer.martinez@email.com', '+1-555-0108', '258 Spruce Ct, San Diego, CA 92101', 'Standard'),
        ('550e8400-e29b-41d4-a716-446655440009', 'William Garcia', 'william.garcia@email.com', '+1-555-0109', '369 Willow Pl, Dallas, TX 75201', 'Premium'),
        ('550e8400-e29b-41d4-a716-446655440010', 'Amanda Rodriguez', 'amanda.rodriguez@email.com', '+1-555-0110', '741 Aspen Blvd, San Jose, CA 95101', 'Standard')
    ]
    
    cursor.executemany('''
        INSERT INTO Customer (customer_id, full_name, email, phone_number, address, customer_segment)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', customers)
    
    conn.commit()
    conn.close()
    print(f"✅ Inserted {len(customers)} customers")

def insert_products():
    """Insert product data"""
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()
    
    products = [
        ('660e8400-e29b-41d4-a716-446655440001', 'iPhone 15 Pro', 'IPH15PRO-128', 'Electronics', 999.99, 'Latest iPhone with advanced camera system and A17 Pro chip', True),
        ('660e8400-e29b-41d4-a716-446655440002', 'MacBook Air M2', 'MBA-M2-256', 'Electronics', 1199.99, 'Lightweight laptop with M2 chip, perfect for productivity', True),
        ('660e8400-e29b-41d4-a716-446655440003', 'Samsung 4K Smart TV', 'SAMS-4K-55', 'Electronics', 799.99, '55-inch 4K Ultra HD Smart TV with HDR', True),
        ('660e8400-e29b-41d4-a716-446655440004', 'Nike Air Max 270', 'NIKE-AM270-10', 'Footwear', 150.00, 'Comfortable running shoes with Air Max technology', True),
        ('660e8400-e29b-41d4-a716-446655440005', 'Adidas Ultraboost 22', 'ADID-UB22-9', 'Footwear', 180.00, 'Premium running shoes with responsive cushioning', True),
        ('660e8400-e29b-41d4-a716-446655440006', 'Levi\'s 501 Original Jeans', 'LEVI-501-32', 'Clothing', 89.99, 'Classic straight-fit jeans in dark wash', True),
        ('660e8400-e29b-41d4-a716-446655440007', 'Nike Dri-FIT T-Shirt', 'NIKE-DFT-L', 'Clothing', 35.00, 'Moisture-wicking athletic t-shirt', True),
        ('660e8400-e29b-41d4-a716-446655440008', 'Sony WH-1000XM4 Headphones', 'SONY-WH4K', 'Electronics', 349.99, 'Wireless noise-canceling headphones', True),
        ('660e8400-e29b-41d4-a716-446655440009', 'Instant Pot Duo 7-in-1', 'INST-DUO-6', 'Home & Kitchen', 89.99, '7-in-1 electric pressure cooker', True),
        ('660e8400-e29b-41d4-a716-446655440010', 'Dyson V15 Detect Vacuum', 'DYSN-V15', 'Home & Kitchen', 699.99, 'Cordless vacuum with laser detection', True),
        ('660e8400-e29b-41d4-a716-446655440011', 'Canon EOS R6 Camera', 'CANO-R6-B', 'Electronics', 2499.99, 'Full-frame mirrorless camera with 4K video', True),
        ('660e8400-e29b-41d4-a716-446655440012', 'Lululemon Align Leggings', 'LULU-ALN-6', 'Clothing', 98.00, 'Ultra-soft high-rise leggings', True),
        ('660e8400-e29b-41d4-a716-446655440013', 'KitchenAid Stand Mixer', 'KITC-SM5', 'Home & Kitchen', 379.99, '5-quart stand mixer in various colors', True),
        ('660e8400-e29b-41d4-a716-446655440014', 'Apple Watch Series 9', 'APLW-S9-45', 'Electronics', 399.99, 'Latest Apple Watch with health monitoring', True),
        ('660e8400-e29b-41d4-a716-446655440015', 'Patagonia Down Jacket', 'PATA-DJ-M', 'Clothing', 229.00, 'Warm and lightweight down jacket', True)
    ]
    
    cursor.executemany('''
        INSERT INTO Product (product_id, product_name, sku, category, price, description, available)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', products)
    
    conn.commit()
    conn.close()
    print(f"✅ Inserted {len(products)} products")

def insert_offers():
    """Insert offer data"""
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()
    
    offers = [
        # Customer-specific offers (Premium customers get better deals)
        ('770e8400-e29b-41d4-a716-446655440001', 'Premium Customer iPhone Discount', 'Exclusive 15% off for premium customers', 'Percentage', 15.00, None, '2024-01-01', '2024-12-31', 'Active', '550e8400-e29b-41d4-a716-446655440001', '660e8400-e29b-41d4-a716-446655440001'),
        ('770e8400-e29b-41d4-a716-446655440002', 'MacBook Air Special', '20% off MacBook Air for premium members', 'Percentage', 20.00, None, '2024-01-01', '2024-12-31', 'Active', '550e8400-e29b-41d4-a716-446655440003', '660e8400-e29b-41d4-a716-446655440002'),
        ('770e8400-e29b-41d4-a716-446655440003', 'Electronics Bundle Deal', '25% off Samsung TV for loyal customers', 'Percentage', 25.00, None, '2024-01-01', '2024-12-31', 'Active', '550e8400-e29b-41d4-a716-446655440005', '660e8400-e29b-41d4-a716-446655440003'),
        ('770e8400-e29b-41d4-a716-446655440004', 'Premium Headphones Offer', '30% off Sony headphones for premium segment', 'Percentage', 30.00, None, '2024-01-01', '2024-12-31', 'Active', '550e8400-e29b-41d4-a716-446655440007', '660e8400-e29b-41d4-a716-446655440008'),
        ('770e8400-e29b-41d4-a716-446655440005', 'Camera Enthusiast Deal', '15% off Canon camera for photography lovers', 'Percentage', 15.00, None, '2024-01-01', '2024-12-31', 'Active', '550e8400-e29b-41d4-a716-446655440009', '660e8400-e29b-41d4-a716-446655440011'),
        
        # Standard customer offers (smaller discounts)
        ('770e8400-e29b-41d4-a716-446655440006', 'Welcome Nike Offer', '10% off Nike shoes for new customers', 'Percentage', 10.00, None, '2024-01-01', '2024-12-31', 'Active', '550e8400-e29b-41d4-a716-446655440002', '660e8400-e29b-41d4-a716-446655440004'),
        ('770e8400-e29b-41d4-a716-446655440007', 'Adidas Running Deal', '12% off Adidas running shoes', 'Percentage', 12.00, None, '2024-01-01', '2024-12-31', 'Active', '550e8400-e29b-41d4-a716-446655440004', '660e8400-e29b-41d4-a716-446655440005'),
        ('770e8400-e29b-41d4-a716-446655440008', 'Denim Special', '8% off Levi\'s jeans for fashion lovers', 'Percentage', 8.00, None, '2024-01-01', '2024-12-31', 'Active', '550e8400-e29b-41d4-a716-446655440006', '660e8400-e29b-41d4-a716-446655440006'),
        ('770e8400-e29b-41d4-a716-446655440009', 'Athletic Wear Discount', '15% off Nike athletic wear', 'Percentage', 15.00, None, '2024-01-01', '2024-12-31', 'Active', '550e8400-e29b-41d4-a716-446655440008', '660e8400-e29b-41d4-a716-446655440007'),
        ('770e8400-e29b-41d4-a716-446655440010', 'Lululemon Special', '10% off premium leggings', 'Percentage', 10.00, None, '2024-01-01', '2024-12-31', 'Active', '550e8400-e29b-41d4-a716-446655440010', '660e8400-e29b-41d4-a716-446655440012'),
        
        # Fixed amount discounts
        ('770e8400-e29b-41d4-a716-446655440011', 'Kitchen Savings', '$50 off Instant Pot for home chefs', 'Fixed', None, 50.00, '2024-01-01', '2024-12-31', 'Active', '550e8400-e29b-41d4-a716-446655440001', '660e8400-e29b-41d4-a716-446655440009'),
        ('770e8400-e29b-41d4-a716-446655440012', 'Vacuum Cleaner Deal', '$100 off Dyson vacuum for clean homes', 'Fixed', None, 100.00, '2024-01-01', '2024-12-31', 'Active', '550e8400-e29b-41d4-a716-446655440003', '660e8400-e29b-41d4-a716-446655440010'),
        ('770e8400-e29b-41d4-a716-446655440013', 'Mixer Special', '$75 off KitchenAid mixer for bakers', 'Fixed', None, 75.00, '2024-01-01', '2024-12-31', 'Active', '550e8400-e29b-41d4-a716-446655440005', '660e8400-e29b-41d4-a716-446655440013'),
        ('770e8400-e29b-41d4-a716-446655440014', 'Apple Watch Deal', '$50 off Apple Watch for tech enthusiasts', 'Fixed', None, 50.00, '2024-01-01', '2024-12-31', 'Active', '550e8400-e29b-41d4-a716-446655440007', '660e8400-e29b-41d4-a716-446655440014'),
        ('770e8400-e29b-41d4-a716-446655440015', 'Outdoor Gear Discount', '$30 off Patagonia jacket for adventurers', 'Fixed', None, 30.00, '2024-01-01', '2024-12-31', 'Active', '550e8400-e29b-41d4-a716-446655440009', '660e8400-e29b-41d4-a716-446655440015'),
        
        # General offers (no specific customer)
        ('770e8400-e29b-41d4-a716-446655440016', 'Flash Sale - Electronics', '20% off all electronics for limited time', 'Percentage', 20.00, None, '2024-06-01', '2024-06-30', 'Active', None, '660e8400-e29b-41d4-a716-446655440001'),
        ('770e8400-e29b-41d4-a716-446655440017', 'Summer Clothing Sale', '25% off all clothing items', 'Percentage', 25.00, None, '2024-06-01', '2024-08-31', 'Active', None, '660e8400-e29b-41d4-a716-446655440006'),
        ('770e8400-e29b-41d4-a716-446655440018', 'Home & Kitchen Clearance', '$100 off all home appliances', 'Fixed', None, 100.00, '2024-07-01', '2024-07-31', 'Active', None, '660e8400-e29b-41d4-a716-446655440009'),
        ('770e8400-e29b-41d4-a716-446655440019', 'Footwear Festival', '15% off all shoes and sneakers', 'Percentage', 15.00, None, '2024-08-01', '2024-08-31', 'Active', None, '660e8400-e29b-41d4-a716-446655440004'),
        ('770e8400-e29b-41d4-a716-446655440020', 'Tech Gadgets Special', '$200 off premium tech products', 'Fixed', None, 200.00, '2024-09-01', '2024-09-30', 'Active', None, '660e8400-e29b-41d4-a716-446655440002')
    ]
    
    cursor.executemany('''
        INSERT INTO Offer (offer_id, offer_title, offer_description, offer_type, discount_percentage, fixed_discount_amount, effective_date, expiration_date, status, customer_id, product_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', offers)
    
    conn.commit()
    conn.close()
    print(f"✅ Inserted {len(offers)} offers")

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
    
    # Insert data
    insert_customers()
    insert_products()
    insert_offers()
    
    # Verify the data
    verify_data()
    
    # Show sample data
    show_sample_data()
    
    print("\n" + "="*60)
    print("✅ Database population complete!")
    print("="*60) 