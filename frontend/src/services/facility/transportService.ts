/**
 * Transport Management Service
 */

import axios from 'axios';
import { Vehicle, Trip, VehicleFormData, TripFormData, PaginatedResponse, ApiResponse } from './types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1/facility/transport`,
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

export const transportService = {
  // Vehicle Management
  createVehicle: async (data: VehicleFormData): Promise<Vehicle> => {
    const response = await api.post<ApiResponse<Vehicle>>('/vehicles', data);
    return response.data.data;
  },

  getVehicles: async (params?: {
    skip?: number;
    limit?: number;
    vehicle_type?: string;
    status?: string;
    assigned_driver?: number;
  }): Promise<PaginatedResponse<Vehicle>> => {
    const response = await api.get<ApiResponse<PaginatedResponse<Vehicle>>>('/vehicles', { params });
    return response.data.data;
  },

  getAvailableVehicles: async (tripDate: string): Promise<Vehicle[]> => {
    const response = await api.get<ApiResponse<Vehicle[]>>('/vehicles/available', { params: { trip_date: tripDate } });
    return response.data.data;
  },

  // Trip Management
  createTrip: async (data: TripFormData): Promise<Trip> => {
    const response = await api.post<ApiResponse<Trip>>('/trips', data);
    return response.data.data;
  },

  getTrips: async (params?: {
    skip?: number;
    limit?: number;
    vehicle_id?: number;
    driver_id?: number;
    status?: string;
    from_date?: string;
    to_date?: string;
  }): Promise<PaginatedResponse<Trip>> => {
    const response = await api.get<ApiResponse<PaginatedResponse<Trip>>>('/trips', { params });
    return response.data.data;
  },

  startTrip: async (tripId: number, startMileage: number): Promise<Trip> => {
    const response = await api.post<ApiResponse<Trip>>(`/trips/${tripId}/start`, { start_mileage: startMileage });
    return response.data.data;
  },

  completeTrip: async (tripId: number, data: {
    end_mileage: number;
    fuel_consumed?: number;
    toll_charges?: number;
    parking_charges?: number;
    other_expenses?: number;
  }): Promise<Trip> => {
    const response = await api.post<ApiResponse<Trip>>(`/trips/${tripId}/complete`, data);
    return response.data.data;
  },

  getUpcomingMaintenance: async (daysAhead: number = 30): Promise<Vehicle[]> => {
    const response = await api.get<ApiResponse<Vehicle[]>>('/maintenance/upcoming', { params: { days_ahead: daysAhead } });
    return response.data.data;
  },
};
