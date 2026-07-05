/**
 * Reports Service
 * API calls for reports and analytics
 */

import { apiClient } from '@/lib/api-client'

export const reportsService = {
  // ============================================
  // Loan Reports
  // ============================================

  async getLoanPortfolioReport(params?: { 
    from_date?: string
    to_date?: string 
  }) {
    return apiClient.get('/reports/loan-portfolio', { params })
  },

  async getDisbursementReport(params?: { 
    from_date?: string
    to_date?: string
    product_id?: string 
  }) {
    return apiClient.get('/reports/disbursements', { params })
  },

  async getCollectionReport(params?: { 
    from_date?: string
    to_date?: string
    status?: string 
  }) {
    return apiClient.get('/reports/collections', { params })
  },

  async getNPAReport(params?: { as_of_date?: string }) {
    return apiClient.get('/reports/npa', { params })
  },

  // ============================================
  // Deposit Reports
  // ============================================

  async getDepositPortfolioReport(params?: { 
    from_date?: string
    to_date?: string 
  }) {
    return apiClient.get('/reports/deposit-portfolio', { params })
  },

  async getMaturityReport(params?: { 
    from_date?: string
    to_date?: string 
  }) {
    return apiClient.get('/reports/deposit-maturity', { params })
  },

  // ============================================
  // Customer Reports
  // ============================================

  async getCustomerAcquisitionReport(params?: { 
    from_date?: string
    to_date?: string 
  }) {
    return apiClient.get('/reports/customer-acquisition', { params })
  },

  async getCustomerSegmentationReport() {
    return apiClient.get('/reports/customer-segmentation')
  },

  // ============================================
  // Performance Reports
  // ============================================

  async getPerformanceMetrics(params?: { 
    from_date?: string
    to_date?: string 
  }) {
    return apiClient.get('/reports/performance-metrics', { params })
  },

  async getProductPerformance(params?: { 
    from_date?: string
    to_date?: string 
  }) {
    return apiClient.get('/reports/product-performance', { params })
  },

  // ============================================
  // Analytics
  // ============================================

  async getTrends(params?: { 
    metric?: string
    period?: string
    from_date?: string
    to_date?: string 
  }) {
    return apiClient.get('/analytics/trends', { params })
  },

  async getComparativeAnalysis(params?: { 
    period?: string 
  }) {
    return apiClient.get('/analytics/comparative', { params })
  },
}
