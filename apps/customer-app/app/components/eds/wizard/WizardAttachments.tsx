import { Camera, FileUp, ScanLine } from 'lucide-react';
import { Badge } from '../foundation/Badge';
import { Button } from '../foundation/Button';
import type { WizardAttachment } from './types';

export interface WizardAttachmentsProps {
  attachments: WizardAttachment[];
  onReviewAttachment?: (attachmentId: string) => void;
}

const statusToneMap = {
  missing: 'warning',
  uploaded: 'success',
  review: 'accent',
} as const;

export function WizardAttachments({ attachments, onReviewAttachment }: WizardAttachmentsProps) {
  return (
    <section className="rounded-xl border border-border-default bg-background-elevated p-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h3 className="text-sm font-semibold text-text-primary">Document Checklist</h3>
          <p className="mt-1 text-sm text-text-secondary">Upload, camera capture, scanner, and OCR states share one checklist model.</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button size="sm" variant="secondary" icon={<FileUp className="h-4 w-4" />}>Upload</Button>
          <Button size="sm" variant="secondary" icon={<Camera className="h-4 w-4" />}>Camera</Button>
          <Button size="sm" variant="secondary" icon={<ScanLine className="h-4 w-4" />}>OCR</Button>
        </div>
      </div>

      <div className="mt-4 grid gap-3 md:grid-cols-2">
        {attachments.map((attachment) => (
          <button
            key={attachment.id}
            type="button"
            onClick={() => onReviewAttachment?.(attachment.id)}
            className="rounded-xl border border-border-default bg-background-surface p-3 text-left transition duration-normal ease-standard hover:border-border-focus"
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="text-sm font-semibold text-text-primary">{attachment.label}</p>
                <p className="mt-1 text-xs capitalize text-text-muted">{attachment.source ?? 'upload'} source</p>
              </div>
              <Badge tone={statusToneMap[attachment.status]}>{attachment.status}</Badge>
            </div>
          </button>
        ))}
      </div>
    </section>
  );
}
