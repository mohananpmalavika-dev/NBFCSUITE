/**
 * Deposit Service
 * API calls for deposit management
 */

import { apiClient } from '@/lib/api-client'
import type { 
  DepositProduct,
  DepositAccount,
  PaginatedResponse,
  PaginationParams 
} from '@/types'

export const depositService = {
  // ============================================
  // Deposit Products
  // ============================================

  async getProducts(params?: PaginationParams & { deposit_type?: string }) {
    return apiClient.get<PaginatedResponse<DepositProduct>>('/deposit-products', { params })
  },

  async getProduct(id: string) {
    return apiClient.get<DepositProduct>(`/deposit-products/${id}`)
  },

  // ============================================
  // Deposit Accounts
  // ============================================

  async getAccounts(params?: PaginationParams & { 
    status?: string
    customer_id?: string
    deposit_type?: string 
  }) {
    return apiClient.get<PaginatedResponse<DepositAccount>>('/deposit-accounts', { params })
  },

  async getAccount(id: string) {
    return apiClient.get<DepositAccount>(`/deposit-accounts/${id}`)
  },

  async createAccount(data: any) {
    return apiClient.post<DepositAccount>('/deposit-accounts', data)
  },

  async updateAccount(id: string, data: any) {
    return apiClient.put<DepositAccount>(`/deposit-accounts/${id}`, data)
  },

  async closeAccount(id: string, remarks?: string) {
    return apiClient.post(`/deposit-accounts/${id}/close`, { remarks })
  },

  // ============================================
  // Transactions
  // ============================================

  async getTransactions(accountId: string, params?: PaginationParams) {
    return apiClient.get(`/deposit-accounts/${accountId}/transactions`, { params })
  },

  async deposit(accountId: string, data: { amount: number; payment_mode: string; remarks?: string }) {
    return apiClient.post(`/deposit-accounts/${accountId}/deposit`, data)
  },

  async withdraw(accountId: string, data: { amount: number; payment_mode: string; remarks?: string }) {
    return apiClient.post(`/deposit-accounts/${accountId}/withdraw`, data)
  },

  // ============================================
  // Statistics
  // ============================================

  async getDepositStats() {
    return apiClient.get('/deposits/statistics')
  },

  // ============================================
  // Reports & Analytics (NEW)
  // ============================================

  async getReportsDashboard() {
    return apiClient.get('/deposit/reports/dashboard')
  },

  async getDepositSummary(params?: { start_date?: string; end_date?: string }) {
    return apiClient.get('/deposit/reports/summary', { params })
  },

  async getMaturityCalendar(days: number = 30) {
    return apiClient.get('/deposit/reports/maturity-calendar', { params: { days } })
  },

  async getInterestAccrualReport(params: { start_date: string; end_date: string }) {
    return apiClient.get('/deposit/reports/interest-accrual', { params })
  },

  async getAgingAnalysis() {
    return apiClient.get('/deposit/reports/aging-analysis')
  },

  async getProductPerformance() {
    return apiClient.get('/deposit/reports/product-performance')
  },

  async getDormancyReport() {
    return apiClient.get('/deposit/reports/dormancy-report')
  },

  async getTDSSummary(params?: { financial_year?: string; quarter?: number }) {
    return apiClient.get('/deposit/reports/tds-summary', { params })
  },

  async getTransactionVolume(params: { start_date: string; end_date: string }) {
    return apiClient.get('/deposit/reports/transaction-volume', { params })
  },

  async getCustomerSummary(customerId: string) {
    return apiClient.get(`/deposit/reports/customer-summary/${customerId}`)
  },

  // ============================================
  // Passbook (NEW)
  // ============================================

  async getPassbookEntries(accountId: number, params?: PaginationParams) {
    return apiClient.get(`/deposit/passbook/${accountId}/entries`, { params })
  },

  async markPassbookPrinted(accountId: number, data: { entry_ids: number[]; page_number: number }) {
    return apiClient.post(`/deposit/passbook/${accountId}/mark-printed`, data)
  },

  async generatePassbookPDF(accountId: number) {
    return apiClient.get(`/deposit/passbook/${accountId}/pdf`, { 
      responseType: 'blob' 
    })
  },

  async getPassbookSummary(accountId: number) {
    return apiClient.get(`/deposit/passbook/${accountId}/summary`)
  },

  async issuePassbook(accountId: number) {
    return apiClient.post(`/deposit/passbook/${accountId}/issue`)
  },

  // ============================================
  // Statements (NEW)
  // ============================================

  async generateStatement(data: {
    account_id: number
    start_date: string
    end_date: string
    format: 'pdf' | 'excel' | 'json'
    include_details?: boolean
  }) {
    return apiClient.post('/deposit/statement', data)
  },

  async generateStatementPDF(accountId: number, params: { start_date: string; end_date: string }) {
    return apiClient.get(`/deposit/statement/${accountId}/pdf`, { 
      params,
      responseType: 'blob' 
    })
  },

  async generateStatementExcel(accountId: number, params: { start_date: string; end_date: string }) {
    return apiClient.get(`/deposit/statement/${accountId}/excel`, { 
      params,
      responseType: 'blob' 
    })
  },

  async emailStatement(accountId: number, data: {
    start_date: string
    end_date: string
    email_to: string
    format: 'pdf' | 'excel'
  }) {
    return apiClient.post(`/deposit/statement/${accountId}/email`, data)
  },

  async getQuarterlyStatement(accountId: number, params: { year: number; quarter: number }) {
    return apiClient.get(`/deposit/statement/${accountId}/quarterly`, { 
      params,
      responseType: 'blob' 
    })
  },

  async getAnnualStatement(accountId: number, params: { financial_year: string }) {
    return apiClient.get(`/deposit/statement/${accountId}/annual`, { 
      params,
      responseType: 'blob' 
    })
  },

  // ============================================
  // Certificates (NEW)
  // ============================================

  async generateInterestCertificate(data: {
    account_id: number
    financial_year: string
    certificate_type: 'interest'
  }) {
    return apiClient.post('/deposit/certificate/interest', data)
  },

  async getInterestCertificatePDF(accountId: number, params: { financial_year: string }) {
    return apiClient.get(`/deposit/certificate/${accountId}/interest/pdf`, { 
      params,
      responseType: 'blob' 
    })
  },

  async getTDSCertificate(accountId: number, params: { financial_year: string; quarter?: number }) {
    return apiClient.get(`/deposit/certificate/${accountId}/tds-certificate`, { 
      params,
      responseType: 'blob' 
    })
  },

  async issueCertificate(accountId: number, data: {
    certificate_type: 'interest' | 'tds'
    financial_year: string
    quarter?: number
  }) {
    return apiClient.post(`/deposit/certificate/${accountId}/issue-certificate`, data)
  },

  async getInterestSummary(accountId: number, params: { financial_year: string }) {
    return apiClient.get(`/deposit/certificate/${accountId}/interest-summary`, { params })
  },

  async getQuarterlyTDS(accountId: number, quarter: number, params: { financial_year: string }) {
    return apiClient.get(`/deposit/certificate/${accountId}/quarterly-tds/${quarter}`, { params })
  },

  // ============================================
  // Batch Operations (NEW)
  // ============================================

  async processMaturityBatch(data: {
    maturity_date: string
    auto_renew?: boolean
    dry_run?: boolean
  }) {
    return apiClient.post('/deposit/batch/maturity/process', data)
  },

  async calculateTDSBatch(data: {
    quarter: number
    financial_year: string
    dry_run?: boolean
  }) {
    return apiClient.post('/deposit/batch/tds/calculate', data)
  },

  async checkDormancyBatch(data: {
    check_date: string
    dormancy_period_months?: number
  }) {
    return apiClient.post('/deposit/batch/dormancy/check', data)
  },

  async applyPenaltiesBatch(data: {
    penalty_date: string
    penalty_types?: string[]
  }) {
    return apiClient.post('/deposit/batch/penalties/apply', data)
  },

  async processMISPayoutBatch(data: {
    payout_month: string
    dry_run?: boolean
  }) {
    return apiClient.post('/deposit/batch/mis-payout/process', data)
  },

  async getBatchStatus(jobId: string) {
    return apiClient.get(`/deposit/batch/status/${jobId}`)
  },

  async bulkCloseAccounts(data: {
    account_ids: number[]
    closure_reason: string
    remarks?: string
  }) {
    return apiClient.post('/deposit/batch/bulk/close-accounts', data)
  },

  async scheduleInterestPosting(data: {
    posting_date: string
    account_types?: string[]
  }) {
    return apiClient.post('/deposit/batch/interest/schedule-posting', data)
  },

  async processAutoRenewalBatch(data: {
    maturity_date: string
    product_types?: string[]
  }) {
    return apiClient.post('/deposit/batch/auto-renewal/process', data)
  },

  async executeStandingInstructions(data: {
    execution_date: string
    instruction_types?: string[]
  }) {
    return apiClient.post('/deposit/batch/standing-instructions/execute', data)
  },

  // ============================================
  // Notifications (NEW)
  // ============================================

  async sendNotification(data: {
    account_id: number
    notification_type: string
    channel: 'email' | 'sms' | 'both'
    custom_message?: string
  }) {
    return apiClient.post('/deposit/notifications/send', data)
  },

  async getNotificationTemplates() {
    return apiClient.get('/deposit/notifications/templates')
  },

  async scheduleMaturityReminders(data: {
    days_before: number
    account_types?: string[]
  }) {
    return apiClient.post('/deposit/notifications/maturity-reminders', data)
  },

  // ============================================
  // Standing Instructions (NEW)
  // ============================================

  async getStandingInstructions(accountId: number) {
    return apiClient.get(`/deposit/standing-instructions/${accountId}`)
  },

  async createStandingInstruction(data: {
    account_id: number
    instruction_type: string
    amount?: number
    frequency: string
    start_date: string
    end_date?: string
  }) {
    return apiClient.post('/deposit/standing-instructions', data)
  },

  async updateStandingInstruction(instructionId: number, data: any) {
    return apiClient.put(`/deposit/standing-instructions/${instructionId}`, data)
  },

  async cancelStandingInstruction(instructionId: number) {
    return apiClient.delete(`/deposit/standing-instructions/${instructionId}`)
  },

  // ============================================
  // Advanced Operations (NEW)
  // ============================================

  async freezeAccount(accountId: number, data: {
    freeze_type: 'debit' | 'credit' | 'full'
    reason: string
    reference_number?: string
  }) {
    return apiClient.post(`/deposit/accounts/${accountId}/freeze`, data)
  },

  async unfreezeAccount(accountId: number, data: {
    release_reason: string
  }) {
    return apiClient.post(`/deposit/accounts/${accountId}/unfreeze`, data)
  },

  async markLien(accountId: number, data: {
    lien_amount: number
    lien_reason: string
    reference_type: string
    reference_number: string
  }) {
    return apiClient.post(`/deposit/accounts/${accountId}/lien`, data)
  },

  async releaseLien(accountId: number, lienId: number, data: {
    release_amount?: number
  }) {
    return apiClient.post(`/deposit/accounts/${accountId}/lien/${lienId}/release`, data)
  },

  async transferAccount(accountId: number, data: {
    new_customer_id: string
    transfer_reason: string
    authorization_document?: string
  }) {
    return apiClient.post(`/deposit/accounts/${accountId}/transfer`, data)
  },

  async getJointHolders(accountId: number) {
    return apiClient.get(`/deposit/accounts/${accountId}/joint-holders`)
  },

  async addJointHolder(accountId: number, data: {
    customer_id: string
    holder_type: string
    operation_mode: string
    share_percentage?: number
  }) {
    return apiClient.post(`/deposit/accounts/${accountId}/joint-holders`, data)
  },

  async removeJointHolder(accountId: number, holderId: number, data: {
    removal_reason: string
  }) {
    return apiClient.delete(`/deposit/accounts/${accountId}/joint-holders/${holderId}`, { data })
  },
}
