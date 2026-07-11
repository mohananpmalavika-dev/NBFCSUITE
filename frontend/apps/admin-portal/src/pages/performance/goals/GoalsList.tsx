/**
 * Goals List Component
 * Display and manage performance goals
 */

import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import performanceManagementService from '../../../services/performance.service';
import { PerformanceGoal, GoalStatus } from '../../../types/performance.types';
import GoalProgressTracker from '../../../components/performance/GoalProgressTracker';

const GoalsList: React.FC = () => {
  const navigate = useNavigate();
  const [goals, setGoals] = useState<PerformanceGoal[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState<GoalStatus | ''>('');
  const [viewMode, setViewMode] = useState<'card' | 'table'>('card');

  useEffect(() => {
    loadGoals();
  }, [filterStatus]);

  const loadGoals = async () => {
    try {
      setLoading(true);
      // In real app, get employee ID from auth context
      const employeeId = 'current-employee-id'; // Replace with actual
      
      const goalsData = await performanceManagementService.goals.listByEmployee(employeeId, {
        status: filterStatus || undefined
      });
      setGoals(goalsData);
    } catch (error) {
      console.error('Error loading goals:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateProgress = async (goalId: string, progress: number) => {
    try {
      await performanceManagementService.goals.update(goalId, {
        progress_percentage: progress
      });
      loadGoals();
    } catch (error) {
      console.error('Error updating progress:', error);
    }
  };

  const handleSubmitGoals = async () => {
    if (window.confirm('Submit all draft goals for manager approval?')) {
      try {
        const employeeId = 'current-employee-id';
        const cycleId = 'current-cycle-id'; // Get from context
        await performanceManagementService.goals.submit(employeeId, cycleId);
        alert('Goals submitted successfully!');
        loadGoals();
      } catch (error) {
        console.error('Error submitting goals:', error);
        alert('Failed to submit goals');
      }
    }
  };

  const calculateTotalWeightage = () => {
    return goals.reduce((sum, goal) => sum + (goal.weightage || 0), 0);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const totalWeightage = calculateTotalWeightage();

  return (
    <div className="goals-list">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">My Goals</h1>
          <p className="text-gray-600 mt-1">Set and track your performance goals</p>
        </div>
        <div className="flex gap-2">
          <Link
            to="/performance/goals/new"
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            + Add Goal
          </Link>
          {goals.filter(g => g.status === GoalStatus.DRAFT).length > 0 && (
            <button
              onClick={handleSubmitGoals}
              className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
            >
              Submit for Approval
            </button>
          )}
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-sm text-gray-600">Total Goals</p>
          <p className="text-2xl font-bold mt-1">{goals.length}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-sm text-gray-600">Total Weightage</p>
          <p className={`text-2xl font-bold mt-1 ${totalWeightage === 100 ? 'text-green-600' : 'text-orange-600'}`}>
            {totalWeightage}%
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-sm text-gray-600">Approved Goals</p>
          <p className="text-2xl font-bold mt-1 text-green-600">
            {goals.filter(g => g.status === GoalStatus.APPROVED).length}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-sm text-gray-600">Avg. Progress</p>
          <p className="text-2xl font-bold mt-1 text-blue-600">
            {Math.round(goals.reduce((sum, g) => sum + g.progress_percentage, 0) / (goals.length || 1))}%
          </p>
        </div>
      </div>

      {/* Filters & View Toggle */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="flex justify-between items-center">
          <div className="flex gap-4">
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value as GoalStatus | '')}
              className="px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">All Statuses</option>
              <option value={GoalStatus.DRAFT}>Draft</option>
              <option value={GoalStatus.SUBMITTED}>Submitted</option>
              <option value={GoalStatus.APPROVED}>Approved</option>
              <option value={GoalStatus.IN_PROGRESS}>In Progress</option>
              <option value={GoalStatus.COMPLETED}>Completed</option>
            </select>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setViewMode('card')}
              className={`px-3 py-2 rounded ${viewMode === 'card' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
            >
              Card View
            </button>
            <button
              onClick={() => setViewMode('table')}
              className={`px-3 py-2 rounded ${viewMode === 'table' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
            >
              Table View
            </button>
          </div>
        </div>
      </div>

      {/* Goals Display */}
      {goals.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <p className="text-lg text-gray-500">No goals found</p>
          <p className="text-sm text-gray-400 mt-2">Create your first goal to get started</p>
        </div>
      ) : viewMode === 'card' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {goals.map((goal) => (
            <GoalProgressTracker
              key={goal.id}
              goal={goal}
              onUpdateProgress={handleUpdateProgress}
              editable={goal.status === GoalStatus.APPROVED || goal.status === GoalStatus.IN_PROGRESS}
              showDetails={true}
            />
          ))}
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Goal</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Target</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Progress</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {goals.map((goal) => (
                <tr key={goal.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div className="text-sm font-medium text-gray-900">{goal.goal_title}</div>
                    <div className="text-sm text-gray-500">{goal.goal_code}</div>
                  </td>
                  <td className="px-6 py-4 text-sm">{goal.goal_type}</td>
                  <td className="px-6 py-4 text-sm">
                    {goal.target_value} {goal.uom} ({goal.weightage}%)
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center">
                      <div className="w-full bg-gray-200 rounded-full h-2 mr-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full"
                          style={{ width: `${goal.progress_percentage}%` }}
                        />
                      </div>
                      <span className="text-sm">{goal.progress_percentage}%</span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className="px-2 py-1 text-xs font-semibold rounded bg-blue-100 text-blue-800">
                      {goal.status.replace(/_/g, ' ')}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right text-sm">
                    <button
                      onClick={() => navigate(`/performance/goals/${goal.id}/edit`)}
                      className="text-blue-600 hover:text-blue-900"
                    >
                      Edit
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Weightage Warning */}
      {totalWeightage !== 100 && goals.length > 0 && (
        <div className="mt-4 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-sm text-yellow-800">
            ⚠️ Total weightage is {totalWeightage}%. It should equal 100% before submission.
          </p>
        </div>
      )}
    </div>
  );
};

export default GoalsList;
