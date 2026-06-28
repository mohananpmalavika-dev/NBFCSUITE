import { ApprovalCard } from '../workflow/ApprovalCard';
import { WidgetContainer } from './WidgetContainer';

import type { WorkflowCardModel } from '../workflow/types';

export interface DashboardApproval {
  workflowId: string;
  transactionTitle: string;
  transactionId: string;
  submitter: string;
  currentStageLabel: string;
  stageStatus: WorkflowCardModel['stageStatus'];
  slaStatus: WorkflowCardModel['slaStatus'];
  slaLabel: string;
  amount?: string;
}

export interface ApprovalWidgetProps {
  approvals: DashboardApproval[];
  onAction?: (action: import('../workflow/types').WorkflowActionType) => void;
}

export function ApprovalWidget({ approvals, onAction }: ApprovalWidgetProps) {
  return (
    <WidgetContainer title="Pending Approvals" category="approval" refreshPolicy="30s" size="lg">
      <div className="grid gap-3 lg:grid-cols-2">
        {approvals.map((approval) => (
          <ApprovalCard
            key={`${approval.transactionId}-${approval.workflowId}`}
            model={approval}
            availability={{ approve: true, reject: true, return: true, requestChanges: true, delegate: true, escalate: true, hold: true }}
            onAction={onAction}
          />
        ))}
      </div>
    </WidgetContainer>
  );
}

