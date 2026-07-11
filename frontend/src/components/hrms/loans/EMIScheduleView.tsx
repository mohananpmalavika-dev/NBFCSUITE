/**
 * EMI Schedule View Component
 * Display detailed EMI repayment schedule
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Chip,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  CircularProgress,
  Grid,
  Divider,
  LinearProgress,
} from '@mui/material';
import { useParams } from 'react-router-dom';
import loanService, { EMISchedule, EMIStatus } from '../../../services/hrms/loanService';
import { format } from 'date-fns';

const statusColors: Record<EMIStatus, 'default' | 'primary' | 'secondary' | 'error' | 'warning' | 'success'> = {
  [EMIStatus.PENDING]: 'warning',
  [EMIStatus.PAID]: 'success',
  [EMIStatus.OVERDUE]: 'error',
  [EMIStatus.PARTIALLY_PAID]: 'info',
  [EMIStatus.WAIVED]: 'default',
};

const EMIScheduleView: React.FC = () => {
  const { loanId } = useParams<{ loanId: string }>();
  const [schedule, setSchedule] = useState<EMISchedule | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (loanId) {
      fetchSchedule();
    }
  }, [loanId]);

  const fetchSchedule = async () => {
    setLoading(true);
    try {
      const data = await loanService.getEMISchedule(loanId!);
      setSchedule(data);
    } catch (error) {
      console.error('Error fetching EMI schedule:', error);
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

  if (!schedule) {
    return (
      <Typography variant="h6" color="textSecondary">
        EMI schedule not found
      </Typography>
    );
  }

  const completionPercentage = (schedule.paid_emis / schedule.total_emis) * 100;

  return (
    <Box>
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            EMI Repayment Schedule
          </Typography>
          <Typography variant="body2" color="textSecondary" gutterBottom>
            Loan Code: {schedule.loan_code}
          </Typography>

          <Grid container spacing={3} sx={{ mt: 2 }}>
            <Grid item xs={12} md={3}>
              <Paper sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="body2" color="textSecondary">
                  Total EMIs
                </Typography>
                <Typography variant="h4">{schedule.total_emis}</Typography>
              </Paper>
            </Grid>

            <Grid item xs={12} md={3}>
              <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'success.light' }}>
                <Typography variant="body2" color="textSecondary">
                  Paid EMIs
                </Typography>
                <Typography variant="h4">{schedule.paid_emis}</Typography>
              </Paper>
            </Grid>

            <Grid item xs={12} md={3}>
              <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'warning.light' }}>
                <Typography variant="body2" color="textSecondary">
                  Pending EMIs
                </Typography>
                <Typography variant="h4">{schedule.pending_emis}</Typography>
              </Paper>
            </Grid>

            <Grid item xs={12} md={3}>
              <Paper
                sx={{
                  p: 2,
                  textAlign: 'center',
                  bgcolor: schedule.overdue_emis > 0 ? 'error.light' : 'grey.200',
                }}
              >
                <Typography variant="body2" color="textSecondary">
                  Overdue EMIs
                </Typography>
                <Typography variant="h4" color={schedule.overdue_emis > 0 ? 'error' : 'inherit'}>
                  {schedule.overdue_emis}
                </Typography>
              </Paper>
            </Grid>
          </Grid>

          <Box sx={{ mt: 3 }}>
            <Typography variant="body2" gutterBottom>
              Repayment Progress
            </Typography>
            <LinearProgress
              variant="determinate"
              value={completionPercentage}
              sx={{ height: 10, borderRadius: 5 }}
            />
            <Typography variant="body2" color="textSecondary" align="right" sx={{ mt: 0.5 }}>
              {completionPercentage.toFixed(1)}% Complete
            </Typography>
          </Box>

          <Divider sx={{ my: 3 }} />

          <Grid container spacing={2}>
            <Grid item xs={4}>
              <Typography variant="body2" color="textSecondary">
                Total Principal
              </Typography>
              <Typography variant="h6">
                ₹{schedule.total_principal.toLocaleString()}
              </Typography>
            </Grid>

            <Grid item xs={4}>
              <Typography variant="body2" color="textSecondary">
                Total Interest
              </Typography>
              <Typography variant="h6">
                ₹{schedule.total_interest.toLocaleString()}
              </Typography>
            </Grid>

            <Grid item xs={4}>
              <Typography variant="body2" color="textSecondary">
                Total Repayment
              </Typography>
              <Typography variant="h6" color="primary">
                ₹{schedule.total_amount.toLocaleString()}
              </Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            EMI Schedule Details
          </Typography>

          <TableContainer component={Paper}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>EMI #</TableCell>
                  <TableCell>Due Date</TableCell>
                  <TableCell align="right">EMI Amount</TableCell>
                  <TableCell align="right">Principal</TableCell>
                  <TableCell align="right">Interest</TableCell>
                  <TableCell align="right">Opening Balance</TableCell>
                  <TableCell align="right">Closing Balance</TableCell>
                  <TableCell>Payment Date</TableCell>
                  <TableCell>Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {schedule.schedule.map((emi) => (
                  <TableRow
                    key={emi.emi_number}
                    sx={{
                      bgcolor: emi.is_overdue
                        ? 'error.lighter'
                        : emi.status === EMIStatus.PAID
                        ? 'success.lighter'
                        : 'inherit',
                    }}
                  >
                    <TableCell>{emi.emi_number}</TableCell>
                    <TableCell>{format(new Date(emi.emi_due_date), 'dd MMM yyyy')}</TableCell>
                    <TableCell align="right">
                      ₹{emi.emi_amount.toLocaleString()}
                    </TableCell>
                    <TableCell align="right">
                      ₹{emi.principal_component.toLocaleString()}
                    </TableCell>
                    <TableCell align="right">
                      ₹{emi.interest_component.toLocaleString()}
                    </TableCell>
                    <TableCell align="right">
                      ₹{emi.opening_balance.toLocaleString()}
                    </TableCell>
                    <TableCell align="right">
                      ₹{emi.closing_balance.toLocaleString()}
                    </TableCell>
                    <TableCell>
                      {emi.payment_date
                        ? format(new Date(emi.payment_date), 'dd MMM yyyy')
                        : '-'}
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={emi.status.toUpperCase()}
                        color={statusColors[emi.status]}
                        size="small"
                      />
                      {emi.is_overdue && (
                        <Typography variant="caption" color="error" display="block">
                          {emi.days_overdue} days overdue
                        </Typography>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    </Box>
  );
};

export default EMIScheduleView;
