/**
 * SLA & Escalation Management Service
 * 
 * API integration for SLA tracking and escalation management
 */

import api from './api';

export interface SLAConfiguration {
  sla_id: string;
  name: string;
  description?: string;
  entity_type: string;
  workflow_step?: string;
  sla_type: 'response_time' | 'resolution_time' | 'approval_time';
  time_value: number;
  time_unit: 'minutes' | 'hours' | 'days';
  calculation_type: 'calendar_hours' | 'business_hours' | 'working_days';
  business_hours_config?: BusinessHoursConfig;
  holiday_calendar_id?: string;
  allow_pause: boolean;
  pause_on_customer_action: boolean;
  warning_threshold: number;
  critical_threshold: number;
  is_active: boolean;
}

export interface BusinessHoursConfig {
  enabled: boolean;
  monday?: { start: string; end: string };
  tuesday?: { start: string; end: string };
  wednesday?: { start: string; end: string };
  thursday?: { start: string; end: string };
  friday?: { start: string; end: string };
  saturday?: { start: string; end: string } | null;
  sunday?: { start: string; end: string } | null;
  timezone: string;
}

export interface EscalationRule {
  rule_id: string;
  name: string;
  description?: string;
  trigger_after_hours?: number;
  trigger_after_percentage?: number;
  escalation_type: 'soft' | 'hard' | 'notify' | 'multi_level';
  send_reminder_to_assignee: boolean;
  notify_supervisor: boolean;
  notify_users?: number[];
  auto_transfer_to?: number;
  escalate_to_next_level: boolean;
  repeat_escalation: boolean;
  repeat_interval_hours?: number;
  max_escalations: number;
  is_active: boolean;
}

export interface SLAEscalationConfig {
  config_id: string;
  name: string;
  entity_type: string;
  sla: SLAConfiguration;
  escalation_rules: EscalationRule[];
  send_breach_notification: boolean;
}

export interface SLAInstance {
  instance_id: number;
  sla_config_id: string;
  entity_type: string;
  entity_id: number;
  workflow_instance_id: number;
  workflow_step_id?: number;
  status: 'active' | 'met' | 'breached' | 'paused' | 'cancelled';
  start_time: string;
  deadline: string;
  completion_time?: string;
  time_elapsed_minutes: number;
  time_remaining_minutes: number;
  sla_percentage: number;
  escalation_count: number;
  total_paused_duration: number;
  breach_time?: string;
  breach_duration_minutes?: number;
}

export interface SLAMetrics {
  entity_type: string;
  period_start: string;
  period_end: string;
  total_slas: number;
  met_slas: number;
  breached_slas: number;
  active_slas: number;
  sla_compliance_rate: number;
  average_completion_percentage: number;
  average_completion_time_hours: number;
  total_escalations: number;
}

export interface HolidayCalendar {
  calendar_id: string;
  name: string;
  holidays: string[];
  country: string;
  region?: string;
}

class SLAService {
  // ==================== SLA CONFIGURATION ====================

  async createConfiguration(config: Omit<SLAEscalationConfig, 'config_id'>): Promise<SLAEscalationConfig> {
    const response = await api.post('/workflow/sla/configurations', config);
    return response.data.data;
  }

  async listConfigurations(entityType?: string): Promise<SLAEscalationConfig[]> {
    const params = entityType ? { entity_type: entityType } : {};
    const response = await api.get('/workflow/sla/configurations', { params });
    return response.data.data;
  }

  async getConfiguration(configId: string): Promise<SLAEscalationConfig> {
    const response = await api.get(`/workflow/sla/configurations/${configId}`);
    return response.data.data;
  }

  async getTemplates(): Promise<SLAEscalationConfig[]> {
    const response = await api.get('/workflow/sla/templates');
    return response.data.data;
  }

  // ==================== SLA TRACKING ====================

  async startTracking(data: {
    sla_config_id: string;
    entity_id: number;
    workflow_instance_id: number;
    workflow_step_id?: number;
  }): Promise<{ sla_instance_id: number; status: string; start_time: string; deadline: string }> {
    const response = await api.post('/workflow/sla/instances/start', data);
    return response.data.data;
  }

  async completeSLA(instanceId: number, success: boolean = true): Promise<any> {
    const response = await api.post(`/workflow/sla/instances/${instanceId}/complete`, null, {
      params: { success }
    });
    return response.data.data;
  }

  async pauseSLA(instanceId: number, reason?: string): Promise<any> {
    const response = await api.post(`/workflow/sla/instances/${instanceId}/pause`, { reason });
    return response.data.data;
  }

  async resumeSLA(instanceId: number): Promise<any> {
    const response = await api.post(`/workflow/sla/instances/${instanceId}/resume`);
    return response.data.data;
  }

  async getSLAStatus(instanceId: number): Promise<SLAInstance> {
    const response = await api.get(`/workflow/sla/instances/${instanceId}/status`);
    return response.data.data;
  }

  async listInstances(filters?: {
    entity_type?: string;
    status?: string;
    workflow_instance_id?: number;
  }): Promise<SLAInstance[]> {
    const response = await api.get('/workflow/sla/instances', { params: filters });
    return response.data.data;
  }

  // ==================== ESCALATION ====================

  async processEscalations(instanceId: number): Promise<any> {
    const response = await api.post(`/workflow/sla/instances/${instanceId}/process-escalations`);
    return response.data.data;
  }

  async getEscalationHistory(instanceId: number): Promise<any[]> {
    const response = await api.get(`/workflow/sla/instances/${instanceId}/escalation-history`);
    return response.data.data;
  }

  // ==================== METRICS ====================

  async getMetrics(entityType: string, periodDays: number = 30): Promise<SLAMetrics> {
    const response = await api.get('/workflow/sla/metrics', {
      params: { entity_type: entityType, period_days: periodDays }
    });
    return response.data.data;
  }

  // ==================== HOLIDAY CALENDAR ====================

  async createHolidayCalendar(calendar: Omit<HolidayCalendar, 'calendar_id'>): Promise<HolidayCalendar> {
    const response = await api.post('/workflow/sla/holiday-calendars', calendar);
    return response.data.data;
  }

  async listHolidayCalendars(): Promise<HolidayCalendar[]> {
    const response = await api.get('/workflow/sla/holiday-calendars');
    return response.data.data;
  }

  // ==================== HELPER METHODS ====================

  getSLAStatusColor(status: string): string {
    switch (status) {
      case 'active':
        return 'primary';
      case 'met':
        return 'success';
      case 'breached':
        return 'error';
      case 'paused':
        return 'warning';
      default:
        return 'default';
    }
  }

  getSLAPercentageColor(percentage: number, warningThreshold: number = 70, criticalThreshold: number = 90): string {
    if (percentage >= criticalThreshold) {
      return 'error';
    } else if (percentage >= warningThreshold) {
      return 'warning';
    } else {
      return 'success';
    }
  }

  formatDuration(minutes: number): string {
    if (minutes < 60) {
      return `${minutes}m`;
    } else if (minutes < 1440) {
      const hours = Math.floor(minutes / 60);
      const mins = minutes % 60;
      return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
    } else {
      const days = Math.floor(minutes / 1440);
      const hours = Math.floor((minutes % 1440) / 60);
      return hours > 0 ? `${days}d ${hours}h` : `${days}d`;
    }
  }

  formatTimeRemaining(minutes: number): string {
    if (minutes < 0) {
      return `Breached by ${this.formatDuration(Math.abs(minutes))}`;
    }
    return this.formatDuration(minutes);
  }
}

export default new SLAService();
