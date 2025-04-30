import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_processor import load_data, extract_keywords
from utils.visualizations import create_sentiment_distribution_chart, create_keyword_cloud_chart

# Set page configuration
st.set_page_config(
    page_title="Sentiment Analysis | Analytics Dashboard",
    page_icon="😊",
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
st.image("https://images.unsplash.com/photo-1504868584819-f8e8b4b6d7e3", use_column_width=True)
st.title("Sentiment Analysis")
st.subheader("Detailed analysis of contact sentiment and emotional indicators")

# Check if data is available
if st.session_state.data.empty:
    st.warning("No sentiment data available. Please check the data source.")
else:
    # Filter controls
    st.markdown("### Filter Analysis")
    
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    
    with filter_col1:
        sentiment_filter = st.multiselect(
            "Filter by sentiment:",
            options=sorted(st.session_state.data['overall_sentiment'].unique().tolist()),
            default=[]
        )
    
    with filter_col2:
        progression_filter = st.multiselect(
            "Filter by progression:",
            options=sorted(st.session_state.data['sentiment_progression'].unique().tolist()),
            default=[]
        )
    
    with filter_col3:
        enthusiasm_range = st.slider(
            "Enthusiasm level range:",
            min_value=0,
            max_value=10,
            value=(0, 10)
        )
    
    # Apply filters
    filtered_data = st.session_state.data.copy()
    
    if sentiment_filter:
        filtered_data = filtered_data[filtered_data['overall_sentiment'].isin(sentiment_filter)]
    
    if progression_filter:
        filtered_data = filtered_data[filtered_data['sentiment_progression'].isin(progression_filter)]
    
    filtered_data = filtered_data[
        (filtered_data['enthusiasm_level'] >= enthusiasm_range[0]) & 
        (filtered_data['enthusiasm_level'] <= enthusiasm_range[1])
    ]
    
    # Display filtered contact count
    st.markdown(f"**{len(filtered_data)} contacts** match your criteria")
    
    # Extract pain points from filtered data
    pain_points = extract_keywords(filtered_data, 'pain_points')
    satisfaction_signals = extract_keywords(filtered_data, 'satisfaction_signals')
    
    # Main sentiment analysis content
    st.markdown("---")
    
    # Overall sentiment distribution
    col1, col2 = st.columns(2)
    
    with col1:
        sentiment_chart = create_sentiment_distribution_chart(filtered_data)
        st.plotly_chart(sentiment_chart, use_container_width=True)
    
    with col2:
        # Enthusiasm level histogram
        fig = px.histogram(
            filtered_data,
            x='enthusiasm_level',
            nbins=10,
            title='Enthusiasm Level Distribution',
            color_discrete_sequence=['#9C27B0']
        )
        fig.update_layout(
            xaxis_title='Enthusiasm Level (0-10)',
            yaxis_title='Number of Contacts',
            bargap=0.2
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Sentiment vs other metrics
    st.markdown("### Sentiment Correlation Analysis")
    
    # Create mapping for sentiment to numeric (for correlation analysis)
    sentiment_mapping = {
        'Positive': 3,
        'Neutral': 2,
        'Mixed': 1.5,
        'Negative': 1
    }
    
    # Add numeric sentiment column for visualization
    filtered_data['sentiment_numeric'] = filtered_data['overall_sentiment'].map(sentiment_mapping)
    
    # Sentiment vs Engagement scatter plot
    fig = px.scatter(
        filtered_data,
        x='sentiment_numeric',
        y='overall_score',
        color='overall_sentiment',
        size='enthusiasm_level',
        hover_name='full_name',
        hover_data=['role', 'challenge_category'],
        title='Sentiment vs Engagement Score',
        labels={'sentiment_numeric': 'Sentiment', 'overall_score': 'Engagement Score'},
        color_discrete_sequence=px.colors.qualitative.Set1
    )
    
    # Add custom x-axis tick labels
    fig.update_layout(
        xaxis = dict(
            tickmode = 'array',
            tickvals = list(sentiment_mapping.values()),
            ticktext = list(sentiment_mapping.keys())
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Pain points and satisfaction signals
    st.markdown("### Sentiment Indicators")
    
    pain_col, satisfaction_col = st.columns(2)
    
    with pain_col:
        st.markdown("#### Top Pain Points")
        pain_chart = create_keyword_cloud_chart(pain_points)
        st.plotly_chart(pain_chart, use_container_width=True)
    
    with satisfaction_col:
        st.markdown("#### Top Satisfaction Signals")
        satisfaction_chart = create_keyword_cloud_chart(satisfaction_signals)
        st.plotly_chart(satisfaction_chart, use_container_width=True)
    
    # Sentiment progression analysis
    st.markdown("### Sentiment Progression Analysis")
    
    # Create donut chart for sentiment progression
    progression_counts = filtered_data['sentiment_progression'].value_counts().reset_index()
    progression_counts.columns = ['Progression', 'Count']
    
    fig = px.pie(
        progression_counts, 
        values='Count', 
        names='Progression',
        title='Sentiment Progression Distribution',
        hole=0.4
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed sentiment data table
    st.markdown("### Detailed Sentiment Data")
    
    show_data = st.checkbox("Show detailed sentiment data table")
    if show_data:
        sentiment_table = filtered_data[[
            'full_name', 'role', 'overall_sentiment', 'sentiment_progression', 
            'enthusiasm_level', 'pain_points', 'satisfaction_signals'
        ]]
        st.dataframe(sentiment_table, use_container_width=True)
    
    # Insights section
    st.markdown("---")
    st.markdown("### Key Sentiment Insights")
    
    insight_col1, insight_col2, insight_col3 = st.columns(3)
    
    with insight_col1:
        # Calculate average enthusiasm by sentiment
        enthusiasm_by_sentiment = filtered_data.groupby('overall_sentiment')['enthusiasm_level'].mean().reset_index()
        enthusiasm_by_sentiment = enthusiasm_by_sentiment.sort_values('enthusiasm_level', ascending=False)
        
        st.markdown("#### Average Enthusiasm by Sentiment")
        st.dataframe(enthusiasm_by_sentiment, use_container_width=True)
    
    with insight_col2:
        # Calculate most common pain points by sentiment
        st.markdown("#### Top Sentiment by Role")
        sentiment_by_role = filtered_data.groupby('role')['overall_sentiment'].agg(
            lambda x: pd.Series.mode(x)[0] if not pd.Series.mode(x).empty else 'Unknown'
        ).reset_index()
        st.dataframe(sentiment_by_role, use_container_width=True)
    
    with insight_col3:
        # Calculate engagement score by sentiment
        engagement_by_sentiment = filtered_data.groupby('overall_sentiment')['overall_score'].mean().reset_index()
        engagement_by_sentiment = engagement_by_sentiment.sort_values('overall_score', ascending=False)
        
        st.markdown("#### Average Engagement by Sentiment")
        st.dataframe(engagement_by_sentiment, use_container_width=True)

# Footer
st.markdown("---")
st.caption("Sentiment Analysis View | Text Analytics Dashboard")
