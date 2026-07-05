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
}
