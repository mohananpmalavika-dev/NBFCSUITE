/**
 * Goal Progress Tracker Component
 * Visual progress tracker for performance goals
 */

import React from 'react';
import { PerformanceGoal, GoalStatus } from '../../types/performance.types';

interface GoalProgressTrackerProps {
  goal: PerformanceGoal;
  onUpdateProgress?: (goalId: string, progress: number) => void;
  editable?: boolean;
  showDetails?: boolean;
}

const GoalProgressTracker: React.FC<GoalProgressTrackerProps> = ({
  goal,
  onUpdateProgress,
  editable = false,
  showDetails = true
}) => {
  const getProgressColor = (progress: number): string => {
    if (progress >= 90) return 'bg-green-500';
    if (progress >= 70) return 'bg-blue-500';
    if (progress >= 50) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const getStatusBadge = (status: GoalStatus): JSX.Element => {
    const statusConfig: Record<GoalStatus, { color: string; label: string }> = {
      [GoalStatus.DRAFT]: { color: 'bg-gray-500', label: 'Draft' },
      [GoalStatus.SUBMITTED]: { color: 'bg-yellow-500', label: 'Submitted' },
      [GoalStatus.APPROVED]: { color: 'bg-green-500', label: 'Approved' },
      [GoalStatus.REJECTED]: { color: 'bg-red-500', label: 'Rejected' },
      [GoalStatus.IN_PROGRESS]: { color: 'bg-blue-500', label: 'In Progress' },
      [GoalStatus.COMPLETED]: { color: 'bg-green-700', label: 'Completed' },
      [GoalStatus.CANCELLED]: { color: 'bg-gray-400', label: 'Cancelled' }
    };

    const config = statusConfig[status];
    return (
      <span className={`px-2 py-1 text-xs font-semibold text-white rounded ${config.color}`}>
        {config.label}
      </span>
    );
  };

  return (
    <div className="goal-progress-tracker border rounded-lg p-4 bg-white shadow-sm">
      <div className="flex justify-between items-start mb-3">
        <div className="flex-1">
          <h4 className="text-sm font-semibold text-gray-900">{goal.goal_title}</h4>
          <p className="text-xs text-gray-500 mt-1">{goal.goal_code}</p>
        </div>
        {getStatusBadge(goal.status)}
      </div>

      {showDetails && (
        <div className="grid grid-cols-2 gap-2 mb-3 text-xs">
          <div>
            <span className="text-gray-500">Target:</span>
            <span className="ml-1 font-medium">{goal.target_value} {goal.uom}</span>
          </div>
          <div>
            <span className="text-gray-500">Achieved:</span>
            <span className="ml-1 font-medium">{goal.achieved_value || 'N/A'} {goal.uom}</span>
          </div>
          <div>
            <span className="text-gray-500">Weightage:</span>
            <span className="ml-1 font-medium">{goal.weightage}%</span>
          </div>
          <div>
            <span className="text-gray-500">Due:</span>
            <span className="ml-1 font-medium">{new Date(goal.target_date).toLocaleDateString()}</span>
          </div>
        </div>
      )}

      <div className="relative">
        <div className="flex justify-between text-xs text-gray-600 mb-1">
          <span>Progress</span>
          <span className="font-semibold">{goal.progress_percentage}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-300 ${getProgressColor(goal.progress_percentage)}`}
            style={{ width: `${goal.progress_percentage}%` }}
          />
        </div>
      </div>

      {editable && onUpdateProgress && (
        <div className="mt-3">
          <input
            type="range"
            min="0"
            max="100"
            value={goal.progress_percentage}
            onChange={(e) => onUpdateProgress(goal.id, parseInt(e.target.value))}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
          />
        </div>
      )}
    </div>
  );
};

export default GoalProgressTracker;
