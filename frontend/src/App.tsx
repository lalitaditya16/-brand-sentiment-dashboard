import { useState } from 'react';
import axios from 'axios';
import { Search, TrendingUp, TrendingDown, Minus, BarChart3, Hash, MessageCircle } from 'lucide-react';
import SentimentChart from './components/SentimentChart';
import TweetList from './components/TweetList';
import TrendingHashtags from './components/TrendingHashtags';
import TimelineChart from './components/TimelineChart';

const API_URL = 'http://localhost:8000';

interface SentimentData {
  query: string;
  total_tweets: number;
  overall_sentiment: string;
  sentiment_score: number;
  positive_count: number;
  neutral_count: number;
  negative_count: number;
  positive_percentage: number;
  neutral_percentage: number;
  negative_percentage: number;
  tweets: Array<{
    text: string;
    created_at: string;
    sentiment_score: number;
    sentiment_label: string;
    username: string;
    likes: number;
    retweets: number;
  }>;
  trending_hashtags: Array<{
    tag: string;
    count: number;
  }>;
  sentiment_over_time: Array<{
    date: string;
    positive: number;
    neutral: number;
    negative: number;
  }>;
}

function App() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<SentimentData | null>(null);
  const [error, setError] = useState('');

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError('');
    setData(null);

    try {
      const response = await axios.post(`${API_URL}/analyze`, {
        query: query.trim(),
        max_results: 100
      });
      setData(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to analyze sentiment');
    } finally {
      setLoading(false);
    }
  };

  const getSentimentIcon = (sentiment: string) => {
    if (sentiment === 'Positive') return <TrendingUp className="text-green-500" />;
    if (sentiment === 'Negative') return <TrendingDown className="text-red-500" />;
    return <Minus className="text-gray-500" />;
  };

  const getSentimentColor = (sentiment: string) => {
    if (sentiment === 'Positive') return 'text-green-600 bg-green-50';
    if (sentiment === 'Negative') return 'text-red-600 bg-red-50';
    return 'text-gray-600 bg-gray-50';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <BarChart3 className="w-8 h-8 text-blue-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Brand Sentiment Dashboard</h1>
                <p className="text-sm text-gray-500">Real-time Twitter sentiment analysis</p>
              </div>
            </div>
            <div className="text-xs text-gray-400 bg-green-50 px-3 py-1 rounded-full border border-green-200">
              ✨ FREE - No API Keys Required
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search Form */}
        <div className="mb-8">
          <form onSubmit={handleSearch} className="flex gap-3">
            <div className="flex-1 relative">
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Enter brand or product name (e.g., Tesla, iPhone, Nike...)"
                className="w-full pl-12 pr-4 py-4 text-lg border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition"
              />
            </div>
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="px-8 py-4 bg-blue-600 text-white font-semibold rounded-xl hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition"
            >
              {loading ? 'Analyzing...' : 'Analyze'}
            </button>
          </form>
          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
              {error}
            </div>
          )}
        </div>

        {/* Loading State */}
        {loading && (
          <div className="text-center py-20">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-blue-500 border-t-transparent"></div>
            <p className="mt-4 text-gray-600">Analyzing sentiment from Twitter...</p>
          </div>
        )}

        {/* Results */}
        {data && !loading && (
          <div className="space-y-6">
            {/* Overview Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-sm font-medium text-gray-500">Overall Sentiment</h3>
                  {getSentimentIcon(data.overall_sentiment)}
                </div>
                <p className={`text-2xl font-bold ${getSentimentColor(data.overall_sentiment)}`}>
                  {data.overall_sentiment}
                </p>
                <p className="text-xs text-gray-400 mt-1">Score: {data.sentiment_score.toFixed(2)}</p>
              </div>

              <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-sm font-medium text-gray-500">Total Tweets</h3>
                  <MessageCircle className="w-5 h-5 text-blue-500" />
                </div>
                <p className="text-2xl font-bold text-gray-900">{data.total_tweets}</p>
                <p className="text-xs text-gray-400 mt-1">Analyzed</p>
              </div>

              <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-sm font-medium text-gray-500">Positive</h3>
                  <TrendingUp className="w-5 h-5 text-green-500" />
                </div>
                <p className="text-2xl font-bold text-green-600">{data.positive_percentage}%</p>
                <p className="text-xs text-gray-400 mt-1">{data.positive_count} tweets</p>
              </div>

              <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-sm font-medium text-gray-500">Negative</h3>
                  <TrendingDown className="w-5 h-5 text-red-500" />
                </div>
                <p className="text-2xl font-bold text-red-600">{data.negative_percentage}%</p>
                <p className="text-xs text-gray-400 mt-1">{data.negative_count} tweets</p>
              </div>
            </div>

            {/* Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <SentimentChart
                positive={data.positive_count}
                neutral={data.neutral_count}
                negative={data.negative_count}
              />
              <TrendingHashtags hashtags={data.trending_hashtags} />
            </div>

            {/* Timeline Chart */}
            {data.sentiment_over_time.length > 0 && (
              <TimelineChart data={data.sentiment_over_time} />
            )}

            {/* Tweet List */}
            <TweetList tweets={data.tweets} />
          </div>
        )}

        {/* Empty State */}
        {!data && !loading && (
          <div className="text-center py-20">
            <BarChart3 className="w-20 h-20 text-gray-300 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-700 mb-2">
              Analyze Brand Sentiment
            </h3>
            <p className="text-gray-500 max-w-md mx-auto">
              Enter a brand or product name above to analyze real-time Twitter sentiment.
              Get insights on public opinion, trending topics, and more!
            </p>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t mt-20 py-8 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-gray-500 text-sm">
          <p>Brand Sentiment Dashboard • Powered by Free Twitter Scraping (snscrape) + AI Sentiment Analysis</p>
          <p className="mt-1">No API keys required • Real-time data</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
