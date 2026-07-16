/**
 * Camera Management Service
 * 
 * API service for CCTV camera management including:
 * - Camera CRUD operations
 * - Health monitoring
 * - Status management
 * - Connectivity testing
 * - Branch summaries
 */

import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface CCTVCamera {
  id: string;
  tenant_id: string;
  branch_id: string;
  camera_id: string;
  camera_name: string;
  camera_type: 'dome' | 'bullet' | 'ptz' | 'thermal' | 'anpr' | 'fisheye' | 'turret' | 'box';
  location_type: string;
  location_description: string;
  manufacturer: string;
  model: string;
  serial_number: string;
  ip_address: string;
  port: number;
  rtsp_url?: string;
  onvif_url?: string;
  mac_address?: string;
  firmware_version?: string;
  installation_date: string;
  warranty_expiry_date?: string;
  status: 'online' | 'offline' | 'maintenance' | 'faulty';
  recording_enabled: boolean;
  audio_recording_enabled: boolean;
  is_critical: boolean;
  uptime_percentage: number;
  last_online_at?: string;
  specifications: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface CameraCreate {
  branch_id: string;
  camera_id: string;
  camera_name: string;
  camera_type: string;
  location_type: string;
  location_description: string;
  manufacturer: string;
  model: string;
  serial_number: string;
  ip_address: string;
  port: number;
  rtsp_url?: string;
  onvif_url?: string;
  mac_address?: string;
  firmware_version?: string;
  installation_date: string;
  warranty_expiry_date?: string;
  recording_enabled?: boolean;
  audio_recording_enabled?: boolean;
  is_critical?: boolean;
  specifications?: Record<string, any>;
}

export interface CameraUpdate {
  camera_name?: string;
  camera_type?: string;
  location_type?: string;
  location_description?: string;
  manufacturer?: string;
  model?: string;
  ip_address?: string;
  port?: number;
  rtsp_url?: string;
  onvif_url?: string;
  firmware_version?: string;
  warranty_expiry_date?: string;
  recording_enabled?: boolean;
  audio_recording_enabled?: boolean;
  is_critical?: boolean;
  specifications?: Record<string, any>;
}

export interface CameraHealth {
  camera_id: string;
  camera_name: string;
  health_score: number;
  health_status: 'excellent' | 'good' | 'fair' | 'poor';
  status: string;
  uptime_percentage: number;
  last_online_at?: string;
  recording_enabled: boolean;
  issues: string[];
  recommendations: string[];
}

export interface CameraUptime {
  camera_id: string;
  camera_name: string;
  period_days: number;
  uptime_percentage: number;
  total_hours: number;
  online_hours: number;
  offline_hours: number;
}

export interface ConnectivityTest {
  camera_id: string;
  camera_name: string;
  ip_address: string;
  connectivity: 'success' | 'failed';
  ping_response_ms?: number;
  rtsp_stream: string;
  onvif_status: string;
  timestamp: string;
}

export interface BranchCameraSummary {
  branch_id: string;
  total_cameras: number;
  online_cameras: number;
  offline_cameras: number;
  maintenance_cameras: number;
  recording_cameras: number;
  critical_cameras: number;
  average_uptime_percentage: number;
  by_type: Record<string, number>;
  by_location: Record<string, number>;
  health_status: string;
}

export interface SystemHealthReport {
  total_cameras: number;
  online_cameras: number;
  offline_cameras: number;
  maintenance_cameras: number;
  faulty_cameras: number;
  availability_percentage: number;
  average_uptime_percentage: number;
  system_health: 'excellent' | 'good' | 'needs_attention';
  cameras_needing_attention: number;
  low_uptime_cameras: Array<{
    camera_id: string;
    camera_name: string;
    uptime_percentage: number;
  }>;
  offline_cameras: Array<{
    camera_id: string;
    camera_name: string;
    last_online?: string;
  }>;
  timestamp: string;
}

class CameraService {
  /**
   * Create a new camera
   */
  async createCamera(data: CameraCreate): Promise<CCTVCamera> {
    const response = await api.post('/cctv/cameras', data);
    return response.data.data;
  }

  /**
   * Get all cameras with filters
   */
  async listCameras(params: {
    branch_id?: string;
    camera_type?: string;
    location_type?: string;
    status?: string;
    is_critical?: boolean;
    page?: number;
    page_size?: number;
  }): Promise<{
    cameras: CCTVCamera[];
    total: number;
    page: number;
    page_size: number;
    total_pages: number;
  }> {
    const response = await api.get('/cctv/cameras', { params });
    return response.data.data;
  }

  /**
   * Get camera by ID
   */
  async getCamera(cameraId: string): Promise<CCTVCamera> {
    const response = await api.get(`/cctv/cameras/${cameraId}`);
    return response.data.data;
  }

  /**
   * Update camera details
   */
  async updateCamera(cameraId: string, data: CameraUpdate): Promise<CCTVCamera> {
    const response = await api.put(`/cctv/cameras/${cameraId}`, data);
    return response.data.data;
  }

  /**
   * Delete camera (soft delete)
   */
  async deleteCamera(cameraId: string): Promise<{ message: string }> {
    const response = await api.delete(`/cctv/cameras/${cameraId}`);
    return response.data.data;
  }

  /**
   * Update camera status
   */
  async updateCameraStatus(
    cameraId: string,
    status: 'online' | 'offline' | 'maintenance' | 'faulty'
  ): Promise<{
    camera_id: string;
    old_status: string;
    new_status: string;
    updated_at: string;
  }> {
    const response = await api.patch(`/cctv/cameras/${cameraId}/status`, null, {
      params: { status }
    });
    return response.data.data;
  }

  /**
   * Get camera health status
   */
  async getCameraHealth(cameraId: string): Promise<CameraHealth> {
    const response = await api.get(`/cctv/cameras/${cameraId}/health`);
    return response.data.data;
  }

  /**
   * Calculate camera uptime
   */
  async calculateUptime(cameraId: string, days: number = 30): Promise<CameraUptime> {
    const response = await api.get(`/cctv/cameras/${cameraId}/uptime`, {
      params: { days }
    });
    return response.data.data;
  }

  /**
   * Test camera connectivity
   */
  async testConnectivity(cameraId: string): Promise<ConnectivityTest> {
    const response = await api.post(`/cctv/cameras/${cameraId}/test`);
    return response.data.data;
  }

  /**
   * Get branch camera summary
   */
  async getBranchSummary(branchId: string): Promise<BranchCameraSummary> {
    const response = await api.get(`/cctv/cameras/branch/${branchId}/summary`);
    return response.data.data;
  }

  /**
   * Get system-wide health report
   */
  async getSystemHealthReport(): Promise<SystemHealthReport> {
    const response = await api.get('/cctv/cameras/health/report');
    return response.data.data;
  }

  /**
   * Get camera types (static list)
   */
  getCameraTypes(): Array<{ value: string; label: string }> {
    return [
      { value: 'dome', label: 'Dome Camera (Indoor)' },
      { value: 'bullet', label: 'Bullet Camera (Outdoor)' },
      { value: 'ptz', label: 'PTZ Camera (Pan-Tilt-Zoom)' },
      { value: 'thermal', label: 'Thermal Camera' },
      { value: 'anpr', label: 'ANPR (License Plate Recognition)' },
      { value: 'fisheye', label: 'Fisheye Camera (360°)' },
      { value: 'turret', label: 'Turret Camera' },
      { value: 'box', label: 'Box Camera' }
    ];
  }

  /**
   * Get camera locations (static list)
   */
  getCameraLocations(): Array<{ value: string; label: string }> {
    return [
      { value: 'entrance', label: 'Branch Entrance' },
      { value: 'exit', label: 'Branch Exit' },
      { value: 'cash_counter', label: 'Cash Counter' },
      { value: 'manager_cabin', label: 'Manager Cabin' },
      { value: 'vault', label: 'Strong Room/Vault' },
      { value: 'locker_room', label: 'Locker Room' },
      { value: 'atm', label: 'ATM Cabin' },
      { value: 'parking', label: 'Parking Area' },
      { value: 'perimeter', label: 'Perimeter Fencing' },
      { value: 'staircase', label: 'Staircase/Corridors' },
      { value: 'server_room', label: 'Server Room' },
      { value: 'waiting_area', label: 'Customer Waiting Area' },
      { value: 'back_office', label: 'Back Office' },
      { value: 'terrace', label: 'Terrace/Roof' },
      { value: 'other', label: 'Other Location' }
    ];
  }

  /**
   * Get camera status options
   */
  getCameraStatuses(): Array<{ value: string; label: string; color: string }> {
    return [
      { value: 'online', label: 'Online', color: 'success' },
      { value: 'offline', label: 'Offline', color: 'error' },
      { value: 'maintenance', label: 'Maintenance', color: 'warning' },
      { value: 'faulty', label: 'Faulty', color: 'error' }
    ];
  }
}

export default new CameraService();
