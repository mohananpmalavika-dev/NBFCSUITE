import { Save } from 'lucide-react';
import { Button } from '../foundation/Button';
import type { WizardAutosaveStatus } from './types';

export interface WizardHeaderProps {
  title: string;
  description?: string;
  currentStep: number;
  totalSteps: number;
  autosaveStatus: WizardAutosaveStatus;
  lastSavedLabel?: string;
  onSaveDraft: () => void;
}

const autosaveLabelMap: Record<WizardAutosaveStatus, string> = {
  idle: 'Draft ready',
  saving: 'Saving draft',
  saved: 'Draft saved',
  error: 'Draft needs attention',
};

export function WizardHeader({
  title,
  description,
  currentStep,
  totalSteps,
  autosaveStatus,
  lastSavedLabel,
  onSaveDraft,
}: WizardHeaderProps) {
  const progress = Math.round((currentStep / totalSteps) * 100);

  return (
    <div className="border-b border-border-default bg-background-surface p-4 sm:p-5">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-accent-primary">EDS-009</p>
          <h2 className="mt-2 text-2xl font-semibold text-text-primary">{title}</h2>
          {description ? <p className="mt-2 max-w-3xl text-sm leading-6 text-text-secondary">{description}</p> : null}
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <span className="rounded-full border border-border-default bg-background-elevated px-3 py-2 text-sm font-semibold text-text-secondary">
            Step {currentStep} of {totalSteps}
          </span>
          <span className="rounded-full bg-background-accent px-3 py-2 text-sm font-semibold text-accent-primary">
            {progress}% complete
          </span>
          <Button size="sm" variant="secondary" icon={<Save className="h-4 w-4" />} onClick={onSaveDraft}>
            Save draft
          </Button>
        </div>
      </div>

      <div className="mt-4">
        <div className="h-2 overflow-hidden rounded-full bg-background-elevated">
          <div className="h-full rounded-full bg-accent-primary transition-all duration-normal ease-standard" style={{ width: `${progress}%` }} />
        </div>
        <p className="mt-2 text-xs font-semibold text-text-muted">
          {autosaveLabelMap[autosaveStatus]}{lastSavedLabel ? ` - ${lastSavedLabel}` : ''}
        </p>
      </div>
    </div>
  );
}
