/**
 * DVR/NVR List Component
 * 
 * Display and manage all DVR/NVR recording devices.
 * Shows device health, storage status, and recording information.
 */

import React, { useState, useEffect } from 'react';
import {
  Box, Card, CardContent, Typography, Table, TableBody, TableCell,
  TableContainer, TableHead, TableRow, Paper, Button, Chip, IconButton,
  LinearProgress, Alert, Dialog, DialogTitle, DialogContent, DialogActions,
  Grid, Tooltip, TextField, MenuItem
} from '@mui/material';
import {
  Add, Edit, Visibility, Storage, Computer, Warning, CheckCircle,
  Error, Backup, VideoLibrary, Refresh
} from '@mui/icons-material';
import { recordingService, DVRNVRConfig } from '../../../services/recordingService';

export const DVRNVRList: React.FC = () => {
  const [devices, setDevices] = useState<DVRNVRConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedDevice, setSelectedDevice] = useState<DVRNVRConfig | null>(null);
  const [detailsOpen, setDetailsOpen] = useState(false);
  
  // Filters
  const [deviceTypeFilter, setDeviceTypeFilter] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('');

  useEffect(() => {
    loadDevices();
  }, [deviceTypeFilter, statusFilter]);

  const loadDevices = async () => {
    try {
      setLoading(true);
      const response = await recordingService.listDVRNVR({
        device_type: deviceTypeFilter || undefined,
        status: statusFilter || undefined
      });
      setDevices(response.data.configs);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to load devices');
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetails = async (device: DVRNVRConfig) => {
    setSelectedDevice(device);
    setDetailsOpen(true);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'success';
      case 'inactive': return 'default';
      case 'maintenance': return 'warning';
      case 'error': return 'error';
      default: return 'default';
    }
  };

  const getHealthColor = (utilization: number) => {
    if (utilization >= 90) return 'error';
    if (utilization >= 80) return 'warning';
    if (utilization >= 70) return 'info';
    return 'success';
  };

  const calculateUtilization = (device: DVRNVRConfig) => {
    return (device.used_storage_tb / device.total_storage_tb) * 100;
  };

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <LinearProgress />
        <Typography sx={{ mt: 2, textAlign: 'center' }}>
          Loading DVR/NVR devices...
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
          DVR/NVR Devices
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={loadDevices}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<Add />}
            href="/cctv/recording/devices/new"
          >
            Add Device
          </Button>
        </Box>
      </Box>

      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                select
                label="Device Type"
                value={deviceTypeFilter}
                onChange={(e) => setDeviceTypeFilter(e.target.value)}
              >
                <MenuItem value="">All Types</MenuItem>
                <MenuItem value="DVR">DVR</MenuItem>
                <MenuItem value="NVR">NVR</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                select
                label="Status"
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
              >
                <MenuItem value="">All Status</MenuItem>
                <MenuItem value="active">Active</MenuItem>
                <MenuItem value="inactive">Inactive</MenuItem>
                <MenuItem value="maintenance">Maintenance</MenuItem>
              </TextField>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Devices Table */}
      <Card>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Device</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Location</TableCell>
                <TableCell>Channels</TableCell>
                <TableCell>Storage</TableCell>
                <TableCell>Health</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {devices.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={8} align="center">
                    <Box sx={{ py: 3 }}>
                      <Computer sx={{ fontSize: 60, color: 'action.disabled', mb: 2 }} />
                      <Typography variant="h6" color="text.secondary">
                        No devices found
                      </Typography>
                      <Button
                        variant="contained"
                        startIcon={<Add />}
                        sx={{ mt: 2 }}
                        href="/cctv/recording/devices/new"
                      >
                        Add First Device
                      </Button>
                    </Box>
                  </TableCell>
                </TableRow>
              ) : (
                devices.map((device) => {
                  const utilization = calculateUtilization(device);
                  return (
                    <TableRow key={device.id} hover>
                      <TableCell>
                        <Box>
                          <Typography variant="body1" sx={{ fontWeight: 'medium' }}>
                            {device.device_name}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            {device.manufacturer} {device.model}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip label={device.device_type} size="small" />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">{device.location}</Typography>
                      </TableCell>
                      <TableCell>
                        <Box>
                          <Typography variant="body2">
                            {device.used_channels} / {device.total_channels}
                          </Typography>
                          <LinearProgress
                            variant="determinate"
                            value={(device.used_channels / device.total_channels) * 100}
                            sx={{ mt: 0.5 }}
                          />
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Box>
                          <Typography variant="body2">
                            {device.used_storage_tb.toFixed(1)} / {device.total_storage_tb.toFixed(1)} TB
                          </Typography>
                          <LinearProgress
                            variant="determinate"
                            value={utilization}
                            color={getHealthColor(utilization)}
                            sx={{ mt: 0.5 }}
                          />
                          <Typography variant="caption" color="text.secondary">
                            {utilization.toFixed(1)}% used
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                          {device.storage_alert_active ? (
                            <Tooltip title="Storage alert active">
                              <Warning color="error" fontSize="small" />
                            </Tooltip>
                          ) : (
                            <Tooltip title="Healthy">
                              <CheckCircle color="success" fontSize="small" />
                            </Tooltip>
                          )}
                          <Typography variant="body2">
                            {device.uptime_percentage.toFixed(1)}%
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={device.status}
                          color={getStatusColor(device.status)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell align="right">
                        <IconButton
                          size="small"
                          onClick={() => handleViewDetails(device)}
                          title="View Details"
                        >
                          <Visibility />
                        </IconButton>
                        <IconButton
                          size="small"
                          href={`/cctv/recording/devices/${device.id}/edit`}
                          title="Edit"
                        >
                          <Edit />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  );
                })
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Card>

      {/* Device Details Dialog */}
      <Dialog
        open={detailsOpen}
        onClose={() => setDetailsOpen(false)}
        maxWidth="md"
        fullWidth
      >
        {selectedDevice && (
          <>
            <DialogTitle>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="h6">{selectedDevice.device_name}</Typography>
                <Chip
                  label={selectedDevice.status}
                  color={getStatusColor(selectedDevice.status)}
                />
              </Box>
            </DialogTitle>
            <DialogContent>
              <Grid container spacing={2}>
                {/* Device Info */}
                <Grid item xs={12}>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                    Device Information
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">Type</Typography>
                  <Typography variant="body1">{selectedDevice.device_type}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">Location</Typography>
                  <Typography variant="body1">{selectedDevice.location}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">Manufacturer</Typography>
                  <Typography variant="body1">{selectedDevice.manufacturer}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">Model</Typography>
                  <Typography variant="body1">{selectedDevice.model}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">IP Address</Typography>
                  <Typography variant="body1">{selectedDevice.ip_address}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">Serial Number</Typography>
                  <Typography variant="body1">{selectedDevice.serial_number}</Typography>
                </Grid>

                {/* Storage Info */}
                <Grid item xs={12} sx={{ mt: 2 }}>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                    Storage Information
                  </Typography>
                </Grid>
                <Grid item xs={4}>
                  <Typography variant="body2" color="text.secondary">Total Capacity</Typography>
                  <Typography variant="h6">{selectedDevice.total_storage_tb.toFixed(1)} TB</Typography>
                </Grid>
                <Grid item xs={4}>
                  <Typography variant="body2" color="text.secondary">Used</Typography>
                  <Typography variant="h6">{selectedDevice.used_storage_tb.toFixed(1)} TB</Typography>
                </Grid>
                <Grid item xs={4}>
                  <Typography variant="body2" color="text.secondary">Available</Typography>
                  <Typography variant="h6">{selectedDevice.available_storage_tb.toFixed(1)} TB</Typography>
                </Grid>

                {/* Recording Settings */}
                <Grid item xs={12} sx={{ mt: 2 }}>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                    Recording Settings
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">Quality</Typography>
                  <Typography variant="body1">{selectedDevice.recording_quality}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">Retention (Hot)</Typography>
                  <Typography variant="body1">{selectedDevice.retention_days_hot} days</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">Channels</Typography>
                  <Typography variant="body1">
                    {selectedDevice.used_channels} / {selectedDevice.total_channels}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">Retention (Cold)</Typography>
                  <Typography variant="body1">{selectedDevice.retention_days_cold} days</Typography>
                </Grid>

                {/* Health Status */}
                <Grid item xs={12} sx={{ mt: 2 }}>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                    Health Status
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">Uptime</Typography>
                  <Typography variant="body1">{selectedDevice.uptime_percentage.toFixed(2)}%</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">Storage Alert</Typography>
                  <Chip
                    label={selectedDevice.storage_alert_active ? 'Active' : 'None'}
                    color={selectedDevice.storage_alert_active ? 'error' : 'success'}
                    size="small"
                  />
                </Grid>
              </Grid>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setDetailsOpen(false)}>Close</Button>
              <Button
                variant="contained"
                startIcon={<Edit />}
                href={`/cctv/recording/devices/${selectedDevice.id}/edit`}
              >
                Edit Device
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Box>
  );
};

export default DVRNVRList;
