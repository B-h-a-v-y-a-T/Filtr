import MetricCard from "@/components/MetricCard";
import { AlertTriangle, CheckCircle, TrendingUp, Users, Globe, Clock } from "lucide-react";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";

const trendData = [
  { time: "00:00", alerts: 12, verified: 8 },
  { time: "04:00", alerts: 19, verified: 14 },
  { time: "08:00", alerts: 35, verified: 28 },
  { time: "12:00", alerts: 52, verified: 41 },
  { time: "16:00", alerts: 48, verified: 39 },
  { time: "20:00", alerts: 31, verified: 25 },
];

const sentimentData = [
  { name: "Positive", value: 234, color: "hsl(var(--success))" },
  { name: "Neutral", value: 456, color: "hsl(var(--muted-foreground))" },
  { name: "Negative", value: 189, color: "hsl(var(--critical))" },
];

const regionData = [
  { region: "North America", incidents: 145 },
  { region: "Europe", incidents: 98 },
  { region: "Asia", incidents: 176 },
  { region: "South America", incidents: 67 },
  { region: "Africa", incidents: 54 },
];

const Dashboard = () => {
  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="animate-fade-in">
        <h1 className="text-4xl font-bold text-foreground mb-2">
          Command Center
        </h1>
        <p className="text-muted-foreground">
          Real-time overview of global crisis information
        </p>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <MetricCard
          title="Active Alerts"
          value="127"
          change="+12% from yesterday"
          changeType="negative"
          icon={AlertTriangle}
          variant="critical"
        />
        <MetricCard
          title="Verified Sources"
          value="1,234"
          change="+8% this week"
          changeType="positive"
          icon={CheckCircle}
          variant="success"
        />
        <MetricCard
          title="Misinformation Detected"
          value="43"
          change="-5% from last hour"
          changeType="positive"
          icon={TrendingUp}
          variant="warning"
        />
        <MetricCard
          title="Active Monitors"
          value="2,847"
          change="Stable"
          changeType="neutral"
          icon={Users}
          variant="primary"
        />
        <MetricCard
          title="Regions Covered"
          value="87"
          change="+3 new regions"
          changeType="positive"
          icon={Globe}
          variant="accent"
        />
        <MetricCard
          title="Avg Response Time"
          value="2.4m"
          change="-12% faster"
          changeType="positive"
          icon={Clock}
          variant="primary"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Trend Chart */}
        <div className="rounded-xl bg-card p-6 shadow-md animate-fade-in">
          <h3 className="text-lg font-semibold text-foreground mb-4">
            Alert Trends (24h)
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={trendData}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis dataKey="time" stroke="hsl(var(--muted-foreground))" />
              <YAxis stroke="hsl(var(--muted-foreground))" />
              <Tooltip
                contentStyle={{
                  backgroundColor: "hsl(var(--card))",
                  border: "1px solid hsl(var(--border))",
                  borderRadius: "8px",
                }}
              />
              <Line
                type="monotone"
                dataKey="alerts"
                stroke="hsl(var(--critical))"
                strokeWidth={3}
                dot={{ fill: "hsl(var(--critical))", r: 4 }}
              />
              <Line
                type="monotone"
                dataKey="verified"
                stroke="hsl(var(--success))"
                strokeWidth={3}
                dot={{ fill: "hsl(var(--success))", r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Sentiment Distribution */}
        <div className="rounded-xl bg-card p-6 shadow-md animate-fade-in">
          <h3 className="text-lg font-semibold text-foreground mb-4">
            Sentiment Distribution
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={sentimentData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) =>
                  `${name}: ${(percent * 100).toFixed(0)}%`
                }
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {sentimentData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: "hsl(var(--card))",
                  border: "1px solid hsl(var(--border))",
                  borderRadius: "8px",
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Regional Overview */}
        <div className="rounded-xl bg-card p-6 shadow-md animate-fade-in lg:col-span-2">
          <h3 className="text-lg font-semibold text-foreground mb-4">
            Incidents by Region
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={regionData}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis dataKey="region" stroke="hsl(var(--muted-foreground))" />
              <YAxis stroke="hsl(var(--muted-foreground))" />
              <Tooltip
                contentStyle={{
                  backgroundColor: "hsl(var(--card))",
                  border: "1px solid hsl(var(--border))",
                  borderRadius: "8px",
                }}
              />
              <Bar
                dataKey="incidents"
                fill="hsl(var(--primary))"
                radius={[8, 8, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
