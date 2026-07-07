/**
 * AML/CFT Service
 * API service for AML/CFT operations
 */

import { apiClient } from '@/lib/api-client';

export interface TransactionMonitoring {
  id: string;
  transaction_id: string;
  transaction_type: string;
  transaction_date: string;
  customer_id: string;
  customer_name: string;
  transaction_amount: number;
  risk_score: number;
  risk_level: string;
  is_cash_transaction: boolean;
  is_cross_border: boolean;
  customer_is_pep: boolean;
  requires_review: boolean;
  alerts_generated: number;
}

export interface AMLAlert {
  id: string;
  alert_id: string;
  alert_type: string;
  alert_category: string;
  severity: string;
  customer_id: string;
  alert_title: string;
  alert_description: string;
  status: string;
  assigned_to: string | null;
  due_date: string;
  is_overdue: boolean;
  created_at: string;
}

export interface CTRReport {
  id: string;
  ctr_number: string;
  reporting_month: string;
  transaction_date: string;
  transaction_amount: number;
  customer_name: string;
  status: string;
  submitted_to_fiu: boolean;
}

export interface STRReport {
  id: string;
  str_number: string;
  report_date: string;
  customer_name: string;
  suspicious_activity_type: string;
  total_amount_involved: number;
  status: string;
  submitted_to_fiu: boolean;
}

export interface PEPScreening {
  id: string;
  screening_id: string;
  customer_name: string;
  screening_date: string;
  is_pep: boolean;
  pep_category: string | null;
  screening_status: string;
  edd_required: boolean;
  risk_rating: string | null;
}

export interface SanctionScreening {
  id: string;
  screening_id: string;
  customer_name: string;
  screening_date: string;
  is_match_found: boolean;
  match_score: number | null;
  screening_status: string;
  account_blocked: boolean;
}

export interface AMLDashboard {
  total_transactions_monitored: number;
  high_risk_transactions: number;
  cash_transactions: number;
  cross_border_transactions: number;
  total_alerts: number;
  open_alerts: number;
  under_review_alerts: number;
  escalated_alerts: number;
  closed_alerts: number;
  total_ctr_reports: number;
  pending_ctr_reports: number;
  submitted_ctr_reports: number;
  total_str_reports: number;
  pending_str_reports: number;
  submitted_str_reports: number;
  total_pep_screenings: number;
  confirmed_peps: number;
  total_sanction_screenings: number;
  sanction_matches: number;
  alerts_by_type: Record<string, number>;
}

class AMLService {
  private baseUrl = '/aml';

  // Transaction Monitoring
  async getTransactions(params?: any): Promise<TransactionMonitoring[]> {
    const response = await apiClient.get(`${this.baseUrl}/transaction-monitoring`, { params });
    return response.data;
  }

  async getTransaction(id: string): Promise<TransactionMonitoring> {
    const response = await apiClient.get(`${this.baseUrl}/transaction-monitoring/${id}`);
    return response.data;
  }

  async monitorTransaction(data: any): Promise<TransactionMonitoring> {
    const response = await apiClient.post(`${this.baseUrl}/transaction-monitoring`, data);
    return response.data;
  }

  // Alerts
  async getAlerts(params?: any): Promise<AMLAlert[]> {
    const response = await apiClient.get(`${this.baseUrl}/alerts`, { params });
    return response.data;
  }

  async getAlert(id: string): Promise<AMLAlert> {
    const response = await apiClient.get(`${this.baseUrl}/alerts/${id}`);
    return response.data;
  }

  async assignAlert(id: string, assignedTo: string): Promise<AMLAlert> {
    const response = await apiClient.post(`${this.baseUrl}/alerts/${id}/assign`, {
      assigned_to: assignedTo
    });
    return response.data;
  }

  async reviewAlert(id: string, data: any): Promise<AMLAlert> {
    const response = await apiClient.post(`${this.baseUrl}/alerts/${id}/review`, data);
    return response.data;
  }

  async closeAlert(id: string, data: any): Promise<AMLAlert> {
    const response = await apiClient.post(`${this.baseUrl}/alerts/${id}/close`, data);
    return response.data;
  }

  // CTR Reports
  async getCTRReports(params?: any): Promise<CTRReport[]> {
    const response = await apiClient.get(`${this.baseUrl}/ctr`, { params });
    return response.data;
  }

  async getCTRReport(id: string): Promise<CTRReport> {
    const response = await apiClient.get(`${this.baseUrl}/ctr/${id}`);
    return response.data;
  }

  async createCTRReport(data: any): Promise<CTRReport> {
    const response = await apiClient.post(`${this.baseUrl}/ctr`, data);
    return response.data;
  }

  async approveCTR(id: string): Promise<CTRReport> {
    const response = await apiClient.post(`${this.baseUrl}/ctr/${id}/approve`);
    return response.data;
  }

  async autoGenerateCTRs(reportingMonth: string): Promise<any> {
    const response = await apiClient.post(`${this.baseUrl}/ctr/auto-generate`, null, {
      params: { reporting_month: reportingMonth }
    });
    return response.data;
  }

  // STR Reports
  async getSTRReports(params?: any): Promise<STRReport[]> {
    const response = await apiClient.get(`${this.baseUrl}/str`, { params });
    return response.data;
  }

  async getSTRReport(id: string): Promise<STRReport> {
    const response = await apiClient.get(`${this.baseUrl}/str/${id}`);
    return response.data;
  }

  async createSTRReport(data: any): Promise<STRReport> {
    const response = await apiClient.post(`${this.baseUrl}/str`, data);
    return response.data;
  }

  async updateSTRReport(id: string, data: any): Promise<STRReport> {
    const response = await apiClient.put(`${this.baseUrl}/str/${id}`, data);
    return response.data;
  }

  async approveSTR(id: string, data: any): Promise<STRReport> {
    const response = await apiClient.post(`${this.baseUrl}/str/${id}/approve`, data);
    return response.data;
  }

  async submitSTRToFIU(id: string, fiuRef: string): Promise<STRReport> {
    const response = await apiClient.post(`${this.baseUrl}/str/${id}/submit-fiu`, {
      fiu_reference_number: fiuRef
    });
    return response.data;
  }

  // PEP Screening
  async getPEPScreenings(params?: any): Promise<PEPScreening[]> {
    const response = await apiClient.get(`${this.baseUrl}/pep-screening`, { params });
    return response.data;
  }

  async getPEPScreening(id: string): Promise<PEPScreening> {
    const response = await apiClient.get(`${this.baseUrl}/pep-screening/${id}`);
    return response.data;
  }

  async createPEPScreening(data: any): Promise<PEPScreening> {
    const response = await apiClient.post(`${this.baseUrl}/pep-screening`, data);
    return response.data;
  }

  async updatePEPScreening(id: string, data: any): Promise<PEPScreening> {
    const response = await apiClient.put(`${this.baseUrl}/pep-screening/${id}`, data);
    return response.data;
  }

  async completeEDD(id: string, data: any): Promise<PEPScreening> {
    const response = await apiClient.post(`${this.baseUrl}/pep-screening/${id}/complete-edd`, data);
    return response.data;
  }

  // Sanction Screening
  async getSanctionScreenings(params?: any): Promise<SanctionScreening[]> {
    const response = await apiClient.get(`${this.baseUrl}/sanction-screening`, { params });
    return response.data;
  }

  async getSanctionScreening(id: string): Promise<SanctionScreening> {
    const response = await apiClient.get(`${this.baseUrl}/sanction-screening/${id}`);
    return response.data;
  }

  async createSanctionScreening(data: any): Promise<SanctionScreening> {
    const response = await apiClient.post(`${this.baseUrl}/sanction-screening`, data);
    return response.data;
  }

  async updateSanctionScreening(id: string, data: any): Promise<SanctionScreening> {
    const response = await apiClient.put(`${this.baseUrl}/sanction-screening/${id}`, data);
    return response.data;
  }

  // Dashboard
  async getDashboardStats(): Promise<AMLDashboard> {
    const response = await apiClient.get(`${this.baseUrl}/dashboard`);
    return response.data;
  }
}

export const amlService = new AMLService();
