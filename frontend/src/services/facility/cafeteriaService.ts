/**
 * Cafeteria Management Service
 */

import axios from 'axios';
import { MenuItem, CafeteriaOrder, MenuItemFormData, OrderFormData, PaginatedResponse, ApiResponse } from './types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1/facility/cafeteria`,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const cafeteriaService = {
  // Menu Management
  createMenuItem: async (data: MenuItemFormData): Promise<MenuItem> => {
    const response = await api.post<ApiResponse<MenuItem>>('/menu', data);
    return response.data.data;
  },

  getMenuItems: async (params?: {
    skip?: number;
    limit?: number;
    meal_type?: string;
    is_available?: boolean;
  }): Promise<PaginatedResponse<MenuItem>> => {
    const response = await api.get<ApiResponse<PaginatedResponse<MenuItem>>>('/menu', { params });
    return response.data.data;
  },

  // Order Management
  createOrder: async (data: OrderFormData): Promise<CafeteriaOrder> => {
    const response = await api.post<ApiResponse<CafeteriaOrder>>('/orders', data);
    return response.data.data;
  },

  getOrders: async (params?: {
    skip?: number;
    limit?: number;
    status?: string;
    employee_id?: number;
    from_date?: string;
    to_date?: string;
  }): Promise<PaginatedResponse<CafeteriaOrder>> => {
    const response = await api.get<ApiResponse<PaginatedResponse<CafeteriaOrder>>>('/orders', { params });
    return response.data.data;
  },

  updateOrderStatus: async (orderId: number, status: string): Promise<CafeteriaOrder> => {
    const response = await api.patch<ApiResponse<CafeteriaOrder>>(`/orders/${orderId}/status`, { status });
    return response.data.data;
  },
};
