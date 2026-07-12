/**
 * CRM API Service
 * Centralized API calls for CRM Account Management operations
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

// ============================================================================
// INTERFACES
// ============================================================================

export interface CRMAccount {
  id: string;
  account_number: string;
  account_name: string;
  account_type: string;
  status: string;
  industry?: string;
  annual_revenue?: number;
  employee_count?: string;
  
  // Tax & Registration
  pan_number?: string;
  gst_number?: string;
  cin_number?: string;
  registration_number?: string;
  
  // Contact Information
  email?: string;
  phone?: string;
  mobile?: string;
  website?: string;
  
  // Address
  billing_address_line1?: string;
  billing_address_line2?: string;
  billing_city?: string;
  billing_state?: string;
  billing_pincode?: string;
  billing_country?: string;
  
  shipping_address_line1?: string;
  shipping_address_line2?: string;
  shipping_city?: string;
  shipping_state?: string;
  shipping_pincode?: string;
  shipping_country?: string;
  same_as_billing?: string;
  
  // Relationship
  parent_account_id?: string;
  account_owner_id?: string;
  
  // Metrics
  customer_since?: string;
  last_activity_date?: string;
  next_followup_date?: string;
  total_opportunities?: number;
  total_revenue?: number;
  
  // Additional
  description?: string;
  notes?: string;
  tags?: string;
  linkedin_url?: string;
  facebook_url?: string;
  twitter_handle?: string;
  rating?: string;
  priority?: string;
  
  // Timestamps
  created_at: string;
  updated_at?: string;
  is_deleted: boolean;
}

export interface CRMContact {
  id: string;
  contact_number: string;
  account_id: string;
  salutation?: string;
  first_name: string;
  middle_name?: string;
  last_name: string;
  full_name: string;
  
  contact_type: string;
  status: string;
  
  // Job Information
  job_title?: string;
  department?: string;
  role?: string;
  
  // Contact Information
  email?: string;
  phone?: string;
  mobile?: string;
  fax?: string;
  
  // Address
  address_line1?: string;
  address_line2?: string;
  city?: string;
  state?: string;
  pincode?: string;
  country?: string;
  
  // Personal
  date_of_birth?: string;
  anniversary_date?: string;
  
  // Preferences
  preferred_contact_method?: string;
  best_time_to_call?: string;
  email_opt_out?: string;
  
  // Relationship
  reports_to_contact_id?: string;
  contact_owner_id?: string;
  
  // Activity
  last_contacted_date?: string;
  next_followup_date?: string;
  
  // Additional
  description?: string;
  notes?: string;
  tags?: string;
  linkedin_url?: string;
  twitter_handle?: string;
  
  // Timestamps
  created_at: string;
  updated_at?: string;
  is_deleted: boolean;
}

export interface CRMAccountRelationship {
  id: string;
  primary_account_id: string;
  related_account_id: string;
  relationship_type: string;
  relationship_description?: string;
  strength?: string;
  is_active?: string;
  start_date?: string;
  end_date?: string;
  notes?: string;
  created_at: string;
  updated_at?: string;
  is_deleted: boolean;
}

export interface CRMActivity {
  id: string;
  activity_type: string;
  subject: string;
  description?: string;
  account_id?: string;
  contact_id?: string;
  activity_date: string;
  duration_minutes?: string;
  location?: string;
  status: string;
  priority?: string;
  outcome?: string;
  follow_up_required?: string;
  follow_up_date?: string;
  activity_owner_id?: string;
  notes?: string;
  attachments?: string;
  created_at: string;
  updated_at?: string;
}

export interface Account360View {
  account: CRMAccount;
  contacts: CRMContact[];
  relationships: CRMAccountRelationship[];
  recent_activities: CRMActivity[];
  child_accounts: CRMAccount[];
  metrics: {
    total_contacts: number;
    total_relationships: number;
    total_child_accounts: number;
    opportunities_count: number;
    total_revenue: number;
  };
}

export interface AccountListParams {
  skip?: number;
  limit?: number;
  search?: string;
  status?: string;
  account_type?: string;
  account_owner_id?: string;
}

export interface AccountListResponse {
  success: boolean;
  data: {
    accounts: CRMAccount[];
    total: number;
    page: number;
    page_size: number;
    total_pages: number;
  };
}

export interface ContactListParams {
  skip?: number;
  limit?: number;
  search?: string;
  account_id?: string;
  status?: string;
  contact_type?: string;
}

export interface ContactListResponse {
  success: boolean;
  data: {
    contacts: CRMContact[];
    total: number;
    page: number;
    page_size: number;
    total_pages: number;
  };
}

export interface RelationshipListParams {
  skip?: number;
  limit?: number;
  account_id?: string;
}

export interface RelationshipListResponse {
  success: boolean;
  data: {
    relationships: CRMAccountRelationship[];
    total: number;
    page: number;
    page_size: number;
    total_pages: number;
  };
}

export interface AccountCreateData {
  account_name: string;
  account_type?: string;
  status?: string;
  industry?: string;
  annual_revenue?: number;
  employee_count?: string;
  pan_number?: string;
  gst_number?: string;
  cin_number?: string;
  email?: string;
  phone?: string;
  mobile?: string;
  website?: string;
  billing_address_line1?: string;
  billing_city?: string;
  billing_state?: string;
  billing_pincode?: string;
  description?: string;
}

export interface ContactCreateData {
  account_id: string;
  first_name: string;
  middle_name?: string;
  last_name: string;
  salutation?: string;
  contact_type?: string;
  status?: string;
  job_title?: string;
  department?: string;
  email?: string;
  phone?: string;
  mobile?: string;
}

export interface RelationshipCreateData {
  primary_account_id: string;
  related_account_id: string;
  relationship_type: string;
  relationship_description?: string;
  strength?: string;
  start_date?: string;
}

// ============================================================================
// ACCOUNT APIs
// ============================================================================

export const accountApi = {
  // List accounts with filters
  list: (params: AccountListParams = {}) => {
    const query = new URLSearchParams();
    if (params.skip !== undefined) query.append('skip', params.skip.toString());
    if (params.limit !== undefined) query.append('limit', params.limit.toString());
    if (params.search) query.append('search', params.search);
    if (params.status) query.append('status', params.status);
    if (params.account_type) query.append('account_type', params.account_type);
    if (params.account_owner_id) query.append('account_owner_id', params.account_owner_id);
    
    return apiRequest<AccountListResponse>(`/api/v1/crm/accounts?${query}`);
  },

  // Get single account
  get: (id: string) => {
    return apiRequest<{ success: boolean; data: CRMAccount }>(`/api/v1/crm/accounts/${id}`);
  },

  // Get account 360 view
  get360: (id: string) => {
    return apiRequest<{ success: boolean; data: Account360View }>(`/api/v1/crm/accounts/${id}/360`);
  },

  // Create account
  create: (data: AccountCreateData) => {
    return apiRequest<{ success: boolean; message: string; data: CRMAccount }>(`/api/v1/crm/accounts`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  // Update account
  update: (id: string, data: Partial<AccountCreateData>) => {
    return apiRequest<{ success: boolean; message: string; data: CRMAccount }>(`/api/v1/crm/accounts/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  },

  // Delete account (soft delete)
  delete: (id: string) => {
    return apiRequest<{ success: boolean; message: string }>(`/api/v1/crm/accounts/${id}`, {
      method: "DELETE",
    });
  },
};

// ============================================================================
// CONTACT APIs
// ============================================================================

export const contactApi = {
  // List contacts with filters
  list: (params: ContactListParams = {}) => {
    const query = new URLSearchParams();
    if (params.skip !== undefined) query.append('skip', params.skip.toString());
    if (params.limit !== undefined) query.append('limit', params.limit.toString());
    if (params.search) query.append('search', params.search);
    if (params.account_id) query.append('account_id', params.account_id);
    if (params.status) query.append('status', params.status);
    if (params.contact_type) query.append('contact_type', params.contact_type);
    
    return apiRequest<ContactListResponse>(`/api/v1/crm/accounts/contacts?${query}`);
  },

  // Get single contact
  get: (id: string) => {
    return apiRequest<{ success: boolean; data: CRMContact }>(`/api/v1/crm/accounts/contacts/${id}`);
  },

  // Create contact
  create: (data: ContactCreateData) => {
    return apiRequest<{ success: boolean; message: string; data: CRMContact }>(`/api/v1/crm/accounts/contacts`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  // Update contact
  update: (id: string, data: Partial<ContactCreateData>) => {
    return apiRequest<{ success: boolean; message: string; data: CRMContact }>(`/api/v1/crm/accounts/contacts/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  },

  // Delete contact (soft delete)
  delete: (id: string) => {
    return apiRequest<{ success: boolean; message: string }>(`/api/v1/crm/accounts/contacts/${id}`, {
      method: "DELETE",
    });
  },
};

// ============================================================================
// RELATIONSHIP APIs
// ============================================================================

export const relationshipApi = {
  // List relationships
  list: (params: RelationshipListParams = {}) => {
    const query = new URLSearchParams();
    if (params.skip !== undefined) query.append('skip', params.skip.toString());
    if (params.limit !== undefined) query.append('limit', params.limit.toString());
    if (params.account_id) query.append('account_id', params.account_id);
    
    return apiRequest<RelationshipListResponse>(`/api/v1/crm/accounts/relationships?${query}`);
  },

  // Create relationship
  create: (data: RelationshipCreateData) => {
    return apiRequest<{ success: boolean; message: string; data: CRMAccountRelationship }>(`/api/v1/crm/accounts/relationships`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  // Update relationship
  update: (id: string, data: Partial<RelationshipCreateData>) => {
    return apiRequest<{ success: boolean; message: string; data: CRMAccountRelationship }>(`/api/v1/crm/accounts/relationships/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  },

  // Delete relationship (soft delete)
  delete: (id: string) => {
    return apiRequest<{ success: boolean; message: string }>(`/api/v1/crm/accounts/relationships/${id}`, {
      method: "DELETE",
    });
  },
};

// Export all APIs
export const crmApi = {
  accounts: accountApi,
  contacts: contactApi,
  relationships: relationshipApi,
};

export default crmApi;
