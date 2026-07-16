/**
 * Business Rules Engine Service
 * API integration for rules management and execution
 */
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API_PREFIX = '/api/v1/rules';

// =====================================================================
// TYPES & INTERFACES
// =====================================================================

export enum RuleType {
  DECISION = 'DECISION',
  VALIDATION = 'VALIDATION',
  CALCULATION = 'CALCULATION',
  ROUTING = 'ROUTING',
  PRICING = 'PRICING',
  ELIGIBILITY = 'ELIGIBILITY',
  SCORING = 'SCORING',
  DERIVATION = 'DERIVATION'
}

export enum RuleStatus {
  DRAFT = 'DRAFT',
  ACTIVE = 'ACTIVE',
  INACTIVE = 'INACTIVE',
  ARCHIVED = 'ARCHIVED',
  TESTING = 'TESTING'
}

export enum ConditionOperator {
  EQUALS = 'EQUALS',
  NOT_EQUALS = 'NOT_EQUALS',
  GREATER_THAN = 'GREATER_THAN',
  GREATER_THAN_OR_EQUAL = 'GREATER_THAN_OR_EQUAL',
  LESS_THAN = 'LESS_THAN',
  LESS_THAN_OR_EQUAL = 'LESS_THAN_OR_EQUAL',
  IN = 'IN',
  NOT_IN = 'NOT_IN',
  CONTAINS = 'CONTAINS',
  NOT_CONTAINS = 'NOT_CONTAINS',
  STARTS_WITH = 'STARTS_WITH',
  ENDS_WITH = 'ENDS_WITH',
  BETWEEN = 'BETWEEN',
  IS_NULL = 'IS_NULL',
  IS_NOT_NULL = 'IS_NOT_NULL',
  MATCHES_REGEX = 'MATCHES_REGEX'
}

export enum LogicalOperator {
  AND = 'AND',
  OR = 'OR',
  NOT = 'NOT'
}

export enum ActionType {
  SET_VALUE = 'SET_VALUE',
  CALCULATE = 'CALCULATE',
  CALL_API = 'CALL_API',
  SEND_NOTIFICATION = 'SEND_NOTIFICATION',
  TRIGGER_WORKFLOW = 'TRIGGER_WORKFLOW',
  LOG_EVENT = 'LOG_EVENT',
  RAISE_ALERT = 'RAISE_ALERT',
  STOP_EXECUTION = 'STOP_EXECUTION',
  EXECUTE_SCRIPT = 'EXECUTE_SCRIPT'
}

export enum DataType {
  STRING = 'STRING',
  INTEGER = 'INTEGER',
  FLOAT = 'FLOAT',
  BOOLEAN = 'BOOLEAN',
  DATE = 'DATE',
  DATETIME = 'DATETIME',
  LIST = 'LIST',
  OBJECT = 'OBJECT'
}

export enum ExecutionMode {
  REAL_TIME = 'REAL_TIME',
  BATCH = 'BATCH',
  ON_DEMAND = 'ON_DEMAND'
}

export interface RuleSet {
  id: string;
  name: string;
  code: string;
  description?: string;
  category?: string;
  version: string;
  status: RuleStatus;
  is_active: boolean;
  execution_mode: ExecutionMode;
  priority: number;
  effective_from?: string;
  effective_to?: string;
  rule_count?: number;
  rules?: Rule[];
  decision_tables?: DecisionTable[];
  created_at: string;
  updated_at: string;
}

export interface Condition {
  id?: string;
  condition_group?: string;
  condition_order: number;
  field_name: string;
  field_type: DataType;
  operator: ConditionOperator;
  value?: string;
  value_list?: any[];
  value_from?: string;
  value_to?: string;
  is_dynamic?: boolean;
  dynamic_field_name?: string;
  expression?: string;
  logical_operator: LogicalOperator;
}

export interface Action {
  id?: string;
  action_type: ActionType;
  action_order: number;
  target_field?: string;
  value?: string;
  expression?: string;
  calculation_formula?: string;
  api_endpoint?: string;
  api_method?: string;
  notification_template?: string;
  workflow_template_id?: string;
  script_content?: string;
  alert_severity?: string;
  alert_message?: string;
}

export interface Rule {
  id: string;
  rule_set_id: string;
  name: string;
  code: string;
  description?: string;
  rule_type: RuleType;
  priority: number;
  execution_order?: number;
  logical_operator: LogicalOperator;
  stop_on_match: boolean;
  continue_on_error: boolean;
  is_active: boolean;
  tags?: string[];
  condition_count?: number;
  action_count?: number;
  conditions?: Condition[];
  actions?: Action[];
  created_at: string;
  updated_at: string;
}

export interface DecisionTable {
  id: string;
  rule_set_id: string;
  name: string;
  code: string;
  description?: string;
  input_columns: any[];
  output_columns: any[];
  hit_policy: string;
  is_active: boolean;
  row_count?: number;
  rows?: DecisionTableRow[];
  created_at: string;
  updated_at: string;
}

export interface DecisionTableRow {
  id: string;
  row_number: number;
  priority: number;
  input_values: { [key: string]: any };
  output_values: { [key: string]: any };
  description?: string;
  is_active: boolean;
}

export interface RuleExecution {
  id: string;
  rule_set_id: string;
  execution_context?: string;
  business_key?: string;
  rules_evaluated: number;
  rules_matched: number;
  actions_executed: number;
  matched_rules: string[];
  status: string;
  execution_time_ms: number;
  started_at: string;
  completed_at?: string;
}

export interface RuleStats {
  total_rule_sets: number;
  active_rule_sets: number;
  total_rules: number;
  total_executions: number;
  avg_execution_time_ms: number;
  success_rate: number;
}

// Request DTOs
export interface CreateRuleSetRequest {
  name: string;
  code: string;
  description?: string;
  category?: string;
  version?: string;
  execution_mode?: ExecutionMode;
  priority?: number;
  effective_from?: string;
  effective_to?: string;
}

export interface CreateRuleRequest {
  name: string;
  code: string;
  description?: string;
  rule_type: RuleType;
  priority?: number;
  execution_order?: number;
  logical_operator?: LogicalOperator;
  stop_on_match?: boolean;
  continue_on_error?: boolean;
  tags?: string[];
  conditions?: Condition[];
  actions?: Action[];
}

export interface CreateDecisionTableRequest {
  name: string;
  code: string;
  description?: string;
  input_columns: any[];
  output_columns: any[];
  hit_policy?: string;
}

export interface ExecuteRuleRequest {
  rule_set_id: string;
  input_data: { [key: string]: any };
  execution_context?: string;
  business_key?: string;
}

export interface ExecuteRuleResponse {
  execution_id: string;
  status: string;
  output_data: { [key: string]: any };
  rules_evaluated: number;
  rules_matched: number;
  actions_executed: number;
  matched_rules: string[];
  execution_time_ms: number;
  error_message?: string;
}

export interface TestRuleResponse {
  matched: boolean;
  conditions_met: string[];
  conditions_failed: string[];
  actions_to_execute: any[];
  output_data: { [key: string]: any };
}

export interface DecisionTableLookupResponse {
  matched: boolean;
  matched_rows: any[];
  output_values: { [key: string]: any };
}

// =====================================================================
// API SERVICE
// =====================================================================

class RulesService {
  private getAuthHeaders() {
    const token = localStorage.getItem('auth_token');
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    };
  }

  // ===================================================================
  // RULE SET MANAGEMENT
  // ===================================================================

  async createRuleSet(data: CreateRuleSetRequest): Promise<any> {
    const response = await axios.post(
      `${API_BASE_URL}${API_PREFIX}/rule-sets/`,
      data,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async listRuleSets(params?: {
    skip?: number;
    limit?: number;
    category?: string;
    status?: RuleStatus;
    search?: string;
  }): Promise<RuleSet[]> {
    const response = await axios.get(
      `${API_BASE_URL}${API_PREFIX}/rule-sets/`,
      { headers: this.getAuthHeaders(), params }
    );
    return response.data;
  }

  async getRuleSet(ruleSetId: string): Promise<RuleSet> {
    const response = await axios.get(
      `${API_BASE_URL}${API_PREFIX}/rule-sets/${ruleSetId}`,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async updateRuleSet(ruleSetId: string, data: Partial<CreateRuleSetRequest>): Promise<any> {
    const response = await axios.put(
      `${API_BASE_URL}${API_PREFIX}/rule-sets/${ruleSetId}`,
      data,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async deleteRuleSet(ruleSetId: string): Promise<any> {
    const response = await axios.delete(
      `${API_BASE_URL}${API_PREFIX}/rule-sets/${ruleSetId}`,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async activateRuleSet(ruleSetId: string): Promise<any> {
    const response = await axios.post(
      `${API_BASE_URL}${API_PREFIX}/rule-sets/${ruleSetId}/activate`,
      {},
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async deactivateRuleSet(ruleSetId: string): Promise<any> {
    const response = await axios.post(
      `${API_BASE_URL}${API_PREFIX}/rule-sets/${ruleSetId}/deactivate`,
      {},
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  // ===================================================================
  // RULE MANAGEMENT
  // ===================================================================

  async createRule(ruleSetId: string, data: CreateRuleRequest): Promise<any> {
    const response = await axios.post(
      `${API_BASE_URL}${API_PREFIX}/rule-sets/${ruleSetId}/rules/`,
      data,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async getRule(ruleId: string): Promise<Rule> {
    const response = await axios.get(
      `${API_BASE_URL}${API_PREFIX}/rules/${ruleId}`,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async updateRule(ruleId: string, data: Partial<CreateRuleRequest>): Promise<any> {
    const response = await axios.put(
      `${API_BASE_URL}${API_PREFIX}/rules/${ruleId}`,
      data,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async deleteRule(ruleId: string): Promise<any> {
    const response = await axios.delete(
      `${API_BASE_URL}${API_PREFIX}/rules/${ruleId}`,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async testRule(ruleId: string, inputData: { [key: string]: any }): Promise<TestRuleResponse> {
    const response = await axios.post(
      `${API_BASE_URL}${API_PREFIX}/rules/${ruleId}/test`,
      { input_data: inputData },
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  // ===================================================================
  // DECISION TABLE MANAGEMENT
  // ===================================================================

  async createDecisionTable(ruleSetId: string, data: CreateDecisionTableRequest): Promise<any> {
    const response = await axios.post(
      `${API_BASE_URL}${API_PREFIX}/rule-sets/${ruleSetId}/decision-tables/`,
      data,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async getDecisionTable(tableId: string): Promise<DecisionTable> {
    const response = await axios.get(
      `${API_BASE_URL}${API_PREFIX}/decision-tables/${tableId}`,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async addTableRow(tableId: string, row: Partial<DecisionTableRow>): Promise<any> {
    const response = await axios.post(
      `${API_BASE_URL}${API_PREFIX}/decision-tables/${tableId}/rows/`,
      row,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async updateTableRow(rowId: string, data: Partial<DecisionTableRow>): Promise<any> {
    const response = await axios.put(
      `${API_BASE_URL}${API_PREFIX}/decision-table-rows/${rowId}`,
      data,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async deleteTableRow(rowId: string): Promise<any> {
    const response = await axios.delete(
      `${API_BASE_URL}${API_PREFIX}/decision-table-rows/${rowId}`,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async lookupDecisionTable(
    tableId: string,
    inputValues: { [key: string]: any }
  ): Promise<DecisionTableLookupResponse> {
    const response = await axios.post(
      `${API_BASE_URL}${API_PREFIX}/decision-tables/lookup`,
      { decision_table_id: tableId, input_values: inputValues },
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  // ===================================================================
  // RULE EXECUTION
  // ===================================================================

  async executeRuleSet(request: ExecuteRuleRequest): Promise<ExecuteRuleResponse> {
    const response = await axios.post(
      `${API_BASE_URL}${API_PREFIX}/execute`,
      request,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async getExecutionHistory(params?: {
    rule_set_id?: string;
    business_key?: string;
    skip?: number;
    limit?: number;
  }): Promise<RuleExecution[]> {
    const response = await axios.get(
      `${API_BASE_URL}${API_PREFIX}/executions/`,
      { headers: this.getAuthHeaders(), params }
    );
    return response.data;
  }

  // ===================================================================
  // VERSIONING
  // ===================================================================

  async createVersion(ruleSetId: string, versionName: string, description?: string): Promise<any> {
    const response = await axios.post(
      `${API_BASE_URL}${API_PREFIX}/rule-sets/${ruleSetId}/versions/`,
      null,
      {
        headers: this.getAuthHeaders(),
        params: { version_name: versionName, description }
      }
    );
    return response.data;
  }

  async listVersions(ruleSetId: string): Promise<any[]> {
    const response = await axios.get(
      `${API_BASE_URL}${API_PREFIX}/rule-sets/${ruleSetId}/versions/`,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  // ===================================================================
  // ANALYTICS
  // ===================================================================

  async getRuleStats(): Promise<RuleStats> {
    const response = await axios.get(
      `${API_BASE_URL}${API_PREFIX}/stats`,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async getDashboardSummary(): Promise<any> {
    const response = await axios.get(
      `${API_BASE_URL}${API_PREFIX}/dashboard`,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }
}

// Export singleton instance
const rulesService = new RulesService();
export default rulesService;
