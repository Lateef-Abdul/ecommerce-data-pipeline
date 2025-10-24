from sqlalchemy import text
from src.utils.db_connection import db
import pandas as pd

def run_query(query_name, sql):
    """Run a SQL query and display results"""
    print(f"\n{'='*60}")
    print(f"📊 {query_name}")
    print('='*60)
    
    try:
        with db.get_connection() as conn:
            df = pd.read_sql(sql, conn)
            print(df.to_string(index=False))
            print(f"\n✓ {len(df)} rows returned")
    except Exception as e:
        print(f"✗ Error running query: {e}")

def main():
    """Run key analytics queries"""
    
    # Sales Overview
    run_query("Sales Overview - Last 30 Days", """
        SELECT 
            COUNT(DISTINCT order_id) as total_orders,
            COUNT(DISTINCT customer_key) as unique_customers,
            ROUND(SUM(total_amount), 2) as total_revenue,
            ROUND(SUM(profit), 2) as total_profit,
            ROUND(AVG(total_amount), 2) as avg_order_value
        FROM marts.fact_orders
        WHERE order_date >= CURRENT_DATE - INTERVAL '30 days'
            AND status = 'completed';
    """)
    
    # Top Products
    run_query("Top 10 Products by Revenue", """
        SELECT 
            p.product_name,
            p.category,
            SUM(fi.quantity) as units_sold,
            ROUND(SUM(fi.total_price), 2) as revenue
        FROM marts.dim_products p
        JOIN marts.fact_order_items fi ON p.product_key = fi.product_key
        GROUP BY p.product_key, p.product_name, p.category
        ORDER BY revenue DESC
        LIMIT 10;
    """)
    
    # Customer Segments
    run_query("Customer Segmentation", """
        SELECT 
            c.customer_segment,
            COUNT(DISTINCT c.customer_key) as customers,
            ROUND(SUM(f.total_amount), 2) as revenue
        FROM marts.dim_customers c
        LEFT JOIN marts.fact_orders f ON c.customer_key = f.customer_key
        WHERE f.status = 'completed'
        GROUP BY c.customer_segment
        ORDER BY revenue DESC;
    """)

if __name__ == "__main__":
    main()