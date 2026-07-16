/**
 * Auto-Approval Criteria Step
 * Configure automatic approval thresholds
 */
import React from 'react';
import {
  Box,
  Grid,
  TextField,
  Typography,
  Card,
  CardContent,
  FormControlLabel,
  Switch,
  InputAdornment
} from '@mui/material';

interface AutoApprovalStepProps {
  data: any;
  onChange: (data: any) => void;
}

const AutoApprovalStep: React.FC<AutoApprovalStepProps> = ({ data, onChange }) => {
  const handleChange = (field: string) => (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const value = event.target.type === 'checkbox' 
      ? event.target.checked
      : event.target.type === 'number'
      ? parseFloat(event.target.value)
      : event.target.value;
    
    onChange({
      ...data,
      [field]: value
    });
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Auto-Approval Criteria
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Set thresholds for automatic loan approval
      </Typography>

      <Grid container spacing={3}>
        {/* Credit Score Criteria */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="subtitle1" gutterBottom fontWeight="bold">
                Credit Score Requirements
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    type="number"
                    label="Minimum Credit Score"
                    value={data.min_credit_score || ''}
                    onChange={handleChange('min_credit_score')}
                    InputProps={{
                      inputProps: { min: 300, max: 900 }
                    }}
                    helperText="e.g., 700"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Credit Score Source"
                    value={data.credit_score_source || ''}
                    onChange={handleChange('credit_score_source')}
                    placeholder="e.g., CIBIL, EXPERIAN"
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Income Criteria */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="subtitle1" gutterBottom fontWeight="bold">
                Income Requirements
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    type="number"
                    label="Minimum Monthly Income"
                    value={data.min_monthly_income || ''}
                    onChange={handleChange('min_monthly_income')}
                    InputProps={{
                      startAdornment: <InputAdornment position="start">₹</InputAdornment>
                    }}
                    helperText="e.g., 50000"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    type="number"
                    label="Maximum DTI Ratio"
                    value={data.max_dti_ratio || ''}
                    onChange={handleChange('max_dti_ratio')}
                    InputProps={{
                      endAdornment: <InputAdornment position="end">%</InputAdornment>
                    }}
                    helperText="e.g., 40"
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Loan Limits */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="subtitle1" gutterBottom fontWeight="bold">
                Loan Limits
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    type="number"
                    label="Maximum Loan Amount"
                    value={data.max_loan_amount || ''}
                    onChange={handleChange('max_loan_amount')}
                    InputProps={{
                      startAdornment: <InputAdornment position="start">₹</InputAdornment>
                    }}
                    helperText="e.g., 1000000"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    type="number"
                    label="Maximum LTV Ratio"
                    value={data.max_ltv_ratio || ''}
                    onChange={handleChange('max_ltv_ratio')}
                    InputProps={{
                      endAdornment: <InputAdornment position="end">%</InputAdornment>
                    }}
                    helperText="e.g., 80"
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Bureau Checks */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="subtitle1" gutterBottom fontWeight="bold">
                Bureau Requirements
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} md={4}>
                  <TextField
                    fullWidth
                    type="number"
                    label="Max Active Loans"
                    value={data.max_active_loans || ''}
                    onChange={handleChange('max_active_loans')}
                    helperText="e.g., 3"
                  />
                </Grid>
                <Grid item xs={12} md={4}>
                  <TextField
                    fullWidth
                    type="number"
                    label="Max DPD Days (Last 12 months)"
                    value={data.max_dpd_days || ''}
                    onChange={handleChange('max_dpd_days')}
                    helperText="e.g., 0"
                  />
                </Grid>
                <Grid item xs={12} md={4}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={data.allow_restructured_accounts || false}
                        onChange={handleChange('allow_restructured_accounts')}
                      />
                    }
                    label="Allow Restructured Accounts"
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Additional Checks */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="subtitle1" gutterBottom fontWeight="bold">
                Additional Checks
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} md={4}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={data.require_bank_statement_analysis || false}
                        onChange={handleChange('require_bank_statement_analysis')}
                      />
                    }
                    label="Require Bank Statement Analysis"
                  />
                </Grid>
                <Grid item xs={12} md={4}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={data.require_dedupe_check || false}
                        onChange={handleChange('require_dedupe_check')}
                      />
                    }
                    label="Require Dedupe Check"
                  />
                </Grid>
                <Grid item xs={12} md={4}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={data.require_fraud_check || false}
                        onChange={handleChange('require_fraud_check')}
                      />
                    }
                    label="Require Fraud Check"
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default AutoApprovalStep;
