/**
 * Workflow Monitoring Dashboard
 * 
 * Real-time monitoring with metrics, alerts, and bottlenecks
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Button,
  Alert,
  LinearProgress,
  Tabs,
  Tab,
  Badge,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Timer as TimerIcon,
  People as PeopleIcon,
  Assignment as AssignmentIcon,
  Speed as SpeedIcon,
} from '@mui/icons-material';
import analyticsService, { RealtimeDashboard, QuickStats } from '../../services/analyticsService';

interface MonitoringDashboardProps {
  autoRefresh?: boolean;
  refreshInterval?: number;
}

const MonitoringDashboard: React.FC<MonitoringDashboardProps> = ({
  autoRefresh = true,
  refreshInterval = 30000, // 30 seconds
}) => {
  const [loading, setLoading] = useState(false);
  const [dashboard, setDashboard] = useState<RealtimeDashboard | null>(null);
  const [quickStats, setQuickStats] = useState<QuickStats | null>(null);
  const [activeTab, setActiveTab] = useState(0);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();

    if (autoRefresh) {
      const interval = setInterval(loadData, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [autoRefresh, refreshInterval]);

  const loadData = async () => {
    setLoading(true);
    setError(null);

    try {
      const [dashboardData, statsData] = await Promise.all([
        analyticsService.getDashboard(),
        analyticsService.getQuickStats()
      ]);
      
      setDashboard(dashboardData);
      setQuickStats(statsData);
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Failed to load dashboard');
    } finally {
      setLoading(false);
    }
  };

  const renderMetricCards = () => {
    if (!dashboard || !quickStats) return null;

    return (
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <Box>
                  <Typography color="text.secondary" variant="body2">
                    Active Workflows
                  </Typography>
                  <Typography variant="h4" sx={{ mt: 1 }}>
                    {quickStats.total_active}
                  </Typography>
                </Box>
                <AssignmentIcon color="primary" sx={{ fontSize: 40 }} />
              </Box>
              <Box sx={{ mt: 2, display: 'flex', alignItems: 'center' }}>
                <Typography variant="body2" color="success.main">
                  {quickStats.completed_today} completed today
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <Box>
                  <Typography color="text.secondary" variant="body2">
                    Pending Approvals
                  </Typography>
                  <Typography variant="h4" sx={{ mt: 1 }}>
                    <Badge badgeContent={quickStats.overdue_tasks} color="error">
                      <span>{dashboard.total_pending_approvals}</span>
                    </Badge>
                  </Typography>
                </Box>
                <PeopleIcon color="warning" sx={{ fontSize: 40 }} />
              </Box>
              <Box sx={{ mt: 2, display: 'flex', alignItems: 'center' }}>
                <Typography variant="body2" color="text.secondary">
                  {quickStats.overdue_tasks} overdue
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <Box>
                  <Typography color="text.secondary" variant="body2">
                    SLA Breaches
                  </Typography>
                  <Typography variant="h4" sx={{ mt: 1 }} color="error.main">
                    {dashboard.total_sla_breaches}
                  </Typography>
                </Box>
                <ErrorIcon color="error" sx={{ fontSize: 40 }} />
              </Box>
              <Box sx={{ mt: 2, display: 'flex', alignItems: 'center' }}>
                <Typography variant="body2" color="text.secondary">
                  Requires attention
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <Box>
                  <Typography color="text.secondary" variant="body2">
                    Avg Cycle Time
                  </Typography>
                  <Typography variant="h4" sx={{ mt: 1 }}>
                    {analyticsService.formatDuration(dashboard.avg_cycle_time_hours)}
                  </Typography>
                </Box>
                <SpeedIcon color="info" sx={{ fontSize: 40 }} />
              </Box>
              <Box sx={{ mt: 2, display: 'flex', alignItems: 'center' }}>
                <TrendingDownIcon color="success" fontSize="small" sx={{ mr: 0.5 }} />
                <Typography variant="body2" color="success.main">
                  15% faster
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    );
  };

  const renderSecondaryMetrics = () => {
    if (!dashboard) return null;

    return (
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={4}>
          <Card variant="outlined">
            <CardContent>
              <Typography variant="body2" color="text.secondary">
                Approval Rate
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'baseline', mt: 1 }}>
                <Typography variant="h5">
                  {dashboard.approval_rate.toFixed(1)}%
                </Typography>
                <CheckCircleIcon color="success" sx={{ ml: 1 }} fontSize="small" />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={4}>
          <Card variant="outlined">
            <CardContent>
              <Typography variant="body2" color="text.secondary">
                Completion Rate Today
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'baseline', mt: 1 }}>
                <Typography variant="h5">
                  {dashboard.completion_rate_today.toFixed(1)}%
                </Typography>
                <TrendingUpIcon color="primary" sx={{ ml: 1 }} fontSize="small" />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={4}>
          <Card variant="outlined">
            <CardContent>
              <Typography variant="body2" color="text.secondary">
                Bottlenecks Detected
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'baseline', mt: 1 }}>
                <Typography variant="h5">
                  {dashboard.total_bottlenecks}
                </Typography>
                <WarningIcon color="warning" sx={{ ml: 1 }} fontSize="small" />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    );
  };

  const renderPendingApprovals = () => {
    if (!dashboard || dashboard.pending_by_user.length === 0) {
      return <Alert severity="info">No pending approvals</Alert>;
    }

    return (
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>User</TableCell>
              <TableCell align="right">Total</TableCell>
              <TableCell align="right">High Priority</TableCell>
              <TableCell align="right">Overdue</TableCell>
              <TableCell align="right">Avg Age</TableCell>
              <TableCell align="right">Oldest</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {dashboard.pending_by_user.map((user) => (
              <TableRow key={user.user_id} hover>
                <TableCell>{user.user_name}</TableCell>
                <TableCell align="right">
                  <Chip label={user.total_pending} size="small" color="primary" />
                </TableCell>
                <TableCell align="right">
                  {user.high_priority > 0 && (
                    <Chip label={user.high_priority} size="small" color="error" />
                  )}
                </TableCell>
                <TableCell align="right">
                  {user.overdue_count > 0 && (
                    <Chip label={user.overdue_count} size="small" color="warning" />
                  )}
                </TableCell>
                <TableCell align="right">
                  {analyticsService.formatDuration(user.avg_age_hours)}
                </TableCell>
                <TableCell align="right">
                  {user.oldest_approval_days.toFixed(1)} days
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    );
  };

  const renderSLABreaches = () => {
    if (!dashboard || dashboard.sla_breach_alerts.length === 0) {
      return <Alert severity="success">No SLA breaches</Alert>;
    }

    return (
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Workflow</TableCell>
              <TableCell>Entity</TableCell>
              <TableCell>Breach Duration</TableCell>
              <TableCell>SLA %</TableCell>
              <TableCell>Severity</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {dashboard.sla_breach_alerts.map((alert) => (
              <TableRow key={alert.alert_id} hover>
                <TableCell>{alert.workflow_name}</TableCell>
                <TableCell>
                  {alert.entity_type} #{alert.entity_id}
                </TableCell>
                <TableCell>
                  {analyticsService.formatDuration(alert.breach_duration_minutes / 60)}
                </TableCell>
                <TableCell>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Box sx={{ width: '100%', mr: 1 }}>
                      <LinearProgress
                        variant="determinate"
                        value={Math.min(alert.sla_percentage, 100)}
                        color="error"
                      />
                    </Box>
                    <Typography variant="body2">{alert.sla_percentage.toFixed(0)}%</Typography>
                  </Box>
                </TableCell>
                <TableCell>
                  <Chip
                    label={alert.severity}
                    color={analyticsService.getSeverityColor(alert.severity) as any}
                    size="small"
                  />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    );
  };

  const renderBottlenecks = () => {
    if (!dashboard || dashboard.bottlenecks.length === 0) {
      return <Alert severity="success">No bottlenecks detected</Alert>;
    }

    return (
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Step</TableCell>
              <TableCell align="right">Avg Duration</TableCell>
              <TableCell align="right">Pending</TableCell>
              <TableCell align="right">Completion Rate</TableCell>
              <TableCell>Severity</TableCell>
              <TableCell>Recommendation</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {dashboard.bottlenecks.map((bottleneck, index) => (
              <TableRow key={index} hover>
                <TableCell>
                  <Typography variant="body2" fontWeight="medium">
                    {bottleneck.step_name}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {bottleneck.step_key}
                  </Typography>
                </TableCell>
                <TableCell align="right">
                  {analyticsService.formatDuration(bottleneck.avg_duration_hours)}
                </TableCell>
                <TableCell align="right">
                  <Chip label={bottleneck.pending_count} size="small" />
                </TableCell>
                <TableCell align="right">
                  <Typography
                    variant="body2"
                    color={analyticsService.getCompletionRateColor(bottleneck.completion_rate)}
                  >
                    {bottleneck.completion_rate.toFixed(1)}%
                  </Typography>
                </TableCell>
                <TableCell>
                  <Chip
                    label={bottleneck.severity}
                    color={analyticsService.getSeverityColor(bottleneck.severity) as any}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Typography variant="body2" color="text.secondary">
                    {bottleneck.recommendation}
                  </Typography>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    );
  };

  return (
    <Box>
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4">Workflow Monitoring</Typography>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          {autoRefresh && (
            <Chip
              label={`Auto-refresh: ${refreshInterval / 1000}s`}
              size="small"
              color="primary"
              variant="outlined"
            />
          )}
          <Button
            startIcon={<RefreshIcon />}
            onClick={loadData}
            disabled={loading}
            variant="outlined"
          >
            Refresh
          </Button>
        </Box>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {renderMetricCards()}
      {renderSecondaryMetrics()}

      <Paper sx={{ mt: 3 }}>
        <Tabs value={activeTab} onChange={(e, v) => setActiveTab(v)}>
          <Tab label="Pending Approvals" />
          <Tab label="SLA Breaches" />
          <Tab label="Bottlenecks" />
        </Tabs>

        <Box sx={{ p: 3 }}>
          {activeTab === 0 && renderPendingApprovals()}
          {activeTab === 1 && renderSLABreaches()}
          {activeTab === 2 && renderBottlenecks()}
        </Box>
      </Paper>
    </Box>
  );
};

export default MonitoringDashboard;
