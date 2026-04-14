import { LucideIcon, TrendingUp, TrendingDown } from "lucide-react";
import { AreaChart, Area, ResponsiveContainer } from "recharts";

interface MetricCardProps {
  icon: LucideIcon;
  label: string;
  value: string;
  trend?: {
    direction: "up" | "down";
    value: string;
  };
  sparklineData?: Array<{ value: number }>;
  variant?: "default" | "success" | "destructive";
}

export function MetricCard({
  icon: Icon,
  label,
  value,
  trend,
  sparklineData,
  variant = "default",
}: MetricCardProps) {
  const variantColors = {
    default: "border-primary/30 bg-gradient-to-br from-card to-card/50",
    success: "border-[#10B981]/30 bg-gradient-to-br from-card to-[#10B981]/5",
    destructive: "border-[#F43F5E]/30 bg-gradient-to-br from-card to-[#F43F5E]/5",
  };

  return (
    <div
      className={`p-5 rounded-lg border backdrop-blur-sm ${variantColors[variant]}`}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="p-2 rounded-lg bg-primary/10">
          <Icon className="w-5 h-5 text-primary" />
        </div>
        {trend && (
          <div
            className={`flex items-center gap-1 text-xs ${
              trend.direction === "up" ? "text-[#10B981]" : "text-[#F43F5E]"
            }`}
          >
            {trend.direction === "up" ? (
              <TrendingUp className="w-3 h-3" />
            ) : (
              <TrendingDown className="w-3 h-3" />
            )}
            <span>{trend.value}</span>
          </div>
        )}
      </div>
      <div className="space-y-1">
        <p className="text-xs text-muted-foreground">{label}</p>
        <p className="text-2xl font-bold">{value}</p>
      </div>
      {sparklineData && (
        <div className="mt-4 h-12">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={sparklineData}>
              <defs>
                <linearGradient id="sparkline" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#06B6D4" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#06B6D4" stopOpacity={0} />
                </linearGradient>
              </defs>
              <Area
                type="monotone"
                dataKey="value"
                stroke="#06B6D4"
                strokeWidth={2}
                fill="url(#sparkline)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
