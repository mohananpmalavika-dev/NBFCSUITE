import { ArrowLeft, ArrowRight, CheckCircle2, Save, X } from 'lucide-react';
import { Button } from '../foundation/Button';

export interface WizardFooterProps {
  isFirstStep: boolean;
  isLastStep: boolean;
  canSubmit: boolean;
  onCancel: () => void;
  onSaveDraft: () => void;
  onPrevious: () => void;
  onNext: () => void;
  onSubmit: () => void;
}

export function WizardFooter({
  isFirstStep,
  isLastStep,
  canSubmit,
  onCancel,
  onSaveDraft,
  onPrevious,
  onNext,
  onSubmit,
}: WizardFooterProps) {
  return (
    <div className="flex flex-col gap-3 border-t border-border-default bg-background-surface p-4 sm:flex-row sm:items-center sm:justify-between">
      <div className="flex flex-wrap gap-2">
        <Button size="sm" variant="ghost" icon={<X className="h-4 w-4" />} onClick={onCancel}>
          Cancel
        </Button>
        <Button size="sm" variant="secondary" icon={<Save className="h-4 w-4" />} onClick={onSaveDraft}>
          Save draft
        </Button>
      </div>
      <div className="flex flex-wrap gap-2">
        <Button size="sm" variant="secondary" icon={<ArrowLeft className="h-4 w-4" />} onClick={onPrevious} disabled={isFirstStep}>
          Previous
        </Button>
        {isLastStep ? (
          <Button size="sm" icon={<CheckCircle2 className="h-4 w-4" />} onClick={onSubmit} disabled={!canSubmit}>
            Submit
          </Button>
        ) : (
          <Button size="sm" icon={<ArrowRight className="h-4 w-4" />} onClick={onNext}>
            Next
          </Button>
        )}
      </div>
    </div>
  );
}
