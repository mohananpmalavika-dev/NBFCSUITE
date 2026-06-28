export type WorkflowStageStatus = 'completed' | 'current' | 'pending' | 'rejected';
export type SlaStatus = 'safe' | 'amber' | 'breached';
export type WorkflowStatus =
  | 'draft'
  | 'submitted'
  | 'validation'
  | 'started'
  | 'approval'
  | 'approved'
  | 'completed'
  | 'rejected'
  | 'returned'
  | 'cancelled'
  | 'expired'
  | 'escalated';

export type WorkflowType = 'sequential' | 'parallel' | 'conditional' | 'dynamic';
export type WorkflowNodeType =
  | 'start'
  | 'task'
  | 'approval'
  | 'decision'
  | 'parallel-merge'
  | 'notification'
  | 'delay'
  | 'script'
  | 'end';

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

export interface WorkflowTask extends WorkflowCardModel {
  module: string;
  branch: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  delegated?: boolean;
  overdue?: boolean;
}

export interface WorkflowComment {
  id: string;
  author: string;
  message: string;
  time: string;
  mentions?: string[];
  attachments?: string[];
}

export interface WorkflowAuditEntry {
  id: string;
  event:
    | 'WORKFLOW_CREATED'
    | 'WORKFLOW_STARTED'
    | 'TASK_ASSIGNED'
    | 'TASK_COMPLETED'
    | 'APPROVAL_GRANTED'
    | 'APPROVAL_REJECTED'
    | 'APPROVAL_RETURNED'
    | 'WORKFLOW_ESCALATED'
    | 'WORKFLOW_CANCELLED'
    | 'WORKFLOW_COMPLETED';
  actor: string;
  time: string;
  description: string;
}

export interface WorkflowDesignerNode {
  id: string;
  label: string;
  type: WorkflowNodeType;
  owner?: string;
  condition?: string;
}

export interface WorkflowAnalyticsMetric {
  label: string;
  value: string;
  helper?: string;
  tone?: 'neutral' | 'success' | 'warning' | 'danger';
}

export interface WorkflowEvent {
  name: WorkflowAuditEntry['event'] | 'ACTION_SELECTED' | 'COMMENT_ADDED' | 'WORKFLOW_VIEWED';
  metadata?: Record<string, string | number | boolean>;
}

export interface WorkflowContract {
  id: string;
  module: string;
  type: WorkflowType;
  configurable: boolean;
  supportsDelegation: boolean;
  supportsEscalation: boolean;
  supportsNotifications: boolean;
  supportsAuditTrail: boolean;
  supportsAnalytics: boolean;
  supportsAiAssistance: boolean;
}

