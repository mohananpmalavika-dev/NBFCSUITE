/**
 * NACH Service
 * API calls for NACH/eNACH mandate and debit management
 */

import { apiClient } from '@/lib/api-client'
import type { PaginatedResponse, PaginationParams } from '@/types'

export interface NACHMandate {
  id: number
  loan_account_id: number
  mandate_number: string
  mandate_type: 'physical' | 'enach'
  bank_account_id: number
  status: 'draft' | 'pending_customer' | 'pending_bank' | 'active' | 'rejected' | 'cancelled' | 'expired' | 'suspended'
  frequency: 'monthly' | 'quarterly' | 'half_yearly' | 'yearly' | 'as_presented'
  max_amount: number
  start_date: string
  end_date: string
  umrn?: string
  enach_request_id?: string
  enach_authentication_url?: string
  approved_at?: string
  rejection_reason?: string
  cancellation_reason?: string
  created_at: string
  updated_at: string
}

export interface CreatePhysicalMandateRequest {
  loan_account_id: number
  bank_account_id: number
  frequency: string
  max_amount: number
  start_date: string
  end_date: string
  physical_form_received?: boolean
  physical_form_number?: string
}

export interface CreateENACHMandateRequest {
  loan_account_id: number
  bank_account_id: number
  frequency: string
  max_amount: number
  start_date: string
  end_date: string
  redirect_url?: string
}

export interface DebitTransaction {
  id: number
  mandate_id: number
  loan_account_id: number
  transaction_reference: string
  debit_amount: number
  debit_date: string
  status: 'initiated' | 'pending' | 'success' | 'failed' | 'reversed'
  bank_reference?: string
  utr_number?: string
  failure_reason?: string
  retry_count: number
  next_retry_date?: string
  created_at: string
}

export interface InitiateDebitRequest {
  mandate_id: number
  repayment_schedule_id: number
  debit_amount: number
  debit_date: string
  purpose: string
}

export interface MandateStatistics {
  total_mandates: number
  active_mandates: number
  pending_mandates: number
  expired_mandates: number
  cancelled_mandates: number
  physical_mandates: number
  enach_mandates: number
  total_max_debit_amount: number
  mandates_expiring_30_days: number
  mandates_expiring_60_days: number
}

export interface DebitStatistics {
  total_transactions: number
  successful_transactions: number
  failed_transactions: number
  pending_transactions: number
  total_debit_amount: number
  total_success_amount: number
  total_failed_amount: number
  success_rate: number
  pending_retry_count: number
}

export const nachService = {
  // ============================================
  // Mandate Management
  // ============================================

  async createPhysicalMandate(data: CreatePhysicalMandateRequest) {
    return apiClient.post<NACHMandate>('/nach/mandates/physical', data)
  },

  async createENACHMandate(data: CreateENACHMandateRequest) {
    return apiClient.post<NACHMandate>('/nach/mandates/enach', data)
  },

  async initiateENACHAuthentication(mandateId: number, redirectUrl: string) {
    return apiClient.post(`/nach/mandates/${mandateId}/initiate-enach`, { redirect_url: redirectUrl })
  },

  async getMandate(id: number) {
    return apiClient.get<NACHMandate>(`/nach/mandates/${id}`)
  },

  async getMandates(params?: PaginationParams & { 
    loan_account_id?: number
    status?: string
    mandate_type?: string
    expiring_before?: string
  }) {
    return apiClient.get<PaginatedResponse<NACHMandate>>('/nach/mandates', { params })
  },

  async getActiveMandateForLoan(loanAccountId: number) {
    return apiClient.get<NACHMandate>(`/nach/mandates/loan/${loanAccountId}/active`)
  },

  async approveMandate(id: number, umrn: string, sponsorBankCode?: string) {
    return apiClient.patch<NACHMandate>(`/nach/mandates/${id}/approve`, {
      umrn,
      sponsor_bank_code: sponsorBankCode
    })
  },

  async rejectMandate(id: number, rejectionReason: string) {
    return apiClient.patch<NACHMandate>(`/nach/mandates/${id}/reject`, {
      rejection_reason: rejectionReason
    })
  },

  async cancelMandate(id: number, cancellationReason: string) {
    return apiClient.patch<NACHMandate>(`/nach/mandates/${id}/cancel`, {
      cancellation_reason: cancellationReason
    })
  },

  async updateMandate(id: number, data: Partial<NACHMandate>) {
    return apiClient.patch<NACHMandate>(`/nach/mandates/${id}`, data)
  },

  // ============================================
  // Debit Transactions
  // ============================================

  async initiateDebit(data: InitiateDebitRequest) {
    return apiClient.post<DebitTransaction>('/nach/debits/initiate', data)
  },

  async bulkInitiateDebits(requests: InitiateDebitRequest[], batchReference?: string) {
    return apiClient.post('/nach/debits/bulk-initiate', {
      debit_requests: requests,
      batch_reference: batchReference
    })
  },

  async getDebitTransaction(id: number) {
    return apiClient.get<DebitTransaction>(`/nach/debits/${id}`)
  },

  async getDebitTransactions(params?: PaginationParams & {
    mandate_id?: number
    loan_account_id?: number
    status?: string
    debit_date_from?: string
    debit_date_to?: string
  }) {
    return apiClient.get<PaginatedResponse<DebitTransaction>>('/nach/debits', { params })
  },

  async processDebitResponse(transactionId: number, response: any) {
    return apiClient.patch<DebitTransaction>(`/nach/debits/${transactionId}/response`, response)
  },

  async retryFailedDebit(transactionId: number, retryDate: string, retryReason: string) {
    return apiClient.post<DebitTransaction>(`/nach/debits/${transactionId}/retry`, {
      retry_date: retryDate,
      retry_reason: retryReason
    })
  },

  async getPendingRetryDebits() {
    return apiClient.get<DebitTransaction[]>('/nach/debits/pending-retry')
  },

  // ============================================
  // Statistics & Dashboard
  // ============================================

  async getMandateStatistics() {
    return apiClient.get<MandateStatistics>('/nach/statistics/mandates')
  },

  async getDebitStatistics(dateFrom?: string, dateTo?: string) {
    return apiClient.get<DebitStatistics>('/nach/statistics/debits', {
      params: { date_from: dateFrom, date_to: dateTo }
    })
  },

  async getDashboard() {
    return apiClient.get('/nach/dashboard')
  },
}
