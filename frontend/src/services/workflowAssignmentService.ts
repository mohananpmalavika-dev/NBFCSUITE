import api from './api';

export interface WorkflowAssignment {
  id?: string;
  assignment_code: string;
  assignment_name: string;
  description: string;
  status: string;
  product_id?: string;
  product_code?: string;
  workflow_template_id?: string;
  stages: ApprovalStage[];
  approval_matrix: ApprovalLevelConfig[];
  maker_checker_rules: MakerCheckerRule[];
  credit_committees: CreditCommitteeConfig[];
  effective_date: string;
  priority: number;
}

export interface ApprovalStage {
  stage_name: string;
  stage_type: string;
  stage_order: number;
  description: string;
  sla_config: SLAConfig;
  approval_levels: ApprovalLevelConfig[];
  assigned_role?: string;
  maker_checker_required: boolean;
  checker_level?: string;
  mandatory: boolean;
}

export interface SLAConfig {
  sla_value: number;
  sla_unit: string;
  warning_threshold_percentage: number;
  escalation_enabled: boolean;
}

export interface ApprovalLevelConfig {
  level: string;
  min_amount?: number;
  max_amount?: number;
  required_approvers: number;
  parallel_approval: boolean;
}

export interface MakerCheckerRule {
  rule_name: string;
  applicable_stages: string[];
  maker_roles: string[];
  checker_level: string;
  checker_roles: string[];
  min_checkers: number;
}

export interface CreditCommitteeConfig {
  committee_type: string;
  committee_name: string;
  min_amount: number;
  max_amount?: number;
  members: CommitteeMember[];
  quorum_count: number;
  sla_config: SLAConfig;
}

export interface CommitteeMember {
  member_role: string;
  member_name?: string;
  is_chairman: boolean;
  voting_rights: boolean;
}

class WorkflowAssignmentService {
  private baseUrl = '/workflow-assignments';

  async createAssignment(assignment: WorkflowAssignment): Promise<WorkflowAssignment> {
    const response = await api.post(this.baseUrl, assignment);
    return response.data;
  }

  async listAssignments(filters?: any): Promise<WorkflowAssignment[]> {
    const response = await api.get(this.baseUrl, { params: filters });
    return response.data;
  }

  async getAssignment(assignmentId: string): Promise<WorkflowAssignment> {
    const response = await api.get(`${this.baseUrl}/${assignmentId}`);
    return response.data;
  }

  async updateAssignment(assignmentId: string, assignment: Partial<WorkflowAssignment>): Promise<WorkflowAssignment> {
    const response = await api.put(`${this.baseUrl}/${assignmentId}`, assignment);
    return response.data;
  }

  async deleteAssignment(assignmentId: string): Promise<void> {
    await api.delete(`${this.baseUrl}/${assignmentId}`);
  }

  async cloneAssignment(assignmentId: string, cloneData: any): Promise<WorkflowAssignment> {
    const response = await api.post(`${this.baseUrl}/${assignmentId}/clone`, cloneData);
    return response.data;
  }

  async activateAssignment(assignmentId: string): Promise<WorkflowAssignment> {
    const response = await api.post(`${this.baseUrl}/${assignmentId}/activate`);
    return response.data;
  }

  async deactivateAssignment(assignmentId: string): Promise<WorkflowAssignment> {
    const response = await api.post(`${this.baseUrl}/${assignmentId}/deactivate`);
    return response.data;
  }

  async getApprovalRouting(assignmentId: string, loanAmount: number): Promise<any> {
    const response = await api.get(`${this.baseUrl}/${assignmentId}/routing`, {
      params: { loan_amount: loanAmount }
    });
    return response.data;
  }

  async getStageAssignments(assignmentId: string): Promise<any[]> {
    const response = await api.get(`${this.baseUrl}/${assignmentId}/stage-assignments`);
    return response.data;
  }

  async getStats(): Promise<any> {
    const response = await api.get(`${this.baseUrl}/stats/summary`);
    return response.data;
  }

  async validateAssignment(assignment: any): Promise<any> {
    const response = await api.post(`${this.baseUrl}/validation/validate`, assignment);
    return response.data;
  }

  async checkAssignmentCode(assignmentCode: string): Promise<any> {
    const response = await api.get(`${this.baseUrl}/validation/check-code/${assignmentCode}`);
    return response.data;
  }
}

export const workflowAssignmentService = new WorkflowAssignmentService();
