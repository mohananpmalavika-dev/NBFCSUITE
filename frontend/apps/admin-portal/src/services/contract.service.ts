/**
 * Legal Contract Management Service
 * API calls for contract repository, lifecycle management, renewal tracking, and version control
 */

import { apiClient } from '@/lib/api-client'
import type { PaginatedResponse, PaginationParams } from '@/types'

// ============================================
// TYPE DEFINITIONS
// ============================================

export type ContractType = 'vendor' | 'customer' | 'employee' | 'partnership' | 'lease' | 'license' | 'service' | 'nda' | 'sla' | 'other'
export type ContractStatus = 'draft' | 'under_review' | 'pending_approval' | 'approved' | 'active' | 'expired' | 'terminated' | 'renewed' | 'cancelled'
export type RenewalStatus = 'not_required' | 'pending' | 'in_progress' | 'completed' | 'rejected'
export type PartyType = 'primary' | 'secondary' | 'witness' | 'guarantor' | 'legal_representative'

export interface Contract {
  id: string
  tenant_id: string
  contract_number: string
  title: string
  contract_type: ContractType
  description?: string
  status: ContractStatus
  effective_date: string
  expiry_date?: string
  execution_date?: string
  termination_date?: string
  contract_value?: number
  currency: string
  is_renewable: boolean
  auto_renewal: boolean
  renewal_notice_days: number
  renewal_status: RenewalStatus
  current_version: number
  is_latest: boolean
  document_url?: string
  tags: string[]
  custom_fields: Record<string, any>
  alert_before_expiry_days: number
  last_alert_sent?: string
  notes?: string
  created_at: string
  updated_at: string
  
  // Related data
  parties?: ContractParty[]
  documents?: ContractDocument[]
  versions?: ContractVersion[]
  renewals?: ContractRenewal[]
  
  // Computed fields
  days_until_expiry?: number
  is_expiring_soon: boolean
  is_expired: boolean
}

export interface ContractParty {
  id: string
  party_type: PartyType
  party_name: string
  party_designation?: string
  organization_name?: string
  email?: string
  phone?: string
  address?: string
  is_signatory: boolean
  signature_date?: string
  created_at: string
}

export interface ContractDocument {
  id: string
  document_name: string
  document_type?: string
  description?: string
  file_name: string
  file_size?: number
  file_type?: string
  file_url: string
  version: number
  is_confidential: boolean
  uploaded_at: string
}

export interface ContractVersion {
  id: string
  version_number: number
  version_name?: string
  title: string
  description?: string
  contract_value?: number
  effective_date: string
  expiry_date?: string
  document_url: string
  changes_summary?: string
  change_reason?: string
  created_at: string
}

export interface ContractRenewal {
  id: string
  renewal_number: number
  renewal_status: RenewalStatus
  renewal_due_date: string
  renewal_initiated_date?: string
  renewal_completed_date?: string
  new_expiry_date?: string
  new_contract_value?: number
  value_change_percentage?: number
  terms_modified: boolean
  modification_summary?: string
  alert_sent_date?: string
  reminder_count: number
  approval_notes?: string
  notes?: string
  created_at: string
  updated_at: string
}

export interface ContractStatistics {
  total_contracts: number
  active_contracts: number
  expired_contracts: number
  expiring_soon: number
  pending_renewals: number
  total_contract_value: number
  contracts_by_type: Record<string, number>
  contracts_by_status: Record<string, number>
  average_contract_value: number
  renewal_completion_rate: number
}

export interface ContractFilters extends PaginationParams {
  contract_type?: ContractType
  status?: ContractStatus
  renewal_status?: RenewalStatus
  is_renewable?: boolean
  expiring_in_days?: number
  effective_date_from?: string
  effective_date_to?: string
  expiry_date_from?: string
  expiry_date_to?: string
  min_value?: number
  max_value?: number
  tags?: string[]
  search_query?: string
  sort_by?: string
  sort_order?: 'asc' | 'desc'
}

export const contractService = {
  // ============================================
  // CONTRACT CRUD
  // ============================================

  async getContracts(params?: ContractFilters) {
    return apiClient.get<PaginatedResponse<Contract>>('/api/v1/legal/contracts', { params })
  },

  async getContract(id: string) {
    return apiClient.get<{ success: boolean; data: Contract }>(`/api/v1/legal/contracts/${id}`)
  },

  async createContract(data: {
    title: string
    contract_type: ContractType
    description?: string
    effective_date: string
    expiry_date?: string
    execution_date?: string
    contract_value?: number
    currency?: string
    is_renewable?: boolean
    auto_renewal?: boolean
    renewal_notice_days?: number
    document_url?: string
    tags?: string[]
    custom_fields?: Record<string, any>
    alert_before_expiry_days?: number
    notes?: string
  }) {
    return apiClient.post<{ success: boolean; data: Contract }>('/api/v1/legal/contracts', data)
  },

  async updateContract(id: string, data: {
    title?: string
    description?: string
    status?: ContractStatus
    effective_date?: string
    expiry_date?: string
    execution_date?: string
    termination_date?: string
    contract_value?: number
    currency?: string
    is_renewable?: boolean
    auto_renewal?: boolean
    renewal_notice_days?: number
    renewal_status?: RenewalStatus
    document_url?: string
    tags?: string[]
    custom_fields?: Record<string, any>
    alert_before_expiry_days?: number
    notes?: string
  }) {
    return apiClient.patch<{ success: boolean; data: Contract }>(`/api/v1/legal/contracts/${id}`, data)
  },

  async deleteContract(id: string) {
    return apiClient.delete(`/api/v1/legal/contracts/${id}`)
  },

  async getStatistics() {
    return apiClient.get<{ success: boolean; data: ContractStatistics }>('/api/v1/legal/contracts/statistics')
  },

  // ============================================
  // CONTRACT PARTIES
  // ============================================

  async getContractParties(contractId: string) {
    return apiClient.get<{ success: boolean; data: ContractParty[] }>(
      `/api/v1/legal/contracts/${contractId}/parties`
    )
  },

  async addContractParty(contractId: string, data: {
    party_type: PartyType
    party_name: string
    party_designation?: string
    organization_name?: string
    email?: string
    phone?: string
    address?: string
    legal_entity_type?: string
    registration_number?: string
    is_signatory?: boolean
    signature_date?: string
    signature_url?: string
    custom_fields?: Record<string, any>
  }) {
    return apiClient.post<{ success: boolean; data: ContractParty }>(
      `/api/v1/legal/contracts/${contractId}/parties`,
      data
    )
  },

  // ============================================
  // CONTRACT DOCUMENTS
  // ============================================

  async getContractDocuments(contractId: string) {
    return apiClient.get<{ success: boolean; data: ContractDocument[] }>(
      `/api/v1/legal/contracts/${contractId}/documents`
    )
  },

  async addContractDocument(contractId: string, data: {
    document_name: string
    document_type?: string
    description?: string
    file_name: string
    file_size?: number
    file_type?: string
    file_url: string
    file_hash?: string
    version?: number
    tags?: string[]
    is_confidential?: boolean
  }) {
    return apiClient.post<{ success: boolean; data: ContractDocument }>(
      `/api/v1/legal/contracts/${contractId}/documents`,
      data
    )
  },

  // ============================================
  // CONTRACT VERSIONS
  // ============================================

  async getContractVersions(contractId: string) {
    return apiClient.get<{ success: boolean; data: ContractVersion[] }>(
      `/api/v1/legal/contracts/${contractId}/versions`
    )
  },

  // ============================================
  // CONTRACT RENEWALS
  // ============================================

  async getContractRenewals(contractId: string) {
    return apiClient.get<{ success: boolean; data: ContractRenewal[] }>(
      `/api/v1/legal/contracts/${contractId}/renewals`
    )
  },

  async createRenewal(contractId: string, data: {
    renewal_due_date: string
    new_expiry_date?: string
    new_contract_value?: number
    value_change_percentage?: number
    terms_modified?: boolean
    modification_summary?: string
    notes?: string
  }) {
    return apiClient.post<{ success: boolean; data: ContractRenewal }>(
      `/api/v1/legal/contracts/${contractId}/renewals`,
      data
    )
  },

  async updateRenewal(renewalId: string, data: {
    renewal_status?: RenewalStatus
    renewal_initiated_date?: string
    renewal_completed_date?: string
    new_expiry_date?: string
    new_contract_value?: number
    value_change_percentage?: number
    terms_modified?: boolean
    modification_summary?: string
    approval_notes?: string
    notes?: string
  }) {
    return apiClient.patch<{ success: boolean; data: ContractRenewal }>(
      `/api/v1/legal/contracts/renewals/${renewalId}`,
      data
    )
  },

  // ============================================
  // BULK OPERATIONS
  // ============================================

  async bulkUpdateStatus(contractIds: string[], newStatus: ContractStatus) {
    return apiClient.post('/api/v1/legal/contracts/bulk/status-update', {
      contract_ids: contractIds,
      new_status: newStatus,
    })
  },

  // ============================================
  // UTILITY FUNCTIONS
  // ============================================

  getContractTypeLabel(type: ContractType): string {
    const labels: Record<ContractType, string> = {
      vendor: 'Vendor Contract',
      customer: 'Customer Contract',
      employee: 'Employee Contract',
      partnership: 'Partnership Agreement',
      lease: 'Lease Agreement',
      license: 'License Agreement',
      service: 'Service Agreement',
      nda: 'Non-Disclosure Agreement',
      sla: 'Service Level Agreement',
      other: 'Other',
    }
    return labels[type] || type
  },

  getContractStatusLabel(status: ContractStatus): string {
    const labels: Record<ContractStatus, string> = {
      draft: 'Draft',
      under_review: 'Under Review',
      pending_approval: 'Pending Approval',
      approved: 'Approved',
      active: 'Active',
      expired: 'Expired',
      terminated: 'Terminated',
      renewed: 'Renewed',
      cancelled: 'Cancelled',
    }
    return labels[status] || status
  },

  getRenewalStatusLabel(status: RenewalStatus): string {
    const labels: Record<RenewalStatus, string> = {
      not_required: 'Not Required',
      pending: 'Pending',
      in_progress: 'In Progress',
      completed: 'Completed',
      rejected: 'Rejected',
    }
    return labels[status] || status
  },

  getContractStatusColor(status: ContractStatus): string {
    const colors: Record<ContractStatus, string> = {
      draft: 'gray',
      under_review: 'blue',
      pending_approval: 'yellow',
      approved: 'green',
      active: 'green',
      expired: 'red',
      terminated: 'red',
      renewed: 'purple',
      cancelled: 'red',
    }
    return colors[status] || 'gray'
  },

  formatCurrency(amount?: number, currency: string = 'INR'): string {
    if (!amount) return '—'
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 2,
    }).format(amount)
  },

  formatDate(date?: string): string {
    if (!date) return '—'
    return new Date(date).toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  },

  calculateDaysUntilExpiry(expiryDate?: string): number | null {
    if (!expiryDate) return null
    const today = new Date()
    const expiry = new Date(expiryDate)
    const diffTime = expiry.getTime() - today.getTime()
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  },
}
