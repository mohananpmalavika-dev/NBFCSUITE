'use client';

import { FileText, Paperclip, Sparkles, UserCheck } from 'lucide-react';
import { AISummary } from '../ai/AISummary';
import { Badge } from '../foundation/Badge';
import { Button } from '../foundation/Button';
import { ApprovalCard } from './ApprovalCard';
import { AuditTimeline } from './AuditTimeline';
import { SLAIndicator } from './SLAIndicator';
import { WorkflowComments } from './WorkflowComments';
import { WorkflowTimeline } from './WorkflowTimeline';
import type {
  WorkflowActionType,
  WorkflowApprovalActionAvailability,
  WorkflowAuditEntry,
  WorkflowCardModel,
  WorkflowComment,
  WorkflowEvent,
  WorkflowTimelineItem,
} from './types';

export interface WorkflowViewerProps {
  workflow: WorkflowCardModel;
  timeline: WorkflowTimelineItem[];
  comments: WorkflowComment[];
  auditEntries: WorkflowAuditEntry[];
  attachments?: string[];
  availability: WorkflowApprovalActionAvailability;
  onEvent?: (event: WorkflowEvent) => void;
}

export function WorkflowViewer({
  workflow,
  timeline,
  comments,
  auditEntries,
  attachments = [],
  availability,
  onEvent,
}: WorkflowViewerProps) {
  function handleAction(action: WorkflowActionType) {
    onEvent?.({
      name: 'ACTION_SELECTED',
      metadata: {
        action,
        workflowId: workflow.workflowId,
      },
    });
  }

  return (
    <section className="rounded-xl border border-border-default bg-background-surface shadow-sm">
      <div className="border-b border-border-default p-4">
        <div className="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-accent-primary">Workflow Viewer</p>
            <h3 className="mt-2 text-2xl font-semibold text-text-primary">{workflow.transactionTitle}</h3>
            <p className="mt-2 text-sm leading-6 text-text-secondary">
              {workflow.transactionId} submitted by {workflow.submitter}
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <Badge tone="warning">{workflow.currentStageLabel}</Badge>
            <SLAIndicator status={workflow.slaStatus} label={workflow.slaLabel} />
          </div>
        </div>
      </div>

      <div className="grid gap-0 xl:grid-cols-[minmax(0,1fr)_360px]">
        <div className="space-y-4 p-4">
          <ApprovalCard model={workflow} availability={availability} onAction={handleAction}>
            <div className="flex flex-wrap items-center gap-2 text-sm text-text-secondary">
              <UserCheck className="h-4 w-4" />
              Current approver: {workflow.approverPrimary ?? 'Workflow engine'}
            </div>
          </ApprovalCard>

          <div className="rounded-xl border border-border-default bg-background-elevated p-4">
            <div className="flex items-center gap-2">
              <FileText className="h-4 w-4 text-accent-primary" />
              <h3 className="text-sm font-semibold text-text-primary">Workflow Timeline</h3>
            </div>
            <div className="mt-4">
              <WorkflowTimeline items={timeline} />
            </div>
          </div>

          <WorkflowComments
            comments={comments}
            onAddComment={() => onEvent?.({ name: 'COMMENT_ADDED', metadata: { workflowId: workflow.workflowId } })}
          />
        </div>

        <aside className="space-y-4 border-t border-border-default p-4 xl:border-l xl:border-t-0">
          <AISummary
            summary="FinDNA predicts this approval may breach SLA if payroll review is not completed within two hours."
            suggestions={['Escalate to payroll lead', 'Summarize blockers', 'Recommend next approver']}
          />

          <section className="rounded-xl border border-border-default bg-background-elevated p-4">
            <div className="flex items-center gap-2">
              <Paperclip className="h-4 w-4 text-text-muted" />
              <h3 className="text-sm font-semibold text-text-primary">Attachments</h3>
            </div>
            <div className="mt-3 space-y-2">
              {attachments.map((attachment) => (
                <div key={attachment} className="flex items-center justify-between gap-3 rounded-xl bg-background-surface px-3 py-2 text-sm text-text-secondary">
                  <span>{attachment}</span>
                  <Button size="sm" variant="ghost">Open</Button>
                </div>
              ))}
              {attachments.length === 0 ? <p className="text-sm text-text-secondary">No attachments linked.</p> : null}
            </div>
          </section>

          <section className="rounded-xl border border-border-default bg-background-accent p-4">
            <div className="flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-accent-primary" />
              <h3 className="text-sm font-semibold text-text-primary">AI Assistance</h3>
            </div>
            <div className="mt-3 space-y-2 text-sm leading-6 text-text-secondary">
              <p>Explain delay risk, detect bottlenecks, recommend delegation, and summarize audit history.</p>
            </div>
          </section>

          <AuditTimeline entries={auditEntries} />
        </aside>
      </div>
    </section>
  );
}
