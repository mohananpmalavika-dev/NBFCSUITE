/**
 * Recording & Storage Service
 * 
 * API service for DVR/NVR management, storage analytics,
 * and recording operations.
 */

import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

export interface DVRNVRConfig {
  id: string;
  device_name: string;
  device_type: string;
  branch_id: string;
  location: string;
  manufacturer: string;
  model: string;
  serial_number: string;
  total_channels: number;
  used_channels: number;
  available_channels: number;
  total_storage_tb: number;
  used_storage_tb: number;
  available_storage_tb: number;
  recording_quality: string;
  retention_days_hot: number;
  retention_days_cold: number;
  ip_address: string;
  status: string;
  uptime_percentage: number;
  storage_alert_active: boolean;
}

export interface StorageCalculationParams {
  num_cameras: number;
  bitrate_kbps: number;
  retention_days: number;
  recording_hours: number;
}

export interface StorageAnalytics {
  total_devices: number;
  total_capacity_tb: number;
  total_used_tb: number;
  total_available_tb: number;
  average_utilization_percentage: number;
  devices_with_alerts: number;
  storage_health: string;
  cleanup_recommended: boolean;
}

export interface StorageHealth {
  dvr_nvr_id: string;
  device_name: string;
  health_status: string;
  disk_health: string;
  raid_status: string;
  total_capacity_tb: number;
  used_capacity_tb: number;
  available_capacity_tb: number;
  utilization_percentage: number;
  days_until_full: number;
  alert_threshold: number;
  alert_active: boolean;
  recommendation: string;
}

class RecordingService {
  private getAuthHeaders() {
    const token = localStorage.getItem('auth_token');
    return {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    };
  }

  // DVR/NVR Management
  async createDVRNVR(config: Partial<DVRNVRConfig>) {
    return axios.post(
      `${API_BASE_URL}/cctv/dvr-nvr`,
      config,
      this.getAuthHeaders()
    );
  }

  async listDVRNVR(params?: {
    branch_id?: string;
    device_type?: string;
    status?: string;
    page?: number;
    page_size?: number;
  }) {
    return axios.get(
      `${API_BASE_URL}/cctv/dvr-nvr`,
      {
        ...this.getAuthHeaders(),
        params
      }
    );
  }

  async getDVRNVR(id: string) {
    return axios.get(
      `${API_BASE_URL}/cctv/dvr-nvr/${id}`,
      this.getAuthHeaders()
    );
  }

  async updateDVRNVR(id: string, updates: Partial<DVRNVRConfig>) {
    return axios.put(
      `${API_BASE_URL}/cctv/dvr-nvr/${id}`,
      updates,
      this.getAuthHeaders()
    );
  }

  // Storage Operations
  async calculateStorage(params: StorageCalculationParams) {
    return axios.post(
      `${API_BASE_URL}/cctv/storage/calculate`,
      null,
      {
        ...this.getAuthHeaders(),
        params
      }
    );
  }

  async getStorageAnalytics(branchId?: string) {
    return axios.get(
      `${API_BASE_URL}/cctv/storage/analytics`,
      {
        ...this.getAuthHeaders(),
        params: branchId ? { branch_id: branchId } : undefined
      }
    );
  }

  async checkStorageHealth(dvrNvrId: string) {
    return axios.get(
      `${API_BASE_URL}/cctv/storage/health/${dvrNvrId}`,
      this.getAuthHeaders()
    );
  }

  // Retention Policy
  async enforceRetentionPolicy(dvrNvrId: string, dryRun: boolean = true) {
    return axios.post(
      `${API_BASE_URL}/cctv/retention/enforce/${dvrNvrId}`,
      null,
      {
        ...this.getAuthHeaders(),
        params: { dry_run: dryRun }
      }
    );
  }

  // Backup Management
  async scheduleBackup(dvrNvrId: string, backupType: 'full' | 'incremental' = 'incremental') {
    return axios.post(
      `${API_BASE_URL}/cctv/backup/schedule/${dvrNvrId}`,
      null,
      {
        ...this.getAuthHeaders(),
        params: { backup_type: backupType }
      }
    );
  }

  // Recording Control
  async getRecordingStatus(cameraId: string) {
    return axios.get(
      `${API_BASE_URL}/cctv/recording/status/${cameraId}`,
      this.getAuthHeaders()
    );
  }

  async startRecording(cameraId: string) {
    return axios.post(
      `${API_BASE_URL}/cctv/recording/${cameraId}/start`,
      null,
      this.getAuthHeaders()
    );
  }

  async stopRecording(cameraId: string) {
    return axios.post(
      `${API_BASE_URL}/cctv/recording/${cameraId}/stop`,
      null,
      this.getAuthHeaders()
    );
  }
}

export const recordingService = new RecordingService();
export default recordingService;
