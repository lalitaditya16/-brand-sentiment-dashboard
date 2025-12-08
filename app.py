import streamlit as st
import pandas as pd
import re
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import random
from groq import Groq
import json

# Page config
st.set_page_config(
    page_title="Brand Sentiment Dashboard",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize sentiment analyzer
vader = SentimentIntensityAnalyzer()

def clean_text(text):
    """Clean tweet text"""
    text = re.sub(r"http\S+|www\S+|https\S+", "", text, flags=re.MULTILINE)
    text = re.sub(r"\@\w+", "", text)
    text = re.sub(r"RT[\s]+", "", text)
    text = text.strip()
    return text

def analyze_sentiment(text):
    """Analyze sentiment using TextBlob and VADER"""
    cleaned = clean_text(text)
    
    if not cleaned:
        return 0, "Neutral", ""
    
    # TextBlob
    blob = TextBlob(cleaned)
    polarity = blob.sentiment.polarity
    
    # VADER (better for social media)
    vader_score = vader.polarity_scores(cleaned)["compound"]
    
    # Weighted average (VADER is better for social media)
    avg_score = (polarity * 0.3) + (vader_score * 0.7)
    
    # Label
    if avg_score > 0.05:
        label = "Positive"
        color = ""
    elif avg_score < -0.05:
        label = "Negative"
        color = ""
    else:
        label = "Neutral"
        color = ""
    
    return avg_score, label, color

def extract_hashtags(tweets):
    """Extract trending hashtags"""
    hashtags = []
    for tweet in tweets:
        found = re.findall(r"#(\w+)", tweet)
        hashtags.extend(found)
    
    if hashtags:
        common = Counter(hashtags).most_common(10)
        return [f"#{tag}" for tag, _ in common]
    return []

@st.cache_data(ttl=3600)
def generate_tweets_with_groq(query, num_tweets=100):
    """Generate realistic tweets using Groq LLM"""
    
    # Get API key from Streamlit secrets
    try:
        groq_api_key = st.secrets["GROQ_API_KEY"]
    except:
        st.error("⚠️ GROQ_API_KEY not found in secrets. Please add it in Streamlit Cloud settings.")
        return None
    
    try:
        client = Groq(api_key=groq_api_key)
        
        # Generate tweets in batches for better performance
        batch_size = 50
        all_tweets = []
        usernames = ["tech_enthusiast", "daily_user", "honest_reviewer", "product_fan", "concerned_customer",
                     "market_watcher", "industry_expert", "random_user", "verified_buyer", "social_observer",
                     "techreviewer", "gadget_lover", "customer123", "real_user", "brand_watcher"]
        
        batches = (num_tweets + batch_size - 1) // batch_size
        
        for i in range(batches):
            current_batch = min(batch_size, num_tweets - len(all_tweets))
            
            prompt = f"""Generate {current_batch} realistic Twitter/X and Reddit-style posts about "{query}".

