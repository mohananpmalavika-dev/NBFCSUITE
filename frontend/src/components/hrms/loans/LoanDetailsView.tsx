/**
 * Loan Details View Component
 * Comprehensive view of loan application with all details
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Divider,
  Grid,
  Paper,
  Typography,
  Alert,
  CircularProgress,
  Timeline,
  TimelineItem,
  TimelineSeparator,
  TimelineConnector,
  TimelineContent,
  TimelineDot,
  TimelineOppositeContent,
} from '@mui/material';
import {
  CheckCircle as ApprovedIcon,
  Cancel as RejectedIcon,
  HourglassEmpty as PendingIcon,
  AccountBalance as BankIcon,
  Person as PersonIcon,
  Description as DocumentIcon,
  Schedule as ScheduleIcon,
} from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import loanService, { Loan, LoanStatus } from '../../../services/hrms/loanService';
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

const LoanDetailsView: React.FC = () => {
  const { loanId } = useParams<{ loanId: string }>();
  const navigate = useNavigate();
  const [loan, setLoan] = useState<Loan | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (loanId) {
      fetchLoanDetails();
    }
  }, [loanId]);

  const fetchLoanDetails = async () => {
    setLoading(true);
    try {
      const data = await loanService.getApplication(loanId!);
      setLoan(data);
    } catch (error) {
      console.error('Error fetching loan details:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!loan) {
    return (
      <Alert severity="error">
        Loan not found
      </Alert>
    );
  }

  const getApprovalStatus = (status?: string) => {
    if (!status) return { icon: <PendingIcon />, color: 'default' as const, label: 'Pending' };
    if (status === 'approved') return { icon: <ApprovedIcon />, color: 'success' as const, label: 'Approved' };
    if (status === 'rejected') return { icon: <RejectedIcon />, color: 'error' as const, label: 'Rejected' };
    return { icon: <PendingIcon />, color: 'warning' as const, label: 'Pending' };
  };

  const renderApprovalTimeline = () => {
    const managerStatus = getApprovalStatus(loan.manager_approval_status);
    const hrStatus = getApprovalStatus(loan.hr_approval_status);
    const financeStatus = getApprovalStatus(loan.finance_approval_status);

    return (
      <Timeline>
        <TimelineItem>
          <TimelineOppositeContent color="textSecondary">
            {loan.submitted_date && format(new Date(loan.submitted_date), 'dd MMM yyyy, HH:mm')}
          </TimelineOppositeContent>
          <TimelineSeparator>
            <TimelineDot color="primary">
              <DocumentIcon />
            </TimelineDot>
            <TimelineConnector />
          </TimelineSeparator>
          <TimelineContent>
            <Typography variant="h6">Application Submitted</Typography>
            <Typography variant="body2" color="textSecondary">
              By {loan.employee_name}
            </Typography>
          </TimelineContent>
        </TimelineItem>

        <TimelineItem>
          <TimelineOppositeContent color="textSecondary">
            {loan.manager_approval_date && format(new Date(loan.manager_approval_date), 'dd MMM yyyy, HH:mm')}
          </TimelineOppositeContent>
          <TimelineSeparator>
            <TimelineDot color={managerStatus.color}>
              {managerStatus.icon}
            </TimelineDot>
            <TimelineConnector />
          </TimelineSeparator>
          <TimelineContent>
            <Typography variant="h6">Manager Approval</Typography>
            <Chip label={managerStatus.label} color={managerStatus.color} size="small" />
            {loan.manager_comments && (
              <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                Comments: {loan.manager_comments}
              </Typography>
            )}
          </TimelineContent>
        </TimelineItem>

        <TimelineItem>
          <TimelineOppositeContent color="textSecondary">
            {loan.hr_approval_date && format(new Date(loan.hr_approval_date), 'dd MMM yyyy, HH:mm')}
          </TimelineOppositeContent>
          <TimelineSeparator>
            <TimelineDot color={hrStatus.color}>
              {hrStatus.icon}
            </TimelineDot>
            <TimelineConnector />
          </TimelineSeparator>
          <TimelineContent>
            <Typography variant="h6">HR Approval</Typography>
            <Chip label={hrStatus.label} color={hrStatus.color} size="small" />
            {loan.hr_comments && (
              <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                Comments: {loan.hr_comments}
              </Typography>
            )}
          </TimelineContent>
        </TimelineItem>

        <TimelineItem>
          <TimelineOppositeContent color="textSecondary">
            {loan.finance_approval_date && format(new Date(loan.finance_approval_date), 'dd MMM yyyy, HH:mm')}
          </TimelineOppositeContent>
          <TimelineSeparator>
            <TimelineDot color={financeStatus.color}>
              {financeStatus.icon}
            </TimelineDot>
            {loan.status === LoanStatus.ACTIVE && <TimelineConnector />}
          </TimelineSeparator>
          <TimelineContent>
            <Typography variant="h6">Finance Approval</Typography>
            <Chip label={financeStatus.label} color={financeStatus.color} size="small" />
            {loan.finance_comments && (
              <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                Comments: {loan.finance_comments}
              </Typography>
            )}
          </TimelineContent>
        </TimelineItem>

        {loan.disbursement_date && (
          <TimelineItem>
            <TimelineOppositeContent color="textSecondary">
              {format(new Date(loan.disbursement_date), 'dd MMM yyyy')}
            </TimelineOppositeContent>
            <TimelineSeparator>
              <TimelineDot color="success">
                <BankIcon />
              </TimelineDot>
            </TimelineSeparator>
            <TimelineContent>
              <Typography variant="h6">Loan Disbursed</Typography>
              <Typography variant="body2" color="textSecondary">
                Amount: ₹{loan.disbursed_amount?.toLocaleString()}
              </Typography>
            </TimelineContent>
          </TimelineItem>
        )}
      </Timeline>
    );
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Box>
          <Typography variant="h5" gutterBottom>
            Loan Details
          </Typography>
          <Typography variant="body2" color="textSecondary">
            Loan Code: {loan.loan_code}
          </Typography>
        </Box>
        <Chip
          label={loan.status.replace('_', ' ').toUpperCase()}
          color={statusColors[loan.status]}
          size="medium"
        />
      </Box>

      {loan.rejected_date && loan.rejection_reason && (
        <Alert severity="error" sx={{ mb: 3 }}>
          <Typography variant="subtitle2" gutterBottom>
            Loan Rejected
          </Typography>
          <Typography variant="body2">
            Reason: {loan.rejection_reason}
          </Typography>
        </Alert>
      )}

      {loan.is_overdue && (
        <Alert severity="error" sx={{ mb: 3 }}>
          <Typography variant="subtitle2">
            {loan.days_overdue} days overdue! Please pay your EMI immediately.
          </Typography>
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Loan Information */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Loan Information
              </Typography>
              <Divider sx={{ mb: 2 }} />

              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">
                    Loan Type
                  </Typography>
                  <Typography variant="body1" fontWeight="medium">
                    {loan.loan_type.charAt(0).toUpperCase() + loan.loan_type.slice(1).replace('_', ' ')}
                  </Typography>
                </Grid>

                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">
                    Application Date
                  </Typography>
                  <Typography variant="body1" fontWeight="medium">
                    {format(new Date(loan.application_date), 'dd MMM yyyy')}
                  </Typography>
                </Grid>

                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">
                    Loan Amount
                  </Typography>
                  <Typography variant="h6" color="primary">
                    ₹{loan.loan_amount.toLocaleString()}
                  </Typography>
                </Grid>

                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">
                    Interest Rate
                  </Typography>
                  <Typography variant="h6">
                    {loan.interest_rate}% p.a.
                  </Typography>
                </Grid>

                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">
                    Tenure
                  </Typography>
                  <Typography variant="body1" fontWeight="medium">
                    {loan.tenure_months} months
                  </Typography>
                </Grid>

                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">
                    Monthly EMI
                  </Typography>
                  <Typography variant="h6" color="secondary">
                    ₹{loan.emi_amount.toLocaleString()}
                  </Typography>
                </Grid>

                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">
                    Total Interest
                  </Typography>
                  <Typography variant="body1">
                    ₹{loan.total_interest.toLocaleString()}
                  </Typography>
                </Grid>

                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">
                    Total Repayment
                  </Typography>
                  <Typography variant="body1" fontWeight="bold">
                    ₹{loan.total_repayment_amount.toLocaleString()}
                  </Typography>
                </Grid>

                <Grid item xs={12}>
                  <Typography variant="body2" color="textSecondary">
                    Purpose
                  </Typography>
                  <Typography variant="body1">
                    {loan.purpose}
                  </Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Outstanding & Payment Status */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Outstanding & Payments
              </Typography>
              <Divider sx={{ mb: 2 }} />

              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Paper sx={{ p: 2, bgcolor: 'error.light' }}>
                    <Typography variant="body2" color="textSecondary">
                      Principal Outstanding
                    </Typography>
                    <Typography variant="h6">
                      ₹{loan.principal_outstanding.toLocaleString()}
                    </Typography>
                  </Paper>
                </Grid>

                <Grid item xs={6}>
                  <Paper sx={{ p: 2, bgcolor: 'warning.light' }}>
                    <Typography variant="body2" color="textSecondary">
                      Interest Outstanding
                    </Typography>
                    <Typography variant="h6">
                      ₹{loan.interest_outstanding.toLocaleString()}
                    </Typography>
                  </Paper>
                </Grid>

                <Grid item xs={12}>
                  <Paper sx={{ p: 2, bgcolor: 'primary.light' }}>
                    <Typography variant="body2" color="white">
                      Total Outstanding
                    </Typography>
                    <Typography variant="h5" color="white" fontWeight="bold">
                      ₹{loan.total_outstanding.toLocaleString()}
                    </Typography>
                  </Paper>
                </Grid>

                <Grid item xs={6}>
                  <Paper sx={{ p: 2, bgcolor: 'success.light' }}>
                    <Typography variant="body2" color="textSecondary">
                      Principal Paid
                    </Typography>
                    <Typography variant="h6">
                      ₹{loan.principal_paid.toLocaleString()}
                    </Typography>
                  </Paper>
                </Grid>

                <Grid item xs={6}>
                  <Paper sx={{ p: 2, bgcolor: 'success.light' }}>
                    <Typography variant="body2" color="textSecondary">
                      Total Paid
                    </Typography>
                    <Typography variant="h6">
                      ₹{loan.total_paid.toLocaleString()}
                    </Typography>
                  </Paper>
                </Grid>

                {loan.first_emi_date && (
                  <Grid item xs={6}>
                    <Typography variant="body2" color="textSecondary">
                      First EMI Date
                    </Typography>
                    <Typography variant="body1">
                      {format(new Date(loan.first_emi_date), 'dd MMM yyyy')}
                    </Typography>
                  </Grid>
                )}

                {loan.last_emi_date && (
                  <Grid item xs={6}>
                    <Typography variant="body2" color="textSecondary">
                      Last EMI Date
                    </Typography>
                    <Typography variant="body1">
                      {format(new Date(loan.last_emi_date), 'dd MMM yyyy')}
                    </Typography>
                  </Grid>
                )}
              </Grid>

              {loan.status === LoanStatus.ACTIVE && (
                <Button
                  fullWidth
                  variant="contained"
                  startIcon={<ScheduleIcon />}
                  onClick={() => navigate(`/hrms/loans/${loan.id}/emi-schedule`)}
                  sx={{ mt: 2 }}
                >
                  View EMI Schedule
                </Button>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Bank Details */}
        {loan.bank_name && (
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  <BankIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                  Bank Details
                </Typography>
                <Divider sx={{ mb: 2 }} />

                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <Typography variant="body2" color="textSecondary">
                      Bank Name
                    </Typography>
                    <Typography variant="body1" fontWeight="medium">
                      {loan.bank_name}
                    </Typography>
                  </Grid>

                  <Grid item xs={6}>
                    <Typography variant="body2" color="textSecondary">
                      Account Number
                    </Typography>
                    <Typography variant="body1">
                      {loan.bank_account_number}
                    </Typography>
                  </Grid>

                  <Grid item xs={6}>
                    <Typography variant="body2" color="textSecondary">
                      IFSC Code
                    </Typography>
                    <Typography variant="body1">
                      {loan.bank_ifsc_code}
                    </Typography>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* Approval Workflow */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Approval Workflow
              </Typography>
              <Divider sx={{ mb: 2 }} />

              {renderApprovalTimeline()}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Box sx={{ mt: 3, display: 'flex', justifyContent: 'space-between' }}>
        <Button variant="outlined" onClick={() => navigate('/hrms/loans/my-loans')}>
          Back to My Loans
        </Button>

        {loan.status === LoanStatus.ACTIVE && (
          <Button
            variant="contained"
            color="primary"
            startIcon={<ScheduleIcon />}
            onClick={() => navigate(`/hrms/loans/${loan.id}/emi-schedule`)}
          >
            View EMI Schedule
          </Button>
        )}
      </Box>
    </Box>
  );
};

export default LoanDetailsView;
