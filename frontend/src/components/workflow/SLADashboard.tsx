/**
 * SLA Dashboard Component
 * 
 * Monitor SLA performance and active instances
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  LinearProgress,
  IconButton,
  Button,
  Tooltip,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Pause as PauseIcon,
  PlayArrow as ResumeIcon,
  CheckCircle as CompleteIcon,
  History as HistoryIcon,
  TrendingUp as EscalateIcon,
} from '@mui/icons-material';
import slaService, { SLAInstance, SLAMetrics } from '../../services/slaService';

interface SLADashboardProps {
  entityType?: string;
  workflowInstanceId?: number;
  autoRefresh?: boolean;
  refreshInterval?: number;
}

const SLADashboard: React.FC<SLADashboardProps> = ({
  entityType,
  workflowInstanceId,
  autoRefresh = true,
  refreshInterval = 30000, // 30 seconds
}) => {
  const [loading, setLoading] = useState(false);
  const [instances, setInstances] = useState<SLAInstance[]>([]);
  const [metrics, setMetrics] = useState<SLAMetrics | null>(null);
  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();

    if (autoRefresh) {
      const interval = setInterval(loadData, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [entityType, workflowInstanceId, selectedStatus, autoRefresh, refreshInterval]);

  const loadData = async () => {
    setLoading(true);
    setError(null);

    try {
      // Load instances
      const filters: any = {};
      if (entityType) filters.entity_type = entityType;
      if (workflowInstanceId) filters.workflow_instance_id = workflowInstanceId;
      if (selectedStatus !== 'all') filters.status = selectedStatus;

      const instancesData = await slaService.listInstances(filters);
      setInstances(instancesData);

      // Load metrics if entity type specified
      if (entityType) {
        const metricsData = await slaService.getMetrics(entityType, 30);
        setMetrics(metricsData);
      }
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Failed to load SLA data');
    } finally {
      setLoading(false);
    }
  };

  const handlePause = async (instanceId: number) => {
    try {
      await slaService.pauseSLA(instanceId, 'Manual pause');
      loadData();
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Failed to pause SLA');
    }
  };

  const handleResume = async (instanceId: number) => {
    try {
      await slaService.resumeSLA(instanceId);
      loadData();
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Failed to resume SLA');
    }
  };

  const handleComplete = async (instanceId: number) => {
    try {
      await slaService.completeSLA(instanceId, true);
      loadData();
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Failed to complete SLA');
    }
  };

  const handleProcessEscalations = async (instanceId: number) => {
    try {
      await slaService.processEscalations(instanceId);
      loadData();
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Failed to process escalations');
    }
  };

  const getStatusColor = (status: string) => {
    return slaService.getSLAStatusColor(status) as any;
  };

  const getPercentageColor = (percentage: number) => {
    if (percentage >= 90) return 'error';
    if (percentage >= 70) return 'warning';
    return 'success';
  };

  const renderMetricsCards = () => {
    if (!metrics) return null;

    return (
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Total SLAs
              </Typography>
              <Typography variant="h4">
                {metrics.total_slas}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Compliance Rate
              </Typography>
              <Typography variant="h4" color="success.main">
                {metrics.sla_compliance_rate}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Breached SLAs
              </Typography>
              <Typography variant="h4" color="error.main">
                {metrics.breached_slas}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Active SLAs
              </Typography>
              <Typography variant="h4" color="primary.main">
                {metrics.active_slas}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Avg Completion Time
              </Typography>
              <Typography variant="h5">
                {metrics.average_completion_time_hours.toFixed(1)} hours
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {metrics.average_completion_percentage.toFixed(1)}% of SLA used
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Total Escalations
              </Typography>
              <Typography variant="h5">
                {metrics.total_escalations}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Last 30 days
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    );
  };

  const renderInstancesTable = () => (
    <TableContainer component={Paper}>
      <Box sx={{ p: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h6">SLA Instances</Typography>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Status Filter</InputLabel>
            <Select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              label="Status Filter"
            >
              <MenuItem value="all">All</MenuItem>
              <MenuItem value="active">Active</MenuItem>
              <MenuItem value="met">Met</MenuItem>
              <MenuItem value="breached">Breached</MenuItem>
              <MenuItem value="paused">Paused</MenuItem>
            </Select>
          </FormControl>
          <IconButton onClick={loadData} disabled={loading}>
            <RefreshIcon />
          </IconButton>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ m: 2 }}>
          {error}
        </Alert>
      )}

      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Entity</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>Progress</TableCell>
            <TableCell>Time Remaining</TableCell>
            <TableCell>Escalations</TableCell>
            <TableCell>Started</TableCell>
            <TableCell>Deadline</TableCell>
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {instances.length === 0 ? (
            <TableRow>
              <TableCell colSpan={8} align="center">
                <Typography color="text.secondary">
                  {loading ? 'Loading...' : 'No SLA instances found'}
                </Typography>
              </TableCell>
            </TableRow>
          ) : (
            instances.map((instance) => (
              <TableRow key={instance.instance_id}>
                <TableCell>
                  <Typography variant="body2">
                    {instance.entity_type}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    #{instance.entity_id}
                  </Typography>
                </TableCell>

                <TableCell>
                  <Chip
                    label={instance.status}
                    color={getStatusColor(instance.status)}
                    size="small"
                  />
                </TableCell>

                <TableCell sx={{ minWidth: 200 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Box sx={{ flex: 1 }}>
                      <LinearProgress
                        variant="determinate"
                        value={Math.min(instance.sla_percentage, 100)}
                        color={getPercentageColor(instance.sla_percentage)}
                      />
                    </Box>
                    <Typography variant="body2" sx={{ minWidth: 45 }}>
                      {instance.sla_percentage.toFixed(0)}%
                    </Typography>
                  </Box>
                </TableCell>

                <TableCell>
                  <Typography
                    variant="body2"
                    color={instance.time_remaining_minutes < 0 ? 'error' : 'text.primary'}
                  >
                    {slaService.formatTimeRemaining(instance.time_remaining_minutes)}
                  </Typography>
                </TableCell>

                <TableCell>
                  <Chip
                    label={instance.escalation_count}
                    size="small"
                    color={instance.escalation_count > 0 ? 'warning' : 'default'}
                  />
                </TableCell>

                <TableCell>
                  <Typography variant="body2">
                    {new Date(instance.start_time).toLocaleString()}
                  </Typography>
                </TableCell>

                <TableCell>
                  <Typography variant="body2">
                    {new Date(instance.deadline).toLocaleString()}
                  </Typography>
                </TableCell>

                <TableCell>
                  <Box sx={{ display: 'flex', gap: 0.5 }}>
                    {instance.status === 'active' && (
                      <>
                        <Tooltip title="Pause SLA">
                          <IconButton
                            size="small"
                            onClick={() => handlePause(instance.instance_id)}
                          >
                            <PauseIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Complete SLA">
                          <IconButton
                            size="small"
                            color="success"
                            onClick={() => handleComplete(instance.instance_id)}
                          >
                            <CompleteIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </>
                    )}

                    {instance.status === 'paused' && (
                      <Tooltip title="Resume SLA">
                        <IconButton
                          size="small"
                          color="primary"
                          onClick={() => handleResume(instance.instance_id)}
                        >
                          <ResumeIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    )}

                    <Tooltip title="Process Escalations">
                      <IconButton
                        size="small"
                        onClick={() => handleProcessEscalations(instance.instance_id)}
                      >
                        <EscalateIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>

                    <Tooltip title="View History">
                      <IconButton size="small">
                        <HistoryIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </Box>
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </TableContainer>
  );

  return (
    <Box>
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4">SLA Dashboard</Typography>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          {autoRefresh && (
            <Chip
              label={`Auto-refresh: ${refreshInterval / 1000}s`}
              size="small"
              color="primary"
              variant="outlined"
            />
          )}
        </Box>
      </Box>

      {renderMetricsCards()}
      {renderInstancesTable()}
    </Box>
  );
};

export default SLADashboard;
