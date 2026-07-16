/**
 * Decision Request Form Component
 * Form to submit new decision requests
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
  CircularProgress,
  Divider,
  MenuItem
} from '@mui/material';
import { Send as SendIcon, ArrowBack as BackIcon } from '@mui/icons-material';
import { useRouter } from 'next/navigation';
import {
  decisionEngineService,
  CreateDecisionRequest
} from '@/services/decisionEngine.service';

export default function DecisionRequestForm() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const [formData, setFormData] = useState<CreateDecisionRequest>({
    application_id: '',
    customer_id: '',
    product_id: '',
    loan_amount: 0,
    tenure_months: 12,
    purpose: '',
    applicant_data: {
      age: 30,
      monthly_income: 50000,
      monthly_obligations: 15000,
      employment_type: 'SALARIED',
      employment_duration: 24,
      employment_verified: true,
      credit_score: 750,
      total_accounts: 5,
      active_accounts: 3,
      total_outstanding: 100000,
      credit_utilization: 30,
      max_dpd_last_12m: 0,
      enquiries_last_6m: 2,
      state: 'Maharashtra',
      city: 'Mumbai',
      device_type: 'Mobile'
    }
  });

  const handleChange = (field: keyof CreateDecisionRequest, value: any) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value
    }));
  };

  const handleApplicantDataChange = (field: string, value: any) => {
    setFormData((prev) => ({
      ...prev,
      applicant_data: {
        ...prev.applicant_data,
        [field]: value
      }
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      setError(null);
      
      const result = await decisionEngineService.submitDecisionRequest(formData);
      
      setSuccess(true);
      setTimeout(() => {
        router.push(`/decision-engine/${result.id}`);
      }, 1500);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to submit decision request');
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    router.push('/decision-engine');
  };

  return (
    <Box>
      <Box display="flex" alignItems="center" mb={3}>
        <Button
          startIcon={<BackIcon />}
          onClick={handleBack}
          sx={{ mr: 2 }}
        >
          Back
        </Button>
        <Typography variant="h4" component="h1">
          New Decision Request
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 3 }}>
          Decision request submitted successfully! Redirecting to details...
        </Alert>
      )}

      <form onSubmit={handleSubmit}>
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Application Details
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  required
                  label="Application ID"
                  value={formData.application_id}
                  onChange={(e) => handleChange('application_id', e.target.value)}
                  helperText="Unique application identifier"
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  required
                  label="Customer ID"
                  value={formData.customer_id}
                  onChange={(e) => handleChange('customer_id', e.target.value)}
                  helperText="Unique customer identifier"
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  required
                  label="Product ID"
                  value={formData.product_id}
                  onChange={(e) => handleChange('product_id', e.target.value)}
                  helperText="Loan product identifier"
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Purpose"
                  value={formData.purpose}
                  onChange={(e) => handleChange('purpose', e.target.value)}
                  helperText="Loan purpose (optional)"
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  required
                  type="number"
                  label="Loan Amount"
                  value={formData.loan_amount}
                  onChange={(e) => handleChange('loan_amount', Number(e.target.value))}
                  InputProps={{
                    startAdornment: '₹'
                  }}
                  helperText="Requested loan amount"
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  required
                  type="number"
                  label="Tenure (Months)"
                  value={formData.tenure_months}
                  onChange={(e) => handleChange('tenure_months', Number(e.target.value))}
                  helperText="Loan tenure in months"
                />
              </Grid>
            </Grid>
          </CardContent>
        </Card>

        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Applicant Personal Information
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  required
                  type="number"
                  label="Age"
                  value={formData.applicant_data.age}
                  onChange={(e) => handleApplicantDataChange('age', Number(e.target.value))}
                />
              </Grid>

              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  select
                  label="Employment Type"
                  value={formData.applicant_data.employment_type}
                  onChange={(e) => handleApplicantDataChange('employment_type', e.target.value)}
                >
                  <MenuItem value="SALARIED">Salaried</MenuItem>
                  <MenuItem value="SELF_EMPLOYED">Self Employed</MenuItem>
                  <MenuItem value="BUSINESS">Business</MenuItem>
                  <MenuItem value="PROFESSIONAL">Professional</MenuItem>
                </TextField>
              </Grid>

              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  type="number"
                  label="Employment Duration (Months)"
                  value={formData.applicant_data.employment_duration}
                  onChange={(e) => handleApplicantDataChange('employment_duration', Number(e.target.value))}
                />
              </Grid>

              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  label="State"
                  value={formData.applicant_data.state}
                  onChange={(e) => handleApplicantDataChange('state', e.target.value)}
                />
              </Grid>

              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  label="City"
                  value={formData.applicant_data.city}
                  onChange={(e) => handleApplicantDataChange('city', e.target.value)}
                />
              </Grid>

              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  select
                  label="Device Type"
                  value={formData.applicant_data.device_type}
                  onChange={(e) => handleApplicantDataChange('device_type', e.target.value)}
                >
                  <MenuItem value="Mobile">Mobile</MenuItem>
                  <MenuItem value="Desktop">Desktop</MenuItem>
                  <MenuItem value="Tablet">Tablet</MenuItem>
                </TextField>
              </Grid>
            </Grid>
          </CardContent>
        </Card>

        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Financial Information
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  required
                  type="number"
                  label="Monthly Income"
                  value={formData.applicant_data.monthly_income}
                  onChange={(e) => handleApplicantDataChange('monthly_income', Number(e.target.value))}
                  InputProps={{
                    startAdornment: '₹'
                  }}
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  type="number"
                  label="Monthly Obligations (EMI)"
                  value={formData.applicant_data.monthly_obligations}
                  onChange={(e) => handleApplicantDataChange('monthly_obligations', Number(e.target.value))}
                  InputProps={{
                    startAdornment: '₹'
                  }}
                />
              </Grid>
            </Grid>
          </CardContent>
        </Card>

        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Credit Bureau Information (Optional)
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  type="number"
                  label="Credit Score"
                  value={formData.applicant_data.credit_score}
                  onChange={(e) => handleApplicantDataChange('credit_score', Number(e.target.value))}
                  helperText="300-900"
                />
              </Grid>

              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  type="number"
                  label="Total Accounts"
                  value={formData.applicant_data.total_accounts}
                  onChange={(e) => handleApplicantDataChange('total_accounts', Number(e.target.value))}
                />
              </Grid>

              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  type="number"
                  label="Active Accounts"
                  value={formData.applicant_data.active_accounts}
                  onChange={(e) => handleApplicantDataChange('active_accounts', Number(e.target.value))}
                />
              </Grid>

              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  type="number"
                  label="Total Outstanding"
                  value={formData.applicant_data.total_outstanding}
                  onChange={(e) => handleApplicantDataChange('total_outstanding', Number(e.target.value))}
                  InputProps={{
                    startAdornment: '₹'
                  }}
                />
              </Grid>

              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  type="number"
                  label="Credit Utilization (%)"
                  value={formData.applicant_data.credit_utilization}
                  onChange={(e) => handleApplicantDataChange('credit_utilization', Number(e.target.value))}
                  helperText="0-100"
                />
              </Grid>

              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  type="number"
                  label="Max DPD (Last 12M)"
                  value={formData.applicant_data.max_dpd_last_12m}
                  onChange={(e) => handleApplicantDataChange('max_dpd_last_12m', Number(e.target.value))}
                  helperText="Days past due"
                />
              </Grid>

              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  type="number"
                  label="Enquiries (Last 6M)"
                  value={formData.applicant_data.enquiries_last_6m}
                  onChange={(e) => handleApplicantDataChange('enquiries_last_6m', Number(e.target.value))}
                />
              </Grid>
            </Grid>
          </CardContent>
        </Card>

        <Box display="flex" justifyContent="flex-end" gap={2}>
          <Button
            variant="outlined"
            onClick={handleBack}
            disabled={loading}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            variant="contained"
            color="primary"
            startIcon={loading ? <CircularProgress size={20} /> : <SendIcon />}
            disabled={loading || success}
          >
            {loading ? 'Submitting...' : 'Submit Decision Request'}
          </Button>
        </Box>
      </form>
    </Box>
  );
}
