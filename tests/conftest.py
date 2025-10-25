import sys
from pathlib import Path

import pytest

from src.utils.db_connection import db

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def database_connection():
    """Provide database connection for tests"""
    return db


@pytest.fixture
def sample_data_path():
    """Provide path to sample data"""
    return Path(__file__).parent.parent / "data" / "sample"
