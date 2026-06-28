import { LockKeyhole } from 'lucide-react';
import type { WorkflowAuditEntry } from './types';

export interface AuditTimelineProps {
  entries: WorkflowAuditEntry[];
}

export function AuditTimeline({ entries }: AuditTimelineProps) {
  return (
    <section className="rounded-xl border border-border-default bg-background-elevated p-4">
      <div className="flex items-center gap-2">
        <LockKeyhole className="h-4 w-4 text-accent-primary" />
        <h3 className="text-sm font-semibold text-text-primary">Immutable Audit Timeline</h3>
      </div>
      <div className="mt-4 space-y-3">
        {entries.map((entry) => (
          <article key={entry.id} className="rounded-xl border border-border-default bg-background-surface p-3">
            <div className="flex flex-wrap items-start justify-between gap-2">
              <div>
                <p className="text-sm font-semibold text-text-primary">{entry.event}</p>
                <p className="mt-1 text-sm text-text-secondary">{entry.description}</p>
              </div>
              <p className="text-xs font-semibold text-text-muted">{entry.time}</p>
            </div>
            <p className="mt-2 text-xs text-text-muted">{entry.actor}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
