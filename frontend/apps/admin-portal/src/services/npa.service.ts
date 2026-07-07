/**
 * NPA Management Service
 * API calls for NPA classification, provisioning, and reporting
 */

import { apiClient } from '@/lib/api-client'
import type { PaginationParams } from '@/types'

export interface NPAClassificationRequest {
  days_past_due: number
  is_restructured?: boolean
  is_written_off?: boolean
}

export interface NPAClassificationResponse {
  npa_category: string
  days_past_due: number
  is_npa: boolean
  is_sma: boolean
  classification_date: string
}

export interface ProvisioningCalculationRequest {
  outstanding_principal: number
  npa_category: string
  is_secured: boolean
  security_coverage_ratio: number
  existing_provision: number
}

export interface ProvisioningCalculationResponse {
  outstanding_principal: number
  provisioning_rate: number
  required_provision: number
  existing_provision: number
  additional_provision: number
  npa_category: string
}

export interface CreateProvisionRequest {
  loan_account_id: number
  provision_amount: number
  npa_category: string
  as_of_date: string
  narration?: string
}

export interface WriteOffRequest {
  loan_account_id: number
  write_off_amount: number
  provision_available: number
  as_of_date: string
  narration?: string
}

export interface AssetClassificationRegisterRequest {
  as_of_date: string
  category_filter?: string
}

export interface NPAMovementReportRequest {
  from_date: string
  to_date: string
}

export interface VintageAnalysisRequest {
  as_of_date: string
  cohort_by: 'month' | 'quarter' | 'year'
}

export const npaService = {
  // ============================================
  // Classification
  // ============================================

  async classifyAsset(data: NPAClassificationRequest) {
    return apiClient.post<NPAClassificationResponse>('/accounting/npa/classify', data)
  },

  async getLoanClassification(loanAccountId: number, asOfDate?: string) {
    const params = asOfDate ? { as_of_date: asOfDate } : {}
    return apiClient.get(`/accounting/npa/classify/loan/${loanAccountId}`, { params })
  },

  // ============================================
  // Provisioning
  // ============================================

  async calculateProvisioning(data: ProvisioningCalculationRequest) {
    return apiClient.post<ProvisioningCalculationResponse>(
      '/accounting/npa/provisioning/calculate',
      data
    )
  },

  async createProvision(data: CreateProvisionRequest) {
    return apiClient.post('/accounting/npa/provisioning/create', data)
  },

  async reverseProvision(data: {
    loan_account_id: number
    provision_amount: number
    as_of_date: string
    narration?: string
  }) {
    return apiClient.post('/accounting/npa/provisioning/reverse', data)
  },

  async writeOffLoan(data: WriteOffRequest) {
    return apiClient.post('/accounting/npa/write-off', data)
  },

  // ============================================
  // Reports
  // ============================================

  async getAssetClassificationRegister(data: AssetClassificationRegisterRequest) {
    return apiClient.post('/accounting/npa/register', data)
  },

  async getNPASummary(asOfDate?: string) {
    const params = asOfDate ? { as_of_date: asOfDate } : {}
    return apiClient.get('/accounting/npa/summary', { params })
  },

  async getNPAMovementReport(data: NPAMovementReportRequest) {
    return apiClient.post('/accounting/npa/movement-report', data)
  },

  async getVintageAnalysis(data: VintageAnalysisRequest) {
    return apiClient.post('/accounting/npa/vintage-analysis', data)
  },

  // ============================================
  // Regulatory Reports
  // ============================================

  async getRBINPAReturn(asOfDate: string) {
    return apiClient.post('/accounting/npa/reports/rbi-return', { as_of_date: asOfDate })
  },

  async getProvisioningCoverageRatio(asOfDate: string) {
    return apiClient.post('/accounting/npa/reports/provisioning-coverage-ratio', {
      as_of_date: asOfDate,
    })
  },

  // ============================================
  // Batch Processing
  // ============================================

  async runMonthlyClassification(asOfDate: string) {
    return apiClient.post('/accounting/npa/batch/monthly-classification', {
      as_of_date: asOfDate,
    })
  },
}

