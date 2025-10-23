from sqlalchemy import text
from src.utils.db_connection import db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DimensionLoader:
    """Load dimension tables from staging data"""
    
    def load_dim_customers(self):
        """Transform and load customer dimension"""
        logger.info("Loading dim_customers...")
        
        query = text("""
            -- Clear existing data
            TRUNCATE TABLE marts.dim_customers CASCADE;
            
            -- Load customer dimension
            INSERT INTO marts.dim_customers (
                customer_id, 
                first_name, 
                last_name, 
                full_name,
                email, 
                country, 
                registration_date,
                customer_segment,
                is_active,
                valid_from,
                is_current
            )
            SELECT DISTINCT
                customer_id,
                first_name,
                last_name,
                first_name || ' ' || last_name as full_name,
                email,
                country,
                registration_date,
                CASE 
                    WHEN registration_date < CURRENT_DATE - INTERVAL '1 year' THEN 'Loyal'
                    WHEN registration_date < CURRENT_DATE - INTERVAL '6 months' THEN 'Regular'
                    ELSE 'New'
                END as customer_segment,
                TRUE as is_active,
                CURRENT_TIMESTAMP as valid_from,
                TRUE as is_current
            FROM staging.customers;
        """)
        
        with db.get_connection() as conn:
            result = conn.execute(query)
            count = db.get_table_count('marts', 'dim_customers')
            logger.info(f"✓ Loaded {count:,} customers to dim_customers")
            return count
    
    def load_dim_products(self):
        """Transform and load product dimension"""
        logger.info("Loading dim_products...")
        
        query = text("""
            -- Clear existing data
            TRUNCATE TABLE marts.dim_products CASCADE;

            -- Load product dimension
            INSERT INTO marts.dim_products (
                product_id,
                product_name,
                category,
                price,
                cost,
                margin_percent,
                valid_from,
                is_current
            )
            SELECT DISTINCT
                product_id,
                product_name,
                category,
                price,
                cost,
                ROUND((((price - cost) / NULLIF(price, 0)) * 100)::numeric, 2) as margin_percent,
                CURRENT_TIMESTAMP as valid_from,
                TRUE as is_current
            FROM staging.products;
        """)
        
        with db.get_connection() as conn:
            result = conn.execute(query)
            count = db.get_table_count('marts', 'dim_products')
            logger.info(f"✓ Loaded {count:,} products to dim_products")
            return count
    
    def load_dim_date(self):
        """Generate and load date dimension"""
        logger.info("Loading dim_date...")
        
        query = text("""
            -- Clear existing data
            TRUNCATE TABLE marts.dim_date CASCADE;
            
            -- Generate date dimension from order dates
            INSERT INTO marts.dim_date (
                date_key,
                date,
                year,
                quarter,
                month,
                month_name,
                week,
                day_of_month,
                day_of_week,
                day_name,
                is_weekend,
                is_holiday
            )
            SELECT DISTINCT
                TO_CHAR(order_date::DATE, 'YYYYMMDD')::INTEGER as date_key,
                order_date::DATE as date,
                EXTRACT(YEAR FROM order_date)::INTEGER as year,
                EXTRACT(QUARTER FROM order_date)::INTEGER as quarter,
                EXTRACT(MONTH FROM order_date)::INTEGER as month,
                TRIM(TO_CHAR(order_date, 'Month')) as month_name,
                EXTRACT(WEEK FROM order_date)::INTEGER as week,
                EXTRACT(DAY FROM order_date)::INTEGER as day_of_month,
                EXTRACT(DOW FROM order_date)::INTEGER as day_of_week,
                TRIM(TO_CHAR(order_date, 'Day')) as day_name,
                CASE 
                    WHEN EXTRACT(DOW FROM order_date) IN (0, 6) THEN TRUE 
                    ELSE FALSE 
                END as is_weekend,
                FALSE as is_holiday
            FROM staging.orders
            ORDER BY date;
        """)
        
        with db.get_connection() as conn:
            result = conn.execute(query)
            count = db.get_table_count('marts', 'dim_date')
            logger.info(f"✓ Loaded {count:,} dates to dim_date")
            return count
    
    def load_all_dimensions(self):
        """Load all dimension tables"""
        print("\n" + "=" * 60)
        print("🔄 LOADING DIMENSION TABLES")
        print("=" * 60 + "\n")
        
        results = {}
        results['dim_customers'] = self.load_dim_customers()
        results['dim_products'] = self.load_dim_products()
        results['dim_date'] = self.load_dim_date()
        
        print("\n" + "=" * 60)
        print("📊 DIMENSION LOAD SUMMARY")
        print("=" * 60)
        for table, count in results.items():
            print(f"   {table:20} {count:>10,} rows")
        print("=" * 60)
        print("✅ ALL DIMENSIONS LOADED!\n")
        
        return results

if __name__ == "__main__":
    loader = DimensionLoader()
    loader.load_all_dimensions()