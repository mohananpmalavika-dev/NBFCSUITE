import { Clock3 } from 'lucide-react';
import { Badge } from '../foundation/Badge';
import type { SlaStatus } from './types';

export interface SLAIndicatorProps {
  status: SlaStatus;
  label: string;
}

const toneMap = {
  safe: 'success',
  amber: 'warning',
  breached: 'danger',
} as const;

export function SLAIndicator({ status, label }: SLAIndicatorProps) {
  return (
    <div className="inline-flex items-center gap-2 rounded-full border border-border-default bg-background-surface px-3 py-2 text-sm font-semibold text-text-secondary">
      <Clock3 className="h-4 w-4 text-text-muted" />
      <span>{label}</span>
      <Badge tone={toneMap[status]} className="px-2 py-0.5 text-xs">
        {status}
      </Badge>
    </div>
  );
}
