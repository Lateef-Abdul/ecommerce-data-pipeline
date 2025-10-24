from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from src.utils.config import config
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConnection:
    """Database connection manager using SQLAlchemy"""

    def __init__(self):
        """Initialize database connection"""
        try:
            # ✅ Enable autocommit to avoid idle transactions and lock waits
            self.engine = create_engine(
                config.database_url,
                pool_pre_ping=True,
                echo=False,
                isolation_level="AUTOCOMMIT"
            )
            self.Session = sessionmaker(bind=self.engine)
            logger.info(f"✓ Database connection established: {config.DB_NAME}")
        except Exception as e:
            logger.error(f"✗ Failed to connect to database: {e}")
            raise

    @contextmanager
    def get_connection(self):
        """Context manager for database connections (autocommit mode)"""
        conn = self.engine.connect()
        # Explicitly enforce autocommit for each connection
        conn = conn.execution_options(isolation_level="AUTOCOMMIT")
        try:
            yield conn
        except Exception as e:
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()

    def test_connection(self):
        """Test database connection"""
        try:
            with self.get_connection() as conn:
                result = conn.execute(text("SELECT version();"))
                version = result.fetchone()[0]
                logger.info("✓ Connection test successful")
                logger.info(f"  PostgreSQL version: {version[:50]}...")
                return True
        except Exception as e:
            logger.error(f"✗ Connection test failed: {e}")
            return False

    def get_table_count(self, schema, table):
        """Get row count for a table"""
        try:
            with self.get_connection() as conn:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {schema}.{table}"))
                count = result.fetchone()[0]
                return count
        except Exception as e:
            logger.error(f"Error getting count for {schema}.{table}: {e}")
            return 0

# Create singleton instance
db = DatabaseConnection()

# Test connection when module is imported
if __name__ == "__main__":
    print("Testing database connection...")
    db.test_connection()
