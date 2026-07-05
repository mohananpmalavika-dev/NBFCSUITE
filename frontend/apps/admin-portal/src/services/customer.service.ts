/**
 * Customer Service
 * API calls for customer management
 */

import { apiClient } from '@/lib/api-client'
import type { 
  Customer, 
  CreateCustomerRequest,
  PaginatedResponse,
  PaginationParams 
} from '@/types'

export const customerService = {
  /**
   * Get all customers with pagination
   */
  async getCustomers(params?: PaginationParams & { search?: string; status?: string }) {
    return apiClient.get<PaginatedResponse<Customer>>('/customers', { params })
  },

  /**
   * Get customer by ID
   */
  async getCustomer(id: string) {
    return apiClient.get<Customer>(`/customers/${id}`)
  },

  /**
   * Create new customer
   */
  async createCustomer(data: CreateCustomerRequest) {
    return apiClient.post<Customer>('/customers', data)
  },

  /**
   * Update customer
   */
  async updateCustomer(id: string, data: Partial<CreateCustomerRequest>) {
    return apiClient.put<Customer>(`/customers/${id}`, data)
  },

  /**
   * Delete customer (soft delete)
   */
  async deleteCustomer(id: string) {
    return apiClient.delete(`/customers/${id}`)
  },

  /**
   * Search customers
   */
  async searchCustomers(query: string) {
    return apiClient.get<Customer[]>('/customers/search', { 
      params: { q: query } 
    })
  },

  /**
   * Get customer statistics
   */
  async getCustomerStats() {
    return apiClient.get('/customers/statistics')
  },
}
