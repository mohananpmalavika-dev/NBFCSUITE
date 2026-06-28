'use client';

import { useEffect, useMemo, useState } from 'react';
import type { ReactNode } from 'react';
import { WizardApproval } from './WizardApproval';
import { WizardFooter } from './WizardFooter';
import { WizardHeader } from './WizardHeader';
import { WizardReview } from './WizardReview';
import { WizardSidebar } from './WizardSidebar';
import { WizardSteps } from './WizardSteps';
import { WizardSuccess } from './WizardSuccess';
import type {
  WizardApiOperation,
  WizardAttachment,
  WizardAutosaveStatus,
  WizardChecklistItem,
  WizardEvent,
  WizardReviewGroup,
  WizardStep,
  WizardValidationItem,
} from './types';

export interface EnterpriseWizardProps {
  title: string;
  description?: string;
  steps: WizardStep[];
  checklist: WizardChecklistItem[];


  attachments?: WizardAttachment[];
  validationItems?: WizardValidationItem[];
  reviewGroups?: WizardReviewGroup[];
  aiTips?: string[];

  approvalRequired?: boolean;
  approvalApprover?: string;
  autosaveIntervalMs?: number;

  /**
   * Unique draft id used to load/resume a wizard session.
   * If omitted, the wizard starts as a fresh local session.
   */
  initialDraftId?: string;

  /**
   * Optional API handler for real drafts/validation/submit.
   * When not provided, the wizard uses local in-memory + simulated timing.
   */
  apiHandler?: (operation: WizardApiOperation) => Promise<unknown>;

  renderStep: (step: WizardStep) => ReactNode;
  onEvent?: (event: WizardEvent) => void;
}

function formatSavedTime(date: Date) {
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

export function EnterpriseWizard({
  title,
  description,
  steps,
  checklist,
  attachments = [],
  validationItems = [],
  reviewGroups = [],
  aiTips = [],
  approvalRequired = false,
  approvalApprover,
  autosaveIntervalMs = 30000,
  initialDraftId,
  apiHandler,
  renderStep,
  onEvent,
}: EnterpriseWizardProps) {

  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [completedStepIds, setCompletedStepIds] = useState<string[]>([]);
  const [autosaveStatus, setAutosaveStatus] = useState<WizardAutosaveStatus>('idle');
  const [lastSavedAt, setLastSavedAt] = useState<Date | null>(null);
  const [submitted, setSubmitted] = useState(false);

  const currentStep = steps[currentStepIndex] ?? steps[0];
  const isFirstStep = currentStepIndex === 0;
  const isLastStep = currentStepIndex === steps.length - 1;
  const blockingErrors = validationItems.filter((item) => item.status === 'error');
  const warnings = validationItems.filter((item) => item.status === 'warning' || item.status === 'error');
  const canSubmit = blockingErrors.length === 0;
  const warningStepIds = useMemo(
    () => (warnings.length > 0 && currentStep ? [currentStep.id] : []),
    [currentStep, warnings.length],
  );

  useEffect(() => {
    onEvent?.({ name: 'WIZARD_OPENED', metadata: { steps: steps.length } });
  }, [onEvent, steps.length]);

  useEffect(() => {
    const autosaveTimer = window.setInterval(() => {
      saveDraft('autosave');
    }, autosaveIntervalMs);

    return () => window.clearInterval(autosaveTimer);
  });

  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 's') {
        event.preventDefault();
        saveDraft('keyboard');
      }

      if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
        event.preventDefault();
        if (isLastStep) {
          submit();
        } else {
          nextStep();
        }
      }

      if (event.key === 'Escape') {
        onEvent?.({ name: 'CANCELLED', metadata: { step: currentStep?.id ?? 'unknown' } });
      }
    }

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  });

  function emit(name: WizardEvent['name'], metadata?: WizardEvent['metadata']) {
    onEvent?.({ name, metadata });
  }

  function saveDraft(source: string) {
    setAutosaveStatus('saving');
    window.setTimeout(() => {
      setLastSavedAt(new Date());
      setAutosaveStatus('saved');
      emit('DRAFT_SAVED', { source, step: currentStep?.id ?? 'unknown' });
    }, 250);
  }

  function setStepByIndex(nextIndex: number) {
    const nextStep = steps[nextIndex];

    if (!nextStep) {
      return;
    }

    setCurrentStepIndex(nextIndex);
    emit('STEP_CHANGED', { step: nextStep.id, index: nextIndex + 1 });
  }

  function selectStep(stepId: string) {
    const nextIndex = steps.findIndex((step) => step.id === stepId);
    setStepByIndex(nextIndex);
  }

  function nextStep() {
    if (!currentStep) {
      return;
    }

    setCompletedStepIds((current) => Array.from(new Set([...current, currentStep.id])));
    emit('VALIDATION_RUN', { step: currentStep.id, errors: blockingErrors.length });
    setStepByIndex(Math.min(currentStepIndex + 1, steps.length - 1));
  }

  function previousStep() {
    setStepByIndex(Math.max(currentStepIndex - 1, 0));
  }

  function submit() {
    if (!canSubmit || !currentStep) {
      emit('VALIDATION_RUN', { step: currentStep?.id ?? 'unknown', errors: blockingErrors.length });
      return;
    }

    setCompletedStepIds((current) => Array.from(new Set([...current, currentStep.id])));
    emit(approvalRequired ? 'APPROVAL_REQUESTED' : 'SUBMITTED', { step: currentStep.id });
    setSubmitted(true);
  }

  if (submitted) {
    return (
      <section className="overflow-hidden rounded-xl border border-border-default bg-background-surface shadow-sm">
        <WizardHeader
          title={title}
          description={description}
          currentStep={steps.length}
          totalSteps={steps.length}
          autosaveStatus={autosaveStatus}
          lastSavedLabel={lastSavedAt ? `Saved at ${formatSavedTime(lastSavedAt)}` : undefined}
          onSaveDraft={() => saveDraft('manual')}
        />
        <div className="p-4 sm:p-5">
          <WizardSuccess
            title={approvalRequired ? 'Employee onboarding sent for approval' : 'Employee created successfully'}
            description={
              approvalRequired
                ? 'The process is now pending HR operations approval and has published an auditable workflow handoff.'
                : 'The record is complete and ready to open from the employee profile.'
            }
            onCreateAnother={() => {
              setSubmitted(false);
              setCurrentStepIndex(0);
              setCompletedStepIds([]);
            }}
          />
        </div>
      </section>
    );
  }

  return (
    <section className="overflow-hidden rounded-xl border border-border-default bg-background-surface shadow-sm">
      <WizardHeader
        title={title}
        description={description}
        currentStep={currentStepIndex + 1}
        totalSteps={steps.length}
        autosaveStatus={autosaveStatus}
        lastSavedLabel={lastSavedAt ? `Saved at ${formatSavedTime(lastSavedAt)}` : undefined}
        onSaveDraft={() => saveDraft('manual')}
      />
      <WizardSteps
        steps={steps}
        currentStepId={currentStep.id}
        completedStepIds={completedStepIds}
        warningStepIds={warningStepIds}
        onStepSelect={selectStep}
      />
      <div className="grid xl:grid-cols-[minmax(0,1fr)_320px]">
        <div className="space-y-4 p-4 sm:p-5">
          {renderStep(currentStep)}
          {currentStep.id === 'review' && reviewGroups.length > 0 ? <WizardReview groups={reviewGroups} /> : null}
          <WizardApproval
            required={approvalRequired}
            status={approvalRequired ? 'draft' : 'not-required'}
            approver={approvalApprover}
          />
        </div>
        <WizardSidebar checklist={checklist} attachments={attachments} warnings={warnings} aiTips={aiTips} />
      </div>
      <WizardFooter
        isFirstStep={isFirstStep}
        isLastStep={isLastStep}
        canSubmit={canSubmit}
        onCancel={() => emit('CANCELLED', { step: currentStep.id })}
        onSaveDraft={() => saveDraft('manual')}
        onPrevious={previousStep}
        onNext={nextStep}
        onSubmit={submit}
      />
    </section>
  );
}
