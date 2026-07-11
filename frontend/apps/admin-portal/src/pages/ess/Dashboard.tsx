/**
 * Employee Self-Service Dashboard
 * Main landing page for employee self-service portal
 */

import React, { useEffect, useState } from 'react';
import {
  Box,
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  IconButton,
  Avatar,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Paper,
  Alert,
  CircularProgress,
  Chip
} from '@mui/material';
import {
  Receipt as ReceiptIcon,
  Event as EventIcon,
  AccountBalance as AccountBalanceIcon,
  Payment as PaymentIcon,
  Person as PersonIcon,
  ArrowForward as ArrowForwardIcon,
  Download as DownloadIcon,
  TrendingUp as TrendingUpIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

interface DashboardStats {
  total_leave_balance: number;
  pending_leave_applications: number;
  approved_leaves_this_month: number;
  has_active_declaration: boolean;
  declaration_status: string | null;
  total_declared_amount: number;
  pending_reimbursement_claims: number;
  approved_claims_pending_payment: number;
  total_pending_amount: number;
  profile_completion_percentage: number;
  profile_update_required: boolean;
}

const ESSDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentPayslips, setRecentPayslips] = useState<any[]>([]);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [statsResponse, payslipsResponse] = await Promise.all([
        axios.get('/api/hrms/ess/dashboard'),
        axios.get('/api/hrms/ess/payslips?page=1&page_size=3')
      ]);
      
      setStats(statsResponse.data);
      setRecentPayslips(payslipsResponse.data);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Welcome Section */}
      <Paper sx={{ p: 3, mb: 3, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box>
            <Typography variant="h4" sx={{ color: 'white', fontWeight: 600 }}>
              Welcome to Employee Self-Service
            </Typography>
            <Typography variant="body1" sx={{ color: 'rgba(255,255,255,0.9)', mt: 1 }}>
              Manage your payslips, leaves, investments, and reimbursements
            </Typography>
          </Box>
          <Avatar sx={{ width: 80, height: 80, bgcolor: 'white', color: '#667eea' }}>
            <PersonIcon sx={{ fontSize: 50 }} />
          </Avatar>
        </Box>
      </Paper>

      {/* Quick Stats */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h4" sx={{ color: 'white', fontWeight: 700 }}>
                    {stats?.total_leave_balance || 0}
                  </Typography>
                  <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.9)' }}>
                    Leave Balance
                  </Typography>
                </Box>
                <EventIcon sx={{ fontSize: 40, color: 'rgba(255,255,255,0.8)' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%', background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h4" sx={{ color: 'white', fontWeight: 700 }}>
                    {stats?.pending_leave_applications || 0}
                  </Typography>
                  <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.9)' }}>
                    Pending Leaves
                  </Typography>
                </Box>
                <WarningIcon sx={{ fontSize: 40, color: 'rgba(255,255,255,0.8)' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%', background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)' }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h4" sx={{ color: 'white', fontWeight: 700 }}>
                    ₹{stats?.total_declared_amount.toLocaleString() || 0}
                  </Typography>
                  <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.9)' }}>
                    Tax Savings
                  </Typography>
                </Box>
                <AccountBalanceIcon sx={{ fontSize: 40, color: 'rgba(255,255,255,0.8)' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%', background: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)' }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h4" sx={{ color: 'white', fontWeight: 700 }}>
                    ₹{stats?.total_pending_amount.toLocaleString() || 0}
                  </Typography>
                  <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.9)' }}>
                    Pending Claims
                  </Typography>
                </Box>
                <PaymentIcon sx={{ fontSize: 40, color: 'rgba(255,255,255,0.8)' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Quick Actions */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Quick Actions
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <Button
                    variant="outlined"
                    fullWidth
                    startIcon={<ReceiptIcon />}
                    endIcon={<ArrowForwardIcon />}
                    onClick={() => navigate('/ess/payslips')}
                    sx={{ justifyContent: 'space-between', py: 1.5 }}
                  >
                    View Payslips
                  </Button>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Button
                    variant="outlined"
                    fullWidth
                    startIcon={<EventIcon />}
                    endIcon={<ArrowForwardIcon />}
                    onClick={() => navigate('/ess/leaves')}
                    sx={{ justifyContent: 'space-between', py: 1.5 }}
                  >
                    Apply for Leave
                  </Button>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Button
                    variant="outlined"
                    fullWidth
                    startIcon={<AccountBalanceIcon />}
                    endIcon={<ArrowForwardIcon />}
                    onClick={() => navigate('/ess/investments')}
                    sx={{ justifyContent: 'space-between', py: 1.5 }}
                  >
                    Investment Declaration
                  </Button>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Button
                    variant="outlined"
                    fullWidth
                    startIcon={<PaymentIcon />}
                    endIcon={<ArrowForwardIcon />}
                    onClick={() => navigate('/ess/reimbursements')}
                    sx={{ justifyContent: 'space-between', py: 1.5 }}
                  >
                    Submit Claim
                  </Button>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Button
                    variant="outlined"
                    fullWidth
                    startIcon={<PersonIcon />}
                    endIcon={<ArrowForwardIcon />}
                    onClick={() => navigate('/ess/profile')}
                    sx={{ justifyContent: 'space-between', py: 1.5 }}
                  >
                    Update Profile
                  </Button>
                </Grid>
              </Grid>
            </CardContent>
          </Card>

          {/* Recent Payslips */}
          <Card sx={{ mt: 3 }}>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6">
                  Recent Payslips
                </Typography>
                <Button
                  size="small"
                  endIcon={<ArrowForwardIcon />}
                  onClick={() => navigate('/ess/payslips')}
                >
                  View All
                </Button>
              </Box>
              <Divider sx={{ mb: 2 }} />
              {recentPayslips.length > 0 ? (
                <List>
                  {recentPayslips.map((payslip) => (
                    <ListItem
                      key={payslip.id}
                      secondaryAction={
                        <IconButton edge="end" onClick={() => handleDownloadPayslip(payslip.id)}>
                          <DownloadIcon />
                        </IconButton>
                      }
                    >
                      <ListItemIcon>
                        <ReceiptIcon color="primary" />
                      </ListItemIcon>
                      <ListItemText
                        primary={`${payslip.month}/${payslip.year}`}
                        secondary={`Net Salary: ₹${payslip.net_salary.toLocaleString()}`}
                      />
                    </ListItem>
                  ))}
                </List>
              ) : (
                <Typography variant="body2" color="text.secondary" textAlign="center" py={2}>
                  No payslips available
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Notifications & Alerts */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Notifications & Alerts
              </Typography>
              <Divider sx={{ mb: 2 }} />

              {stats?.profile_update_required && (
                <Alert severity="warning" sx={{ mb: 2 }}>
                  <Typography variant="body2">
                    Profile Completion: {stats?.profile_completion_percentage}%
                  </Typography>
                  <Button
                    size="small"
                    onClick={() => navigate('/ess/profile')}
                    sx={{ mt: 1 }}
                  >
                    Update Now
                  </Button>
                </Alert>
              )}

              {stats?.has_active_declaration && (
                <Alert severity="info" sx={{ mb: 2 }}>
                  <Typography variant="body2">
                    Investment Declaration Status: {stats?.declaration_status}
                  </Typography>
                </Alert>
              )}

              {stats && stats.pending_reimbursement_claims > 0 && (
                <Alert severity="info" sx={{ mb: 2 }}>
                  <Typography variant="body2">
                    {stats.pending_reimbursement_claims} reimbursement claim(s) pending approval
                  </Typography>
                </Alert>
              )}

              {(!stats?.profile_update_required && !stats?.has_active_declaration && 
                (!stats || stats.pending_reimbursement_claims === 0)) && (
                <Typography variant="body2" color="text.secondary" textAlign="center" py={2}>
                  No new notifications
                </Typography>
              )}
            </CardContent>
          </Card>

          {/* Leave Balance Details */}
          <Card sx={{ mt: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Leave Balance
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <Box>
                <Box display="flex" justifyContent="space-between" mb={1}>
                  <Typography variant="body2" color="text.secondary">Casual Leave</Typography>
                  <Typography variant="body2" fontWeight={600}>8 days</Typography>
                </Box>
                <Box display="flex" justifyContent="space-between" mb={1}>
                  <Typography variant="body2" color="text.secondary">Sick Leave</Typography>
                  <Typography variant="body2" fontWeight={600}>6 days</Typography>
                </Box>
                <Box display="flex" justifyContent="space-between" mb={1}>
                  <Typography variant="body2" color="text.secondary">Earned Leave</Typography>
                  <Typography variant="body2" fontWeight={600}>12 days</Typography>
                </Box>
                <Button
                  fullWidth
                  variant="text"
                  size="small"
                  endIcon={<ArrowForwardIcon />}
                  onClick={() => navigate('/ess/leaves')}
                  sx={{ mt: 1 }}
                >
                  View Details
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );

  async function handleDownloadPayslip(payslipId: string) {
    try {
      const response = await axios.get(`/api/hrms/ess/payslips/${payslipId}/download`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `payslip_${payslipId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error('Failed to download payslip:', err);
    }
  }
};

export default ESSDashboard;
