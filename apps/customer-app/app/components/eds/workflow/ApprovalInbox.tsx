import { Search } from 'lucide-react';
import { Badge } from '../foundation/Badge';
import { ApprovalCard } from './ApprovalCard';
import type { WorkflowActionType, WorkflowApprovalActionAvailability, WorkflowTask } from './types';

export interface ApprovalInboxProps {
  tasks: WorkflowTask[];
  activeTaskId: string;
  onSelectTask: (workflowId: string) => void;
  onAction: (workflowId: string, action: WorkflowActionType) => void;
}

const priorityToneMap = {
  low: 'neutral',
  medium: 'accent',
  high: 'warning',
  critical: 'danger',
} as const;

const actionAvailability: WorkflowApprovalActionAvailability = {
  approve: true,
  reject: true,
  return: true,
  requestChanges: true,
  delegate: true,
  escalate: true,
  hold: true,
};

export function ApprovalInbox({ tasks, activeTaskId, onSelectTask, onAction }: ApprovalInboxProps) {
  const todayCount = tasks.filter((task) => !task.overdue).length;
  const overdueCount = tasks.filter((task) => task.overdue).length;
  const delegatedCount = tasks.filter((task) => task.delegated).length;

  return (
    <section className="rounded-xl border border-border-default bg-background-surface shadow-sm">
      <div className="border-b border-border-default p-4">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h3 className="text-lg font-semibold text-text-primary">Approval Inbox</h3>
            <p className="mt-1 text-sm text-text-secondary">One queue for approvals, overdue work, delegated tasks, and completed decisions.</p>
          </div>
          <div className="flex flex-wrap gap-2">
            <Badge tone="accent">Today {todayCount}</Badge>
            <Badge tone="danger">Overdue {overdueCount}</Badge>
            <Badge tone="neutral">Delegated {delegatedCount}</Badge>
          </div>
        </div>
        <div className="mt-4 flex items-center gap-2 rounded-xl border border-border-default bg-background-elevated px-3 py-2 text-sm text-text-muted">
          <Search className="h-4 w-4" />
          <span>Search workflow ID, transaction, submitter, branch, or approver</span>
        </div>
      </div>

      <div className="max-h-[620px] space-y-3 overflow-y-auto p-4">
        {tasks.map((task) => (
          <div
            key={task.workflowId}
            role="button"
            tabIndex={0}
            onClick={() => onSelectTask(task.workflowId)}
            onKeyDown={(event) => {
              if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                onSelectTask(task.workflowId);
              }
            }}
            className={`block w-full rounded-xl text-left transition duration-normal ease-standard ${
              activeTaskId === task.workflowId ? 'ring-2 ring-border-focus' : ''
            }`}
          >
            <ApprovalCard
              model={task}
              availability={actionAvailability}
              onAction={(action) => onAction(task.workflowId, action)}
            >
              <div className="flex flex-wrap gap-2">
                <Badge tone={priorityToneMap[task.priority]}>{task.priority}</Badge>
                <Badge tone="neutral">{task.module}</Badge>
                <Badge tone="neutral">{task.branch}</Badge>
              </div>
            </ApprovalCard>
          </div>
        ))}
      </div>
    </section>
  );
}
