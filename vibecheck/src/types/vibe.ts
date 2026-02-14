export interface RedditData {
  username: string;
  totalKarma: number;
  linkKarma: number;
  commentKarma: number;
  accountAgeDays: number;
  avatarUrl: string;
  displayName: string;
  mock: boolean;
  totalPosts?: number;
  totalComments?: number;
  avgPostScore?: number;
  avgCommentScore?: number;
  bestPost?: { title: string; score: number; subreddit: string; permalink: string };
  mostDiscussed?: { title: string; numComments: number; subreddit: string };
  topSubreddits?: Array<{ name: string; total: number; posts: number; comments: number }>;
  uniqueSubreddits?: number;
  trophies?: string[];
  activityHeatmap?: { hours: number[]; peakHour: number; peakDay: string };
  topDomains?: Array<{ domain: string; count: number }>;
  avgCommentLength?: number;
  nsfwPercent?: number;
  controversialPosts?: number;
  postsPerMonth?: number;
  llmSummary?: string;
}

export interface YouTubeData {
  channelName: string;
  channelDescription: string;
  channelThumbnail: string;
  subscribers: number;
  hiddenSubscribers: boolean;
  totalViews: number;
  videoCount: number;
  watchHours: number;
  topCategory: string;
  notFound?: boolean;
  mock: boolean;
  topVideos?: Array<{ title: string; views: number }>;
  avgViewsPerVideo?: number;
  likedVideos?: number;
  subscriptions?: number;
  playlists?: number;
  recentUploads?: Array<{ title: string; views: number }>;
}

export interface VibeData {
  platform: "reddit" | "youtube";
  reddit?: RedditData;
  youtube?: YouTubeData;
}

export interface WrappedSlideData {
  label: string;
  value: string;
  detail: string;
}

export interface EvidenceItem {
  platform: string;
  source: string;
  topic: string;
  tone: string;
  text?: string;
  engagement_score?: number;
  controversy_score?: number;
  clickbait_score?: number;
}

export interface AlgoProfile {
  counts: { items: number };
  topic_raw: Record<string, number>;
  topic_weighted: Record<string, number>;
  tone_raw: Record<string, number>;
  tone_weighted: Record<string, number>;
  lift: Record<string, number>;
  diversity: { topic_entropy: number; top5_source_share: number };
  evidence: {
    most_reinforced: EvidenceItem[];
    most_intense: EvidenceItem[];
  };
}

export interface IngestPayload {
  userId: string;
  redditUsername?: string;
  youtubeSources?: Record<string, unknown>[] | null;
  maxRedditItems?: number;
}

export interface IngestResponse {
  user_id: string;
  items: number;
  metrics_keys: string[];
}
