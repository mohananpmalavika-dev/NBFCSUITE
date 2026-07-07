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
// Cash Position Types
// ============================================

export interface CashPosition {
  id: number
  tenant_id: number
  position_date: string
  branch_id?: number
  branch_name?: string
  account_id?: number
  account_number?: string
  opening_balance: number
  cash_received: number
  cash_paid: number
  bank_deposit: number
  bank_withdrawal: number
  closing_balance: number
  denomination_details?: DenominationBreakup
  vault_location?: string
  recorded_by?: number
  verified_by?: number
  verified_at?: string
  discrepancy_amount: number
  discrepancy_reason?: string
  notes?: string
  status: 'draft' | 'verified' | 'finalized'
  created_at: string
  updated_at: string
}

export interface DenominationBreakup {
  notes_2000: number
  notes_500: number
  notes_200: number
  notes_100: number
  notes_50: number
  notes_20: number
  notes_10: number
  coins_10: number
  coins_5: number
  coins_2: number
  coins_1: number
}

export interface CashPositionCreate {
  position_date: string
  branch_id?: number
  account_id?: number
  opening_balance: number
  cash_received: number
  cash_paid: number
  bank_deposit: number
  bank_withdrawal: number
  closing_balance?: number
  denomination_details?: DenominationBreakup
  vault_location?: string
  verified_by?: number
  verified_at?: string
  discrepancy_amount?: number
  discrepancy_reason?: string
  notes?: string
  status?: 'draft' | 'verified' | 'finalized'
}

export interface CashPositionUpdate {
  opening_balance?: number
  cash_received?: number
  cash_paid?: number
  bank_deposit?: number
  bank_withdrawal?: number
  closing_balance?: number
  denomination_details?: DenominationBreakup
  vault_location?: string
  verified_by?: number
  verified_at?: string
  discrepancy_amount?: number
  discrepancy_reason?: string
  notes?: string
  status?: 'draft' | 'verified' | 'finalized'
}

export interface CashPositionStatistics {
  total_cash_on_hand: number
  total_branches: number
  branches_with_low_cash: number
  branches_with_high_cash: number
  total_cash_received_today: number
  total_cash_paid_today: number
  total_bank_deposits_today: number
  positions_pending_verification: number
  cash_by_branch: Record<string, number>
  denomination_summary?: DenominationBreakup
}

export interface CashMovementSummary {
  date: string
  opening_balance: number
  cash_received: number
  cash_paid: number
  bank_deposit: number
  bank_withdrawal: number
  closing_balance: number
  net_movement: number
}

export interface CashAlert {
  alert_type: 'low_cash' | 'high_cash' | 'discrepancy' | 'pending_verification'
  severity: 'info' | 'warning' | 'critical'
  branch_id?: number
  branch_name?: string
  message: string
  amount?: number
  created_at: string
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

  // ============================================
  // Cash Position
  // ============================================

  async getCashPositions(params?: PaginationParams & {
    branch_id?: number
    status?: string
    start_date?: string
    end_date?: string
  }) {
    const response = await apiClient.get<PaginatedResponse<CashPosition>>(
      '/treasury/cash-position',
      { params }
    )
    return response.data
  },

  async getCashPosition(id: number) {
    const response = await apiClient.get<CashPosition>(`/treasury/cash-position/${id}`)
    return response.data
  },

  async createCashPosition(data: CashPositionCreate) {
    const response = await apiClient.post<CashPosition>('/treasury/cash-position', data)
    return response.data
  },

  async updateCashPosition(id: number, data: CashPositionUpdate) {
    const response = await apiClient.patch<CashPosition>(`/treasury/cash-position/${id}`, data)
    return response.data
  },

  async deleteCashPosition(id: number) {
    const response = await apiClient.delete(`/treasury/cash-position/${id}`)
    return response.data
  },

  async verifyCashPosition(id: number) {
    const response = await apiClient.post<CashPosition>(`/treasury/cash-position/${id}/verify`)
    return response.data
  },

  async finalizeCashPosition(id: number) {
    const response = await apiClient.post<CashPosition>(`/treasury/cash-position/${id}/finalize`)
    return response.data
  },

  async getCurrentCashPosition(branchId?: number) {
    const response = await apiClient.get<CashPosition>(
      '/treasury/cash-position/current/today',
      { params: { branch_id: branchId } }
    )
    return response.data
  },

  async getCashPositionByDate(date: string, branchId?: number) {
    const response = await apiClient.get<CashPosition>(
      `/treasury/cash-position/date/${date}`,
      { params: { branch_id: branchId } }
    )
    return response.data
  },

  async getCashStatistics() {
    const response = await apiClient.get<CashPositionStatistics>(
      '/treasury/cash-position/statistics/summary'
    )
    return response.data
  },

  async getCashMovement(startDate: string, endDate: string, branchId?: number) {
    const response = await apiClient.get<CashMovementSummary[]>(
      '/treasury/cash-position/movement/summary',
      { params: { start_date: startDate, end_date: endDate, branch_id: branchId } }
    )
    return response.data
  },

  async getCashAlerts() {
    const response = await apiClient.get<CashAlert[]>(
      '/treasury/cash-position/alerts/active'
    )
    return response.data
  },

  async calculateDenominationTotal(denomination: DenominationBreakup) {
    const response = await apiClient.post(
      '/treasury/cash-position/denomination/calculate',
      denomination
    )
    return response.data
  },
}


// ============================================
// Bank Reconciliation Types
// ============================================

export type ReconciliationStatus = 
  | 'draft' 
  | 'in_progress' 
  | 'matched' 
  | 'pending_approval' 
  | 'approved' 
  | 'rejected'

export type ReconciliationItemType = 
  | 'outstanding_cheque' 
  | 'deposit_in_transit' 
  | 'bank_charges' 
  | 'interest_earned' 
  | 'direct_debit' 
  | 'direct_credit' 
  | 'error_correction' 
  | 'other'

export interface BankStatement {
  id: number
  tenant_id: number
  bank_account_id: number
  transaction_date: string
  value_date?: string
  transaction_reference?: string
  description: string
  cheque_number?: string
  debit_amount: number
  credit_amount: number
  balance?: number
  import_batch_id?: string
  import_date: string
  imported_by: number
  is_matched: boolean
  matched_gl_entry_id?: number
  matched_at?: string
  matched_by?: number
  created_at: string
}

export interface BankStatementCreate {
  bank_account_id: number
  transaction_date: string
  value_date?: string
  transaction_reference?: string
  description: string
  cheque_number?: string
  debit_amount?: number
  credit_amount?: number
  balance?: number
  import_batch_id?: string
}

export interface BankStatementBulkImport {
  bank_account_id: number
  import_batch_id: string
  statements: BankStatementCreate[]
}


export interface ReconciliationItem {
  id: number
  tenant_id: number
  reconciliation_id: number
  item_type: ReconciliationItemType
  item_date: string
  description: string
  reference_number?: string
  amount: number
  is_debit: boolean
  bank_statement_id?: number
  gl_entry_id?: number
  is_matched: boolean
  is_cleared: boolean
  cleared_date?: string
  notes?: string
  created_at: string
  created_by: number
}

export interface ReconciliationItemCreate {
  item_type: ReconciliationItemType
  item_date: string
  description: string
  reference_number?: string
  amount: number
  is_debit?: boolean
  bank_statement_id?: number
  gl_entry_id?: number
  notes?: string
}

export interface BankReconciliation {
  id: number
  tenant_id: number
  reconciliation_number: string
  reconciliation_date: string
  bank_account_id: number
  period_start_date: string
  period_end_date: string
  book_balance: number
  bank_balance: number
  difference: number
  total_matched: number
  total_unmatched: number
  matched_amount: number
  unmatched_amount: number
  status: ReconciliationStatus
  approved_by?: number
  approved_at?: string
  approval_notes?: string
  notes?: string
  created_at: string
  updated_at: string
  created_by: number
  updated_by?: number
}

export interface BankReconciliationDetail extends BankReconciliation {
  items: ReconciliationItem[]
}

export interface BankReconciliationCreate {
  bank_account_id: number
  reconciliation_date: string
  period_start_date: string
  period_end_date: string
  book_balance: number
  bank_balance: number
  notes?: string
}

export interface ReconciliationStatistics {
  total_reconciliations: number
  draft_count: number
  in_progress_count: number
  matched_count: number
  pending_approval_count: number
  approved_count: number
  rejected_count: number
  total_matched_amount: number
  total_unmatched_amount: number
  average_difference: number
  oldest_unreconciled_date?: string
}

export interface BankStatementSummary {
  bank_account_id: number
  statement_count: number
  matched_count: number
  unmatched_count: number
  total_debit: number
  total_credit: number
  oldest_unmatched_date?: string
}

export interface ReconciliationDifference {
  outstanding_cheques_amount: number
  outstanding_cheques_count: number
  deposits_in_transit_amount: number
  deposits_in_transit_count: number
  bank_charges_amount: number
  bank_charges_count: number
  interest_earned_amount: number
  interest_earned_count: number
  direct_debits_amount: number
  direct_debits_count: number
  direct_credits_amount: number
  direct_credits_count: number
  error_corrections_amount: number
  error_corrections_count: number
  other_amount: number
  other_count: number
  total_difference: number
  total_items: number
}


// Add to treasuryService object (Bank Reconciliation methods)
export const reconciliationService = {
  // ============================================
  // Bank Statements
  // ============================================

  async getBankStatements(params?: PaginationParams & {
    bank_account_id?: number
    is_matched?: boolean
    start_date?: string
    end_date?: string
  }) {
    const response = await apiClient.get<PaginatedResponse<BankStatement>>(
      '/treasury/reconciliation/bank-statements',
      { params }
    )
    return response.data
  },

  async getBankStatement(id: number) {
    const response = await apiClient.get<BankStatement>(
      `/treasury/reconciliation/bank-statements/${id}`
    )
    return response.data
  },

  async createBankStatement(data: BankStatementCreate) {
    const response = await apiClient.post<BankStatement>(
      '/treasury/reconciliation/bank-statements',
      data
    )
    return response.data
  },

  async bulkImportStatements(data: BankStatementBulkImport) {
    const response = await apiClient.post<BankStatement[]>(
      '/treasury/reconciliation/bank-statements/bulk-import',
      data
    )
    return response.data
  },

  async deleteBankStatement(id: number) {
    const response = await apiClient.delete(
      `/treasury/reconciliation/bank-statements/${id}`
    )
    return response.data
  },

  async getBankStatementSummary(bankAccountId: number) {
    const response = await apiClient.get<BankStatementSummary>(
      `/treasury/reconciliation/bank-statements/account/${bankAccountId}/summary`
    )
    return response.data
  },

  // ============================================
  // Bank Reconciliation
  // ============================================

  async getReconciliations(params?: PaginationParams & {
    bank_account_id?: number
    status?: ReconciliationStatus
    start_date?: string
    end_date?: string
  }) {
    const response = await apiClient.get<PaginatedResponse<BankReconciliation>>(
      '/treasury/reconciliation',
      { params }
    )
    return response.data
  },

  async getReconciliation(id: number) {
    const response = await apiClient.get<BankReconciliationDetail>(
      `/treasury/reconciliation/${id}`
    )
    return response.data
  },

  async createReconciliation(data: BankReconciliationCreate) {
    const response = await apiClient.post<BankReconciliation>(
      '/treasury/reconciliation',
      data
    )
    return response.data
  },

  async updateReconciliation(id: number, data: Partial<BankReconciliationCreate>) {
    const response = await apiClient.patch<BankReconciliation>(
      `/treasury/reconciliation/${id}`,
      data
    )
    return response.data
  },

  async deleteReconciliation(id: number) {
    const response = await apiClient.delete(`/treasury/reconciliation/${id}`)
    return response.data
  },

  // ============================================
  // Reconciliation Items
  // ============================================

  async addReconciliationItem(reconciliationId: number, data: ReconciliationItemCreate) {
    const response = await apiClient.post<ReconciliationItem>(
      `/treasury/reconciliation/${reconciliationId}/items`,
      data
    )
    return response.data
  },

  async updateReconciliationItem(itemId: number, data: Partial<ReconciliationItemCreate>) {
    const response = await apiClient.patch<ReconciliationItem>(
      `/treasury/reconciliation/items/${itemId}`,
      data
    )
    return response.data
  },

  async deleteReconciliationItem(itemId: number) {
    const response = await apiClient.delete(
      `/treasury/reconciliation/items/${itemId}`
    )
    return response.data
  },

  // ============================================
  // Matching Operations
  // ============================================

  async matchTransaction(bankStatementId: number, glEntryId?: number) {
    const response = await apiClient.post<BankStatement>(
      '/treasury/reconciliation/match-transaction',
      { bank_statement_id: bankStatementId, gl_entry_id: glEntryId }
    )
    return response.data
  },

  async unmatchTransaction(bankStatementId: number) {
    const response = await apiClient.post<BankStatement>(
      '/treasury/reconciliation/unmatch-transaction',
      { bank_statement_id: bankStatementId }
    )
    return response.data
  },

  async autoMatch(reconciliationId: number, matchTolerance = 0, matchDaysRange = 3) {
    const response = await apiClient.post(
      '/treasury/reconciliation/auto-match',
      { 
        reconciliation_id: reconciliationId,
        match_tolerance: matchTolerance,
        match_days_range: matchDaysRange
      }
    )
    return response.data
  },

  // ============================================
  // Approval Workflow
  // ============================================

  async submitForApproval(id: number) {
    const response = await apiClient.post<BankReconciliation>(
      `/treasury/reconciliation/${id}/submit`
    )
    return response.data
  },

  async approveReconciliation(id: number, approvalNotes?: string) {
    const response = await apiClient.post<BankReconciliation>(
      `/treasury/reconciliation/${id}/approve`,
      { approval_notes: approvalNotes }
    )
    return response.data
  },

  async rejectReconciliation(id: number, approvalNotes: string) {
    const response = await apiClient.post<BankReconciliation>(
      `/treasury/reconciliation/${id}/reject`,
      { approval_notes: approvalNotes }
    )
    return response.data
  },

  // ============================================
  // Statistics & Reports
  // ============================================

  async getReconciliationStatistics() {
    const response = await apiClient.get<ReconciliationStatistics>(
      '/treasury/reconciliation/statistics/summary'
    )
    return response.data
  },

  async getDifferenceBreakdown(id: number) {
    const response = await apiClient.get<ReconciliationDifference>(
      `/treasury/reconciliation/${id}/difference-breakdown`
    )
    return response.data
  },
}
