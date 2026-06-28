import { BarChart3 } from 'lucide-react';
import { MetricCard } from '../data-display/MetricCard';
import type { WorkflowAnalyticsMetric } from './types';

export interface WorkflowAnalyticsProps {
  metrics: WorkflowAnalyticsMetric[];
}

export function WorkflowAnalytics({ metrics }: WorkflowAnalyticsProps) {
  return (
    <section className="rounded-xl border border-border-default bg-background-surface p-4 shadow-sm">
      <div className="flex items-center gap-2">
        <BarChart3 className="h-5 w-5 text-accent-primary" />
        <h3 className="text-lg font-semibold text-text-primary">Workflow Analytics</h3>
      </div>
      <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        {metrics.map((metric) => (
          <MetricCard key={metric.label} label={metric.label} value={metric.value} helper={metric.helper} tone={metric.tone} />
        ))}
      </div>
    </section>
  );
}
