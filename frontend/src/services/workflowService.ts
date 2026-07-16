/**
 * Workflow Engine Service
 * API integration for workflow management and execution
 */
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API_PREFIX = '/api/v1/workflows';

// =====================================================================
// TYPES & INTERFACES
// =====================================================================

export enum NodeType {
  START_EVENT = 'START_EVENT',
  END_EVENT = 'END_EVENT',
  USER_TASK = 'USER_TASK',
  SERVICE_TASK = 'SERVICE_TASK',
  SCRIPT_TASK = 'SCRIPT_TASK',
  MANUAL_TASK = 'MANUAL_TASK',
  BUSINESS_RULE_TASK = 'BUSINESS_RULE_TASK',
  EXCLUSIVE_GATEWAY = 'EXCLUSIVE_GATEWAY',
  PARALLEL_GATEWAY = 'PARALLEL_GATEWAY',
  INCLUSIVE_GATEWAY = 'INCLUSIVE_GATEWAY',
  EVENT_BASED_GATEWAY = 'EVENT_BASED_GATEWAY',
  TIMER_EVENT = 'TIMER_EVENT',
  SIGNAL_EVENT = 'SIGNAL_EVENT',
  MESSAGE_EVENT = 'MESSAGE_EVENT',
  SUBPROCESS = 'SUBPROCESS'
}

export enum GatewayType {
  EXCLUSIVE = 'EXCLUSIVE',
  PARALLEL = 'PARALLEL',
  INCLUSIVE = 'INCLUSIVE'
}

export enum ApprovalType {
  SEQUENTIAL = 'SEQUENTIAL',
  PARALLEL = 'PARALLEL',
  ANY_ONE = 'ANY_ONE',
  MAJORITY = 'MAJORITY',
  CONSENSUS = 'CONSENSUS',
  CONDITIONAL = 'CONDITIONAL'
}

export enum SLAUnit {
  MINUTES = 'MINUTES',
  HOURS = 'HOURS',
  DAYS = 'DAYS',
  BUSINESS_DAYS = 'BUSINESS_DAYS'
}

export enum EscalationType {
  SOFT = 'SOFT',
  HARD = 'HARD',
  MULTI_LEVEL = 'MULTI_LEVEL'
}

export enum WorkflowStatus {
  DRAFT = 'DRAFT',
  ACTIVE = 'ACTIVE',
  PAUSED = 'PAUSED',
  COMPLETED = 'COMPLETED',
  CANCELLED = 'CANCELLED',
  ERROR = 'ERROR'
}


export enum TaskStatus {
  PENDING = 'PENDING',
  IN_PROGRESS = 'IN_PROGRESS',
  COMPLETED = 'COMPLETED',
  SKIPPED = 'SKIPPED',
  FAILED = 'FAILED',
  CANCELLED = 'CANCELLED'
}

export enum ApprovalDecision {
  APPROVED = 'APPROVED',
  REJECTED = 'REJECTED',
  SENT_BACK = 'SENT_BACK',
  ESCALATED = 'ESCALATED',
  PENDING = 'PENDING'
}

export enum WorkflowTrigger {
  MANUAL = 'MANUAL',
  APPLICATION_SUBMIT = 'APPLICATION_SUBMIT',
  DOCUMENT_UPLOAD = 'DOCUMENT_UPLOAD',
  PAYMENT_RECEIVED = 'PAYMENT_RECEIVED',
  SCHEDULE = 'SCHEDULE',
  API_CALL = 'API_CALL',
  WEBHOOK = 'WEBHOOK'
}

export interface WorkflowTemplate {
  id: string;
  name: string;
  code: string;
  description?: string;
  category?: string;
  version: string;
  status: WorkflowStatus;
  is_active: boolean;
  trigger_type: WorkflowTrigger;
  trigger_config?: any;
  bpmn_xml?: string;
  diagram_json?: any;
  tags?: string[];
  effective_from?: string;
  effective_to?: string;
  node_count?: number;
  connection_count?: number;
  nodes?: WorkflowNode[];
  connections?: WorkflowConnection[];
  created_at: string;
  updated_at: string;
}

export interface WorkflowNode {
  id: string;
  node_id: string;
  node_type: NodeType;
  name: string;
  description?: string;
  position_x: number;
  position_y: number;
  width: number;
  height: number;
  config?: any;
  assignee_type?: string;
  assignee_value?: string;
  form_key?: string;
  service_class?: string;
  service_method?: string;
  service_params?: any;
  script_language?: string;
  script_content?: string;
  gateway_type?: GatewayType;
  default_path?: string;
  timer_duration?: string;
  timer_date?: string;
  timer_cycle?: string;
  sla_duration?: number;
  sla_unit?: SLAUnit;
  sla_business_hours_only?: boolean;
  approval_config?: ApprovalConfig;
  escalation_rules?: EscalationRule[];
}


export interface WorkflowConnection {
  id: string;
  connection_id: string;
  name?: string;
  source_node_id: string;
  target_node_id: string;
  condition_expression?: string;
  condition_type?: string;
  is_default?: boolean;
  waypoints?: { x: number; y: number }[];
}

export interface ApprovalConfig {
  id?: string;
  approval_type: ApprovalType;
  approver_roles?: string[];
  approver_users?: string[];
  approver_expression?: string;
  approval_order?: string[];
  approval_threshold?: number;
  approval_percentage?: number;
  is_maker_checker?: boolean;
  maker_roles?: string[];
  checker_roles?: string[];
  min_checkers?: number;
  same_branch_required?: boolean;
  cooling_period_hours?: number;
  allow_self_approval?: boolean;
  allow_reassignment?: boolean;
  allow_delegation?: boolean;
  require_comments?: boolean;
  routing_rules?: any[];
}

export interface EscalationRule {
  id?: string;
  escalation_type: EscalationType;
  escalation_level: number;
  trigger_after_duration: number;
  trigger_after_unit: SLAUnit;
  send_reminder?: boolean;
  reminder_before_duration?: number;
  reminder_before_unit?: SLAUnit;
  escalate_to_supervisor?: boolean;
  escalate_to_roles?: string[];
  escalate_to_users?: string[];
  auto_reassign?: boolean;
  notify_assignee?: boolean;
  notify_supervisor?: boolean;
  notify_stakeholders?: string[];
  escalation_subject?: string;
  escalation_message?: string;
}

export interface WorkflowInstance {
  id: string;
  template_id: string;
  template_name?: string;
  instance_name: string;
  business_key?: string;
  status: WorkflowStatus;
  current_node_id?: string;
  priority: number;
  variables?: any;
  started_at: string;
  completed_at?: string;
  error_message?: string;
  executions?: WorkflowExecution[];
  approvals?: ApprovalExecution[];
}

export interface WorkflowExecution {
  id: string;
  node_id: string;
  node_name: string;
  status: TaskStatus;
  started_at: string;
  completed_at?: string;
  due_date?: string;
}


export interface ApprovalExecution {
  id: string;
  instance_id: string;
  workflow_name?: string;
  business_key?: string;
  approver_id: string;
  approver_name?: string;
  approval_level: number;
  decision: ApprovalDecision;
  comments?: string;
  assigned_at: string;
  responded_at?: string;
  due_date?: string;
  is_escalated: boolean;
  reminder_count: number;
}

export interface WorkflowStats {
  total_instances: number;
  active_instances: number;
  completed_instances: number;
  pending_approvals: number;
  sla_breached: number;
  avg_cycle_time_hours: number;
  completion_rate: number;
}

export interface NodeStats {
  node_id: string;
  node_name: string;
  total_executions: number;
  avg_duration_minutes: number;
  pending_count: number;
  sla_breach_count: number;
}

export interface Holiday {
  id: string;
  holiday_date: string;
  holiday_name: string;
  country?: string;
  state?: string;
  city?: string;
  is_working_day: boolean;
}

// Request DTOs
export interface CreateTemplateRequest {
  name: string;
  code: string;
  description?: string;
  category?: string;
  version?: string;
  trigger_type?: WorkflowTrigger;
  trigger_config?: any;
  bpmn_xml?: string;
  diagram_json?: any;
  tags?: string[];
  effective_from?: string;
  effective_to?: string;
}

export interface CreateNodeRequest {
  node_id: string;
  node_type: NodeType;
  name: string;
  description?: string;
  position_x?: number;
  position_y?: number;
  width?: number;
  height?: number;
  config?: any;
  assignee_type?: string;
  assignee_value?: string;
  sla_duration?: number;
  sla_unit?: SLAUnit;
  sla_business_hours_only?: boolean;
}


export interface CreateConnectionRequest {
  connection_id: string;
  name?: string;
  source_node_id: string;
  target_node_id: string;
  condition_expression?: string;
  condition_type?: string;
  is_default?: boolean;
  waypoints?: { x: number; y: number }[];
}

export interface StartWorkflowRequest {
  template_id: string;
  instance_name?: string;
  business_key?: string;
  variables?: any;
  priority?: number;
}

export interface ProcessApprovalRequest {
  decision: ApprovalDecision;
  comments?: string;
  reason?: string;
}

// =====================================================================
// API SERVICE
// =====================================================================

class WorkflowService {
  private getAuthHeaders() {
    const token = localStorage.getItem('auth_token');
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    };
  }

  // ===================================================================
  // TEMPLATE MANAGEMENT
  // ===================================================================

  async createTemplate(data: CreateTemplateRequest): Promise<any> {
    const response = await axios.post(
      `${API_BASE_URL}${API_PREFIX}/templates/`,
      data,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async listTemplates(params?: {
    skip?: number;
    limit?: number;
    category?: string;
    status?: WorkflowStatus;
    search?: string;
  }): Promise<WorkflowTemplate[]> {
    const response = await axios.get(
      `${API_BASE_URL}${API_PREFIX}/templates/`,
      { headers: this.getAuthHeaders(), params }
    );
    return response.data;
  }

  async getTemplate(templateId: string): Promise<WorkflowTemplate> {
    const response = await axios.get(
      `${API_BASE_URL}${API_PREFIX}/templates/${templateId}`,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async updateTemplate(templateId: string, data: Partial<CreateTemplateRequest>): Promise<any> {
    const response = await axios.put(
      `${API_BASE_URL}${API_PREFIX}/templates/${templateId}`,
      data,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }


  async deleteTemplate(templateId: string): Promise<any> {
    const response = await axios.delete(
      `${API_BASE_URL}${API_PREFIX}/templates/${templateId}`,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async activateTemplate(templateId: string): Promise<any> {
    const response = await axios.post(
      `${API_BASE_URL}${API_PREFIX}/templates/${templateId}/activate`,
      {},
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async deactivateTemplate(templateId: string): Promise<any> {
    const response = await axios.post(
      `${API_BASE_URL}${API_PREFIX}/templates/${templateId}/deactivate`,
      {},
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async cloneTemplate(templateId: string, newName: string, newCode: string): Promise<any> {
    const response = await axios.post(
      `${API_BASE_URL}${API_PREFIX}/templates/${templateId}/clone`,
      null,
      {
        headers: this.getAuthHeaders(),
        params: { new_name: newName, new_code: newCode }
      }
    );
    return response.data;
  }

  // ===================================================================
  // NODE MANAGEMENT
  // ===================================================================

  async createNode(templateId: string, data: CreateNodeRequest): Promise<any> {
    const response = await axios.post(
      `${API_BASE_URL}${API_PREFIX}/templates/${templateId}/nodes/`,
      data,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async getNode(nodeId: string): Promise<WorkflowNode> {
    const response = await axios.get(
      `${API_BASE_URL}${API_PREFIX}/nodes/${nodeId}`,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async updateNode(nodeId: string, data: Partial<CreateNodeRequest>): Promise<any> {
    const response = await axios.put(
      `${API_BASE_URL}${API_PREFIX}/nodes/${nodeId}`,
      data,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async deleteNode(nodeId: string): Promise<any> {
    const response = await axios.delete(
      `${API_BASE_URL}${API_PREFIX}/nodes/${nodeId}`,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  // ===================================================================
  // CONNECTION MANAGEMENT
  // ===================================================================

  async createConnection(templateId: string, data: CreateConnectionRequest): Promise<any> {
    const response = await axios.post(
      `${API_BASE_URL}${API_PREFIX}/templates/${templateId}/connections/`,
      data,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async deleteConnection(connectionId: string): Promise<any> {
    const response = await axios.delete(
      `${API_BASE_URL}${API_PREFIX}/connections/${connectionId}`,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }


  // ===================================================================
  // APPROVAL CONFIGURATION
  // ===================================================================

  async createApprovalConfig(nodeId: string, data: ApprovalConfig): Promise<any> {
    const response = await axios.post(
      `${API_BASE_URL}${API_PREFIX}/nodes/${nodeId}/approval-config/`,
      data,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async updateApprovalConfig(configId: string, data: Partial<ApprovalConfig>): Promise<any> {
    const response = await axios.put(
      `${API_BASE_URL}${API_PREFIX}/approval-configs/${configId}`,
      data,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  // ===================================================================
  // ESCALATION RULES
  // ===================================================================

  async createEscalationRule(nodeId: string, data: EscalationRule): Promise<any> {
    const response = await axios.post(
      `${API_BASE_URL}${API_PREFIX}/nodes/${nodeId}/escalation-rules/`,
      data,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async getEscalationRules(nodeId: string): Promise<EscalationRule[]> {
    const response = await axios.get(
      `${API_BASE_URL}${API_PREFIX}/nodes/${nodeId}/escalation-rules/`,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  // ===================================================================
  // WORKFLOW INSTANCES
  // ===================================================================

  async startWorkflow(data: StartWorkflowRequest): Promise<any> {
    const response = await axios.post(
      `${API_BASE_URL}${API_PREFIX}/instances/`,
      data,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async listInstances(params?: {
    skip?: number;
    limit?: number;
    status?: WorkflowStatus;
    template_id?: string;
    business_key?: string;
  }): Promise<WorkflowInstance[]> {
    const response = await axios.get(
      `${API_BASE_URL}${API_PREFIX}/instances/`,
      { headers: this.getAuthHeaders(), params }
    );
    return response.data;
  }

  async getInstance(instanceId: string): Promise<WorkflowInstance> {
    const response = await axios.get(
      `${API_BASE_URL}${API_PREFIX}/instances/${instanceId}`,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async cancelInstance(instanceId: string, reason?: string): Promise<any> {
    const response = await axios.post(
      `${API_BASE_URL}${API_PREFIX}/instances/${instanceId}/cancel`,
      null,
      {
        headers: this.getAuthHeaders(),
        params: { reason }
      }
    );
    return response.data;
  }


  // ===================================================================
  // APPROVAL PROCESSING
  // ===================================================================

  async processApproval(approvalId: string, data: ProcessApprovalRequest): Promise<any> {
    const response = await axios.post(
      `${API_BASE_URL}${API_PREFIX}/approvals/${approvalId}/process`,
      data,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async getPendingApprovals(params?: {
    user_id?: string;
    skip?: number;
    limit?: number;
  }): Promise<ApprovalExecution[]> {
    const response = await axios.get(
      `${API_BASE_URL}${API_PREFIX}/approvals/pending`,
      { headers: this.getAuthHeaders(), params }
    );
    return response.data;
  }

  // ===================================================================
  // SLA TRACKING
  // ===================================================================

  async getSLABreaches(): Promise<any[]> {
    const response = await axios.get(
      `${API_BASE_URL}${API_PREFIX}/sla/breaches`,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async pauseSLA(slaId: string, reason: string): Promise<any> {
    const response = await axios.post(
      `${API_BASE_URL}${API_PREFIX}/sla/${slaId}/pause`,
      null,
      {
        headers: this.getAuthHeaders(),
        params: { reason }
      }
    );
    return response.data;
  }

  async resumeSLA(slaId: string): Promise<any> {
    const response = await axios.post(
      `${API_BASE_URL}${API_PREFIX}/sla/${slaId}/resume`,
      {},
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  // ===================================================================
  // ESCALATIONS
  // ===================================================================

  async checkEscalations(): Promise<any[]> {
    const response = await axios.get(
      `${API_BASE_URL}${API_PREFIX}/escalations/check`,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  // ===================================================================
  // ANALYTICS & MONITORING
  // ===================================================================

  async getWorkflowStats(templateId?: string): Promise<WorkflowStats> {
    const response = await axios.get(
      `${API_BASE_URL}${API_PREFIX}/stats`,
      {
        headers: this.getAuthHeaders(),
        params: { template_id: templateId }
      }
    );
    return response.data;
  }

  async getNodeStats(templateId: string): Promise<NodeStats[]> {
    const response = await axios.get(
      `${API_BASE_URL}${API_PREFIX}/templates/${templateId}/node-stats`,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async getBottlenecks(templateId: string, limit: number = 5): Promise<any[]> {
    const response = await axios.get(
      `${API_BASE_URL}${API_PREFIX}/templates/${templateId}/bottlenecks`,
      {
        headers: this.getAuthHeaders(),
        params: { limit }
      }
    );
    return response.data;
  }

  async getUserProductivity(userId: string, startDate?: string, endDate?: string): Promise<any> {
    const response = await axios.get(
      `${API_BASE_URL}${API_PREFIX}/users/${userId}/productivity`,
      {
        headers: this.getAuthHeaders(),
        params: { start_date: startDate, end_date: endDate }
      }
    );
    return response.data;
  }

  async getMyProductivity(startDate?: string, endDate?: string): Promise<any> {
    const response = await axios.get(
      `${API_BASE_URL}${API_PREFIX}/users/my-productivity`,
      {
        headers: this.getAuthHeaders(),
        params: { start_date: startDate, end_date: endDate }
      }
    );
    return response.data;
  }


  // ===================================================================
  // PROCESS MINING
  // ===================================================================

  async getActualPaths(templateId: string): Promise<any> {
    const response = await axios.get(
      `${API_BASE_URL}${API_PREFIX}/templates/${templateId}/process-mining/paths`,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async getDeviationAnalysis(templateId: string): Promise<any> {
    const response = await axios.get(
      `${API_BASE_URL}${API_PREFIX}/templates/${templateId}/process-mining/deviations`,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  // ===================================================================
  // HOLIDAY CALENDAR
  // ===================================================================

  async addHoliday(data: {
    holiday_date: string;
    holiday_name: string;
    country?: string;
    state?: string;
    city?: string;
  }): Promise<any> {
    const response = await axios.post(
      `${API_BASE_URL}${API_PREFIX}/holidays/`,
      data,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async getHolidays(startDate: string, endDate: string, country?: string): Promise<Holiday[]> {
    const response = await axios.get(
      `${API_BASE_URL}${API_PREFIX}/holidays/`,
      {
        headers: this.getAuthHeaders(),
        params: { start_date: startDate, end_date: endDate, country }
      }
    );
    return response.data;
  }

  // ===================================================================
  // DASHBOARD
  // ===================================================================

  async getDashboardSummary(): Promise<any> {
    const response = await axios.get(
      `${API_BASE_URL}${API_PREFIX}/dashboard/summary`,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async getDashboardTrends(days: number = 30): Promise<any> {
    const response = await axios.get(
      `${API_BASE_URL}${API_PREFIX}/dashboard/trends`,
      {
        headers: this.getAuthHeaders(),
        params: { days }
      }
    );
    return response.data;
  }
}

// Export singleton instance
const workflowService = new WorkflowService();
export default workflowService;
