/**
 * Clearance Checklist Component
 * Displays and manages exit clearance checklist
 */

import React, { useState } from 'react';
import { ExitClearance, ClearanceStatus } from '@/types/exit.types';
import ExitStatusBadge from './ExitStatusBadge';

interface ClearanceChecklistProps {
  clearances: ExitClearance[];
  onComplete?: (clearanceId: string, remarks: string) => void;
  readOnly?: boolean;
}

const ClearanceChecklist: React.FC<ClearanceChecklistProps> = ({
  clearances,
  onComplete,
  readOnly = false
}) => {
  const [selectedClearance, setSelectedClearance] = useState<string | null>(null);
  const [remarks, setRemarks] = useState('');

  const handleComplete = (clearanceId: string) => {
    if (onComplete && remarks.trim()) {
      onComplete(clearanceId, remarks);
      setSelectedClearance(null);
      setRemarks('');
    }
  };

  const getStatusIcon = (status: ClearanceStatus) => {
    switch (status) {
      case ClearanceStatus.COMPLETED:
        return (
          <svg className="w-6 h-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
      case ClearanceStatus.IN_PROGRESS:
        return (
          <svg className="w-6 h-6 text-blue-600 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        );
      case ClearanceStatus.PENDING:
        return (
          <svg className="w-6 h-6 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
      case ClearanceStatus.WAIVED:
        return (
          <svg className="w-6 h-6 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
          </svg>
        );
      default:
        return (
          <svg className="w-6 h-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
    }
  };

  const completedCount = clearances.filter(c => c.status === ClearanceStatus.COMPLETED).length;
  const totalCount = clearances.length;
  const progressPercentage = totalCount > 0 ? (completedCount / totalCount) * 100 : 0;

  return (
    <div className="space-y-4">
      {/* Progress Bar */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-medium text-gray-700">Clearance Progress</h3>
          <span className="text-sm text-gray-600">
            {completedCount} of {totalCount} completed
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-green-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${progressPercentage}%` }}
          />
        </div>
      </div>

      {/* Clearance List */}
      <div className="space-y-3">
        {clearances.map((clearance) => (
          <div
            key={clearance.id}
            className={`
              border rounded-lg p-4 transition-all
              ${clearance.is_overdue ? 'border-red-300 bg-red-50' : 'border-gray-200 bg-white'}
              ${selectedClearance === clearance.id ? 'ring-2 ring-blue-500' : ''}
            `}
          >
            <div className="flex items-start justify-between">
              <div className="flex items-start space-x-3 flex-1">
                {/* Status Icon */}
                <div className="flex-shrink-0 mt-0.5">
                  {getStatusIcon(clearance.status)}
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <h4 className="text-sm font-medium text-gray-900">
                      {clearance.clearance_from}
                      {clearance.is_mandatory && (
                        <span className="ml-2 text-red-600">*</span>
                      )}
                    </h4>
                    <ExitStatusBadge 
                      status={clearance.status} 
                      type="clearance" 
                      size="sm" 
                    />
                  </div>

                  <p className="text-sm text-gray-600 mt-1">
                    {clearance.clearance_type}
                  </p>

                  {clearance.description && (
                    <p className="text-xs text-gray-500 mt-1">
                      {clearance.description}
                    </p>
                  )}

                  {/* Checklist Items */}
                  {clearance.checklist_items && (
                    <div className="mt-2 space-y-1">
                      {JSON.parse(clearance.checklist_items).map((item: string, index: number) => (
                        <div key={index} className="flex items-start text-xs text-gray-600">
                          <span className="mr-2">•</span>
                          <span>{item}</span>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Due Date */}
                  {clearance.due_date && (
                    <div className="mt-2 flex items-center text-xs">
                      <svg className="w-4 h-4 mr-1 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                      <span className={clearance.is_overdue ? 'text-red-600 font-medium' : 'text-gray-600'}>
                        Due: {new Date(clearance.due_date).toLocaleDateString()}
                        {clearance.is_overdue && ' (Overdue)'}
                      </span>
                    </div>
                  )}

                  {/* Clearance Remarks */}
                  {clearance.status === ClearanceStatus.COMPLETED && clearance.clearance_remarks && (
                    <div className="mt-2 p-2 bg-green-50 rounded border border-green-200">
                      <p className="text-xs text-green-800">
                        <span className="font-medium">Remarks:</span> {clearance.clearance_remarks}
                      </p>
                      {clearance.cleared_date && (
                        <p className="text-xs text-green-600 mt-1">
                          Cleared on {new Date(clearance.cleared_date).toLocaleString()}
                        </p>
                      )}
                    </div>
                  )}
                </div>
              </div>

              {/* Actions */}
              {!readOnly && clearance.status !== ClearanceStatus.COMPLETED && clearance.status !== ClearanceStatus.WAIVED && (
                <button
                  onClick={() => setSelectedClearance(clearance.id)}
                  className="ml-4 px-3 py-1 text-xs font-medium text-blue-700 bg-blue-100 rounded hover:bg-blue-200"
                >
                  Complete
                </button>
              )}
            </div>

            {/* Complete Form */}
            {selectedClearance === clearance.id && (
              <div className="mt-4 pt-4 border-t border-gray-200">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Clearance Remarks <span className="text-red-600">*</span>
                </label>
                <textarea
                  value={remarks}
                  onChange={(e) => setRemarks(e.target.value)}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 text-sm"
                  placeholder="Enter clearance remarks and confirmation..."
                />
                <div className="mt-3 flex justify-end space-x-2">
                  <button
                    onClick={() => {
                      setSelectedClearance(null);
                      setRemarks('');
                    }}
                    className="px-3 py-1.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={() => handleComplete(clearance.id)}
                    disabled={!remarks.trim()}
                    className="px-3 py-1.5 text-sm font-medium text-white bg-green-600 rounded hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Mark as Cleared
                  </button>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {clearances.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          <svg className="w-12 h-12 mx-auto mb-3 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p className="text-sm">No clearances found</p>
        </div>
      )}
    </div>
  );
};

export default ClearanceChecklist;
