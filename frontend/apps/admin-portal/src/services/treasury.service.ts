/**
 * Treasury & Cash Management Service
 * API calls for treasury operations
 */

import { apiClient } from '@/lib/api-client'
import type { PaginatedResponse, PaginationParams } from '@/types'

// ============================================
// Types
// ============================================

export interface BankAccount {
  id: number
  tenant_id: number
  account_number: string
  account_name: string
  bank_name: string
  branch_name: string
  ifsc_code: string
  account_type: 'current' | 'savings' | 'overdraft' | 'cash_credit'
  currency: string
  status: 'active' | 'inactive' | 'closed' | 'frozen'
  is_primary: boolean
  opening_balance: number
  current_balance: number
  available_balance: number
  overdraft_limit: number
  minimum_balance: number
  last_reconciled_at?: string
  contact_person?: string
  contact_phone?: string
  contact_email?: string
  notes?: string
  created_at: string
  updated_at: string
}

// Alias for backward compatibility
export type TreasuryBankAccount = BankAccount

export interface BankAccountBalance {
  account_id: number
  account_number: string
  account_name: string
  current_balance: number
  available_balance: number
  minimum_balance: number
  last_updated_at?: string
  status: string
}

export interface BankAccountStatistics {
  total_accounts: number
  active_accounts: number
  inactive_accounts: number
  total_balance: number
  accounts_below_minimum: number
  accounts_by_type: Record<string, number>
  accounts_by_purpose: Record<string, number>
}

export interface BankAccountCreate {
  account_number: string
  account_name: string
  bank_name: string
  branch_name: string
  ifsc_code: string
  account_type: 'current' | 'savings' | 'overdraft' | 'cash_credit'
  currency?: string
  status?: 'active' | 'inactive' | 'closed' | 'frozen'
  is_primary?: boolean
  opening_balance?: number
  current_balance?: number
  available_balance?: number
  overdraft_limit?: number
  minimum_balance?: number
  contact_person?: string
  contact_phone?: string
  contact_email?: string
  notes?: string
}

export interface BankAccountUpdate {
  account_name?: string
  bank_name?: string
  branch_name?: string
  ifsc_code?: string
  account_type?: 'current' | 'savings' | 'overdraft' | 'cash_credit'
  currency?: string
  status?: 'active' | 'inactive' | 'closed' | 'frozen'
  is_primary?: boolean
  current_balance?: number
  available_balance?: number
  overdraft_limit?: number
  minimum_balance?: number
  contact_person?: string
  contact_phone?: string
  contact_email?: string
  notes?: string
}

// Legacy types for backward compatibility
export interface CreateBankAccountData extends BankAccountCreate {
  branch_id?: number
  location?: string
  swift_code?: string
  account_purpose?: string
  maximum_balance?: number
  daily_withdrawal_limit?: number
  monthly_withdrawal_limit?: number
  gl_account_id?: number
  gl_account_code?: string
  documentation?: Record<string, any>
  opening_date?: string
}

export interface UpdateBankAccountData extends BankAccountUpdate {
  branch_id?: number
  location?: string
  account_purpose?: string
  maximum_balance?: number
  daily_withdrawal_limit?: number
  monthly_withdrawal_limit?: number
  gl_account_id?: number
  documentation?: Record<string, any>
}

export interface UpdateBalanceData {
  new_balance: number
  transaction_date: string
  description?: string
  create_journal_entry?: boolean
}

// ============================================
// Treasury Bank Account Service
// ============================================

export const treasuryService = {
  // ============================================
  // Bank Accounts
  // ============================================

  async getBankAccounts(params?: PaginationParams & {
    status?: string
    account_type?: string
    account_purpose?: string
    branch_id?: number
    search?: string
  }) {
    const response = await apiClient.get<PaginatedResponse<BankAccount>>(
      '/treasury/bank-accounts',
      { params }
    )
    return response.data
  },

  async getBankAccount(id: number) {
    const response = await apiClient.get<BankAccount>(`/treasury/bank-accounts/${id}`)
    return response.data
  },

  async createBankAccount(data: BankAccountCreate) {
    const response = await apiClient.post<BankAccount>('/treasury/bank-accounts', data)
    return response.data
  },

  async updateBankAccount(id: number, data: BankAccountUpdate) {
    const response = await apiClient.patch<BankAccount>(`/treasury/bank-accounts/${id}`, data)
    return response.data
  },

  async deleteBankAccount(id: number) {
    const response = await apiClient.delete(`/treasury/bank-accounts/${id}`)
    return response.data
  },

  async getActiveBankAccounts() {
    const response = await apiClient.get<BankAccount[]>('/treasury/bank-accounts/active/list')
    return response.data
  },

  async getBankAccountBalance(id: number) {
    const response = await apiClient.get<BankAccountBalance>(`/treasury/bank-accounts/${id}/balance`)
    return response.data
  },

  async updateBankAccountBalance(id: number, data: UpdateBalanceData) {
    const response = await apiClient.post<BankAccountBalance>(
      `/treasury/bank-accounts/${id}/update-balance`,
      data
    )
    return response.data
  },

  async getBankAccountsByBranch(branchId: number) {
    const response = await apiClient.get<BankAccount[]>(
      `/treasury/bank-accounts/branch/${branchId}/accounts`
    )
    return response.data
  },

  async getBankAccountStatistics() {
    const response = await apiClient.get<BankAccountStatistics>(
      '/treasury/bank-accounts/statistics/summary'
    )
    return response.data
  },

  async bulkCreateBankAccounts(accounts: BankAccountCreate[]) {
    const response = await apiClient.post('/treasury/bank-accounts/bulk/create', { accounts })
    return response.data
  },

  async getBankAccountHistory(id: number, params?: {
    start_date?: string
    end_date?: string
  }) {
    const response = await apiClient.get(`/treasury/bank-accounts/${id}/history`, { params })
    return response.data
  },
}
