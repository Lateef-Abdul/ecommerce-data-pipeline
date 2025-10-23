from sqlalchemy import text
from src.utils.db_connection import db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FactLoader:
    """Load fact tables from staging data"""
    
    def load_fact_orders(self):
        """Transform and load orders fact table"""
        logger.info("Loading fact_orders...")
        
        query = text("""
            -- Clear existing data
            TRUNCATE TABLE marts.fact_orders CASCADE;
            
            -- Load orders fact
            INSERT INTO marts.fact_orders (
                order_id,
                customer_key,
                order_date_key,
                order_date,
                status,
                total_items,
                total_amount,
                total_cost,
                profit
            )
            SELECT 
                o.order_id,
                dc.customer_key,
                TO_CHAR(o.order_date::DATE, 'YYYYMMDD')::INTEGER as order_date_key,
                o.order_date,
                o.status,
                COALESCE(SUM(oi.quantity), 0) AS total_items,
                COALESCE(SUM(oi.quantity * oi.unit_price), 0) as total_amount,
                COALESCE(SUM(oi.quantity * dp.cost), 0) as total_cost,
                COALESCE(SUM(oi.quantity * oi.unit_price) - SUM(oi.quantity * dp.cost), 0) as profit
            FROM staging.orders o
            LEFT JOIN marts.dim_customers dc ON o.customer_id = dc.customer_id
            LEFT JOIN staging.order_items oi ON o.order_id = oi.order_id
            LEFT JOIN staging.products p ON oi.product_id = p.product_id
            LEFT JOIN marts.dim_products dp ON p.product_id = dp.product_id
            GROUP BY o.order_id, dc.customer_key, o.order_date, o.status;
        """)
        
        with db.get_connection() as conn:
            result = conn.execute(query)
            count = db.get_table_count('marts', 'fact_orders')
            logger.info(f"✓ Loaded {count:,} orders to fact_orders")
            return count
    
    def load_fact_order_items(self):
        """Transform and load order items fact table"""
        logger.info("Loading fact_order_items...")
        
        query = text("""
            -- Clear existing data
            TRUNCATE TABLE marts.fact_order_items CASCADE;
            
            -- Load order items fact
            INSERT INTO marts.fact_order_items (
                order_key,
                product_key,
                order_id,
                product_id,
                quantity,
                unit_price,
                total_price,
                unit_cost,
                total_cost,
                profit
            )
            SELECT 
                fo.order_key,
                dp.product_key,
                oi.order_id,
                oi.product_id,
                oi.quantity,
                oi.unit_price,
                oi.quantity * oi.unit_price as total_price,
                dp.cost as unit_cost,
                oi.quantity * dp.cost as total_cost,
                (oi.quantity * oi.unit_price) - (oi.quantity * dp.cost) as profit
            FROM staging.order_items oi
            JOIN marts.fact_orders fo ON oi.order_id = fo.order_id
            JOIN marts.dim_products dp ON oi.product_id = dp.product_id;
        """)
        
        with db.get_connection() as conn:
            result = conn.execute(query)
            count = db.get_table_count('marts', 'fact_order_items')
            logger.info(f"✓ Loaded {count:,} items to fact_order_items")
            return count
    
    def load_all_facts(self):
        """Load all fact tables"""
        print("\n" + "=" * 60)
        print("🔄 LOADING FACT TABLES")
        print("=" * 60 + "\n")
        
        results = {}
        results['fact_orders'] = self.load_fact_orders()
        results['fact_order_items'] = self.load_fact_order_items()
        
        print("\n" + "=" * 60)
        print("📊 FACT LOAD SUMMARY")
        print("=" * 60)
        for table, count in results.items():
            print(f"   {table:20} {count:>10,} rows")
        print("=" * 60)
        print("✅ ALL FACTS LOADED!\n")
        
        return results

if __name__ == "__main__":
    loader = FactLoader()
    loader.load_all_facts()