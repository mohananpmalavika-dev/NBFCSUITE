import type { ReactNode } from 'react';
import { Badge } from '../foundation/Badge';
import { Typography } from '../foundation/Typography';

import type {
  SlaStatus,
  WorkflowActionType,
  WorkflowCardModel,
  WorkflowApprovalActionAvailability,
  WorkflowStageStatus,
} from './types';
import { ApprovalActions } from './ApprovalActions';

export interface ApprovalCardProps {
  /**
   * Contract-driven version (used by the workflow framework).
   */
  model?: WorkflowCardModel;

  availability?: WorkflowApprovalActionAvailability;
  onAction?: (action: WorkflowActionType) => void;
  children?: ReactNode;

  /**
   * Back-compat props for older demo usage inside AppShell.
   * Prefer `model`.
   */
  title?: string;
  requester?: string;
  amount?: string;
  onApprove?: () => void;
}


const stageToneMap: Record<WorkflowStageStatus, 'warning' | 'success' | 'danger' | 'neutral'> = {
  completed: 'success',
  current: 'warning',
  pending: 'neutral',
  rejected: 'danger',
};

const slaToneMap: Record<SlaStatus, 'success' | 'warning' | 'danger'> = {
  safe: 'success',
  amber: 'warning',
  breached: 'danger',
};

export function ApprovalCard({
  model,
  availability,
  onAction,
  children,
  title,
  requester,
  amount,
  onApprove,
}: ApprovalCardProps) {
  const isBackCompat = !model && (title || requester || amount);
  const displayTitle = isBackCompat ? (title ?? '') : model?.transactionTitle;
  const displaySubmitter = isBackCompat ? (requester ?? '') : model?.submitter;
  const displayTransactionId = isBackCompat ? '' : model?.transactionId;

  const stageStatus = (isBackCompat ? 'pending' : model?.stageStatus) as WorkflowStageStatus;
  const slaStatus = (isBackCompat ? 'safe' : model?.slaStatus) as SlaStatus;


  const displayAmount = isBackCompat ? amount : model?.amount;


  return (
    <article className="rounded-xl border border-border-default bg-background-surface p-4 shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <Typography as="h3" variant="h3">
            {displayTitle}
          </Typography>
          {displaySubmitter ? (
            <Typography tone="secondary" className="mt-1">
              {displaySubmitter}
              {displayTransactionId ? ' • ' + displayTransactionId : ''}
            </Typography>
          ) : null}
        </div>

        <div className="flex items-center gap-2">
          <Badge tone={stageToneMap[stageStatus]}>{stageStatus}</Badge>
          <Badge tone={slaToneMap[slaStatus]}>

            {isBackCompat ? 'SLA: -' : `SLA: ${model?.slaLabel ?? ''}`}
          </Badge>

        </div>
      </div>

      {displayAmount ? (
        <p className="mt-4 text-xl font-semibold text-text-primary">{displayAmount}</p>
      ) : null}
      {children ? <div className="mt-4 text-sm text-text-secondary">{children}</div> : null}

      {isBackCompat && onApprove ? (
        <div className="mt-4">
          <button
            type="button"
            className="w-full rounded-full bg-accent-primary px-4 py-2 text-sm font-semibold"
            style={{ color: 'var(--accent-on-primary)' }}
            onClick={onApprove}
          >
            Approve
          </button>
        </div>
      ) : null}

      {!isBackCompat && availability && onAction ? (
        <ApprovalActions availability={availability} onAction={onAction} />
      ) : null}
    </article>
  );
}

