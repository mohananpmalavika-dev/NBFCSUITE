import { Button } from '../foundation/Button';
import type { WorkflowActionType } from './types';

export interface ApprovalActionsProps {
  availability: {
    approve?: boolean;
    reject?: boolean;
    return?: boolean;
    requestChanges?: boolean;
    delegate?: boolean;
    escalate?: boolean;
    hold?: boolean;
  };
  onAction: (action: WorkflowActionType) => void;
}

export function ApprovalActions({ availability, onAction }: ApprovalActionsProps) {
  const actions: Array<{ key: WorkflowActionType; label: string; enabled: boolean }> = [
    { key: 'approve', label: 'Approve', enabled: Boolean(availability.approve) },
    { key: 'reject', label: 'Reject', enabled: Boolean(availability.reject) },
    { key: 'return', label: 'Return', enabled: Boolean(availability.return) },
    { key: 'request-changes', label: 'Request changes', enabled: Boolean(availability.requestChanges) },
    { key: 'delegate', label: 'Delegate', enabled: Boolean(availability.delegate) },
    { key: 'escalate', label: 'Escalate', enabled: Boolean(availability.escalate) },
    { key: 'hold', label: 'Put on hold', enabled: Boolean(availability.hold) },
  ];

  return (
    <div className="mt-4 flex flex-wrap gap-2">
      {actions
        .filter((a) => a.enabled)
        .map((a) => (
          <Button key={a.key} size="sm" onClick={() => onAction(a.key)}>
            {a.label}
          </Button>
        ))}
    </div>
  );
}

