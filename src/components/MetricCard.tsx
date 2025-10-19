import { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface MetricCardProps {
  title: string;
  value: string | number;
  change?: string;
  changeType?: "positive" | "negative" | "neutral";
  icon: LucideIcon;
  variant?: "primary" | "accent" | "success" | "warning" | "critical";
}

const MetricCard = ({
  title,
  value,
  change,
  changeType = "neutral",
  icon: Icon,
  variant = "primary",
}: MetricCardProps) => {
  const variantClasses = {
    primary: "bg-gradient-primary text-primary-foreground",
    accent: "bg-gradient-to-br from-accent to-accent-glow text-accent-foreground",
    success: "bg-gradient-success text-success-foreground",
    warning: "bg-gradient-warning text-warning-foreground",
    critical: "bg-gradient-critical text-critical-foreground",
  };

  const changeClasses = {
    positive: "text-success-foreground bg-success/20",
    negative: "text-critical-foreground bg-critical/20",
    neutral: "text-muted-foreground bg-muted",
  };

  return (
    <div className="group relative overflow-hidden rounded-xl bg-card shadow-md hover:shadow-lg transition-all duration-300 animate-fade-in">
      <div className="absolute inset-0 bg-gradient-card opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
      
      <div className="relative p-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <p className="text-sm font-medium text-muted-foreground mb-1">
              {title}
            </p>
            <p className="text-3xl font-bold text-foreground mb-2">
              {value}
            </p>
            {change && (
              <span
                className={cn(
                  "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium",
                  changeClasses[changeType]
                )}
              >
                {change}
              </span>
            )}
          </div>
          
          <div
            className={cn(
              "rounded-xl p-3 shadow-md",
              variantClasses[variant]
            )}
          >
            <Icon className="h-6 w-6" />
          </div>
        </div>
      </div>
    </div>
  );
};

export default MetricCard;
