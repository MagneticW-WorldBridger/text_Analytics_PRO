import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_processor import load_data
from utils.visualizations import create_industry_vertical_chart, create_tech_adoption_chart

# Set page configuration
st.set_page_config(
    page_title="Industry Insights | Analytics Dashboard",
    page_icon="🏢",
    layout="wide"
)

# Load data if not in session state
if 'data' not in st.session_state:
    try:
        st.session_state.data = load_data()
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.session_state.data = pd.DataFrame()

# Page header
st.image("https://images.unsplash.com/photo-1526628953301-3e589a6a8b74", use_column_width=True)
st.title("Industry Insights")
st.subheader("Analysis of industry verticals, company sizes, and technology adoption")

# Check if data is available
if st.session_state.data.empty:
    st.warning("No industry data available. Please check the data source.")
else:
    # Filter controls
    st.markdown("### Filter Analysis")
    
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    
    with filter_col1:
        industry_filter = st.multiselect(
            "Filter by industry vertical:",
            options=sorted(st.session_state.data['industry_vertical'].unique().tolist()),
            default=[]
        )
    
    with filter_col2:
        company_size_filter = st.multiselect(
            "Filter by company size:",
            options=sorted(st.session_state.data['company_size_indicator'].unique().tolist()),
            default=[]
        )
    
    with filter_col3:
        tech_adoption_filter = st.multiselect(
            "Filter by tech adoption level:",
            options=sorted(st.session_state.data['tech_adoption_level'].unique().tolist()),
            default=[]
        )
    
    # Apply filters
    filtered_data = st.session_state.data.copy()
    
    if industry_filter:
        filtered_data = filtered_data[filtered_data['industry_vertical'].isin(industry_filter)]
    
    if company_size_filter:
        filtered_data = filtered_data[filtered_data['company_size_indicator'].isin(company_size_filter)]
    
    if tech_adoption_filter:
        filtered_data = filtered_data[filtered_data['tech_adoption_level'].isin(tech_adoption_filter)]
    
    # Display filtered contact count
    st.markdown(f"**{len(filtered_data)} contacts** match your criteria")
    
    # Main industry insights content
    st.markdown("---")
    
    # Industry vertical distribution and technology adoption
    col1, col2 = st.columns(2)
    
    with col1:
        industry_chart = create_industry_vertical_chart(filtered_data)
        st.plotly_chart(industry_chart, use_container_width=True)
    
    with col2:
        tech_adoption_chart = create_tech_adoption_chart(filtered_data)
        st.plotly_chart(tech_adoption_chart, use_container_width=True)
    
    # Company size distribution
    st.markdown("### Company Size Distribution")
    
    company_size_counts = filtered_data['company_size_indicator'].value_counts().reset_index()
    company_size_counts.columns = ['Company Size', 'Count']
    
    # Define order for company sizes
    size_order = ['Micro', 'Small', 'Medium', 'Large', 'Enterprise', 'Unknown']
    
    # Map sizes to order values
    company_size_counts['order'] = company_size_counts['Company Size'].map(
        {size: i for i, size in enumerate(size_order)}
    )
    company_size_counts = company_size_counts.sort_values('order')
    
    fig = px.bar(
        company_size_counts,
        x='Company Size',
        y='Count',
        title='Company Size Distribution',
        color='Company Size',
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    
    fig.update_layout(
        xaxis_title='Company Size',
        yaxis_title='Number of Contacts',
        xaxis={'categoryorder': 'array', 'categoryarray': size_order}
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Industry vs Challenge Category
    st.markdown("### Industry vs Challenge Category")
    
    # Create a crosstab of industry vs challenge category
    industry_challenge = pd.crosstab(
        filtered_data['industry_vertical'], 
        filtered_data['challenge_category']
    ).reset_index()
    
    # Melt the dataframe for visualization
    industry_challenge_melted = pd.melt(
        industry_challenge, 
        id_vars=['industry_vertical'],
        var_name='challenge_category',
        value_name='count'
    )
    
    # Remove zero counts for better visualization
    industry_challenge_melted = industry_challenge_melted[industry_challenge_melted['count'] > 0]
    
    fig = px.bar(
        industry_challenge_melted,
        x='industry_vertical',
        y='count',
        color='challenge_category',
        title='Challenge Categories by Industry',
        barmode='stack'
    )
    
    fig.update_layout(
        xaxis_title='Industry Vertical',
        yaxis_title='Number of Contacts',
        legend_title='Challenge Category'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Tech adoption vs lead score
    st.markdown("### Tech Adoption vs Lead Score")
    
    tech_lead_score = filtered_data.groupby('tech_adoption_level')['lead_score'].mean().reset_index()
    
    # Define order for tech adoption levels
    adoption_order = ['Innovator', 'Early Adopter', 'Early Majority', 'Mainstream', 'Late Majority', 'Laggard', 'Unknown']
    
    # Map adoption levels to order values
    tech_lead_score['order'] = tech_lead_score['tech_adoption_level'].map(
        {level: i for i, level in enumerate(adoption_order)}
    )
    tech_lead_score = tech_lead_score.sort_values('order')
    
    fig = px.bar(
        tech_lead_score,
        x='tech_adoption_level',
        y='lead_score',
        title='Average Lead Score by Tech Adoption Level',
        color='lead_score',
        color_continuous_scale=px.colors.sequential.Viridis
    )
    
    fig.update_layout(
        xaxis_title='Technology Adoption Level',
        yaxis_title='Average Lead Score',
        xaxis={'categoryorder': 'array', 'categoryarray': adoption_order}
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Competitive position analysis
    st.markdown("### Competitive Position Analysis")
    
    # Clean 'Unknown' values for better visualization
    filtered_data_clean = filtered_data.copy()
    filtered_data_clean['competitive_position'] = filtered_data_clean['competitive_position'].replace('Unknown', 'Not Specified')
    
    position_counts = filtered_data_clean['competitive_position'].value_counts().reset_index()
    position_counts.columns = ['Competitive Position', 'Count']
    
    fig = px.pie(
        position_counts, 
        values='Count', 
        names='Competitive Position',
        title='Competitive Position Distribution',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)
    
    # Industry data table
    st.markdown("### Detailed Industry Data")
    
    show_data = st.checkbox("Show detailed industry data table")
    if show_data:
        industry_table = filtered_data[[
            'full_name', 'role', 'industry_vertical', 'company_size_indicator', 
            'tech_adoption_level', 'competitive_position'
        ]]
        st.dataframe(industry_table, use_container_width=True)
    
    # Industry insights summary
    st.markdown("---")
    st.markdown("### Industry Insights Summary")
    
    # Calculate average lead score by industry
    industry_lead_score = filtered_data.groupby('industry_vertical')['lead_score'].mean().reset_index()
    industry_lead_score = industry_lead_score.sort_values('lead_score', ascending=False)
    industry_lead_score.columns = ['Industry Vertical', 'Average Lead Score']
    
    # Calculate technology adoption distribution
    tech_adoption_by_industry = pd.crosstab(
        filtered_data['industry_vertical'],
        filtered_data['tech_adoption_level'],
        normalize='index'
    ).reset_index()
    
    # Display summary tables
    summary_col1, summary_col2 = st.columns(2)
    
    with summary_col1:
        st.markdown("#### Lead Score by Industry")
        st.dataframe(industry_lead_score, use_container_width=True)
    
    with summary_col2:
        st.markdown("#### Top Industry Verticals")
        top_industries = filtered_data['industry_vertical'].value_counts().reset_index()
        top_industries.columns = ['Industry Vertical', 'Count']
        st.dataframe(top_industries, use_container_width=True)

# Footer
st.markdown("---")
st.caption("Industry Insights View | Text Analytics Dashboard")
