/**
 * Workflow Execution Dashboard
 * Monitor and manage workflow instances
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
  Button,
  IconButton,
  Stack,
  TextField,
  InputAdornment,
  Tabs,
  Tab,
  LinearProgress,
} from '@mui/material';
import {
  Search as SearchIcon,
  Visibility as ViewIcon,
  PlayArrow as StartIcon,
  Refresh as RefreshIcon,
  Assignment as TaskIcon,
  AccountTree as WorkflowIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import workflowService from '../../services/workflowService';

interface DashboardStats {
  totalWorkflows: number;
  activeWorkflows: number;
  completedToday: number;
  pendingTasks: number;
}

const WorkflowDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState(0);
  const [instances, setInstances] = useState<any[]>([]);
  const [myTasks, setMyTasks] = useState<any[]>([]);
  const [stats, setStats] = useState<DashboardStats>({
    totalWorkflows: 0,
    activeWorkflows: 0,
    completedToday: 0,
    pendingTasks: 0,
  });
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadData();
  }, [activeTab]);

  const loadData = async () => {
    setLoading(true);
    try {
      if (activeTab === 0) {
        // Load instances
        const response = await workflowService.getInstances({ limit: 50 });
        setInstances(response.instances || []);
        
        // Calculate stats
        const active = response.instances?.filter(
          (i: any) => i.status === 'in_progress'
        ).length || 0;
        const completedToday = response.instances?.filter(
          (i: any) => 
            i.status === 'completed' && 
            isToday(new Date(i.completed_at))
        ).length || 0;
        
        setStats({
          totalWorkflows: response.instances?.length || 0,
          activeWorkflows: active,
          completedToday,
          pendingTasks: stats.pendingTasks,
        });
      } else {
        // Load my tasks
        const response = await workflowService.getMyTasks({ limit: 50 });
        setMyTasks(response.tasks || []);
        
        const pending = response.tasks?.filter(
          (t: any) => t.status === 'pending'
        ).length || 0;
        
        setStats({
          ...stats,
          pendingTasks: pending,
        });
      }
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  const isToday = (date: Date) => {
    const today = new Date();
    return (
      date.getDate() === today.getDate() &&
      date.getMonth() === today.getMonth() &&
      date.getFullYear() === today.getFullYear()
    );
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'in_progress':
        return 'primary';
      case 'pending':
        return 'warning';
      case 'failed':
      case 'cancelled':
        return 'error';
      default:
        return 'default';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent':
        return 'error';
      case 'high':
        return 'warning';
      case 'normal':
        return 'info';
      case 'low':
        return 'default';
      default:
        return 'default';
    }
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  };

  const handleViewInstance = (instanceId: number) => {
    navigate(`/workflow/instances/${instanceId}`);
  };

  const handleViewTask = (taskId: number) => {
    navigate(`/workflow/tasks/${taskId}`);
  };

  const filteredInstances = instances.filter((instance) =>
    instance.instance_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    instance.instance_name?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const filteredTasks = myTasks.filter((task) =>
    task.task_title?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" fontWeight="bold">
          Workflow Dashboard
        </Typography>
        <Stack direction="row" spacing={2}>
          <Button
            startIcon={<RefreshIcon />}
            onClick={loadData}
            variant="outlined"
          >
            Refresh
          </Button>
          <Button
            startIcon={<WorkflowIcon />}
            onClick={() => navigate('/workflow/designer')}
            variant="contained"
          >
            Design Workflow
          </Button>
        </Stack>
      </Stack>

      {/* Stats Cards */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Stack direction="row" justifyContent="space-between" alignItems="center">
                <Box>
                  <Typography variant="h4" fontWeight="bold">
                    {stats.totalWorkflows}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Total Workflows
                  </Typography>
                </Box>
                <WorkflowIcon sx={{ fontSize: 48, color: 'primary.main', opacity: 0.3 }} />
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Stack direction="row" justifyContent="space-between" alignItems="center">
                <Box>
                  <Typography variant="h4" fontWeight="bold" color="primary">
                    {stats.activeWorkflows}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Active Workflows
                  </Typography>
                </Box>
                <PlayArrow sx={{ fontSize: 48, color: 'primary.main', opacity: 0.3 }} />
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Stack direction="row" justifyContent="space-between" alignItems="center">
                <Box>
                  <Typography variant="h4" fontWeight="bold" color="success.main">
                    {stats.completedToday}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Completed Today
                  </Typography>
                </Box>
                <ViewIcon sx={{ fontSize: 48, color: 'success.main', opacity: 0.3 }} />
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Stack direction="row" justifyContent="space-between" alignItems="center">
                <Box>
                  <Typography variant="h4" fontWeight="bold" color="warning.main">
                    {stats.pendingTasks}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Pending Tasks
                  </Typography>
                </Box>
                <TaskIcon sx={{ fontSize: 48, color: 'warning.main', opacity: 0.3 }} />
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      </Grid>


      {/* Main Content */}
      <Paper>
        {/* Tabs */}
        <Tabs value={activeTab} onChange={(e, v) => setActiveTab(v)}>
          <Tab label="Workflow Instances" />
          <Tab label="My Tasks" />
        </Tabs>

        {loading && <LinearProgress />}

        {/* Search */}
        <Box sx={{ p: 2 }}>
          <TextField
            fullWidth
            size="small"
            placeholder={activeTab === 0 ? "Search workflows..." : "Search tasks..."}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
          />
        </Box>

        {/* Workflow Instances Table */}
        {activeTab === 0 && (
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Instance Number</TableCell>
                  <TableCell>Name</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Priority</TableCell>
                  <TableCell>Started</TableCell>
                  <TableCell>Completed</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredInstances.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} align="center">
                      <Typography variant="body2" color="textSecondary" py={3}>
                        No workflow instances found
                      </Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredInstances.map((instance) => (
                    <TableRow key={instance.id} hover>
                      <TableCell>{instance.instance_number}</TableCell>
                      <TableCell>{instance.instance_name || '-'}</TableCell>
                      <TableCell>
                        <Chip
                          label={instance.status}
                          color={getStatusColor(instance.status)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={instance.priority}
                          color={getPriorityColor(instance.priority)}
                          size="small"
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell>{formatDate(instance.started_at)}</TableCell>
                      <TableCell>{formatDate(instance.completed_at)}</TableCell>
                      <TableCell align="right">
                        <IconButton
                          size="small"
                          onClick={() => handleViewInstance(instance.id)}
                        >
                          <ViewIcon />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        )}

        {/* My Tasks Table */}
        {activeTab === 1 && (
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Task</TableCell>
                  <TableCell>Workflow</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Priority</TableCell>
                  <TableCell>Due Date</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredTasks.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} align="center">
                      <Typography variant="body2" color="textSecondary" py={3}>
                        No tasks assigned to you
                      </Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredTasks.map((task) => (
                    <TableRow key={task.id} hover>
                      <TableCell>
                        <Typography variant="body2" fontWeight="medium">
                          {task.task_title}
                        </Typography>
                        {task.task_description && (
                          <Typography variant="caption" color="textSecondary">
                            {task.task_description}
                          </Typography>
                        )}
                      </TableCell>
                      <TableCell>{task.workflow_instance_number || '-'}</TableCell>
                      <TableCell>
                        <Chip label={task.task_type} size="small" variant="outlined" />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={task.status}
                          color={getStatusColor(task.status)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={task.priority}
                          color={getPriorityColor(task.priority)}
                          size="small"
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell>{formatDate(task.due_date)}</TableCell>
                      <TableCell align="right">
                        <Button
                          size="small"
                          variant="contained"
                          startIcon={<ViewIcon />}
                          onClick={() => handleViewTask(task.id)}
                        >
                          Open
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Paper>
    </Box>
  );
};

export default WorkflowDashboard;
