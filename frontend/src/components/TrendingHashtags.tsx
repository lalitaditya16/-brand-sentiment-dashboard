import { Hash } from 'lucide-react';

interface Props {
  hashtags: Array<{
    tag: string;
    count: number;
  }>;
}

export default function TrendingHashtags({ hashtags }: Props) {
  if (hashtags.length === 0) {
    return (
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <Hash className="w-5 h-5" />
          Trending Hashtags
        </h2>
        <p className="text-gray-500 text-sm">No hashtags found in the analyzed tweets</p>
      </div>
    );
  }

  const maxCount = Math.max(...hashtags.map(h => h.count));

  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
      <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
        <Hash className="w-5 h-5" />
        Trending Hashtags
      </h2>
      <div className="space-y-3">
        {hashtags.map((hashtag, index) => (
          <div key={index} className="flex items-center gap-3">
            <span className="text-sm font-medium text-gray-700 w-32 truncate">
              {hashtag.tag}
            </span>
            <div className="flex-1 bg-gray-100 rounded-full h-6 relative overflow-hidden">
              <div
                className="bg-blue-500 h-full rounded-full transition-all duration-500"
                style={{ width: `${(hashtag.count / maxCount) * 100}%` }}
              />
              <span className="absolute right-2 top-1/2 transform -translate-y-1/2 text-xs font-medium text-gray-700">
                {hashtag.count}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
