/**
 * Reimbursement Claims Page
 * Submit and track expense reimbursement claims
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
  Divider
} from '@mui/material';
import {
  Add as AddIcon,
  ArrowBack as ArrowBackIcon,
  Send as SendIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import axios from 'axios';

const claimTypes = [
  { value: 'travel', label: 'Travel' },
  { value: 'medical', label: 'Medical' },
  { value: 'telephone', label: 'Telephone' },
  { value: 'internet', label: 'Internet' },
  { value: 'fuel', label: 'Fuel' },
  { value: 'food', label: 'Food' },
  { value: 'training', label: 'Training' },
  { value: 'other', label: 'Other' }
];

const Reimbursements: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [claims, setClaims] = useState<any[]>([]);
  const [openDialog, setOpenDialog] = useState(false);
  const [formData, setFormData] = useState({
    claim_title: '',
    reimbursement_type: '',
    claim_description: '',
    expense_date: null as Date | null,
    claim_amount: 0,
    bill_number: '',
    vendor_name: ''
  });

  useEffect(() => {
    fetchClaims();
  }, []);

  const fetchClaims = async () => {
    try {
      setLoading(false);
      const response = await axios.get('/api/hrms/ess/reimbursement/claims');
      setClaims(response.data.items);
    } catch (err) {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    try {
      const payload = {
        ...formData,
        expense_date: formData.expense_date?.toISOString().split('T')[0]
      };
      
      const response = await axios.post('/api/hrms/ess/reimbursement/claims', payload);
      await axios.post(`/api/hrms/ess/reimbursement/claims/${response.data.id}/submit`);
      
      setOpenDialog(false);
      setFormData({
        claim_title: '',
        reimbursement_type: '',
        claim_description: '',
        expense_date: null,
        claim_amount: 0,
        bill_number: '',
        vendor_name: ''
      });
      fetchClaims();
    } catch (err: any) {
      alert(err.response?.data?.message || 'Failed to submit claim');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved': case 'paid': return 'success';
      case 'rejected': return 'error';
      case 'pending_approval': return 'warning';
      default: return 'default';
    }
  };

  if (loading) {
    return <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px"><CircularProgress /></Box>;
  }

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box display="flex" alignItems="center" mb={3}>
          <IconButton onClick={() => navigate('/ess')} sx={{ mr: 2 }}>
            <ArrowBackIcon />
          </IconButton>
          <Box flex={1}>
            <Typography variant="h4" fontWeight={600}>Reimbursement Claims</Typography>
            <Typography variant="body2" color="text.secondary">Submit and track expense claims</Typography>
          </Box>
          <Button variant="contained" startIcon={<AddIcon />} onClick={() => setOpenDialog(true)}>
            New Claim
          </Button>
        </Box>

        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>Claim History</Typography>
            <Divider sx={{ mb: 2 }} />
            
            {claims.length > 0 ? (
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Claim Code</TableCell>
                      <TableCell>Title</TableCell>
                      <TableCell>Type</TableCell>
                      <TableCell>Expense Date</TableCell>
                      <TableCell align="right">Amount</TableCell>
                      <TableCell>Status</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {claims.map((claim) => (
                      <TableRow key={claim.id}>
                        <TableCell>{claim.claim_code}</TableCell>
                        <TableCell>{claim.claim_title}</TableCell>
                        <TableCell>{claim.reimbursement_type.toUpperCase()}</TableCell>
                        <TableCell>{new Date(claim.expense_date).toLocaleDateString()}</TableCell>
                        <TableCell align="right">₹{claim.claim_amount.toLocaleString()}</TableCell>
                        <TableCell>
                          <Chip label={claim.status.replace('_', ' ').toUpperCase()} size="small" color={getStatusColor(claim.status)} />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            ) : (
              <Typography variant="body2" color="text.secondary" textAlign="center" py={4}>
                No claims found
              </Typography>
            )}
          </CardContent>
        </Card>

        <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
          <DialogTitle>Submit Reimbursement Claim</DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12}>
                <TextField fullWidth label="Claim Title" value={formData.claim_title} onChange={(e) => setFormData({ ...formData, claim_title: e.target.value })} required />
              </Grid>
              <Grid item xs={6}>
                <TextField select fullWidth label="Claim Type" value={formData.reimbursement_type} onChange={(e) => setFormData({ ...formData, reimbursement_type: e.target.value })} required>
                  {claimTypes.map((type) => (
                    <MenuItem key={type.value} value={type.value}>{type.label}</MenuItem>
                  ))}
                </TextField>
              </Grid>
              <Grid item xs={6}>
                <DatePicker
                  label="Expense Date"
                  value={formData.expense_date}
                  onChange={(date) => setFormData({ ...formData, expense_date: date })}
                  slotProps={{ textField: { fullWidth: true, required: true } }}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField fullWidth type="number" label="Claim Amount" value={formData.claim_amount} onChange={(e) => setFormData({ ...formData, claim_amount: parseFloat(e.target.value) })} required />
              </Grid>
              <Grid item xs={6}>
                <TextField fullWidth label="Bill Number" value={formData.bill_number} onChange={(e) => setFormData({ ...formData, bill_number: e.target.value })} />
              </Grid>
              <Grid item xs={6}>
                <TextField fullWidth label="Vendor Name" value={formData.vendor_name} onChange={(e) => setFormData({ ...formData, vendor_name: e.target.value })} />
              </Grid>
              <Grid item xs={12}>
                <TextField fullWidth multiline rows={3} label="Description" value={formData.claim_description} onChange={(e) => setFormData({ ...formData, claim_description: e.target.value })} required helperText="Minimum 10 characters" />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
            <Button variant="contained" startIcon={<SendIcon />} onClick={handleSubmit} disabled={!formData.claim_title || !formData.reimbursement_type || formData.claim_description.length < 10}>
              Submit Claim
            </Button>
          </DialogActions>
        </Dialog>
      </Container>
    </LocalizationProvider>
  );
};

export default Reimbursements;
