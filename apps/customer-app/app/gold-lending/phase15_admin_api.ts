/**
 * Phase 15: Platform Administration API Client
 * TypeScript client for admin and configuration endpoints
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// =====================================================
// Type Definitions
// =====================================================

export interface SystemSetting {
  id: string;
  setting_key: string;
  setting_value: string;
  setting_type: string;
  category: string;
  description?: string;
  is_encrypted: boolean;
  is_editable: boolean;
  requires_restart: boolean;
  validation_rules?: Record<string, any>;
  default_value?: string;
  last_modified_by?: string;
  last_modified_at?: string;
  change_history?: any[];
  metadata?: Record<string, any>;
  created_at: string;
  updated_at: string;
  version: number;
}

export interface Role {
  id: string;
  role_code: string;
  role_name: string;
  description?: string;
  role_type: string;
  is_system_role: boolean;
  permissions: string[];
  resource_access: Record<string, any>;
  parent_role_id?: string;
  hierarchy_level: number;
  is_active: boolean;
  status: string;
  max_users?: number;
  current_user_count: number;
  metadata?: Record<string, any>;
  created_by?: string;
  updated_by?: string;
  created_at: string;
  updated_at: string;
  version: number;
}


export interface UserRole {
  id: string;
  user_id: string;
  role_id: string;
  assigned_by?: string;
  assigned_at?: string;
  expires_at?: string;
  is_active: boolean;
  status: string;
  scope_type?: string;
  scope_value?: string;
  assignment_reason?: string;
  metadata?: Record<string, any>;
  created_at: string;
  updated_at: string;
  version: number;
}

export interface Permission {
  id: string;
  permission_code: string;
  permission_name: string;
  description?: string;
  module: string;
  resource: string;
  action: string;
  permission_type: string;
  risk_level?: string;
  requires_approval: boolean;
  requires_mfa: boolean;
  is_active: boolean;
  metadata?: Record<string, any>;
  created_at: string;
  updated_at: string;
  version: number;
}

export interface AuditLog {
  id: string;
  log_code: string;
  event_type: string;
  event_category: string;
  event_name: string;
  event_description?: string;
  user_id?: string;
  username?: string;
  user_ip_address?: string;
  user_agent?: string;
  resource_type?: string;
  resource_id?: string;
  resource_name?: string;
  action: string;
  action_result: string;
  old_values?: Record<string, any>;
  new_values?: Record<string, any>;
  changes?: Record<string, any>;
  request_id?: string;
  session_id?: string;
  metadata?: Record<string, any>;
  tags?: string[];
  created_at: string;
  updated_at: string;
  version: number;
}

export interface SystemHealth {
  id: string;
  check_code: string;
  check_name: string;
  check_type: string;
  component_name: string;
  health_status: string;
  previous_status?: string;
  response_time_ms?: number;
  availability_percent?: number;
  last_check_at: string;
  next_check_at?: string;
  consecutive_failures: number;
  is_critical: boolean;
  is_enabled: boolean;
  metadata?: Record<string, any>;
  created_at: string;
  updated_at: string;
  version: number;
}

export interface SystemMetric {
  id: string;
  metric_name: string;
  metric_type: string;
  metric_category: string;
  metric_value: number;
  metric_unit?: string;
  service_name?: string;
  module_name?: string;
  recorded_at: string;
  labels?: Record<string, any>;
  tags?: string[];
  metadata?: Record<string, any>;
  created_at: string;
  updated_at: string;
  version: number;
}


export interface NotificationTemplate {
  id: string;
  template_code: string;
  template_name: string;
  description?: string;
  notification_type: string;
  template_category: string;
  subject_template?: string;
  body_template: string;
  html_template?: string;
  template_engine: string;
  template_variables: string[];
  language: string;
  priority: string;
  is_active: boolean;
  status: string;
  usage_count: number;
  last_used_at?: string;
  metadata?: Record<string, any>;
  created_by?: string;
  updated_by?: string;
  created_at: string;
  updated_at: string;
  version: number;
}

export interface ScheduledJob {
  id: string;
  job_code: string;
  job_name: string;
  description?: string;
  job_type: string;
  job_category: string;
  handler_class: string;
  handler_method: string;
  parameters?: Record<string, any>;
  schedule_expression?: string;
  interval_minutes?: number;
  is_enabled: boolean;
  status: string;
  last_execution_at?: string;
  last_execution_status?: string;
  next_execution_at?: string;
  total_executions: number;
  success_count: number;
  failure_count: number;
  avg_duration_ms?: number;
  metadata?: Record<string, any>;
  created_by?: string;
  updated_by?: string;
  created_at: string;
  updated_at: string;
  version: number;
}


export interface JobExecution {
  id: string;
  execution_code: string;
  job_id: string;
  execution_type: string;
  started_at: string;
  completed_at?: string;
  duration_ms?: number;
  execution_status: string;
  execution_result?: Record<string, any>;
  rows_processed?: number;
  error_message?: string;
  metadata?: Record<string, any>;
  created_at: string;
  updated_at: string;
  version: number;
}

export interface FeatureFlag {
  id: string;
  flag_key: string;
  flag_name: string;
  description?: string;
  flag_type: string;
  flag_value: string;
  default_value?: string;
  is_enabled: boolean;
  status: string;
  targeting_rules: any[];
  rollout_percentage: number;
  scope: string;
  environment: string;
  usage_count: number;
  last_accessed_at?: string;
  metadata?: Record<string, any>;
  tags?: string[];
  created_by?: string;
  updated_by?: string;
  created_at: string;
  updated_at: string;
  version: number;
}

export interface APIKey {
  id: string;
  key_name: string;
  key_hash: string;
  key_prefix: string;
  user_id?: string;
  application_name?: string;
  allowed_permissions: string[];
  scope: string;
  is_active: boolean;
  status: string;
  expires_at?: string;
  last_used_at?: string;
  usage_count: number;
  metadata?: Record<string, any>;
  created_by?: string;
  created_at: string;
  updated_at: string;
  version: number;
}


export interface LoginHistory {
  id: string;
  user_id?: string;
  username?: string;
  login_type: string;
  login_status: string;
  session_id?: string;
  ip_address?: string;
  user_agent?: string;
  device_type?: string;
  browser?: string;
  country?: string;
  city?: string;
  is_suspicious: boolean;
  risk_score?: number;
  mfa_used: boolean;
  login_at?: string;
  logout_at?: string;
  session_duration_minutes?: number;
  metadata?: Record<string, any>;
  created_at: string;
  updated_at: string;
  version: number;
}

export interface AdminOverview {
  total_users: number;
  active_users: number;
  total_roles: number;
  active_roles: number;
  total_permissions: number;
  total_audit_logs: number;
  total_system_health_checks: number;
  healthy_components: number;
  unhealthy_components: number;
  total_scheduled_jobs: number;
  active_scheduled_jobs: number;
  total_feature_flags: number;
  enabled_feature_flags: number;
  total_api_keys: number;
  active_api_keys: number;
  total_logins_today: number;
  failed_logins_today: number;
}

// =====================================================
// API Client Class
// =====================================================

class Phase15AdminAPI {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }

    return response.json();
  }


  // =====================================================
  // System Settings
  // =====================================================

  async createSystemSetting(data: Partial<SystemSetting>): Promise<SystemSetting> {
    return this.request<SystemSetting>('/api/v1/gold/admin/settings', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async listSystemSettings(params?: {
    skip?: number;
    limit?: number;
    category?: string;
    setting_type?: string;
  }): Promise<SystemSetting[]> {
    const query = new URLSearchParams(params as any).toString();
    return this.request<SystemSetting[]>(`/api/v1/gold/admin/settings?${query}`);
  }

  async getSystemSetting(id: string): Promise<SystemSetting> {
    return this.request<SystemSetting>(`/api/v1/gold/admin/settings/${id}`);
  }

  async getSystemSettingByKey(key: string): Promise<SystemSetting> {
    return this.request<SystemSetting>(`/api/v1/gold/admin/settings/key/${key}`);
  }

  async updateSystemSetting(id: string, data: Partial<SystemSetting>): Promise<SystemSetting> {
    return this.request<SystemSetting>(`/api/v1/gold/admin/settings/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteSystemSetting(id: string): Promise<void> {
    return this.request<void>(`/api/v1/gold/admin/settings/${id}`, {
      method: 'DELETE',
    });
  }

  // =====================================================
  // Roles
  // =====================================================

  async createRole(data: Partial<Role>): Promise<Role> {
    return this.request<Role>('/api/v1/gold/admin/roles', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async listRoles(params?: {
    skip?: number;
    limit?: number;
    role_type?: string;
    status?: string;
    is_active?: boolean;
  }): Promise<Role[]> {
    const query = new URLSearchParams(params as any).toString();
    return this.request<Role[]>(`/api/v1/gold/admin/roles?${query}`);
  }


  async getRole(id: string): Promise<Role> {
    return this.request<Role>(`/api/v1/gold/admin/roles/${id}`);
  }

  async updateRole(id: string, data: Partial<Role>): Promise<Role> {
    return this.request<Role>(`/api/v1/gold/admin/roles/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteRole(id: string): Promise<void> {
    return this.request<void>(`/api/v1/gold/admin/roles/${id}`, {
      method: 'DELETE',
    });
  }

  // =====================================================
  // User Role Assignments
  // =====================================================

  async assignUserRole(data: Partial<UserRole>): Promise<UserRole> {
    return this.request<UserRole>('/api/v1/gold/admin/user-roles', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async listUserRoles(params?: {
    skip?: number;
    limit?: number;
    user_id?: string;
    role_id?: string;
    status?: string;
  }): Promise<UserRole[]> {
    const query = new URLSearchParams(params as any).toString();
    return this.request<UserRole[]>(`/api/v1/gold/admin/user-roles?${query}`);
  }

  async getUserRole(id: string): Promise<UserRole> {
    return this.request<UserRole>(`/api/v1/gold/admin/user-roles/${id}`);
  }

  async updateUserRole(id: string, data: Partial<UserRole>): Promise<UserRole> {
    return this.request<UserRole>(`/api/v1/gold/admin/user-roles/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async revokeUserRole(id: string): Promise<void> {
    return this.request<void>(`/api/v1/gold/admin/user-roles/${id}`, {
      method: 'DELETE',
    });
  }


  // =====================================================
  // Permissions
  // =====================================================

  async createPermission(data: Partial<Permission>): Promise<Permission> {
    return this.request<Permission>('/api/v1/gold/admin/permissions', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async listPermissions(params?: {
    skip?: number;
    limit?: number;
    module?: string;
    resource?: string;
    action?: string;
    is_active?: boolean;
  }): Promise<Permission[]> {
    const query = new URLSearchParams(params as any).toString();
    return this.request<Permission[]>(`/api/v1/gold/admin/permissions?${query}`);
  }

  async getPermission(id: string): Promise<Permission> {
    return this.request<Permission>(`/api/v1/gold/admin/permissions/${id}`);
  }

  async updatePermission(id: string, data: Partial<Permission>): Promise<Permission> {
    return this.request<Permission>(`/api/v1/gold/admin/permissions/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deletePermission(id: string): Promise<void> {
    return this.request<void>(`/api/v1/gold/admin/permissions/${id}`, {
      method: 'DELETE',
    });
  }

  // =====================================================
  // Audit Logs
  // =====================================================

  async createAuditLog(data: Partial<AuditLog>): Promise<AuditLog> {
    return this.request<AuditLog>('/api/v1/gold/admin/audit-logs', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async listAuditLogs(params?: {
    skip?: number;
    limit?: number;
    event_type?: string;
    event_category?: string;
    user_id?: string;
    action?: string;
    action_result?: string;
    resource_type?: string;
    is_sensitive?: boolean;
  }): Promise<AuditLog[]> {
    const query = new URLSearchParams(params as any).toString();
    return this.request<AuditLog[]>(`/api/v1/gold/admin/audit-logs?${query}`);
  }


  async getAuditLog(id: string): Promise<AuditLog> {
    return this.request<AuditLog>(`/api/v1/gold/admin/audit-logs/${id}`);
  }

  // =====================================================
  // System Health
  // =====================================================

  async createHealthCheck(data: Partial<SystemHealth>): Promise<SystemHealth> {
    return this.request<SystemHealth>('/api/v1/gold/admin/health-checks', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async listHealthChecks(params?: {
    skip?: number;
    limit?: number;
    check_type?: string;
    component_name?: string;
    health_status?: string;
    is_critical?: boolean;
  }): Promise<SystemHealth[]> {
    const query = new URLSearchParams(params as any).toString();
    return this.request<SystemHealth[]>(`/api/v1/gold/admin/health-checks?${query}`);
  }

  async getHealthCheck(id: string): Promise<SystemHealth> {
    return this.request<SystemHealth>(`/api/v1/gold/admin/health-checks/${id}`);
  }

  async updateHealthCheck(id: string, data: Partial<SystemHealth>): Promise<SystemHealth> {
    return this.request<SystemHealth>(`/api/v1/gold/admin/health-checks/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async runHealthCheck(id: string): Promise<SystemHealth> {
    return this.request<SystemHealth>(`/api/v1/gold/admin/health-checks/${id}/run`, {
      method: 'POST',
    });
  }

  async deleteHealthCheck(id: string): Promise<void> {
    return this.request<void>(`/api/v1/gold/admin/health-checks/${id}`, {
      method: 'DELETE',
    });
  }

  // =====================================================
  // System Metrics
  // =====================================================

  async createSystemMetric(data: Partial<SystemMetric>): Promise<SystemMetric> {
    return this.request<SystemMetric>('/api/v1/gold/admin/metrics', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }


  async listSystemMetrics(params?: {
    skip?: number;
    limit?: number;
    metric_name?: string;
    metric_type?: string;
    metric_category?: string;
    service_name?: string;
  }): Promise<SystemMetric[]> {
    const query = new URLSearchParams(params as any).toString();
    return this.request<SystemMetric[]>(`/api/v1/gold/admin/metrics?${query}`);
  }

  async getSystemMetric(id: string): Promise<SystemMetric> {
    return this.request<SystemMetric>(`/api/v1/gold/admin/metrics/${id}`);
  }

  // =====================================================
  // Notification Templates
  // =====================================================

  async createNotificationTemplate(data: Partial<NotificationTemplate>): Promise<NotificationTemplate> {
    return this.request<NotificationTemplate>('/api/v1/gold/admin/notification-templates', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async listNotificationTemplates(params?: {
    skip?: number;
    limit?: number;
    notification_type?: string;
    template_category?: string;
    status?: string;
  }): Promise<NotificationTemplate[]> {
    const query = new URLSearchParams(params as any).toString();
    return this.request<NotificationTemplate[]>(`/api/v1/gold/admin/notification-templates?${query}`);
  }

  async getNotificationTemplate(id: string): Promise<NotificationTemplate> {
    return this.request<NotificationTemplate>(`/api/v1/gold/admin/notification-templates/${id}`);
  }

  async updateNotificationTemplate(id: string, data: Partial<NotificationTemplate>): Promise<NotificationTemplate> {
    return this.request<NotificationTemplate>(`/api/v1/gold/admin/notification-templates/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteNotificationTemplate(id: string): Promise<void> {
    return this.request<void>(`/api/v1/gold/admin/notification-templates/${id}`, {
      method: 'DELETE',
    });
  }


  // =====================================================
  // Scheduled Jobs
  // =====================================================

  async createScheduledJob(data: Partial<ScheduledJob>): Promise<ScheduledJob> {
    return this.request<ScheduledJob>('/api/v1/gold/admin/scheduled-jobs', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async listScheduledJobs(params?: {
    skip?: number;
    limit?: number;
    job_type?: string;
    job_category?: string;
    status?: string;
    is_enabled?: boolean;
  }): Promise<ScheduledJob[]> {
    const query = new URLSearchParams(params as any).toString();
    return this.request<ScheduledJob[]>(`/api/v1/gold/admin/scheduled-jobs?${query}`);
  }

  async getScheduledJob(id: string): Promise<ScheduledJob> {
    return this.request<ScheduledJob>(`/api/v1/gold/admin/scheduled-jobs/${id}`);
  }

  async updateScheduledJob(id: string, data: Partial<ScheduledJob>): Promise<ScheduledJob> {
    return this.request<ScheduledJob>(`/api/v1/gold/admin/scheduled-jobs/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async executeScheduledJob(id: string): Promise<JobExecution> {
    return this.request<JobExecution>(`/api/v1/gold/admin/scheduled-jobs/${id}/execute`, {
      method: 'POST',
    });
  }

  async deleteScheduledJob(id: string): Promise<void> {
    return this.request<void>(`/api/v1/gold/admin/scheduled-jobs/${id}`, {
      method: 'DELETE',
    });
  }

  // =====================================================
  // Job Executions
  // =====================================================

  async listJobExecutions(params?: {
    skip?: number;
    limit?: number;
    job_id?: string;
    execution_status?: string;
    execution_type?: string;
  }): Promise<JobExecution[]> {
    const query = new URLSearchParams(params as any).toString();
    return this.request<JobExecution[]>(`/api/v1/gold/admin/job-executions?${query}`);
  }


  async getJobExecution(id: string): Promise<JobExecution> {
    return this.request<JobExecution>(`/api/v1/gold/admin/job-executions/${id}`);
  }

  async updateJobExecution(id: string, data: Partial<JobExecution>): Promise<JobExecution> {
    return this.request<JobExecution>(`/api/v1/gold/admin/job-executions/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  // =====================================================
  // Feature Flags
  // =====================================================

  async createFeatureFlag(data: Partial<FeatureFlag>): Promise<FeatureFlag> {
    return this.request<FeatureFlag>('/api/v1/gold/admin/feature-flags', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async listFeatureFlags(params?: {
    skip?: number;
    limit?: number;
    flag_type?: string;
    environment?: string;
    is_enabled?: boolean;
    status?: string;
  }): Promise<FeatureFlag[]> {
    const query = new URLSearchParams(params as any).toString();
    return this.request<FeatureFlag[]>(`/api/v1/gold/admin/feature-flags?${query}`);
  }

  async getFeatureFlag(id: string): Promise<FeatureFlag> {
    return this.request<FeatureFlag>(`/api/v1/gold/admin/feature-flags/${id}`);
  }

  async getFeatureFlagByKey(key: string): Promise<FeatureFlag> {
    return this.request<FeatureFlag>(`/api/v1/gold/admin/feature-flags/key/${key}`);
  }

  async updateFeatureFlag(id: string, data: Partial<FeatureFlag>): Promise<FeatureFlag> {
    return this.request<FeatureFlag>(`/api/v1/gold/admin/feature-flags/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async toggleFeatureFlag(id: string): Promise<FeatureFlag> {
    return this.request<FeatureFlag>(`/api/v1/gold/admin/feature-flags/${id}/toggle`, {
      method: 'POST',
    });
  }

  async deleteFeatureFlag(id: string): Promise<void> {
    return this.request<void>(`/api/v1/gold/admin/feature-flags/${id}`, {
      method: 'DELETE',
    });
  }


  // =====================================================
  // API Keys
  // =====================================================

  async createAPIKey(data: Partial<APIKey>): Promise<APIKey> {
    return this.request<APIKey>('/api/v1/gold/admin/api-keys', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async listAPIKeys(params?: {
    skip?: number;
    limit?: number;
    user_id?: string;
    status?: string;
    is_active?: boolean;
  }): Promise<APIKey[]> {
    const query = new URLSearchParams(params as any).toString();
    return this.request<APIKey[]>(`/api/v1/gold/admin/api-keys?${query}`);
  }

  async getAPIKey(id: string): Promise<APIKey> {
    return this.request<APIKey>(`/api/v1/gold/admin/api-keys/${id}`);
  }

  async updateAPIKey(id: string, data: Partial<APIKey>): Promise<APIKey> {
    return this.request<APIKey>(`/api/v1/gold/admin/api-keys/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async revokeAPIKey(id: string, reason?: string): Promise<APIKey> {
    return this.request<APIKey>(`/api/v1/gold/admin/api-keys/${id}/revoke`, {
      method: 'POST',
      body: JSON.stringify({ revoked_reason: reason }),
    });
  }

  async deleteAPIKey(id: string): Promise<void> {
    return this.request<void>(`/api/v1/gold/admin/api-keys/${id}`, {
      method: 'DELETE',
    });
  }

  // =====================================================
  // Login History
  // =====================================================

  async createLoginHistory(data: Partial<LoginHistory>): Promise<LoginHistory> {
    return this.request<LoginHistory>('/api/v1/gold/admin/login-history', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async listLoginHistory(params?: {
    skip?: number;
    limit?: number;
    user_id?: string;
    login_status?: string;
    is_suspicious?: boolean;
  }): Promise<LoginHistory[]> {
    const query = new URLSearchParams(params as any).toString();
    return this.request<LoginHistory[]>(`/api/v1/gold/admin/login-history?${query}`);
  }


  async getLoginHistory(id: string): Promise<LoginHistory> {
    return this.request<LoginHistory>(`/api/v1/gold/admin/login-history/${id}`);
  }

  async updateLoginHistory(id: string, data: Partial<LoginHistory>): Promise<LoginHistory> {
    return this.request<LoginHistory>(`/api/v1/gold/admin/login-history/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  // =====================================================
  // Statistics & Analytics
  // =====================================================

  async getAdminOverview(): Promise<AdminOverview> {
    return this.request<AdminOverview>('/api/v1/gold/admin/statistics/overview');
  }

  async getSystemHealthMetrics(params?: {
    skip?: number;
    limit?: number;
  }): Promise<any[]> {
    const query = new URLSearchParams(params as any).toString();
    return this.request<any[]>(`/api/v1/gold/admin/statistics/system-health?${query}`);
  }

  async getJobExecutionMetrics(params?: {
    skip?: number;
    limit?: number;
  }): Promise<any[]> {
    const query = new URLSearchParams(params as any).toString();
    return this.request<any[]>(`/api/v1/gold/admin/statistics/job-executions?${query}`);
  }

  async getSecurityMetrics(): Promise<any> {
    return this.request<any>('/api/v1/gold/admin/statistics/security');
  }

  async getUserActivityMetrics(params?: {
    skip?: number;
    limit?: number;
  }): Promise<any[]> {
    const query = new URLSearchParams(params as any).toString();
    return this.request<any[]>(`/api/v1/gold/admin/statistics/user-activity?${query}`);
  }
}

// Export singleton instance
export const adminAPI = new Phase15AdminAPI();
export default adminAPI;


  async getLoginHistory(id: string): Promise<LoginHistory> {
    return this.request<LoginHistory>(`/api/v1/gold/admin/login-history/${id}`);
  }

  async updateLoginHistory(id: string, data: Partial<LoginHistory>): Promise<LoginHistory> {
    return this.request<LoginHistory>(`/api/v1/gold/admin/login-history/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  // =====================================================
  // Statistics & Overview
  // =====================================================

  async getAdminOverview(): Promise<AdminOverview> {
    return this.request<AdminOverview>('/api/v1/gold/admin/statistics/overview');
  }

  async getSystemHealthMetrics(params?: { skip?: number; limit?: number }): Promise<any[]> {
    const query = new URLSearchParams(params as any).toString();
    return this.request<any[]>(`/api/v1/gold/admin/statistics/system-health?${query}`);
  }

  async getJobExecutionMetrics(params?: { skip?: number; limit?: number }): Promise<any[]> {
    const query = new URLSearchParams(params as any).toString();
    return this.request<any[]>(`/api/v1/gold/admin/statistics/job-executions?${query}`);
  }

  async getSecurityMetrics(): Promise<any> {
    return this.request<any>('/api/v1/gold/admin/statistics/security');
  }

  async getUserActivityMetrics(params?: { skip?: number; limit?: number }): Promise<any[]> {
    const query = new URLSearchParams(params as any).toString();
    return this.request<any[]>(`/api/v1/gold/admin/statistics/user-activity?${query}`);
  }
}

// Export singleton instance
export const phase15AdminAPI = new Phase15AdminAPI();

// Export class for custom instances
export default Phase15AdminAPI;
