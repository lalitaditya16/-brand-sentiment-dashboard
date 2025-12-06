import { Heart, Repeat2, TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface Tweet {
  text: string;
  created_at: string;
  sentiment_score: number;
  sentiment_label: string;
  username: string;
  likes: number;
  retweets: number;
}

interface Props {
  tweets: Tweet[];
}

export default function TweetList({ tweets }: Props) {
  const getSentimentBadge = (label: string) => {
    const badges = {
      Positive: 'bg-green-100 text-green-800 border-green-200',
      Negative: 'bg-red-100 text-red-800 border-red-200',
      Neutral: 'bg-gray-100 text-gray-800 border-gray-200',
    };
    return badges[label as keyof typeof badges] || badges.Neutral;
  };

  const getSentimentIcon = (label: string) => {
    if (label === 'Positive') return <TrendingUp className="w-3 h-3" />;
    if (label === 'Negative') return <TrendingDown className="w-3 h-3" />;
    return <Minus className="w-3 h-3" />;
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Tweets</h2>
      <div className="space-y-4 max-h-[600px] overflow-y-auto">
        {tweets.map((tweet, index) => (
          <div
            key={index}
            className="p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:shadow-sm transition"
          >
            <div className="flex items-start justify-between gap-3 mb-2">
              <div className="flex items-center gap-2">
                <span className="font-semibold text-sm text-gray-900">@{tweet.username}</span>
                <span className="text-xs text-gray-500">{formatDate(tweet.created_at)}</span>
              </div>
              <span
                className={`px-2 py-1 rounded-full text-xs font-medium border flex items-center gap-1 ${getSentimentBadge(
                  tweet.sentiment_label
                )}`}
              >
                {getSentimentIcon(tweet.sentiment_label)}
                {tweet.sentiment_label}
              </span>
            </div>
            
            <p className="text-gray-700 text-sm mb-3 leading-relaxed">{tweet.text}</p>
            
            <div className="flex items-center gap-4 text-xs text-gray-500">
              <div className="flex items-center gap-1">
                <Heart className="w-4 h-4" />
                <span>{tweet.likes}</span>
              </div>
              <div className="flex items-center gap-1">
                <Repeat2 className="w-4 h-4" />
                <span>{tweet.retweets}</span>
              </div>
              <div className="ml-auto">
                Score: {tweet.sentiment_score.toFixed(2)}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
