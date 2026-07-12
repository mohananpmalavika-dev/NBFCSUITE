/**
 * Building Management Service
 */

import axios from 'axios';
import { Building, Floor, Room, BuildingFormData, FloorFormData, RoomFormData, PaginatedResponse, ApiResponse } from './types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1/facility/buildings`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ============================================================================
// BUILDING OPERATIONS
// ============================================================================

export const buildingService = {
  // Create a new building
  createBuilding: async (data: BuildingFormData): Promise<Building> => {
    const response = await api.post<ApiResponse<Building>>('', data);
    return response.data.data;
  },

  // Get all buildings with filters
  getBuildings: async (params?: {
    skip?: number;
    limit?: number;
    building_type?: string;
    status?: string;
    search?: string;
  }): Promise<PaginatedResponse<Building>> => {
    const response = await api.get<ApiResponse<PaginatedResponse<Building>>>('', { params });
    return response.data.data;
  },

  // Get building by ID
  getBuilding: async (id: number): Promise<Building> => {
    const response = await api.get<ApiResponse<Building>>(`/${id}`);
    return response.data.data;
  },

  // Update building
  updateBuilding: async (id: number, data: Partial<BuildingFormData>): Promise<Building> => {
    const response = await api.put<ApiResponse<Building>>(`/${id}`, data);
    return response.data.data;
  },

  // Delete building
  deleteBuilding: async (id: number): Promise<void> => {
    await api.delete(`/${id}`);
  },

  // ============================================================================
  // FLOOR OPERATIONS
  // ============================================================================

  // Create a new floor
  createFloor: async (buildingId: number, data: FloorFormData): Promise<Floor> => {
    const response = await api.post<ApiResponse<Floor>>(`/${buildingId}/floors`, data);
    return response.data.data;
  },

  // Get all floors in a building
  getFloors: async (buildingId: number): Promise<Floor[]> => {
    const response = await api.get<ApiResponse<Floor[]>>(`/${buildingId}/floors`);
    return response.data.data;
  },

  // ============================================================================
  // ROOM OPERATIONS
  // ============================================================================

  // Create a new room
  createRoom: async (buildingId: number, floorId: number, data: RoomFormData): Promise<Room> => {
    const response = await api.post<ApiResponse<Room>>(`/${buildingId}/floors/${floorId}/rooms`, data);
    return response.data.data;
  },

  // Get all rooms with filters
  getRooms: async (params?: {
    skip?: number;
    limit?: number;
    building_id?: number;
    floor_id?: number;
    room_type?: string;
    status?: string;
  }): Promise<PaginatedResponse<Room>> => {
    const response = await api.get<ApiResponse<PaginatedResponse<Room>>>('/rooms', { params });
    return response.data.data;
  },

  // Update room status
  updateRoomStatus: async (roomId: number, status: string): Promise<Room> => {
    const response = await api.patch<ApiResponse<Room>>(`/rooms/${roomId}/status`, { status });
    return response.data.data;
  },
};
