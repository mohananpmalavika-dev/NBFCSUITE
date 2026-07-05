/**
 * Customer API Service
 * Centralized API calls for customer operations
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Generic fetch wrapper with error handling
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = localStorage.getItem("auth_token");
  
  const config: RequestInit = {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    },
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, config);

  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: "Request failed" }));
    throw new Error(error.detail || error.message || `HTTP ${response.status}`);
  }

  return response.json();
}

// Interfaces
export interface Customer {
  id: number;
  customer_code: string;
  customer_type: string;
  full_name: string;
  first_name?: string;
  middle_name?: string;
  last_name?: string;
  business_name?: string;
  email?: string;
  mobile: string;
  alternate_mobile?: string;
  pan_number?: string;
  aadhaar_number?: string;
  date_of_birth?: string;
  age?: number;
  gender?: string;
  marital_status?: string;
  father_name?: string;
  mother_name?: string;
  kyc_status: string;
  risk_rating: string;
  cibil_score?: number;
  is_active: boolean;
  is_blacklisted: boolean;
  created_at: string;
  updated_at?: string;
}

export interface CustomerListParams {
  page?: number;
  page_size?: number;
  search?: string;
  kyc_status?: string;
  risk_rating?: string;
  is_active?: boolean;
}

export interface CustomerListResponse {
  items: Customer[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface CustomerStats {
  total_customers: number;
  active_customers: number;
  kyc_pending: number;
  kyc_completed: number;
  high_risk_customers: number;
  blacklisted_customers: number;
  new_this_month: number;
  avg_cibil_score?: number;
}

export interface CustomerCreate {
  customer_type: string;
  first_name?: string;
  middle_name?: string;
  last_name?: string;
  business_name?: string;
  email?: string;
  mobile: string;
  alternate_mobile?: string;
  pan_number?: string;
  aadhaar_number?: string;
  date_of_birth?: string;
  gender?: string;
  marital_status?: string;
  father_name?: string;
  mother_name?: string;
}

export interface CustomerUpdate {
  first_name?: string;
  middle_name?: string;
  last_name?: string;
  email?: string;
  mobile?: string;
  alternate_mobile?: string;
  date_of_birth?: string;
  gender?: string;
  marital_status?: string;
  occupation_id?: number;
  industry_id?: number;
  monthly_income?: number;
  current_address_line1?: string;
  current_city_id?: number;
  current_state_id?: number;
  current_pincode?: string;
}

// ============================================================================
// CUSTOMER APIs
// ============================================================================

export const customerApi = {
  // List customers with filters
  list: (params: CustomerListParams = {}) => {
    const query = new URLSearchParams(params as any);
    return apiRequest<CustomerListResponse>(`/api/v1/customers?${query}`);
  },

  // Get single customer
  get: (id: number) => {
    return apiRequest<Customer>(`/api/v1/customers/${id}`);
  },

  // Get customer by code
  getByCode: (code: string) => {
    return apiRequest<Customer>(`/api/v1/customers/code/${code}`);
  },

  // Create customer
  create: (data: CustomerCreate) => {
    return apiRequest<Customer>(`/api/v1/customers`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  // Update customer
  update: (id: number, data: CustomerUpdate) => {
    return apiRequest<Customer>(`/api/v1/customers/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  },

  // Delete customer (soft delete)
  delete: (id: number) => {
    return apiRequest<void>(`/api/v1/customers/${id}`, {
      method: "DELETE",
    });
  },

  // Get dashboard stats
  getStats: () => {
    return apiRequest<CustomerStats>(`/api/v1/customers/stats`);
  },

  // Search customers
  search: (params: { mobile?: string; pan?: string; aadhaar?: string }) => {
    const query = new URLSearchParams(params as any);
    return apiRequest<Customer[]>(`/api/v1/customers/search?${query}`);
  },

  // Blacklist customer
  blacklist: (id: number, reason: string) => {
    return apiRequest<Customer>(`/api/v1/customers/${id}/blacklist?reason=${encodeURIComponent(reason)}`, {
      method: "POST",
    });
  },

  // Unblacklist customer
  unblacklist: (id: number) => {
    return apiRequest<Customer>(`/api/v1/customers/${id}/unblacklist`, {
      method: "POST",
    });
  },

  // Update CIBIL score
  updateCibil: (id: number, score: number) => {
    return apiRequest<Customer>(`/api/v1/customers/${id}/update-cibil?cibil_score=${score}`, {
      method: "POST",
    });
  },
};

export default customerApi;
