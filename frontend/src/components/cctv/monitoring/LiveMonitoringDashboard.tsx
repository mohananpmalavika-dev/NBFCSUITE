/**
 * Live Monitoring Dashboard
 * 
 * Control room interface for 24/7 surveillance monitoring
 * Features:
 * - Multi-camera grid view
 * - Real-time alerts
 * - PTZ camera control
 * - Event bookmarking
 * - Shift management
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  IconButton,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  Badge,
  Tooltip,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  CircularProgress
} from '@mui/material';
import {
  Videocam,
  GridView,
  Fullscreen,
  VolumeUp,
  VolumeOff,
  Bookmark,
  Warning,
  CheckCircle,
  Refresh,
  CameraAlt,
  AspectRatio
} from '@mui/icons-material';
import monitoringService, {
  LiveCamera,
  MonitoringDashboard,
  ActiveAlert
} from '../../../services/monitoringService';

const LiveMonitoringDashboard: React.FC = () => {
  const [cameras, setCameras] = useState<LiveCamera[]>([]);
  const [dashboard, setDashboard] = useState<MonitoringDashboard | null>(null);
  const [activeAlerts, setActiveAlerts] = useState<ActiveAlert[]>([]);
  const [loading, setLoading] = useState(true);
  const [gridLayout, setGridLayout] = useState<number>(4); // 4, 9, 16 cameras
  const [selectedCamera, setSelectedCamera] = useState<LiveCamera | null>(null);
  const [fullscreenCamera, setFullscreenCamera] = useState<string | null>(null);
  const [bookmarkDialog, setBookmarkDialog] = useState(false);
  const [bookmarkData, setBookmarkData] = useState({
    camera_id: '',
    bookmark_name: '',
    description: ''
  });
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    loadMonitoringData();

    // Auto-refresh every 5 seconds
    if (autoRefresh) {
      const interval = setInterval(() => {
        loadMonitoringData();
      }, 5000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const loadMonitoringData = async () => {
    try {
      setLoading(true);

      // Load live cameras
      const camerasData = await monitoringService.getLiveCameras({
        page: 1,
        page_size: 50
      });
      setCameras(camerasData.cameras);

      // Load dashboard stats
      const dashboardData = await monitoringService.getMonitoringDashboard();
      setDashboard(dashboardData);

      // Load active alerts
      const alertsData = await monitoringService.getActiveAlerts({
        limit: 50
      });
      setActiveAlerts(alertsData.alerts);

      setLoading(false);
    } catch (error) {
      console.error('Failed to load monitoring data:', error);
      setLoading(false);
    }
  };

  const handleGridLayoutChange = (layout: number) => {
    setGridLayout(layout);
  };

  const handleCameraClick = (camera: LiveCamera) => {
    setSelectedCamera(camera);
  };

  const handleFullscreen = (cameraId: string) => {
    setFullscreenCamera(cameraId);
  };

  const handleBookmark = (camera: LiveCamera) => {
    setBookmarkData({
      camera_id: camera.id,
      bookmark_name: '',
      description: ''
    });
    setBookmarkDialog(true);
  };

  const saveBookmark = async () => {
    try {
      await monitoringService.createBookmark(bookmarkData);
      setBookmarkDialog(false);
      setBookmarkData({ camera_id: '', bookmark_name: '', description: '' });
      alert('Bookmark created successfully');
    } catch (error) {
      console.error('Failed to create bookmark:', error);
      alert('Failed to create bookmark');
    }
  };

  const acknowledgeAlert = async (alertId: string) => {
    try {
      await monitoringService.acknowledgeAlert(alertId);
      setActiveAlerts(prev => prev.filter(a => a.id !== alertId));
    } catch (error) {
      console.error('Failed to acknowledge alert:', error);
    }
  };

  const getGridColumns = () => {
    switch (gridLayout) {
      case 4: return 2; // 2x2
      case 9: return 3; // 3x3
      case 16: return 4; // 4x4
      default: return 2;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'error';
      case 'high': return 'warning';
      case 'medium': return 'info';
      case 'low': return 'default';
      default: return 'default';
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4">
          <Videocam sx={{ mr: 1, verticalAlign: 'middle' }} />
          Live Monitoring - Control Room
        </Typography>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Grid Layout</InputLabel>
            <Select
              value={gridLayout}
              label="Grid Layout"
              onChange={(e) => handleGridLayoutChange(Number(e.target.value))}
            >
              <MenuItem value={4}>2x2 (4 cameras)</MenuItem>
              <MenuItem value={9}>3x3 (9 cameras)</MenuItem>
              <MenuItem value={16}>4x4 (16 cameras)</MenuItem>
            </Select>
          </FormControl>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={loadMonitoringData}
          >
            Refresh
          </Button>
          <Chip
            label={`Auto-refresh: ${autoRefresh ? 'ON' : 'OFF'}`}
            color={autoRefresh ? 'success' : 'default'}
            onClick={() => setAutoRefresh(!autoRefresh)}
          />
        </Box>
      </Box>

      {/* Dashboard Stats */}
      {dashboard && (
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Total Cameras
                </Typography>
                <Typography variant="h3">{dashboard.cameras.total}</Typography>
                <Typography variant="body2" color="success.main">
                  {dashboard.cameras.online} Online
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Availability
                </Typography>
                <Typography variant="h3">
                  {dashboard.cameras.availability_percentage.toFixed(1)}%
                </Typography>
                <Typography variant="body2">
                  System Health
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card sx={{ bgcolor: activeAlerts.length > 0 ? 'warning.light' : 'inherit' }}>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Active Alerts
                </Typography>
                <Typography variant="h3">{dashboard.alerts.active}</Typography>
                <Typography variant="body2" color="error.main">
                  {dashboard.alerts.critical} Critical
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Alerts (Last Hour)
                </Typography>
                <Typography variant="h3">{dashboard.alerts.last_hour}</Typography>
                <Typography variant="body2">
                  Recent Activity
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Active Alerts Bar */}
      {activeAlerts.length > 0 && (
        <Alert 
          severity="warning" 
          sx={{ mb: 3 }}
          action={
            <Button color="inherit" size="small" onClick={loadMonitoringData}>
              Refresh Alerts
            </Button>
          }
        >
          <Typography variant="subtitle2">
            {activeAlerts.length} Active Alerts Requiring Attention
          </Typography>
          <Box sx={{ mt: 1, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            {activeAlerts.slice(0, 5).map(alert => (
              <Chip
                key={alert.id}
                label={`${alert.alert_type} - ${alert.alert_severity}`}
                color={getSeverityColor(alert.alert_severity) as any}
                size="small"
                onDelete={() => acknowledgeAlert(alert.id)}
              />
            ))}
            {activeAlerts.length > 5 && (
              <Chip label={`+${activeAlerts.length - 5} more`} size="small" />
            )}
          </Box>
        </Alert>
      )}

      {/* Camera Grid */}
      <Grid container spacing={2}>
        {cameras.slice(0, gridLayout).map((camera) => (
          <Grid item xs={12} sm={6} md={12 / getGridColumns()} key={camera.id}>
            <Card 
              sx={{ 
                position: 'relative',
                border: selectedCamera?.id === camera.id ? '2px solid' : 'none',
                borderColor: 'primary.main',
                cursor: 'pointer'
              }}
              onClick={() => handleCameraClick(camera)}
            >
              <CardContent>
                {/* Camera Header */}
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <CameraAlt color={camera.status === 'online' ? 'success' : 'error'} />
                    <Typography variant="subtitle2" noWrap>
                      {camera.camera_name}
                    </Typography>
                  </Box>
                  <Box>
                    <Chip 
                      label={camera.status} 
                      size="small" 
                      color={camera.status === 'online' ? 'success' : 'error'}
                    />
                  </Box>
                </Box>

                {/* Camera Video Feed Placeholder */}
                <Box
                  sx={{
                    bgcolor: 'black',
                    height: 200,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    mb: 1,
                    position: 'relative'
                  }}
                >
                  <Videocam sx={{ fontSize: 60, color: 'grey.600' }} />
                  {camera.is_critical && (
                    <Chip
                      label="CRITICAL"
                      color="error"
                      size="small"
                      sx={{ position: 'absolute', top: 8, left: 8 }}
                    />
                  )}
                  {camera.audio_recording_enabled && (
                    <VolumeUp sx={{ position: 'absolute', top: 8, right: 8, color: 'white' }} />
                  )}
                </Box>

                {/* Camera Info */}
                <Typography variant="caption" color="textSecondary" display="block">
                  {camera.location_type} - {camera.location_description}
                </Typography>

                {/* Camera Controls */}
                <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
                  <Tooltip title="Fullscreen">
                    <IconButton 
                      size="small" 
                      onClick={(e) => {
                        e.stopPropagation();
                        handleFullscreen(camera.id);
                      }}
                    >
                      <Fullscreen />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Bookmark Event">
                    <IconButton 
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleBookmark(camera);
                      }}
                    >
                      <Bookmark />
                    </IconButton>
                  </Tooltip>
                  {camera.camera_type === 'ptz' && (
                    <Tooltip title="PTZ Control">
                      <IconButton size="small">
                        <AspectRatio />
                      </IconButton>
                    </Tooltip>
                  )}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Bookmark Dialog */}
      <Dialog open={bookmarkDialog} onClose={() => setBookmarkDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create Event Bookmark</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Bookmark Name"
            fullWidth
            value={bookmarkData.bookmark_name}
            onChange={(e) => setBookmarkData({ ...bookmarkData, bookmark_name: e.target.value })}
            required
          />
          <TextField
            margin="dense"
            label="Description"
            fullWidth
            multiline
            rows={3}
            value={bookmarkData.description}
            onChange={(e) => setBookmarkData({ ...bookmarkData, description: e.target.value })}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setBookmarkDialog(false)}>Cancel</Button>
          <Button 
            onClick={saveBookmark} 
            variant="contained"
            disabled={!bookmarkData.bookmark_name}
          >
            Save Bookmark
          </Button>
        </DialogActions>
      </Dialog>

      {/* No Cameras Message */}
      {cameras.length === 0 && (
        <Alert severity="info">
          No cameras available for live monitoring. Please check camera status.
        </Alert>
      )}
    </Box>
  );
};

export default LiveMonitoringDashboard;
