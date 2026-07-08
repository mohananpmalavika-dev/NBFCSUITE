/**
 * Grievance & Complaint Management - API Service
 */

import axios from 'axios';
import type {
  Complaint,
  ComplaintChannel,
  ComplaintEscalation,
  OmbudsmanCase,
  ComplaintStatistics,
  ComplaintCreateInput,
  ComplaintUpdateInput,
  ComplaintAssignInput,
  ComplaintAcknowledgeInput,
  ComplaintResolveInput,
  ComplaintCloseInput,
  ComplaintReopenInput,
  EscalationCreateInput,
  OmbudsmanCaseCreateInput,
} from '@/types/grievance';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

class GrievanceService {
  // ============================================================================
  // COMPLAINT ENDPOINTS
  // ============================================================================

  async createComplaint(data: ComplaintCreateInput): Promise<Complaint> {
    const response = await axios.post(`${API_URL}/grievance/complaints`, data);
    return response.data;
  }

  async listComplaints(params?: {
    status?: string;
    priority?: string;
    category?: string;
    channel?: string;
    assigned_to?: number;
    customer_id?: number;
    sla_breach?: boolean;
    search_text?: string;
    skip?: number;
    limit?: number;
  }): Promise<{ complaints: Complaint[]; total: number; skip: number; limit: number }> {
    const response = await axios.get(`${API_URL}/grievance/complaints`, { params });
    return response.data;
  }

  async getComplaint(id: number): Promise<Complaint> {
    const response = await axios.get(`${API_URL}/grievance/complaints/${id}`);
    return response.data;
  }

  async getComplaintByNumber(complaintNumber: string): Promise<Complaint> {
    const response = await axios.get(`${API_URL}/grievance/complaints/number/${complaintNumber}`);
    return response.data;
  }

  async updateComplaint(id: number, data: ComplaintUpdateInput): Promise<Complaint> {
    const response = await axios.put(`${API_URL}/grievance/complaints/${id}`, data);
    return response.data;
  }

  async assignComplaint(id: number, data: ComplaintAssignInput): Promise<Complaint> {
    const response = await axios.post(`${API_URL}/grievance/complaints/${id}/assign`, data);
    return response.data;
  }

  async acknowledgeComplaint(id: number, data: ComplaintAcknowledgeInput): Promise<Complaint> {
    const response = await axios.post(`${API_URL}/grievance/complaints/${id}/acknowledge`, data);
    return response.data;
  }

  async resolveComplaint(id: number, data: ComplaintResolveInput): Promise<Complaint> {
    const response = await axios.post(`${API_URL}/grievance/complaints/${id}/resolve`, data);
    return response.data;
  }

  async closeComplaint(id: number, data: ComplaintCloseInput): Promise<Complaint> {
    const response = await axios.post(`${API_URL}/grievance/complaints/${id}/close`, data);
    return response.data;
  }

  async reopenComplaint(id: number, data: ComplaintReopenInput): Promise<Complaint> {
    const response = await axios.post(`${API_URL}/grievance/complaints/${id}/reopen`, data);
    return response.data;
  }

  async deleteComplaint(id: number): Promise<void> {
    await axios.delete(`${API_URL}/grievance/complaints/${id}`);
  }

  async getComplaintStatistics(): Promise<ComplaintStatistics> {
    const response = await axios.get(`${API_URL}/grievance/complaints/statistics/summary`);
    return response.data;
  }

  // ============================================================================
  // ESCALATION ENDPOINTS
  // ============================================================================

  async createEscalation(data: EscalationCreateInput): Promise<ComplaintEscalation> {
    const response = await axios.post(`${API_URL}/grievance/escalations`, data);
    return response.data;
  }

  async autoEscalateComplaint(complaintId: number, escalatedTo: number): Promise<ComplaintEscalation> {
    const response = await axios.post(
      `${API_URL}/grievance/escalations/auto-escalate/${complaintId}`,
      null,
      { params: { escalated_to: escalatedTo } }
    );
    return response.data;
  }

  async listEscalations(params?: {
    complaint_id?: number;
    escalation_level?: string;
    escalated_to?: number;
    status?: string;
    skip?: number;
    limit?: number;
  }): Promise<{ escalations: ComplaintEscalation[]; total: number }> {
    const response = await axios.get(`${API_URL}/grievance/escalations`, { params });
    return response.data;
  }

  async getEscalation(id: number): Promise<ComplaintEscalation> {
    const response = await axios.get(`${API_URL}/grievance/escalations/${id}`);
    return response.data;
  }

  async acknowledgeEscalation(
    id: number,
    data: { acknowledgement_notes: string }
  ): Promise<ComplaintEscalation> {
    const response = await axios.post(`${API_URL}/grievance/escalations/${id}/acknowledge`, data);
    return response.data;
  }

  async resolveEscalation(
    id: number,
    data: { resolution_notes: string; action_taken: string }
  ): Promise<ComplaintEscalation> {
    const response = await axios.post(`${API_URL}/grievance/escalations/${id}/resolve`, data);
    return response.data;
  }

  async getPendingEscalations(userId?: number): Promise<ComplaintEscalation[]> {
    const response = await axios.get(`${API_URL}/grievance/escalations/pending/list`, {
      params: { user_id: userId },
    });
    return response.data;
  }

  async getSLABreachEscalations(): Promise<ComplaintEscalation[]> {
    const response = await axios.get(`${API_URL}/grievance/escalations/sla-breach/list`);
    return response.data;
  }

  async deleteEscalation(id: number): Promise<void> {
    await axios.delete(`${API_URL}/grievance/escalations/${id}`);
  }

  // ============================================================================
  // OMBUDSMAN ENDPOINTS
  // ============================================================================

  async createOmbudsmanCase(data: OmbudsmanCaseCreateInput): Promise<OmbudsmanCase> {
    const response = await axios.post(`${API_URL}/grievance/ombudsman`, data);
    return response.data;
  }

  async listOmbudsmanCases(params?: {
    status?: string;
    skip?: number;
    limit?: number;
  }): Promise<{ cases: OmbudsmanCase[]; total: number }> {
    const response = await axios.get(`${API_URL}/grievance/ombudsman`, { params });
    return response.data;
  }

  async getOmbudsmanCase(id: number): Promise<OmbudsmanCase> {
    const response = await axios.get(`${API_URL}/grievance/ombudsman/${id}`);
    return response.data;
  }

  async getOmbudsmanCaseByComplaint(complaintId: number): Promise<OmbudsmanCase> {
    const response = await axios.get(`${API_URL}/grievance/ombudsman/complaint/${complaintId}`);
    return response.data;
  }

  async updateOmbudsmanCase(
    id: number,
    data: Partial<OmbudsmanCaseCreateInput>
  ): Promise<OmbudsmanCase> {
    const response = await axios.put(`${API_URL}/grievance/ombudsman/${id}`, data);
    return response.data;
  }

  async submitToOmbudsman(
    id: number,
    data: { submitted_date: string; submission_reference: string }
  ): Promise<OmbudsmanCase> {
    const response = await axios.post(`${API_URL}/grievance/ombudsman/${id}/submit`, data);
    return response.data;
  }

  async scheduleHearing(
    id: number,
    data: { hearing_date: string; bank_representative: string }
  ): Promise<OmbudsmanCase> {
    const response = await axios.post(`${API_URL}/grievance/ombudsman/${id}/schedule-hearing`, data);
    return response.data;
  }

  async recordAward(
    id: number,
    data: { award_date: string; award_details: string; compensation_awarded: number }
  ): Promise<OmbudsmanCase> {
    const response = await axios.post(`${API_URL}/grievance/ombudsman/${id}/award`, data);
    return response.data;
  }

  async closeOmbudsmanCase(id: number): Promise<OmbudsmanCase> {
    const response = await axios.post(`${API_URL}/grievance/ombudsman/${id}/close`);
    return response.data;
  }

  async deleteOmbudsmanCase(id: number): Promise<void> {
    await axios.delete(`${API_URL}/grievance/ombudsman/${id}`);
  }
}

export const grievanceService = new GrievanceService();
