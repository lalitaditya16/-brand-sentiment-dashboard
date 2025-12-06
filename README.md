# 📊 Brand Sentiment Dashboard

A simple Streamlit dashboard that analyzes public sentiment about brands and products from Twitter/X.

**No API keys needed!** Uses free Twitter scraping.

## 🚀 Quick Start

### 1. Install Dependencies

```powershell
cd brand-sentiment-dashboard
pip install -r requirements.txt
```

### 2. Download NLTK Data (One-time setup)

```powershell
python -c "import nltk; nltk.download('punkt'); nltk.download('brown')"
```

### 3. Run the Dashboard

```powershell
streamlit run app.py
```

The dashboard will open in your browser at `http://localhost:8501`

## 🎯 How to Use

1. Enter a brand or product name (e.g., "Tesla", "iPhone", "ChatGPT")
2. Select number of tweets to analyze (20-200)
3. Click **Analyze**
4. View the results:
   - Overall sentiment score
   - Sentiment distribution pie chart
   - Score histogram
   - Trending hashtags
   - Word cloud
   - Sample positive/negative tweets
5. Download results as CSV

## 📊 Features

- **Real-time Twitter scraping** - No API keys required
- **Sentiment analysis** - Uses both TextBlob and VADER algorithms
- **Visual analytics** - Interactive charts with Plotly
- **Word cloud** - See most common terms
- **Trending topics** - Discover related hashtags
- **Export data** - Download CSV for further analysis

## 🛠️ Tech Stack

- **Streamlit** - Web dashboard framework
- **ntscraper** - Free Twitter scraper (no API needed)
- **TextBlob & VADER** - Sentiment analysis
- **Plotly** - Interactive visualizations
- **WordCloud** - Text visualization
- **Pandas** - Data processing

## 📝 Example Searches

### Tech Brands
- Apple
- Tesla
- Microsoft
- Google

### Products
- iPhone 15
- PlayStation 5
- ChatGPT
- AirPods

### Services
- Netflix
- Spotify
- Uber
- Amazon Prime

## ⚠️ Notes

- **Rate limiting**: Free scraping may have limits. If you hit errors, wait a few minutes
- **Tweet volume**: More tweets = better analysis but slower processing
- **English only**: Currently optimized for English tweets
- **Recency**: Scraper gets recent tweets (last few days)

## 🐛 Troubleshooting

### "No tweets found"
- Try a more general search term
- Check spelling
- Some terms may be rate-limited

### Slow performance
- Reduce number of tweets in sidebar
- Close other browser tabs

### Installation errors
```powershell
# If you get SSL errors with ntscraper
pip install --upgrade certifi

# If matplotlib fails
pip install --upgrade pillow
```

## 🔧 Customization

Edit `app.py` to customize:
- Color schemes (line 150-200)
- Number of sample tweets shown
- Sentiment thresholds
- Chart types and layouts

## 📄 License

MIT License - Feel free to use and modify!

## 🤝 Contributing

Found a bug or want a feature? Open an issue or submit a PR!
