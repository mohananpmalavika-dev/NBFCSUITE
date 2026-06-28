import { GitPullRequestArrow, ShieldCheck } from 'lucide-react';
import { Badge } from '../foundation/Badge';
import type { WizardApprovalStatus } from './types';

export interface WizardApprovalProps {
  required: boolean;
  status: WizardApprovalStatus;
  approver?: string;
}

const toneMap = {
  'not-required': 'neutral',
  draft: 'neutral',
  pending: 'warning',
  approved: 'success',
} as const;

export function WizardApproval({ required, status, approver = 'Workflow engine' }: WizardApprovalProps) {
  return (
    <section className="rounded-xl border border-border-default bg-background-elevated p-4">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3">
          {required ? <GitPullRequestArrow className="mt-1 h-5 w-5 text-accent-primary" /> : <ShieldCheck className="mt-1 h-5 w-5 text-accent-success" />}
          <div>
            <h3 className="text-sm font-semibold text-text-primary">Approval Handoff</h3>
            <p className="mt-1 text-sm leading-6 text-text-secondary">
              {required
                ? `Submit sends the process to ${approver} before the record is created.`
                : 'This template completes directly after validation and submit.'}
            </p>
          </div>
        </div>
        <Badge tone={toneMap[status]}>{status}</Badge>
      </div>
    </section>
  );
}
