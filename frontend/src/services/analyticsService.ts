/**
 * Workflow Analytics Service
 * 
 * API integration for monitoring and analytics
 */

import api from './api';

export interface RealtimeDashboard {
  timestamp: string;
  total_active_workflows: number;
  total_pending_approvals: number;
  total_sla_breaches: number;
  total_bottlenecks: number;
  pending_by_user: PendingApprovalSummary[];
  pending_by_workflow: WorkflowPendingByType[];
  sla_breach_alerts: SLABreachAlert[];
  bottlenecks: BottleneckInfo[];
  avg_cycle_time_hours: number;
  approval_rate: number;
  completion_rate_today: number;
}

export interface PendingApprovalSummary {
  user_id: number;
  user_name: string;
  total_pending: number;
  high_priority: number;
  medium_priority: number;
  low_priority: number;
  overdue_count: number;
  avg_age_hours: number;
  oldest_approval_days: number;
}

export interface WorkflowPendingByType {
  workflow_type: string;
  workflow_name: string;
  pending_count: number;
  in_progress_count: number;
  avg_completion_time_hours: number;
  oldest_pending_days: number;
}

export interface SLABreachAlert {
  alert_id: string;
  workflow_instance_id: number;
  workflow_name: string;
  entity_type: string;
  entity_id: number;
  breach_time: string;
  breach_duration_minutes: number;
  severity: string;
  sla_percentage: number;
}

export interface BottleneckInfo {
  step_key: string;
  step_name: string;
  workflow_type: string;
  avg_duration_hours: number;
  max_duration_hours: number;
  pending_count: number;
  completion_rate: number;
  severity: string;
  recommendation: string;
}

export interface WorkflowMetrics {
  period: string;
  period_start: string;
  period_end: string;
  total_workflows: number;
  active_workflows: number;
  completion_rate: number;
  avg_cycle_time_hours: number;
}

export interface QuickStats {
  total_active: number;
  completed_today: number;
  pending_approvals: number;
  overdue_tasks: number;
}

class AnalyticsService {
  // ==================== DASHBOARD ====================

  async getDashboard(): Promise<RealtimeDashboard> {
    const response = await api.get('/workflow/analytics/dashboard');
    return response.data.data;
  }

  async getPendingApprovals(userId?: number): Promise<PendingApprovalSummary[]> {
    const params = userId ? { user_id: userId } : {};
    const response = await api.get('/workflow/analytics/dashboard/pending-approvals', { params });
    return response.data.data;
  }

  async getSLABreaches(severity?: string): Promise<SLABreachAlert[]> {
    const params = severity ? { severity } : {};
    const response = await api.get('/workflow/analytics/dashboard/sla-breaches', { params });
    return response.data.data;
  }

  async getBottlenecks(): Promise<BottleneckInfo[]> {
    const response = await api.get('/workflow/analytics/dashboard/bottlenecks');
    return response.data.data;
  }

  async getQuickStats(): Promise<QuickStats> {
    const response = await api.get('/workflow/analytics/quick-stats');
    return response.data.data;
  }

  // ==================== METRICS ====================

  async getMetrics(
    period: string = 'this_month',
    workflowType?: string,
    startDate?: string,
    endDate?: string
  ): Promise<WorkflowMetrics> {
    const params: any = { period };
    if (workflowType) params.workflow_type = workflowType;
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;

    const response = await api.get('/workflow/analytics/metrics', { params });
    return response.data.data;
  }

  async getWorkflowTypeMetrics(periodDays: number = 30): Promise<any[]> {
    const response = await api.get('/workflow/analytics/metrics/workflow-types', {
      params: { period_days: periodDays }
    });
    return response.data.data;
  }

  async getStepMetrics(workflowType?: string, periodDays: number = 30): Promise<any[]> {
    const params: any = { period_days: periodDays };
    if (workflowType) params.workflow_type = workflowType;

    const response = await api.get('/workflow/analytics/metrics/steps', { params });
    return response.data.data;
  }

  async getUserProductivity(userId?: number, periodDays: number = 30): Promise<any[]> {
    const params: any = { period_days: periodDays };
    if (userId) params.user_id = userId;

    const response = await api.get('/workflow/analytics/metrics/user-productivity', { params });
    return response.data.data;
  }

  // ==================== PROCESS MINING ====================

  async getProcessMining(workflowType: string, periodDays: number = 90): Promise<any> {
    const response = await api.get(`/workflow/analytics/process-mining/${workflowType}`, {
      params: { period_days: periodDays }
    });
    return response.data.data;
  }

  async getWorkflowPaths(workflowType: string, periodDays: number = 90): Promise<any[]> {
    const response = await api.get(`/workflow/analytics/process-mining/${workflowType}/paths`, {
      params: { period_days: periodDays }
    });
    return response.data.data;
  }

  async getDeviations(workflowType: string, periodDays: number = 90): Promise<any[]> {
    const response = await api.get(`/workflow/analytics/process-mining/${workflowType}/deviations`, {
      params: { period_days: periodDays }
    });
    return response.data.data;
  }

  async getOptimizationSuggestions(workflowType: string): Promise<any[]> {
    const response = await api.get(`/workflow/analytics/process-mining/${workflowType}/optimization`);
    return response.data.data;
  }

  // ==================== TRENDS ====================

  async getMetricTrend(
    metricName: string,
    period: string = 'this_month',
    workflowType?: string
  ): Promise<any> {
    const params: any = { period };
    if (workflowType) params.workflow_type = workflowType;

    const response = await api.get(`/workflow/analytics/trends/${metricName}`, { params });
    return response.data.data;
  }

  async getComparison(
    comparisonType: string,
    metricName: string,
    periodDays: number = 30
  ): Promise<any> {
    const response = await api.get('/workflow/analytics/trends/comparison', {
      params: {
        comparison_type: comparisonType,
        metric_name: metricName,
        period_days: periodDays
      }
    });
    return response.data.data;
  }

  // ==================== HELPER METHODS ====================

  getSeverityColor(severity: string): string {
    switch (severity.toLowerCase()) {
      case 'critical':
        return 'error';
      case 'high':
        return 'error';
      case 'medium':
        return 'warning';
      case 'low':
        return 'info';
      default:
        return 'default';
    }
  }

  getPriorityColor(priority: string): string {
    switch (priority.toLowerCase()) {
      case 'high':
      case 'urgent':
        return 'error';
      case 'medium':
        return 'warning';
      case 'low':
        return 'info';
      default:
        return 'default';
    }
  }

  formatDuration(hours: number): string {
    if (hours < 1) {
      return `${Math.round(hours * 60)}m`;
    } else if (hours < 24) {
      return `${Math.round(hours * 10) / 10}h`;
    } else {
      const days = Math.floor(hours / 24);
      const remainingHours = Math.round(hours % 24);
      return remainingHours > 0 ? `${days}d ${remainingHours}h` : `${days}d`;
    }
  }

  formatPercentage(value: number): string {
    return `${Math.round(value * 10) / 10}%`;
  }

  getCompletionRateColor(rate: number): string {
    if (rate >= 90) return 'success';
    if (rate >= 70) return 'warning';
    return 'error';
  }
}

export default new AnalyticsService();
