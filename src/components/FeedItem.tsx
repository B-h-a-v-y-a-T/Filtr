import { cn } from "@/lib/utils";
import { Clock, TrendingUp, TrendingDown, Minus } from "lucide-react";

interface FeedItemProps {
  source: string;
  content: string;
  timestamp: string;
  sentiment: "positive" | "negative" | "neutral";
  platform: string;
  region?: string;
}

const FeedItem = ({
  source,
  content,
  timestamp,
  sentiment,
  platform,
  region,
}: FeedItemProps) => {
  const sentimentConfig = {
    positive: {
      icon: TrendingUp,
      color: "text-success",
      bg: "bg-success/10",
      border: "border-success/30",
    },
    negative: {
      icon: TrendingDown,
      color: "text-critical",
      bg: "bg-critical/10",
      border: "border-critical/30",
    },
    neutral: {
      icon: Minus,
      color: "text-muted-foreground",
      bg: "bg-muted/50",
      border: "border-border",
    },
  };

  const config = sentimentConfig[sentiment];
  const SentimentIcon = config.icon;

  return (
    <div
      className={cn(
        "group rounded-lg border-2 bg-card p-4 shadow-sm hover:shadow-md transition-all duration-200 animate-fade-in",
        config.border
      )}
    >
      <div className="flex items-start gap-3">
        <div className={cn("rounded-lg p-2", config.bg)}>
          <SentimentIcon className={cn("h-5 w-5", config.color)} />
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <span className="font-semibold text-foreground">{source}</span>
              <span className="text-xs text-muted-foreground">•</span>
              <span className="text-xs font-medium text-primary">
                {platform}
              </span>
              {region && (
                <>
                  <span className="text-xs text-muted-foreground">•</span>
                  <span className="text-xs text-muted-foreground">{region}</span>
                </>
              )}
            </div>
            <div className="flex items-center gap-1 text-xs text-muted-foreground">
              <Clock className="h-3 w-3" />
              <span>{timestamp}</span>
            </div>
          </div>

          <p className="text-sm text-foreground leading-relaxed line-clamp-2">
            {content}
          </p>
        </div>
      </div>
    </div>
  );
};

export default FeedItem;
