import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
from collections import Counter
import numpy as np

# Color palette for consistent styling
COLOR_PALETTE = px.colors.qualitative.Plotly

def create_sentiment_distribution_chart(df):
    """
    Create a pie chart showing the distribution of sentiment across contacts
    
    Args:
        df (pd.DataFrame): Processed contact data
        
    Returns:
        plotly.graph_objects.Figure: Pie chart of sentiment distribution
    """
    sentiment_counts = df['overall_sentiment'].value_counts().reset_index()
    sentiment_counts.columns = ['Sentiment', 'Count']
    
    # Map sentiments to a color scale
    sentiment_color_map = {
        'Positive': '#2E8B57',  # SeaGreen
        'Neutral': '#4682B4',   # SteelBlue
        'Negative': '#CD5C5C',  # IndianRed
        'Mixed': '#9370DB'      # MediumPurple
    }
    
    # Get colors for each sentiment in the data
    colors = [sentiment_color_map.get(sentiment, '#808080') for sentiment in sentiment_counts['Sentiment']]
    
    fig = px.pie(
        sentiment_counts, 
        values='Count', 
        names='Sentiment',
        color='Sentiment',
        color_discrete_map={sentiment: color for sentiment, color in zip(sentiment_counts['Sentiment'], colors)},
        title='Overall Sentiment Distribution'
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        legend_title_text='Sentiment',
        legend=dict(orientation='h', yanchor='bottom', y=-0.1, xanchor='center', x=0.5)
    )
    
    return fig

def create_challenge_category_chart(df):
    """
    Create a horizontal bar chart showing the distribution of challenge categories
    
    Args:
        df (pd.DataFrame): Processed contact data
        
    Returns:
        plotly.graph_objects.Figure: Bar chart of challenge categories
    """
    category_counts = df['challenge_category'].value_counts().reset_index()
    category_counts.columns = ['Category', 'Count']
    
    # Sort by count descending
    category_counts = category_counts.sort_values('Count', ascending=True)
    
    fig = px.bar(
        category_counts,
        y='Category',
        x='Count',
        title='Challenge Categories',
        orientation='h',
        color='Count',
        color_continuous_scale=px.colors.sequential.Blues
    )
    
    fig.update_layout(
        xaxis_title='Number of Contacts',
        yaxis_title='Challenge Category',
        yaxis={'categoryorder': 'total ascending'}
    )
    
    return fig

def create_lead_score_histogram(df):
    """
    Create a histogram showing the distribution of lead scores
    
    Args:
        df (pd.DataFrame): Processed contact data
        
    Returns:
        plotly.graph_objects.Figure: Histogram of lead scores
    """
    fig = px.histogram(
        df,
        x='lead_score',
        nbins=5,
        title='Lead Score Distribution',
        color_discrete_sequence=['#1E88E5']
    )
    
    fig.update_layout(
        xaxis_title='Lead Score',
        yaxis_title='Number of Contacts',
        bargap=0.2
    )
    
    return fig

def create_engagement_vs_enthusiasm_scatter(df):
    """
    Create a scatter plot comparing engagement score and enthusiasm level
    
    Args:
        df (pd.DataFrame): Processed contact data
        
    Returns:
        plotly.graph_objects.Figure: Scatter plot
    """
    fig = px.scatter(
        df,
        x='overall_score',
        y='enthusiasm_level',
        color='lead_score',
        size='completion_rate',
        hover_name='full_name',
        hover_data=['role', 'challenge_category', 'overall_sentiment'],
        title='Engagement Score vs. Enthusiasm Level',
        color_continuous_scale=px.colors.sequential.Viridis
    )
    
    fig.update_layout(
        xaxis_title='Engagement Score',
        yaxis_title='Enthusiasm Level',
        coloraxis_colorbar_title='Lead Score'
    )
    
    return fig

def create_keyword_cloud_chart(keyword_counts):
    """
    Create a bar chart visualization of keyword frequency
    
    Args:
        keyword_counts (dict): Dictionary of keywords and their counts
        
    Returns:
        plotly.graph_objects.Figure: Bar chart of keywords
    """
    if not keyword_counts:
        return go.Figure()
    
    # Convert to DataFrame for plotting
    keywords_df = pd.DataFrame(list(keyword_counts.items()), columns=['Keyword', 'Count'])
    keywords_df = keywords_df.sort_values('Count', ascending=True)
    
    # Take top N keywords
    top_n = min(15, len(keywords_df))
    keywords_df = keywords_df.tail(top_n)
    
    fig = px.bar(
        keywords_df,
        y='Keyword',
        x='Count',
        title='Top Keywords',
        orientation='h',
        color='Count',
        color_continuous_scale=px.colors.sequential.Plasma
    )
    
    fig.update_layout(
        xaxis_title='Frequency',
        yaxis_title='Keyword',
        yaxis={'categoryorder': 'total ascending'}
    )
    
    return fig

def create_completion_rate_gauge(avg_completion_rate):
    """
    Create a gauge chart showing average completion rate
    
    Args:
        avg_completion_rate (float): Average completion rate
        
    Returns:
        plotly.graph_objects.Figure: Gauge chart
    """
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=avg_completion_rate,
        title={'text': "Avg. Completion Rate"},
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "#1E88E5"},
            'steps': [
                {'range': [0, 33], 'color': "#EF5350"},
                {'range': [33, 66], 'color': "#FFCA28"},
                {'range': [66, 100], 'color': "#66BB6A"}
            ]
        }
    ))
    
    return fig

def create_industry_vertical_chart(df):
    """
    Create a pie chart showing the distribution of industry verticals
    
    Args:
        df (pd.DataFrame): Processed contact data
        
    Returns:
        plotly.graph_objects.Figure: Pie chart of industry verticals
    """
    # Clean 'Unknown' values for better visualization
    df_clean = df.copy()
    df_clean['industry_vertical'] = df_clean['industry_vertical'].replace('Unknown', 'Not Specified')
    
    vertical_counts = df_clean['industry_vertical'].value_counts().reset_index()
    vertical_counts.columns = ['Industry', 'Count']
    
    fig = px.pie(
        vertical_counts, 
        values='Count', 
        names='Industry',
        title='Industry Vertical Distribution',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        legend_title_text='Industry',
        legend=dict(orientation='h', yanchor='bottom', y=-0.1, xanchor='center', x=0.5)
    )
    
    return fig

def create_tech_adoption_chart(df):
    """
    Create a bar chart showing tech adoption levels
    
    Args:
        df (pd.DataFrame): Processed contact data
        
    Returns:
        plotly.graph_objects.Figure: Bar chart of tech adoption levels
    """
    # Define the order for tech adoption levels
    adoption_order = ['Innovator', 'Early Adopter', 'Early Majority', 'Mainstream', 'Late Majority', 'Laggard', 'Unknown']
    
    # Count occurrences but maintain the defined order
    adoption_counts = df['tech_adoption_level'].value_counts().reindex(adoption_order, fill_value=0).reset_index()
    adoption_counts.columns = ['Adoption Level', 'Count']
    
    # Remove levels with 0 count
    adoption_counts = adoption_counts[adoption_counts['Count'] > 0]
    
    fig = px.bar(
        adoption_counts,
        x='Adoption Level',
        y='Count',
        title='Technology Adoption Levels',
        color='Count',
        color_continuous_scale=px.colors.sequential.Viridis
    )
    
    fig.update_layout(
        xaxis_title='Technology Adoption Level',
        yaxis_title='Number of Contacts',
        xaxis={'categoryorder': 'array', 'categoryarray': adoption_order}
    )
    
    return fig

def create_preferred_channel_chart(df):
    """
    Create a horizontal bar chart showing preferred communication channels
    
    Args:
        df (pd.DataFrame): Processed contact data
        
    Returns:
        plotly.graph_objects.Figure: Bar chart of preferred channels
    """
    channel_counts = df['preferred_channel'].value_counts().reset_index()
    channel_counts.columns = ['Channel', 'Count']
    
    # Sort by count descending
    channel_counts = channel_counts.sort_values('Count', ascending=True)
    
    fig = px.bar(
        channel_counts,
        y='Channel',
        x='Count',
        title='Preferred Communication Channels',
        orientation='h',
        color='Channel',
        color_discrete_sequence=COLOR_PALETTE
    )
    
    fig.update_layout(
        xaxis_title='Number of Contacts',
        yaxis_title='Channel',
        yaxis={'categoryorder': 'total ascending'}
    )
    
    return fig

def create_timeline_distribution_chart(df):
    """
    Create a bar chart showing estimated sales timelines
    
    Args:
        df (pd.DataFrame): Processed contact data
        
    Returns:
        plotly.graph_objects.Figure: Bar chart of timelines
    """
    # Create a mapping for timeline sorting
    timeline_mapping = {
        '30 days': 1, 
        '60 days': 2, 
        '90 days': 3,
        '90+ days': 4,
        '120 days': 5,
        '180 days': 6,
        'Unknown': 7
    }
    
    # Group by timeline and count
    timeline_counts = df['estimated_timeline'].value_counts().reset_index()
    timeline_counts.columns = ['Timeline', 'Count']
    
    # Add sort order
    timeline_counts['sort_order'] = timeline_counts['Timeline'].map(timeline_mapping)
    timeline_counts = timeline_counts.sort_values('sort_order')
    
    fig = px.bar(
        timeline_counts,
        x='Timeline',
        y='Count',
        title='Estimated Timeline Distribution',
        color='Timeline',
        color_discrete_sequence=COLOR_PALETTE
    )
    
    fig.update_layout(
        xaxis_title='Estimated Timeline',
        yaxis_title='Number of Contacts',
        xaxis={'categoryorder': 'array', 'categoryarray': timeline_counts['Timeline']}
    )
    
    return fig

def create_role_distribution_chart(df):
    """
    Create a pie chart showing the distribution of roles
    
    Args:
        df (pd.DataFrame): Processed contact data
        
    Returns:
        plotly.graph_objects.Figure: Pie chart of roles
    """
    role_counts = df['role'].value_counts().reset_index()
    role_counts.columns = ['Role', 'Count']
    
    fig = px.pie(
        role_counts, 
        values='Count', 
        names='Role',
        title='Role Distribution',
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        legend_title_text='Role',
        legend=dict(orientation='h', yanchor='bottom', y=-0.1, xanchor='center', x=0.5)
    )
    
    return fig

def create_correlation_heatmap(df):
    """
    Create a heatmap showing correlations between numeric metrics
    
    Args:
        df (pd.DataFrame): Processed contact data
        
    Returns:
        plotly.graph_objects.Figure: Correlation heatmap
    """
    # Select numeric columns for correlation
    numeric_cols = ['lead_score', 'overall_score', 'enthusiasm_level', 'completion_rate']
    correlation_df = df[numeric_cols].corr()
    
    fig = px.imshow(
        correlation_df,
        text_auto=True,
        color_continuous_scale='RdBu_r',
        title='Correlation Between Key Metrics',
        aspect="auto"
    )
    
    fig.update_layout(
        xaxis_title='Metric',
        yaxis_title='Metric'
    )
    
    return fig

def create_pain_points_chart(df):
    """
    Create a horizontal bar chart showing top pain points
    
    Args:
        df (pd.DataFrame): Processed contact data
        
    Returns:
        plotly.graph_objects.Figure: Bar chart of pain points
    """
    # Extract all pain points
    all_pain_points = []
    for pain_points in df['pain_points'].dropna():
        points = [p.strip() for p in pain_points.split(',')]
        all_pain_points.extend(points)
    
    # Count frequencies
    pain_point_counts = Counter(all_pain_points)
    
    # Convert to DataFrame
    pain_df = pd.DataFrame(list(pain_point_counts.items()), columns=['Pain Point', 'Count'])
    pain_df = pain_df.sort_values('Count', ascending=True)
    
    # Take top 10 pain points
    top_n = min(10, len(pain_df))
    pain_df = pain_df.tail(top_n)
    
    fig = px.bar(
        pain_df,
        y='Pain Point',
        x='Count',
        title='Top Pain Points',
        orientation='h',
        color='Count',
        color_continuous_scale=px.colors.sequential.Reds
    )
    
    fig.update_layout(
        xaxis_title='Frequency',
        yaxis_title='Pain Point',
        yaxis={'categoryorder': 'total ascending'}
    )
    
    return fig

def create_radar_chart(df, contact_id):
    """
    Create a radar chart for a specific contact showing their metrics
    
    Args:
        df (pd.DataFrame): Processed contact data
        contact_id (str): ID of the contact to visualize
        
    Returns:
        plotly.graph_objects.Figure: Radar chart
    """
    # Filter for the specific contact
    contact_df = df[df['contact_id'] == contact_id]
    
    if contact_df.empty:
        return go.Figure()
    
    # Extract metrics
    metrics = {
        'Engagement Score': contact_df['overall_score'].values[0] / 100,
        'Lead Score': contact_df['lead_score'].values[0] / 5,
        'Enthusiasm': contact_df['enthusiasm_level'].values[0] / 10,
        'Completion Rate': contact_df['completion_rate'].values[0] / 100
    }
    
    # Create radar chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=list(metrics.values()),
        theta=list(metrics.keys()),
        fill='toself',
        name=contact_df['full_name'].values[0]
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )
        ),
        title=f"Contact Performance: {contact_df['full_name'].values[0]}",
        showlegend=False
    )
    
    return fig

def format_metrics_cards(metrics):
    """
    Format and display metrics cards in Streamlit
    
    Args:
        metrics (dict): Dictionary of metrics to display
    """
    # Create a 4-column layout
    cols = st.columns(4)
    
    # Display total contacts
    with cols[0]:
        st.metric("Total Contacts", metrics.get('total_contacts', 0))
    
    # Display average engagement score
    with cols[1]:
        st.metric("Avg. Engagement Score", f"{metrics.get('avg_engagement_score', 0):.1f}")
    
    # Display average lead score
    with cols[2]:
        st.metric("Avg. Lead Score", f"{metrics.get('avg_lead_score', 0):.1f}")
    
    # Display average enthusiasm level
    with cols[3]:
        st.metric("Avg. Enthusiasm", f"{metrics.get('avg_enthusiasm_level', 0):.1f}")
