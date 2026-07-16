/**
 * Camera Health Dashboard Component
 * 
 * System-wide health overview for all cameras
 * Features:
 * - Overall system health metrics
 * - Cameras needing attention
 * - Low uptime cameras
 * - Offline cameras list
 * - Real-time status indicators
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  LinearProgress,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Alert,
  CircularProgress,
  Button,
  Paper
} from '@mui/material';
import {
  CheckCircle,
  Error,
  Warning,
  Refresh,
  TrendingUp,
  TrendingDown,
  Videocam
} from '@mui/icons-material';
import cameraService, { SystemHealthReport } from '../../../services/cameraService';

const CameraHealthDashboard: React.FC = () => {
  const [healthReport, setHealthReport] = useState<SystemHealthReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    loadHealthReport();

    if (autoRefresh) {
      const interval = setInterval(() => {
        loadHealthReport();
      }, 30000); // Refresh every 30 seconds

      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const loadHealthReport = async () => {
    try {
      setLoading(true);
      const report = await cameraService.getSystemHealthReport();
      setHealthReport(report);
      setLoading(false);
    } catch (error) {
      console.error('Failed to load health report:', error);
      setLoading(false);
    }
  };

  const getHealthColor = (health: string) => {
    switch (health) {
      case 'excellent':
        return 'success';
      case 'good':
        return 'info';
      case 'needs_attention':
        return 'warning';
      default:
        return 'default';
    }
  };

  const getHealthIcon = (health: string) => {
    switch (health) {
      case 'excellent':
        return <CheckCircle color="success" />;
      case 'good':
        return <CheckCircle color="info" />;
      case 'needs_attention':
        return <Warning color="warning" />;
      default:
        return <Error color="error" />;
    }
  };

  if (loading && !healthReport) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (!healthReport) {
    return (
      <Alert severity="error">
        Failed to load health report. Please try again.
      </Alert>
    );
  }

  const availabilityPercentage = healthReport.availability_percentage;
  const uptimePercentage = healthReport.average_uptime_percentage;

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5">
          <Videocam sx={{ mr: 1, verticalAlign: 'middle' }} />
          Camera System Health Dashboard
        </Typography>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <Chip
            label={`Auto-refresh: ${autoRefresh ? 'ON' : 'OFF'}`}
            color={autoRefresh ? 'success' : 'default'}
            onClick={() => setAutoRefresh(!autoRefresh)}
            sx={{ cursor: 'pointer' }}
          />
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={loadHealthReport}
            disabled={loading}
          >
            Refresh
          </Button>
        </Box>
      </Box>

      {/* Overall Health Status */}
      <Card sx={{ mb: 3, bgcolor: getHealthColor(healthReport.system_health) + '.light' }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            {getHealthIcon(healthReport.system_health)}
            <Box sx={{ flex: 1 }}>
              <Typography variant="h4" sx={{ textTransform: 'capitalize' }}>
                System Health: {healthReport.system_health.replace('_', ' ')}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Last updated: {new Date(healthReport.timestamp).toLocaleString()}
              </Typography>
            </Box>
            {healthReport.cameras_needing_attention > 0 && (
              <Chip
                label={`${healthReport.cameras_needing_attention} Cameras Need Attention`}
                color="warning"
                icon={<Warning />}
              />
            )}
          </Box>
        </CardContent>
      </Card>

      {/* Key Metrics */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Cameras
              </Typography>
              <Typography variant="h3">
                {healthReport.total_cameras}
              </Typography>
              <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                System-wide
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card sx={{ bgcolor: 'success.light' }}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Online Cameras
              </Typography>
              <Typography variant="h3">
                {healthReport.online_cameras}
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
                <TrendingUp fontSize="small" />
                <Typography variant="body2">
                  {availabilityPercentage.toFixed(1)}% Availability
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card sx={{ bgcolor: healthReport.offline_cameras > 0 ? 'error.light' : 'inherit' }}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Offline Cameras
              </Typography>
              <Typography variant="h3">
                {healthReport.offline_cameras}
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
                {healthReport.offline_cameras > 0 ? (
                  <>
                    <TrendingDown fontSize="small" color="error" />
                    <Typography variant="body2" color="error.main">
                      Requires attention
                    </Typography>
                  </>
                ) : (
                  <Typography variant="body2" color="success.main">
                    All online
                  </Typography>
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Maintenance/Faulty
              </Typography>
              <Typography variant="h3">
                {healthReport.maintenance_cameras + healthReport.faulty_cameras}
              </Typography>
              <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                {healthReport.maintenance_cameras} maintenance, {healthReport.faulty_cameras} faulty
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Performance Metrics */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                System Availability
              </Typography>
              <Box sx={{ mb: 1 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Online Cameras</Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {availabilityPercentage.toFixed(2)}%
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={availabilityPercentage}
                  color={availabilityPercentage >= 95 ? 'success' : availabilityPercentage >= 85 ? 'warning' : 'error'}
                  sx={{ height: 10, borderRadius: 1 }}
                />
              </Box>
              <Typography variant="caption" color="textSecondary">
                Target: 95% or higher
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Average Uptime
              </Typography>
              <Box sx={{ mb: 1 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">System Average</Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {uptimePercentage.toFixed(2)}%
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={uptimePercentage}
                  color={uptimePercentage >= 95 ? 'success' : uptimePercentage >= 85 ? 'warning' : 'error'}
                  sx={{ height: 10, borderRadius: 1 }}
                />
              </Box>
              <Typography variant="caption" color="textSecondary">
                Target: 95% or higher (30-day average)
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Cameras Needing Attention */}
      <Grid container spacing={3}>
        {/* Low Uptime Cameras */}
        {healthReport.low_uptime_cameras.length > 0 && (
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom color="warning.main">
                  <Warning sx={{ mr: 1, verticalAlign: 'middle' }} />
                  Low Uptime Cameras ({healthReport.low_uptime_cameras.length})
                </Typography>
                <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                  Cameras with uptime below 90%
                </Typography>
                <TableContainer component={Paper} variant="outlined">
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Camera Name</TableCell>
                        <TableCell align="right">Uptime</TableCell>
                        <TableCell align="center">Action</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {healthReport.low_uptime_cameras.map((camera) => (
                        <TableRow key={camera.camera_id}>
                          <TableCell>{camera.camera_name}</TableCell>
                          <TableCell align="right">
                            <Typography
                              variant="body2"
                              color={camera.uptime_percentage < 80 ? 'error' : 'warning.main'}
                              fontWeight="bold"
                            >
                              {camera.uptime_percentage.toFixed(1)}%
                            </Typography>
                          </TableCell>
                          <TableCell align="center">
                            <Button
                              size="small"
                              variant="outlined"
                              onClick={() => window.location.href = `/cctv/cameras/${camera.camera_id}`}
                            >
                              View
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* Offline Cameras */}
        {healthReport.offline_cameras_list && healthReport.offline_cameras_list.length > 0 && (
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom color="error.main">
                  <Error sx={{ mr: 1, verticalAlign: 'middle' }} />
                  Offline Cameras ({healthReport.offline_cameras_list.length})
                </Typography>
                <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                  Cameras currently offline
                </Typography>
                <TableContainer component={Paper} variant="outlined">
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Camera Name</TableCell>
                        <TableCell>Last Online</TableCell>
                        <TableCell align="center">Action</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {healthReport.offline_cameras_list.map((camera) => (
                        <TableRow key={camera.camera_id}>
                          <TableCell>{camera.camera_name}</TableCell>
                          <TableCell>
                            <Typography variant="body2" color="textSecondary">
                              {camera.last_online
                                ? new Date(camera.last_online).toLocaleString()
                                : 'Unknown'}
                            </Typography>
                          </TableCell>
                          <TableCell align="center">
                            <Button
                              size="small"
                              variant="outlined"
                              color="error"
                              onClick={() => window.location.href = `/cctv/cameras/${camera.camera_id}`}
                            >
                              View
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>

      {/* All Systems Normal */}
      {healthReport.low_uptime_cameras.length === 0 &&
        healthReport.offline_cameras === 0 &&
        healthReport.cameras_needing_attention === 0 && (
          <Alert severity="success" sx={{ mt: 3 }}>
            <Typography variant="h6">
              ✅ All Systems Operational
            </Typography>
            <Typography variant="body2">
              All cameras are online and performing optimally. No attention required.
            </Typography>
          </Alert>
        )}
    </Box>
  );
};

export default CameraHealthDashboard;
