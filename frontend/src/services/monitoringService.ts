/**
 * Live Monitoring Service
 * 
 * Handles API calls for CCTV live monitoring including:
 * - Live camera feeds
 * - PTZ camera control
 * - Event bookmarking
 * - Alert management
 * - Shift logging
 */

import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface LiveCamera {
  id: string;
  camera_name: string;
  camera_id: string;
  location_type: string;
  location_description: string;
  camera_type: string;
  status: string;
  rtsp_url?: string;
  audio_recording_enabled: boolean;
  is_critical: boolean;
  specifications: Record<string, any>;
}

export interface StreamInfo {
  camera_id: string;
  camera_name: string;
  stream_url: string;
  quality: string;
  audio_enabled: boolean;
  can_ptz: boolean;
  resolution: string;
  frame_rate: number;
}

export interface PTZControl {
  camera_id: string;
  camera_name: string;
  action: string;
  speed: number;
  preset?: number;
  timestamp: string;
  status: string;
}

export interface VideoBookmark {
  id: string;
  camera_id: string;
  bookmark_name: string;
  description?: string;
  bookmark_timestamp: string;
  created_by: string;
  created_at: string;
}

export interface ActiveAlert {
  id: string;
  camera_id: string;
  alert_type: string;
  alert_severity: string;
  status: string;
  alert_timestamp: string;
  alert_message: string;
  alert_metadata?: Record<string, any>;
}

export interface ShiftLog {
  id: string;
  shift_start: string;
  shift_end?: string;
  personnel: string;
  observations?: string;
}

export interface CameraSequence {
  id?: string;
  sequence_name: string;
  camera_ids: string[];
  interval_seconds: number;
  camera_count?: number;
}

export interface MonitoringDashboard {
  cameras: {
    total: number;
    online: number;
    offline: number;
    availability_percentage: number;
  };
  alerts: {
    active: number;
    critical: number;
    last_hour: number;
  };
  timestamp: string;
}

class MonitoringService {
  /**
   * Get all cameras available for live monitoring
   */
  async getLiveCameras(params: {
    branch_id?: string;
    location_type?: string;
    page?: number;
    page_size?: number;
  }): Promise<{
    cameras: LiveCamera[];
    total: number;
    page: number;
    page_size: number;
    total_pages: number;
  }> {
    const response = await api.get('/cctv/monitoring/live-cameras', { params });
    return response.data.data;
  }

  /**
   * Get streaming URL for a specific camera
   */
  async getStreamUrl(
    cameraId: string,
    quality: 'low' | 'medium' | 'high' | 'ultra' = 'high'
  ): Promise<StreamInfo> {
    const response = await api.get(`/cctv/monitoring/stream/${cameraId}`, {
      params: { quality }
    });
    return response.data.data;
  }

  /**
   * Control PTZ camera
   */
  async controlPTZ(
    cameraId: string,
    action: 'pan_left' | 'pan_right' | 'tilt_up' | 'tilt_down' | 'zoom_in' | 'zoom_out' | 'stop' | 'go_to_preset' | 'set_preset' | 'home',
    speed?: number,
    preset?: number
  ): Promise<PTZControl> {
    const response = await api.post(`/cctv/monitoring/ptz/${cameraId}/control`, null, {
      params: { action, speed, preset }
    });
    return response.data.data;
  }

  /**
   * Create a bookmark for an important event
   */
  async createBookmark(data: {
    camera_id: string;
    bookmark_name: string;
    description?: string;
    timestamp?: string;
  }): Promise<VideoBookmark> {
    const response = await api.post('/cctv/monitoring/bookmarks', null, {
      params: data
    });
    return response.data.data;
  }

  /**
   * Get bookmarked events
   */
  async getBookmarks(params: {
    camera_id?: string;
    date_from?: string;
    date_to?: string;
    page?: number;
    page_size?: number;
  }): Promise<{
    bookmarks: VideoBookmark[];
    total: number;
    page: number;
    page_size: number;
  }> {
    const response = await api.get('/cctv/monitoring/bookmarks', { params });
    return response.data.data;
  }

  /**
   * Get active alerts
   */
  async getActiveAlerts(params: {
    severity?: 'low' | 'medium' | 'high' | 'critical';
    alert_type?: string;
    camera_id?: string;
    limit?: number;
  }): Promise<{
    alerts: ActiveAlert[];
    count: number;
  }> {
    const response = await api.get('/cctv/monitoring/alerts/active', { params });
    return response.data.data;
  }

  /**
   * Acknowledge an alert
   */
  async acknowledgeAlert(alertId: string): Promise<{
    alert_id: string;
    status: string;
    acknowledged_by: string;
    acknowledged_at: string;
  }> {
    const response = await api.post(`/cctv/monitoring/alerts/${alertId}/acknowledge`);
    return response.data.data;
  }

  /**
   * Create shift handover log
   */
  async createShiftLog(data: {
    shift_start: string;
    shift_end?: string;
    shift_personnel: string;
    observations?: string;
  }): Promise<ShiftLog> {
    const response = await api.post('/cctv/monitoring/shift-logs', null, {
      params: data
    });
    return response.data.data;
  }

  /**
   * Create camera auto-switch sequence
   */
  async createCameraSequence(data: {
    sequence_name: string;
    camera_ids: string[];
    interval_seconds?: number;
  }): Promise<CameraSequence> {
    const response = await api.post('/cctv/monitoring/sequences', null, {
      params: {
        sequence_name: data.sequence_name,
        camera_ids: data.camera_ids,
        interval_seconds: data.interval_seconds || 10
      }
    });
    return response.data.data;
  }

  /**
   * Get camera sequence configuration
   */
  async getCameraSequence(
    sequenceName: string,
    intervalSeconds: number = 10
  ): Promise<CameraSequence> {
    const response = await api.get(`/cctv/monitoring/sequences/${sequenceName}`, {
      params: { interval_seconds: intervalSeconds }
    });
    return response.data.data;
  }

  /**
   * Get monitoring dashboard data
   */
  async getMonitoringDashboard(): Promise<MonitoringDashboard> {
    const response = await api.get('/cctv/monitoring/dashboard');
    return response.data.data;
  }

  /**
   * Toggle audio monitoring for a camera
   */
  async toggleAudioMonitoring(
    cameraId: string,
    enabled: boolean
  ): Promise<{
    camera_id: string;
    camera_name: string;
    audio_enabled: boolean;
    timestamp: string;
  }> {
    const response = await api.post(`/cctv/monitoring/${cameraId}/audio`, null, {
      params: { enabled }
    });
    return response.data.data;
  }
}

export default new MonitoringService();
