/**
 * Camera Form Component
 * 
 * Form for creating and editing CCTV cameras
 * Features:
 * - Complete camera configuration
 * - Field validation
 * - Network settings
 * - Technical specifications
 * - Installation details
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Checkbox,
  Alert,
  CircularProgress,
  Divider,
  Paper
} from '@mui/material';
import {
  Save,
  Cancel,
  Videocam
} from '@mui/icons-material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import cameraService, { CameraCreate, CameraUpdate, CCTVCamera } from '../../../services/cameraService';

interface CameraFormProps {
  cameraId?: string;
  onSuccess?: () => void;
  onCancel?: () => void;
}

const CameraForm: React.FC<CameraFormProps> = ({ cameraId, onSuccess, onCancel }) => {
  const [loading, setLoading] = useState(false);
  const [loadingCamera, setLoadingCamera] = useState(!!cameraId);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    branch_id: '',
    camera_id: '',
    camera_name: '',
    camera_type: 'dome',
    location_type: 'entrance',
    location_description: '',
    manufacturer: '',
    model: '',
    serial_number: '',
    ip_address: '',
    port: 554,
    rtsp_url: '',
    onvif_url: '',
    mac_address: '',
    firmware_version: '',
    installation_date: new Date(),
    warranty_expiry_date: null as Date | null,
    recording_enabled: true,
    audio_recording_enabled: false,
    is_critical: false,
    // Specifications
    resolution: '1080p',
    frame_rate: 25,
    field_of_view: '90',
    ir_distance: '30',
    weatherproof_rating: 'IP66',
    audio_support: false
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (cameraId) {
      loadCamera();
    }
  }, [cameraId]);

  const loadCamera = async () => {
    try {
      setLoadingCamera(true);
      const camera = await cameraService.getCamera(cameraId!);
      
      setFormData({
        branch_id: camera.branch_id,
        camera_id: camera.camera_id,
        camera_name: camera.camera_name,
        camera_type: camera.camera_type,
        location_type: camera.location_type,
        location_description: camera.location_description,
        manufacturer: camera.manufacturer,
        model: camera.model,
        serial_number: camera.serial_number,
        ip_address: camera.ip_address,
        port: camera.port,
        rtsp_url: camera.rtsp_url || '',
        onvif_url: camera.onvif_url || '',
        mac_address: camera.mac_address || '',
        firmware_version: camera.firmware_version || '',
        installation_date: new Date(camera.installation_date),
        warranty_expiry_date: camera.warranty_expiry_date ? new Date(camera.warranty_expiry_date) : null,
        recording_enabled: camera.recording_enabled,
        audio_recording_enabled: camera.audio_recording_enabled,
        is_critical: camera.is_critical,
        resolution: camera.specifications?.resolution || '1080p',
        frame_rate: camera.specifications?.frame_rate || 25,
        field_of_view: camera.specifications?.field_of_view || '90',
        ir_distance: camera.specifications?.ir_distance || '30',
        weatherproof_rating: camera.specifications?.weatherproof_rating || 'IP66',
        audio_support: camera.specifications?.audio_support || false
      });
      
      setLoadingCamera(false);
    } catch (error) {
      console.error('Failed to load camera:', error);
      setError('Failed to load camera details');
      setLoadingCamera(false);
    }
  };

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.camera_id.trim()) {
      newErrors.camera_id = 'Camera ID is required';
    }
    if (!formData.camera_name.trim()) {
      newErrors.camera_name = 'Camera name is required';
    }
    if (!formData.branch_id) {
      newErrors.branch_id = 'Branch is required';
    }
    if (!formData.manufacturer.trim()) {
      newErrors.manufacturer = 'Manufacturer is required';
    }
    if (!formData.model.trim()) {
      newErrors.model = 'Model is required';
    }
    if (!formData.serial_number.trim()) {
      newErrors.serial_number = 'Serial number is required';
    }
    if (!formData.ip_address.trim()) {
      newErrors.ip_address = 'IP address is required';
    } else if (!/^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$/.test(formData.ip_address)) {
      newErrors.ip_address = 'Invalid IP address format';
    }
    if (!formData.port || formData.port < 1 || formData.port > 65535) {
      newErrors.port = 'Port must be between 1 and 65535';
    }
    if (!formData.location_description.trim()) {
      newErrors.location_description = 'Location description is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const specifications = {
        resolution: formData.resolution,
        frame_rate: formData.frame_rate,
        field_of_view: formData.field_of_view,
        ir_distance: formData.ir_distance,
        weatherproof_rating: formData.weatherproof_rating,
        audio_support: formData.audio_support
      };

      if (cameraId) {
        // Update existing camera
        const updateData: CameraUpdate = {
          camera_name: formData.camera_name,
          camera_type: formData.camera_type,
          location_type: formData.location_type,
          location_description: formData.location_description,
          manufacturer: formData.manufacturer,
          model: formData.model,
          ip_address: formData.ip_address,
          port: formData.port,
          rtsp_url: formData.rtsp_url || undefined,
          onvif_url: formData.onvif_url || undefined,
          firmware_version: formData.firmware_version || undefined,
          warranty_expiry_date: formData.warranty_expiry_date?.toISOString() || undefined,
          recording_enabled: formData.recording_enabled,
          audio_recording_enabled: formData.audio_recording_enabled,
          is_critical: formData.is_critical,
          specifications
        };
        
        await cameraService.updateCamera(cameraId, updateData);
      } else {
        // Create new camera
        const createData: CameraCreate = {
          branch_id: formData.branch_id,
          camera_id: formData.camera_id,
          camera_name: formData.camera_name,
          camera_type: formData.camera_type,
          location_type: formData.location_type,
          location_description: formData.location_description,
          manufacturer: formData.manufacturer,
          model: formData.model,
          serial_number: formData.serial_number,
          ip_address: formData.ip_address,
          port: formData.port,
          rtsp_url: formData.rtsp_url || undefined,
          onvif_url: formData.onvif_url || undefined,
          mac_address: formData.mac_address || undefined,
          firmware_version: formData.firmware_version || undefined,
          installation_date: formData.installation_date.toISOString(),
          warranty_expiry_date: formData.warranty_expiry_date?.toISOString() || undefined,
          recording_enabled: formData.recording_enabled,
          audio_recording_enabled: formData.audio_recording_enabled,
          is_critical: formData.is_critical,
          specifications
        };
        
        await cameraService.createCamera(createData);
      }

      setLoading(false);
      if (onSuccess) {
        onSuccess();
      }
    } catch (error: any) {
      console.error('Failed to save camera:', error);
      setError(error.response?.data?.message || 'Failed to save camera');
      setLoading(false);
    }
  };

  if (loadingCamera) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Box component="form" onSubmit={handleSubmit}>
        <Card>
          <CardContent>
            {/* Header */}
            <Typography variant="h5" gutterBottom>
              <Videocam sx={{ mr: 1, verticalAlign: 'middle' }} />
              {cameraId ? 'Edit Camera' : 'Add New Camera'}
            </Typography>

            {error && (
              <Alert severity="error" sx={{ mb: 3 }}>
                {error}
              </Alert>
            )}

            {/* Basic Information */}
            <Paper elevation={0} sx={{ p: 2, mb: 3, bgcolor: 'grey.50' }}>
              <Typography variant="h6" gutterBottom>
                Basic Information
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    required
                    label="Camera ID"
                    value={formData.camera_id}
                    onChange={(e) => setFormData({ ...formData, camera_id: e.target.value })}
                    error={!!errors.camera_id}
                    helperText={errors.camera_id || 'Unique identifier for the camera'}
                    disabled={!!cameraId}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    required
                    label="Camera Name"
                    value={formData.camera_name}
                    onChange={(e) => setFormData({ ...formData, camera_name: e.target.value })}
                    error={!!errors.camera_name}
                    helperText={errors.camera_name || 'Descriptive name for the camera'}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth required error={!!errors.camera_type}>
                    <InputLabel>Camera Type</InputLabel>
                    <Select
                      value={formData.camera_type}
                      label="Camera Type"
                      onChange={(e) => setFormData({ ...formData, camera_type: e.target.value })}
                    >
                      {cameraService.getCameraTypes().map(type => (
                        <MenuItem key={type.value} value={type.value}>
                          {type.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth required error={!!errors.location_type}>
                    <InputLabel>Location Type</InputLabel>
                    <Select
                      value={formData.location_type}
                      label="Location Type"
                      onChange={(e) => setFormData({ ...formData, location_type: e.target.value })}
                    >
                      {cameraService.getCameraLocations().map(loc => (
                        <MenuItem key={loc.value} value={loc.value}>
                          {loc.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    required
                    label="Location Description"
                    value={formData.location_description}
                    onChange={(e) => setFormData({ ...formData, location_description: e.target.value })}
                    error={!!errors.location_description}
                    helperText={errors.location_description || 'Detailed location description'}
                    multiline
                    rows={2}
                  />
                </Grid>
              </Grid>
            </Paper>

            {/* Hardware Details */}
            <Paper elevation={0} sx={{ p: 2, mb: 3, bgcolor: 'grey.50' }}>
              <Typography variant="h6" gutterBottom>
                Hardware Details
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} md={4}>
                  <TextField
                    fullWidth
                    required
                    label="Manufacturer"
                    value={formData.manufacturer}
                    onChange={(e) => setFormData({ ...formData, manufacturer: e.target.value })}
                    error={!!errors.manufacturer}
                    helperText={errors.manufacturer}
                  />
                </Grid>
                <Grid item xs={12} md={4}>
                  <TextField
                    fullWidth
                    required
                    label="Model"
                    value={formData.model}
                    onChange={(e) => setFormData({ ...formData, model: e.target.value })}
                    error={!!errors.model}
                    helperText={errors.model}
                  />
                </Grid>
                <Grid item xs={12} md={4}>
                  <TextField
                    fullWidth
                    required
                    label="Serial Number"
                    value={formData.serial_number}
                    onChange={(e) => setFormData({ ...formData, serial_number: e.target.value })}
                    error={!!errors.serial_number}
                    helperText={errors.serial_number}
                    disabled={!!cameraId}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="MAC Address"
                    value={formData.mac_address}
                    onChange={(e) => setFormData({ ...formData, mac_address: e.target.value })}
                    helperText="Hardware MAC address"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Firmware Version"
                    value={formData.firmware_version}
                    onChange={(e) => setFormData({ ...formData, firmware_version: e.target.value })}
                    helperText="Current firmware version"
                  />
                </Grid>
              </Grid>
            </Paper>

            {/* Network Configuration */}
            <Paper elevation={0} sx={{ p: 2, mb: 3, bgcolor: 'grey.50' }}>
              <Typography variant="h6" gutterBottom>
                Network Configuration
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    required
                    label="IP Address"
                    value={formData.ip_address}
                    onChange={(e) => setFormData({ ...formData, ip_address: e.target.value })}
                    error={!!errors.ip_address}
                    helperText={errors.ip_address || 'Camera IP address (e.g., 192.168.1.100)'}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    required
                    type="number"
                    label="Port"
                    value={formData.port}
                    onChange={(e) => setFormData({ ...formData, port: parseInt(e.target.value) })}
                    error={!!errors.port}
                    helperText={errors.port || 'RTSP port (default: 554)'}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="RTSP URL"
                    value={formData.rtsp_url}
                    onChange={(e) => setFormData({ ...formData, rtsp_url: e.target.value })}
                    helperText="RTSP stream URL (optional)"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="ONVIF URL"
                    value={formData.onvif_url}
                    onChange={(e) => setFormData({ ...formData, onvif_url: e.target.value })}
                    helperText="ONVIF service URL (optional)"
                  />
                </Grid>
              </Grid>
            </Paper>

            {/* Technical Specifications */}
            <Paper elevation={0} sx={{ p: 2, mb: 3, bgcolor: 'grey.50' }}>
              <Typography variant="h6" gutterBottom>
                Technical Specifications
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} md={3}>
                  <FormControl fullWidth>
                    <InputLabel>Resolution</InputLabel>
                    <Select
                      value={formData.resolution}
                      label="Resolution"
                      onChange={(e) => setFormData({ ...formData, resolution: e.target.value })}
                    >
                      <MenuItem value="720p">720p (1MP)</MenuItem>
                      <MenuItem value="1080p">1080p (2MP)</MenuItem>
                      <MenuItem value="2K">2K (4MP)</MenuItem>
                      <MenuItem value="4K">4K (8MP)</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={3}>
                  <TextField
                    fullWidth
                    type="number"
                    label="Frame Rate (FPS)"
                    value={formData.frame_rate}
                    onChange={(e) => setFormData({ ...formData, frame_rate: parseInt(e.target.value) })}
                    helperText="Frames per second"
                  />
                </Grid>
                <Grid item xs={12} md={3}>
                  <TextField
                    fullWidth
                    label="Field of View"
                    value={formData.field_of_view}
                    onChange={(e) => setFormData({ ...formData, field_of_view: e.target.value })}
                    helperText="e.g., 90°, 120°"
                  />
                </Grid>
                <Grid item xs={12} md={3}>
                  <TextField
                    fullWidth
                    label="IR Distance (meters)"
                    value={formData.ir_distance}
                    onChange={(e) => setFormData({ ...formData, ir_distance: e.target.value })}
                    helperText="Night vision range"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <InputLabel>Weatherproof Rating</InputLabel>
                    <Select
                      value={formData.weatherproof_rating}
                      label="Weatherproof Rating"
                      onChange={(e) => setFormData({ ...formData, weatherproof_rating: e.target.value })}
                    >
                      <MenuItem value="IP54">IP54 (Dust/Splash)</MenuItem>
                      <MenuItem value="IP65">IP65 (Dust/Water)</MenuItem>
                      <MenuItem value="IP66">IP66 (Heavy Water)</MenuItem>
                      <MenuItem value="IP67">IP67 (Waterproof)</MenuItem>
                      <MenuItem value="IP68">IP68 (Submersible)</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={6}>
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={formData.audio_support}
                        onChange={(e) => setFormData({ ...formData, audio_support: e.target.checked })}
                      />
                    }
                    label="Audio Support Available"
                  />
                </Grid>
              </Grid>
            </Paper>

            {/* Installation Details */}
            <Paper elevation={0} sx={{ p: 2, mb: 3, bgcolor: 'grey.50' }}>
              <Typography variant="h6" gutterBottom>
                Installation & Warranty
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <DatePicker
                    label="Installation Date"
                    value={formData.installation_date}
                    onChange={(date) => setFormData({ ...formData, installation_date: date || new Date() })}
                    slotProps={{ textField: { fullWidth: true, required: true } }}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <DatePicker
                    label="Warranty Expiry Date"
                    value={formData.warranty_expiry_date}
                    onChange={(date) => setFormData({ ...formData, warranty_expiry_date: date })}
                    slotProps={{ textField: { fullWidth: true } }}
                  />
                </Grid>
              </Grid>
            </Paper>

            {/* Settings */}
            <Paper elevation={0} sx={{ p: 2, mb: 3, bgcolor: 'grey.50' }}>
              <Typography variant="h6" gutterBottom>
                Camera Settings
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} md={4}>
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={formData.recording_enabled}
                        onChange={(e) => setFormData({ ...formData, recording_enabled: e.target.checked })}
                      />
                    }
                    label="Enable Recording"
                  />
                </Grid>
                <Grid item xs={12} md={4}>
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={formData.audio_recording_enabled}
                        onChange={(e) => setFormData({ ...formData, audio_recording_enabled: e.target.checked })}
                        disabled={!formData.audio_support}
                      />
                    }
                    label="Enable Audio Recording"
                  />
                </Grid>
                <Grid item xs={12} md={4}>
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={formData.is_critical}
                        onChange={(e) => setFormData({ ...formData, is_critical: e.target.checked })}
                      />
                    }
                    label="Mark as Critical Camera"
                  />
                </Grid>
              </Grid>
            </Paper>

            {/* Action Buttons */}
            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
              <Button
                variant="outlined"
                startIcon={<Cancel />}
                onClick={onCancel}
                disabled={loading}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                variant="contained"
                startIcon={<Save />}
                disabled={loading}
              >
                {loading ? 'Saving...' : cameraId ? 'Update Camera' : 'Create Camera'}
              </Button>
            </Box>
          </CardContent>
        </Card>
      </Box>
    </LocalizationProvider>
  );
};

export default CameraForm;
