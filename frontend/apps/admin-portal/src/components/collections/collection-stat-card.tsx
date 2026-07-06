/**
 * Collection Stat Card Component
 * Reusable card for displaying collection statistics
 */

import { LucideIcon } from "lucide-react";
import { ArrowUpRight, ArrowDownRight } from "lucide-react";

interface CollectionStatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  color: string;
  trend?: {
    value: number;
    isPositive: boolean;
    label?: string;
  };
  onClick?: () => void;
}

export function CollectionStatCard({
  title,
  value,
  subtitle,
  icon: Icon,
  color,
  trend,
  onClick
}: CollectionStatCardProps) {
  return (
    <div
      className={`bg-white rounded-lg shadow-sm border border-gray-200 p-6 ${
        onClick ? "cursor-pointer hover:shadow-md transition-shadow" : ""
      }`}
      onClick={onClick}
    >
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="mt-2 text-3xl font-bold text-gray-900">{value}</p>
          {subtitle && (
            <p className="mt-1 text-sm text-gray-500">{subtitle}</p>
          )}
          {trend && (
            <div className="mt-2 flex items-center">
              {trend.isPositive ? (
                <ArrowDownRight className="h-4 w-4 text-green-500" />
              ) : (
                <ArrowUpRight className="h-4 w-4 text-red-500" />
              )}
              <span
                className={`text-sm font-medium ${
                  trend.isPositive ? "text-green-600" : "text-red-600"
                }`}
              >
                {Math.abs(trend.value).toFixed(1)}%
              </span>
              {trend.label && (
                <span className="ml-2 text-sm text-gray-500">{trend.label}</span>
              )}
            </div>
          )}
        </div>
        <div className={`p-3 rounded-full ${color}`}>
          <Icon className="h-6 w-6 text-white" />
        </div>
      </div>
    </div>
  );
}
