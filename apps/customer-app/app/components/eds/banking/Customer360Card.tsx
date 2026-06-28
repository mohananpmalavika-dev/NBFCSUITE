import { Badge } from '../foundation/Badge';
import { Typography } from '../foundation/Typography';

export interface Customer360CardProps {
  name: string;
  customerId: string;
  risk: 'low' | 'medium' | 'high';
  relationshipValue: string;
}

const riskToneMap = {
  low: 'success',
  medium: 'warning',
  high: 'danger',
} as const;

export function Customer360Card({ name, customerId, risk, relationshipValue }: Customer360CardProps) {
  return (
    <article className="rounded-xl border border-border-default bg-background-surface p-4 shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <Typography as="h3" variant="h3">
            {name}
          </Typography>
          <Typography variant="caption" tone="muted" className="mt-1">
            {customerId}
          </Typography>
        </div>
        <Badge tone={riskToneMap[risk]}>{risk} risk</Badge>
      </div>
      <div className="mt-4 rounded-xl bg-background-elevated p-3">
        <Typography variant="label" tone="muted">
          Relationship Value
        </Typography>
        <p className="mt-2 text-xl font-semibold text-text-primary">{relationshipValue}</p>
      </div>
    </article>
  );
}
