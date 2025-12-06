from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime
import re
import snscrape.modules.twitter as sntwitter
from collections import Counter

load_dotenv()

app = FastAPI(title="Brand Sentiment Dashboard API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize sentiment analyzers
vader_analyzer = SentimentIntensityAnalyzer()

# Models
class SentimentRequest(BaseModel):
    query: str
    max_results: Optional[int] = 100
    days_back: Optional[int] = 7

class TweetData(BaseModel):
    text: str
    created_at: str
    sentiment_score: float
    sentiment_label: str
    username: str
    likes: int
    retweets: int

class SentimentResponse(BaseModel):
    query: str
    total_tweets: int
    overall_sentiment: str
    sentiment_score: float
    positive_count: int
    neutral_count: int
    negative_count: int
    positive_percentage: float
    neutral_percentage: float
    negative_percentage: float
    tweets: List[TweetData]
    trending_hashtags: List[dict]
    sentiment_over_time: List[dict]

def clean_tweet(text: str) -> str:
    """Clean tweet text"""
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'RT[\s]+', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def analyze_sentiment(text: str) -> tuple:
    """Analyze sentiment using both TextBlob and VADER"""
    cleaned_text = clean_tweet(text)
    
    # Skip empty tweets
    if not cleaned_text:
        return 0.0, "Neutral"
    
    # TextBlob sentiment
    try:
        blob = TextBlob(cleaned_text)
        polarity = blob.sentiment.polarity
    except:
        polarity = 0.0
    
    # VADER sentiment (better for social media)
    vader_scores = vader_analyzer.polarity_scores(cleaned_text)
    vader_compound = vader_scores['compound']
    
    # Weight VADER more heavily (70%) as it's better for social media
    avg_score = (polarity * 0.3) + (vader_compound * 0.7)
    
    # Determine label
    if avg_score > 0.05:
        label = "Positive"
    elif avg_score < -0.05:
        label = "Negative"
    else:
        label = "Neutral"
    
    return avg_score, label

def extract_hashtags(tweets: List[str]) -> List[dict]:
    """Extract most common hashtags"""
    hashtags = []
    for tweet in tweets:
        found = re.findall(r'#(\w+)', tweet)
        hashtags.extend([tag.lower() for tag in found])
    
    # Get top 10 hashtags
    common = Counter(hashtags).most_common(10)
    return [{"tag": f"#{tag}", "count": count} for tag, count in common if count > 1]

@app.get("/")
async def root():
    return {
        "message": "Brand Sentiment Dashboard API - FREE (No API Keys Required!)",
        "version": "1.0.0",
        "description": "Analyzes Twitter sentiment using free scraping - no authentication needed",
        "endpoints": {
            "/analyze": "POST - Analyze sentiment for a brand/product",
            "/health": "GET - Check API health"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "scraper": "snscrape (free, no API keys)",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/analyze", response_model=SentimentResponse)
async def analyze_brand(request: SentimentRequest):
    """Analyze sentiment for a brand/product using free Twitter scraping"""
    
    try:
        query = request.query.strip()
        max_results = min(request.max_results, 500)
        
        print(f"Scraping tweets for: {query}")
        
        # Use snscrape to get tweets (NO API KEY NEEDED!)
        tweets_data = []
        tweet_texts = []
        
        # Build search query
        search_query = f"{query} lang:en -filter:replies"
        
        # Scrape tweets
        for i, tweet in enumerate(sntwitter.TwitterSearchScraper(search_query).get_items()):
            if i >= max_results:
                break
            
            # Skip retweets
            if tweet.content.startswith('RT @'):
                continue
            
            tweets_data.append({
                'text': tweet.content,
                'date': tweet.date,
                'username': tweet.user.username,
                'likes': tweet.likeCount or 0,
                'retweets': tweet.retweetCount or 0,
            })
            tweet_texts.append(tweet.content)
        
        if not tweets_data:
            raise HTTPException(
                status_code=404,
                detail=f"No tweets found for '{query}'. Try a different search term."
            )
        
        print(f"Found {len(tweets_data)} tweets")
        
        # Analyze sentiment for each tweet
        analyzed_tweets = []
        positive_count = 0
        neutral_count = 0
        negative_count = 0
        total_score = 0
        
        # Track sentiment over time
        sentiment_by_date = {}
        
        for tweet_info in tweets_data:
            text = tweet_info['text']
            score, label = analyze_sentiment(text)
            total_score += score
            
            if label == "Positive":
                positive_count += 1
            elif label == "Negative":
                negative_count += 1
            else:
                neutral_count += 1
            
            # Group by date
            date_key = tweet_info['date'].strftime('%Y-%m-%d')
            if date_key not in sentiment_by_date:
                sentiment_by_date[date_key] = {'positive': 0, 'neutral': 0, 'negative': 0, 'total': 0}
            
            sentiment_by_date[date_key][label.lower()] += 1
            sentiment_by_date[date_key]['total'] += 1
            
            analyzed_tweets.append(TweetData(
                text=text[:280],  # Limit display length
                created_at=tweet_info['date'].isoformat(),
                sentiment_score=round(score, 3),
                sentiment_label=label,
                username=tweet_info['username'],
                likes=tweet_info['likes'],
                retweets=tweet_info['retweets']
            ))
        
        # Calculate overall metrics
        total_tweets = len(analyzed_tweets)
        avg_score = total_score / total_tweets if total_tweets > 0 else 0
        
        if avg_score > 0.05:
            overall_sentiment = "Positive"
        elif avg_score < -0.05:
            overall_sentiment = "Negative"
        else:
            overall_sentiment = "Mixed/Neutral"
        
        # Get trending hashtags
        trending = extract_hashtags(tweet_texts)
        
        # Format sentiment over time
        sentiment_timeline = [
            {
                'date': date,
                'positive': data['positive'],
                'neutral': data['neutral'],
                'negative': data['negative']
            }
            for date, data in sorted(sentiment_by_date.items())
        ]
        
        positive_pct = (positive_count / total_tweets) * 100
        neutral_pct = (neutral_count / total_tweets) * 100
        negative_pct = (negative_count / total_tweets) * 100
        
        return SentimentResponse(
            query=query,
            total_tweets=total_tweets,
            overall_sentiment=overall_sentiment,
            sentiment_score=round(avg_score, 3),
            positive_count=positive_count,
            neutral_count=neutral_count,
            negative_count=negative_count,
            positive_percentage=round(positive_pct, 1),
            neutral_percentage=round(neutral_pct, 1),
            negative_percentage=round(negative_pct, 1),
            tweets=analyzed_tweets[:50],  # Return top 50 for display
            trending_hashtags=trending,
            sentiment_over_time=sentiment_timeline
        )
        
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing sentiment: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"🚀 Starting FREE Brand Sentiment Dashboard API on port {port}")
    print(f"📊 No API keys required - using free scraping!")
    uvicorn.run(app, host="0.0.0.0", port=port)
