-- Insert Data for Customer, Product, and Offer Tables
-- Sample data with 5 customers, 10 products, and 10 offers

-- ===========================================
-- INSERT CUSTOMERS (5 customers)
-- ===========================================

INSERT INTO Customer (customer_id, full_name, email, phone_number, address, customer_segment) VALUES
('550e8400-e29b-41d4-a716-446655440001', 'John Smith', 'john.smith@email.com', '+1-555-0101', '123 Main St, New York, NY 10001', 'Premium'),
('550e8400-e29b-41d4-a716-446655440002', 'Sarah Johnson', 'sarah.johnson@email.com', '+1-555-0102', '456 Oak Ave, Los Angeles, CA 90210', 'Standard'),
('550e8400-e29b-41d4-a716-446655440003', 'Michael Brown', 'michael.brown@email.com', '+1-555-0103', '789 Pine Rd, Chicago, IL 60601', 'Premium'),
('550e8400-e29b-41d4-a716-446655440004', 'Emily Davis', 'emily.davis@email.com', '+1-555-0104', '321 Elm St, Houston, TX 77001', 'Standard'),
('550e8400-e29b-41d4-a716-446655440005', 'David Wilson', 'david.wilson@email.com', '+1-555-0105', '654 Maple Dr, Phoenix, AZ 85001', 'Premium');

-- ===========================================
-- INSERT PRODUCTS (10 products)
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
('660e8400-e29b-41d4-a716-446655440010', 'Dyson V15 Detect Vacuum', 'DYSN-V15', 'Home & Kitchen', 699.99, 'Cordless vacuum with laser detection', TRUE);

-- ===========================================
-- INSERT OFFERS (10 offers with relationships)
-- ===========================================

INSERT INTO Offer (offer_id, offer_title, offer_description, offer_type, discount_percentage, fixed_discount_amount, effective_date, expiration_date, status, customer_id, product_id) VALUES
-- Customer-specific offers (Premium customers get better deals)
('770e8400-e29b-41d4-a716-446655440001', 'Premium Customer iPhone Discount', 'Exclusive 15% off for premium customers', 'Percentage', 15.00, NULL, '2024-01-01', '2024-12-31', 'Active', '550e8400-e29b-41d4-a716-446655440001', '660e8400-e29b-41d4-a716-446655440001'),
('770e8400-e29b-41d4-a716-446655440002', 'MacBook Air Special', '20% off MacBook Air for premium members', 'Percentage', 20.00, NULL, '2024-01-01', '2024-12-31', 'Active', '550e8400-e29b-41d4-a716-446655440003', '660e8400-e29b-41d4-a716-446655440002'),
('770e8400-e29b-41d4-a716-446655440003', 'Electronics Bundle Deal', '25% off Samsung TV for loyal customers', 'Percentage', 25.00, NULL, '2024-01-01', '2024-12-31', 'Active', '550e8400-e29b-41d4-a716-446655440005', '660e8400-e29b-41d4-a716-446655440003'),

-- Standard customer offers (smaller discounts)
('770e8400-e29b-41d4-a716-446655440004', 'Welcome Nike Offer', '10% off Nike shoes for new customers', 'Percentage', 10.00, NULL, '2024-01-01', '2024-12-31', 'Active', '550e8400-e29b-41d4-a716-446655440002', '660e8400-e29b-41d4-a716-446655440004'),
('770e8400-e29b-41d4-a716-446655440005', 'Adidas Running Deal', '12% off Adidas running shoes', 'Percentage', 12.00, NULL, '2024-01-01', '2024-12-31', 'Active', '550e8400-e29b-41d4-a716-446655440004', '660e8400-e29b-41d4-a716-446655440005'),

-- Fixed amount discounts
('770e8400-e29b-41d4-a716-446655440006', 'Kitchen Savings', '$50 off Instant Pot for home chefs', 'Fixed', NULL, 50.00, '2024-01-01', '2024-12-31', 'Active', '550e8400-e29b-41d4-a716-446655440001', '660e8400-e29b-41d4-a716-446655440009'),
('770e8400-e29b-41d4-a716-446655440007', 'Vacuum Cleaner Deal', '$100 off Dyson vacuum for clean homes', 'Fixed', NULL, 100.00, '2024-01-01', '2024-12-31', 'Active', '550e8400-e29b-41d4-a716-446655440003', '660e8400-e29b-41d4-a716-446655440010'),

-- General offers (no specific customer)
('770e8400-e29b-41d4-a716-446655440008', 'Flash Sale - Electronics', '20% off all electronics for limited time', 'Percentage', 20.00, NULL, '2024-06-01', '2024-06-30', 'Active', NULL, '660e8400-e29b-41d4-a716-446655440008'),
('770e8400-e29b-41d4-a716-446655440009', 'Summer Clothing Sale', '25% off all clothing items', 'Percentage', 25.00, NULL, '2024-06-01', '2024-08-31', 'Active', NULL, '660e8400-e29b-41d4-a716-446655440006'),
('770e8400-e29b-41d4-a716-446655440010', 'Footwear Festival', '15% off all shoes and sneakers', 'Percentage', 15.00, NULL, '2024-08-01', '2024-08-31', 'Active', NULL, '660e8400-e29b-41d4-a716-446655440007'); 