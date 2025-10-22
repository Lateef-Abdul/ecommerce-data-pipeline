import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for database and application settings"""
    
    # Database Configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'ecommerce_dw')
    DB_USER = os.getenv('DB_USER', 'dataeng')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'dataeng123')
    
    @property
    def database_url(self):
        """Get database connection URL"""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    def __repr__(self):
        return f"<Config DB={self.DB_NAME}@{self.DB_HOST}:{self.DB_PORT}>"

# Create singleton instance
config = Config()