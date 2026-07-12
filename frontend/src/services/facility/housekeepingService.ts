/**
 * Housekeeping Management Service
 */

import axios from 'axios';
import { HousekeepingTask, HousekeepingSupply, TaskFormData, PaginatedResponse, ApiResponse } from './types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1/facility/housekeeping`,
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

export const housekeepingService = {
  // Create a new task
  createTask: async (data: TaskFormData): Promise<HousekeepingTask> => {
    const response = await api.post<ApiResponse<HousekeepingTask>>('/tasks', data);
    return response.data.data;
  },

  // Get all tasks with filters
  getTasks: async (params?: {
    skip?: number;
    limit?: number;
    status?: string;
    priority?: string;
    assigned_to?: number;
    building_id?: number;
    from_date?: string;
    to_date?: string;
  }): Promise<PaginatedResponse<HousekeepingTask>> => {
    const response = await api.get<ApiResponse<PaginatedResponse<HousekeepingTask>>>('/tasks', { params });
    return response.data.data;
  },

  // Update task status
  updateTaskStatus: async (taskId: number, status: string, remarks?: string): Promise<HousekeepingTask> => {
    const response = await api.patch<ApiResponse<HousekeepingTask>>(`/tasks/${taskId}/status`, { status, remarks });
    return response.data.data;
  },

  // Assign task to employee
  assignTask: async (taskId: number, employeeId: number): Promise<HousekeepingTask> => {
    const response = await api.post<ApiResponse<HousekeepingTask>>(`/tasks/${taskId}/assign`, { employee_id: employeeId });
    return response.data.data;
  },

  // Get low stock supplies
  getLowStockItems: async (): Promise<HousekeepingSupply[]> => {
    const response = await api.get<ApiResponse<HousekeepingSupply[]>>('/supplies/low-stock');
    return response.data.data;
  },
};
