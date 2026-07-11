/**
 * Leave Management Page
 * Apply for leave, view leave balance and history
 */

import React, { useEffect, useState } from 'react';
import {
  Box,
  Container,
  Card,
  CardContent,
  Typography,
  Button,
  IconButton,
  Grid,
  TextField,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Alert,
  CircularProgress,
  Chip,
  Divider,
  FormControlLabel,
  Checkbox,
  Paper
} from '@mui/material';
import {
  Add as AddIcon,
  ArrowBack as ArrowBackIcon,
  Event as EventIcon,
  Cancel as CancelIcon,
  CheckCircle as CheckCircleIcon,
  HourglassEmpty as HourglassEmptyIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';

interface LeaveBalance {
  leave_type: string;
  financial_year: string;
  opening_balance: number;
  accrued: number;
  used: number;
  current_balance: number;
}

interface LeaveApplication {
  id: string;
  application_code: string;
  leave_type: string;
  from_date: string;
  to_date: string;
  number_of_days: number;
  is_half_day: boolean;
  reason: string;
  status: string;
  submitted_date: string;
  approver1_name: string;
}

const leaveTypes = [
  { value: 'casual', label: 'Casual Leave' },
  { value: 'sick', label: 'Sick Leave' },
  { value: 'earned', label: 'Earned Leave' },
  { value: 'compensatory_off', label: 'Compensatory Off' },
  { value: 'maternity', label: 'Maternity Leave' },
  { value: 'paternity', label: 'Paternity Leave' },
  { value: 'work_from_home', label: 'Work From Home' }
];

const Leaves: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [balances, setBalances] = useState<LeaveBalance[]>([]);
  const [applications, setApplications] = useState<LeaveApplication[]>([]);
  const [openDialog, setOpenDialog] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  
  // Form state
  const [formData, setFormData] = useState({
    leave_type: '',
    from_date: null as Date | null,
    to_date: null as Date | null,
    is_half_day: false,
    half_day_session: 'first_half',
    reason: '',
    contact_number_during_leave: '',
    contact_address_during_leave: ''
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [balancesRes, applicationsRes] = await Promise.all([
        axios.get('/api/hrms/ess/leave/balances'),
        axios.get('/api/hrms/ess/leave/applications')
      ]);
      setBalances(balancesRes.data);
      setApplications(applicationsRes.data.items);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to load leave data');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    try {
      setSubmitting(true);
      const payload = {
        ...formData,
        from_date: formData.from_date?.toISOString().split('T')[0],
        to_date: formData.to_date?.toISOString().split('T')[0]
      };
      
      const response = await axios.post('/api/hrms/ess/leave/applications', payload);
      
      // Submit the application
      await axios.post(`/api/hrms/ess/leave/applications/${response.data.id}/submit`);
      
      setOpenDialog(false);
      fetchData();
      
      // Reset form
      setFormData({
        leave_type: '',
        from_date: null,
        to_date: null,
        is_half_day: false,
        half_day_session: 'first_half',
        reason: '',
        contact_number_during_leave: '',
        contact_address_during_leave: ''
      });
    } catch (err: any) {
      alert(err.response?.data?.message || 'Failed to submit leave application');
    } finally {
      setSubmitting(false);
    }
  };

  const handleCancel = async (applicationId: string) => {
    if (!confirm('Are you sure you want to cancel this leave application?')) return;
    
    try {
      const reason = prompt('Please provide a reason for cancellation:');
      if (!reason) return;
      
      await axios.post(`/api/hrms/ess/leave/applications/${applicationId}/cancel`, null, {
        params: { reason }
      });
      fetchData();
    } catch (err: any) {
      alert(err.response?.data?.message || 'Failed to cancel leave application');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved': return 'success';
      case 'rejected': return 'error';
      case 'pending_approval': return 'warning';
      case 'cancelled': return 'default';
      default: return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'approved': return <CheckCircleIcon fontSize="small" />;
      case 'rejected': return <CancelIcon fontSize="small" />;
      case 'pending_approval': return <HourglassEmptyIcon fontSize="small" />;
      default: return null;
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
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        {/* Header */}
        <Box display="flex" alignItems="center" mb={3}>
          <IconButton onClick={() => navigate('/ess')} sx={{ mr: 2 }}>
            <ArrowBackIcon />
          </IconButton>
          <Box flex={1}>
            <Typography variant="h4" fontWeight={600}>
              Leave Management
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Apply for leave and manage your applications
            </Typography>
          </Box>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setOpenDialog(true)}
          >
            Apply for Leave
          </Button>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        <Grid container spacing={3}>
          {/* Leave Balance */}
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Leave Balance
                </Typography>
                <Divider sx={{ mb: 2 }} />
                {balances.map((balance) => (
                  <Paper key={balance.leave_type} sx={{ p: 2, mb: 2, bgcolor: 'grey.50' }}>
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                      <Box>
                        <Typography variant="body2" fontWeight={600}>
                          {balance.leave_type.replace('_', ' ').toUpperCase()}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Used: {balance.used} days
                        </Typography>
                      </Box>
                      <Typography variant="h5" fontWeight={700} color="primary">
                        {balance.current_balance}
                      </Typography>
                    </Box>
                  </Paper>
                ))}
              </CardContent>
            </Card>
          </Grid>

          {/* Leave Applications */}
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Leave Applications
                </Typography>
                <Divider sx={{ mb: 2 }} />
                
                {applications.length > 0 ? (
                  <TableContainer>
                    <Table>
                      <TableHead>
                        <TableRow>
                          <TableCell>Type</TableCell>
                          <TableCell>From - To</TableCell>
                          <TableCell align="center">Days</TableCell>
                          <TableCell>Status</TableCell>
                          <TableCell align="center">Actions</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {applications.map((app) => (
                          <TableRow key={app.id}>
                            <TableCell>
                              <Typography variant="body2" fontWeight={600}>
                                {app.leave_type.replace('_', ' ').toUpperCase()}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                {app.application_code}
                              </Typography>
                            </TableCell>
                            <TableCell>
                              <Typography variant="body2">
                                {new Date(app.from_date).toLocaleDateString()} - {new Date(app.to_date).toLocaleDateString()}
                              </Typography>
                            </TableCell>
                            <TableCell align="center">
                              <Chip label={app.number_of_days} size="small" />
                            </TableCell>
                            <TableCell>
                              <Chip
                                icon={getStatusIcon(app.status)}
                                label={app.status.replace('_', ' ').toUpperCase()}
                                color={getStatusColor(app.status)}
                                size="small"
                              />
                            </TableCell>
                            <TableCell align="center">
                              {(app.status === 'draft' || app.status === 'pending_approval') && (
                                <IconButton
                                  size="small"
                                  color="error"
                                  onClick={() => handleCancel(app.id)}
                                >
                                  <CancelIcon fontSize="small" />
                                </IconButton>
                              )}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                ) : (
                  <Typography variant="body2" color="text.secondary" textAlign="center" py={4}>
                    No leave applications found
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Apply Leave Dialog */}
        <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
          <DialogTitle>Apply for Leave</DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12}>
                <TextField
                  select
                  fullWidth
                  label="Leave Type"
                  value={formData.leave_type}
                  onChange={(e) => setFormData({ ...formData, leave_type: e.target.value })}
                  required
                >
                  {leaveTypes.map((type) => (
                    <MenuItem key={type.value} value={type.value}>
                      {type.label}
                    </MenuItem>
                  ))}
                </TextField>
              </Grid>

              <Grid item xs={6}>
                <DatePicker
                  label="From Date"
                  value={formData.from_date}
                  onChange={(date) => setFormData({ ...formData, from_date: date })}
                  slotProps={{ textField: { fullWidth: true, required: true } }}
                />
              </Grid>

              <Grid item xs={6}>
                <DatePicker
                  label="To Date"
                  value={formData.to_date}
                  onChange={(date) => setFormData({ ...formData, to_date: date })}
                  minDate={formData.from_date || undefined}
                  slotProps={{ textField: { fullWidth: true, required: true } }}
                />
              </Grid>

              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={formData.is_half_day}
                      onChange={(e) => setFormData({ ...formData, is_half_day: e.target.checked })}
                    />
                  }
                  label="Half Day Leave"
                />
              </Grid>

              {formData.is_half_day && (
                <Grid item xs={12}>
                  <TextField
                    select
                    fullWidth
                    label="Half Day Session"
                    value={formData.half_day_session}
                    onChange={(e) => setFormData({ ...formData, half_day_session: e.target.value })}
                  >
                    <MenuItem value="first_half">First Half</MenuItem>
                    <MenuItem value="second_half">Second Half</MenuItem>
                  </TextField>
                </Grid>
              )}

              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  label="Reason"
                  value={formData.reason}
                  onChange={(e) => setFormData({ ...formData, reason: e.target.value })}
                  required
                  helperText="Minimum 10 characters required"
                />
              </Grid>

              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Contact Number During Leave"
                  value={formData.contact_number_during_leave}
                  onChange={(e) => setFormData({ ...formData, contact_number_during_leave: e.target.value })}
                />
              </Grid>

              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={2}
                  label="Contact Address During Leave"
                  value={formData.contact_address_during_leave}
                  onChange={(e) => setFormData({ ...formData, contact_address_during_leave: e.target.value })}
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setOpenDialog(false)} disabled={submitting}>
              Cancel
            </Button>
            <Button
              variant="contained"
              onClick={handleSubmit}
              disabled={submitting || !formData.leave_type || !formData.from_date || !formData.to_date || formData.reason.length < 10}
            >
              {submitting ? <CircularProgress size={24} /> : 'Submit Application'}
            </Button>
          </DialogActions>
        </Dialog>
      </Container>
    </LocalizationProvider>
  );
};

export default Leaves;
