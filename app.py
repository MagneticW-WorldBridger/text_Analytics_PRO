import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import json
from utils.data_processor import load_data, get_aggregate_metrics, extract_keywords, filter_dataframe, search_dataframe
from utils.visualizations import (
    create_sentiment_distribution_chart,
    create_challenge_category_chart,
    create_lead_score_histogram,
    create_engagement_vs_enthusiasm_scatter,
    create_keyword_cloud_chart,
    create_completion_rate_gauge,
    create_industry_vertical_chart,
    create_timeline_distribution_chart,
    create_tech_adoption_chart,
    create_preferred_channel_chart,
    create_role_distribution_chart,
    create_pain_points_chart,
    create_radar_chart,
    create_correlation_heatmap
)

# Set page configuration
st.set_page_config(
    page_title="TEXT ANALYTICS POWERBOARD",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Glasmorphism and Sidebar Visibility Enhancements ---
st.markdown("""
    <style>
    /* Glasmorphism effect for sidebar */
    section[data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.55) !important;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.18);
        backdrop-filter: blur(12px) saturate(180%);
        -webkit-backdrop-filter: blur(12px) saturate(180%);
        border-radius: 16px 0 0 16px;
        border: 1px solid rgba(255, 255, 255, 0.18);
        margin: 8px 0 8px 8px;
    }
    /* Make the sidebar toggle arrow more visible and glasmorphic */
    [data-testid="collapsedControl"] {
        background: rgba(21, 101, 192, 0.95) !important;
        color: white !important;
        border-radius: 50% !important;
        box-shadow: 0 0 32px #42a5f5, 0 0 0 8px rgba(255,255,255,0.25);
        width: 56px !important;
        height: 56px !important;
        min-width: 56px !important;
        min-height: 56px !important;
        max-width: 56px !important;
        max-height: 56px !important;
        left: 10px !important;
        top: 10px !important;
        z-index: 1001 !important;
        border: 3px solid #fff;
        font-size: 2rem !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        opacity: 1 !important;
        transition: box-shadow 0.3s, background 0.3s;
        animation: pulse 1.5s infinite;
    }
    [data-testid="collapsedControl"] svg {
        width: 2.5em !important;
        height: 2.5em !important;
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 16px #1565C0, 0 0 0 8px rgba(255,255,255,0.25); }
        50% { box-shadow: 0 0 48px #42a5f5, 0 0 0 16px rgba(255,255,255,0.18); }
        100% { box-shadow: 0 0 16px #1565C0, 0 0 0 8px rgba(255,255,255,0.25); }
    }
    </style>
""", unsafe_allow_html=True)

# Add a callout at the very top of the main page
st.info("👈 Use the blue glowing arrow on the left to open the navigation menu!", icon="ℹ️")

# Initialize session state variables if they don't exist
# This ensures all necessary session state variables are available
if 'data' not in st.session_state:
    try:
        # Load data
        st.session_state.data = load_data()
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.info("Check if 'attached_assets/data.json' exists and is correctly formatted.")
        # Initialize with empty DataFrame if data loading fails
        st.session_state.data = pd.DataFrame()

# Initialize other session state variables regardless of data loading success
# This ensures all required variables exist even if some are missing
if 'aggregate_metrics' not in st.session_state or not st.session_state.aggregate_metrics:
    try:
        if not st.session_state.data.empty:
            st.session_state.aggregate_metrics = get_aggregate_metrics(st.session_state.data)
        else:
            st.session_state.aggregate_metrics = {
                'total_contacts': 0,
                'avg_engagement_score': 0,
                'avg_lead_score': 0, 
                'avg_enthusiasm_level': 0,
                'avg_completion_rate': 0,
                'sentiment_distribution': {},
                'challenge_categories': {},
                'role_distribution': {},
                'preferred_channels': {},
                'industry_verticals': {}
            }
    except Exception as e:
        st.error(f"Error generating metrics: {str(e)}")
        st.session_state.aggregate_metrics = {
            'total_contacts': len(st.session_state.data) if hasattr(st.session_state, 'data') else 0,
            'avg_engagement_score': 0,
            'avg_lead_score': 0,
            'avg_enthusiasm_level': 0,
            'avg_completion_rate': 0,
            'sentiment_distribution': {},
            'challenge_categories': {},
            'role_distribution': {},
            'preferred_channels': {},
            'industry_verticals': {}
        }

# Initialize keyword analysis
if 'challenge_keywords' not in st.session_state:
    try:
        if not st.session_state.data.empty and 'challenge_keywords' in st.session_state.data.columns:
            st.session_state.challenge_keywords = extract_keywords(st.session_state.data, 'challenge_keywords')
        else:
            st.session_state.challenge_keywords = {}
    except:
        st.session_state.challenge_keywords = {}

if 'pain_points' not in st.session_state:
    try:
        if not st.session_state.data.empty and 'pain_points' in st.session_state.data.columns:
            st.session_state.pain_points = extract_keywords(st.session_state.data, 'pain_points')
        else:
            st.session_state.pain_points = {}
    except:
        st.session_state.pain_points = {}

if 'satisfaction_signals' not in st.session_state:
    try:
        if not st.session_state.data.empty and 'satisfaction_signals' in st.session_state.data.columns:
            st.session_state.satisfaction_signals = extract_keywords(st.session_state.data, 'satisfaction_signals')
        else:
            st.session_state.satisfaction_signals = {}
    except:
        st.session_state.satisfaction_signals = {}

if 'talking_points' not in st.session_state:
    try:
        if not st.session_state.data.empty and 'key_talking_points' in st.session_state.data.columns:
            st.session_state.talking_points = extract_keywords(st.session_state.data, 'key_talking_points')
        else:
            st.session_state.talking_points = {}
    except:
        st.session_state.talking_points = {}

# Initialize UI state variables
if 'selected_contact' not in st.session_state:
    st.session_state.selected_contact = None

if 'filters' not in st.session_state:
    st.session_state.filters = {}

if 'search_term' not in st.session_state:
    st.session_state.search_term = ""

if 'current_view' not in st.session_state:
    st.session_state.current_view = "dashboard"

if 'view_conversation' not in st.session_state:
    st.session_state.view_conversation = False

# Initialize conversations if needed
if 'conversations' not in st.session_state:
    st.session_state.conversations = {}
    
    # Generate sample conversations for each contact
    if not st.session_state.data.empty:
        for _, row in st.session_state.data.iterrows():
            contact_id = row['contact_id']
            
            # Create a conversation based on the contact's challenge and sentiment
            conversation = [
                {
                    "role": "user", 
                    "content": f"Hi there! I'm interested in learning more about how your service can help with {row['raw_challenge']}."
                },
                {
                    "role": "assistant", 
                    "content": f"Thanks for reaching out! I'd be happy to discuss how we can address your challenge with {row['raw_challenge']}. Could you tell me a bit more about your specific needs?"
                },
                {
                    "role": "user", 
                    "content": f"Sure! We're specifically struggling with {row['challenge_keywords'].split(',')[0] if ',' in row['challenge_keywords'] else row['challenge_keywords']}."
                },
                {
                    "role": "assistant", 
                    "content": f"I understand. Many of our clients face similar challenges. Based on what you've shared, our {row['industry_vertical'] if row['industry_vertical'] != 'Unknown' else 'solutions'} would be a good fit for your needs."
                }
            ]
            
            # Add some variation based on sentiment
            if row['overall_sentiment'] == 'Positive':
                conversation.append({
                    "role": "user",
                    "content": "That sounds promising! What would the next steps be?"
                })
            elif row['overall_sentiment'] == 'Negative':
                conversation.append({
                    "role": "user",
                    "content": "I'm not sure if that would work for us. We've tried similar solutions before."
                })
            else:
                conversation.append({
                    "role": "user",
                    "content": "I'd need to learn more about how this would fit our specific situation."
                })
            
            # Store the conversation
            st.session_state.conversations[contact_id] = conversation

# Show warning if data is empty
if st.session_state.data.empty:
    st.warning("No data available. Please check if the data file exists and is accessible.")
    # Display file upload option as a fallback
    uploaded_file = st.file_uploader("Upload a JSON data file", type=['json'])
    if uploaded_file is not None:
        try:
            data_json = json.load(uploaded_file)
            with open('attached_assets/data.json', 'w') as f:
                json.dump(data_json, f)
            st.success("Data uploaded successfully! Please refresh the page.")
            st.experimental_rerun()
        except Exception as e:
            st.error(f"Error processing uploaded file: {str(e)}")
    
    # Stop further execution if no data
    st.stop()

# Professional header with gradient background and logo
header_cols = st.columns([1, 5])
with header_cols[0]:
    st.image("attached_assets/Untitled design-24.png", width=120)
    
with header_cols[1]:
    st.markdown("""
    <div class="header-container">
        <h1>TEXT ANALYTICS POWERBOARD</h1>
        <div class="subtitle">Enterprise-grade contact analytics & insights platform</div>
    </div>
    """, unsafe_allow_html=True)

# Key metrics display - wrap in safety checks for robustness
metrics_col1, metrics_col2, metrics_col3, metrics_col4, metrics_col5 = st.columns(5)
with metrics_col1:
    total_contacts = len(st.session_state.data)
    st.metric("TOTAL CONTACTS", total_contacts)
with metrics_col2:
    if 'avg_engagement_score' in st.session_state.aggregate_metrics:
        st.metric("AVG ENGAGEMENT", f"{st.session_state.aggregate_metrics['avg_engagement_score']:.1f}")
    else:
        st.metric("AVG ENGAGEMENT", "N/A")
with metrics_col3:
    if 'avg_lead_score' in st.session_state.aggregate_metrics:
        st.metric("AVG LEAD SCORE", f"{st.session_state.aggregate_metrics['avg_lead_score']:.1f}")
    else:
        st.metric("AVG LEAD SCORE", "N/A")
with metrics_col4:
    if 'avg_enthusiasm_level' in st.session_state.aggregate_metrics:
        st.metric("AVG ENTHUSIASM", f"{st.session_state.aggregate_metrics['avg_enthusiasm_level']:.1f}")
    else:
        st.metric("AVG ENTHUSIASM", "N/A")
with metrics_col5:
    if 'avg_completion_rate' in st.session_state.aggregate_metrics:
        st.metric("AVG COMPLETION", f"{st.session_state.aggregate_metrics['avg_completion_rate']:.1f}%")
    else:
        st.metric("AVG COMPLETION", "N/A")

# Top navigation using expander for filters
with st.expander("🔍 SEARCH & FILTERS", expanded=False):
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    
    with filter_col1:
        search_term = st.text_input("🔎 Search across all fields:", 
                                     value=st.session_state.search_term,
                                     placeholder="Name, role, challenge, etc.")
        
        sentiment_filter = st.multiselect(
            "Filter by sentiment:",
            options=sorted(st.session_state.data['overall_sentiment'].unique()),
            default=[]
        )
    
    with filter_col2:
        role_filter = st.multiselect(
            "Filter by role:",
            options=sorted(st.session_state.data['role'].unique()),
            default=[]
        )
        
        challenge_filter = st.multiselect(
            "Filter by challenge category:",
            options=sorted(st.session_state.data['challenge_category'].unique()),
            default=[]
        )
    
    with filter_col3:
        lead_score_range = st.slider(
            "Lead score range:",
            min_value=0,
            max_value=5,
            value=(0, 5)
        )
        
        industry_filter = st.multiselect(
            "Filter by industry:",
            options=sorted(st.session_state.data['industry_vertical'].unique()),
            default=[]
        )
    
    # Update session state with filters
    st.session_state.search_term = search_term
    st.session_state.filters = {
        'role': role_filter,
        'overall_sentiment': sentiment_filter,
        'challenge_category': challenge_filter,
        'industry_vertical': industry_filter
    }
    
    # Apply filters to the data
    filtered_data = st.session_state.data.copy()
    
    # Apply range filters
    filtered_data = filtered_data[
        (filtered_data['lead_score'] >= lead_score_range[0]) &
        (filtered_data['lead_score'] <= lead_score_range[1])
    ]
    
    # Apply categorical filters
    filtered_data = filter_dataframe(filtered_data, st.session_state.filters)
    
    # Apply search term
    if search_term:
        filtered_data = search_dataframe(filtered_data, search_term)
    
    # Show filter results count
    st.markdown(f"**{len(filtered_data)} of {total_contacts} contacts** match your criteria")

# Main content area
if st.session_state.data.empty:
    st.error("⚠️ No data available. Please check the data source.")
else:
    # Create dynamic view based on session state
    if st.session_state.selected_contact is not None:
        # INDIVIDUAL CONTACT VIEW
        contact_data = st.session_state.data[st.session_state.data['contact_id'] == st.session_state.selected_contact].iloc[0]
        
        # Back button to return to dashboard
        if st.button("⬅️ Back to Dashboard"):
            st.session_state.selected_contact = None
            st.session_state.current_view = "dashboard"
            st.rerun()
        
        # Contact header
        st.markdown(f"## 👤 {contact_data['full_name']} ({contact_data['role']})")
        
        # Contact overview metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            sentiment_class = contact_data['overall_sentiment'].lower()
            st.markdown(f"**Sentiment:** <span class='sentiment-{sentiment_class}'>{contact_data['overall_sentiment']}</span>", unsafe_allow_html=True)
        with col2:
            lead_score = contact_data['lead_score']
            score_class = "high-score" if lead_score >= 4 else "medium-score" if lead_score >= 2 else "low-score"
            st.markdown(f"**Lead Score:** <span class='{score_class}'>{lead_score}/5</span>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"**Timeline:** {contact_data['estimated_timeline']}")
        with col4:
            st.markdown(f"**Industry:** {contact_data['industry_vertical']}")
        
        # Radar chart for key metrics
        radar_chart = create_radar_chart(st.session_state.data, st.session_state.selected_contact)
        st.plotly_chart(radar_chart, use_container_width=True)
        
        # Tabbed sections for contact details
        contact_tab1, contact_tab2, contact_tab3, contact_tab4 = st.tabs([
            "💬 Engagement & Sentiment", 
            "🧩 Challenge Analysis", 
            "💼 Sales Qualification", 
            "🏢 Industry & Follow-up"
        ])
        
        with contact_tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 💬 Engagement Analysis")
                st.markdown(f"""
                **Overall Score:** {contact_data['overall_score']}/100  
                **Pattern:** {contact_data['response_pattern']}  
                **Conversation Depth:** {contact_data['conversation_depth']}  
                **Contact Sharing:** {contact_data['contact_sharing_willingness']}
                
                **Interested Features:**  
                {contact_data['interested_features']}
                """)
                
                st.markdown("### 🎯 5K Giveaway Performance")
                participated = "✅ Yes" if contact_data['participated'] else "❌ No"
                completed = "✅ Yes" if contact_data['completed_full_hunt'] else "❌ No"
                
                st.markdown(f"""
                **Participated:** {participated}  
                **Completion Rate:** {contact_data['completion_rate']}%  
                **Response Speed:** {contact_data['response_speed']}  
                **Completed Full Hunt:** {completed}
                
                **Completed Activities:**  
                {contact_data['completed_activities']}
                """)
                
            with col2:
                st.markdown("### 😊 Sentiment Analysis")
                st.markdown(f"""
                **Overall Sentiment:** {contact_data['overall_sentiment']}  
                **Progression:** {contact_data['sentiment_progression']}  
                **Enthusiasm Level:** {contact_data['enthusiasm_level']}/10
                
                **Pain Points:**  
                {contact_data['pain_points']}
                
                **Satisfaction Signals:**  
                {contact_data['satisfaction_signals']}
                """)
        
        with contact_tab2:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🧩 Challenge Details")
                st.markdown(f"""
                **Raw Challenge:**  
                "{contact_data['raw_challenge']}"
                
                **Category:** {contact_data['challenge_category']}  
                **Severity:** {contact_data['severity_level']}  
                **Impact Area:** {contact_data['impact_area']}
                
                **Keywords:**  
                {contact_data['challenge_keywords']}
                """)
            
            with col2:
                st.markdown("### 💪 Objections & Concerns")
                st.markdown(f"""
                **Objections to Address:**  
                {contact_data['objections_to_address']}
                """)
        
        with contact_tab3:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 💼 Sales Qualification")
                st.markdown(f"""
                **Lead Score:** {contact_data['lead_score']}/5  
                **Timeline:** {contact_data['estimated_timeline']}  
                **Budget:** {contact_data['budget_indicator']}  
                **Decision Maker:** {contact_data['decision_maker_status']}
                """)
            
            with col2:
                st.markdown("### 🤝 Follow-up Strategy")
                st.markdown(f"""
                **Next Step:**  
                {contact_data['recommended_next_step']}
                
                **Suggested Content:**  
                {contact_data['suggested_content']}
                
                **Ideal Follow-up Time:** {contact_data['ideal_follow_up_time']}  
                **Preferred Channel:** {contact_data['preferred_channel']}
                
                **Key Talking Points:**  
                {contact_data['key_talking_points']}
                """)
        
        with contact_tab4:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🏢 Industry Insights")
                st.markdown(f"""
                **Industry:** {contact_data['industry_vertical']}  
                **Company Size:** {contact_data['company_size_indicator']}  
                **Tech Adoption:** {contact_data['tech_adoption_level']}  
                **Competitive Position:** {contact_data['competitive_position']}
                """)
            
            with col2:
                st.markdown("### 📝 Basic Information")
                st.markdown(f"""
                **Full Name:** {contact_data['full_name']}  
                **Role:** {contact_data['role']}  
                **Company:** {contact_data['company'] if contact_data['company'] else 'Not specified'}  
                **Contact ID:** {contact_data['contact_id']}
                """)
                
        # Add conversation history section with a button to show/hide
        st.markdown("---")
        st.markdown("### 💬 Conversation History")
        
        # Button to show/hide conversation
        if st.button("View Conversation History" if not st.session_state.view_conversation else "Hide Conversation History"):
            st.session_state.view_conversation = not st.session_state.view_conversation
        
        # Display conversation if view_conversation is True
        if st.session_state.view_conversation:
            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            
            # Get conversation for this contact
            if st.session_state.selected_contact in st.session_state.conversations:
                conversation = st.session_state.conversations[st.session_state.selected_contact]
                
                for message in conversation:
                    role = message["role"]
                    content = message["content"]
                    
                    # Style based on message role
                    if role == "user":
                        st.markdown(f'<div class="conversation-bubble user-message"><strong>{contact_data["full_name"]}:</strong><br>{content}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="conversation-bubble assistant-message"><strong>Support Agent:</strong><br>{content}</div>', unsafe_allow_html=True)
            else:
                st.info("No conversation history available for this contact.")
                
            st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        # MAIN DASHBOARD VIEW - No duplicate metrics needed here
        
        # Dynamic tabs for different analytics views
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "👋 CONTACTS", 
            "💰 SALES INSIGHTS", 
            "😊 SENTIMENT", 
            "🧩 CHALLENGES", 
            "🏢 INDUSTRY"
        ])
        
        with tab1:
            # CONTACTS VIEW
            st.markdown("### 👋 Contact Explorer")
            
            # Create an expanded table of all contacts with key metrics
            contact_df = filtered_data[[
                'contact_id', 'full_name', 'role', 'overall_sentiment', 
                'lead_score', 'overall_score', 'enthusiasm_level', 
                'challenge_category', 'industry_vertical'
            ]].copy()
            
            # Display the dataframe with contact information
            st.dataframe(
                contact_df.drop(columns=['contact_id']),
                use_container_width=True
            )
            
            # Create a selectbox to choose contacts
            contact_options = [(row['contact_id'], f"{row['full_name']} ({row['role']})") 
                               for _, row in contact_df.iterrows()]
            contact_dict = {id: name for id, name in contact_options}
            
            selected_contact_id = st.selectbox(
                "Select a contact to view details:",
                options=[id for id, _ in contact_options],
                format_func=lambda x: contact_dict[x]
            )
            
            if st.button("View Contact Details"):
                st.session_state.selected_contact = selected_contact_id
                st.session_state.current_view = "contact"
                st.rerun()
            
            # Show additional visualizations for contacts
            col1, col2 = st.columns(2)
            
            with col1:
                # Role distribution
                role_chart = create_role_distribution_chart(filtered_data)
                st.plotly_chart(role_chart, use_container_width=True)
            
            with col2:
                # Engagement vs enthusiasm scatter plot
                scatter_chart = create_engagement_vs_enthusiasm_scatter(filtered_data)
                st.plotly_chart(scatter_chart, use_container_width=True)
        
        with tab2:
            # SALES INSIGHTS VIEW
            st.markdown("### 💰 Sales Qualification Analytics")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Lead score histogram
                lead_score_chart = create_lead_score_histogram(filtered_data)
                st.plotly_chart(lead_score_chart, use_container_width=True)
                
                # Timeline distribution
                timeline_chart = create_timeline_distribution_chart(filtered_data)
                st.plotly_chart(timeline_chart, use_container_width=True)
            
            with col2:
                # Top prospects table
                st.markdown("#### 🌟 Top Prospects")
                top_prospects = filtered_data.sort_values('lead_score', ascending=False).head(10)
                st.dataframe(
                    top_prospects[[
                        'full_name', 'role', 'lead_score', 'estimated_timeline', 
                        'overall_sentiment', 'decision_maker_status'
                    ]],
                    use_container_width=True
                )
                
                # Correlation heatmap 
                correlation_chart = create_correlation_heatmap(filtered_data)
                st.plotly_chart(correlation_chart, use_container_width=True)
        
        with tab3:
            # SENTIMENT VIEW
            st.markdown("### 😊 Sentiment Analytics")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Sentiment distribution
                sentiment_chart = create_sentiment_distribution_chart(filtered_data)
                st.plotly_chart(sentiment_chart, use_container_width=True)
                
                # Pain points chart
                pain_points_chart = create_pain_points_chart(filtered_data)
                st.plotly_chart(pain_points_chart, use_container_width=True)
            
            with col2:
                # Enthusiasm histogram
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
                
                # Satisfaction signals
                satisfaction_chart = create_keyword_cloud_chart(st.session_state.satisfaction_signals)
                st.plotly_chart(satisfaction_chart, use_container_width=True)
        
        with tab4:
            # CHALLENGES VIEW
            st.markdown("### 🧩 Challenge Analytics")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Challenge category chart
                challenge_chart = create_challenge_category_chart(filtered_data)
                st.plotly_chart(challenge_chart, use_container_width=True)
                
                # Challenge keywords
                keywords_chart = create_keyword_cloud_chart(st.session_state.challenge_keywords)
                st.plotly_chart(keywords_chart, use_container_width=True)
            
            with col2:
                # Severity distribution
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
                
                # Impact area analysis
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
        
        with tab5:
            # INDUSTRY VIEW
            st.markdown("### 🏢 Industry Analytics")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Industry vertical chart
                industry_chart = create_industry_vertical_chart(filtered_data)
                st.plotly_chart(industry_chart, use_container_width=True)
                
                # Preferred channel chart
                channel_chart = create_preferred_channel_chart(filtered_data)
                st.plotly_chart(channel_chart, use_container_width=True)
            
            with col2:
                # Tech adoption chart
                tech_chart = create_tech_adoption_chart(filtered_data)
                st.plotly_chart(tech_chart, use_container_width=True)
                
                # Company size distribution
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
                
                st.plotly_chart(fig, use_container_width=True)
