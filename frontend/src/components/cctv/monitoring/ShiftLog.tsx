/**
 * Shift Log Component
 * 
 * Manages shift handover logs for 24/7 monitoring personnel
 * Features:
 * - Create shift logs
 * - Record observations
 * - View shift history
 * - Shift handover documentation
 */

import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Grid,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  Divider,
  Chip
} from '@mui/material';
import {
  Assignment,
  Add,
  Schedule,
  Person
} from '@mui/icons-material';
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import monitoringService, { ShiftLog as ShiftLogType } from '../../../services/monitoringService';

const ShiftLog: React.FC = () => {
  const [logs, setLogs] = useState<ShiftLogType[]>([]);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    shift_start: new Date(),
    shift_end: new Date(),
    shift_personnel: '',
    observations: ''
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.shift_personnel.trim()) {
      newErrors.shift_personnel = 'Personnel name is required';
    }

    if (formData.shift_end <= formData.shift_start) {
      newErrors.shift_end = 'Shift end must be after shift start';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validateForm()) {
      return;
    }

    try {
      setLoading(true);
      const log = await monitoringService.createShiftLog({
        shift_start: formData.shift_start.toISOString(),
        shift_end: formData.shift_end.toISOString(),
        shift_personnel: formData.shift_personnel,
        observations: formData.observations || undefined
      });

      setLogs(prev => [log, ...prev]);
      setDialogOpen(false);
      resetForm();
      setLoading(false);
    } catch (error) {
      console.error('Failed to create shift log:', error);
      setLoading(false);
      alert('Failed to create shift log');
    }
  };

  const resetForm = () => {
    setFormData({
      shift_start: new Date(),
      shift_end: new Date(),
      shift_personnel: '',
      observations: ''
    });
    setErrors({});
  };

  const calculateShiftDuration = (start: string, end?: string) => {
    if (!end) return 'Ongoing';
    const duration = new Date(end).getTime() - new Date(start).getTime();
    const hours = Math.floor(duration / (1000 * 60 * 60));
    const minutes = Math.floor((duration % (1000 * 60 * 60)) / (1000 * 60));
    return `${hours}h ${minutes}m`;
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Box>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h6">
                <Assignment sx={{ mr: 1, verticalAlign: 'middle' }} />
                Shift Handover Logs
              </Typography>
              <Button
                variant="contained"
                startIcon={<Add />}
                onClick={() => setDialogOpen(true)}
              >
                Create Shift Log
              </Button>
            </Box>

            <Alert severity="info" sx={{ mb: 3 }}>
              <Typography variant="body2">
                Document shift changes, observations, incidents, and handover notes for 24/7 monitoring operations.
              </Typography>
            </Alert>

            {/* Shift Logs List */}
            {logs.length === 0 ? (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <Typography color="textSecondary">
                  No shift logs recorded yet. Click "Create Shift Log" to add one.
                </Typography>
              </Box>
            ) : (
              <List>
                {logs.map((log, index) => (
                  <React.Fragment key={log.id}>
                    <ListItem
                      sx={{
                        flexDirection: 'column',
                        alignItems: 'stretch',
                        bgcolor: 'background.paper',
                        borderRadius: 1,
                        mb: 1
                      }}
                    >
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Person color="primary" />
                          <Typography variant="subtitle1" fontWeight="bold">
                            {log.personnel}
                          </Typography>
                        </Box>
                        <Chip
                          label={calculateShiftDuration(log.shift_start, log.shift_end)}
                          size="small"
                          color="primary"
                        />
                      </Box>

                      <Grid container spacing={2}>
                        <Grid item xs={6}>
                          <Typography variant="caption" color="textSecondary">
                            Shift Start
                          </Typography>
                          <Typography variant="body2">
                            {new Date(log.shift_start).toLocaleString()}
                          </Typography>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="caption" color="textSecondary">
                            Shift End
                          </Typography>
                          <Typography variant="body2">
                            {log.shift_end ? new Date(log.shift_end).toLocaleString() : 'Ongoing'}
                          </Typography>
                        </Grid>
                      </Grid>

                      {log.observations && (
                        <Box sx={{ mt: 2 }}>
                          <Typography variant="caption" color="textSecondary">
                            Observations & Handover Notes
                          </Typography>
                          <Typography variant="body2" sx={{ mt: 0.5, whiteSpace: 'pre-wrap' }}>
                            {log.observations}
                          </Typography>
                        </Box>
                      )}
                    </ListItem>
                    {index < logs.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
            )}
          </CardContent>
        </Card>

        {/* Create Shift Log Dialog */}
        <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
          <DialogTitle>
            <Schedule sx={{ mr: 1, verticalAlign: 'middle' }} />
            Create Shift Handover Log
          </DialogTitle>
          <DialogContent>
            <Box sx={{ pt: 2 }}>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <DateTimePicker
                    label="Shift Start"
                    value={formData.shift_start}
                    onChange={(newValue) => setFormData({ ...formData, shift_start: newValue || new Date() })}
                    slotProps={{
                      textField: {
                        fullWidth: true,
                        error: !!errors.shift_start,
                        helperText: errors.shift_start
                      }
                    }}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <DateTimePicker
                    label="Shift End"
                    value={formData.shift_end}
                    onChange={(newValue) => setFormData({ ...formData, shift_end: newValue || new Date() })}
                    slotProps={{
                      textField: {
                        fullWidth: true,
                        error: !!errors.shift_end,
                        helperText: errors.shift_end
                      }
                    }}
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Personnel Name(s)"
                    value={formData.shift_personnel}
                    onChange={(e) => setFormData({ ...formData, shift_personnel: e.target.value })}
                    error={!!errors.shift_personnel}
                    helperText={errors.shift_personnel || 'Names of security personnel on shift'}
                    required
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Observations & Handover Notes"
                    value={formData.observations}
                    onChange={(e) => setFormData({ ...formData, observations: e.target.value })}
                    multiline
                    rows={6}
                    helperText="Document any incidents, unusual activities, system issues, or important notes for the next shift"
                    placeholder="Example:&#10;- All cameras operational&#10;- Motion detected at entrance at 14:30, staff identified&#10;- Camera 5 showing intermittent connection&#10;- No incidents to report"
                  />
                </Grid>
              </Grid>

              <Alert severity="info" sx={{ mt: 2 }}>
                <Typography variant="body2">
                  <strong>Best Practices:</strong><br />
                  • Record all incidents and unusual activities<br />
                  • Note any camera or system malfunctions<br />
                  • Document actions taken during the shift<br />
                  • Include relevant timestamps for events<br />
                  • Highlight critical items for next shift
                </Typography>
              </Alert>
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
            <Button
              onClick={handleSubmit}
              variant="contained"
              disabled={loading}
            >
              {loading ? 'Saving...' : 'Create Log'}
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </LocalizationProvider>
  );
};

export default ShiftLog;
