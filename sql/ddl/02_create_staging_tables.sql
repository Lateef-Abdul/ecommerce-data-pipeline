-- Staging: Customers
CREATE TABLE IF NOT EXISTS staging.customers (
    customer_id INTEGER PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(255),
    registration_date DATE,
    country VARCHAR(100),
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_file VARCHAR(255)
);

-- Staging: Products
CREATE TABLE IF NOT EXISTS staging.products (
    product_id INTEGER PRIMARY KEY,
    product_name VARCHAR(255),
    category VARCHAR(100),
    price DECIMAL(10, 2),
    cost DECIMAL(10, 2),
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Staging: Orders
CREATE TABLE IF NOT EXISTS staging.orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    order_date TIMESTAMP,
    status VARCHAR(50),
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Staging: Order Items
CREATE TABLE IF NOT EXISTS staging.order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    unit_price DECIMAL(10, 2),
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_customers_email ON staging.customers(email);
CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON staging.orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_date ON staging.orders(order_date);
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON staging.order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON staging.order_items(product_id);

-- Log completion
DO $$
BEGIN
    RAISE NOTICE 'Staging tables created successfully';
END $$;