/**
 * Accounting Service
 * API calls for accounting management
 */

import { apiClient } from '@/lib/api-client'
import type { 
  ChartOfAccount,
  JournalEntry,
  PaginatedResponse,
  PaginationParams 
} from '@/types'

export const accountingService = {
  // ============================================
  // Chart of Accounts
  // ============================================

  async getAccounts(params?: PaginationParams & { 
    account_type?: string
    is_active?: boolean
    is_group?: boolean 
  }) {
    return apiClient.get<PaginatedResponse<ChartOfAccount>>('/accounting/accounts', { params })
  },

  async getAccount(id: string) {
    return apiClient.get<ChartOfAccount>(`/accounting/accounts/${id}`)
  },

  async getAccountByCode(code: string) {
    return apiClient.get<ChartOfAccount>(`/accounting/accounts/code/${code}`)
  },

  async createAccount(data: any) {
    return apiClient.post<ChartOfAccount>('/accounting/accounts', data)
  },

  async updateAccount(id: string, data: any) {
    return apiClient.put<ChartOfAccount>(`/accounting/accounts/${id}`, data)
  },

  async getAccountHierarchy() {
    return apiClient.get('/accounting/accounts/hierarchy/tree')
  },

  // ============================================
  // Journal Entries
  // ============================================

  async getJournalEntries(params?: PaginationParams & { 
    status?: string
    entry_type?: string
    from_date?: string
    to_date?: string
    reference_type?: string 
  }) {
    return apiClient.get<PaginatedResponse<JournalEntry>>('/accounting/journal-entries', { params })
  },

  async getJournalEntry(id: string) {
    return apiClient.get<JournalEntry>(`/accounting/journal-entries/${id}`)
  },

  async getJournalEntryByNumber(entryNumber: string) {
    return apiClient.get<JournalEntry>(`/accounting/journal-entries/number/${entryNumber}`)
  },

  async createJournalEntry(data: any) {
    return apiClient.post<JournalEntry>('/accounting/journal-entries', data)
  },

  async postJournalEntry(id: string, postingDate?: string) {
    return apiClient.post<JournalEntry>(`/accounting/journal-entries/${id}/post`, { 
      posting_date: postingDate 
    })
  },

  async reverseJournalEntry(id: string, data: { reversal_date: string; narration: string }) {
    return apiClient.post<JournalEntry>(`/accounting/journal-entries/${id}/reverse`, data)
  },

  // ============================================
  // General Ledger
  // ============================================

  async getGeneralLedger(params?: PaginationParams & { 
    account_id?: string
    account_code?: string
    from_date?: string
    to_date?: string
    financial_year?: number 
  }) {
    return apiClient.get('/accounting/general-ledger', { params })
  },

  async getAccountStatement(data: { 
    account_id: string
    from_date: string
    to_date: string 
  }) {
    return apiClient.post('/accounting/general-ledger/account-statement', data)
  },

  // ============================================
  // Reports
  // ============================================

  async getTrialBalance(data: { balance_date: string; account_type?: string }) {
    return apiClient.post('/accounting/trial-balance', data)
  },

  async getProfitLoss(data: { from_date: string; to_date: string }) {
    return apiClient.post('/accounting/reports/profit-loss', data)
  },

  async getBalanceSheet(data: { as_of_date: string }) {
    return apiClient.post('/accounting/reports/balance-sheet', data)
  },

  // ============================================
  // Statistics
  // ============================================

  async getStatistics() {
    return apiClient.get('/accounting/statistics')
  },
}
