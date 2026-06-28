import { CheckCircle2 } from 'lucide-react';
import { Badge } from '../foundation/Badge';
import type { WizardReviewGroup } from './types';

export interface WizardReviewProps {
  groups: WizardReviewGroup[];
}

const statusToneMap = {
  success: 'success',
  warning: 'warning',
  error: 'danger',
} as const;

export function WizardReview({ groups }: WizardReviewProps) {
  return (
    <section className="rounded-xl border border-border-default bg-background-elevated p-4">
      <div className="flex items-center gap-2">
        <CheckCircle2 className="h-4 w-4 text-accent-success" />
        <h3 className="text-sm font-semibold text-text-primary">Review Summary</h3>
      </div>
      <div className="mt-4 grid gap-4 lg:grid-cols-2">
        {groups.map((group) => (
          <div key={group.title} className="rounded-xl border border-border-default bg-background-surface p-4">
            <h4 className="text-sm font-semibold text-text-primary">{group.title}</h4>
            <dl className="mt-3 space-y-3">
              {group.items.map((item) => (
                <div key={item.label} className="flex items-start justify-between gap-4 text-sm">
                  <dt className="text-text-secondary">{item.label}</dt>
                  <dd className="text-right font-semibold text-text-primary">
                    {item.value}
                    {item.status ? <span className="ml-2"><Badge tone={statusToneMap[item.status]}>{item.status}</Badge></span> : null}
                  </dd>
                </div>
              ))}
            </dl>
          </div>
        ))}
      </div>
    </section>
  );
}
