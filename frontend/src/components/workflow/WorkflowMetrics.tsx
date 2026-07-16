/**
 * Workflow Metrics Component
 * 
 * Comprehensive metrics visualization with charts
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  LinearProgress,
  Tabs,
  Tab,
} from '@mui/material';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import analyticsService from '../../services/analyticsService';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

const WorkflowMetrics: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [period, setPeriod] = useState('this_month');
  const [activeTab, setActiveTab] = useState(0);
  const [workflowTypeMetrics, setWorkflowTypeMetrics] = useState<any[]>([]);
  const [stepMetrics, setStepMetrics] = useState<any[]>([]);
  const [userProductivity, setUserProductivity] = useState<any[]>([]);

  useEffect(() => {
    loadMetrics();
  }, [period]);

  const loadMetrics = async () => {
    setLoading(true);
    try {
      const [workflowData, stepData, userData] = await Promise.all([
        analyticsService.getWorkflowTypeMetrics(30),
        analyticsService.getStepMetrics(undefined, 30),
        analyticsService.getUserProductivity(undefined, 30)
      ]);

      setWorkflowTypeMetrics(workflowData);
      setStepMetrics(stepData);
      setUserProductivity(userData);
    } catch (err) {
      console.error('Failed to load metrics:', err);
    } finally {
      setLoading(false);
    }
  };

  const renderWorkflowTypeMetrics = () => {
    if (workflowTypeMetrics.length === 0) {
      return <Typography>No data available</Typography>;
    }

    const chartData = workflowTypeMetrics.map(wf => ({
      name: wf.workflow_name || wf.workflow_type,
      active: wf.active_workflows,
      completed: wf.completed_workflows,
      failed: wf.failed_workflows,
      avgTime: wf.avg_cycle_time_hours,
    }));

    return (
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Workflow Volume by Type
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="active" fill="#8884d8" name="Active" />
                  <Bar dataKey="completed" fill="#82ca9d" name="Completed" />
                  <Bar dataKey="failed" fill="#ff8042" name="Failed" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Average Cycle Time
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="avgTime"
                    stroke="#8884d8"
                    name="Avg Hours"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Workflow Type</TableCell>
                  <TableCell align="right">Total</TableCell>
                  <TableCell align="right">Active</TableCell>
                  <TableCell align="right">Completed</TableCell>
                  <TableCell align="right">Completion Rate</TableCell>
                  <TableCell align="right">Avg Cycle Time</TableCell>
                  <TableCell align="right">SLA Compliance</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {workflowTypeMetrics.map((wf, index) => (
                  <TableRow key={index}>
                    <TableCell>{wf.workflow_name || wf.workflow_type}</TableCell>
                    <TableCell align="right">{wf.total_workflows}</TableCell>
                    <TableCell align="right">
                      <Chip label={wf.active_workflows} size="small" color="primary" />
                    </TableCell>
                    <TableCell align="right">{wf.completed_workflows}</TableCell>
                    <TableCell align="right">
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Box sx={{ width: '100%', mr: 1 }}>
                          <LinearProgress
                            variant="determinate"
                            value={wf.completion_rate || 0}
                            color={analyticsService.getCompletionRateColor(wf.completion_rate)}
                          />
                        </Box>
                        <Typography variant="body2">
                          {(wf.completion_rate || 0).toFixed(1)}%
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell align="right">
                      {analyticsService.formatDuration(wf.avg_cycle_time_hours || 0)}
                    </TableCell>
                    <TableCell align="right">
                      <Typography
                        variant="body2"
                        color={analyticsService.getCompletionRateColor(wf.sla_compliance_rate || 0)}
                      >
                        {(wf.sla_compliance_rate || 0).toFixed(1)}%
                      </Typography>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Grid>
      </Grid>
    );
  };

  const renderStepMetrics = () => {
    if (stepMetrics.length === 0) {
      return <Typography>No step data available</Typography>;
    }

    return (
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Step</TableCell>
              <TableCell align="right">Executions</TableCell>
              <TableCell align="right">Success Rate</TableCell>
              <TableCell align="right">Avg Duration</TableCell>
              <TableCell align="right">Currently Pending</TableCell>
              <TableCell>Status</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {stepMetrics.map((step, index) => (
              <TableRow key={index} hover>
                <TableCell>
                  <Typography variant="body2" fontWeight="medium">
                    {step.step_name}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {step.step_type}
                  </Typography>
                </TableCell>
                <TableCell align="right">{step.total_executions}</TableCell>
                <TableCell align="right">
                  <Typography
                    variant="body2"
                    color={analyticsService.getCompletionRateColor(step.completion_rate || 0)}
                  >
                    {(step.completion_rate || 0).toFixed(1)}%
                  </Typography>
                </TableCell>
                <TableCell align="right">
                  {analyticsService.formatDuration(step.avg_duration_hours || 0)}
                </TableCell>
                <TableCell align="right">
                  <Chip label={step.currently_pending || 0} size="small" />
                </TableCell>
                <TableCell>
                  {step.is_bottleneck && (
                    <Chip
                      label={`Bottleneck (${step.bottleneck_severity})`}
                      color={analyticsService.getSeverityColor(step.bottleneck_severity || 'low') as any}
                      size="small"
                    />
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    );
  };

  const renderUserProductivity = () => {
    if (userProductivity.length === 0) {
      return <Typography>No user data available</Typography>;
    }

    const chartData = userProductivity.slice(0, 10).map(user => ({
      name: user.user_name,
      completed: user.tasks_completed,
      pending: user.tasks_pending,
      completionRate: user.completion_rate,
    }));

    return (
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Task Completion by User
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="completed" fill="#82ca9d" name="Completed" />
                  <Bar dataKey="pending" fill="#8884d8" name="Pending" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Completion Rate by User
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={chartData.slice(0, 5)}
                    dataKey="completionRate"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    label
                  >
                    {chartData.slice(0, 5).map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>User</TableCell>
                  <TableCell align="right">Total Assigned</TableCell>
                  <TableCell align="right">Completed</TableCell>
                  <TableCell align="right">Pending</TableCell>
                  <TableCell align="right">Completion Rate</TableCell>
                  <TableCell align="right">Avg Response Time</TableCell>
                  <TableCell align="right">Approval Rate</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {userProductivity.map((user, index) => (
                  <TableRow key={index} hover>
                    <TableCell>{user.user_name}</TableCell>
                    <TableCell align="right">{user.total_tasks_assigned}</TableCell>
                    <TableCell align="right">
                      <Chip label={user.tasks_completed} size="small" color="success" />
                    </TableCell>
                    <TableCell align="right">
                      <Chip label={user.tasks_pending} size="small" />
                    </TableCell>
                    <TableCell align="right">
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Box sx={{ width: '100%', mr: 1 }}>
                          <LinearProgress
                            variant="determinate"
                            value={user.completion_rate || 0}
                            color={analyticsService.getCompletionRateColor(user.completion_rate)}
                          />
                        </Box>
                        <Typography variant="body2">
                          {(user.completion_rate || 0).toFixed(1)}%
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell align="right">
                      {analyticsService.formatDuration(user.avg_response_time_hours || 0)}
                    </TableCell>
                    <TableCell align="right">
                      {(user.approval_rate || 0).toFixed(1)}%
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Grid>
      </Grid>
    );
  };

  return (
    <Box>
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4">Workflow Metrics</Typography>
        <FormControl sx={{ minWidth: 200 }}>
          <InputLabel>Period</InputLabel>
          <Select
            value={period}
            onChange={(e) => setPeriod(e.target.value)}
            label="Period"
          >
            <MenuItem value="today">Today</MenuItem>
            <MenuItem value="this_week">This Week</MenuItem>
            <MenuItem value="this_month">This Month</MenuItem>
            <MenuItem value="this_quarter">This Quarter</MenuItem>
            <MenuItem value="this_year">This Year</MenuItem>
          </Select>
        </FormControl>
      </Box>

      <Paper>
        <Tabs value={activeTab} onChange={(e, v) => setActiveTab(v)}>
          <Tab label="Workflow Types" />
          <Tab label="Step Analysis" />
          <Tab label="User Productivity" />
        </Tabs>

        <Box sx={{ p: 3 }}>
          {loading && <LinearProgress />}
          {!loading && activeTab === 0 && renderWorkflowTypeMetrics()}
          {!loading && activeTab === 1 && renderStepMetrics()}
          {!loading && activeTab === 2 && renderUserProductivity()}
        </Box>
      </Paper>
    </Box>
  );
};

export default WorkflowMetrics;
