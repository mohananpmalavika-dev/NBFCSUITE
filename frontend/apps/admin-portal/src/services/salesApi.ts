/**
 * CRM Sales Automation API Service
 * API calls for Products, Quotes, and Orders
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function apiRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
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

export interface Product {
  id: string;
  product_code: string;
  product_name: string;
  product_category: string;
  status: string;
  short_description?: string;
  detailed_description?: string;
  unit_price: number;
  cost_price?: number;
  currency: string;
  tax_type: string;
  tax_rate: number;
  hsn_code?: string;
  stock_quantity: number;
  reorder_level?: number;
  unit_of_measure: string;
  manufacturer?: string;
  brand?: string;
  model_number?: string;
  barcode?: string;
  sku?: string;
  image_url?: string;
  specification_url?: string;
  discount_percentage: number;
  discount_amount: number;
  is_taxable: string;
  is_discountable: string;
  is_returnable: string;
  created_at: string;
  updated_at: string;
}

export interface QuoteItem {
  id?: string;
  product_id: string;
  line_number: number;
  product_name: string;
  description?: string;
  quantity: number;
  unit_price: number;
  unit_of_measure: string;
  discount_percentage: number;
  discount_amount: number;
  tax_rate: number;
  tax_amount: number;
  line_total: number;
  net_amount: number;
}

export interface Quote {
  id: string;
  quote_number: string;
  quote_title: string;
  status: string;
  account_id: string;
  contact_id?: string;
  opportunity_id?: string;
  quote_date: string;
  valid_until: string;
  subtotal: number;
  tax_amount: number;
  discount_amount: number;
  shipping_charges: number;
  total_amount: number;
  currency: string;
  payment_terms?: string;
  delivery_terms?: string;
  terms_and_conditions?: string;
  notes?: string;
  shipping_address_line1?: string;
  shipping_city?: string;
  shipping_state?: string;
  shipping_pincode?: string;
  shipping_country: string;
  viewed_count: number;
  viewed_date?: string;
  accepted_date?: string;
  rejected_date?: string;
  items: QuoteItem[];
  created_at: string;
  updated_at: string;
}

export interface OrderItem {
  id?: string;
  product_id: string;
  line_number: number;
  product_name: string;
  description?: string;
  quantity: number;
  unit_price: number;
  unit_of_measure: string;
  discount_percentage: number;
  discount_amount: number;
  tax_rate: number;
  tax_amount: number;
  line_total: number;
  net_amount: number;
  quantity_shipped: number;
  quantity_delivered: number;
  is_fulfilled: string;
}

export interface Order {
  id: string;
  order_number: string;
  order_status: string;
  payment_status: string;
  account_id: string;
  contact_id?: string;
  quote_id?: string;
  order_date: string;
  expected_delivery_date?: string;
  actual_delivery_date?: string;
  subtotal: number;
  tax_amount: number;
  discount_amount: number;
  shipping_charges: number;
  total_amount: number;
  paid_amount: number;
  balance_amount: number;
  currency: string;
  shipping_address_line1?: string;
  shipping_city?: string;
  shipping_state?: string;
  shipping_pincode?: string;
  shipping_country: string;
  shipping_method?: string;
  tracking_number?: string;
  carrier?: string;
  payment_terms?: string;
  delivery_terms?: string;
  notes?: string;
  internal_notes?: string;
  is_fulfilled: string;
  items: OrderItem[];
  created_at: string;
  updated_at: string;
}

// ============================================================================
// PRODUCT APIs
// ============================================================================

export const productApi = {
  list: (params: { skip?: number; limit?: number; search?: string; category?: string; status?: string } = {}) => {
    const query = new URLSearchParams();
    if (params.skip !== undefined) query.append('skip', params.skip.toString());
    if (params.limit !== undefined) query.append('limit', params.limit.toString());
    if (params.search) query.append('search', params.search);
    if (params.category) query.append('category', params.category);
    if (params.status) query.append('status', params.status);
    return apiRequest<{ success: boolean; data: { products: Product[]; total: number; page: number; page_size: number; total_pages: number } }>(`/api/v1/crm/products?${query}`);
  },

  get: (id: string) => {
    return apiRequest<{ success: boolean; data: Product }>(`/api/v1/crm/products/${id}`);
  },

  create: (data: Partial<Product>) => {
    return apiRequest<{ success: boolean; message: string; data: Product }>(`/api/v1/crm/products`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  update: (id: string, data: Partial<Product>) => {
    return apiRequest<{ success: boolean; message: string; data: Product }>(`/api/v1/crm/products/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  },

  delete: (id: string) => {
    return apiRequest<{ success: boolean; message: string }>(`/api/v1/crm/products/${id}`, {
      method: "DELETE",
    });
  },
};

// ============================================================================
// QUOTE APIs
// ============================================================================

export const quoteApi = {
  list: (params: { skip?: number; limit?: number; search?: string; status?: string; account_id?: string } = {}) => {
    const query = new URLSearchParams();
    if (params.skip !== undefined) query.append('skip', params.skip.toString());
    if (params.limit !== undefined) query.append('limit', params.limit.toString());
    if (params.search) query.append('search', params.search);
    if (params.status) query.append('status', params.status);
    if (params.account_id) query.append('account_id', params.account_id);
    return apiRequest<{ success: boolean; data: { quotes: Quote[]; total: number; page: number; page_size: number; total_pages: number } }>(`/api/v1/crm/quotes?${query}`);
  },

  get: (id: string) => {
    return apiRequest<{ success: boolean; data: Quote }>(`/api/v1/crm/quotes/${id}`);
  },

  create: (data: { quote_title: string; account_id: string; quote_date: string; valid_until: string; total_amount: number; items: Partial<QuoteItem>[] }) => {
    return apiRequest<{ success: boolean; message: string; data: Quote }>(`/api/v1/crm/quotes`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  update: (id: string, data: Partial<Quote>) => {
    return apiRequest<{ success: boolean; message: string; data: Quote }>(`/api/v1/crm/quotes/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  },

  updateStatus: (id: string, status: string) => {
    return apiRequest<{ success: boolean; message: string; data: Quote }>(`/api/v1/crm/quotes/${id}/status?new_status=${status}`, {
      method: "POST",
    });
  },
};

// ============================================================================
// ORDER APIs
// ============================================================================

export const orderApi = {
  list: (params: { skip?: number; limit?: number; search?: string; order_status?: string; payment_status?: string; account_id?: string } = {}) => {
    const query = new URLSearchParams();
    if (params.skip !== undefined) query.append('skip', params.skip.toString());
    if (params.limit !== undefined) query.append('limit', params.limit.toString());
    if (params.search) query.append('search', params.search);
    if (params.order_status) query.append('order_status', params.order_status);
    if (params.payment_status) query.append('payment_status', params.payment_status);
    if (params.account_id) query.append('account_id', params.account_id);
    return apiRequest<{ success: boolean; data: { orders: Order[]; total: number; page: number; page_size: number; total_pages: number } }>(`/api/v1/crm/orders?${query}`);
  },

  get: (id: string) => {
    return apiRequest<{ success: boolean; data: Order }>(`/api/v1/crm/orders/${id}`);
  },

  create: (data: { account_id: string; order_date: string; total_amount: number; items: Partial<OrderItem>[] }) => {
    return apiRequest<{ success: boolean; message: string; data: Order }>(`/api/v1/crm/orders`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  update: (id: string, data: Partial<Order>) => {
    return apiRequest<{ success: boolean; message: string; data: Order }>(`/api/v1/crm/orders/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  },
};

export const salesApi = {
  products: productApi,
  quotes: quoteApi,
  orders: orderApi,
};

export default salesApi;
