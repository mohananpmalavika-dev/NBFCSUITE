import type { ReactNode } from 'react';
import { Badge } from '../foundation/Badge';
import { Button } from '../foundation/Button';
import { Typography } from '../foundation/Typography';

export interface ApprovalCardProps {
  title: string;
  requester: string;
  amount?: string;
  status?: 'pending' | 'approved' | 'rejected';
  children?: ReactNode;
  onApprove?: () => void;
}

const statusToneMap = {
  pending: 'warning',
  approved: 'success',
  rejected: 'danger',
} as const;

export function ApprovalCard({
  title,
  requester,
  amount,
  status = 'pending',
  children,
  onApprove,
}: ApprovalCardProps) {
  return (
    <article className="rounded-xl border border-border-default bg-background-surface p-4 shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <Typography as="h3" variant="h3">
            {title}
          </Typography>
          <Typography tone="secondary" className="mt-1">
            {requester}
          </Typography>
        </div>
        <Badge tone={statusToneMap[status]}>{status}</Badge>
      </div>
      {amount ? <p className="mt-4 text-xl font-semibold text-text-primary">{amount}</p> : null}
      {children ? <div className="mt-4 text-sm text-text-secondary">{children}</div> : null}
      {onApprove ? (
        <div className="mt-4">
          <Button size="sm" onClick={onApprove}>
            Approve
          </Button>
        </div>
      ) : null}
    </article>
  );
}
