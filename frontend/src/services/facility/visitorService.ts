/**
 * Visitor Management Service
 */

import axios from 'axios';
import { Visitor, VisitorFormData, PaginatedResponse, ApiResponse } from './types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1/facility/visitors`,
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

export const visitorService = {
  // Create a new visitor entry
  createVisitor: async (data: VisitorFormData): Promise<Visitor> => {
    const response = await api.post<ApiResponse<Visitor>>('', data);
    return response.data.data;
  },

  // Get all visitors with filters
  getVisitors: async (params?: {
    skip?: number;
    limit?: number;
    visitor_type?: string;
    status?: string;
    host_employee_id?: number;
    from_date?: string;
    to_date?: string;
    search?: string;
  }): Promise<PaginatedResponse<Visitor>> => {
    const response = await api.get<ApiResponse<PaginatedResponse<Visitor>>>('', { params });
    return response.data.data;
  },

  // Get visitor by ID
  getVisitor: async (id: number): Promise<Visitor> => {
    const response = await api.get<ApiResponse<Visitor>>(`/${id}`);
    return response.data.data;
  },

  // Check in visitor
  checkInVisitor: async (id: number, badgeNumber?: string): Promise<Visitor> => {
    const response = await api.post<ApiResponse<Visitor>>(`/${id}/check-in`, { badge_number: badgeNumber });
    return response.data.data;
  },

  // Check out visitor
  checkOutVisitor: async (id: number): Promise<Visitor> => {
    const response = await api.post<ApiResponse<Visitor>>(`/${id}/check-out`);
    return response.data.data;
  },

  // Get active visitors
  getActiveVisitors: async (): Promise<Visitor[]> => {
    const response = await api.get<ApiResponse<Visitor[]>>('/active/current');
    return response.data.data;
  },

  // Get expected visitors today
  getExpectedVisitorsToday: async (): Promise<Visitor[]> => {
    const response = await api.get<ApiResponse<Visitor[]>>('/expected/today');
    return response.data.data;
  },

  // Approve visitor
  approveVisitor: async (id: number): Promise<Visitor> => {
    const response = await api.post<ApiResponse<Visitor>>(`/${id}/approve`);
    return response.data.data;
  },

  // Get visitor statistics
  getVisitorStatistics: async (fromDate: string, toDate: string): Promise<any> => {
    const response = await api.get<ApiResponse<any>>('/statistics/range', { 
      params: { from_date: fromDate, to_date: toDate } 
    });
    return response.data.data;
  },
};
