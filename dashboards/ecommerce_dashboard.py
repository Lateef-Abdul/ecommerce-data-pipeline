import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine, text
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.config import config

# Page configuration
st.set_page_config(
    page_title="E-Commerce Analytics",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_resource
def get_connection():
    """Create database connection"""
    return create_engine(config.database_url)

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_data(query):
    """Load data from database"""
    engine = get_connection()
    return pd.read_sql(query, engine)

def main():
    """Main dashboard function"""
    
    # Title
    st.title("🛍️ E-Commerce Analytics Dashboard")
    st.markdown("---")
    
    # Sidebar
    st.sidebar.header("📊 Filters")
    date_range = st.sidebar.selectbox(
        "Time Period",
        ["Last 7 Days", "Last 30 Days", "Last 90 Days", "All Time"]
    )
    
    # Map selection to days
    days_map = {
        "Last 7 Days": 7,
        "Last 30 Days": 30,
        "Last 90 Days": 90,
        "All Time": 9999
    }
    days = days_map[date_range]
    
    # ===== KPI METRICS =====
    st.header("📈 Key Performance Indicators")
    
    kpi_query = f"""
        SELECT 
            COUNT(DISTINCT order_id) as total_orders,
            COUNT(DISTINCT customer_key) as total_customers,
            COALESCE(SUM(total_amount), 0) as revenue,
            COALESCE(AVG(total_amount), 0) as avg_order_value,
            COALESCE(SUM(profit), 0) as profit
        FROM marts.fact_orders
        WHERE order_date >= CURRENT_DATE - INTERVAL '{days} days'
            AND status = 'completed'
    """
    
    kpis = load_data(kpi_query).iloc[0]
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="Total Orders",
            value=f"{int(kpis['total_orders']):,}",
            delta="Orders placed"
        )
    
    with col2:
        st.metric(
            label="Unique Customers",
            value=f"{int(kpis['total_customers']):,}",
            delta="Active customers"
        )
    
    with col3:
        st.metric(
            label="Total Revenue",
            value=f"${kpis['revenue']:,.2f}",
            delta=f"${kpis['avg_order_value']:.2f} avg"
        )
    
    with col4:
        st.metric(
            label="Total Profit",
            value=f"${kpis['profit']:,.2f}",
            delta=f"{(kpis['profit']/kpis['revenue']*100):.1f}% margin"
        )
    
    with col5:
        st.metric(
            label="Avg Order Value",
            value=f"${kpis['avg_order_value']:.2f}",
            delta="Per order"
        )
    
    st.markdown("---")
    
    # ===== REVENUE TREND =====
    st.header("📊 Revenue Trend Over Time")
    
    trend_query = f"""
        SELECT 
            d.date,
            COALESCE(SUM(f.total_amount), 0) as revenue,
            COALESCE(SUM(f.profit), 0) as profit,
            COUNT(DISTINCT f.order_id) as orders
        FROM marts.dim_date d
        LEFT JOIN marts.fact_orders f ON d.date_key = f.order_date_key 
            AND f.status = 'completed'
        WHERE d.date >= CURRENT_DATE - INTERVAL '{days} days'
        GROUP BY d.date
        ORDER BY d.date
    """
    
    trend_df = load_data(trend_query)
    
    if not trend_df.empty:
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=trend_df['date'],
            y=trend_df['revenue'],
            name='Revenue',
            line=dict(color='#1f77b4', width=2),
            fill='tonexty'
        ))
        
        fig.add_trace(go.Scatter(
            x=trend_df['date'],
            y=trend_df['profit'],
            name='Profit',
            line=dict(color='#2ca02c', width=2)
        ))
        
        fig.update_layout(
            title="Daily Revenue & Profit",
            xaxis_title="Date",
            yaxis_title="Amount ($)",
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # ===== TWO COLUMNS =====
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏆 Top 10 Products by Revenue")
        
        products_query = f"""
            SELECT 
                p.product_name,
                p.category,
                COALESCE(SUM(fi.total_price), 0) as revenue,
                SUM(fi.quantity) as units_sold
            FROM marts.dim_products p
            JOIN marts.fact_order_items fi ON p.product_key = fi.product_key
            JOIN marts.fact_orders fo ON fi.order_key = fo.order_key
            WHERE fo.order_date >= CURRENT_DATE - INTERVAL '{days} days'
                AND fo.status = 'completed'
            GROUP BY p.product_key, p.product_name, p.category
            ORDER BY revenue DESC
            LIMIT 10
        """
        
        products_df = load_data(products_query)
        
        if not products_df.empty:
            fig = px.bar(
                products_df,
                x='revenue',
                y='product_name',
                orientation='h',
                color='category',
                title="Revenue by Product",
                labels={'revenue': 'Revenue ($)', 'product_name': 'Product'}
            )
            fig.update_layout(height=400, showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📦 Revenue by Category")
        
        category_query = f"""
            SELECT 
                p.category,
                COALESCE(SUM(fi.total_price), 0) as revenue,
                COUNT(DISTINCT fi.order_key) as orders
            FROM marts.dim_products p
            JOIN marts.fact_order_items fi ON p.product_key = fi.product_key
            JOIN marts.fact_orders fo ON fi.order_key = fo.order_key
            WHERE fo.order_date >= CURRENT_DATE - INTERVAL '{days} days'
                AND fo.status = 'completed'
            GROUP BY p.category
            ORDER BY revenue DESC
        """
        
        category_df = load_data(category_query)
        
        if not category_df.empty:
            fig = px.pie(
                category_df,
                values='revenue',
                names='category',
                title="Revenue Distribution",
                hole=0.4
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # ===== CUSTOMER ANALYSIS =====
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👥 Customer Segments")
        
        segments_query = f"""
            SELECT 
                c.customer_segment,
                COUNT(DISTINCT c.customer_key) as customers,
                COALESCE(SUM(f.total_amount), 0) as revenue
            FROM marts.dim_customers c
            LEFT JOIN marts.fact_orders f ON c.customer_key = f.customer_key
            WHERE f.order_date >= CURRENT_DATE - INTERVAL '{days} days'
                AND f.status = 'completed'
            GROUP BY c.customer_segment
            ORDER BY revenue DESC
        """
        
        segments_df = load_data(segments_query)
        
        if not segments_df.empty:
            fig = px.bar(
                segments_df,
                x='customer_segment',
                y='revenue',
                color='customer_segment',
                title="Revenue by Customer Segment",
                labels={'revenue': 'Revenue ($)', 'customer_segment': 'Segment'}
            )
            fig.update_layout(height=350, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📍 Top 10 Countries by Revenue")
        
        country_query = f"""
            SELECT 
                c.country,
                COALESCE(SUM(f.total_amount), 0) as revenue
            FROM marts.dim_customers c
            JOIN marts.fact_orders f ON c.customer_key = f.customer_key
            WHERE f.order_date >= CURRENT_DATE - INTERVAL '{days} days'
                AND f.status = 'completed'
            GROUP BY c.country
            ORDER BY revenue DESC
            LIMIT 10
        """
        
        country_df = load_data(country_query)
        
        if not country_df.empty:
            fig = px.bar(
                country_df,
                x='revenue',
                y='country',
                orientation='h',
                title="Revenue by Country",
                labels={'revenue': 'Revenue ($)', 'country': 'Country'}
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # ===== DATA TABLE =====
    st.header("📋 Recent Orders")
    
    orders_query = f"""
        SELECT 
            fo.order_id,
            dc.full_name as customer,
            dc.country,
            fo.order_date,
            fo.status,
            fo.total_items,
            fo.total_amount,
            fo.profit
        FROM marts.fact_orders fo
        JOIN marts.dim_customers dc ON fo.customer_key = dc.customer_key
        WHERE fo.order_date >= CURRENT_DATE - INTERVAL '{days} days'
        ORDER BY fo.order_date DESC
        LIMIT 100
    """
    
    orders_df = load_data(orders_query)
    
    if not orders_df.empty:
        # Format currency columns
        orders_df['total_amount'] = orders_df['total_amount'].apply(lambda x: f"${x:,.2f}")
        orders_df['profit'] = orders_df['profit'].apply(lambda x: f"${x:,.2f}")
        
        st.dataframe(
            orders_df,
            use_container_width=True,
            height=400,
            hide_index=True
        )
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: gray; padding: 20px;'>
            Built with ❤️ using Streamlit | Data updated every 5 minutes
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()