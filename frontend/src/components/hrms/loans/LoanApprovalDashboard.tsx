/**
 * Loan Approval Dashboard Component
 * For managers, HR, and finance to approve/reject loan applications
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  FormControlLabel,
  Grid,
  IconButton,
  Paper,
  Radio,
  RadioGroup,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TablePagination,
  TableRow,
  Tabs,
  Tab,
  TextField,
  Typography,
  Alert,
  CircularProgress,
  Tooltip,
} from '@mui/material';
import {
  Visibility as ViewIcon,
  CheckCircle as ApproveIcon,
  Cancel as RejectIcon,
  Schedule as ScheduleIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import loanService, { Loan, LoanStatus, LoanApprovalAction } from '../../../services/hrms/loanService';
import { format } from 'date-fns';

interface ApprovalDialogState {
  open: boolean;
  loan: Loan | null;
  action: 'approve' | 'reject' | null;
  comments: string;
  approvedAmount?: number;
  error: string;
}

const LoanApprovalDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState(0);
  const [loans, setLoans] = useState<Loan[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [total, setTotal] = useState(0);
  const [processing, setProcessing] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  const [dialogState, setDialogState] = useState<ApprovalDialogState>({
    open: false,
    loan: null,
    action: null,
    comments: '',
    error: '',
  });

  // Determine user role and approval stage
  const [userRole, setUserRole] = useState<'manager' | 'hr' | 'finance'>('manager');

  useEffect(() => {
    // TODO: Get user role from auth context
    // For now, defaulting to manager
    fetchPendingLoans();
  }, [page, rowsPerPage, activeTab]);

  const fetchPendingLoans = async () => {
    setLoading(true);
    try {
      const response = await loanService.getAllLoans({
        status: LoanStatus.PENDING_APPROVAL,
        page: page + 1,
        page_size: rowsPerPage,
      });

      // Filter based on approval stage
      let filteredLoans = response.items;
      if (activeTab === 0) {
        // Manager pending
        filteredLoans = response.items.filter(
          (l) => l.manager_approval_status === 'pending'
        );
      } else if (activeTab === 1) {
        // HR pending
        filteredLoans = response.items.filter(
          (l) => l.manager_approval_status === 'approved' && l.hr_approval_status === 'pending'
        );
      } else if (activeTab === 2) {
        // Finance pending
        filteredLoans = response.items.filter(
          (l) =>
            l.manager_approval_status === 'approved' &&
            l.hr_approval_status === 'approved' &&
            l.finance_approval_status === 'pending'
        );
      }

      setLoans(filteredLoans);
      setTotal(filteredLoans.length);
    } catch (error) {
      console.error('Error fetching loans:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (loan: Loan, action: 'approve' | 'reject') => {
    setDialogState({
      open: true,
      loan,
      action,
      comments: '',
      approvedAmount: loan.loan_amount,
      error: '',
    });
  };

  const handleCloseDialog = () => {
    setDialogState({
      open: false,
      loan: null,
      action: null,
      comments: '',
      error: '',
    });
  };

  const handleApproval = async () => {
    if (!dialogState.loan || !dialogState.action) return;

    setProcessing(true);
    setDialogState({ ...dialogState, error: '' });

    try {
      const approvalData: LoanApprovalAction = {
        action: dialogState.action,
        comments: dialogState.comments || undefined,
        approved_amount:
          dialogState.action === 'approve' ? dialogState.approvedAmount : undefined,
      };

      // Determine which approval endpoint to call
      if (activeTab === 0) {
        await loanService.approveByManager(dialogState.loan.id, approvalData);
      } else if (activeTab === 1) {
        await loanService.approveByHR(dialogState.loan.id, approvalData);
      } else if (activeTab === 2) {
        await loanService.approveByFinance(dialogState.loan.id, approvalData);
      }

      setSuccessMessage(
        `Loan ${dialogState.action === 'approve' ? 'approved' : 'rejected'} successfully`
      );
      handleCloseDialog();
      fetchPendingLoans();
    } catch (error: any) {
      setDialogState({
        ...dialogState,
        error: error.response?.data?.detail || 'Error processing approval',
      });
    } finally {
      setProcessing(false);
    }
  };

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const renderApprovalDialog = () => {
    const { open, loan, action, comments, approvedAmount, error } = dialogState;

    if (!loan) return null;

    return (
      <Dialog open={open} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {action === 'approve' ? 'Approve Loan' : 'Reject Loan'}
        </DialogTitle>
        <DialogContent>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <Paper sx={{ p: 2, mb: 3, bgcolor: 'grey.100' }}>
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Typography variant="body2" color="textSecondary">
                  Employee
                </Typography>
                <Typography variant="body1" fontWeight="medium">
                  {loan.employee_name} ({loan.employee_code})
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="textSecondary">
                  Loan Code
                </Typography>
                <Typography variant="body1" fontWeight="medium">
                  {loan.loan_code}
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="textSecondary">
                  Loan Type
                </Typography>
                <Typography variant="body1">
                  {loan.loan_type.charAt(0).toUpperCase() + loan.loan_type.slice(1).replace('_', ' ')}
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="textSecondary">
                  Requested Amount
                </Typography>
                <Typography variant="h6" color="primary">
                  ₹{loan.loan_amount.toLocaleString()}
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="textSecondary">
                  Tenure
                </Typography>
                <Typography variant="body1">{loan.tenure_months} months</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="textSecondary">
                  Monthly EMI
                </Typography>
                <Typography variant="h6" color="secondary">
                  ₹{loan.emi_amount.toLocaleString()}
                </Typography>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="body2" color="textSecondary">
                  Purpose
                </Typography>
                <Typography variant="body1">{loan.purpose}</Typography>
              </Grid>
            </Grid>
          </Paper>

          {action === 'approve' && activeTab === 2 && (
            <TextField
              fullWidth
              label="Approved Amount (optional)"
              type="number"
              value={approvedAmount}
              onChange={(e) =>
                setDialogState({ ...dialogState, approvedAmount: parseFloat(e.target.value) })
              }
              helperText="Leave same as requested amount or modify if needed"
              sx={{ mb: 2 }}
            />
          )}

          <TextField
            fullWidth
            label={action === 'approve' ? 'Comments (optional)' : 'Rejection Reason *'}
            multiline
            rows={4}
            value={comments}
            onChange={(e) => setDialogState({ ...dialogState, comments: e.target.value })}
            required={action === 'reject'}
            error={action === 'reject' && !comments}
            helperText={
              action === 'reject' && !comments ? 'Rejection reason is required' : ''
            }
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog} disabled={processing}>
            Cancel
          </Button>
          <Button
            onClick={handleApproval}
            variant="contained"
            color={action === 'approve' ? 'success' : 'error'}
            disabled={processing || (action === 'reject' && !comments)}
            startIcon={processing ? <CircularProgress size={20} /> : null}
          >
            {action === 'approve' ? 'Approve' : 'Reject'}
          </Button>
        </DialogActions>
      </Dialog>
    );
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Loan Approval Dashboard
      </Typography>

      {successMessage && (
        <Alert severity="success" onClose={() => setSuccessMessage('')} sx={{ mb: 3 }}>
          {successMessage}
        </Alert>
      )}

      <Card>
        <CardContent>
          <Tabs
            value={activeTab}
            onChange={(e, newValue) => {
              setActiveTab(newValue);
              setPage(0);
            }}
            sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}
          >
            <Tab label="Manager Approval" />
            <Tab label="HR Approval" />
            <Tab label="Finance Approval" />
          </Tabs>

          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
              <CircularProgress />
            </Box>
          ) : loans.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 8 }}>
              <Typography variant="h6" color="textSecondary">
                No pending approvals
              </Typography>
              <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                All loan applications have been processed
              </Typography>
            </Box>
          ) : (
            <>
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Loan Code</TableCell>
                      <TableCell>Employee</TableCell>
                      <TableCell>Type</TableCell>
                      <TableCell align="right">Amount</TableCell>
                      <TableCell align="right">EMI</TableCell>
                      <TableCell>Tenure</TableCell>
                      <TableCell>Application Date</TableCell>
                      <TableCell align="center">Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {loans.map((loan) => (
                      <TableRow key={loan.id} hover>
                        <TableCell>{loan.loan_code}</TableCell>
                        <TableCell>
                          <Typography variant="body2" fontWeight="medium">
                            {loan.employee_name}
                          </Typography>
                          <Typography variant="caption" color="textSecondary">
                            {loan.employee_code}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          {loan.loan_type.charAt(0).toUpperCase() +
                            loan.loan_type.slice(1).replace('_', ' ')}
                        </TableCell>
                        <TableCell align="right">
                          ₹{loan.loan_amount.toLocaleString()}
                        </TableCell>
                        <TableCell align="right">
                          ₹{loan.emi_amount.toLocaleString()}
                        </TableCell>
                        <TableCell>{loan.tenure_months} months</TableCell>
                        <TableCell>
                          {format(new Date(loan.application_date), 'dd MMM yyyy')}
                        </TableCell>
                        <TableCell align="center">
                          <Tooltip title="View Details">
                            <IconButton
                              size="small"
                              onClick={() => navigate(`/hrms/loans/${loan.id}`)}
                            >
                              <ViewIcon />
                            </IconButton>
                          </Tooltip>

                          <Tooltip title="Approve">
                            <IconButton
                              size="small"
                              color="success"
                              onClick={() => handleOpenDialog(loan, 'approve')}
                            >
                              <ApproveIcon />
                            </IconButton>
                          </Tooltip>

                          <Tooltip title="Reject">
                            <IconButton
                              size="small"
                              color="error"
                              onClick={() => handleOpenDialog(loan, 'reject')}
                            >
                              <RejectIcon />
                            </IconButton>
                          </Tooltip>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>

              <TablePagination
                rowsPerPageOptions={[5, 10, 25, 50]}
                component="div"
                count={total}
                rowsPerPage={rowsPerPage}
                page={page}
                onPageChange={handleChangePage}
                onRowsPerPageChange={handleChangeRowsPerPage}
              />
            </>
          )}
        </CardContent>
      </Card>

      {renderApprovalDialog()}
    </Box>
  );
};

export default LoanApprovalDashboard;
