import { Badge } from '../foundation/Badge';
import { Typography } from '../foundation/Typography';

export interface LoanSummaryCardProps {
  accountNumber: string;
  product: string;
  outstanding: string;
  status: 'standard' | 'watchlist' | 'npa';
}

const statusToneMap = {
  standard: 'success',
  watchlist: 'warning',
  npa: 'danger',
} as const;

export function LoanSummaryCard({ accountNumber, product, outstanding, status }: LoanSummaryCardProps) {
  return (
    <article className="rounded-xl border border-border-default bg-background-surface p-4 shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <Typography as="h3" variant="h3">
            {product}
          </Typography>
          <Typography variant="caption" tone="muted" className="mt-1">
            {accountNumber}
          </Typography>
        </div>
        <Badge tone={statusToneMap[status]}>{status}</Badge>
      </div>
      <Typography variant="label" tone="muted" className="mt-4">
        Outstanding
      </Typography>
      <p className="mt-2 text-xl font-semibold text-text-primary">{outstanding}</p>
    </article>
  );
}
