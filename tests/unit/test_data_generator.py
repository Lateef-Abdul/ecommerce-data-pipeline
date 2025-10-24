import pytest
import pandas as pd
from pathlib import Path

def test_sample_data_exists(sample_data_path):
    """Test that sample data files exist"""
    assert (sample_data_path / "customers.csv").exists()
    assert (sample_data_path / "products.csv").exists()
    assert (sample_data_path / "orders.csv").exists()
    assert (sample_data_path / "order_items.csv").exists()

def test_customers_data_structure(sample_data_path):
    """Test customers CSV has correct structure"""
    df = pd.read_csv(sample_data_path / "customers.csv")
    
    required_columns = ['customer_id', 'first_name', 'last_name', 'email', 'country']
    for col in required_columns:
        assert col in df.columns
    
    assert len(df) > 0
    assert df['customer_id'].is_unique

def test_products_data_structure(sample_data_path):
    """Test products CSV has correct structure"""
    df = pd.read_csv(sample_data_path / "products.csv")
    
    required_columns = ['product_id', 'product_name', 'category', 'price', 'cost']
    for col in required_columns:
        assert col in df.columns
    
    assert len(df) > 0
    assert df['product_id'].is_unique
    assert (df['price'] >= df['cost']).all()