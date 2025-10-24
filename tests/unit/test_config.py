import pytest
from src.utils.config import config

def test_config_has_database_url():
    """Test that config has database URL"""
    assert config.database_url is not None
    assert "postgresql://" in config.database_url

def test_config_has_required_fields():
    """Test that config has all required fields"""
    assert config.DB_HOST is not None
    assert config.DB_PORT is not None
    assert config.DB_NAME is not None
    assert config.DB_USER is not None