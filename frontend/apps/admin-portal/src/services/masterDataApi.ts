/**
 * Master Data API Service
 * Centralized API calls for all master data operations
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
    throw new Error(error.message || `HTTP ${response.status}`);
  }

  return response.json();
}

// Generic list response interface
export interface ListResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

// Generic list params
export interface ListParams {
  page?: number;
  page_size?: number;
  search?: string;
  is_active?: boolean;
}

// ============================================================================
// GEOGRAPHY APIs
// ============================================================================

export const countryApi = {
  list: (params: ListParams) => {
    const query = new URLSearchParams(params as any);
    return apiRequest<ListResponse<any>>(`/api/v1/masterdata/countries?${query}`);
  },
  get: (id: number) => apiRequest<any>(`/api/v1/masterdata/countries/${id}`),
  create: (data: any) => apiRequest<any>(`/api/v1/masterdata/countries`, {
    method: "POST",
    body: JSON.stringify(data),
  }),
  update: (id: number, data: any) => apiRequest<any>(`/api/v1/masterdata/countries/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  }),
  delete: (id: number) => apiRequest<void>(`/api/v1/masterdata/countries/${id}`, {
    method: "DELETE",
  }),
};

export const stateApi = {
  list: (params: ListParams) => {
    const query = new URLSearchParams(params as any);
    return apiRequest<ListResponse<any>>(`/api/v1/masterdata/states?${query}`);
  },
  get: (id: number) => apiRequest<any>(`/api/v1/masterdata/states/${id}`),
  create: (data: any) => apiRequest<any>(`/api/v1/masterdata/states`, {
    method: "POST",
    body: JSON.stringify(data),
  }),
  update: (id: number, data: any) => apiRequest<any>(`/api/v1/masterdata/states/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  }),
  delete: (id: number) => apiRequest<void>(`/api/v1/masterdata/states/${id}`, {
    method: "DELETE",
  }),
};

export const cityApi = {
  list: (params: ListParams & { state_id?: number }) => {
    const query = new URLSearchParams(params as any);
    return apiRequest<ListResponse<any>>(`/api/v1/masterdata/cities?${query}`);
  },
  get: (id: number) => apiRequest<any>(`/api/v1/masterdata/cities/${id}`),
  create: (data: any) => apiRequest<any>(`/api/v1/masterdata/cities`, {
    method: "POST",
    body: JSON.stringify(data),
  }),
  update: (id: number, data: any) => apiRequest<any>(`/api/v1/masterdata/cities/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  }),
  delete: (id: number) => apiRequest<void>(`/api/v1/masterdata/cities/${id}`, {
    method: "DELETE",
  }),
};

export const pincodeApi = {
  list: (params: ListParams) => {
    const query = new URLSearchParams(params as any);
    return apiRequest<ListResponse<any>>(`/api/v1/masterdata/pincodes?${query}`);
  },
  get: (id: number) => apiRequest<any>(`/api/v1/masterdata/pincodes/${id}`),
  search: (pincode: string) => apiRequest<any>(`/api/v1/masterdata/pincodes/search/${pincode}`),
  create: (data: any) => apiRequest<any>(`/api/v1/masterdata/pincodes`, {
    method: "POST",
    body: JSON.stringify(data),
  }),
  update: (id: number, data: any) => apiRequest<any>(`/api/v1/masterdata/pincodes/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  }),
  delete: (id: number) => apiRequest<void>(`/api/v1/masterdata/pincodes/${id}`, {
    method: "DELETE",
  }),
};

// ============================================================================
// BANKING APIs
// ============================================================================

export const bankApi = {
  list: (params: ListParams) => {
    const query = new URLSearchParams(params as any);
    return apiRequest<ListResponse<any>>(`/api/v1/masterdata/banks?${query}`);
  },
  get: (id: number) => apiRequest<any>(`/api/v1/masterdata/banks/${id}`),
  searchByCode: (code: string) => apiRequest<any>(`/api/v1/masterdata/banks/code/${code}`),
  create: (data: any) => apiRequest<any>(`/api/v1/masterdata/banks`, {
    method: "POST",
    body: JSON.stringify(data),
  }),
  update: (id: number, data: any) => apiRequest<any>(`/api/v1/masterdata/banks/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  }),
  delete: (id: number) => apiRequest<void>(`/api/v1/masterdata/banks/${id}`, {
    method: "DELETE",
  }),
};

export const bankBranchApi = {
  list: (params: ListParams & { bank_id?: number }) => {
    const query = new URLSearchParams(params as any);
    return apiRequest<ListResponse<any>>(`/api/v1/masterdata/bank-branches?${query}`);
  },
  get: (id: number) => apiRequest<any>(`/api/v1/masterdata/bank-branches/${id}`),
  searchIfsc: (ifsc: string) => apiRequest<any>(`/api/v1/masterdata/bank-branches/ifsc/${ifsc}`),
  create: (data: any) => apiRequest<any>(`/api/v1/masterdata/bank-branches`, {
    method: "POST",
    body: JSON.stringify(data),
  }),
  update: (id: number, data: any) => apiRequest<any>(`/api/v1/masterdata/bank-branches/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  }),
  delete: (id: number) => apiRequest<void>(`/api/v1/masterdata/bank-branches/${id}`, {
    method: "DELETE",
  }),
};

// ============================================================================
// FINANCIAL APIs
// ============================================================================

export const currencyApi = {
  list: (params: ListParams) => {
    const query = new URLSearchParams(params as any);
    return apiRequest<ListResponse<any>>(`/api/v1/masterdata/currency?${query}`);
  },
  get: (id: number) => apiRequest<any>(`/api/v1/masterdata/currency/${id}`),
  create: (data: any) => apiRequest<any>(`/api/v1/masterdata/currency`, {
    method: "POST",
    body: JSON.stringify(data),
  }),
  update: (id: number, data: any) => apiRequest<any>(`/api/v1/masterdata/currency/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  }),
  delete: (id: number) => apiRequest<void>(`/api/v1/masterdata/currency/${id}`, {
    method: "DELETE",
  }),
};

export const loanProductApi = {
  list: (params: ListParams) => {
    const query = new URLSearchParams(params as any);
    return apiRequest<ListResponse<any>>(`/api/v1/masterdata/loan-products?${query}`);
  },
  get: (id: number) => apiRequest<any>(`/api/v1/masterdata/loan-products/${id}`),
  create: (data: any) => apiRequest<any>(`/api/v1/masterdata/loan-products`, {
    method: "POST",
    body: JSON.stringify(data),
  }),
  update: (id: number, data: any) => apiRequest<any>(`/api/v1/masterdata/loan-products/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  }),
  delete: (id: number) => apiRequest<void>(`/api/v1/masterdata/loan-products/${id}`, {
    method: "DELETE",
  }),
};

// ============================================================================
// DOCUMENT APIs
// ============================================================================

export const documentTypeApi = {
  list: (params: ListParams & { is_mandatory?: boolean }) => {
    const query = new URLSearchParams(params as any);
    return apiRequest<ListResponse<any>>(`/api/v1/masterdata/documents?${query}`);
  },
  get: (id: number) => apiRequest<any>(`/api/v1/masterdata/documents/${id}`),
  create: (data: any) => apiRequest<any>(`/api/v1/masterdata/documents`, {
    method: "POST",
    body: JSON.stringify(data),
  }),
  update: (id: number, data: any) => apiRequest<any>(`/api/v1/masterdata/documents/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  }),
  delete: (id: number) => apiRequest<void>(`/api/v1/masterdata/documents/${id}`, {
    method: "DELETE",
  }),
};

// ============================================================================
// OCCUPATION & INDUSTRY APIs
// ============================================================================

export const occupationApi = {
  list: (params: ListParams & { category?: string }) => {
    const query = new URLSearchParams(params as any);
    return apiRequest<ListResponse<any>>(`/api/v1/masterdata/occupations?${query}`);
  },
  get: (id: number) => apiRequest<any>(`/api/v1/masterdata/occupations/${id}`),
  create: (data: any) => apiRequest<any>(`/api/v1/masterdata/occupations`, {
    method: "POST",
    body: JSON.stringify(data),
  }),
  update: (id: number, data: any) => apiRequest<any>(`/api/v1/masterdata/occupations/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  }),
  delete: (id: number) => apiRequest<void>(`/api/v1/masterdata/occupations/${id}`, {
    method: "DELETE",
  }),
};

export const industryApi = {
  list: (params: ListParams) => {
    const query = new URLSearchParams(params as any);
    return apiRequest<ListResponse<any>>(`/api/v1/masterdata/industries?${query}`);
  },
  get: (id: number) => apiRequest<any>(`/api/v1/masterdata/industries/${id}`),
  create: (data: any) => apiRequest<any>(`/api/v1/masterdata/industries`, {
    method: "POST",
    body: JSON.stringify(data),
  }),
  update: (id: number, data: any) => apiRequest<any>(`/api/v1/masterdata/industries/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  }),
  delete: (id: number) => apiRequest<void>(`/api/v1/masterdata/industries/${id}`, {
    method: "DELETE",
  }),
};

// ============================================================================
// STATISTICS API
// ============================================================================

export interface MasterDataStats {
  countries: number;
  states: number;
  cities: number;
  pincodes: number;
  banks: number;
  bank_branches: number;
  loan_products: number;
  documents: number;
  occupations: number;
  industries: number;
}

export const masterDataApi = {
  getStats: () => apiRequest<MasterDataStats>(`/api/v1/masterdata/stats`),
};

export default {
  country: countryApi,
  state: stateApi,
  city: cityApi,
  pincode: pincodeApi,
  bank: bankApi,
  bankBranch: bankBranchApi,
  currency: currencyApi,
  loanProduct: loanProductApi,
  documentType: documentTypeApi,
  occupation: occupationApi,
  industry: industryApi,
  stats: masterDataApi,
};
