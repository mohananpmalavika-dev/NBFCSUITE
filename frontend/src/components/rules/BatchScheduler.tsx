/**
 * Batch Scheduler Component
 * 
 * Configure batch execution schedules with cron expressions
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Divider,
  Grid,
  Card,
  CardContent,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Alert,
  Chip,
  IconButton,
  Tooltip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import {
  Save as SaveIcon,
  Schedule as ScheduleIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
  Info as InfoIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  Email as EmailIcon,
} from '@mui/icons-material';

export interface BatchSchedule {
  schedule_id: string;
  schedule_name: string;
  ruleset_id: string;
  cron_expression: string;
  timezone: string;
  enabled: boolean;
  max_execution_time_seconds: number;
  data_source_type: string;
  data_source_config: any;
  batch_size: number;
  parallel_execution: boolean;
  max_parallel_threads: number;
  notify_on_completion: boolean;
  notify_on_failure: boolean;
  notification_emails: string[];
  last_execution_at?: string;
  last_execution_status?: string;
  next_execution_at?: string;
}

interface BatchSchedulerProps {
  rulesetId: string;
  schedule?: BatchSchedule;
  onSave: (schedule: BatchSchedule) => void;
  onCancel: () => void;
}

const BatchScheduler: React.FC<BatchSchedulerProps> = ({
  rulesetId,
  schedule,
  onSave,
  onCancel,
}) => {
  const [formData, setFormData] = useState<BatchSchedule>({
    schedule_id: schedule?.schedule_id || '',
    schedule_name: schedule?.schedule_name || '',
    ruleset_id: rulesetId,
    cron_expression: schedule?.cron_expression || '0 0 * * *',
    timezone: schedule?.timezone || 'UTC',
    enabled: schedule?.enabled !== false,
    max_execution_time_seconds: schedule?.max_execution_time_seconds || 300,
    data_source_type: schedule?.data_source_type || 'database',
    data_source_config: schedule?.data_source_config || {},
    batch_size: schedule?.batch_size || 100,
    parallel_execution: schedule?.parallel_execution || false,
    max_parallel_threads: schedule?.max_parallel_threads || 5,
    notify_on_completion: schedule?.notify_on_completion || false,
    notify_on_failure: schedule?.notify_on_failure !== false,
    notification_emails: schedule?.notification_emails || [],
  });

  const [newEmail, setNewEmail] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [cronHelper, setCronHelper] = useState({
    minute: '0',
    hour: '0',
    dayOfMonth: '*',
    month: '*',
    dayOfWeek: '*',
  });

  // Common cron presets
  const cronPresets = [
    { label: 'Every Minute', value: '* * * * *' },
    { label: 'Every 5 Minutes', value: '*/5 * * * *' },
    { label: 'Every 15 Minutes', value: '*/15 * * * *' },
    { label: 'Every Hour', value: '0 * * * *' },
    { label: 'Daily at Midnight', value: '0 0 * * *' },
    { label: 'Daily at 6 AM', value: '0 6 * * *' },
    { label: 'Daily at Noon', value: '0 12 * * *' },
    { label: 'Daily at 6 PM', value: '0 18 * * *' },
    { label: 'Weekly on Monday', value: '0 0 * * 1' },
    { label: 'Monthly on 1st', value: '0 0 1 * *' },
  ];

  const timezones = [
    'UTC',
    'America/New_York',
    'America/Chicago',
    'America/Los_Angeles',
    'Europe/London',
    'Europe/Paris',
    'Asia/Tokyo',
    'Asia/Shanghai',
    'Asia/Kolkata',
    'Australia/Sydney',
  ];

  const handleTextChange = (field: keyof BatchSchedule) => (event: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [field]: event.target.value,
    });
  };

  const handleNumberChange = (field: keyof BatchSchedule) => (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(event.target.value, 10);
    if (!isNaN(value)) {
      setFormData({
        ...formData,
        [field]: value,
      });
    }
  };

  const handleSwitchChange = (field: keyof BatchSchedule) => (event: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [field]: event.target.checked,
    });
  };

  const handleCronPresetChange = (preset: string) => {
    setFormData({
      ...formData,
      cron_expression: preset,
    });
  };

  const handleAddEmail = () => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (newEmail.trim() && emailRegex.test(newEmail.trim())) {
      setFormData({
        ...formData,
        notification_emails: [...formData.notification_emails, newEmail.trim()],
      });
      setNewEmail('');
    } else {
      setErrors({ ...errors, email: 'Invalid email address' });
    }
  };

  const handleRemoveEmail = (index: number) => {
    const updated = [...formData.notification_emails];
    updated.splice(index, 1);
    setFormData({
      ...formData,
      notification_emails: updated,
    });
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.schedule_name.trim()) {
      newErrors.schedule_name = 'Schedule name is required';
    }

    // Basic cron validation (5 parts)
    const cronParts = formData.cron_expression.split(' ');
    if (cronParts.length !== 5) {
      newErrors.cron_expression = 'Invalid cron expression (should have 5 parts)';
    }

    if (formData.batch_size < 1 || formData.batch_size > 10000) {
      newErrors.batch_size = 'Batch size must be between 1 and 10000';
    }

    if (formData.parallel_execution && (formData.max_parallel_threads < 1 || formData.max_parallel_threads > 50)) {
      newErrors.max_parallel_threads = 'Max parallel threads must be between 1 and 50';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = () => {
    if (validateForm()) {
      onSave(formData);
    }
  };

  const getCronDescription = (cron: string): string => {
    const preset = cronPresets.find(p => p.value === cron);
    if (preset) return preset.label;
    
    // Basic human-readable conversion
    const parts = cron.split(' ');
    if (parts.length !== 5) return 'Invalid cron expression';
    
    return `At ${parts[1]}:${parts[0]} on ${parts[2] === '*' ? 'every day' : `day ${parts[2]}`}`;
  };

  return (
    <Box>
      <Paper elevation={2} sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <ScheduleIcon color="primary" />
          Batch Execution Scheduler
        </Typography>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Configure scheduled batch execution for rules
        </Typography>
        <Divider sx={{ my: 2 }} />

        {/* Basic Settings */}
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Schedule Name"
              value={formData.schedule_name}
              onChange={handleTextChange('schedule_name')}
              error={!!errors.schedule_name}
              helperText={errors.schedule_name}
              required
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <FormControlLabel
              control={
                <Switch
                  checked={formData.enabled}
                  onChange={handleSwitchChange('enabled')}
                  color="primary"
                />
              }
              label={formData.enabled ? 'Enabled' : 'Disabled'}
            />
          </Grid>

          {/* Schedule Configuration */}
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              Schedule Configuration
            </Typography>
          </Grid>

          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Cron Preset</InputLabel>
              <Select
                value=""
                label="Cron Preset"
                onChange={(e) => handleCronPresetChange(e.target.value)}
              >
                {cronPresets.map((preset) => (
                  <MenuItem key={preset.value} value={preset.value}>
                    {preset.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Cron Expression"
              value={formData.cron_expression}
              onChange={handleTextChange('cron_expression')}
              error={!!errors.cron_expression}
              helperText={errors.cron_expression || getCronDescription(formData.cron_expression)}
              placeholder="0 0 * * *"
            />
          </Grid>

          <Grid item xs={12}>
            <Alert severity="info">
              <Typography variant="body2">
                Cron format: <code>minute hour day month weekday</code>
                <br />
                Use * for "any", numbers for specific values, */n for intervals
              </Typography>
            </Alert>
          </Grid>

          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Timezone</InputLabel>
              <Select
                value={formData.timezone}
                label="Timezone"
                onChange={(e) => setFormData({ ...formData, timezone: e.target.value })}
              >
                {timezones.map((tz) => (
                  <MenuItem key={tz} value={tz}>
                    {tz}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Max Execution Time (seconds)"
              type="number"
              value={formData.max_execution_time_seconds}
              onChange={handleNumberChange('max_execution_time_seconds')}
              inputProps={{ min: 1, max: 3600 }}
            />
          </Grid>

          {/* Data Source */}
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              Data Source
            </Typography>
          </Grid>

          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Data Source Type</InputLabel>
              <Select
                value={formData.data_source_type}
                label="Data Source Type"
                onChange={(e) => setFormData({ ...formData, data_source_type: e.target.value })}
              >
                <MenuItem value="database">Database Query</MenuItem>
                <MenuItem value="api">API Endpoint</MenuItem>
                <MenuItem value="file">File Upload</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          {/* Batch Processing */}
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              Batch Processing
            </Typography>
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Batch Size"
              type="number"
              value={formData.batch_size}
              onChange={handleNumberChange('batch_size')}
              error={!!errors.batch_size}
              helperText={errors.batch_size || 'Number of records per batch'}
              inputProps={{ min: 1, max: 10000 }}
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <FormControlLabel
              control={
                <Switch
                  checked={formData.parallel_execution}
                  onChange={handleSwitchChange('parallel_execution')}
                  color="primary"
                />
              }
              label="Enable Parallel Execution"
            />
          </Grid>

          {formData.parallel_execution && (
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Max Parallel Threads"
                type="number"
                value={formData.max_parallel_threads}
                onChange={handleNumberChange('max_parallel_threads')}
                error={!!errors.max_parallel_threads}
                helperText={errors.max_parallel_threads}
                inputProps={{ min: 1, max: 50 }}
              />
            </Grid>
          )}

          {/* Notifications */}
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <EmailIcon />
              Notifications
            </Typography>
          </Grid>

          <Grid item xs={12} md={6}>
            <FormControlLabel
              control={
                <Switch
                  checked={formData.notify_on_completion}
                  onChange={handleSwitchChange('notify_on_completion')}
                  color="primary"
                />
              }
              label="Notify on Completion"
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <FormControlLabel
              control={
                <Switch
                  checked={formData.notify_on_failure}
                  onChange={handleSwitchChange('notify_on_failure')}
                  color="primary"
                />
              }
              label="Notify on Failure"
            />
          </Grid>

          {(formData.notify_on_completion || formData.notify_on_failure) && (
            <>
              <Grid item xs={12}>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <TextField
                    fullWidth
                    size="small"
                    label="Notification Email"
                    value={newEmail}
                    onChange={(e) => setNewEmail(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleAddEmail()}
                    error={!!errors.email}
                    helperText={errors.email}
                    placeholder="email@example.com"
                  />
                  <Button
                    variant="outlined"
                    startIcon={<AddIcon />}
                    onClick={handleAddEmail}
                  >
                    Add
                  </Button>
                </Box>
              </Grid>

              <Grid item xs={12}>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {formData.notification_emails.map((email, index) => (
                    <Chip
                      key={index}
                      label={email}
                      onDelete={() => handleRemoveEmail(index)}
                      color="primary"
                      variant="outlined"
                      icon={<EmailIcon />}
                    />
                  ))}
                </Box>
              </Grid>
            </>
          )}

          {/* Execution Status */}
          {schedule && (
            <Grid item xs={12}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Execution Status
                  </Typography>
                  <TableContainer>
                    <Table size="small">
                      <TableBody>
                        <TableRow>
                          <TableCell>Last Execution</TableCell>
                          <TableCell>
                            {schedule.last_execution_at || 'Never'}
                          </TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell>Last Status</TableCell>
                          <TableCell>
                            {schedule.last_execution_status && (
                              <Chip
                                label={schedule.last_execution_status}
                                color={schedule.last_execution_status === 'success' ? 'success' : 'error'}
                                size="small"
                                icon={schedule.last_execution_status === 'success' ? <CheckCircleIcon /> : <CancelIcon />}
                              />
                            )}
                          </TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell>Next Execution</TableCell>
                          <TableCell>
                            {schedule.next_execution_at || 'Not scheduled'}
                          </TableCell>
                        </TableRow>
                      </TableBody>
                    </Table>
                  </TableContainer>
                </CardContent>
              </Card>
            </Grid>
          )}
        </Grid>

        {/* Action Buttons */}
        <Box sx={{ mt: 3, display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
          <Button variant="outlined" onClick={onCancel}>
            Cancel
          </Button>
          <Button
            variant="contained"
            startIcon={<SaveIcon />}
            onClick={handleSubmit}
            color="primary"
          >
            Save Schedule
          </Button>
        </Box>
      </Paper>
    </Box>
  );
};

export default BatchScheduler;
