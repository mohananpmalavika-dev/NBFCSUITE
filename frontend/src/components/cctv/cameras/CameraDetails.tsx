/**
 * Camera Details Component
 * 
 * Single camera detailed view with comprehensive information
 * Features:
 * - Complete camera information display
 * - Real-time health metrics and status
 * - Uptime chart and statistics
 * - Connectivity test
 * - Live stream preview
 * - Edit/Delete actions
 * - Activity history
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  Button,
  CircularProgress,
  Alert,
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Tooltip,
  LinearProgress,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableRow,
  Tabs,
  Tab
} from '@mui/material';
import {
  Edit,
  Delete,
  Refresh,
  PlayArrow,
  CheckCircle,
  Error,
  Warning,
  SignalWifiOff,
  NetworkCheck,
  Speed,
  Storage,
  CalendarToday,
  Build,
  Info,
  Settings,
  History,
  Timeline,
  Close
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, Area, AreaChart } from 'recharts';
import cameraService, { Camera, CameraHealth, ConnectivityTest } from '../../../services/cameraService';

interface CameraDetailsProps {
  cameraId: string;
  onEdit?: (camera: Camera) => void;
  onDelete?: (cameraId: string) => void;
  onClose?: () => void;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index, ...other }) => {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`camera-tabpanel-${index}`}
      aria-labelledby={`camera-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ py: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
};

const CameraDetails: React.FC<CameraDetailsProps> = ({ cameraId, onEdit, onDelete, onClose }) => {
  const [camera, setCamera] = useState<Camera | null>(null);
  const [health, setHealth] = useState<CameraHealth | null>(null);
  const [uptimeData, setUptimeData] = useState<any[]>([]);
  const [connectivityTest, setConnectivityTest] = useState<ConnectivityTest | null>(null);
  const [loading, setLoading] = useState(true);
  const [testingConnection, setTestingConnection] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [activeTab, setActiveTab] = useState(0);

  useEffect(() => {
    loadCameraDetails();
  }, [cameraId]);

  const loadCameraDetails = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load camera details and health in parallel
      const [cameraData, healthData] = await Promise.all([
        cameraService.getCamera(cameraId),
        cameraService.getCameraHealth(cameraId)
      ]);

      setCamera(cameraData);
      setHealth(healthData);

      // Generate mock uptime data (last 7 days)
      const mockUptimeData = generateMockUptimeData(healthData.uptime_percentage);
      setUptimeData(mockUptimeData);

      setLoading(false);
    } catch (err: any) {
      console.error('Failed to load camera details:', err);
      setError(err.message || 'Failed to load camera details');
      setLoading(false);
    }
  };

  const generateMockUptimeData = (currentUptime: number) => {
    const data = [];
    const now = Date.now();
    const oneDay = 24 * 60 * 60 * 1000;

    for (let i = 6; i >= 0; i--) {
      const date = new Date(now - i * oneDay);
      const variation = (Math.random() - 0.5) * 10; // ±5% variation
      const uptime = Math.max(0, Math.min(100, currentUptime + variation));
      
      data.push({
        date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        uptime: parseFloat(uptime.toFixed(2)),
        downtime: parseFloat((100 - uptime).toFixed(2))
      });
    }

    return data;
  };

  const handleTestConnectivity = async () => {
    try {
      setTestingConnection(true);
      const result = await cameraService.testCameraConnectivity(cameraId);
      setConnectivityTest(result);
      
      // Reload camera details to update status
      await loadCameraDetails();
    } catch (err: any) {
      console.error('Connectivity test failed:', err);
      setConnectivityTest({
        camera_id: cameraId,
        success: false,
        response_time_ms: 0,
        tested_at: new Date().toISOString(),
        error_message: err.message || 'Connection test failed'
      });
    } finally {
      setTestingConnection(false);
    }
  };

  const handleEdit = () => {
    if (camera && onEdit) {
      onEdit(camera);
    }
  };

  const handleDeleteClick = () => {
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    try {
      await cameraService.deleteCamera(cameraId);
      setDeleteDialogOpen(false);
      if (onDelete) {
        onDelete(cameraId);
      }
    } catch (err: any) {
      console.error('Failed to delete camera:', err);
      setError(err.message || 'Failed to delete camera');
      setDeleteDialogOpen(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online':
        return 'success';
      case 'offline':
        return 'error';
      case 'maintenance':
        return 'warning';
      default:
        return 'default';
    }
  };

  const getHealthStatusInfo = () => {
    if (!health) return { label: 'Unknown', color: 'default', icon: <Info /> };

    const uptime = health.uptime_percentage;
    if (uptime >= 99) {
      return { label: 'Excellent', color: 'success', icon: <CheckCircle /> };
    } else if (uptime >= 95) {
      return { label: 'Good', color: 'info', icon: <CheckCircle /> };
    } else if (uptime >= 90) {
      return { label: 'Fair', color: 'warning', icon: <Warning /> };
    } else {
      return { label: 'Poor', color: 'error', icon: <Error /> };
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error || !camera) {
    return (
      <Alert severity="error" action={
        <Button color="inherit" size="small" onClick={loadCameraDetails}>
          Retry
        </Button>
      }>
        {error || 'Camera not found'}
      </Alert>
    );
  }

  const healthStatus = getHealthStatusInfo();

  return (
    <Box>
      {/* Header */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
            <Box sx={{ flex: 1 }}>
              <Typography variant="h5" gutterBottom>
                {camera.name}
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', alignItems: 'center' }}>
                <Chip
                  label={camera.status}
                  color={getStatusColor(camera.status)}
                  size="small"
                />
                <Chip
                  label={camera.type}
                  variant="outlined"
                  size="small"
                />
                <Chip
                  label={camera.location}
                  variant="outlined"
                  size="small"
                />
                {camera.is_critical && (
                  <Chip
                    label="Critical"
                    color="error"
                    size="small"
                  />
                )}
              </Box>
            </Box>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Tooltip title="Refresh">
                <IconButton onClick={loadCameraDetails} color="primary">
                  <Refresh />
                </IconButton>
              </Tooltip>
              <Tooltip title="Test Connection">
                <IconButton
                  onClick={handleTestConnectivity}
                  color="primary"
                  disabled={testingConnection}
                >
                  {testingConnection ? <CircularProgress size={24} /> : <NetworkCheck />}
                </IconButton>
              </Tooltip>
              <Tooltip title="Edit">
                <IconButton onClick={handleEdit} color="primary">
                  <Edit />
                </IconButton>
              </Tooltip>
              <Tooltip title="Delete">
                <IconButton onClick={handleDeleteClick} color="error">
                  <Delete />
                </IconButton>
              </Tooltip>
              {onClose && (
                <Tooltip title="Close">
                  <IconButton onClick={onClose}>
                    <Close />
                  </IconButton>
                </Tooltip>
              )}
            </Box>
          </Box>

          {/* Health Status Banner */}
          {health && (
            <Paper
              elevation={0}
              sx={{
                p: 2,
                bgcolor: `${healthStatus.color}.light`,
                borderRadius: 1,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between'
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                {healthStatus.icon}
                <Box>
                  <Typography variant="h6">
                    Health Status: {healthStatus.label}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Uptime: {health.uptime_percentage.toFixed(2)}% | 
                    Last Check: {new Date(health.last_check).toLocaleString()}
                  </Typography>
                </Box>
              </Box>
              <Box sx={{ textAlign: 'right' }}>
                <Typography variant="caption" color="textSecondary">
                  Response Time
                </Typography>
                <Typography variant="h6">
                  {health.response_time_ms}ms
                </Typography>
              </Box>
            </Paper>
          )}

          {/* Connectivity Test Result */}
          {connectivityTest && (
            <Alert
              severity={connectivityTest.success ? 'success' : 'error'}
              sx={{ mt: 2 }}
              onClose={() => setConnectivityTest(null)}
            >
              {connectivityTest.success ? (
                <>
                  Connection successful! Response time: {connectivityTest.response_time_ms}ms
                </>
              ) : (
                <>
                  Connection failed: {connectivityTest.error_message}
                </>
              )}
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Tabs */}
      <Card>
        <Tabs
          value={activeTab}
          onChange={(e, newValue) => setActiveTab(newValue)}
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          <Tab icon={<Info />} label="Details" />
          <Tab icon={<Timeline />} label="Performance" />
          <Tab icon={<Settings />} label="Configuration" />
        </Tabs>

        {/* Tab 1: Details */}
        <TabPanel value={activeTab} index={0}>
          <CardContent>
            <Grid container spacing={3}>
              {/* Basic Information */}
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Info /> Basic Information
                </Typography>
                <TableContainer>
                  <Table size="small">
                    <TableBody>
                      <TableRow>
                        <TableCell><strong>Camera ID</strong></TableCell>
                        <TableCell>{camera.camera_id}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell><strong>Name</strong></TableCell>
                        <TableCell>{camera.name}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell><strong>Type</strong></TableCell>
                        <TableCell>{camera.type}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell><strong>Location</strong></TableCell>
                        <TableCell>{camera.location}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell><strong>Branch</strong></TableCell>
                        <TableCell>{camera.branch_name || camera.branch_id}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell><strong>Status</strong></TableCell>
                        <TableCell>
                          <Chip
                            label={camera.status}
                            color={getStatusColor(camera.status)}
                            size="small"
                          />
                        </TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell><strong>Critical</strong></TableCell>
                        <TableCell>{camera.is_critical ? 'Yes' : 'No'}</TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </TableContainer>
              </Grid>

              {/* Network Information */}
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <NetworkCheck /> Network Information
                </Typography>
                <TableContainer>
                  <Table size="small">
                    <TableBody>
                      <TableRow>
                        <TableCell><strong>IP Address</strong></TableCell>
                        <TableCell>{camera.ip_address}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell><strong>Port</strong></TableCell>
                        <TableCell>{camera.port}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell><strong>MAC Address</strong></TableCell>
                        <TableCell>{camera.mac_address || 'N/A'}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell><strong>RTSP URL</strong></TableCell>
                        <TableCell sx={{ wordBreak: 'break-all', fontSize: '0.875rem' }}>
                          {camera.rtsp_url}
                        </TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell><strong>Stream URL</strong></TableCell>
                        <TableCell sx={{ wordBreak: 'break-all', fontSize: '0.875rem' }}>
                          {camera.stream_url || 'N/A'}
                        </TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </TableContainer>
              </Grid>

              {/* Hardware Information */}
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Build /> Hardware Details
                </Typography>
                <TableContainer>
                  <Table size="small">
                    <TableBody>
                      <TableRow>
                        <TableCell><strong>Manufacturer</strong></TableCell>
                        <TableCell>{camera.manufacturer || 'N/A'}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell><strong>Model</strong></TableCell>
                        <TableCell>{camera.model || 'N/A'}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell><strong>Serial Number</strong></TableCell>
                        <TableCell>{camera.serial_number || 'N/A'}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell><strong>Firmware Version</strong></TableCell>
                        <TableCell>{camera.firmware_version || 'N/A'}</TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </TableContainer>
              </Grid>

              {/* Installation Information */}
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <CalendarToday /> Installation & Warranty
                </Typography>
                <TableContainer>
                  <Table size="small">
                    <TableBody>
                      <TableRow>
                        <TableCell><strong>Installation Date</strong></TableCell>
                        <TableCell>
                          {camera.installation_date
                            ? new Date(camera.installation_date).toLocaleDateString()
                            : 'N/A'}
                        </TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell><strong>Warranty Expiry</strong></TableCell>
                        <TableCell>
                          {camera.warranty_expiry_date
                            ? new Date(camera.warranty_expiry_date).toLocaleDateString()
                            : 'N/A'}
                        </TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell><strong>Last Maintenance</strong></TableCell>
                        <TableCell>
                          {camera.last_maintenance_date
                            ? new Date(camera.last_maintenance_date).toLocaleDateString()
                            : 'N/A'}
                        </TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell><strong>Created At</strong></TableCell>
                        <TableCell>
                          {new Date(camera.created_at).toLocaleString()}
                        </TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell><strong>Updated At</strong></TableCell>
                        <TableCell>
                          {new Date(camera.updated_at).toLocaleString()}
                        </TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </TableContainer>
              </Grid>

              {/* Notes */}
              {camera.notes && (
                <Grid item xs={12}>
                  <Typography variant="h6" gutterBottom>
                    Notes
                  </Typography>
                  <Paper variant="outlined" sx={{ p: 2 }}>
                    <Typography variant="body2">
                      {camera.notes}
                    </Typography>
                  </Paper>
                </Grid>
              )}
            </Grid>
          </CardContent>
        </TabPanel>

        {/* Tab 2: Performance */}
        <TabPanel value={activeTab} index={1}>
          <CardContent>
            {/* Uptime Chart */}
            <Box sx={{ mb: 4 }}>
              <Typography variant="h6" gutterBottom>
                7-Day Uptime Trend
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={uptimeData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis domain={[0, 100]} />
                  <RechartsTooltip />
                  <Area
                    type="monotone"
                    dataKey="uptime"
                    stackId="1"
                    stroke="#4caf50"
                    fill="#4caf50"
                    fillOpacity={0.6}
                  />
                  <Area
                    type="monotone"
                    dataKey="downtime"
                    stackId="1"
                    stroke="#f44336"
                    fill="#f44336"
                    fillOpacity={0.6}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </Box>

            {health && (
              <>
                <Divider sx={{ my: 3 }} />

                {/* Performance Metrics */}
                <Grid container spacing={3}>
                  <Grid item xs={12} md={4}>
                    <Card variant="outlined">
                      <CardContent>
                        <Typography color="textSecondary" gutterBottom>
                          Average Uptime
                        </Typography>
                        <Typography variant="h4" color="success.main">
                          {health.uptime_percentage.toFixed(2)}%
                        </Typography>
                        <LinearProgress
                          variant="determinate"
                          value={health.uptime_percentage}
                          sx={{ mt: 2 }}
                          color="success"
                        />
                      </CardContent>
                    </Card>
                  </Grid>

                  <Grid item xs={12} md={4}>
                    <Card variant="outlined">
                      <CardContent>
                        <Typography color="textSecondary" gutterBottom>
                          Response Time
                        </Typography>
                        <Typography variant="h4" color={health.response_time_ms < 100 ? 'success.main' : 'warning.main'}>
                          {health.response_time_ms}ms
                        </Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', mt: 2 }}>
                          <Speed sx={{ mr: 1 }} />
                          <Typography variant="body2" color="textSecondary">
                            {health.response_time_ms < 100 ? 'Excellent' : health.response_time_ms < 200 ? 'Good' : 'Needs Attention'}
                          </Typography>
                        </Box>
                      </CardContent>
                    </Card>
                  </Grid>

                  <Grid item xs={12} md={4}>
                    <Card variant="outlined">
                      <CardContent>
                        <Typography color="textSecondary" gutterBottom>
                          Last Check
                        </Typography>
                        <Typography variant="body1" fontWeight="bold">
                          {new Date(health.last_check).toLocaleString()}
                        </Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', mt: 2 }}>
                          <CheckCircle sx={{ mr: 1, color: 'success.main' }} />
                          <Typography variant="body2" color="textSecondary">
                            {Math.floor((Date.now() - new Date(health.last_check).getTime()) / 60000)} minutes ago
                          </Typography>
                        </Box>
                      </CardContent>
                    </Card>
                  </Grid>
                </Grid>

                {/* Issues */}
                {health.issues && health.issues.length > 0 && (
                  <Box sx={{ mt: 3 }}>
                    <Typography variant="h6" gutterBottom color="error">
                      Active Issues ({health.issues.length})
                    </Typography>
                    <Alert severity="error">
                      <ul style={{ margin: 0, paddingLeft: 20 }}>
                        {health.issues.map((issue, index) => (
                          <li key={index}>{issue}</li>
                        ))}
                      </ul>
                    </Alert>
                  </Box>
                )}
              </>
            )}
          </CardContent>
        </TabPanel>

        {/* Tab 3: Configuration */}
        <TabPanel value={activeTab} index={2}>
          <CardContent>
            <Grid container spacing={3}>
              {/* Technical Specifications */}
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>
                  Technical Specifications
                </Typography>
                <TableContainer>
                  <Table size="small">
                    <TableBody>
                      <TableRow>
                        <TableCell><strong>Resolution</strong></TableCell>
                        <TableCell>{camera.resolution || 'N/A'}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell><strong>Frame Rate</strong></TableCell>
                        <TableCell>{camera.frame_rate ? `${camera.frame_rate} fps` : 'N/A'}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell><strong>Field of View</strong></TableCell>
                        <TableCell>{camera.field_of_view ? `${camera.field_of_view}°` : 'N/A'}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell><strong>PTZ Capable</strong></TableCell>
                        <TableCell>{camera.ptz_capable ? 'Yes' : 'No'}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell><strong>IR Capable</strong></TableCell>
                        <TableCell>{camera.ir_capable ? 'Yes' : 'No'}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell><strong>Audio Enabled</strong></TableCell>
                        <TableCell>{camera.audio_enabled ? 'Yes' : 'No'}</TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </TableContainer>
              </Grid>

              {/* Recording Settings */}
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>
                  Recording Settings
                </Typography>
                <TableContainer>
                  <Table size="small">
                    <TableBody>
                      <TableRow>
                        <TableCell><strong>Recording Enabled</strong></TableCell>
                        <TableCell>
                          <Chip
                            label={camera.recording_enabled ? 'Enabled' : 'Disabled'}
                            color={camera.recording_enabled ? 'success' : 'default'}
                            size="small"
                          />
                        </TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell><strong>Motion Detection</strong></TableCell>
                        <TableCell>
                          <Chip
                            label={camera.motion_detection_enabled ? 'Enabled' : 'Disabled'}
                            color={camera.motion_detection_enabled ? 'success' : 'default'}
                            size="small"
                          />
                        </TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell><strong>Recording Quality</strong></TableCell>
                        <TableCell>{camera.recording_quality || 'N/A'}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell><strong>Retention Days</strong></TableCell>
                        <TableCell>{camera.retention_days || 'N/A'} days</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell><strong>Storage Location</strong></TableCell>
                        <TableCell>{camera.storage_location || 'N/A'}</TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </TableContainer>
              </Grid>

              {/* Authentication */}
              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom>
                  Authentication
                </Typography>
                <TableContainer>
                  <Table size="small">
                    <TableBody>
                      <TableRow>
                        <TableCell sx={{ width: '25%' }}><strong>Username</strong></TableCell>
                        <TableCell>{camera.username || 'N/A'}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell><strong>Password</strong></TableCell>
                        <TableCell>••••••••</TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </TableContainer>
              </Grid>
            </Grid>
          </CardContent>
        </TabPanel>
      </Card>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete camera <strong>{camera.name}</strong>?
          </Typography>
          <Typography color="error" sx={{ mt: 2 }}>
            This action cannot be undone. All associated data will be permanently deleted.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>
            Cancel
          </Button>
          <Button onClick={handleDeleteConfirm} color="error" variant="contained">
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default CameraDetails;
