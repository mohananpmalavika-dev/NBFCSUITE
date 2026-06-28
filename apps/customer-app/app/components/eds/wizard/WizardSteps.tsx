import { CheckCircle2, Circle, CircleAlert } from 'lucide-react';
import { cn } from '../utils/cn';
import type { WizardStep, WizardStepStatus } from './types';

export interface WizardStepsProps {
  steps: WizardStep[];
  currentStepId: string;
  completedStepIds: string[];
  warningStepIds?: string[];
  onStepSelect: (stepId: string) => void;
}

function getStepStatus(
  stepId: string,
  currentStepId: string,
  completedStepIds: string[],
  warningStepIds: string[],
): WizardStepStatus {
  if (stepId === currentStepId) {
    return 'active';
  }

  if (warningStepIds.includes(stepId)) {
    return 'warning';
  }

  if (completedStepIds.includes(stepId)) {
    return 'complete';
  }

  return 'pending';
}

export function WizardSteps({
  steps,
  currentStepId,
  completedStepIds,
  warningStepIds = [],
  onStepSelect,
}: WizardStepsProps) {
  return (
    <ol className="grid gap-2 border-b border-border-default bg-background-elevated p-3 md:grid-cols-3 xl:grid-cols-6">
      {steps.map((step, index) => {
        const status = getStepStatus(step.id, currentStepId, completedStepIds, warningStepIds);
        const Icon = status === 'complete' ? CheckCircle2 : status === 'warning' ? CircleAlert : Circle;

        return (
          <li key={step.id}>
            <button
              type="button"
              onClick={() => onStepSelect(step.id)}
              className={cn(
                'flex min-h-20 w-full items-start gap-3 rounded-xl border p-3 text-left transition duration-normal ease-standard',
                status === 'active'
                  ? 'border-border-focus bg-background-surface shadow-sm'
                  : 'border-border-default bg-background-surface hover:border-border-focus',
              )}
            >
              <span
                className={cn(
                  'flex h-8 w-8 shrink-0 items-center justify-center rounded-full border text-xs font-semibold',
                  status === 'active' || status === 'complete'
                    ? 'border-accent-primary bg-background-accent text-accent-primary'
                    : 'border-border-default text-text-muted',
                )}
              >
                {status === 'complete' || status === 'warning' ? <Icon className="h-4 w-4" /> : index + 1}
              </span>
              <span className="min-w-0">
                <span className="block text-sm font-semibold text-text-primary">{step.label}</span>
                {step.description ? (
                  <span className="mt-1 block text-xs leading-5 text-text-secondary">{step.description}</span>
                ) : null}
              </span>
            </button>
          </li>
        );
      })}
    </ol>
  );
}
