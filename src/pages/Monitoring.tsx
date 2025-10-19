import { useState } from "react";
import FeedItem from "@/components/FeedItem";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Search, Filter, RefreshCw } from "lucide-react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

const mockFeed = [
  {
    id: 1,
    source: "CNN Breaking",
    content: "Major policy announcement expected from government officials regarding new crisis management protocols.",
    timestamp: "2 min ago",
    sentiment: "neutral" as const,
    platform: "Twitter",
    region: "North America",
  },
  {
    id: 2,
    source: "Local News Network",
    content: "Emergency services respond swiftly to coordinated incident. All personnel accounted for and safe.",
    timestamp: "5 min ago",
    sentiment: "positive" as const,
    platform: "Facebook",
    region: "Europe",
  },
  {
    id: 3,
    source: "Global Observer",
    content: "Unverified reports circulating about potential misinformation campaign. Investigation ongoing by fact-checkers.",
    timestamp: "12 min ago",
    sentiment: "negative" as const,
    platform: "Reddit",
    region: "Asia",
  },
  {
    id: 4,
    source: "Reuters",
    content: "International cooperation strengthens response capabilities. Multiple agencies coordinate effectively.",
    timestamp: "18 min ago",
    sentiment: "positive" as const,
    platform: "Twitter",
    region: "Global",
  },
  {
    id: 5,
    source: "Independent Media",
    content: "Analysis reveals patterns in recent social media activity suggesting coordinated disinformation efforts.",
    timestamp: "25 min ago",
    sentiment: "negative" as const,
    platform: "Instagram",
    region: "South America",
  },
  {
    id: 6,
    source: "Tech News Daily",
    content: "New AI-powered monitoring tools show promising results in early detection of false narratives.",
    timestamp: "32 min ago",
    sentiment: "positive" as const,
    platform: "LinkedIn",
    region: "North America",
  },
];

const Monitoring = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [platform, setPlatform] = useState("all");
  const [region, setRegion] = useState("all");

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="animate-fade-in">
        <h1 className="text-4xl font-bold text-foreground mb-2">
          Live Monitoring Feed
        </h1>
        <p className="text-muted-foreground">
          Real-time social media and news monitoring
        </p>
      </div>

      {/* Filters */}
      <div className="rounded-xl bg-card p-6 shadow-md animate-fade-in">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="md:col-span-2">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Search by keyword..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>

          <Select value={platform} onValueChange={setPlatform}>
            <SelectTrigger>
              <SelectValue placeholder="Platform" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Platforms</SelectItem>
              <SelectItem value="twitter">Twitter</SelectItem>
              <SelectItem value="facebook">Facebook</SelectItem>
              <SelectItem value="reddit">Reddit</SelectItem>
              <SelectItem value="instagram">Instagram</SelectItem>
              <SelectItem value="linkedin">LinkedIn</SelectItem>
            </SelectContent>
          </Select>

          <Select value={region} onValueChange={setRegion}>
            <SelectTrigger>
              <SelectValue placeholder="Region" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Regions</SelectItem>
              <SelectItem value="north-america">North America</SelectItem>
              <SelectItem value="europe">Europe</SelectItem>
              <SelectItem value="asia">Asia</SelectItem>
              <SelectItem value="south-america">South America</SelectItem>
              <SelectItem value="africa">Africa</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="flex gap-2 mt-4">
          <Button variant="outline" size="sm" className="gap-2">
            <Filter className="h-4 w-4" />
            Advanced Filters
          </Button>
          <Button variant="outline" size="sm" className="gap-2">
            <RefreshCw className="h-4 w-4" />
            Refresh Feed
          </Button>
        </div>
      </div>

      {/* Feed */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <p className="text-sm text-muted-foreground">
            Showing {mockFeed.length} recent posts
          </p>
          <div className="flex items-center gap-2">
            <div className="h-2 w-2 rounded-full bg-success animate-pulse-glow" />
            <span className="text-sm text-success font-medium">Live</span>
          </div>
        </div>

        <div className="space-y-3">
          {mockFeed.map((item) => (
            <FeedItem key={item.id} {...item} />
          ))}
        </div>

        <Button variant="outline" className="w-full">
          Load More
        </Button>
      </div>
    </div>
  );
};

export default Monitoring;
