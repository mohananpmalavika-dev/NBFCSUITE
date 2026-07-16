/**
 * Approval Service
 * API service for advanced approval workflows
 */

import api from './api';

export interface ApprovalLevel {
  level: number;
  name: string;
  assigned_users?: number[];
  assigned_roles?: string[];
  approval_type: 'sequential' | 'parallel' | 'any_one' | 'majority' | 'conditional';
  threshold?: number;
  threshold_percentage?: number;
  sla_hours?: number;
  conditions?: any[];
  skip_conditions?: any[];
}

export interface ApprovalChain {
  chain_id: string;
  name: string;
  description?: string;
  entity_type: string;
  levels: ApprovalLevel[];
  overall_type: 'sequential' | 'parallel' | 'any_one' | 'majority';
  maker_checker_enabled: boolean;
  version: number;
}

export interface ApprovalInstance {
  id: number;
  instance_number: string;
  entity_type: string;
  entity_id: number;
  status: string;
  result?: string;
  started_at?: string;
  completed_at?: string;
  approval_levels: any[];
}

class ApprovalService {
  // ==================== APPROVAL CHAINS ====================
  
  async getApprovalChains(entityType?: string) {
    const response = await api.get('/approvals/chains', {
      params: { entity_type: entityType }
    });
    return response.data;
  }

  async getApprovalChain(chainId: string) {
    const response = await api.get(`/approvals/chains/${chainId}`);
    return response.data;
  }

  async createApprovalChain(chain: ApprovalChain) {
    const response = await api.post('/approvals/chains', chain);
    return response.data;
  }

  async updateApprovalChain(chainId: string, chain: ApprovalChain) {
    const response = await api.put(`/approvals/chains/${chainId}`, chain);
    return response.data;
  }

  // ==================== APPROVAL EXECUTION ====================

  async startApproval(data: {
    chain_id: string;
    entity_type: string;
    entity_id: number;
    variables?: Record<string, any>;
  }) {
    const response = await api.post('/approvals/start', data);
    return response.data;
  }

  async processApproval(
    instanceId: number,
    taskId: number,
    data: {
      action: 'approve' | 'reject' | 'delegate' | 'return';
      comments?: string;
      delegate_to?: number;
      return_to_level?: number;
    }
  ) {
    const response = await api.post(
      `/approvals/instances/${instanceId}/tasks/${taskId}/process`,
      data
    );
    return response.data;
  }

  // ==================== APPROVAL STATUS ====================

  async getApprovalStatus(instanceId: number) {
    const response = await api.get(`/approvals/instances/${instanceId}`);
    return response.data;
  }

  async getEntityApprovals(entityType: string, entityId: number) {
    const response = await api.get(`/approvals/entity/${entityType}/${entityId}`);
    return response.data;
  }

  async getMyPendingApprovals(skip = 0, limit = 50) {
    const response = await api.get('/approvals/my-pending', {
      params: { skip, limit }
    });
    return response.data;
  }

  // ==================== TEMPLATES ====================

  async getApprovalTemplates() {
    const response = await api.get('/approvals/templates');
    return response.data;
  }
}

export default new ApprovalService();
