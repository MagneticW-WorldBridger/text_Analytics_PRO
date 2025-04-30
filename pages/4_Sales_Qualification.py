import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_processor import load_data, get_timeline_mapping
from utils.visualizations import create_lead_score_histogram, create_timeline_distribution_chart

# Set page configuration
st.set_page_config(
    page_title="Sales Qualification | Analytics Dashboard",
    page_icon="💼",
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
st.image("https://images.unsplash.com/photo-1559526324-593bc073d938", use_column_width=True)
st.title("Sales Qualification Analysis")
st.subheader("Analysis of lead scores, timelines, and sales readiness")

# Check if data is available
if st.session_state.data.empty:
    st.warning("No sales qualification data available. Please check the data source.")
else:
    # Filter controls
    st.markdown("### Filter Analysis")
    
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    
    with filter_col1:
        lead_score_range = st.slider(
            "Lead score range:",
            min_value=0,
            max_value=5,
            value=(0, 5)
        )
    
    with filter_col2:
        timeline_filter = st.multiselect(
            "Filter by estimated timeline:",
            options=sorted(st.session_state.data['estimated_timeline'].unique().tolist()),
            default=[]
        )
    
    with filter_col3:
        decision_maker_filter = st.multiselect(
            "Filter by decision maker status:",
            options=sorted(st.session_state.data['decision_maker_status'].unique().tolist()),
            default=[]
        )
    
    # Apply filters
    filtered_data = st.session_state.data.copy()
    
    filtered_data = filtered_data[
        (filtered_data['lead_score'] >= lead_score_range[0]) & 
        (filtered_data['lead_score'] <= lead_score_range[1])
    ]
    
    if timeline_filter:
        filtered_data = filtered_data[filtered_data['estimated_timeline'].isin(timeline_filter)]
    
    if decision_maker_filter:
        filtered_data = filtered_data[filtered_data['decision_maker_status'].isin(decision_maker_filter)]
    
    # Display filtered contact count
    st.markdown(f"**{len(filtered_data)} contacts** match your criteria")
    
    # Main sales qualification content
    st.markdown("---")
    
    # Lead score metrics
    st.markdown("### Lead Score Metrics")
    
    metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
    
    with metrics_col1:
        avg_lead_score = filtered_data['lead_score'].mean()
        st.metric("Average Lead Score", f"{avg_lead_score:.1f}")
    
    with metrics_col2:
        high_lead_count = len(filtered_data[filtered_data['lead_score'] >= 4])
        st.metric("High Lead Score Contacts (4-5)", high_lead_count)
    
    with metrics_col3:
        medium_lead_count = len(filtered_data[(filtered_data['lead_score'] >= 2) & (filtered_data['lead_score'] < 4)])
        st.metric("Medium Lead Score Contacts (2-3)", medium_lead_count)
    
    with metrics_col4:
        low_lead_count = len(filtered_data[filtered_data['lead_score'] < 2])
        st.metric("Low Lead Score Contacts (0-1)", low_lead_count)
    
    # Lead score distribution and timeline distribution
    score_col, timeline_col = st.columns(2)
    
    with score_col:
        lead_score_chart = create_lead_score_histogram(filtered_data)
        st.plotly_chart(lead_score_chart, use_container_width=True)
    
    with timeline_col:
        timeline_chart = create_timeline_distribution_chart(filtered_data)
        st.plotly_chart(timeline_chart, use_container_width=True)
    
    # Budget indicator analysis
    st.markdown("### Budget Indicator Analysis")
    
    budget_counts = filtered_data['budget_indicator'].value_counts().reset_index()
    budget_counts.columns = ['Budget Indicator', 'Count']
    
    fig = px.pie(
        budget_counts, 
        values='Count', 
        names='Budget Indicator',
        title='Budget Indicator Distribution',
        color_discrete_sequence=px.colors.sequential.Plasma
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)
    
    # Decision maker status analysis
    st.markdown("### Decision Maker Status Analysis")
    
    decision_maker_counts = filtered_data['decision_maker_status'].value_counts().reset_index()
    decision_maker_counts.columns = ['Decision Maker Status', 'Count']
    
    fig = px.bar(
        decision_maker_counts,
        x='Decision Maker Status',
        y='Count',
        title='Decision Maker Status Distribution',
        color='Count',
        color_continuous_scale=px.colors.sequential.Viridis
    )
    
    fig.update_layout(
        xaxis_title='Decision Maker Status',
        yaxis_title='Number of Contacts'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Lead score by role
    st.markdown("### Lead Score by Role")
    
    role_lead_score = filtered_data.groupby('role')['lead_score'].mean().reset_index()
    role_lead_score = role_lead_score.sort_values('lead_score', ascending=False)
    
    fig = px.bar(
        role_lead_score,
        x='role',
        y='lead_score',
        title='Average Lead Score by Role',
        color='lead_score',
        color_continuous_scale=px.colors.sequential.Viridis
    )
    
    fig.update_layout(
        xaxis_title='Role',
        yaxis_title='Average Lead Score'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Common objections analysis
    st.markdown("### Common Objections Analysis")
    
    # Extract all objections
    all_objections = []
    for objections in filtered_data['objections_to_address'].dropna():
        objections_list = [obj.strip() for obj in objections.split(',')]
        all_objections.extend(objections_list)
    
    # Count objection frequencies
    from collections import Counter
    objection_counts = Counter(all_objections)
    
    # Create a DataFrame for visualization
    objections_df = pd.DataFrame(list(objection_counts.items()), columns=['Objection', 'Count'])
    objections_df = objections_df.sort_values('Count', ascending=True)
    
    # Take top N objections
    top_n = min(10, len(objections_df))
    objections_df = objections_df.tail(top_n)
    
    fig = px.bar(
        objections_df,
        y='Objection',
        x='Count',
        title='Top Objections to Address',
        orientation='h',
        color='Count',
        color_continuous_scale=px.colors.sequential.Reds
    )
    
    fig.update_layout(
        xaxis_title='Frequency',
        yaxis_title='Objection',
        yaxis={'categoryorder': 'total ascending'}
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Top sales prospects
    st.markdown("### Top Sales Prospects")
    
    # Sort by lead score descending
    top_prospects = filtered_data.sort_values('lead_score', ascending=False).head(10)
    top_prospects = top_prospects[[
        'full_name', 'role', 'industry_vertical', 'lead_score', 'estimated_timeline', 
        'decision_maker_status', 'budget_indicator'
    ]]
    
    st.dataframe(top_prospects, use_container_width=True)

# Footer
st.markdown("---")
st.caption("Sales Qualification View | Text Analytics Dashboard")
