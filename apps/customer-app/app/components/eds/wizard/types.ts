import type { ReactNode } from 'react';

export type WizardStepStatus = 'pending' | 'active' | 'complete' | 'warning' | 'blocked';
export type WizardAutosaveStatus = 'idle' | 'saving' | 'saved' | 'error';
export type WizardValidationLevel = 'client' | 'business' | 'server';
export type WizardValidationStatus = 'success' | 'warning' | 'error';
export type WizardApprovalStatus = 'not-required' | 'draft' | 'pending' | 'approved';

export interface WizardStep {
  id: string;
  label: string;
  description?: string;
}

export interface WizardChecklistItem {
  id: string;
  label: string;
  complete: boolean;
  required?: boolean;
}

export interface WizardAttachment {
  id: string;
  label: string;
  status: 'missing' | 'uploaded' | 'review';
  required?: boolean;
  source?: 'upload' | 'camera' | 'scanner' | 'ocr';
}

export interface WizardValidationItem {
  id: string;
  level: WizardValidationLevel;
  status: WizardValidationStatus;
  message: string;
}

export interface WizardReviewGroup {
  title: string;
  items: Array<{
    label: string;
    value: ReactNode;
    status?: WizardValidationStatus;
  }>;
}

export interface WizardEvent {
  name:
    | 'WIZARD_OPENED'
    | 'DRAFT_SAVED'
    | 'STEP_CHANGED'
    | 'VALIDATION_RUN'
    | 'ATTACHMENT_REVIEWED'
    | 'SUBMITTED'
    | 'APPROVAL_REQUESTED'
    | 'CANCELLED';
  metadata?: Record<string, string | number | boolean>;
}

export interface WizardContract {
  id: string;
  module: string;
  type: 'linear' | 'branching' | 'nested' | 'review';
  supportsDrafts: boolean;
  supportsAutosave: boolean;
  supportsValidationLevels: WizardValidationLevel[];
  supportsAttachments: boolean;
  supportsApproval: boolean;
  supportsAiGuidance: boolean;
  performanceTarget: {
    nextStepMs: number;
    validationMs: number;
    draftResumeMs: number;
    submitMs: number;
  };
}
