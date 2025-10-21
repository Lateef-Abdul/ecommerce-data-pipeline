import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random
import os

# Set seeds for reproducibility
fake = Faker()
Faker.seed(42)
np.random.seed(42)
random.seed(42)

def generate_customers(n=1000):
    """Generate sample customer data"""
    print(f"📦 Generating {n} customers...")
    
    customers = []
    for i in range(1, n+1):
        customers.append({
            'customer_id': i,
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'email': fake.email(),
            'registration_date': fake.date_between(start_date='-2y', end_date='today'),
            'country': fake.country()
        })
    
    df = pd.DataFrame(customers)
    
    # Ensure directory exists
    os.makedirs('data/sample', exist_ok=True)
    
    df.to_csv('data/sample/customers.csv', index=False)
    print(f"   ✓ Customers saved: {len(df):,} records")
    return df

def generate_products(n=200):
    """Generate sample product data"""
    print(f"📦 Generating {n} products...")
    
    categories = ['Electronics', 'Clothing', 'Home & Garden', 'Books', 
                  'Sports', 'Toys', 'Food & Beverage', 'Health & Beauty']
    
    products = []
    for i in range(1, n+1):
        cost = round(random.uniform(5, 250), 2)
        price = round(cost * random.uniform(1.3, 2.5), 2)
        
        products.append({
            'product_id': i,
            'product_name': f"{fake.word().capitalize()} {fake.word().capitalize()}",
            'category': random.choice(categories),
            'price': price,
            'cost': cost
        })
    
    df = pd.DataFrame(products)
    df.to_csv('data/sample/products.csv', index=False)
    print(f"   ✓ Products saved: {len(df):,} records")
    return df

def generate_orders(n=5000, customers_df=None):
    """Generate sample order data"""
    print(f"📦 Generating {n} orders...")
    
    if customers_df is None:
        customers_df = pd.read_csv('data/sample/customers.csv')
    
    orders = []
    start_date = datetime.now() - timedelta(days=365)
    
    for i in range(1, n+1):
        order_date = start_date + timedelta(
            days=random.randint(0, 365),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        orders.append({
            'order_id': i,
            'customer_id': random.choice(customers_df['customer_id'].tolist()),
            'order_date': order_date.strftime('%Y-%m-%d %H:%M:%S'),
            'status': random.choices(
                ['completed', 'cancelled', 'pending', 'shipped'],
                weights=[0.80, 0.10, 0.05, 0.05]
            )[0]
        })
    
    df = pd.DataFrame(orders)
    df.to_csv('data/sample/orders.csv', index=False)
    print(f"   ✓ Orders saved: {len(df):,} records")
    return df

def generate_order_items(orders_df=None, products_df=None):
    """Generate sample order items data"""
    print(f"📦 Generating order items...")
    
    if orders_df is None:
        orders_df = pd.read_csv('data/sample/orders.csv')
    if products_df is None:
        products_df = pd.read_csv('data/sample/products.csv')
    
    order_items = []
    item_id = 1
    
    for order_id in orders_df['order_id']:
        # Each order has 1-5 items
        n_items = random.randint(1, 5)
        
        # Randomly select products for this order
        available_products = products_df['product_id'].tolist()
        selected_products = random.sample(
            available_products, 
            min(n_items, len(available_products))
        )
        
        for product_id in selected_products:
            product = products_df[products_df['product_id'] == product_id].iloc[0]
            
            order_items.append({
                'order_item_id': item_id,
                'order_id': order_id,
                'product_id': product_id,
                'quantity': random.randint(1, 5),
                'unit_price': product['price']
            })
            item_id += 1
    
    df = pd.DataFrame(order_items)
    df.to_csv('data/sample/order_items.csv', index=False)
    print(f"   ✓ Order items saved: {len(df):,} records")
    return df

def main():
    """Generate all sample data"""
    print("\n" + "=" * 60)
    print("🚀 GENERATING SAMPLE E-COMMERCE DATA")
    print("=" * 60 + "\n")
    
    # Generate data
    customers = generate_customers(1000)
    products = generate_products(200)
    orders = generate_orders(5000, customers)
    order_items = generate_order_items(orders, products)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"   Customers:    {len(customers):>8,}")
    print(f"   Products:     {len(products):>8,}")
    print(f"   Orders:       {len(orders):>8,}")
    print(f"   Order Items:  {len(order_items):>8,}")
    print(f"\n   📁 All files saved to: data/sample/")
    print("=" * 60 + "\n")
    
    print("✅ Data generation complete!")

if __name__ == "__main__":
    main()