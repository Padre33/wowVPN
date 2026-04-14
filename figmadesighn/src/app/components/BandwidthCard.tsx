import { TrendingUp, TrendingDown } from "lucide-react";

interface BandwidthCardProps {
  period: string;
  value: string;
  trend: {
    direction: "up" | "down";
    percentage: string;
  };
}

export function BandwidthCard({ period, value, trend }: BandwidthCardProps) {
  return (
    <div className="p-5 rounded-lg border border-primary/30 bg-gradient-to-br from-card to-card/50 backdrop-blur-sm">
      <p className="text-xs text-muted-foreground mb-2">{period}</p>
      <div className="flex items-end justify-between">
        <p className="text-3xl font-bold">{value}</p>
        <div
          className={`flex items-center gap-1 text-sm ${
            trend.direction === "up" ? "text-[#10B981]" : "text-[#F43F5E]"
          }`}
        >
          {trend.direction === "up" ? (
            <TrendingUp className="w-4 h-4" />
          ) : (
            <TrendingDown className="w-4 h-4" />
          )}
          <span>{trend.percentage}</span>
        </div>
      </div>
    </div>
  );
}
