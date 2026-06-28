import { AlertCircle, CheckCircle2, ShieldCheck } from 'lucide-react';
import { Badge } from '../foundation/Badge';
import type { WizardValidationItem } from './types';

export interface WizardValidationProps {
  items: WizardValidationItem[];
}

const levelLabelMap = {
  client: 'Client',
  business: 'Business',
  server: 'Server',
};

const toneMap = {
  success: 'success',
  warning: 'warning',
  error: 'danger',
} as const;

export function WizardValidation({ items }: WizardValidationProps) {
  return (
    <section className="rounded-xl border border-border-default bg-background-elevated p-4">
      <div className="flex items-center gap-2">
        <ShieldCheck className="h-4 w-4 text-accent-primary" />
        <h3 className="text-sm font-semibold text-text-primary">Validation</h3>
      </div>
      <div className="mt-4 grid gap-3 md:grid-cols-3">
        {items.map((item) => {
          const Icon = item.status === 'error' ? AlertCircle : CheckCircle2;

          return (
            <div key={item.id} className="rounded-xl border border-border-default bg-background-surface p-3">
              <div className="flex items-center justify-between gap-2">
                <Badge tone={toneMap[item.status]}>{levelLabelMap[item.level]}</Badge>
                <Icon className="h-4 w-4 text-text-muted" />
              </div>
              <p className="mt-3 text-sm leading-6 text-text-secondary">{item.message}</p>
            </div>
          );
        })}
      </div>
    </section>
  );
}
