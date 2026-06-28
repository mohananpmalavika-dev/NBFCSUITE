import { TrendingDown, TrendingUp } from 'lucide-react';
import { Typography } from '../foundation/Typography';
import { WidgetContainer } from './WidgetContainer';

export interface KPIWidgetProps {
  title: string;
  value: string;
  trend: 'up' | 'down';
  change: string;
  drilldownTarget?: string;
}

export function KPIWidget({ title, value, trend, change, drilldownTarget }: KPIWidgetProps) {
  const TrendIcon = trend === 'up' ? TrendingUp : TrendingDown;

  return (
    <WidgetContainer title={title} category="kpi" refreshPolicy="30s" size="sm">
      <p className="text-3xl font-semibold text-text-primary">{value}</p>
      <div className={`mt-3 inline-flex items-center gap-2 text-sm font-semibold ${trend === 'up' ? 'text-accent-success' : 'text-accent-danger'}`}>
        <TrendIcon className="h-4 w-4" />
        {change}
      </div>
      {drilldownTarget ? (
        <Typography variant="caption" tone="muted" className="mt-3">
          Drill-down: {drilldownTarget}
        </Typography>
      ) : null}
    </WidgetContainer>
  );
}
