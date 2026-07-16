/**
 * Branch Cameras Summary Component
 * 
 * Branch-specific camera statistics and overview
 * Features:
 * - Camera count by type and location
 * - Status breakdown
 * - Uptime metrics
 * - Critical cameras count
 * - Quick health status
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  CircularProgress,
  Alert,
  Divider,
  List,
  ListItem,
  ListItemText
} from '@mui/material';
import {
  Videocam,
  CheckCircle,
  Error,
  Warning,
  FiberManualRecord
} from '@mui/icons-material';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import cameraService, { BranchCameraSummary } from '../../../services/cameraService';

interface BranchCamerasSummaryProps {
  branchId: string;
  branchName?: string;
}

const BranchCamerasSummary: React.FC<BranchCamerasSummaryProps> = ({ branchId, branchName }) => {
  const [summary, setSummary] = useState<BranchCameraSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadSummary();
  }, [branchId]);

  const loadSummary = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await cameraService.getBranchSummary(branchId);
      setSummary(data);
      setLoading(false);
    } catch (err: any) {
      console.error('Failed to load branch summary:', err);
      setError(err.message || 'Failed to load branch summary');
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="300px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error">
        {error}
      </Alert>
    );
  }

  if (!summary) {
    return (
      <Alert severity="info">
        No camera data available for this branch.
      </Alert>
    );
  }

  // Prepare data for pie charts
  const statusData = [
    { name: 'Online', value: summary.online_cameras, color: '#4caf50' },
    { name: 'Offline', value: summary.offline_cameras, color: '#f44336' },
    { name: 'Maintenance', value: summary.maintenance_cameras, color: '#ff9800' }
  ].filter(item => item.value > 0);

  const typeData = Object.entries(summary.by_type).map(([type, count]) => ({
    name: type.charAt(0).toUpperCase() + type.slice(1),
    value: count
  }));

  const locationData = Object.entries(summary.by_location).map(([location, count]) => ({
    name: location.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
    value: count
  }));

  const getHealthStatus = () => {
    if (summary.health_status === 'good' && summary.average_uptime_percentage >= 95) {
      return { label: 'Excellent', color: 'success', icon: <CheckCircle /> };
    } else if (summary.health_status === 'good') {
      return { label: 'Good', color: 'info', icon: <CheckCircle /> };
    } else {
      return { label: 'Needs Attention', color: 'warning', icon: <Warning /> };
    }
  };

  const healthStatus = getHealthStatus();

  return (
    <Box>
      <Card>
        <CardContent>
          {/* Header */}
          <Typography variant="h6" gutterBottom>
            <Videocam sx={{ mr: 1, verticalAlign: 'middle' }} />
            {branchName || 'Branch'} - Camera Summary
          </Typography>

          {/* Overall Health */}
          <Box sx={{ mb: 3, p: 2, bgcolor: `${healthStatus.color}.light`, borderRadius: 1 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              {healthStatus.icon}
              <Typography variant="h6">
                Health Status: {healthStatus.label}
              </Typography>
            </Box>
            <Typography variant="body2" color="textSecondary">
              Average Uptime: {summary.average_uptime_percentage.toFixed(1)}%
            </Typography>
          </Box>

          {/* Key Metrics */}
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={6} md={3}>
              <Card variant="outlined">
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography color="textSecondary" variant="body2">
                    Total
                  </Typography>
                  <Typography variant="h4">
                    {summary.total_cameras}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={6} md={3}>
              <Card variant="outlined" sx={{ bgcolor: 'success.light' }}>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography color="textSecondary" variant="body2">
                    Online
                  </Typography>
                  <Typography variant="h4">
                    {summary.online_cameras}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={6} md={3}>
              <Card variant="outlined" sx={{ bgcolor: summary.offline_cameras > 0 ? 'error.light' : 'inherit' }}>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography color="textSecondary" variant="body2">
                    Offline
                  </Typography>
                  <Typography variant="h4">
                    {summary.offline_cameras}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={6} md={3}>
              <Card variant="outlined" sx={{ bgcolor: summary.critical_cameras > 0 ? 'warning.light' : 'inherit' }}>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography color="textSecondary" variant="body2">
                    Critical
                  </Typography>
                  <Typography variant="h4">
                    {summary.critical_cameras}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          <Divider sx={{ my: 3 }} />

          {/* Charts and Lists */}
          <Grid container spacing={3}>
            {/* Status Distribution */}
            <Grid item xs={12} md={4}>
              <Typography variant="subtitle1" gutterBottom fontWeight="bold">
                Status Distribution
              </Typography>
              {statusData.length > 0 ? (
                <ResponsiveContainer width="100%" height={200}>
                  <PieChart>
                    <Pie
                      data={statusData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, value }) => `${name}: ${value}`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {statusData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <Typography variant="body2" color="textSecondary">
                  No data available
                </Typography>
              )}
            </Grid>

            {/* Camera Types */}
            <Grid item xs={12} md={4}>
              <Typography variant="subtitle1" gutterBottom fontWeight="bold">
                Camera Types ({typeData.length})
              </Typography>
              <List dense>
                {typeData.map((item) => (
                  <ListItem key={item.name}>
                    <FiberManualRecord sx={{ mr: 1, fontSize: 12, color: 'primary.main' }} />
                    <ListItemText
                      primary={item.name}
                      secondary={`${item.value} camera${item.value !== 1 ? 's' : ''}`}
                    />
                  </ListItem>
                ))}
                {typeData.length === 0 && (
                  <Typography variant="body2" color="textSecondary">
                    No cameras found
                  </Typography>
                )}
              </List>
            </Grid>

            {/* Locations */}
            <Grid item xs={12} md={4}>
              <Typography variant="subtitle1" gutterBottom fontWeight="bold">
                Locations ({locationData.length})
              </Typography>
              <List dense>
                {locationData.slice(0, 5).map((item) => (
                  <ListItem key={item.name}>
                    <FiberManualRecord sx={{ mr: 1, fontSize: 12, color: 'secondary.main' }} />
                    <ListItemText
                      primary={item.name}
                      secondary={`${item.value} camera${item.value !== 1 ? 's' : ''}`}
                    />
                  </ListItem>
                ))}
                {locationData.length > 5 && (
                  <ListItem>
                    <ListItemText
                      secondary={`+${locationData.length - 5} more locations`}
                    />
                  </ListItem>
                )}
                {locationData.length === 0 && (
                  <Typography variant="body2" color="textSecondary">
                    No locations found
                  </Typography>
                )}
              </List>
            </Grid>
          </Grid>

          {/* Additional Stats */}
          <Box sx={{ mt: 3, pt: 2, borderTop: 1, borderColor: 'divider' }}>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={4}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Chip
                    icon={<CheckCircle />}
                    label={`${summary.recording_cameras} Recording`}
                    color="success"
                    variant="outlined"
                    size="small"
                  />
                </Box>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Chip
                    icon={<Warning />}
                    label={`${summary.maintenance_cameras} Maintenance`}
                    color="warning"
                    variant="outlined"
                    size="small"
                  />
                </Box>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Chip
                    icon={<Error />}
                    label={`${summary.critical_cameras} Critical`}
                    color="error"
                    variant="outlined"
                    size="small"
                  />
                </Box>
              </Grid>
            </Grid>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default BranchCamerasSummary;
