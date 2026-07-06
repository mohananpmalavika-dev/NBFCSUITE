/**
 * Master Data Service
 * API calls for master data management
 */

import { apiClient } from '@/lib/api-client';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Helper function for direct fetch (when apiClient isn't suitable)
async function fetchMasterData(endpoint: string, options: RequestInit = {}) {
  const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null;
  
  const response = await fetch(`${API_URL}/api/v1/masterdata${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
      ...options.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`API call failed: ${response.statusText}`);
  }

  return response.json();
}

// Generic list function for any master data type
export async function listMasterData(
  type: string,
  params: {
    page?: number;
    page_size?: number;
    search?: string;
    is_active?: boolean;
  } = {}
) {
  const queryParams = new URLSearchParams();
  
  if (params.page) queryParams.append('page', params.page.toString());
  if (params.page_size) queryParams.append('page_size', params.page_size.toString());
  if (params.search) queryParams.append('search', params.search);
  if (params.is_active !== undefined) queryParams.append('is_active', params.is_active.toString());

  const result = await fetchMasterData(`/${type}?${queryParams.toString()}`);
  return result;
}

// Generic delete function
export async function deleteMasterData(type: string, id: string | number) {
  const result = await fetchMasterData(`/${type}/${id}`, {
    method: 'DELETE',
  });
  return result;
}

// Generic create function
export async function createMasterData(type: string, data: any) {
  const result = await fetchMasterData(`/${type}`, {
    method: 'POST',
    body: JSON.stringify(data),
  });
  return result;
}

// Generic update function
export async function updateMasterData(type: string, id: string | number, data: any) {
  const result = await fetchMasterData(`/${type}/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
  return result;
}

// Specific functions for common operations

export async function listStates(params: { page?: number; page_size?: number; search?: string } = {}) {
  return listMasterData('states', params);
}

export async function listCities(params: { page?: number; page_size?: number; search?: string; state_id?: number } = {}) {
  const queryParams = new URLSearchParams();
  if (params.page) queryParams.append('page', params.page.toString());
  if (params.page_size) queryParams.append('page_size', params.page_size.toString());
  if (params.search) queryParams.append('search', params.search);
  if (params.state_id) queryParams.append('state_id', params.state_id.toString());
  
  return fetchMasterData(`/cities?${queryParams.toString()}`);
}

export async function listBanks(params: { page?: number; page_size?: number; search?: string } = {}) {
  return listMasterData('banks', params);
}

export async function listBankBranches(params: { 
  page?: number; 
  page_size?: number; 
  search?: string;
  bank_id?: number;
  ifsc_code?: string;
} = {}) {
  const queryParams = new URLSearchParams();
  if (params.page) queryParams.append('page', params.page.toString());
  if (params.page_size) queryParams.append('page_size', params.page_size.toString());
  if (params.search) queryParams.append('search', params.search);
  if (params.bank_id) queryParams.append('bank_id', params.bank_id.toString());
  if (params.ifsc_code) queryParams.append('ifsc_code', params.ifsc_code);
  
  return fetchMasterData(`/bank-branches?${queryParams.toString()}`);
}

export async function searchPincode(pincode: string) {
  return fetchMasterData(`/pincodes/search/${pincode}`);
}

export async function listPincodes(params: { page?: number; page_size?: number; search?: string } = {}) {
  return listMasterData('pincodes', params);
}

export async function listDocumentTypes(params: { page?: number; page_size?: number; search?: string } = {}) {
  return listMasterData('documents', params);
}

export async function listOccupations(params: { page?: number; page_size?: number; search?: string } = {}) {
  return listMasterData('occupations', params);
}

export async function listIndustries(params: { page?: number; page_size?: number; search?: string } = {}) {
  return listMasterData('industries', params);
}

export async function listLoanProducts(params: { page?: number; page_size?: number; search?: string } = {}) {
  return listMasterData('loan-products', params);
}

export async function getMasterDataStats() {
  return fetchMasterData('/stats');
}
