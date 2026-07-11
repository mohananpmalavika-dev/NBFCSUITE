/**
 * Performance Management Routes
 * Main routing configuration for Performance Management module
 */

import React from 'react';
import { Routes, Route } from 'react-router-dom';

// Lazy load components for better performance
const AppraisalCycleList = React.lazy(() => import('./cycles/AppraisalCycleList'));
const AppraisalCycleForm = React.lazy(() => import('./cycles/AppraisalCycleForm'));
const AppraisalCycleDetail = React.lazy(() => import('./cycles/AppraisalCycleDetail'));

const GoalsList = React.lazy(() => import('./goals/GoalsList'));
const GoalsForm = React.lazy(() => import('./goals/GoalsForm'));
const GoalsApproval = React.lazy(() => import('./goals/GoalsApproval'));

const AppraisalsList = React.lazy(() => import('./appraisals/AppraisalsList'));
const AppraisalDetail = React.lazy(() => import('./appraisals/AppraisalDetail'));
const SelfAssessmentForm = React.lazy(() => import('./appraisals/SelfAssessmentForm'));
const ManagerReviewForm = React.lazy(() => import('./appraisals/ManagerReviewForm'));
const HRReviewForm = React.lazy(() => import('./appraisals/HRReviewForm'));

const FeedbackRequestList = React.lazy(() => import('./feedback/FeedbackRequestList'));
const FeedbackResponseForm = React.lazy(() => import('./feedback/FeedbackResponseForm'));
const FeedbackSummary = React.lazy(() => import('./feedback/FeedbackSummary'));

const IncrementsList = React.lazy(() => import('./increments/IncrementsList'));
const IncrementForm = React.lazy(() => import('./increments/IncrementForm'));
const IncrementApproval = React.lazy(() => import('./increments/IncrementApproval'));

const IDPList = React.lazy(() => import('./idp/IDPList'));
const IDPForm = React.lazy(() => import('./idp/IDPForm'));
const IDPDetail = React.lazy(() => import('./idp/IDPDetail'));
const ActivityForm = React.lazy(() => import('./idp/ActivityForm'));

const PerformanceDashboard = React.lazy(() => import('./dashboard/PerformanceDashboard'));

const PerformanceManagementRoutes: React.FC = () => {
  return (
    <Routes>
      {/* Dashboard */}
      <Route path="/" element={<PerformanceDashboard />} />
      
      {/* Appraisal Cycles */}
      <Route path="/cycles" element={<AppraisalCycleList />} />
      <Route path="/cycles/new" element={<AppraisalCycleForm />} />
      <Route path="/cycles/:id" element={<AppraisalCycleDetail />} />
      <Route path="/cycles/:id/edit" element={<AppraisalCycleForm />} />
      
      {/* Performance Goals (KRA/KPI) */}
      <Route path="/goals" element={<GoalsList />} />
      <Route path="/goals/new" element={<GoalsForm />} />
      <Route path="/goals/:id/edit" element={<GoalsForm />} />
      <Route path="/goals/approval" element={<GoalsApproval />} />
      
      {/* Employee Appraisals */}
      <Route path="/appraisals" element={<AppraisalsList />} />
      <Route path="/appraisals/:id" element={<AppraisalDetail />} />
      <Route path="/appraisals/:id/self-assessment" element={<SelfAssessmentForm />} />
      <Route path="/appraisals/:id/manager-review" element={<ManagerReviewForm />} />
      <Route path="/appraisals/:id/hr-review" element={<HRReviewForm />} />
      
      {/* 360 Feedback */}
      <Route path="/feedback" element={<FeedbackRequestList />} />
      <Route path="/feedback/:id/respond" element={<FeedbackResponseForm />} />
      <Route path="/feedback/summary/:employeeId" element={<FeedbackSummary />} />
      
      {/* Performance Increments */}
      <Route path="/increments" element={<IncrementsList />} />
      <Route path="/increments/new" element={<IncrementForm />} />
      <Route path="/increments/approval" element={<IncrementApproval />} />
      
      {/* Individual Development Plans (IDP) */}
      <Route path="/idp" element={<IDPList />} />
      <Route path="/idp/new" element={<IDPForm />} />
      <Route path="/idp/:id" element={<IDPDetail />} />
      <Route path="/idp/:id/edit" element={<IDPForm />} />
      <Route path="/idp/:idpId/activities/new" element={<ActivityForm />} />
      <Route path="/idp/:idpId/activities/:id/edit" element={<ActivityForm />} />
    </Routes>
  );
};

export default PerformanceManagementRoutes;
