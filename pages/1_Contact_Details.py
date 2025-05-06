import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_processor import load_data, search_dataframe
from utils.visualizations import create_radar_chart

# Set page configuration
st.set_page_config(
    page_title="Contact Details | Analytics Dashboard",
    page_icon="👤",
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
st.image("https://images.unsplash.com/photo-1518186285589-2f7649de83e0", use_container_width=True)
st.title("Contact Details")
st.subheader("Detailed view of individual contact profiles and their analytics")

# Check if data is available
if st.session_state.data.empty:
    st.warning("No contact data available. Please check the data source.")
else:
    # Search and filter section
    st.markdown("### Search Contacts")
    search_col1, search_col2 = st.columns([3, 1])
    
    with search_col1:
        search_term = st.text_input("Search by name, role, or other attributes:", "")
    
    with search_col2:
        role_filter = st.selectbox(
            "Filter by role:",
            options=["All Roles"] + sorted(st.session_state.data['role'].unique().tolist()),
            index=0
        )
    
    # Apply search and filters
    filtered_data = st.session_state.data
    
    # Apply role filter if not "All Roles"
    if role_filter != "All Roles":
        filtered_data = filtered_data[filtered_data['role'] == role_filter]
    
    # Apply search term if provided
    if search_term:
        filtered_data = search_dataframe(filtered_data, search_term)
    
    # Display filtered contact count
    st.markdown(f"**{len(filtered_data)} contacts** match your criteria")
    
    # Contacts selector
    if not filtered_data.empty:
        # Create contact selector
        contact_options = [f"{row['full_name']} ({row['role']})" for _, row in filtered_data.iterrows()]
        contact_map = {f"{row['full_name']} ({row['role']})": row['contact_id'] for _, row in filtered_data.iterrows()}
        
        selected_contact_name = st.selectbox(
            "Select a contact to view details:",
            options=contact_options,
            index=0
        )
        
        selected_contact_id = contact_map[selected_contact_name]
        contact_data = filtered_data[filtered_data['contact_id'] == selected_contact_id].iloc[0]
        
        # Display contact details
        st.markdown("---")
        st.markdown(f"## {contact_data['full_name']}")
        
        # Contact info and metrics
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("### Basic Information")
            
            # Basic info card
            st.markdown(f"""
            **Role:** {contact_data['role']}  
            **Company:** {contact_data['company'] if contact_data['company'] else 'Not specified'}  
            **Contact ID:** {contact_data['contact_id']}
            """)
            
            # Challenge info
            st.markdown("### Challenge")
            st.markdown(f"""
            **Challenge:** {contact_data['raw_challenge']}  
            **Category:** {contact_data['challenge_category']}  
            **Severity:** {contact_data['severity_level']}  
            **Impact Area:** {contact_data['impact_area']}
            """)
            
            # Sales qualification info
            st.markdown("### Sales Qualification")
            st.markdown(f"""
            **Lead Score:** {contact_data['lead_score']}  
            **Timeline:** {contact_data['estimated_timeline']}  
            **Budget:** {contact_data['budget_indicator']}  
            **Decision Maker:** {contact_data['decision_maker_status']}
            """)
        
        with col2:
            # Radar chart with key metrics
            radar_chart = create_radar_chart(filtered_data, selected_contact_id)
            st.plotly_chart(radar_chart, use_container_width=True)
            
            # Metrics in columns
            metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
            
            with metrics_col1:
                st.metric("Engagement Score", contact_data['overall_score'])
            
            with metrics_col2:
                st.metric("Lead Score", contact_data['lead_score'])
            
            with metrics_col3:
                st.metric("Enthusiasm", contact_data['enthusiasm_level'])
            
            with metrics_col4:
                st.metric("Completion Rate", contact_data['completion_rate'])
        
        # Additional sections
        st.markdown("---")
        
        # Engagement and sentiment
        engagement_col1, engagement_col2 = st.columns(2)
        
        with engagement_col1:
            st.markdown("### Engagement Analysis")
            st.markdown(f"""
            **Overall Score:** {contact_data['overall_score']}  
            **Pattern:** {contact_data['response_pattern']}  
            **Depth:** {contact_data['conversation_depth']}  
            **Contact Sharing:** {contact_data['contact_sharing_willingness']}
            
            **Interested Features:**  
            {contact_data['interested_features']}
            """)
        
        with engagement_col2:
            st.markdown("### Sentiment Analysis")
            st.markdown(f"""
            **Overall Sentiment:** {contact_data['overall_sentiment']}  
            **Progression:** {contact_data['sentiment_progression']}  
            **Enthusiasm Level:** {contact_data['enthusiasm_level']}
            
            **Pain Points:**  
            {contact_data['pain_points']}
            
            **Satisfaction Signals:**  
            {contact_data['satisfaction_signals']}
            """)
        
        # Scavenger hunt and follow-up sections
        hunt_col1, hunt_col2 = st.columns(2)
        
        with hunt_col1:
            st.markdown("### Scavenger Hunt Metrics")
            
            # Participated status with color
            participated = "✅ Yes" if contact_data['participated'] else "❌ No"
            completed_hunt = "✅ Yes" if contact_data['completed_full_hunt'] else "❌ No"
            
            st.markdown(f"""
            **Participated:** {participated}  
            **Completion Rate:** {contact_data['completion_rate']}%  
            **Response Speed:** {contact_data['response_speed']}  
            **Completed Full Hunt:** {completed_hunt}
            
            **Completed Activities:**  
            {contact_data['completed_activities']}
            """)
        
        with hunt_col2:
            st.markdown("### Follow-up Strategy")
            st.markdown(f"""
            **Recommended Next Step:**  
            {contact_data['recommended_next_step']}
            
            **Suggested Content:**  
            {contact_data['suggested_content']}
            
            **Ideal Follow-up Time:** {contact_data['ideal_follow_up_time']}  
            **Preferred Channel:** {contact_data['preferred_channel']}
            
            **Key Talking Points:**  
            {contact_data['key_talking_points']}
            """)
        
        # Industry insights
        st.markdown("---")
        st.markdown("### Industry Insights")
        
        industry_cols = st.columns(4)
        
        with industry_cols[0]:
            st.markdown(f"**Company Size:** {contact_data['company_size_indicator']}")
        
        with industry_cols[1]:
            st.markdown(f"**Industry:** {contact_data['industry_vertical']}")
        
        with industry_cols[2]:
            st.markdown(f"**Tech Adoption:** {contact_data['tech_adoption_level']}")
        
        with industry_cols[3]:
            st.markdown(f"**Competitive Position:** {contact_data['competitive_position']}")
    
    else:
        st.warning("No contacts match your search criteria. Try adjusting your filters.")

# Footer
st.markdown("---")
st.caption("Contact Details View | Text Analytics Dashboard")
