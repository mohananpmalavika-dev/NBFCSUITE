import { AlertTriangle, CheckCircle2, FileCheck2, Sparkles } from 'lucide-react';
import { Badge } from '../foundation/Badge';
import type { WizardAttachment, WizardChecklistItem, WizardValidationItem } from './types';

export interface WizardSidebarProps {
  checklist: WizardChecklistItem[];
  attachments: WizardAttachment[];
  warnings: WizardValidationItem[];
  aiTips?: string[];
}

export function WizardSidebar({ checklist, attachments, warnings, aiTips = [] }: WizardSidebarProps) {
  const completedChecklist = checklist.filter((item) => item.complete).length;
  const uploadedAttachments = attachments.filter((attachment) => attachment.status === 'uploaded').length;

  return (
    <aside className="space-y-4 border-t border-border-default bg-background-surface p-4 xl:border-l xl:border-t-0">
      <div className="rounded-xl border border-border-default bg-background-elevated p-4">
        <div className="flex items-center justify-between gap-3">
          <p className="text-sm font-semibold text-text-primary">Completion</p>
          <Badge tone="accent">{completedChecklist}/{checklist.length}</Badge>
        </div>
        <div className="mt-4 space-y-3">
          {checklist.map((item) => (
            <div key={item.id} className="flex items-start gap-3 text-sm">
              <CheckCircle2 className={`mt-0.5 h-4 w-4 ${item.complete ? 'text-accent-success' : 'text-text-muted'}`} />
              <div>
                <p className="font-semibold text-text-primary">{item.label}</p>
                {item.required ? <p className="text-xs text-text-muted">Required</p> : null}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="rounded-xl border border-border-default bg-background-elevated p-4">
        <div className="flex items-center justify-between gap-3">
          <p className="text-sm font-semibold text-text-primary">Documents</p>
          <Badge tone="neutral">{uploadedAttachments}/{attachments.length}</Badge>
        </div>
        <div className="mt-4 space-y-3">
          {attachments.map((attachment) => (
            <div key={attachment.id} className="flex items-start gap-3 text-sm">
              <FileCheck2 className="mt-0.5 h-4 w-4 text-text-muted" />
              <div>
                <p className="font-semibold text-text-primary">{attachment.label}</p>
                <p className="text-xs capitalize text-text-muted">{attachment.status}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {warnings.length > 0 ? (
        <div className="rounded-xl border border-border-default bg-background-elevated p-4">
          <div className="flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 text-accent-warning" />
            <p className="text-sm font-semibold text-text-primary">Warnings</p>
          </div>
          <div className="mt-3 space-y-2">
            {warnings.map((warning) => (
              <p key={warning.id} className="text-sm leading-6 text-text-secondary">{warning.message}</p>
            ))}
          </div>
        </div>
      ) : null}

      {aiTips.length > 0 ? (
        <div className="rounded-xl border border-border-default bg-background-accent p-4">
          <div className="flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-accent-primary" />
            <p className="text-sm font-semibold text-text-primary">FinDNA Guidance</p>
          </div>
          <div className="mt-3 space-y-2">
            {aiTips.map((tip) => (
              <p key={tip} className="text-sm leading-6 text-text-secondary">{tip}</p>
            ))}
          </div>
        </div>
      ) : null}
    </aside>
  );
}
