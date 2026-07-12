/**
 * CRM Account Management Service
 * API client for account, contact, and relationship operations
 */

import api from './api';

// ============================================================================
// TYPES
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
  
  // Contact
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
  
  // Relations
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
  
  // Social
  linkedin_url?: string;
  facebook_url?: string;
  twitter_handle?: string;
  
  rating?: string;
  priority?: string;
  
  // Audit
  tenant_id: string;
  created_at: string;
  updated_at: string;
  created_by?: string;
  updated_by?: string;
  is_deleted: boolean;
}

export interface CRMAccountCreate {
  account_name: string;
  account_type?: string;
  status?: string;
  industry?: string;
  annual_revenue?: number;
  employee_count?: string;
  pan_number?: string;
  gst_number?: string;
  cin_number?: string;
  registration_number?: string;
  email?: string;
  phone?: string;
  mobile?: string;
  website?: string;
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
  parent_account_id?: string;
  account_owner_id?: string;
  customer_since?: string;
  description?: string;
  notes?: string;
  tags?: string;
  linkedin_url?: string;
  facebook_url?: string;
  twitter_handle?: string;
  rating?: string;
  priority?: string;
}

export interface CRMAccountUpdate extends Partial<CRMAccountCreate> {}

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
  
  // Job
  job_title?: string;
  department?: string;
  role?: string;
  
  // Contact Info
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
  
  // Relations
  reports_to_contact_id?: string;
  contact_owner_id?: string;
  
  // Activity
  last_contacted_date?: string;
  next_followup_date?: string;
  
  // Additional
  description?: string;
  notes?: string;
  tags?: string;
  
  // Social
  linkedin_url?: string;
  twitter_handle?: string;
  
  // Audit
  tenant_id: string;
  created_at: string;
  updated_at: string;
  created_by?: string;
  updated_by?: string;
  is_deleted: boolean;
}

export interface CRMContactCreate {
  account_id: string;
  salutation?: string;
  first_name: string;
  middle_name?: string;
  last_name: string;
  contact_type?: string;
  status?: string;
  job_title?: string;
  department?: string;
  role?: string;
  email?: string;
  phone?: string;
  mobile?: string;
  fax?: string;
  address_line1?: string;
  address_line2?: string;
  city?: string;
  state?: string;
  pincode?: string;
  country?: string;
  date_of_birth?: string;
  anniversary_date?: string;
  preferred_contact_method?: string;
  best_time_to_call?: string;
  email_opt_out?: string;
  reports_to_contact_id?: string;
  contact_owner_id?: string;
  description?: string;
  notes?: string;
  tags?: string;
  linkedin_url?: string;
  twitter_handle?: string;
}

export interface CRMContactUpdate extends Partial<CRMContactCreate> {}

export interface CRMAccountRelationship {
  id: string;
  primary_account_id: string;
  related_account_id: string;
  relationship_type: string;
  relationship_description?: string;
  strength?: string;
  is_active: string;
  start_date?: string;
  end_date?: string;
  notes?: string;
  tenant_id: string;
  created_at: string;
  updated_at: string;
}

export interface CRMAccountRelationshipCreate {
  primary_account_id: string;
  related_account_id: string;
  relationship_type: string;
  relationship_description?: string;
  strength?: string;
  is_active?: string;
  start_date?: string;
  end_date?: string;
  notes?: string;
}

export interface CRMAccountRelationshipUpdate extends Partial<CRMAccountRelationshipCreate> {}

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
  tenant_id: string;
  created_at: string;
  updated_at: string;
}

export interface Account360View {
  account: CRMAccount;
  contacts: CRMContact[];
  relationships: CRMAccountRelationship[];
  recent_activities: CRMActivity[];
  child_accounts: CRMAccount[];
  opportunities_count: number;
  total_revenue: number;
}

export interface PaginatedAccountList {
  total: number;
  page: number;
  page_size: number;
  accounts: CRMAccount[];
}

export interface PaginatedContactList {
  total: number;
  page: number;
  page_size: number;
  contacts: CRMContact[];
}

export interface AccountSummary {
  total_accounts: number;
  total_contacts: number;
  total_revenue: number;
  by_status: Record<string, number>;
  by_type: Record<string, number>;
}

export interface AccountFilters {
  skip?: number;
  limit?: number;
  search?: string;
  status?: string;
  account_type?: string;
  account_owner_id?: string;
}

export interface ContactFilters {
  skip?: number;
  limit?: number;
  search?: string;
  account_id?: string;
  status?: string;
  contact_type?: string;
}

// ============================================================================
// API SERVICE
// ============================================================================

const ACCOUNTS_URL = '/api/v1/crm/accounts';

export const crmAccountService = {
  // ============================================================================
  // ACCOUNT CRUD
  // ============================================================================

  /**
   * Create new account
   */
  createAccount: async (data: CRMAccountCreate): Promise<{ success: boolean; data: CRMAccount; message: string }> => {
    const response = await api.post(`${ACCOUNTS_URL}`, data);
    return response.data;
  },

  /**
   * Get account by ID
   */
  getAccount: async (id: string): Promise<{ success: boolean; data: CRMAccount }> => {
    const response = await api.get(`${ACCOUNTS_URL}/${id}`);
    return response.data;
  },

  /**
   * Get account 360 view
   */
  getAccount360: async (id: string): Promise<{ success: boolean; data: Account360View }> => {
    const response = await api.get(`${ACCOUNTS_URL}/${id}/360`);
    return response.data;
  },

  /**
   * List accounts with filters
   */
  listAccounts: async (filters: AccountFilters = {}): Promise<{ success: boolean; data: PaginatedAccountList }> => {
    const response = await api.get(`${ACCOUNTS_URL}`, { params: filters });
    return response.data;
  },

  /**
   * Update account
   */
  updateAccount: async (id: string, data: CRMAccountUpdate): Promise<{ success: boolean; data: CRMAccount; message: string }> => {
    const response = await api.put(`${ACCOUNTS_URL}/${id}`, data);
    return response.data;
  },

  /**
   * Delete account (soft delete)
   */
  deleteAccount: async (id: string): Promise<{ success: boolean; message: string }> => {
    const response = await api.delete(`${ACCOUNTS_URL}/${id}`);
    return response.data;
  },

  /**
   * Get account summary statistics
   */
  getAccountsSummary: async (): Promise<{ success: boolean; data: AccountSummary }> => {
    const response = await api.get(`${ACCOUNTS_URL}/stats/summary`);
    return response.data;
  },

  // ============================================================================
  // CONTACT CRUD
  // ============================================================================

  /**
   * Create new contact
   */
  createContact: async (data: CRMContactCreate): Promise<{ success: boolean; data: CRMContact; message: string }> => {
    const response = await api.post(`${ACCOUNTS_URL}/contacts`, data);
    return response.data;
  },

  /**
   * Get contact by ID
   */
  getContact: async (id: string): Promise<{ success: boolean; data: CRMContact }> => {
    const response = await api.get(`${ACCOUNTS_URL}/contacts/${id}`);
    return response.data;
  },

  /**
   * List contacts with filters
   */
  listContacts: async (filters: ContactFilters = {}): Promise<{ success: boolean; data: PaginatedContactList }> => {
    const response = await api.get(`${ACCOUNTS_URL}/contacts`, { params: filters });
    return response.data;
  },

  /**
   * Update contact
   */
  updateContact: async (id: string, data: CRMContactUpdate): Promise<{ success: boolean; data: CRMContact; message: string }> => {
    const response = await api.put(`${ACCOUNTS_URL}/contacts/${id}`, data);
    return response.data;
  },

  /**
   * Delete contact (soft delete)
   */
  deleteContact: async (id: string): Promise<{ success: boolean; message: string }> => {
    const response = await api.delete(`${ACCOUNTS_URL}/contacts/${id}`);
    return response.data;
  },

  // ============================================================================
  // RELATIONSHIP CRUD
  // ============================================================================

  /**
   * Create new relationship
   */
  createRelationship: async (data: CRMAccountRelationshipCreate): Promise<{ success: boolean; data: CRMAccountRelationship; message: string }> => {
    const response = await api.post(`${ACCOUNTS_URL}/relationships`, data);
    return response.data;
  },

  /**
   * List relationships
   */
  listRelationships: async (accountId?: string, skip = 0, limit = 50): Promise<{ success: boolean; data: any }> => {
    const params: any = { skip, limit };
    if (accountId) params.account_id = accountId;
    const response = await api.get(`${ACCOUNTS_URL}/relationships`, { params });
    return response.data;
  },

  /**
   * Update relationship
   */
  updateRelationship: async (id: string, data: CRMAccountRelationshipUpdate): Promise<{ success: boolean; data: CRMAccountRelationship; message: string }> => {
    const response = await api.put(`${ACCOUNTS_URL}/relationships/${id}`, data);
    return response.data;
  },

  /**
   * Delete relationship (soft delete)
   */
  deleteRelationship: async (id: string): Promise<{ success: boolean; message: string }> => {
    const response = await api.delete(`${ACCOUNTS_URL}/relationships/${id}`);
    return response.data;
  }
};

export default crmAccountService;
