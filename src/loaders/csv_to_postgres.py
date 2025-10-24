import pandas as pd
from datetime import datetime
from src.utils.db_connection import db
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CSVLoader:
    """Load CSV files into PostgreSQL staging tables"""
    
    def __init__(self, schema='staging'):
        self.schema = schema
        logger.info(f"CSVLoader initialized for schema: {schema}")
    
    def load_customers(self, csv_path='data/sample/customers.csv'):
        """Load customers from CSV to staging table"""
        logger.info(f"Loading customers from {csv_path}...")
        
        # Read CSV
        df = pd.read_csv(csv_path)
        
        # Add metadata columns
        df['load_timestamp'] = datetime.now()
        df['source_file'] = os.path.basename(csv_path)

        # Load to database
        with db.get_connection() as conn:
            df.to_sql(
                'customers',
                conn,
                schema=self.schema,
                if_exists='append',  # Use 'append' for incremental loads
                index=False,
                method='multi',
                chunksize=1000
            )
        
        logger.info(f"✓ Loaded {len(df):,} customers")
        return len(df)
    
    def load_products(self, csv_path='data/sample/products.csv'):
        """Load products from CSV to staging table"""
        logger.info(f"Loading products from {csv_path}...")
        
        df = pd.read_csv(csv_path)
        df['load_timestamp'] = datetime.now()
        
        with db.get_connection() as conn:
            df.to_sql(
                'products',
                conn,
                schema=self.schema,
                if_exists='replace',
                index=False,
                method='multi',
                chunksize=1000
            )
        
        logger.info(f"✓ Loaded {len(df):,} products")
        return len(df)
    
    def load_orders(self, csv_path='data/sample/orders.csv'):
        """Load orders from CSV to staging table"""
        logger.info(f"Loading orders from {csv_path}...")
        
        df = pd.read_csv(csv_path)
        df['load_timestamp'] = datetime.now()
        df['order_date'] = pd.to_datetime(df['order_date'])
        
        with db.get_connection() as conn:
            df.to_sql(
                'orders',
                conn,
                schema=self.schema,
                if_exists='replace',
                index=False,
                method='multi',
                chunksize=1000
            )
        
        logger.info(f"✓ Loaded {len(df):,} orders")
        return len(df)
    
    def load_order_items(self, csv_path='data/sample/order_items.csv'):
        """Load order items from CSV to staging table"""
        logger.info(f"Loading order items from {csv_path}...")
        
        df = pd.read_csv(csv_path)
        df['load_timestamp'] = datetime.now()
        
        # Remove order_item_id to let database auto-generate it
        if 'order_item_id' in df.columns:
            df = df.drop('order_item_id', axis=1)
        
        with db.get_connection() as conn:
            df.to_sql(
                'order_items',
                conn,
                schema=self.schema,
                if_exists='replace',
                index=False,
                method='multi',
                chunksize=1000
            )
        
        logger.info(f"✓ Loaded {len(df):,} order items")
        return len(df)
    
    def load_all(self, data_dir='data/sample'):
        """Load all CSV files to staging tables"""
        print("\n" + "=" * 60)
        print("🚀 LOADING DATA TO STAGING TABLES")
        print("=" * 60 + "\n")
        
        results = {}
        
        try:
            results['customers'] = self.load_customers(f"{data_dir}/customers.csv")
            results['products'] = self.load_products(f"{data_dir}/products.csv")
            results['orders'] = self.load_orders(f"{data_dir}/orders.csv")
            results['order_items'] = self.load_order_items(f"{data_dir}/order_items.csv")
            
            print("\n" + "=" * 60)
            print("📊 LOAD SUMMARY")
            print("=" * 60)
            for table, count in results.items():
                print(f"   {table:15} {count:>10,} rows")
            print("=" * 60)
            print("✅ ALL DATA LOADED SUCCESSFULLY!\n")
            
            return results
            
        except Exception as e:
            logger.error(f"✗ Error loading data: {e}")
            raise

def main():
    """Main function to run the loader"""
    loader = CSVLoader()
    loader.load_all()
    
    # Verify data in database
    print("\n📋 Verifying data in database...")
    for table in ['customers', 'products', 'orders', 'order_items']:
        count = db.get_table_count('staging', table)
        print(f"   staging.{table:15} {count:>10,} rows")

if __name__ == "__main__":
    main()