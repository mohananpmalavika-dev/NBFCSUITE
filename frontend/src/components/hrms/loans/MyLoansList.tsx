/**
 * My Loans List Component
 * Display employee's loan applications with status
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Grid,
  IconButton,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TablePagination,
  TableRow,
  Typography,
  Alert,
  CircularProgress,
  Tooltip,
} from '@mui/material';
import {
  Add as AddIcon,
  Visibility as ViewIcon,
  Cancel as CancelIcon,
  Schedule as ScheduleIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import loanService, { Loan, LoanStatus, EmployeeLoanSummary } from '../../../services/hrms/loanService';
import { format } from 'date-fns';

const statusColors: Record<LoanStatus, 'default' | 'primary' | 'secondary' | 'error' | 'warning' | 'info' | 'success'> = {
  [LoanStatus.DRAFT]: 'default',
  [LoanStatus.SUBMITTED]: 'info',
  [LoanStatus.PENDING_APPROVAL]: 'warning',
  [LoanStatus.APPROVED]: 'success',
  [LoanStatus.REJECTED]: 'error',
  [LoanStatus.DISBURSED]: 'primary',
  [LoanStatus.ACTIVE]: 'success',
  [LoanStatus.CLOSED]: 'default',
  [LoanStatus.CANCELLED]: 'error',
};

const statusLabels: Record<LoanStatus, string> = {
  [LoanStatus.DRAFT]: 'Draft',
  [LoanStatus.SUBMITTED]: 'Submitted',
  [LoanStatus.PENDING_APPROVAL]: 'Pending Approval',
  [LoanStatus.APPROVED]: 'Approved',
  [LoanStatus.REJECTED]: 'Rejected',
  [LoanStatus.DISBURSED]: 'Disbursed',
  [LoanStatus.ACTIVE]: 'Active',
  [LoanStatus.CLOSED]: 'Closed',
  [LoanStatus.CANCELLED]: 'Cancelled',
};

const MyLoansList: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [loans, setLoans] = useState<Loan[]>([]);
  const [summary, setSummary] = useState<EmployeeLoanSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [total, setTotal] = useState(0);
  const [successMessage, setSuccessMessage] = useState('');

  useEffect(() => {
    if (location.state?.message) {
      setSuccessMessage(location.state.message);
      // Clear the message from location state
      window.history.replaceState({}, document.title);
    }
  }, [location]);

  useEffect(() => {
    fetchLoans();
    fetchSummary();
  }, [page, rowsPerPage]);

  const fetchLoans = async () => {
    setLoading(true);
    try {
      const response = await loanService.getMyApplications({
        page: page + 1,
        page_size: rowsPerPage,
      });
      setLoans(response.items);
      setTotal(response.total);
    } catch (error) {
      console.error('Error fetching loans:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchSummary = async () => {
    try {
      const data = await loanService.getMySummary();
      setSummary(data);
    } catch (error) {
      console.error('Error fetching summary:', error);
    }
  };

  const handleViewDetails = (loanId: string) => {
    navigate(`/hrms/loans/${loanId}`);
  };

  const handleCancelLoan = async (loanId: string) => {
    if (window.confirm('Are you sure you want to cancel this loan application?')) {
      try {
        await loanService.cancelApplication(loanId);
        fetchLoans();
        setSuccessMessage('Loan application cancelled successfully');
      } catch (error) {
        console.error('Error cancelling loan:', error);
      }
    }
  };

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  return (
    <Box>
      {successMessage && (
        <Alert severity="success" onClose={() => setSuccessMessage('')} sx={{ mb: 3 }}>
          {successMessage}
        </Alert>
      )}

      {/* Summary Cards */}
      {summary && (
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Total Loans
                </Typography>
                <Typography variant="h4">{summary.total_loans}</Typography>
                <Typography variant="body2" color="textSecondary">
                  Active: {summary.active_loans} | Closed: {summary.closed_loans}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Total Outstanding
                </Typography>
                <Typography variant="h4" color="error">
                  ₹{summary.total_outstanding.toLocaleString()}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Total Paid: ₹{summary.total_paid.toLocaleString()}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Monthly EMI
                </Typography>
                <Typography variant="h4" color="primary">
                  ₹{summary.current_monthly_emi.toLocaleString()}
                </Typography>
                {summary.next_emi_date && (
                  <Typography variant="body2" color="textSecondary">
                    Next: {format(new Date(summary.next_emi_date), 'dd MMM yyyy')}
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ bgcolor: summary.overdue_emis > 0 ? 'error.light' : 'inherit' }}>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Overdue EMIs
                </Typography>
                <Typography variant="h4">{summary.overdue_emis}</Typography>
                {summary.overdue_amount > 0 && (
                  <Typography variant="body2" color="error">
                    Amount: ₹{summary.overdue_amount.toLocaleString()}
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Loans Table */}
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
            <Typography variant="h6">My Loan Applications</Typography>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => navigate('/hrms/loans/apply')}
            >
              Apply for Loan
            </Button>
          </Box>

          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
              <CircularProgress />
            </Box>
          ) : loans.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 8 }}>
              <Typography variant="h6" color="textSecondary" gutterBottom>
                No loan applications found
              </Typography>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => navigate('/hrms/loans/apply')}
                sx={{ mt: 2 }}
              >
                Apply for Your First Loan
              </Button>
            </Box>
          ) : (
            <>
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Loan Code</TableCell>
                      <TableCell>Type</TableCell>
                      <TableCell align="right">Amount</TableCell>
                      <TableCell align="right">EMI</TableCell>
                      <TableCell align="right">Outstanding</TableCell>
                      <TableCell>Application Date</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell align="center">Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {loans.map((loan) => (
                      <TableRow key={loan.id} hover>
                        <TableCell>{loan.loan_code}</TableCell>
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
                        <TableCell align="right">
                          {loan.total_outstanding > 0 ? (
                            <Typography
                              color={loan.is_overdue ? 'error' : 'inherit'}
                              fontWeight={loan.is_overdue ? 'bold' : 'normal'}
                            >
                              ₹{loan.total_outstanding.toLocaleString()}
                            </Typography>
                          ) : (
                            '-'
                          )}
                        </TableCell>
                        <TableCell>
                          {format(new Date(loan.application_date), 'dd MMM yyyy')}
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={statusLabels[loan.status]}
                            color={statusColors[loan.status]}
                            size="small"
                          />
                          {loan.is_overdue && (
                            <Chip
                              label={`${loan.days_overdue} days overdue`}
                              color="error"
                              size="small"
                              sx={{ ml: 1 }}
                            />
                          )}
                        </TableCell>
                        <TableCell align="center">
                          <Tooltip title="View Details">
                            <IconButton
                              size="small"
                              onClick={() => handleViewDetails(loan.id)}
                            >
                              <ViewIcon />
                            </IconButton>
                          </Tooltip>

                          {loan.status === LoanStatus.ACTIVE && (
                            <Tooltip title="View EMI Schedule">
                              <IconButton
                                size="small"
                                onClick={() => navigate(`/hrms/loans/${loan.id}/emi-schedule`)}
                              >
                                <ScheduleIcon />
                              </IconButton>
                            </Tooltip>
                          )}

                          {(loan.status === LoanStatus.DRAFT ||
                            loan.status === LoanStatus.PENDING_APPROVAL) && (
                            <Tooltip title="Cancel Application">
                              <IconButton
                                size="small"
                                color="error"
                                onClick={() => handleCancelLoan(loan.id)}
                              >
                                <CancelIcon />
                              </IconButton>
                            </Tooltip>
                          )}
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
    </Box>
  );
};

export default MyLoansList;
