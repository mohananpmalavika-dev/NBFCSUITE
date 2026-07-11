/**
 * Performance Management Dashboard
 * Main landing page for performance management
 */

import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import performanceManagementService from '../../../services/performance.service';
import { AppraisalCycle, EmployeeAppraisal, FeedbackRequest } from '../../../types/performance.types';
import StatusBadge from '../../../components/performance/StatusBadge';

const PerformanceDashboard: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [currentCycle, setCurrentCycle] = useState<AppraisalCycle | null>(null);
  const [pendingAppraisals, setPendingAppraisals] = useState<EmployeeAppraisal[]>([]);
  const [pendingFeedback, setPendingFeedback] = useState<FeedbackRequest[]>([]);
  const [stats, setStats] = useState({
    totalEmployees: 0,
    completedAppraisals: 0,
    pendingGoals: 0,
    pendingFeedback: 0
  });

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);

      // Load current active cycle
      const cyclesResponse = await performanceManagementService.cycles.list({ status: 'active', limit: 1 });
      if (cyclesResponse.items.length > 0) {
        setCurrentCycle(cyclesResponse.items[0] as AppraisalCycle);
      }

      // Load pending appraisals (mock - replace with actual user ID)
      // const appraisalsResponse = await performanceManagementService.appraisals.list({
      //   status: 'self_assessment_pending',
      //   limit: 5
      // });
      // setPendingAppraisals(appraisalsResponse.items as EmployeeAppraisal[]);

      // Load pending feedback requests
      // const userId = 'current-user-id'; // Get from auth context
      // const feedbackResponse = await performanceManagementService.feedback.listRequestsForReviewer(userId, {
      //   status: 'pending'
      // });
      // setPendingFeedback(feedbackResponse);

      setLoading(false);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
      setLoading(false);
    }
  };

  const QuickStatCard: React.FC<{ title: string; value: number; color: string; icon: string }> = ({
    title,
    value,
    color,
    icon
  }) => (
    <div className={`bg-white rounded-lg shadow p-6 border-l-4 ${color}`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-600 font-medium">{title}</p>
          <p className="text-3xl font-bold mt-2">{value}</p>
        </div>
        <div className="text-4xl">{icon}</div>
      </div>
    </div>
  );

  const NavigationCard: React.FC<{ title: string; description: string; link: string; icon: string }> = ({
    title,
    description,
    link,
    icon
  }) => (
    <Link to={link} className="block">
      <div className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow border border-gray-200">
        <div className="flex items-start">
          <div className="text-3xl mr-4">{icon}</div>
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
            <p className="text-sm text-gray-600 mt-1">{description}</p>
          </div>
          <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </div>
      </div>
    </Link>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="performance-dashboard">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Performance Management</h1>
        <p className="mt-2 text-gray-600">
          Manage goals, appraisals, feedback, and employee development
        </p>
      </div>

      {/* Current Cycle Info */}
      {currentCycle && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-8">
          <div className="flex items-start justify-between">
            <div>
              <h2 className="text-xl font-semibold text-blue-900">{currentCycle.cycle_name}</h2>
              <p className="text-sm text-blue-700 mt-1">
                {new Date(currentCycle.start_date).toLocaleDateString()} - {new Date(currentCycle.end_date).toLocaleDateString()}
              </p>
              <div className="mt-3">
                <StatusBadge status={currentCycle.status} variant="info" />
              </div>
            </div>
            <div className="text-right">
              <p className="text-sm text-blue-700">Progress</p>
              <p className="text-2xl font-bold text-blue-900">
                {currentCycle.completed_appraisals} / {currentCycle.total_employees}
              </p>
              <p className="text-xs text-blue-600 mt-1">
                {Math.round((currentCycle.completed_appraisals / currentCycle.total_employees) * 100)}% Complete
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <QuickStatCard
          title="Total Employees"
          value={currentCycle?.total_employees || 0}
          color="border-blue-500"
          icon="👥"
        />
        <QuickStatCard
          title="Completed Appraisals"
          value={currentCycle?.completed_appraisals || 0}
          color="border-green-500"
          icon="✅"
        />
        <QuickStatCard
          title="Pending Goals"
          value={stats.pendingGoals}
          color="border-yellow-500"
          icon="🎯"
        />
        <QuickStatCard
          title="Pending Feedback"
          value={stats.pendingFeedback}
          color="border-purple-500"
          icon="💬"
        />
      </div>

      {/* Pending Actions */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Pending Actions</h2>
        <div className="bg-white rounded-lg shadow overflow-hidden">
          {pendingAppraisals.length === 0 && pendingFeedback.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              <p className="text-lg">✨ All caught up!</p>
              <p className="text-sm mt-2">You have no pending actions at the moment.</p>
            </div>
          ) : (
            <div className="divide-y">
              {/* Pending items would be listed here */}
            </div>
          )}
        </div>
      </div>

      {/* Quick Navigation */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Access</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <NavigationCard
            title="Appraisal Cycles"
            description="Manage appraisal cycles and timelines"
            link="/performance/cycles"
            icon="📅"
          />
          <NavigationCard
            title="My Goals"
            description="Set and track performance goals"
            link="/performance/goals"
            icon="🎯"
          />
          <NavigationCard
            title="My Appraisals"
            description="View and complete appraisals"
            link="/performance/appraisals"
            icon="📊"
          />
          <NavigationCard
            title="Feedback Requests"
            description="Provide 360-degree feedback"
            link="/performance/feedback"
            icon="💬"
          />
          <NavigationCard
            title="Increments"
            description="View performance increments"
            link="/performance/increments"
            icon="💰"
          />
          <NavigationCard
            title="Development Plan"
            description="Manage career development"
            link="/performance/idp"
            icon="📚"
          />
        </div>
      </div>

      {/* Upcoming Deadlines */}
      {currentCycle && (
        <div>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Upcoming Deadlines</h2>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="space-y-4">
              {currentCycle.goal_setting_end && new Date(currentCycle.goal_setting_end) > new Date() && (
                <div className="flex items-center justify-between border-b pb-4">
                  <div>
                    <p className="font-medium">Goal Setting Deadline</p>
                    <p className="text-sm text-gray-600">Submit your goals for approval</p>
                  </div>
                  <p className="text-sm font-semibold text-orange-600">
                    {new Date(currentCycle.goal_setting_end).toLocaleDateString()}
                  </p>
                </div>
              )}
              {currentCycle.self_assessment_end && new Date(currentCycle.self_assessment_end) > new Date() && (
                <div className="flex items-center justify-between border-b pb-4">
                  <div>
                    <p className="font-medium">Self-Assessment Deadline</p>
                    <p className="text-sm text-gray-600">Complete your self-assessment</p>
                  </div>
                  <p className="text-sm font-semibold text-orange-600">
                    {new Date(currentCycle.self_assessment_end).toLocaleDateString()}
                  </p>
                </div>
              )}
              {currentCycle.manager_review_end && new Date(currentCycle.manager_review_end) > new Date() && (
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Manager Review Deadline</p>
                    <p className="text-sm text-gray-600">Complete team reviews</p>
                  </div>
                  <p className="text-sm font-semibold text-orange-600">
                    {new Date(currentCycle.manager_review_end).toLocaleDateString()}
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PerformanceDashboard;
