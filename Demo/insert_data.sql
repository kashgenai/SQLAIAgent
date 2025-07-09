-- Insert Data for Customer, Product, and Offer Tables
-- This script maintains proper relationships between all tables

-- ===========================================
-- INSERT CUSTOMERS (10 customers)
-- ===========================================

INSERT INTO Customer (customer_id, full_name, email, phone_number, address, customer_segment) VALUES
('550e8400-e29b-41d4-a716-446655440001', 'John Smith', 'john.smith@email.com', '+1-555-0101', '123 Main St, New York, NY 10001', 'Premium'),
('550e8400-e29b-41d4-a716-446655440002', 'Sarah Johnson', 'sarah.johnson@email.com', '+1-555-0102', '456 Oak Ave, Los Angeles, CA 90210', 'Standard'),
('550e8400-e29b-41d4-a716-446655440003', 'Michael Brown', 'michael.brown@email.com', '+1-555-0103', '789 Pine Rd, Chicago, IL 60601', 'Premium'),
('550e8400-e29b-41d4-a716-446655440004', 'Emily Davis', 'emily.davis@email.com', '+1-555-0104', '321 Elm St, Houston, TX 77001', 'Standard'),
('550e8400-e29b-41d4-a716-446655440005', 'David Wilson', 'david.wilson@email.com', '+1-555-0105', '654 Maple Dr, Phoenix, AZ 85001', 'Premium'),
('550e8400-e29b-41d4-a716-446655440006', 'Lisa Anderson', 'lisa.anderson@email.com', '+1-555-0106', '987 Cedar Ln, Philadelphia, PA 19101', 'Standard'),
('550e8400-e29b-41d4-a716-446655440007', 'Robert Taylor', 'robert.taylor@email.com', '+1-555-0107', '147 Birch Way, San Antonio, TX 78201', 'Premium'),
('550e8400-e29b-41d4-a716-446655440008', 'Jennifer Martinez', 'jennifer.martinez@email.com', '+1-555-0108', '258 Spruce Ct, San Diego, CA 92101', 'Standard'),
('550e8400-e29b-41d4-a716-446655440009', 'William Garcia', 'william.garcia@email.com', '+1-555-0109', '369 Willow Pl, Dallas, TX 75201', 'Premium'),
('550e8400-e29b-41d4-a716-446655440010', 'Amanda Rodriguez', 'amanda.rodriguez@email.com', '+1-555-0110', '741 Aspen Blvd, San Jose, CA 95101', 'Standard');

-- ===========================================
-- INSERT PRODUCTS (15 products across different categories)
-- ===========================================

INSERT INTO Product (product_id, product_name, sku, category, price, description, available) VALUES
('660e8400-e29b-41d4-a716-446655440001', 'iPhone 15 Pro', 'IPH15PRO-128', 'Electronics', 999.99, 'Latest iPhone with advanced camera system and A17 Pro chip', TRUE),
('660e8400-e29b-41d4-a716-446655440002', 'MacBook Air M2', 'MBA-M2-256', 'Electronics', 1199.99, 'Lightweight laptop with M2 chip, perfect for productivity', TRUE),
('660e8400-e29b-41d4-a716-446655440003', 'Samsung 4K Smart TV', 'SAMS-4K-55', 'Electronics', 799.99, '55-inch 4K Ultra HD Smart TV with HDR', TRUE),
('660e8400-e29b-41d4-a716-446655440004', 'Nike Air Max 270', 'NIKE-AM270-10', 'Footwear', 150.00, 'Comfortable running shoes with Air Max technology', TRUE),
('660e8400-e29b-41d4-a716-446655440005', 'Adidas Ultraboost 22', 'ADID-UB22-9', 'Footwear', 180.00, 'Premium running shoes with responsive cushioning', TRUE),
('660e8400-e29b-41d4-a716-446655440006', 'Levi''s 501 Original Jeans', 'LEVI-501-32', 'Clothing', 89.99, 'Classic straight-fit jeans in dark wash', TRUE),
('660e8400-e29b-41d4-a716-446655440007', 'Nike Dri-FIT T-Shirt', 'NIKE-DFT-L', 'Clothing', 35.00, 'Moisture-wicking athletic t-shirt', TRUE),
('660e8400-e29b-41d4-a716-446655440008', 'Sony WH-1000XM4 Headphones', 'SONY-WH4K', 'Electronics', 349.99, 'Wireless noise-canceling headphones', TRUE),
('660e8400-e29b-41d4-a716-446655440009', 'Instant Pot Duo 7-in-1', 'INST-DUO-6', 'Home & Kitchen', 89.99, '7-in-1 electric pressure cooker', TRUE),
('660e8400-e29b-41d4-a716-446655440010', 'Dyson V15 Detect Vacuum', 'DYSN-V15', 'Home & Kitchen', 699.99, 'Cordless vacuum with laser detection', TRUE),
('660e8400-e29b-41d4-a716-446655440011', 'Canon EOS R6 Camera', 'CANO-R6-B', 'Electronics', 2499.99, 'Full-frame mirrorless camera with 4K video', TRUE),
('660e8400-e29b-41d4-a716-446655440012', 'Lululemon Align Leggings', 'LULU-ALN-6', 'Clothing', 98.00, 'Ultra-soft high-rise leggings', TRUE),
('660e8400-e29b-41d4-a716-446655440013', 'KitchenAid Stand Mixer', 'KITC-SM5', 'Home & Kitchen', 379.99, '5-quart stand mixer in various colors', TRUE),
('660e8400-e29b-41d4-a716-446655440014', 'Apple Watch Series 9', 'APLW-S9-45', 'Electronics', 399.99, 'Latest Apple Watch with health monitoring', TRUE),
('660e8400-e29b-41d4-a716-446655440015', 'Patagonia Down Jacket', 'PATA-DJ-M', 'Clothing', 229.00, 'Warm and lightweight down jacket', TRUE);

-- ===========================================
-- INSERT OFFERS (20 offers with various relationships)
-- ===========================================

INSERT INTO Offer (offer_id, offer_title, offer_description, offer_type, discount_percentage, fixed_discount_amount, effective_date, expiration_date, status, customer_id, product_id) VALUES
-- Customer-specific offers (Premium customers get better deals)
('770e8400-e29b-41d4-a716-446655440001', 'Premium Customer iPhone Discount', 'Exclusive 15% off for premium customers', 'Percentage', 15.00, NULL, '2024-01-01', '2024-12-31', 'Active', '550e8400-e29b-41d4-a716-446655440001', '660e8400-e29b-41d4-a716-446655440001'),
('770e8400-e29b-41d4-a716-446655440002', 'MacBook Air Special', '20% off MacBook Air for premium members', 'Percentage', 20.00, NULL, '2024-01-01', '2024-12-31', 'Active', '550e8400-e29b-41d4-a716-446655440003', '660e8400-e29b-41d4-a716-446655440002'),
('770e8400-e29b-41d4-a716-446655440003', 'Electronics Bundle Deal', '25% off Samsung TV for loyal customers', 'Percentage', 25.00, NULL, '2024-01-01', '2024-12-31', 'Active', '550e8400-e29b-41d4-a716-446655440005', '660e8400-e29b-41d4-a716-446655440003'),
('770e8400-e29b-41d4-a716-446655440004', 'Premium Headphones Offer', '30% off Sony headphones for premium segment', 'Percentage', 30.00, NULL, '2024-01-01', '2024-12-31', 'Active', '550e8400-e29b-41d4-a716-446655440007', '660e8400-e29b-41d4-a716-446655440008'),
('770e8400-e29b-41d4-a716-446655440005', 'Camera Enthusiast Deal', '15% off Canon camera for photography lovers', 'Percentage', 15.00, NULL, '2024-01-01', '2024-12-31', 'Active', '550e8400-e29b-41d4-a716-446655440009', '660e8400-e29b-41d4-a716-446655440011'),

-- Standard customer offers (smaller discounts)
('770e8400-e29b-41d4-a716-446655440006', 'Welcome Nike Offer', '10% off Nike shoes for new customers', 'Percentage', 10.00, NULL, '2024-01-01', '2024-12-31', 'Active', '550e8400-e29b-41d4-a716-446655440002', '660e8400-e29b-41d4-a716-446655440004'),
('770e8400-e29b-41d4-a716-446655440007', 'Adidas Running Deal', '12% off Adidas running shoes', 'Percentage', 12.00, NULL, '2024-01-01', '2024-12-31', 'Active', '550e8400-e29b-41d4-a716-446655440004', '660e8400-e29b-41d4-a716-446655440005'),
('770e8400-e29b-41d4-a716-446655440008', 'Denim Special', '8% off Levi''s jeans for fashion lovers', 'Percentage', 8.00, NULL, '2024-01-01', '2024-12-31', 'Active', '550e8400-e29b-41d4-a716-446655440006', '660e8400-e29b-41d4-a716-446655440006'),
('770e8400-e29b-41d4-a716-446655440009', 'Athletic Wear Discount', '15% off Nike athletic wear', 'Percentage', 15.00, NULL, '2024-01-01', '2024-12-31', 'Active', '550e8400-e29b-41d4-a716-446655440008', '660e8400-e29b-41d4-a716-446655440007'),
('770e8400-e29b-41d4-a716-446655440010', 'Lululemon Special', '10% off premium leggings', 'Percentage', 10.00, NULL, '2024-01-01', '2024-12-31', 'Active', '550e8400-e29b-41d4-a716-446655440010', '660e8400-e29b-41d4-a716-446655440012'),

-- Fixed amount discounts
('770e8400-e29b-41d4-a716-446655440011', 'Kitchen Savings', '$50 off Instant Pot for home chefs', 'Fixed', NULL, 50.00, '2024-01-01', '2024-12-31', 'Active', '550e8400-e29b-41d4-a716-446655440001', '660e8400-e29b-41d4-a716-446655440009'),
('770e8400-e29b-41d4-a716-446655440012', 'Vacuum Cleaner Deal', '$100 off Dyson vacuum for clean homes', 'Fixed', NULL, 100.00, '2024-01-01', '2024-12-31', 'Active', '550e8400-e29b-41d4-a716-446655440003', '660e8400-e29b-41d4-a716-446655440010'),
('770e8400-e29b-41d4-a716-446655440013', 'Mixer Special', '$75 off KitchenAid mixer for bakers', 'Fixed', NULL, 75.00, '2024-01-01', '2024-12-31', 'Active', '550e8400-e29b-41d4-a716-446655440005', '660e8400-e29b-41d4-a716-446655440013'),
('770e8400-e29b-41d4-a716-446655440014', 'Apple Watch Deal', '$50 off Apple Watch for tech enthusiasts', 'Fixed', NULL, 50.00, '2024-01-01', '2024-12-31', 'Active', '550e8400-e29b-41d4-a716-446655440007', '660e8400-e29b-41d4-a716-446655440014'),
('770e8400-e29b-41d4-a716-446655440015', 'Outdoor Gear Discount', '$30 off Patagonia jacket for adventurers', 'Fixed', NULL, 30.00, '2024-01-01', '2024-12-31', 'Active', '550e8400-e29b-41d4-a716-446655440009', '660e8400-e29b-41d4-a716-446655440015'),

-- General offers (no specific customer)
('770e8400-e29b-41d4-a716-446655440016', 'Flash Sale - Electronics', '20% off all electronics for limited time', 'Percentage', 20.00, NULL, '2024-06-01', '2024-06-30', 'Active', NULL, '660e8400-e29b-41d4-a716-446655440001'),
('770e8400-e29b-41d4-a716-446655440017', 'Summer Clothing Sale', '25% off all clothing items', 'Percentage', 25.00, NULL, '2024-06-01', '2024-08-31', 'Active', NULL, '660e8400-e29b-41d4-a716-446655440006'),
('770e8400-e29b-41d4-a716-446655440018', 'Home & Kitchen Clearance', '$100 off all home appliances', 'Fixed', NULL, 100.00, '2024-07-01', '2024-07-31', 'Active', NULL, '660e8400-e29b-41d4-a716-446655440009'),
('770e8400-e29b-41d4-a716-446655440019', 'Footwear Festival', '15% off all shoes and sneakers', 'Percentage', 15.00, NULL, '2024-08-01', '2024-08-31', 'Active', NULL, '660e8400-e29b-41d4-a716-446655440004'),
('770e8400-e29b-41d4-a716-446655440020', 'Tech Gadgets Special', '$200 off premium tech products', 'Fixed', NULL, 200.00, '2024-09-01', '2024-09-30', 'Active', NULL, '660e8400-e29b-41d4-a716-446655440002');

-- ===========================================
-- VERIFICATION QUERIES
-- ===========================================

-- Count records in each table
SELECT 'Customer' as table_name, COUNT(*) as record_count FROM Customer
UNION ALL
SELECT 'Product' as table_name, COUNT(*) as record_count FROM Product
UNION ALL
SELECT 'Offer' as table_name, COUNT(*) as record_count FROM Offer;

-- Show customer segments and their offer counts
SELECT 
    c.customer_segment,
    COUNT(c.customer_id) as customer_count,
    COUNT(o.offer_id) as offer_count
FROM Customer c
LEFT JOIN Offer o ON c.customer_id = o.customer_id
GROUP BY c.customer_segment;

-- Show products with their offer counts
SELECT 
    p.product_name,
    p.category,
    p.price,
    COUNT(o.offer_id) as offer_count
FROM Product p
LEFT JOIN Offer o ON p.product_id = o.product_id
GROUP BY p.product_id, p.product_name, p.category, p.price
ORDER BY offer_count DESC; 