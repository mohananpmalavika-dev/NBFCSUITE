/**
 * Resignation Workflow Stepper Component
 * Visual stepper showing the resignation process workflow
 */

import React from 'react';
import { ResignationStatus } from '@/types/exit.types';

interface WorkflowStep {
  id: string;
  label: string;
  description: string;
  status: ResignationStatus[];
}

interface ResignationWorkflowStepperProps {
  currentStatus: ResignationStatus;
  className?: string;
}

const ResignationWorkflowStepper: React.FC<ResignationWorkflowStepperProps> = ({
  currentStatus,
  className = ''
}) => {
  const steps: WorkflowStep[] = [
    {
      id: 'submitted',
      label: 'Submitted',
      description: 'Resignation submitted',
      status: [ResignationStatus.SUBMITTED]
    },
    {
      id: 'review',
      label: 'Under Review',
      description: 'Manager and HR review',
      status: [ResignationStatus.UNDER_REVIEW]
    },
    {
      id: 'approved',
      label: 'Approved',
      description: 'Resignation approved',
      status: [ResignationStatus.APPROVED]
    },
    {
      id: 'completed',
      label: 'Completed',
      description: 'Exit process completed',
      status: [ResignationStatus.COMPLETED]
    }
  ];

  const getCurrentStepIndex = () => {
    return steps.findIndex(step => step.status.includes(currentStatus));
  };

  const currentStepIndex = getCurrentStepIndex();
  const isRejected = currentStatus === ResignationStatus.REJECTED;
  const isWithdrawn = currentStatus === ResignationStatus.WITHDRAWN;
  const isCancelled = currentStatus === ResignationStatus.CANCELLED;

  if (isRejected || isWithdrawn || isCancelled) {
    return (
      <div className={`bg-red-50 border border-red-200 rounded-lg p-4 ${className}`}>
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <svg className="w-6 h-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">
              {isRejected && 'Resignation Rejected'}
              {isWithdrawn && 'Resignation Withdrawn'}
              {isCancelled && 'Resignation Cancelled'}
            </h3>
            <p className="text-sm text-red-700 mt-1">
              {isRejected && 'The resignation request was not approved.'}
              {isWithdrawn && 'The resignation was withdrawn by the employee.'}
              {isCancelled && 'The resignation process was cancelled.'}
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={className}>
      <div className="flex items-center justify-between">
        {steps.map((step, index) => {
          const isCompleted = index < currentStepIndex;
          const isCurrent = index === currentStepIndex;
          const isPending = index > currentStepIndex;

          return (
            <React.Fragment key={step.id}>
              {/* Step */}
              <div className="flex flex-col items-center flex-1">
                {/* Circle */}
                <div className="relative flex items-center justify-center">
                  <div
                    className={`
                      w-10 h-10 rounded-full flex items-center justify-center text-sm font-semibold
                      ${isCompleted ? 'bg-green-600 text-white' : ''}
                      ${isCurrent ? 'bg-blue-600 text-white ring-4 ring-blue-100' : ''}
                      ${isPending ? 'bg-gray-200 text-gray-500' : ''}
                    `}
                  >
                    {isCompleted ? (
                      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    ) : (
                      <span>{index + 1}</span>
                    )}
                  </div>
                </div>

                {/* Label */}
                <div className="mt-2 text-center">
                  <p
                    className={`
                      text-sm font-medium
                      ${isCompleted || isCurrent ? 'text-gray-900' : 'text-gray-500'}
                    `}
                  >
                    {step.label}
                  </p>
                  <p className="text-xs text-gray-500 mt-0.5">{step.description}</p>
                </div>
              </div>

              {/* Connector line */}
              {index < steps.length - 1 && (
                <div
                  className={`
                    flex-1 h-0.5 mx-2 -mt-12
                    ${isCompleted ? 'bg-green-600' : 'bg-gray-200'}
                  `}
                />
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
};

export default ResignationWorkflowStepper;
