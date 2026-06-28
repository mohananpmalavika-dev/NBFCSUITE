export type WorkflowStageStatus = 'completed' | 'current' | 'pending' | 'rejected';
export type SlaStatus = 'safe' | 'amber' | 'breached';

export type WorkflowActionType =
  | 'approve'
  | 'reject'
  | 'return'
  | 'request-changes'
  | 'delegate'
  | 'escalate'
  | 'hold';

export interface WorkflowApprovalActionAvailability {
  approve?: boolean;
  reject?: boolean;
  return?: boolean;
  requestChanges?: boolean;
  delegate?: boolean;
  escalate?: boolean;
  hold?: boolean;
}

export interface WorkflowTimelineItem {
  title: string;
  description?: string;
  time?: string;
  actor?: string;
  state?: WorkflowStageStatus | 'assigned';
}

export interface WorkflowCardModel {
  workflowId: string;
  transactionTitle: string;
  transactionId: string;
  submitter: string;
  currentStageLabel: string;
  stageStatus: WorkflowStageStatus;
  slaStatus: SlaStatus;
  slaLabel: string;
  amount?: string;
  approverPrimary?: string;
}

