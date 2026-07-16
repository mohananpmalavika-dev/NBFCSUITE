/**
 * Recording & Storage Dashboard
 * 
 * Main dashboard for DVR/NVR management showing storage analytics,
 * device health, and recording status.
 */

import React, { useState, useEffect } from 'react';
import { Box, Grid, Card, CardContent, Typography, Button, Alert, LinearProgress, Chip } from '@mui/material';
import {
  Storage, VideoLibrary, Computer, Backup, Warning, CheckCircle,
  Error, Info, TrendingUp, Speed
} from '@mui/icons-material';
import { recordingService } from '../../../services/recordingService';

interface StorageAnalytics {
  total_devices: number;
  total_capacity_tb: number;
  total_used_tb: number;
  total_available_tb: number;
  average_utilization_percentage: number;
  devices_with_alerts: number;
  storage_health: string;
  cleanup_recommended: boolean;
}

export const RecordingDashboard: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [analytics, setAnalytics] = useState<StorageAnalytics | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadStorageAnalytics();
  }, []);

  const loadStorageAnalytics = async () => {
    try {
      setLoading(true);
      const response = await recordingService.getStorageAnalytics();
      setAnalytics(response.data);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to load storage analytics');
    } finally {
      setLoading(false);
    }
  };

  const getHealthColor = (health: string) => {
    switch (health) {
      case 'good': return 'success';
      case 'fair': return 'info';
      case 'warning': return 'warning';
      case 'critical': return 'error';
      default: return 'default';
    }
  };

  const getHealthIcon = (health: string) => {
    switch (health) {
      case 'good': return <CheckCircle />;
      case 'fair': return <Info />;
      case 'warning': return <Warning />;
      case 'critical': return <Error />;
      default: return <Speed />;
    }
  };

  const getUtilizationColor = (utilization: number) => {
    if (utilization >= 90) return 'error';
    if (utilization >= 80) return 'warning';
    if (utilization >= 70) return 'info';
    return 'success';
  };

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <LinearProgress />
        <Typography sx={{ mt: 2, textAlign: 'center' }}>
          Loading storage analytics...
        </Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error" onClose={() => setError(null)}>
          {error}
        </Alert>
        <Button onClick={loadStorageAnalytics} sx={{ mt: 2 }}>
          Retry
        </Button>
      </Box>
    );
  }

  if (!analytics) return null;

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
          Recording & Storage Management
        </Typography>
        <Button
          variant="contained"
          startIcon={<VideoLibrary />}
          href="/cctv/recording/devices"
        >
          Manage Devices
        </Button>
      </Box>

      {/* Alert Section */}
      {analytics.cleanup_recommended && (
        <Alert severity="warning" sx={{ mb: 3 }} icon={<Warning />}>
          Storage utilization is high ({analytics.average_utilization_percentage.toFixed(1)}%). 
          Cleanup or expansion recommended.
        </Alert>
      )}

      {analytics.devices_with_alerts > 0 && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {analytics.devices_with_alerts} device(s) have active storage alerts!
        </Alert>
      )}

      {/* Key Metrics */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        {/* Total Devices */}
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Computer color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Total Devices</Typography>
              </Box>
              <Typography variant="h3" sx={{ fontWeight: 'bold' }}>
                {analytics.total_devices}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                DVR/NVR Systems
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Total Capacity */}
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Storage color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Total Capacity</Typography>
              </Box>
              <Typography variant="h3" sx={{ fontWeight: 'bold' }}>
                {analytics.total_capacity_tb.toFixed(1)} TB
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Storage Space
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Used Storage */}
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <VideoLibrary color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Used Storage</Typography>
              </Box>
              <Typography variant="h3" sx={{ fontWeight: 'bold' }}>
                {analytics.total_used_tb.toFixed(1)} TB
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {analytics.average_utilization_percentage.toFixed(1)}% Utilized
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Available Storage */}
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <TrendingUp color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Available</Typography>
              </Box>
              <Typography variant="h3" sx={{ fontWeight: 'bold' }}>
                {analytics.total_available_tb.toFixed(1)} TB
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Free Space
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Storage Health & Utilization */}
      <Grid container spacing={3}>
        {/* Storage Health */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Storage Health Status
              </Typography>
              <Box sx={{ textAlign: 'center', py: 3 }}>
                <Chip
                  icon={getHealthIcon(analytics.storage_health)}
                  label={analytics.storage_health.toUpperCase()}
                  color={getHealthColor(analytics.storage_health)}
                  size="large"
                  sx={{ fontSize: '1.2rem', px: 2, py: 3 }}
                />
                <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                  System health assessment based on utilization and device status
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Storage Utilization */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Storage Utilization
              </Typography>
              <Box sx={{ py: 2 }}>
                <Typography variant="h2" sx={{ fontWeight: 'bold', textAlign: 'center', mb: 2 }}>
                  {analytics.average_utilization_percentage.toFixed(1)}%
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={analytics.average_utilization_percentage}
                  color={getUtilizationColor(analytics.average_utilization_percentage)}
                  sx={{ height: 20, borderRadius: 10 }}
                />
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
                  <Typography variant="body2">
                    Used: {analytics.total_used_tb.toFixed(1)} TB
                  </Typography>
                  <Typography variant="body2">
                    Total: {analytics.total_capacity_tb.toFixed(1)} TB
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Quick Actions
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6} md={3}>
                  <Button
                    fullWidth
                    variant="outlined"
                    startIcon={<Computer />}
                    href="/cctv/recording/devices"
                  >
                    Manage DVR/NVR
                  </Button>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Button
                    fullWidth
                    variant="outlined"
                    startIcon={<Storage />}
                    href="/cctv/recording/storage-calculator"
                  >
                    Storage Calculator
                  </Button>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Button
                    fullWidth
                    variant="outlined"
                    startIcon={<Backup />}
                    href="/cctv/recording/backup"
                  >
                    Backup Management
                  </Button>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Button
                    fullWidth
                    variant="outlined"
                    startIcon={<VideoLibrary />}
                    href="/cctv/recording/retention"
                  >
                    Retention Policy
                  </Button>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default RecordingDashboard;
