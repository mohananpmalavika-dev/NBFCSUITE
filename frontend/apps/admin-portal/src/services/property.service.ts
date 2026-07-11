/**
 * Property & Rent Management Service
 * API calls for property management, leases, rent collection, utilities, and maintenance
 */

import { apiClient } from '@/lib/api-client'
import type { PaginatedResponse, PaginationParams } from '@/types'

// ============================================
// TYPE DEFINITIONS
// ============================================

export interface Property {
  id: number
  property_code: string
  property_name: string
  property_type: string
  address_line1: string
  address_line2?: string
  city: string
  state: string
  country: string
  pincode: string
  landmark?: string
  total_area: number
  area_unit: string
  built_up_area?: number
  carpet_area?: number
  floors_count?: number
  year_built?: number
  ownership_type: string
  owner_name?: string
  owner_contact?: string
  owner_email?: string
  purchase_date?: string
  purchase_value?: number
  current_market_value?: number
  status: string
  occupancy_status: string
  electricity_connection: boolean
  water_connection: boolean
  gas_connection: boolean
  annual_property_tax?: number
  annual_maintenance?: number
  insurance_premium?: number
  caretaker_name?: string
  caretaker_contact?: string
  amenities?: any
  features?: any
  description?: string
  created_at: string
  total_spaces?: number
  active_leases?: number
}

export interface PropertySpace {
  id: number
  space_code: string
  space_name: string
  property_id: number
  property_name?: string
  space_type: string
  floor_number?: number
  unit_number?: string
  area: number
  area_unit: string
  base_rent: number
  maintenance_charges: number
  security_deposit: number
  furnishing_status?: string
  amenities?: any
  status: string
  description?: string
  created_at: string
}

export interface Lease {
  id: number
  lease_number: string
  property_id: number
  property_name?: string
  lease_type: string
  lessee_type: string
  lessee_name: string
  lessee_contact: string
  lessee_email?: string
  lessee_address?: string
  lease_start_date: string
  lease_end_date: string
  lease_duration_months: number
  monthly_rent: number
  maintenance_charges: number
  other_charges: number
  total_monthly_payment: number
  rent_due_day: number
  payment_frequency: string
  security_deposit: number
  escalation_applicable: boolean
  escalation_percentage?: number
  agreement_date: string
  status: string
  allocated_spaces?: any[]
  payment_summary?: any
  created_at: string
}

export interface RentPayment {
  id: number
  payment_number: string
  lease_id: number
  lease_number?: string
  lessee_name?: string
  payment_month: string
  due_date: string
  total_amount: number
  paid_amount: number
  outstanding_amount: number
  payment_status: string
  payment_date?: string
  payment_mode?: string
  days_overdue: number
  created_at: string
}

export interface UtilityBill {
  id: number
  bill_number: string
  property_id: number
  property_name?: string
  utility_type: string
  bill_month: string
  bill_date: string
  due_date: string
  total_amount: number
  paid_amount: number
  payment_status: string
  consumption_units?: number
  provider_name?: string
  consumer_number?: string
  created_at: string
}

export interface PropertyMaintenance {
  id: number
  ticket_number: string
  property_id: number
  property_name?: string
  maintenance_type: string
  issue_description: string
  category?: string
  priority: string
  request_date: string
  status: string
  scheduled_date?: string
  completed_date?: string
  estimated_cost?: number
  actual_cost?: number
  vendor_name?: string
  created_at: string
}

export const propertyService = {
  // ============================================
  // PROPERTIES
  // ============================================

  async getProperties(params?: PaginationParams & {
    search?: string
    property_type?: string
    status?: string
    occupancy_status?: string
    city?: string
    ownership_type?: string
  }) {
    return apiClient.get<PaginatedResponse<Property>>('/properties', { params })
  },

  async getProperty(id: number) {
    return apiClient.get<{ success: boolean; data: Property }>(`/properties/${id}`)
  },

  async createProperty(data: any) {
    return apiClient.post('/properties', data)
  },

  async updateProperty(id: number, data: any) {
    return apiClient.put(`/properties/${id}`, data)
  },

  async deleteProperty(id: number) {
    return apiClient.delete(`/properties/${id}`)
  },

  async getPropertyStatistics() {
    return apiClient.get('/properties/dashboard/statistics')
  },

  // ============================================
  // PROPERTY SPACES
  // ============================================

  async getPropertySpaces(params?: PaginationParams & {
    property_id?: number
    status?: string
    space_type?: string
  }) {
    return apiClient.get<PaginatedResponse<PropertySpace>>('/property-spaces', { params })
  },

  async getPropertySpace(id: number) {
    return apiClient.get<{ success: boolean; data: PropertySpace }>(`/property-spaces/${id}`)
  },

  async createPropertySpace(data: any) {
    return apiClient.post('/property-spaces', data)
  },

  async updatePropertySpace(id: number, data: any) {
    return apiClient.put(`/property-spaces/${id}`, data)
  },

  async getSpaceStatistics() {
    return apiClient.get('/property-spaces/dashboard/statistics')
  },

  // ============================================
  // LEASES
  // ============================================

  async getLeases(params?: PaginationParams & {
    search?: string
    status?: string
    property_id?: number
    lease_type?: string
  }) {
    return apiClient.get<PaginatedResponse<Lease>>('/leases', { params })
  },

  async getLease(id: number) {
    return apiClient.get<{ success: boolean; data: Lease }>(`/leases/${id}`)
  },

  async createLease(data: any) {
    return apiClient.post('/leases', data)
  },

  async updateLease(id: number, data: any) {
    return apiClient.put(`/leases/${id}`, data)
  },

  async terminateLease(id: number, data: { termination_reason: string; termination_date: string }) {
    return apiClient.post(`/leases/${id}/terminate`, data)
  },

  async getLeaseStatistics() {
    return apiClient.get('/leases/dashboard/statistics')
  },

  // ============================================
  // RENT PAYMENTS
  // ============================================

  async getRentPayments(params?: PaginationParams & {
    lease_id?: number
    payment_status?: string
    payment_month?: string
  }) {
    return apiClient.get<PaginatedResponse<RentPayment>>('/rent-payments', { params })
  },

  async createRentPayment(data: any) {
    return apiClient.post('/rent-payments', data)
  },

  async getRentStatistics() {
    return apiClient.get('/rent-payments/dashboard/statistics')
  },

  // ============================================
  // UTILITY BILLS
  // ============================================

  async getUtilityBills(params?: PaginationParams & {
    property_id?: number
    utility_type?: string
    payment_status?: string
  }) {
    return apiClient.get<PaginatedResponse<UtilityBill>>('/utility-bills', { params })
  },

  async createUtilityBill(data: any) {
    return apiClient.post('/utility-bills', data)
  },

  async payUtilityBill(id: number, data: {
    paid_amount: number
    payment_date: string
    payment_mode: string
    payment_reference?: string
  }) {
    return apiClient.post(`/utility-bills/${id}/pay`, data)
  },

  // ============================================
  // MAINTENANCE
  // ============================================

  async getMaintenanceRequests(params?: PaginationParams & {
    property_id?: number
    status?: string
    priority?: string
    maintenance_type?: string
  }) {
    return apiClient.get<PaginatedResponse<PropertyMaintenance>>('/property-maintenance', { params })
  },

  async getMaintenanceRequest(id: number) {
    return apiClient.get<{ success: boolean; data: PropertyMaintenance }>(`/property-maintenance/${id}`)
  },

  async createMaintenanceRequest(data: any) {
    return apiClient.post('/property-maintenance', data)
  },

  async updateMaintenanceRequest(id: number, data: any) {
    return apiClient.put(`/property-maintenance/${id}`, data)
  },

  async getMaintenanceStatistics() {
    return apiClient.get('/property-maintenance/dashboard/statistics')
  },
}
