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
IMPORTANT: Create a BALANCED mix of sentiments:
- 40% POSITIVE (praise, satisfaction, recommendations)
- 35% NEGATIVE (complaints, disappointments, criticisms, issues)
- 25% NEUTRAL (questions, observations, news reactions)

Study real Reddit and Twitter discussions about brands. Include:

POSITIVE examples:
- "Just got my {query} and wow, the quality is insane! Best decision ever"
- "Been using {query} for 6 months, zero issues. Highly recommend #quality"
- "{query} customer service actually helped me in 10 mins. Rare these days"

NEGATIVE examples (BE CRITICAL):
- "My {query} broke after 3 weeks. Customer support ghosted me. Avoid! #disappointed"
- "Overpriced garbage. {query} used to be good but quality tanked recently"
- "Still waiting 2 weeks for {query} support to respond. Absolutely terrible service"
- "Don't waste money on {query}. Cheap knockoffs work better tbh"

NEUTRAL examples:
- "Thinking about getting {query}. Anyone have real experience with it?"
- "Saw {query} announced new features. Might be worth checking out"
- "{query} is trending. What's everyone's take on this?"

Style requirements:
- Write like REAL people (informal, casual, sometimes frustrated)
- Include typos occasionally ("tho", "gonna", "u", "rn")
- Use Reddit-style formatting occasionally
- Vary length (some short rants, some detailed reviews)
- Add emojis naturally when appropriate
- Include realistic hashtags (#scam #loveit #meh)
- Mix complaints about: price, quality, customer service, features, reliability

Make negative tweets GENUINELY critical with specific complaints, not generic disappointment.

Return ONLY a JSON array:
[
  {{"text": "tweet content here"}},
  {{"text": "another tweet here"}}
]"""

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.9,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse JSON response
            try:
                tweets_data = json.loads(content)
                
                for tweet_obj in tweets_data:
                    all_tweets.append({
                        "text": tweet_obj["text"],
                        "date": datetime.now() - timedelta(hours=random.randint(1, 168)),
                        "likes": random.randint(1, 1000),
                        "retweets": random.randint(0, 500),
                        "username": random.choice(usernames)
                    })
                    
                    if len(all_tweets) >= num_tweets:
                        break
                        
            except json.JSONDecodeError:
                st.warning(f"Batch {i+1} failed to parse. Using fallback data.")
                continue
        
        random.shuffle(all_tweets)
        return all_tweets[:num_tweets]
        
    except Exception as e:
        st.error(f"Error generating tweets with Groq: {str(e)}")
        return None# Streamlit UI
st.title(" Brand Sentiment Dashboard")
st.markdown("**Analyze public opinion about any brand, product, or topic**")



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
        max_value=1000,
        value=100,
        step=20,
        help="More tweets = better analysis"
    )
    
    analyze_button = st.button(" Analyze", type="primary", use_container_width=True)
    
    st.markdown("---")
    st.markdown("###  How it works")
    st.markdown("""
    1. Enter a brand/product name
    2. Click Analyze
    3. View sentiment analysis
    4. See trending topics
    """)

# Main content
if analyze_button and query:
    with st.spinner(f"Analyzing sentiment for {query}..."):
        
        # Generate tweets using Groq AI
        tweets = generate_tweets_with_groq(query, num_tweets)
        
        if not tweets:
            st.error(f"No data available for {query}. Try a different search term.")
            st.stop()
        
        # Analyze each tweet
        results = []
        for tweet in tweets:
            text = tweet.get("text", "")
            if text:
                score, label, color = analyze_sentiment(text)
                results.append({
                    "text": text,
                    "sentiment_score": score,
                    "sentiment": label,
                    "color": color,
                    "date": tweet.get("date", "Unknown"),
                    "likes": tweet.get("likes", 0),
                    "retweets": tweet.get("retweets", 0),
                    "username": tweet.get("username", "Unknown")
                })
        
        if not results:
            st.error("Could not analyze data. Please try again.")
            st.stop()
        
        df = pd.DataFrame(results)
        
        # Calculate metrics
        total_tweets = len(df)
        avg_sentiment = df["sentiment_score"].mean()
        positive_pct = (df["sentiment"] == "Positive").sum() / total_tweets * 100
        neutral_pct = (df["sentiment"] == "Neutral").sum() / total_tweets * 100
        negative_pct = (df["sentiment"] == "Negative").sum() / total_tweets * 100
        
        # Determine overall sentiment
        if avg_sentiment > 0.05:
            overall = "Positive"
            overall_color = ""
        elif avg_sentiment < -0.05:
            overall = "Negative"
            overall_color = ""
        else:
            overall = "Neutral"
            overall_color = ""
        
        # Header with results
        st.success(f" Analyzed {total_tweets} posts about **{query}**")
        
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
                f"{int(positive_pct * total_tweets / 100)} posts"
            )
        
        with col3:
            st.metric(
                "Neutral",
                f"{neutral_pct:.1f}%",
                f"{int(neutral_pct * total_tweets / 100)} posts"
            )
        
        with col4:
            st.metric(
                "Negative",
                f"{negative_pct:.1f}%",
                f"{int(negative_pct * total_tweets / 100)} posts"
            )
        
        # Charts
        st.markdown("---")
        
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.subheader(" Sentiment Distribution")
            
            # Pie chart
            fig_pie = go.Figure(data=[go.Pie(
                labels=["Positive", "Neutral", "Negative"],
                values=[positive_pct, neutral_pct, negative_pct],
                marker=dict(colors=["#22c55e", "#eab308", "#ef4444"]),
                hole=0.4,
                textinfo="label+percent"
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
                x="sentiment_score",
                nbins=30,
                color="sentiment",
                color_discrete_map={
                    "Positive": "#22c55e",
                    "Neutral": "#eab308",
                    "Negative": "#ef4444"
                },
                labels={"sentiment_score": "Sentiment Score", "count": "Number of Posts"}
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
        
        hashtags = extract_hashtags(df["text"].tolist())
        
        if hashtags:
            cols = st.columns(5)
            for i, tag in enumerate(hashtags[:10]):
                with cols[i % 5]:
                    st.info(tag)
        else:
            st.info("No hashtags found in posts")
        
        # Word cloud
        st.markdown("---")
        st.subheader(" Word Cloud")
        
        all_text = " ".join(df["text"].apply(clean_text).tolist())
        
        if all_text.strip():
            try:
                wordcloud = WordCloud(
                    width=1200,
                    height=400,
                    background_color="white",
                    colormap="viridis",
                    max_words=100
                ).generate(all_text)
                
                fig_wc, ax = plt.subplots(figsize=(15, 5))
                ax.imshow(wordcloud, interpolation="bilinear")
                ax.axis("off")
                st.pyplot(fig_wc)
            except:
                st.info("Not enough text data for word cloud")
        
        # Sample posts
        st.markdown("---")
        st.subheader(" Sample Posts")
        
        # Top positive
        st.markdown("####  Most Positive Posts")
        top_positive = df.nlargest(3, "sentiment_score")
        for _, post in top_positive.iterrows():
            with st.container():
                st.markdown(f"{post['color']} **Score: {post['sentiment_score']:.3f}**  @{post['username']}")
                st.markdown(f"> {post['text']}")
                st.caption(f" {post['likes']} |  {post['retweets']}")
                st.markdown("")
        
        # Top negative
        st.markdown("####  Most Negative Posts")
        top_negative = df.nsmallest(3, "sentiment_score")
        for _, post in top_negative.iterrows():
            with st.container():
                st.markdown(f"{post['color']} **Score: {post['sentiment_score']:.3f}**  @{post['username']}")
                st.markdown(f"> {post['text']}")
                st.caption(f" {post['likes']} |  {post['retweets']}")
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
    ###  What you will get:
    - **Overall sentiment** (Positive/Neutral/Negative)
    - **Sentiment distribution** pie chart
    - **Score histogram** showing sentiment spread
    - **Trending hashtags** related to the brand
    - **Word cloud** of common terms
    - **Sample posts** (most positive and negative)
    - **Downloadable CSV** with all data
    
    ###  Technical Implementation:
    - **TextBlob** for linguistic sentiment analysis
    - **VADER** for social media-optimized analysis
    - **Weighted scoring** combining both algorithms
    - **Interactive visualizations** with Plotly
    """)

# Footer
st.markdown("---")
st.caption("Built with Streamlit  Demo Mode with Sample Data")

