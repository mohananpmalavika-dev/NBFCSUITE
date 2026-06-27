'use client';

import { useCIFStore } from '@/lib/cif-store';
import { cifApi } from '@/lib/cif-api';
import { useState } from 'react';

interface StageApprovalProps {
  onNext: () => void;
}

export default function StageApproval({ onNext }: StageApprovalProps) {
  const { customerId, setLoading, setError, markStageComplete } = useCIFStore();
  const [approvalStatus, setApprovalStatus] = useState<string | null>(null);
  const [approvalId, setApprovalId] = useState<string | null>(null);
  const [currentLevel, setCurrentLevel] = useState(0);

  const approvalLevels = [
    { level: 1, name: 'Checker', role: 'Validates completeness' },
    { level: 2, name: 'Manager', role: 'Business approval' },
    { level: 3, name: 'Compliance', role: 'Compliance sign-off' },
    { level: 4, name: 'Final Approver', role: 'Executive approval' },
  ];

  const handleInitiateApproval = async () => {
    if (!customerId) {
      setError('No customer selected');
      return;
    }

    setLoading(true);
    try {
      const response = await cifApi.initiateApproval(customerId, {
        initiated_by: 'system',
        notes: 'CIF onboarding initiated',
      });

      setApprovalId(response.approval_id);
      setApprovalStatus('checker_pending');
      setCurrentLevel(0);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleApproveLevel = async (level: number) => {
    if (!customerId || !approvalId) {
      setError('Missing approval details');
      return;
    }

    setLoading(true);
    try {
      const data = {
        approval_id: approvalId,
        approved: true,
        notes: `${approvalLevels[level - 1].name} approval granted`,
        approved_by: 'system',
      };

      if (level === 1) {
        await cifApi.checkerApproval(customerId, data);
      } else if (level === 2) {
        await cifApi.managerApproval(customerId, data);
      } else if (level === 3) {
        await cifApi.complianceApproval(customerId, data);
      } else if (level === 4) {
        await cifApi.finalApproval(customerId, data);
      }

      setCurrentLevel(level);

      if (level === 4) {
        // All levels approved
        markStageComplete(16);
        setTimeout(() => onNext(), 1500);
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (!approvalStatus) {
    return (
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 mb-2">Stage 16: Approval Workflow</h2>
          <p className="text-slate-600">
            Customer information goes through a 4-level approval process for quality assurance.
          </p>
        </div>

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 space-y-4">
          <h3 className="font-bold text-blue-900">⚙️ Approval Levels</h3>
          <div className="space-y-3">
            {approvalLevels.map((level) => (
              <div key={level.level} className="flex items-start gap-3">
                <div className="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">
                  {level.level}
                </div>
                <div>
                  <p className="font-semibold text-blue-900">{level.name}</p>
                  <p className="text-sm text-blue-800">{level.role}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <button
          onClick={handleInitiateApproval}
          className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold"
        >
          ⚙️ Initiate Approval Process
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 mb-2">Stage 16: Multi-Level Approval</h2>
        <p className="text-slate-600">Approval workflow in progress...</p>
      </div>

      <div className="space-y-4">
        {approvalLevels.map((level) => (
          <div
            key={level.level}
            className={`border-2 rounded-lg p-4 transition-all ${
              currentLevel >= level.level
                ? 'bg-green-50 border-green-500'
                : currentLevel === level.level - 1
                ? 'bg-blue-50 border-blue-500'
                : 'bg-slate-50 border-slate-300'
            }`}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center font-bold ${
                    currentLevel >= level.level
                      ? 'bg-green-600 text-white'
                      : currentLevel === level.level - 1
                      ? 'bg-blue-600 text-white'
                      : 'bg-slate-300 text-slate-600'
                  }`}
                >
                  {currentLevel >= level.level ? '✓' : level.level}
                </div>
                <div>
                  <p className="font-semibold text-slate-900">{level.name}</p>
                  <p className="text-sm text-slate-600">{level.role}</p>
                </div>
              </div>
              {currentLevel === level.level - 1 && (
                <button
                  onClick={() => handleApproveLevel(level.level)}
                  className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 font-semibold text-sm"
                >
                  Approve
                </button>
              )}
              {currentLevel >= level.level && (
                <span className="text-green-600 font-semibold">✓ Approved</span>
              )}
            </div>
          </div>
        ))}
      </div>

      {currentLevel === 4 && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-center">
          <div className="text-4xl mb-2">🎉</div>
          <h3 className="font-bold text-green-900 mb-2">All Approvals Granted!</h3>
          <p className="text-green-800 text-sm">
            Customer has been approved and CIF ID will be generated on the next stage.
          </p>
        </div>
      )}
    </div>
  );
}
