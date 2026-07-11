/**
 * Loan Application Form Component
 * Multi-step form for employees to apply for loans
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  FormControl,
  FormControlLabel,
  FormHelperText,
  Grid,
  InputLabel,
  MenuItem,
  Select,
  Step,
  StepLabel,
  Stepper,
  TextField,
  Typography,
  Alert,
  Checkbox,
  CircularProgress,
  Paper,
  Divider,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import loanService, {
  LoanType,
  LoanApplicationCreate,
  LoanEligibilityResponse,
} from '../../../services/hrms/loanService';

const steps = ['Loan Details', 'Eligibility Check', 'Bank & Guarantor', 'Review & Submit'];

const loanTypes = [
  { value: LoanType.PERSONAL, label: 'Personal Loan' },
  { value: LoanType.VEHICLE, label: 'Vehicle Loan' },
  { value: LoanType.HOME, label: 'Home Loan' },
  { value: LoanType.EDUCATION, label: 'Education Loan' },
  { value: LoanType.MEDICAL, label: 'Medical Loan' },
  { value: LoanType.MARRIAGE, label: 'Marriage Loan' },
  { value: LoanType.SALARY_ADVANCE, label: 'Salary Advance' },
  { value: LoanType.EMERGENCY, label: 'Emergency Loan' },
  { value: LoanType.FESTIVAL_ADVANCE, label: 'Festival Advance' },
  { value: LoanType.OTHER, label: 'Other' },
];

interface FormData extends LoanApplicationCreate {
  [key: string]: any;
}

const LoanApplicationForm: React.FC = () => {
  const navigate = useNavigate();
  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [checkingEligibility, setCheckingEligibility] = useState(false);
  const [eligibility, setEligibility] = useState<LoanEligibilityResponse | null>(null);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [submitError, setSubmitError] = useState<string>('');

  const [formData, setFormData] = useState<FormData>({
    loan_type: LoanType.PERSONAL,
    loan_amount: 0,
    tenure_months: 12,
    purpose: '',
    reason_for_loan: '',
    repayment_frequency: 'monthly',
    bank_name: '',
    bank_account_number: '',
    bank_ifsc_code: '',
    guarantor_name: '',
    guarantor_relation: '',
    guarantor_contact: '',
    attachment_urls: [],
  });

  const [emiDetails, setEmiDetails] = useState({
    emi_amount: 0,
    total_interest: 0,
    total_repayment_amount: 0,
  });

  // Handle input change
  const handleChange = (field: string, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    // Clear error for this field
    if (errors[field]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  // Calculate EMI whenever loan amount, interest rate, or tenure changes
  useEffect(() => {
    if (eligibility && formData.loan_amount > 0 && formData.tenure_months > 0) {
      const calculateEMI = async () => {
        try {
          const result = await loanService.calculateEMI({
            principal_amount: formData.loan_amount,
            interest_rate: eligibility.interest_rate,
            tenure_months: formData.tenure_months,
          });
          setEmiDetails(result);
        } catch (error) {
          console.error('Error calculating EMI:', error);
        }
      };
      calculateEMI();
    }
  }, [formData.loan_amount, formData.tenure_months, eligibility]);

  // Check eligibility
  const handleCheckEligibility = async () => {
    // Validate step 1
    const stepErrors: Record<string, string> = {};
    
    if (!formData.loan_type) {
      stepErrors.loan_type = 'Please select loan type';
    }
    if (formData.loan_amount <= 0) {
      stepErrors.loan_amount = 'Please enter valid loan amount';
    }
    if (formData.tenure_months <= 0) {
      stepErrors.tenure_months = 'Please enter valid tenure';
    }
    if (!formData.purpose || formData.purpose.length < 10) {
      stepErrors.purpose = 'Purpose must be at least 10 characters';
    }

    if (Object.keys(stepErrors).length > 0) {
      setErrors(stepErrors);
      return;
    }

    setCheckingEligibility(true);
    try {
      const result = await loanService.checkEligibility({
        loan_type: formData.loan_type,
        requested_amount: formData.loan_amount,
        tenure_months: formData.tenure_months,
      });
      setEligibility(result);
      
      if (result.is_eligible) {
        setActiveStep(2); // Move to next step
      }
    } catch (error: any) {
      setSubmitError(error.response?.data?.detail || 'Error checking eligibility');
    } finally {
      setCheckingEligibility(false);
    }
  };

  // Handle next
  const handleNext = () => {
    if (activeStep === 0) {
      handleCheckEligibility();
    } else if (activeStep === 2) {
      // Validate bank details
      const stepErrors: Record<string, string> = {};
      if (!formData.bank_name) {
        stepErrors.bank_name = 'Bank name is required';
      }
      if (!formData.bank_account_number) {
        stepErrors.bank_account_number = 'Account number is required';
      }
      if (!formData.bank_ifsc_code) {
        stepErrors.bank_ifsc_code = 'IFSC code is required';
      }

      if (Object.keys(stepErrors).length > 0) {
        setErrors(stepErrors);
        return;
      }

      setActiveStep((prev) => prev + 1);
    } else {
      setActiveStep((prev) => prev + 1);
    }
  };

  // Handle back
  const handleBack = () => {
    setActiveStep((prev) => prev - 1);
  };

  // Handle submit
  const handleSubmit = async () => {
    setLoading(true);
    setSubmitError('');
    
    try {
      const loan = await loanService.createApplication(formData);
      // Submit the application
      await loanService.submitApplication(loan.id);
      
      navigate('/hrms/loans/my-loans', {
        state: { message: 'Loan application submitted successfully!' },
      });
    } catch (error: any) {
      setSubmitError(error.response?.data?.detail || 'Error submitting application');
    } finally {
      setLoading(false);
    }
  };

  // Render step content
  const renderStepContent = (step: number) => {
    switch (step) {
      case 0:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth error={!!errors.loan_type}>
                <InputLabel>Loan Type *</InputLabel>
                <Select
                  value={formData.loan_type}
                  onChange={(e) => handleChange('loan_type', e.target.value)}
                  label="Loan Type *"
                >
                  {loanTypes.map((type) => (
                    <MenuItem key={type.value} value={type.value}>
                      {type.label}
                    </MenuItem>
                  ))}
                </Select>
                {errors.loan_type && <FormHelperText>{errors.loan_type}</FormHelperText>}
              </FormControl>
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Loan Amount *"
                type="number"
                value={formData.loan_amount || ''}
                onChange={(e) => handleChange('loan_amount', parseFloat(e.target.value) || 0)}
                error={!!errors.loan_amount}
                helperText={errors.loan_amount}
                InputProps={{ inputProps: { min: 0 } }}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Tenure (Months) *"
                type="number"
                value={formData.tenure_months || ''}
                onChange={(e) => handleChange('tenure_months', parseInt(e.target.value) || 0)}
                error={!!errors.tenure_months}
                helperText={errors.tenure_months || 'Maximum 60 months'}
                InputProps={{ inputProps: { min: 1, max: 360 } }}
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Purpose of Loan *"
                multiline
                rows={3}
                value={formData.purpose}
                onChange={(e) => handleChange('purpose', e.target.value)}
                error={!!errors.purpose}
                helperText={errors.purpose || 'Minimum 10 characters'}
                inputProps={{ maxLength: 500 }}
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Detailed Reason (Optional)"
                multiline
                rows={3}
                value={formData.reason_for_loan}
                onChange={(e) => handleChange('reason_for_loan', e.target.value)}
                helperText="Additional details about your loan requirement"
                inputProps={{ maxLength: 1000 }}
              />
            </Grid>
          </Grid>
        );

      case 1:
        return (
          <Box>
            {eligibility && (
              <>
                {eligibility.is_eligible ? (
                  <Alert severity="success" sx={{ mb: 3 }}>
                    <Typography variant="h6" gutterBottom>
                      Congratulations! You are eligible for this loan.
                    </Typography>
                  </Alert>
                ) : (
                  <Alert severity="error" sx={{ mb: 3 }}>
                    <Typography variant="h6" gutterBottom>
                      You are not eligible for this loan
                    </Typography>
                    <Typography variant="body2">
                      Reasons:
                      <ul>
                        {eligibility.reasons.map((reason, index) => (
                          <li key={index}>{reason}</li>
                        ))}
                      </ul>
                    </Typography>
                  </Alert>
                )}

                <Paper sx={{ p: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    Eligibility Details
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="textSecondary">
                        Eligible Amount
                      </Typography>
                      <Typography variant="h6">
                        ₹{eligibility.eligible_amount.toLocaleString()}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="textSecondary">
                        Maximum EMI
                      </Typography>
                      <Typography variant="h6">
                        ₹{eligibility.max_emi_amount.toLocaleString()}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="textSecondary">
                        Interest Rate
                      </Typography>
                      <Typography variant="h6">{eligibility.interest_rate}% p.a.</Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="textSecondary">
                        Suggested Tenure
                      </Typography>
                      <Typography variant="h6">
                        {eligibility.suggested_tenure_months} months
                      </Typography>
                    </Grid>
                  </Grid>

                  {emiDetails.emi_amount > 0 && (
                    <>
                      <Divider sx={{ my: 3 }} />
                      <Typography variant="h6" gutterBottom>
                        EMI Breakdown
                      </Typography>
                      <Grid container spacing={2}>
                        <Grid item xs={6}>
                          <Typography variant="body2" color="textSecondary">
                            Monthly EMI
                          </Typography>
                          <Typography variant="h6" color="primary">
                            ₹{emiDetails.emi_amount.toLocaleString()}
                          </Typography>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="body2" color="textSecondary">
                            Total Interest
                          </Typography>
                          <Typography variant="h6">
                            ₹{emiDetails.total_interest.toLocaleString()}
                          </Typography>
                        </Grid>
                        <Grid item xs={12}>
                          <Typography variant="body2" color="textSecondary">
                            Total Repayment Amount
                          </Typography>
                          <Typography variant="h5" color="secondary">
                            ₹{emiDetails.total_repayment_amount.toLocaleString()}
                          </Typography>
                        </Grid>
                      </Grid>
                    </>
                  )}
                </Paper>
              </>
            )}
          </Box>
        );

      case 2:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Bank Account Details
              </Typography>
              <Typography variant="body2" color="textSecondary" gutterBottom>
                Loan amount will be disbursed to this account
              </Typography>
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Bank Name *"
                value={formData.bank_name}
                onChange={(e) => handleChange('bank_name', e.target.value)}
                error={!!errors.bank_name}
                helperText={errors.bank_name}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Account Number *"
                value={formData.bank_account_number}
                onChange={(e) => handleChange('bank_account_number', e.target.value)}
                error={!!errors.bank_account_number}
                helperText={errors.bank_account_number}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="IFSC Code *"
                value={formData.bank_ifsc_code}
                onChange={(e) => handleChange('bank_ifsc_code', e.target.value.toUpperCase())}
                error={!!errors.bank_ifsc_code}
                helperText={errors.bank_ifsc_code}
                inputProps={{ maxLength: 11 }}
              />
            </Grid>

            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
              <Typography variant="h6" gutterBottom>
                Guarantor Details (Optional)
              </Typography>
            </Grid>

            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Guarantor Name"
                value={formData.guarantor_name}
                onChange={(e) => handleChange('guarantor_name', e.target.value)}
              />
            </Grid>

            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Relation"
                value={formData.guarantor_relation}
                onChange={(e) => handleChange('guarantor_relation', e.target.value)}
              />
            </Grid>

            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Contact Number"
                value={formData.guarantor_contact}
                onChange={(e) => handleChange('guarantor_contact', e.target.value)}
                inputProps={{ maxLength: 20 }}
              />
            </Grid>
          </Grid>
        );

      case 3:
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              Review Your Application
            </Typography>

            <Paper sx={{ p: 3, mb: 2 }}>
              <Typography variant="subtitle1" gutterBottom fontWeight="bold">
                Loan Details
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">
                    Loan Type
                  </Typography>
                  <Typography>
                    {loanTypes.find((t) => t.value === formData.loan_type)?.label}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">
                    Loan Amount
                  </Typography>
                  <Typography>₹{formData.loan_amount.toLocaleString()}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">
                    Tenure
                  </Typography>
                  <Typography>{formData.tenure_months} months</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">
                    Monthly EMI
                  </Typography>
                  <Typography color="primary" fontWeight="bold">
                    ₹{emiDetails.emi_amount.toLocaleString()}
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="body2" color="textSecondary">
                    Purpose
                  </Typography>
                  <Typography>{formData.purpose}</Typography>
                </Grid>
              </Grid>
            </Paper>

            <Paper sx={{ p: 3, mb: 2 }}>
              <Typography variant="subtitle1" gutterBottom fontWeight="bold">
                Bank Details
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <Typography variant="body2" color="textSecondary">
                    Bank Name
                  </Typography>
                  <Typography>{formData.bank_name}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">
                    Account Number
                  </Typography>
                  <Typography>{formData.bank_account_number}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">
                    IFSC Code
                  </Typography>
                  <Typography>{formData.bank_ifsc_code}</Typography>
                </Grid>
              </Grid>
            </Paper>

            {formData.guarantor_name && (
              <Paper sx={{ p: 3, mb: 2 }}>
                <Typography variant="subtitle1" gutterBottom fontWeight="bold">
                  Guarantor Details
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={4}>
                    <Typography variant="body2" color="textSecondary">
                      Name
                    </Typography>
                    <Typography>{formData.guarantor_name}</Typography>
                  </Grid>
                  <Grid item xs={4}>
                    <Typography variant="body2" color="textSecondary">
                      Relation
                    </Typography>
                    <Typography>{formData.guarantor_relation}</Typography>
                  </Grid>
                  <Grid item xs={4}>
                    <Typography variant="body2" color="textSecondary">
                      Contact
                    </Typography>
                    <Typography>{formData.guarantor_contact}</Typography>
                  </Grid>
                </Grid>
              </Paper>
            )}

            {submitError && (
              <Alert severity="error" sx={{ mt: 2 }}>
                {submitError}
              </Alert>
            )}
          </Box>
        );

      default:
        return null;
    }
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h5" gutterBottom>
          Apply for Loan
        </Typography>

        <Stepper activeStep={activeStep} sx={{ mt: 3, mb: 4 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        {submitError && activeStep !== 3 && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {submitError}
          </Alert>
        )}

        <Box sx={{ minHeight: 400 }}>{renderStepContent(activeStep)}</Box>

        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
          <Button
            disabled={activeStep === 0 || activeStep === 1}
            onClick={handleBack}
            variant="outlined"
          >
            Back
          </Button>

          <Box>
            <Button onClick={() => navigate('/hrms/loans/my-loans')} sx={{ mr: 2 }}>
              Cancel
            </Button>

            {activeStep === steps.length - 1 ? (
              <Button
                variant="contained"
                onClick={handleSubmit}
                disabled={loading || !eligibility?.is_eligible}
              >
                {loading ? <CircularProgress size={24} /> : 'Submit Application'}
              </Button>
            ) : activeStep === 1 ? (
              eligibility?.is_eligible && (
                <Button variant="contained" onClick={handleNext}>
                  Continue
                </Button>
              )
            ) : (
              <Button
                variant="contained"
                onClick={handleNext}
                disabled={checkingEligibility}
              >
                {checkingEligibility ? <CircularProgress size={24} /> : 'Next'}
              </Button>
            )}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

export default LoanApplicationForm;
