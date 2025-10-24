import pytest
from sqlalchemy import text

def test_database_connection(database_connection):
    """Test that database connection works"""
    result = database_connection.test_connection()
    assert result is True

def test_staging_tables_exist(database_connection):
    """Test that staging tables exist"""
    tables = ['customers', 'products', 'orders', 'order_items']
    
    for table in tables:
        query = text(f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'staging' 
                AND table_name = '{table}'
            );
        """)
        
        with database_connection.get_connection() as conn:
            result = conn.execute(query).scalar()
            assert result is True, f"Table staging.{table} does not exist"

def test_marts_tables_exist(database_connection):
    """Test that marts tables exist"""
    tables = ['dim_customers', 'dim_products', 'dim_date', 'fact_orders', 'fact_order_items']
    
    for table in tables:
        query = text(f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'marts' 
                AND table_name = '{table}'
            );
        """)
        
        with database_connection.get_connection() as conn:
            result = conn.execute(query).scalar()
            assert result is True, f"Table marts.{table} does not exist"

def test_staging_has_data(database_connection):
    """Test that staging tables have data"""
    count = database_connection.get_table_count('staging', 'customers')
    assert count > 0, "staging.customers has no data"
    
    count = database_connection.get_table_count('staging', 'orders')
    assert count > 0, "staging.orders has no data"

def test_marts_has_data(database_connection):
    """Test that marts tables have data"""
    count = database_connection.get_table_count('marts', 'dim_customers')
    assert count > 0, "marts.dim_customers has no data"
    
    count = database_connection.get_table_count('marts', 'fact_orders')
    assert count > 0, "marts.fact_orders has no data"

def test_data_quality_no_nulls_in_keys(database_connection):
    """Test that primary keys have no nulls"""
    query = text("""
        SELECT COUNT(*) 
        FROM marts.dim_customers 
        WHERE customer_id IS NULL
    """)
    
    with database_connection.get_connection() as conn:
        result = conn.execute(query).scalar()
        assert result == 0, "Found NULL values in customer_id"

def test_revenue_calculations(database_connection):
    """Test that revenue calculations are correct"""
    query = text("""
        SELECT 
            COUNT(*) as orders_with_negative_revenue
        FROM marts.fact_orders
        WHERE total_amount < 0
    """)
    
    with database_connection.get_connection() as conn:
        result = conn.execute(query).scalar()
        assert result == 0, "Found orders with negative revenue"