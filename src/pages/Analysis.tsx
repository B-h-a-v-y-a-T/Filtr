import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import VerificationWorkbench from "@/components/VerificationWorkbench";
import { Search, TrendingUp, AlertTriangle, CheckCircle } from "lucide-react";
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from "recharts";

const topicData = [
  { topic: "Climate", x: 65, y: 80, credibility: 85 },
  { topic: "Politics", x: 45, y: 30, credibility: 40 },
  { topic: "Health", x: 80, y: 70, credibility: 90 },
  { topic: "Economy", x: 55, y: 60, credibility: 75 },
  { topic: "Tech", x: 90, y: 85, credibility: 95 },
];

const credibilityData = [
  { factor: "Source Reputation", value: 85 },
  { factor: "Fact-Check Score", value: 78 },
  { factor: "Cross-Reference", value: 92 },
  { factor: "Author History", value: 88 },
  { factor: "Evidence Quality", value: 75 },
  { factor: "Bias Detection", value: 82 },
];

const insights = [
  {
    id: 1,
    type: "verified",
    title: "High Credibility Source Cluster",
    description: "Identified 15 interconnected verified sources discussing climate policy changes.",
    confidence: 94,
  },
  {
    id: 2,
    type: "warning",
    title: "Potential Misinformation Pattern",
    description: "Detected coordinated messaging across 8 low-credibility accounts about economic data.",
    confidence: 87,
  },
  {
    id: 3,
    type: "critical",
    title: "Viral Misinformation Alert",
    description: "Rapidly spreading false narrative identified. 50k+ shares in the last 2 hours.",
    confidence: 96,
  },
];

const Analysis = () => {
  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="animate-fade-in">
        <h1 className="text-4xl font-bold text-foreground mb-2">
          AI-Driven Crisis Analysis
        </h1>
        <p className="text-muted-foreground">
          Advanced insights and credibility assessment
        </p>
      </div>

      {/* Verification Workbench */}
      <VerificationWorkbench />

      {/* AI Insights */}
      <div className="space-y-4">
        <h2 className="text-2xl font-semibold text-foreground">
          Key Insights
        </h2>
        <div className="grid grid-cols-1 gap-4">
          {insights.map((insight) => (
            <div
              key={insight.id}
              className="rounded-xl bg-card p-6 shadow-md hover:shadow-lg transition-all duration-200 animate-fade-in border-l-4"
              style={{
                borderLeftColor:
                  insight.type === "verified"
                    ? "hsl(var(--success))"
                    : insight.type === "warning"
                    ? "hsl(var(--warning))"
                    : "hsl(var(--critical))",
              }}
            >
              <div className="flex items-start gap-4">
                <div
                  className={`rounded-lg p-3 ${
                    insight.type === "verified"
                      ? "bg-success/10"
                      : insight.type === "warning"
                      ? "bg-warning/10"
                      : "bg-critical/10"
                  }`}
                >
                  {insight.type === "verified" ? (
                    <CheckCircle className="h-6 w-6 text-success" />
                  ) : insight.type === "warning" ? (
                    <TrendingUp className="h-6 w-6 text-warning" />
                  ) : (
                    <AlertTriangle className="h-6 w-6 text-critical" />
                  )}
                </div>

                <div className="flex-1">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-lg font-semibold text-foreground">
                      {insight.title}
                    </h3>
                    <span className="text-sm font-medium text-primary">
                      {insight.confidence}% confidence
                    </span>
                  </div>
                  <p className="text-muted-foreground">{insight.description}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Topic Clustering */}
        <div className="rounded-xl bg-card p-6 shadow-md animate-fade-in">
          <h3 className="text-lg font-semibold text-foreground mb-4">
            Topic Clustering & Credibility
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <ScatterChart>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis
                type="number"
                dataKey="x"
                name="Engagement"
                stroke="hsl(var(--muted-foreground))"
              />
              <YAxis
                type="number"
                dataKey="y"
                name="Reach"
                stroke="hsl(var(--muted-foreground))"
              />
              <Tooltip
                cursor={{ strokeDasharray: "3 3" }}
                contentStyle={{
                  backgroundColor: "hsl(var(--card))",
                  border: "1px solid hsl(var(--border))",
                  borderRadius: "8px",
                }}
              />
              <Scatter
                name="Topics"
                data={topicData}
                fill="hsl(var(--primary))"
              >
                {topicData.map((entry, index) => (
                  <circle
                    key={`dot-${index}`}
                    r={entry.credibility / 5}
                    fill={
                      entry.credibility > 80
                        ? "hsl(var(--success))"
                        : entry.credibility > 60
                        ? "hsl(var(--warning))"
                        : "hsl(var(--critical))"
                    }
                  />
                ))}
              </Scatter>
            </ScatterChart>
          </ResponsiveContainer>
        </div>

        {/* Credibility Factors */}
        <div className="rounded-xl bg-card p-6 shadow-md animate-fade-in">
          <h3 className="text-lg font-semibold text-foreground mb-4">
            Credibility Assessment Factors
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <RadarChart data={credibilityData}>
              <PolarGrid stroke="hsl(var(--border))" />
              <PolarAngleAxis
                dataKey="factor"
                stroke="hsl(var(--muted-foreground))"
                tick={{ fontSize: 12 }}
              />
              <PolarRadiusAxis
                angle={90}
                domain={[0, 100]}
                stroke="hsl(var(--muted-foreground))"
              />
              <Radar
                name="Score"
                dataKey="value"
                stroke="hsl(var(--accent))"
                fill="hsl(var(--accent))"
                fillOpacity={0.6}
              />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default Analysis;
