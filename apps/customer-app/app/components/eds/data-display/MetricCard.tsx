import type { ReactNode } from 'react';
import { Typography } from '../foundation/Typography';

export interface MetricCardProps {
  label: string;
  value: string;
  helper?: string;
  icon?: ReactNode;
  tone?: 'neutral' | 'success' | 'warning' | 'danger';
}

const toneClassMap = {
  neutral: 'text-accent-primary',
  success: 'text-accent-success',
  warning: 'text-accent-warning',
  danger: 'text-accent-danger',
};

export function MetricCard({ label, value, helper, icon, tone = 'neutral' }: MetricCardProps) {
  return (
    <article className="rounded-xl border border-border-default bg-background-surface p-4 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <div>
          <Typography variant="label" tone="muted">
            {label}
          </Typography>
          <p className="mt-3 text-2xl font-semibold text-text-primary">{value}</p>
        </div>
        {icon ? <div className={`${toneClassMap[tone]} shrink-0`}>{icon}</div> : null}
      </div>
      {helper ? (
        <Typography tone="secondary" className="mt-2">
          {helper}
        </Typography>
      ) : null}
    </article>
  );
}
