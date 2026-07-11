/**
 * Payslips Page
 * View and download employee payslips
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
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Alert,
  CircularProgress,
  Chip,
  Divider
} from '@mui/material';
import {
  Download as DownloadIcon,
  Visibility as VisibilityIcon,
  ArrowBack as ArrowBackIcon,
  Receipt as ReceiptIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

interface Payslip {
  id: string;
  payslip_number: string;
  employee_code: string;
  employee_name: string;
  department_name: string;
  designation_name: string;
  month: number;
  year: number;
  days_in_month: number;
  days_worked: number;
  basic_salary: number;
  gross_earnings: number;
  total_deductions: number;
  net_salary: number;
  generated_date: string;
}

const Payslips: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [payslips, setPayslips] = useState<Payslip[]>([]);
  const [selectedPayslip, setSelectedPayslip] = useState<Payslip | null>(null);

  useEffect(() => {
    fetchPayslips();
  }, []);

  const fetchPayslips = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/hrms/ess/payslips');
      setPayslips(response.data);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to load payslips');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (payslipId: string) => {
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
  };

  const getMonthName = (month: number): string => {
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    return months[month - 1];
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box display="flex" alignItems="center" mb={3}>
        <IconButton onClick={() => navigate('/ess')} sx={{ mr: 2 }}>
          <ArrowBackIcon />
        </IconButton>
        <Box flex={1}>
          <Typography variant="h4" fontWeight={600}>
            My Payslips
          </Typography>
          <Typography variant="body2" color="text.secondary">
            View and download your salary slips
          </Typography>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Payslips List */}
        <Grid item xs={12} md={selectedPayslip ? 6 : 12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Payslip History
              </Typography>
              <Divider sx={{ mb: 2 }} />
              
              {payslips.length > 0 ? (
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Period</TableCell>
                        <TableCell align="right">Gross</TableCell>
                        <TableCell align="right">Deductions</TableCell>
                        <TableCell align="right">Net Salary</TableCell>
                        <TableCell align="center">Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {payslips.map((payslip) => (
                        <TableRow 
                          key={payslip.id}
                          hover
                          selected={selectedPayslip?.id === payslip.id}
                          onClick={() => setSelectedPayslip(payslip)}
                          sx={{ cursor: 'pointer' }}
                        >
                          <TableCell>
                            <Box display="flex" alignItems="center" gap={1}>
                              <ReceiptIcon fontSize="small" color="primary" />
                              <Typography variant="body2" fontWeight={600}>
                                {getMonthName(payslip.month)} {payslip.year}
                              </Typography>
                            </Box>
                          </TableCell>
                          <TableCell align="right">
                            ₹{payslip.gross_earnings.toLocaleString()}
                          </TableCell>
                          <TableCell align="right">
                            ₹{payslip.total_deductions.toLocaleString()}
                          </TableCell>
                          <TableCell align="right">
                            <Typography variant="body2" fontWeight={700} color="success.main">
                              ₹{payslip.net_salary.toLocaleString()}
                            </Typography>
                          </TableCell>
                          <TableCell align="center">
                            <IconButton 
                              size="small" 
                              color="primary"
                              onClick={(e) => {
                                e.stopPropagation();
                                handleDownload(payslip.id);
                              }}
                            >
                              <DownloadIcon fontSize="small" />
                            </IconButton>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              ) : (
                <Typography variant="body2" color="text.secondary" textAlign="center" py={4}>
                  No payslips available
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Payslip Details */}
        {selectedPayslip && (
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                  <Typography variant="h6">
                    Payslip Details
                  </Typography>
                  <Button
                    variant="contained"
                    startIcon={<DownloadIcon />}
                    onClick={() => handleDownload(selectedPayslip.id)}
                  >
                    Download PDF
                  </Button>
                </Box>
                <Divider sx={{ mb: 2 }} />

                {/* Employee Info */}
                <Paper sx={{ p: 2, mb: 2, bgcolor: 'grey.50' }}>
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary">
                        Employee Code
                      </Typography>
                      <Typography variant="body2" fontWeight={600}>
                        {selectedPayslip.employee_code}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary">
                        Period
                      </Typography>
                      <Typography variant="body2" fontWeight={600}>
                        {getMonthName(selectedPayslip.month)} {selectedPayslip.year}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary">
                        Department
                      </Typography>
                      <Typography variant="body2" fontWeight={600}>
                        {selectedPayslip.department_name}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary">
                        Designation
                      </Typography>
                      <Typography variant="body2" fontWeight={600}>
                        {selectedPayslip.designation_name}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary">
                        Days Worked
                      </Typography>
                      <Typography variant="body2" fontWeight={600}>
                        {selectedPayslip.days_worked} / {selectedPayslip.days_in_month}
                      </Typography>
                    </Grid>
                  </Grid>
                </Paper>

                {/* Salary Summary */}
                <Box mb={2}>
                  <Typography variant="subtitle2" gutterBottom>
                    Salary Summary
                  </Typography>
                  <Box sx={{ bgcolor: 'grey.50', p: 2, borderRadius: 1 }}>
                    <Box display="flex" justifyContent="space-between" mb={1}>
                      <Typography variant="body2" color="text.secondary">
                        Basic Salary
                      </Typography>
                      <Typography variant="body2" fontWeight={600}>
                        ₹{selectedPayslip.basic_salary.toLocaleString()}
                      </Typography>
                    </Box>
                    <Box display="flex" justifyContent="space-between" mb={1}>
                      <Typography variant="body2" color="text.secondary">
                        Gross Earnings
                      </Typography>
                      <Typography variant="body2" fontWeight={600}>
                        ₹{selectedPayslip.gross_earnings.toLocaleString()}
                      </Typography>
                    </Box>
                    <Box display="flex" justifyContent="space-between" mb={1}>
                      <Typography variant="body2" color="error">
                        Total Deductions
                      </Typography>
                      <Typography variant="body2" fontWeight={600} color="error">
                        - ₹{selectedPayslip.total_deductions.toLocaleString()}
                      </Typography>
                    </Box>
                    <Divider sx={{ my: 1 }} />
                    <Box display="flex" justifyContent="space-between">
                      <Typography variant="body1" fontWeight={700}>
                        Net Salary
                      </Typography>
                      <Typography variant="body1" fontWeight={700} color="success.main">
                        ₹{selectedPayslip.net_salary.toLocaleString()}
                      </Typography>
                    </Box>
                  </Box>
                </Box>

                <Alert severity="info" sx={{ mt: 2 }}>
                  Download the PDF for detailed breakdown of earnings and deductions
                </Alert>
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>
    </Container>
  );
};

export default Payslips;
