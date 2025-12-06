import streamlit as st
import pandas as pd
import snscrape.modules.twitter as sntwitter
import re
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt

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
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\@\w+', '', text)
    text = re.sub(r'RT[\s]+', '', text)
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
    vader_score = vader.polarity_scores(cleaned)['compound']
    
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
        found = re.findall(r'#(\w+)', tweet)
        hashtags.extend(found)
    
    if hashtags:
        common = Counter(hashtags).most_common(10)
        return [f"#{tag}" for tag, _ in common]
    return []

def scrape_tweets(query, num_tweets=100):
    """Scrape tweets using snscrape"""
    tweets = []
    
    try:
        # Use snscrape to get tweets
        for i, tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
            if i >= num_tweets:
                break
            
            tweets.append({
                'text': tweet.rawContent,
                'date': tweet.date,
                'likes': tweet.likeCount or 0,
                'retweets': tweet.retweetCount or 0,
                'username': tweet.user.username
            })
        
        return tweets if tweets else None
        
    except Exception as e:
        st.error(f"Error scraping tweets: {str(e)}")
        return None

# Streamlit UI
st.title(" Brand Sentiment Dashboard")
st.markdown("**Analyze public opinion about any brand, product, or topic from Twitter/X**")

# Sidebar
with st.sidebar:
    st.header(" Settings")
    
    query = st.text_input(
        "Enter Brand/Product Name",
        placeholder="e.g., Tesla, iPhone, ChatGPT",
        help="Enter the brand or product you want to analyze"
    )
    
    num_tweets = st.slider(
        "Number of Tweets",
        min_value=20,
        max_value=200,
        value=100,
        step=20,
        help="More tweets = better analysis but slower"
    )
    
    analyze_button = st.button(" Analyze", type="primary", use_container_width=True)
    
    st.markdown("---")
    st.markdown("###  How it works")
    st.markdown("""
    1. Enter a brand/product name
    2. Click Analyze
    3. View sentiment analysis
    4. See trending topics
    
    **No API keys needed!**
    """)

# Main content
if analyze_button and query:
    with st.spinner(f"Analyzing sentiment for '{query}'..."):
        
        # Scrape tweets
        tweets = scrape_tweets(query, num_tweets)
        
        if not tweets:
            st.error(f"No tweets found for '{query}'. Try a different search term.")
            st.stop()
        
        # Analyze each tweet
        results = []
        for tweet in tweets:
            text = tweet.get('text', '')
            if text:
                score, label, color = analyze_sentiment(text)
                results.append({
                    'text': text,
                    'sentiment_score': score,
                    'sentiment': label,
                    'color': color,
                    'date': tweet.get('date', 'Unknown'),
                    'likes': tweet.get('likes', 0),
                    'retweets': tweet.get('retweets', 0),
                    'username': tweet.get('username', 'Unknown')
                })
        
        if not results:
            st.error("Could not analyze tweets. Please try again.")
            st.stop()
        
        df = pd.DataFrame(results)
        
        # Calculate metrics
        total_tweets = len(df)
        avg_sentiment = df['sentiment_score'].mean()
        positive_pct = (df['sentiment'] == 'Positive').sum() / total_tweets * 100
        neutral_pct = (df['sentiment'] == 'Neutral').sum() / total_tweets * 100
        negative_pct = (df['sentiment'] == 'Negative').sum() / total_tweets * 100
        
        # Determine overall sentiment
        if avg_sentiment > 0.05:
            overall = "Positive"
            overall_color = ""
            sentiment_emoji = ""
        elif avg_sentiment < -0.05:
            overall = "Negative"
            overall_color = ""
            sentiment_emoji = ""
        else:
            overall = "Neutral"
            overall_color = ""
            sentiment_emoji = ""
        
        # Header with results
        st.success(f" Analyzed {total_tweets} tweets about **{query}**")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Overall Sentiment",
                f"{overall_color} {overall}",
                f"{avg_sentiment:.3f}"
            )
        
        with col2:
            st.metric(
                "Positive",
                f"{positive_pct:.1f}%",
                f"{int(positive_pct * total_tweets / 100)} tweets"
            )
        
        with col3:
            st.metric(
                "Neutral",
                f"{neutral_pct:.1f}%",
                f"{int(neutral_pct * total_tweets / 100)} tweets"
            )
        
        with col4:
            st.metric(
                "Negative",
                f"{negative_pct:.1f}%",
                f"{int(negative_pct * total_tweets / 100)} tweets"
            )
        
        # Charts
        st.markdown("---")
        
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.subheader(" Sentiment Distribution")
            
            # Pie chart
            fig_pie = go.Figure(data=[go.Pie(
                labels=['Positive', 'Neutral', 'Negative'],
                values=[positive_pct, neutral_pct, negative_pct],
                marker=dict(colors=['#22c55e', '#eab308', '#ef4444']),
                hole=0.4,
                textinfo='label+percent'
            )])
            
            fig_pie.update_layout(
                height=400,
                showlegend=True,
                margin=dict(t=0, b=0, l=0, r=0)
            )
            
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col_right:
            st.subheader(" Sentiment Score Distribution")
            
            # Histogram
            fig_hist = px.histogram(
                df,
                x='sentiment_score',
                nbins=30,
                color='sentiment',
                color_discrete_map={
                    'Positive': '#22c55e',
                    'Neutral': '#eab308',
                    'Negative': '#ef4444'
                },
                labels={'sentiment_score': 'Sentiment Score', 'count': 'Number of Tweets'}
            )
            
            fig_hist.update_layout(
                height=400,
                showlegend=True,
                xaxis_title="Sentiment Score",
                yaxis_title="Count"
            )
            
            st.plotly_chart(fig_hist, use_container_width=True)
        
        # Trending hashtags
        st.markdown("---")
        st.subheader(" Trending Topics & Hashtags")
        
        hashtags = extract_hashtags(df['text'].tolist())
        
        if hashtags:
            cols = st.columns(5)
            for i, tag in enumerate(hashtags[:10]):
                with cols[i % 5]:
                    st.info(tag)
        else:
            st.info("No hashtags found in tweets")
        
        # Word cloud
        st.markdown("---")
        st.subheader(" Word Cloud")
        
        all_text = ' '.join(df['text'].apply(clean_text).tolist())
        
        if all_text.strip():
            try:
                wordcloud = WordCloud(
                    width=1200,
                    height=400,
                    background_color='white',
                    colormap='viridis',
                    max_words=100
                ).generate(all_text)
                
                fig_wc, ax = plt.subplots(figsize=(15, 5))
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis('off')
                st.pyplot(fig_wc)
            except:
                st.info("Not enough text data for word cloud")
        
        # Sample tweets
        st.markdown("---")
        st.subheader(" Sample Tweets")
        
        # Top positive
        st.markdown("####  Most Positive Tweets")
        top_positive = df.nlargest(3, 'sentiment_score')
        for _, tweet in top_positive.iterrows():
            with st.container():
                st.markdown(f"{tweet['color']} **Score: {tweet['sentiment_score']:.3f}**  @{tweet['username']}")
                st.markdown(f"> {tweet['text'][:200]}...")
                st.caption(f" {tweet['likes']} |  {tweet['retweets']}")
                st.markdown("")
        
        # Top negative
        st.markdown("####  Most Negative Tweets")
        top_negative = df.nsmallest(3, 'sentiment_score')
        for _, tweet in top_negative.iterrows():
            with st.container():
                st.markdown(f"{tweet['color']} **Score: {tweet['sentiment_score']:.3f}**  @{tweet['username']}")
                st.markdown(f"> {tweet['text'][:200]}...")
                st.caption(f" {tweet['likes']} |  {tweet['retweets']}")
                st.markdown("")
        
        # Download data
        st.markdown("---")
        st.subheader(" Download Data")
        
        csv = df.to_csv(index=False)
        st.download_button(
            label=" Download CSV",
            data=csv,
            file_name=f"{query}_sentiment_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

else:
    # Welcome screen
    st.info(" Enter a brand or product name in the sidebar to get started!")
    
    st.markdown("###  Example searches:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **Tech Brands:**
        - Apple
        - Tesla
        - Google
        - Microsoft
        """)
    
    with col2:
        st.markdown("""
        **Products:**
        - iPhone
        - ChatGPT
        - PlayStation
        - Netflix
        """)
    
    with col3:
        st.markdown("""
        **Services:**
        - Uber
        - Amazon
        - Spotify
        - Twitter
        """)
    
    st.markdown("---")
    st.markdown("""
    ###  What you'll get:
    - **Overall sentiment** (Positive/Neutral/Negative)
    - **Sentiment distribution** pie chart
    - **Score histogram** showing sentiment spread
    - **Trending hashtags** related to the brand
    - **Word cloud** of common terms
    - **Sample tweets** (most positive and negative)
    - **Downloadable CSV** with all data
    """)

# Footer
st.markdown("---")
st.caption("Built with Streamlit  Free Twitter scraping  No API keys needed")
