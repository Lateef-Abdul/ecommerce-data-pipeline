-- ================================================================
-- E-COMMERCE BUSINESS ANALYTICS QUERIES
-- ================================================================

-- Query 1: Sales Overview - Last 30 Days
-- ================================================================
SELECT 
    COUNT(DISTINCT order_id) as total_orders,
    COUNT(DISTINCT customer_key) as unique_customers,
    SUM(total_amount) as total_revenue,
    SUM(profit) as total_profit,
    ROUND(AVG(total_amount), 2) as avg_order_value,
    ROUND((SUM(profit) / NULLIF(SUM(total_amount), 0)) * 100, 2) as profit_margin_pct
FROM marts.fact_orders
WHERE order_date >= CURRENT_DATE - INTERVAL '30 days'
    AND status = 'completed';

-- Query 2: Daily Sales Trend - Last 90 Days
-- ================================================================
SELECT 
    d.date,
    d.day_name,
    d.is_weekend,
    COUNT(DISTINCT f.order_id) as orders,
    SUM(f.total_amount) as revenue,
    SUM(f.profit) as profit,
    ROUND(AVG(f.total_amount), 2) as avg_order_value
FROM marts.dim_date d
LEFT JOIN marts.fact_orders f ON d.date_key = f.order_date_key
WHERE d.date >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY d.date, d.day_name, d.is_weekend
ORDER BY d.date DESC;

-- Query 3: Top 10 Customers by Revenue
-- ================================================================
SELECT 
    c.customer_key,
    c.full_name,
    c.email,
    c.country,
    c.customer_segment,
    COUNT(DISTINCT f.order_id) as total_orders,
    SUM(f.total_amount) as lifetime_value,
    SUM(f.profit) as total_profit,
    ROUND(AVG(f.total_amount), 2) as avg_order_value,
    MAX(f.order_date) as last_order_date
FROM marts.dim_customers c
JOIN marts.fact_orders f ON c.customer_key = f.customer_key
WHERE f.status = 'completed'
GROUP BY c.customer_key, c.full_name, c.email, c.country, c.customer_segment
ORDER BY lifetime_value DESC
LIMIT 10;

-- Query 4: Product Performance by Category
-- ================================================================
SELECT 
    p.category,
    COUNT(DISTINCT p.product_key) as num_products,
    COUNT(DISTINCT fi.order_key) as num_orders,
    SUM(fi.quantity) as total_units_sold,
    SUM(fi.total_price) as total_revenue,
    SUM(fi.profit) as total_profit,
    ROUND(AVG(fi.profit / NULLIF(fi.total_price, 0)) * 100, 2) as avg_margin_pct
FROM marts.dim_products p
JOIN marts.fact_order_items fi ON p.product_key = fi.product_key
GROUP BY p.category
ORDER BY total_revenue DESC;

-- Query 5: Top 20 Products by Revenue
-- ================================================================
SELECT 
    p.product_name,
    p.category,
    p.price,
    p.margin_percent,
    COUNT(DISTINCT fi.order_key) as times_ordered,
    SUM(fi.quantity) as units_sold,
    SUM(fi.total_price) as total_revenue,
    SUM(fi.profit) as total_profit
FROM marts.dim_products p
JOIN marts.fact_order_items fi ON p.product_key = fi.product_key
GROUP BY p.product_key, p.product_name, p.category, p.price, p.margin_percent
ORDER BY total_revenue DESC
LIMIT 20;

-- Query 6: Customer Segmentation Analysis
-- ================================================================
SELECT 
    c.customer_segment,
    COUNT(DISTINCT c.customer_key) as num_customers,
    COUNT(DISTINCT f.order_id) as total_orders,
    SUM(f.total_amount) as total_revenue,
    ROUND(AVG(f.total_amount), 2) as avg_order_value,
    ROUND(COUNT(DISTINCT f.order_id)::NUMERIC / COUNT(DISTINCT c.customer_key), 2) as orders_per_customer
FROM marts.dim_customers c
LEFT JOIN marts.fact_orders f ON c.customer_key = f.customer_key
WHERE f.status = 'completed' OR f.status IS NULL
GROUP BY c.customer_segment
ORDER BY total_revenue DESC;

-- Query 7: Monthly Revenue & Profit Trend
-- ================================================================
SELECT 
    d.year,
    d.month,
    d.month_name,
    COUNT(DISTINCT f.order_id) as orders,
    COUNT(DISTINCT f.customer_key) as customers,
    SUM(f.total_amount) as revenue,
    SUM(f.profit) as profit,
    ROUND((SUM(f.profit) / NULLIF(SUM(f.total_amount), 0)) * 100, 2) as profit_margin_pct
FROM marts.dim_date d
JOIN marts.fact_orders f ON d.date_key = f.order_date_key
WHERE f.status = 'completed'
GROUP BY d.year, d.month, d.month_name
ORDER BY d.year, d.month;

-- Query 8: Order Status Distribution
-- ================================================================
SELECT 
    status,
    COUNT(*) as num_orders,
    ROUND(COUNT(*)::NUMERIC * 100 / SUM(COUNT(*)) OVER (), 2) as percentage,
    SUM(total_amount) as total_value,
    ROUND(AVG(total_amount), 2) as avg_order_value
FROM marts.fact_orders
GROUP BY status
ORDER BY num_orders DESC;

-- Query 9: Weekend vs Weekday Performance
-- ================================================================
SELECT 
    CASE WHEN d.is_weekend THEN 'Weekend' ELSE 'Weekday' END as day_type,
    COUNT(DISTINCT f.order_id) as orders,
    SUM(f.total_amount) as revenue,
    SUM(f.profit) as profit,
    ROUND(AVG(f.total_amount), 2) as avg_order_value
FROM marts.dim_date d
JOIN marts.fact_orders f ON d.date_key = f.order_date_key
WHERE f.status = 'completed'
GROUP BY d.is_weekend
ORDER BY day_type;

-- Query 10: Country Performance
-- ================================================================
SELECT 
    c.country,
    COUNT(DISTINCT c.customer_key) as customers,
    COUNT(DISTINCT f.order_id) as orders,
    SUM(f.total_amount) as revenue,
    SUM(f.profit) as profit,
    ROUND(AVG(f.total_amount), 2) as avg_order_value
FROM marts.dim_customers c
JOIN marts.fact_orders f ON c.customer_key = f.customer_key
WHERE f.status = 'completed'
GROUP BY c.country
ORDER BY revenue DESC
LIMIT 15;