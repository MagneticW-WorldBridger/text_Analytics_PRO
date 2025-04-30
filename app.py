import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils.data_processor import load_data, get_aggregate_metrics, extract_keywords
from utils.visualizations import (
    create_sentiment_distribution_chart, 
    create_challenge_category_chart,
    create_lead_score_histogram,
    create_engagement_vs_enthusiasm_scatter,
    create_keyword_cloud_chart,
    create_completion_rate_gauge,
    create_industry_vertical_chart,
    format_metrics_cards
)

# Set page configuration
st.set_page_config(
    page_title="Contact Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for data
if 'data' not in st.session_state:
    try:
        st.session_state.data = load_data()
        st.session_state.aggregate_metrics = get_aggregate_metrics(st.session_state.data)
        
        # Extract keywords from challenge_keywords
        st.session_state.challenge_keywords = extract_keywords(st.session_state.data, 'challenge_keywords')
        
        # Extract keywords from pain_points
        st.session_state.pain_points = extract_keywords(st.session_state.data, 'pain_points')
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.session_state.data = pd.DataFrame()
        st.session_state.aggregate_metrics = {}
        st.session_state.challenge_keywords = {}
        st.session_state.pain_points = {}

# Header with banner image
st.image("https://images.unsplash.com/photo-1542744173-05336fcc7ad4", use_column_width=True)
st.title("Text Analytics Dashboard")
st.subheader("Interactive visualization of contact engagement and sentiment metrics")

# Display metrics cards
if not st.session_state.data.empty:
    format_metrics_cards(st.session_state.aggregate_metrics)
else:
    st.warning("No data available. Please check the data source.")

# Main dashboard content
if not st.session_state.data.empty:
    # Create tabs for different sections
    tab1, tab2, tab3 = st.tabs(["Overview", "Engagement Metrics", "Keyword Analysis"])
    
    with tab1:
        # Create a 2-column layout
        col1, col2 = st.columns(2)
        
        with col1:
            # Sentiment distribution chart
            sentiment_chart = create_sentiment_distribution_chart(st.session_state.data)
            st.plotly_chart(sentiment_chart, use_container_width=True)
            
            # Challenge category chart
            challenge_chart = create_challenge_category_chart(st.session_state.data)
            st.plotly_chart(challenge_chart, use_container_width=True)
        
        with col2:
            # Lead score histogram
            lead_score_chart = create_lead_score_histogram(st.session_state.data)
            st.plotly_chart(lead_score_chart, use_container_width=True)
            
            # Industry vertical chart
            industry_chart = create_industry_vertical_chart(st.session_state.data)
            st.plotly_chart(industry_chart, use_container_width=True)
    
    with tab2:
        # Engagement vs enthusiasm scatter plot
        engagement_scatter = create_engagement_vs_enthusiasm_scatter(st.session_state.data)
        st.plotly_chart(engagement_scatter, use_container_width=True)
        
        # Create a 2-column layout for completion rate gauge and industry vertical pie chart
        col1, col2 = st.columns(2)
        
        with col1:
            # Completion rate gauge
            completion_gauge = create_completion_rate_gauge(st.session_state.aggregate_metrics['avg_completion_rate'])
            st.plotly_chart(completion_gauge, use_container_width=True)
        
        with col2:
            # Top contacts table
            st.subheader("Top Engaged Contacts")
            top_contacts = st.session_state.data.sort_values('overall_score', ascending=False).head(5)
            st.dataframe(
                top_contacts[['full_name', 'role', 'overall_score', 'lead_score', 'enthusiasm_level']],
                use_container_width=True
            )
    
    with tab3:
        # Create a 2-column layout
        col1, col2 = st.columns(2)
        
        with col1:
            # Challenge keywords chart
            keywords_chart = create_keyword_cloud_chart(st.session_state.challenge_keywords)
            st.plotly_chart(keywords_chart, use_container_width=True)
        
        with col2:
            # Pain points chart
            pain_points_chart = create_keyword_cloud_chart(st.session_state.pain_points)
            st.plotly_chart(pain_points_chart, use_container_width=True, height=500)
    
    # About section
    st.markdown("---")
    st.markdown("""
    ### About this dashboard
    This interactive dashboard visualizes text analytics from contact engagement data. Navigate through the tabs to explore different dimensions of the data:
    
    - **Overview**: High-level metrics and distributions
    - **Engagement Metrics**: Detailed engagement scores and patterns
    - **Keyword Analysis**: Common challenge keywords and pain points
    
    Use the pages in the sidebar to access detailed views for specific analytics areas.
    """)
else:
    st.error("No data available. Please check the data source and try again.")

# Footer
st.markdown("---")
st.caption("Text Analytics Dashboard | Built with Streamlit")

# Help sidebar
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1460925895917-afdab827c52f", use_column_width=True)
    st.title("Dashboard Navigation")
    st.markdown("""
    Use the navigation above to explore different aspects of the contact analytics:
    
    - **Contact Details**: Individual contact profiles and metrics
    - **Sentiment Analysis**: Detailed sentiment breakdowns
    - **Challenge Analysis**: Challenge categorization and impact
    - **Sales Qualification**: Lead scores and sales readiness
    - **Industry Insights**: Industry-specific patterns
    """)
