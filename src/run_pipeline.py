#!/usr/bin/env python3
"""
Complete ETL Pipeline Runner
Orchestrates the entire data pipeline from CSV to Analytics
"""

import logging
import sys
from datetime import datetime

# Import pipeline components
from src.loaders.csv_to_postgres import CSVLoader
from src.transformers.load_dimensions import DimensionLoader
from src.transformers.load_facts import FactLoader
from src.utils.db_connection import db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ETLPipeline:
    """Complete ETL Pipeline orchestrator"""
    
    def __init__(self):
        self.start_time = datetime.now()
        logger.info("ETL Pipeline initialized")
    
    def test_connections(self):
        """Test database connection"""
        logger.info("Testing database connection...")
        if not db.test_connection():
            logger.error("Database connection failed!")
            sys.exit(1)
        logger.info("✓ Database connection successful")
    
    def extract_and_load(self):
        """Extract data from CSV and load to staging"""
        logger.info("=" * 60)
        logger.info("STEP 1: EXTRACT & LOAD TO STAGING")
        logger.info("=" * 60)
        
        loader = CSVLoader()
        results = loader.load_all()
        
        total_rows = sum(results.values())
        logger.info(f"✓ Loaded {total_rows:,} total rows to staging")
        return results
    
    def transform_dimensions(self):
        """Transform and load dimension tables"""
        logger.info("\n" + "=" * 60)
        logger.info("STEP 2: TRANSFORM & LOAD DIMENSIONS")
        logger.info("=" * 60)
        
        dim_loader = DimensionLoader()
        results = dim_loader.load_all_dimensions()
        
        total_rows = sum(results.values())
        logger.info(f"✓ Loaded {total_rows:,} total rows to dimensions")
        return results
    
    def transform_facts(self):
        """Transform and load fact tables"""
        logger.info("\n" + "=" * 60)
        logger.info("STEP 3: TRANSFORM & LOAD FACTS")
        logger.info("=" * 60)
        
        fact_loader = FactLoader()
        results = fact_loader.load_all_facts()
        
        total_rows = sum(results.values())
        logger.info(f"✓ Loaded {total_rows:,} total rows to facts")
        return results
    
    def validate_data(self):
        """Validate data quality"""
        logger.info("\n" + "=" * 60)
        logger.info("STEP 4: DATA VALIDATION")
        logger.info("=" * 60)
        
        validations = {
            'staging.customers': db.get_table_count('staging', 'customers'),
            'staging.products': db.get_table_count('staging', 'products'),
            'staging.orders': db.get_table_count('staging', 'orders'),
            'staging.order_items': db.get_table_count('staging', 'order_items'),
            'marts.dim_customers': db.get_table_count('marts', 'dim_customers'),
            'marts.dim_products': db.get_table_count('marts', 'dim_products'),
            'marts.dim_date': db.get_table_count('marts', 'dim_date'),
            'marts.fact_orders': db.get_table_count('marts', 'fact_orders'),
            'marts.fact_order_items': db.get_table_count('marts', 'fact_order_items'),
        }
        
        logger.info("Table row counts:")
        for table, count in validations.items():
            logger.info(f"  {table:30} {count:>10,} rows")
        
        # Check for data quality issues
        issues = []
        if validations['marts.fact_orders'] == 0:
            issues.append("No orders in fact table")
        if validations['marts.dim_customers'] == 0:
            issues.append("No customers in dimension")
        
        if issues:
            logger.warning(f"⚠️  Data quality issues found: {issues}")
            return False
        
        logger.info("✓ All validations passed")
        return True
    
    def print_summary(self):
        """Print pipeline execution summary"""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        print("\n" + "=" * 60)
        print("🎉 ETL PIPELINE COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"   Start Time:    {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   End Time:      {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Duration:      {duration:.2f} seconds")
        print("=" * 60)
        print("\n📊 Next Steps:")
        print("   1. Run analytics: python src/utils/run_analytics.py")
        print("   2. Query data in PgAdmin: http://localhost:5050")
        print("   3. Explore dashboards (coming in next steps)")
        print("=" * 60 + "\n")
    
    def run(self):
        """Run the complete ETL pipeline"""
        try:
            print("\n" + "=" * 60)
            print("🚀 STARTING ETL PIPELINE")
            print("=" * 60 + "\n")
            
            # Step 1: Test connections
            self.test_connections()
            
            # Step 2: Extract & Load
            self.extract_and_load()
            
            # Step 3: Transform Dimensions
            self.transform_dimensions()
            
            # Step 4: Transform Facts
            self.transform_facts()
            
            # Step 5: Validate
            self.validate_data()
            
            # Summary
            self.print_summary()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Pipeline failed: {e}", exc_info=True)
            return False

def main():
    """Main entry point"""
    pipeline = ETLPipeline()
    success = pipeline.run()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()