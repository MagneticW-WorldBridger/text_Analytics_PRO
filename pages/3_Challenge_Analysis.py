import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_processor import load_data, extract_keywords
from utils.visualizations import create_challenge_category_chart, create_keyword_cloud_chart

# Set page configuration
st.set_page_config(
    page_title="Challenge Analysis | Analytics Dashboard",
    page_icon="🧩",
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
st.image("https://images.unsplash.com/photo-1496449903678-68ddcb189a24", use_column_width=True)
st.title("Challenge Analysis")
st.subheader("Analysis of contact challenges, categories, and their impact")

# Check if data is available
if st.session_state.data.empty:
    st.warning("No challenge data available. Please check the data source.")
else:
    # Filter controls
    st.markdown("### Filter Analysis")
    
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    
    with filter_col1:
        category_filter = st.multiselect(
            "Filter by challenge category:",
            options=sorted(st.session_state.data['challenge_category'].unique().tolist()),
            default=[]
        )
    
    with filter_col2:
        severity_filter = st.multiselect(
            "Filter by severity level:",
            options=sorted(st.session_state.data['severity_level'].unique().tolist()),
            default=[]
        )
    
    with filter_col3:
        impact_filter = st.multiselect(
            "Filter by impact area:",
            options=sorted(st.session_state.data['impact_area'].unique().tolist()),
            default=[]
        )
    
    # Apply filters
    filtered_data = st.session_state.data.copy()
    
    if category_filter:
        filtered_data = filtered_data[filtered_data['challenge_category'].isin(category_filter)]
    
    if severity_filter:
        filtered_data = filtered_data[filtered_data['severity_level'].isin(severity_filter)]
    
    if impact_filter:
        filtered_data = filtered_data[filtered_data['impact_area'].isin(impact_filter)]
    
    # Display filtered contact count
    st.markdown(f"**{len(filtered_data)} contacts** match your criteria")
    
    # Extract challenge keywords from filtered data
    challenge_keywords = extract_keywords(filtered_data, 'challenge_keywords')
    
    # Main challenge analysis content
    st.markdown("---")
    
    # Challenge category distribution
    col1, col2 = st.columns(2)
    
    with col1:
        challenge_chart = create_challenge_category_chart(filtered_data)
        st.plotly_chart(challenge_chart, use_container_width=True)
    
    with col2:
        # Challenge severity distribution
        severity_counts = filtered_data['severity_level'].value_counts().reset_index()
        severity_counts.columns = ['Severity', 'Count']
        
        # Define a custom order for severity levels
        severity_order = ['Critical', 'High', 'Medium', 'Low']
        severity_counts['order'] = severity_counts['Severity'].map(
            {level: i for i, level in enumerate(severity_order)}
        )
        severity_counts = severity_counts.sort_values('order')
        
        # Create color map
        severity_colors = {
            'Critical': '#d32f2f',
            'High': '#f57c00',
            'Medium': '#fbc02d',
            'Low': '#7cb342'
        }
        
        fig = px.bar(
            severity_counts,
            x='Severity',
            y='Count',
            title='Challenge Severity Distribution',
            color='Severity',
            color_discrete_map=severity_colors
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Challenge keywords
    st.markdown("### Challenge Keywords Analysis")
    
    keyword_chart = create_keyword_cloud_chart(challenge_keywords)
    st.plotly_chart(keyword_chart, use_container_width=True)
    
    # Impact area analysis
    st.markdown("### Impact Area Analysis")
    
    impact_counts = filtered_data['impact_area'].value_counts().reset_index()
    impact_counts.columns = ['Impact Area', 'Count']
    
    fig = px.pie(
        impact_counts, 
        values='Count', 
        names='Impact Area',
        title='Challenge Impact Area Distribution'
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)
    
    # Challenge category vs lead score
    st.markdown("### Challenge Category vs Lead Score")
    
    category_lead_score = filtered_data.groupby('challenge_category')['lead_score'].mean().reset_index()
    category_lead_score = category_lead_score.sort_values('lead_score', ascending=False)
    
    fig = px.bar(
        category_lead_score,
        x='challenge_category',
        y='lead_score',
        title='Average Lead Score by Challenge Category',
        color='lead_score',
        color_continuous_scale=px.colors.sequential.Viridis
    )
    
    fig.update_layout(
        xaxis_title='Challenge Category',
        yaxis_title='Average Lead Score'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Challenge category and severity correlation
    st.markdown("### Challenge Category and Severity Correlation")
    
    # Create a crosstab of category vs severity
    category_severity = pd.crosstab(
        filtered_data['challenge_category'], 
        filtered_data['severity_level']
    ).reset_index()
    
    # Melt the dataframe for visualization
    category_severity_melted = pd.melt(
        category_severity, 
        id_vars=['challenge_category'],
        var_name='severity_level',
        value_name='count'
    )
    
    fig = px.bar(
        category_severity_melted,
        x='challenge_category',
        y='count',
        color='severity_level',
        title='Challenge Categories by Severity Level',
        barmode='stack',
        color_discrete_map=severity_colors
    )
    
    fig.update_layout(
        xaxis_title='Challenge Category',
        yaxis_title='Number of Contacts',
        legend_title='Severity Level'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Raw challenges data table
    st.markdown("### Raw Challenges")
    
    show_data = st.checkbox("Show raw challenge data")
    if show_data:
        challenge_table = filtered_data[[
            'full_name', 'role', 'raw_challenge', 'challenge_category', 
            'severity_level', 'impact_area', 'challenge_keywords'
        ]]
        st.dataframe(challenge_table, use_container_width=True)

# Footer
st.markdown("---")
st.caption("Challenge Analysis View | Text Analytics Dashboard")
