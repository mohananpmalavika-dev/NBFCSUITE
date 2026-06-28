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
  model: WorkflowCardModel;
  availability?: WorkflowApprovalActionAvailability;
  onAction?: (action: WorkflowActionType) => void;
  children?: ReactNode;
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

export function ApprovalCard({ model, availability, onAction, children }: ApprovalCardProps) {
  return (
    <article className="rounded-xl border border-border-default bg-background-surface p-4 shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <Typography as="h3" variant="h3">
            {model.transactionTitle}
          </Typography>
          <Typography tone="secondary" className="mt-1">
            {model.submitter}
            {' • ' + model.transactionId}

          </Typography>
        </div>

        <div className="flex items-center gap-2">
          <Badge tone={stageToneMap[model.stageStatus]}>{model.stageStatus}</Badge>
          <Badge tone={slaToneMap[model.slaStatus]}>SLA: {model.slaLabel}</Badge>
        </div>
      </div>

      {model.amount ? <p className="mt-4 text-xl font-semibold text-text-primary">{model.amount}</p> : null}
      {children ? <div className="mt-4 text-sm text-text-secondary">{children}</div> : null}

      {availability && onAction ? (
        <ApprovalActions availability={availability} onAction={onAction} />
      ) : null}
    </article>
  );
}
