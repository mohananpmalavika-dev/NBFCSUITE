/**
 * Accounting Service
 * API calls for accounting management including TDS, GST, and Asset Management
 */

import { apiClient } from '@/lib/api-client'
import type { 
  ChartOfAccount,
  JournalEntry,
  PaginatedResponse,
  PaginationParams 
} from '@/types'

// ============================================
// TDS Types
// ============================================
export interface TDSSection {
  id: number
  section_code: string
  section_name: string
  financial_year: number
  tds_rate: number
  threshold_limit?: number
  rate_without_pan?: number
  description?: string
  is_active: boolean
}

export interface TDSDeduction {
  id: number
  deduction_number: string
  deduction_date: string
  section_code: string
  deductee_name: string
  deductee_pan?: string
  gross_amount: number
  tds_amount: number
  total_tds: number
  net_amount: number
  payment_status: string
}

export interface TDSChallan {
  id: number
  challan_number: string
  payment_date: string
  total_tds_amount: number
  bsr_code: string
  bank_name: string
  payment_status: string
}

export interface TDSCertificate {
  id: number
  certificate_number: string
  issue_date: string
  deductee_name: string
  deductee_pan: string
  total_gross_amount: number
  total_tds_amount: number
  status: string
}

// ============================================
// GST Types
// ============================================
export interface GSTConfiguration {
  id: number
  gstin: string
  legal_name: string
  state_name: string
  registration_type: string
}

export interface GSTTransaction {
  id: number
  transaction_number: string
  transaction_date: string
  transaction_type: string
  party_name: string
  taxable_amount: number
  total_gst: number
  total_amount: number
}

export interface HSNSAC {
  id: number
  code: string
  code_type: string
  description: string
  cgst_rate: number
  sgst_rate: number
  igst_rate: number
}

// ============================================
// Asset Types
// ============================================
export interface FixedAsset {
  id: number
  asset_code: string
  asset_name: string
  category: string
  purchase_date: string
  purchase_cost: number
  depreciation_method: string
  accumulated_depreciation: number
  written_down_value: number
  status: string
}

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

// Export NPA service for convenience
export { npaService } from './npa.service'

// ============================================
// TDS Service Methods
// ============================================
export const tdsService = {
  // TDS Sections
  async getSections(financial_year: number) {
    return apiClient.get<{ data: { sections: TDSSection[] } }>(`/accounting/tds/sections`, { 
      params: { financial_year } 
    })
  },

  async createSection(data: Partial<TDSSection>) {
    return apiClient.post('/accounting/tds/sections', data)
  },

  // TDS Calculation
  async calculateTDS(data: {
    section_code: string
    gross_amount: number
    financial_year: number
    has_pan?: boolean
  }) {
    return apiClient.post('/accounting/tds/calculate', data)
  },

  // TDS Deductions
  async getDeductions(params?: PaginationParams & {
    financial_year?: number
    quarter?: number
    section_code?: string
    payment_status?: string
    from_date?: string
    to_date?: string
  }) {
    return apiClient.get<Pag inatedResponse<TDSDeduction>>('/accounting/tds/deductions', { params })
  },

  async recordDeduction(data: {
    section_code: string
    deduction_date: string
    deductee_type: string
    deductee_id: number
    deductee_name: string
    deductee_pan?: string
    transaction_type: string
    transaction_id: number
    gross_amount: number
    invoice_number?: string
  }) {
    return apiClient.post('/accounting/tds/deductions', data)
  },

  // TDS Challans
  async createChallan(data: {
    financial_year: number
    quarter: number
    section_code: string
    payment_date: string
    bsr_code: string
    bank_name: string
    total_tds_amount: number
    payment_mode?: string
    transaction_reference?: string
    deduction_ids?: number[]
  }) {
    return apiClient.post('/accounting/tds/challans', data)
  },

  async getPendingDeductions(financial_year: number, quarter: number, section_code?: string) {
    return apiClient.get('/accounting/tds/challans/pending-deductions', {
      params: { financial_year, quarter, section_code }
    })
  },

  // TDS Certificates
  async generateCertificate(data: {
    financial_year: number
    quarter: number
    deductee_id: number
    deductee_type: string
    deductee_name: string
    deductee_pan: string
    deductee_address?: string
    deductor_tan: string
    deductor_pan: string
    deductor_name: string
  }) {
    return apiClient.post('/accounting/tds/certificates/generate', data)
  },

  // TDS Returns
  async prepareReturn(data: {
    financial_year: number
    quarter: number
    return_type?: string
  }) {
    return apiClient.post('/accounting/tds/returns/prepare', data)
  },

  // TDS Reports
  async getSummary(financial_year: number, quarter?: number) {
    return apiClient.get('/accounting/tds/reports/summary', {
      params: { financial_year, quarter }
    })
  },
}

// ============================================
// GST Service Methods
// ============================================
export const gstService = {
  // GST Configuration
  async getConfiguration(gstin: string) {
    return apiClient.get<{ data: GSTConfiguration }>(`/accounting/gst/configuration/${gstin}`)
  },

  async createConfiguration(data: {
    gstin: string
    legal_name: string
    state_code: string
    state_name: string
    address: string
    pincode: string
    registration_date: string
    registration_type?: string
    trade_name?: string
    email?: string
    phone?: string
  }) {
    return apiClient.post('/accounting/gst/configuration', data)
  },

  // HSN/SAC Master
  async getHSNSAC(code: string) {
    return apiClient.get<{ data: HSNSAC }>(`/accounting/gst/hsn-sac/${code}`)
  },

  async createHSNSAC(data: {
    code: string
    code_type: string
    description: string
    cgst_rate: number
    sgst_rate: number
    igst_rate: number
    cess_rate?: number
    category?: string
  }) {
    return apiClient.post('/accounting/gst/hsn-sac', data)
  },

  // GST Calculation
  async calculateGST(data: {
    taxable_amount: number
    hsn_sac_code: string
    is_inter_state: boolean
    is_reverse_charge?: boolean
  }) {
    return apiClient.post('/accounting/gst/calculate', data)
  },

  // GST Transactions
  async getTransactions(params?: PaginationParams & {
    from_date?: string
    to_date?: string
    transaction_type?: string
  }) {
    return apiClient.get<PaginatedResponse<GSTTransaction>>('/accounting/gst/transactions', { params })
  },

  async recordTransaction(data: {
    transaction_date: string
    transaction_type: string
    reference_type: string
    reference_id: number
    party_name: string
    taxable_amount: number
    cgst_amount?: number
    sgst_amount?: number
    igst_amount?: number
    cess_amount?: number
    party_gstin?: string
    party_state?: string
    hsn_sac_code?: string
    invoice_number?: string
    place_of_supply?: string
    is_reverse_charge?: boolean
  }) {
    return apiClient.post('/accounting/gst/transactions', data)
  },

  // Input Tax Credit
  async recordInputCredit(data: {
    supplier_gstin: string
    supplier_name: string
    invoice_number: string
    invoice_date: string
    taxable_amount: number
    cgst_amount?: number
    sgst_amount?: number
    igst_amount?: number
    cess_amount?: number
    transaction_id?: number
  }) {
    return apiClient.post('/accounting/gst/input-credit', data)
  },

  // GST Returns
  async prepareGSTR1(data: {
    gstin: string
    financial_year: number
    month: number
  }) {
    return apiClient.post('/accounting/gst/returns/gstr1', data)
  },

  async prepareGSTR3B(data: {
    gstin: string
    financial_year: number
    month: number
  }) {
    return apiClient.post('/accounting/gst/returns/gstr3b', data)
  },

  // GST Reports
  async getSummary(financial_year: number, month?: number) {
    return apiClient.get('/accounting/gst/reports/summary', {
      params: { financial_year, month }
    })
  },
}

// ============================================
// Asset Management Service Methods
// ============================================
export const assetService = {
  // Asset CRUD
  async getAssets(params?: PaginationParams & {
    category?: string
    status?: string
    location?: string
  }) {
    return apiClient.get<PaginatedResponse<FixedAsset>>('/accounting/assets', { params })
  },

  async getAsset(id: string) {
    return apiClient.get<{ data: FixedAsset }>(`/accounting/assets/${id}`)
  },

  async createAsset(data: {
    asset_name: string
    category: string
    purchase_date: string
    purchase_cost: number
    depreciation_method: string
    depreciation_rate: number
    useful_life_years: number
    salvage_value?: number
    description?: string
    location?: string
    department?: string
    vendor_name?: string
    invoice_number?: string
  }) {
    return apiClient.post('/accounting/assets', data)
  },

  async updateAsset(id: string, data: Partial<FixedAsset>) {
    return apiClient.put(`/accounting/assets/${id}`, data)
  },

  // Depreciation
  async calculateDepreciation(assetId: string, depreciation_date: string) {
    return apiClient.post(`/accounting/assets/${assetId}/depreciation/calculate`, {
      depreciation_date
    })
  },

  async postDepreciation(assetId: string, data: {
    depreciation_date: string
    journal_entry_id?: number
  }) {
    return apiClient.post(`/accounting/assets/${assetId}/depreciation/post`, data)
  },

  async getDepreciationSchedule(params: {
    asset_id?: string
    financial_year?: number
    month?: number
  }) {
    return apiClient.get('/accounting/assets/depreciation/schedule', { params })
  },

  // Asset Transfer
  async transferAsset(assetId: string, data: {
    to_location?: string
    to_department?: string
    to_custodian?: string
    transfer_reason?: string
  }) {
    return apiClient.post(`/accounting/assets/${assetId}/transfer`, data)
  },

  // Asset Disposal
  async disposeAsset(assetId: string, data: {
    disposal_date: string
    disposal_amount: number
    disposal_reason: string
  }) {
    return apiClient.post(`/accounting/assets/${assetId}/dispose`, data)
  },

  // Asset Maintenance
  async recordMaintenance(assetId: string, data: {
    maintenance_date: string
    maintenance_type: string
    description: string
    cost: number
    vendor_name?: string
  }) {
    return apiClient.post(`/accounting/assets/${assetId}/maintenance`, data)
  },

  async getMaintenanceHistory(assetId: string) {
    return apiClient.get(`/accounting/assets/${assetId}/maintenance`)
  },

  // Asset Reports
  async getAssetRegister(params?: {
    category?: string
    location?: string
    status?: string
  }) {
    return apiClient.get('/accounting/assets/reports/register', { params })
  },

  async getDepreciationReport(financial_year: number) {
    return apiClient.get('/accounting/assets/reports/depreciation', {
      params: { financial_year }
    })
  },
}
