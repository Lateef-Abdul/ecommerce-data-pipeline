-- Dimension: Customers
CREATE TABLE IF NOT EXISTS marts.dim_customers (
    customer_key SERIAL PRIMARY KEY,
    customer_id INTEGER UNIQUE,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    full_name VARCHAR(255),
    email VARCHAR(255),
    country VARCHAR(100),
    registration_date DATE,
    customer_segment VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    valid_from TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    valid_to TIMESTAMP,
    is_current BOOLEAN DEFAULT TRUE
);

-- Dimension: Products
CREATE TABLE IF NOT EXISTS marts.dim_products (
    product_key SERIAL PRIMARY KEY,
    product_id INTEGER UNIQUE,
    product_name VARCHAR(255),
    category VARCHAR(100),
    price DECIMAL(10, 2),
    cost DECIMAL(10, 2),
    margin_percent DECIMAL(5, 2),
    valid_from TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    valid_to TIMESTAMP,
    is_current BOOLEAN DEFAULT TRUE
);

-- Dimension: Date
CREATE TABLE IF NOT EXISTS marts.dim_date (
    date_key INTEGER PRIMARY KEY,
    date DATE UNIQUE,
    year INTEGER,
    quarter INTEGER,
    month INTEGER,
    month_name VARCHAR(20),
    week INTEGER,
    day_of_month INTEGER,
    day_of_week INTEGER,
    day_name VARCHAR(20),
    is_weekend BOOLEAN,
    is_holiday BOOLEAN
);

-- Fact: Orders
CREATE TABLE IF NOT EXISTS marts.fact_orders (
    order_key SERIAL PRIMARY KEY,
    order_id INTEGER UNIQUE,
    customer_key INTEGER REFERENCES marts.dim_customers(customer_key),
    order_date_key INTEGER REFERENCES marts.dim_date(date_key),
    order_date TIMESTAMP,
    status VARCHAR(50),
    total_items INTEGER,
    total_amount DECIMAL(12, 2),
    total_cost DECIMAL(12, 2),
    profit DECIMAL(12, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Fact: Order Items
CREATE TABLE IF NOT EXISTS marts.fact_order_items (
    order_item_key SERIAL PRIMARY KEY,
    order_key INTEGER REFERENCES marts.fact_orders(order_key),
    product_key INTEGER REFERENCES marts.dim_products(product_key),
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    unit_price DECIMAL(10, 2),
    total_price DECIMAL(12, 2),
    unit_cost DECIMAL(10, 2),
    total_cost DECIMAL(12, 2),
    profit DECIMAL(12, 2)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_fact_orders_customer ON marts.fact_orders(customer_key);
CREATE INDEX IF NOT EXISTS idx_fact_orders_date ON marts.fact_orders(order_date_key);
CREATE INDEX IF NOT EXISTS idx_fact_order_items_order ON marts.fact_order_items(order_key);
CREATE INDEX IF NOT EXISTS idx_fact_order_items_product ON marts.fact_order_items(product_key);

-- Log completion
DO $$
BEGIN
    RAISE NOTICE 'Marts tables created successfully';
END $$;