import pandas as pd
import json
import nltk
from nltk.corpus import stopwords
from collections import Counter

# Download NLTK resources
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

def load_data(file_path='attached_assets/data.json'):
    """
    Load and process the JSON data from the provided file path.
    
    Args:
        file_path (str): Path to the JSON data file
        
    Returns:
        pd.DataFrame: Processed data in a DataFrame format
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Initialize list to hold processed data
        processed_data = []
        
        # Extract and flatten the nested JSON structure
        for item in data:
            if 'message' in item and 'content' in item['message'] and 'contact_analytics' in item['message']['content']:
                contact_data = item['message']['content']['contact_analytics']
                
                # Flatten the nested structure
                flat_data = {
                    'contact_id': contact_data.get('contact_id', ''),
                }
                
                # Add basic info
                if 'basic_info' in contact_data:
                    basic_info = contact_data['basic_info']
                    flat_data.update({
                        'full_name': basic_info.get('full_name', ''),
                        'company': basic_info.get('company', ''),
                        'role': basic_info.get('role', '')
                    })
                
                # Add challenge analysis
                if 'challenge_analysis' in contact_data:
                    challenge = contact_data['challenge_analysis']
                    flat_data.update({
                        'raw_challenge': challenge.get('raw_challenge', ''),
                        'challenge_category': challenge.get('category', ''),
                        'challenge_keywords': ', '.join(challenge.get('keywords', [])),
                        'severity_level': challenge.get('severity_level', ''),
                        'impact_area': challenge.get('impact_area', '')
                    })
                
                # Add scavenger hunt metrics
                if 'scavenger_hunt_metrics' in contact_data:
                    hunt = contact_data['scavenger_hunt_metrics']
                    flat_data.update({
                        'participated': hunt.get('participated', False),
                        'completion_rate': hunt.get('completion_rate', 0),
                        'completed_activities': ', '.join(hunt.get('completed_activities', [])),
                        'response_speed': hunt.get('response_speed', ''),
                        'completed_full_hunt': hunt.get('completed_full_hunt', False)
                    })
                
                # Add engagement analysis
                if 'engagement_analysis' in contact_data:
                    engagement = contact_data['engagement_analysis']
                    flat_data.update({
                        'overall_score': engagement.get('overall_score', 0),
                        'response_pattern': engagement.get('response_pattern', ''),
                        'interested_features': ', '.join(engagement.get('interested_features', [])),
                        'conversation_depth': engagement.get('conversation_depth', ''),
                        'contact_sharing_willingness': engagement.get('contact_sharing_willingness', '')
                    })
                
                # Add sentiment metrics
                if 'sentiment_metrics' in contact_data:
                    sentiment = contact_data['sentiment_metrics']
                    flat_data.update({
                        'overall_sentiment': sentiment.get('overall_sentiment', ''),
                        'sentiment_progression': sentiment.get('sentiment_progression', ''),
                        'enthusiasm_level': sentiment.get('enthusiasm_level', 0),
                        'pain_points': ', '.join(sentiment.get('pain_points', [])),
                        'satisfaction_signals': ', '.join(sentiment.get('satisfaction_signals', []))
                    })
                
                # Add industry insights
                if 'industry_insights' in contact_data:
                    industry = contact_data['industry_insights']
                    flat_data.update({
                        'company_size_indicator': industry.get('company_size_indicator', ''),
                        'industry_vertical': industry.get('industry_vertical', ''),
                        'tech_adoption_level': industry.get('tech_adoption_level', ''),
                        'competitive_position': industry.get('competitive_position', '')
                    })
                
                # Add follow-up strategy
                if 'follow_up_strategy' in contact_data:
                    follow_up = contact_data['follow_up_strategy']
                    flat_data.update({
                        'recommended_next_step': follow_up.get('recommended_next_step', ''),
                        'suggested_content': follow_up.get('suggested_content', ''),
                        'ideal_follow_up_time': follow_up.get('ideal_follow_up_time', ''),
                        'preferred_channel': follow_up.get('preferred_channel', ''),
                        'key_talking_points': ', '.join(follow_up.get('key_talking_points', []))
                    })
                
                # Add sales qualification
                if 'sales_qualification' in contact_data:
                    sales = contact_data['sales_qualification']
                    flat_data.update({
                        'lead_score': sales.get('lead_score', 0),
                        'estimated_timeline': sales.get('estimated_timeline', ''),
                        'objections_to_address': ', '.join(sales.get('objections_to_address', [])),
                        'budget_indicator': sales.get('budget_indicator', ''),
                        'decision_maker_status': sales.get('decision_maker_status', '')
                    })
                
                processed_data.append(flat_data)
        
        # Create DataFrame
        df = pd.DataFrame(processed_data)
        
        # Convert numeric columns to appropriate types
        numeric_cols = ['completion_rate', 'overall_score', 'enthusiasm_level', 'lead_score']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Convert boolean columns
        bool_cols = ['participated', 'completed_full_hunt']
        for col in bool_cols:
            if col in df.columns:
                df[col] = df[col].astype(bool)
        
        return df
    
    except Exception as e:
        raise Exception(f"Error loading or processing data: {str(e)}")

def get_aggregate_metrics(df):
    """
    Calculate aggregated metrics from the dataset.
    
    Args:
        df (pd.DataFrame): The processed data
        
    Returns:
        dict: Dictionary containing aggregated metrics
    """
    if df.empty:
        return {}
    
    metrics = {
        'total_contacts': len(df),
        'avg_engagement_score': df['overall_score'].mean(),
        'avg_lead_score': df['lead_score'].mean(),
        'avg_enthusiasm_level': df['enthusiasm_level'].mean(),
        'avg_completion_rate': df['completion_rate'].mean(),
        'sentiment_distribution': df['overall_sentiment'].value_counts().to_dict(),
        'challenge_categories': df['challenge_category'].value_counts().to_dict(),
        'role_distribution': df['role'].value_counts().to_dict(),
        'preferred_channels': df['preferred_channel'].value_counts().to_dict(),
        'industry_verticals': df['industry_vertical'].value_counts().to_dict()
    }
    
    return metrics

def extract_keywords(df, column):
    """
    Extract and count keywords from a comma-separated column
    
    Args:
        df (pd.DataFrame): The processed data
        column (str): The column name containing comma-separated keywords
        
    Returns:
        dict: Dictionary with keywords and their frequencies
    """
    all_keywords = []
    
    for keywords_str in df[column].dropna():
        keywords = [k.strip() for k in keywords_str.split(',')]
        all_keywords.extend(keywords)
    
    # Remove empty strings
    all_keywords = [k for k in all_keywords if k]
    
    # Count frequencies
    keyword_counts = Counter(all_keywords)
    
    return dict(keyword_counts.most_common(20))

def get_timeline_mapping():
    """
    Create a mapping of timeline strings to numeric values for sorting
    
    Returns:
        dict: Mapping of timeline strings to numeric values
    """
    return {
        '30 days': 30,
        '60 days': 60, 
        '90 days': 90,
        '90+ days': 100,
        '120 days': 120,
        '180 days': 180,
        'Unknown': 999
    }

def filter_dataframe(df, filters):
    """
    Filter the DataFrame based on provided filter criteria
    
    Args:
        df (pd.DataFrame): The processed data
        filters (dict): Dictionary of filter criteria
        
    Returns:
        pd.DataFrame: Filtered DataFrame
    """
    filtered_df = df.copy()
    
    for column, value in filters.items():
        if value and column in filtered_df.columns:
            if isinstance(value, list):
                if value:  # Only filter if list is not empty
                    filtered_df = filtered_df[filtered_df[column].isin(value)]
            else:
                filtered_df = filtered_df[filtered_df[column] == value]
    
    return filtered_df

def search_dataframe(df, search_term):
    """
    Search the DataFrame for a specific term across all text columns
    
    Args:
        df (pd.DataFrame): The processed data
        search_term (str): Term to search for
        
    Returns:
        pd.DataFrame: DataFrame with rows matching the search term
    """
    if not search_term:
        return df
    
    # Convert search term to lowercase for case-insensitive search
    search_term = search_term.lower()
    
    # Create a mask to filter the DataFrame
    mask = pd.Series(False, index=df.index)
    
    # Apply search to all string columns
    for column in df.columns:
        if df[column].dtype == 'object':  # Object type typically means strings
            column_mask = df[column].fillna('').astype(str).str.lower().str.contains(search_term, na=False)
            mask = mask | column_mask
    
    return df[mask]
