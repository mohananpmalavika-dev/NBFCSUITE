import React, { useState, useEffect } from 'react';
import {
  Box,
  Stepper,
  Step,
  StepLabel,
  Button,
  Typography,
  Paper,
  Grid,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Switch,
  Chip,
  IconButton,
  Alert,
  Divider,
  InputAdornment,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  ExpandMore as ExpandMoreIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
} from '@mui/icons-material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { eligibilityService } from '../../services/eligibilityService';

const steps = [
  'Basic Information',
  'Customer Eligibility',
  'Financial Eligibility',
  'Geographic Eligibility',
  'Review & Save',
];

const employmentTypes = ['SALARIED', 'SELF_EMPLOYED', 'BUSINESS', 'PROFESSIONAL', 'PENSIONER'];
const residencyStatuses = ['RESIDENT', 'NRI', 'PIO', 'FOREIGN_NATIONAL'];
const verificationMethods = ['SALARY_SLIP', 'BANK_STATEMENT', 'ITR', 'FORM_16', 'FINANCIALS', 'GST_RETURNS'];

interface EligibilityRuleBuilderProps {
  ruleId?: string;
  onSave?: (rule: any) => void;
  onCancel?: () => void;
}

const EligibilityRuleBuilder: React.FC<EligibilityRuleBuilderProps> = ({ ruleId, onSave, onCancel }) => {
  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const [rule, setRule] = useState<any>({
    rule_code: '',
    rule_name: '',
    description: '',
    status: 'DRAFT',
    product_id: '',
    product_code: '',
    apply_to_all_products: false,
    priority: 10,
    effective_date: new Date().toISOString().split('T')[0],
    allow_manual_override: true,
    override_approval_required: true,
    override_reason_mandatory: true,
    customer_eligibility: {
      age_criteria: { min_age: 21, max_age: 60 },
      income_criteria: { min_monthly_income: 25000, verification_methods: ['SALARY_SLIP'], require_proof: true },
      employment_types: ['SALARIED'],
      credit_score_criteria: { min_credit_score: 650, mandatory: true, allow_no_history: false },
      existing_customer_required: false,
      negative_areas_check: true,
      allowed_nationalities: ['IN'],
      allowed_residency_status: ['RESIDENT'],
      co_applicant_rules: { required: false, min_count: 0, max_count: 2 },
      guarantor_rules: { required: false, min_count: 0, max_count: 2 },
      dedup_check: true,
      blacklist_check: true,
      politically_exposed_person_check: true,
    },
    financial_eligibility: {
      foir_criteria: { max_foir_percentage: 50, include_proposed_emi: true },
      dti_criteria: { max_dti_percentage: 40, include_all_obligations: true },
      existing_obligations: { max_existing_loans: 3, max_existing_emi: 50000, check_credit_card_dues: true },
      banking_turnover: { required: false, min_monthly_turnover: 50000, months_to_consider: 6 },
      itr_criteria: { required: false, min_years: 2 },
      min_net_worth: null,
      min_liquid_assets: null,
      debt_free_required: false,
    },
    geographic_eligibility: {
      pin_code_restriction: null,
      state_restriction: null,
      city_restriction: null,
      branch_availability: { enabled: false, branch_codes: [] },
      serviceable_locations_only: true,
      check_negative_areas: true,
      allow_rural_areas: true,
      allow_semi_urban_areas: true,
      allow_urban_areas: true,
      allow_metro_areas: true,
    },
  });

  useEffect(() => {
    if (ruleId) {
      loadRule();
    }
  }, [ruleId]);

  const loadRule = async () => {
    try {
      setLoading(true);
      const data = await eligibilityService.getRule(ruleId!);
      setRule(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load rule');
    } finally {
      setLoading(false);
    }
  };

  const handleNext = () => setActiveStep((prev) => prev + 1);
  const handleBack = () => setActiveStep((prev) => prev - 1);

  const handleSave = async () => {
    try {
      setLoading(true);
      setError(null);
      
      let savedRule;
      if (ruleId) {
        savedRule = await eligibilityService.updateRule(ruleId, rule);
        setSuccess('Rule updated successfully');
      } else {
        savedRule = await eligibilityService.createRule(rule);
        setSuccess('Rule created successfully');
      }
      
      if (onSave) {
        onSave(savedRule);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to save rule');
    } finally {
      setLoading(false);
    }
  };

  const updateRule = (field: string, value: any) => {
    setRule((prev: any) => ({ ...prev, [field]: value }));
  };

  const updateNested = (section: string, field: string, value: any) => {
    setRule((prev: any) => ({
      ...prev,
      [section]: { ...prev[section], [field]: value },
    }));
  };

  const updateDeepNested = (section: string, subsection: string, field: string, value: any) => {
    setRule((prev: any) => ({
      ...prev,
      [section]: {
        ...prev[section],
        [subsection]: { ...prev[section][subsection], [field]: value },
      },
    }));
  };

  const renderBasicInformation = () => (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Typography variant="h6" gutterBottom>Basic Rule Information</Typography>
      </Grid>
      
      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          label="Rule Code"
          value={rule.rule_code}
          onChange={(e) => updateRule('rule_code', e.target.value)}
          required
          helperText="Unique identifier for the rule"
        />
      </Grid>
      
      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          label="Rule Name"
          value={rule.rule_name}
          onChange={(e) => updateRule('rule_name', e.target.value)}
          required
        />
      </Grid>
      
      <Grid item xs={12}>
        <TextField
          fullWidth
          multiline
          rows={3}
          label="Description"
          value={rule.description}
          onChange={(e) => updateRule('description', e.target.value)}
        />
      </Grid>
      
      <Grid item xs={12} md={6}>
        <FormControl fullWidth>
          <InputLabel>Status</InputLabel>
          <Select
            value={rule.status}
            onChange={(e) => updateRule('status', e.target.value)}
            label="Status"
          >
            <MenuItem value="DRAFT">Draft</MenuItem>
            <MenuItem value="ACTIVE">Active</MenuItem>
            <MenuItem value="INACTIVE">Inactive</MenuItem>
          </Select>
        </FormControl>
      </Grid>
      
      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          type="number"
          label="Priority"
          value={rule.priority}
          onChange={(e) => updateRule('priority', parseInt(e.target.value))}
          InputProps={{ inputProps: { min: 1, max: 100 } }}
          helperText="1 = Highest priority"
        />
      </Grid>
      
      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          label="Product Code (Optional)"
          value={rule.product_code}
          onChange={(e) => updateRule('product_code', e.target.value)}
          helperText="Leave empty for general rules"
        />
      </Grid>
      
      <Grid item xs={12} md={6}>
        <FormControlLabel
          control={
            <Switch
              checked={rule.apply_to_all_products}
              onChange={(e) => updateRule('apply_to_all_products', e.target.checked)}
            />
          }
          label="Apply to All Products"
        />
      </Grid>
      
      <Grid item xs={12} md={6}>
        <LocalizationProvider dateAdapter={AdapterDateFns}>
          <DatePicker
            label="Effective Date"
            value={new Date(rule.effective_date)}
            onChange={(date) => updateRule('effective_date', date?.toISOString().split('T')[0])}
            slotProps={{ textField: { fullWidth: true } }}
          />
        </LocalizationProvider>
      </Grid>
      
      <Grid item xs={12} md={6}>
        <LocalizationProvider dateAdapter={AdapterDateFns}>
          <DatePicker
            label="Expiry Date (Optional)"
            value={rule.expiry_date ? new Date(rule.expiry_date) : null}
            onChange={(date) => updateRule('expiry_date', date?.toISOString().split('T')[0])}
            slotProps={{ textField: { fullWidth: true } }}
          />
        </LocalizationProvider>
      </Grid>
      
      <Grid item xs={12}>
        <Divider sx={{ my: 2 }} />
        <Typography variant="subtitle1" gutterBottom>Override Options</Typography>
      </Grid>
      
      <Grid item xs={12} md={4}>
        <FormControlLabel
          control={
            <Switch
              checked={rule.allow_manual_override}
              onChange={(e) => updateRule('allow_manual_override', e.target.checked)}
            />
          }
          label="Allow Manual Override"
        />
      </Grid>
      
      <Grid item xs={12} md={4}>
        <FormControlLabel
          control={
            <Switch
              checked={rule.override_approval_required}
              onChange={(e) => updateRule('override_approval_required', e.target.checked)}
            />
          }
          label="Override Approval Required"
        />
      </Grid>
      
      <Grid item xs={12} md={4}>
        <FormControlLabel
          control={
            <Switch
              checked={rule.override_reason_mandatory}
              onChange={(e) => updateRule('override_reason_mandatory', e.target.checked)}
            />
          }
          label="Override Reason Mandatory"
        />
      </Grid>
    </Grid>
  );

  const renderCustomerEligibility = () => (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Typography variant="h6" gutterBottom>Customer Eligibility Criteria</Typography>
      </Grid>
      
      <Grid item xs={12}>
        <Typography variant="subtitle1" gutterBottom>Age Criteria</Typography>
      </Grid>
      
      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          type="number"
          label="Minimum Age"
          value={rule.customer_eligibility.age_criteria.min_age}
          onChange={(e) => updateDeepNested('customer_eligibility', 'age_criteria', 'min_age', parseInt(e.target.value))}
          InputProps={{ inputProps: { min: 18, max: 100 } }}
        />
      </Grid>
      
      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          type="number"
          label="Maximum Age"
          value={rule.customer_eligibility.age_criteria.max_age}
          onChange={(e) => updateDeepNested('customer_eligibility', 'age_criteria', 'max_age', parseInt(e.target.value))}
          InputProps={{ inputProps: { min: 18, max: 100 } }}
        />
      </Grid>
      
      <Grid item xs={12}>
        <Divider sx={{ my: 2 }} />
        <Typography variant="subtitle1" gutterBottom>Income Criteria</Typography>
      </Grid>
      
      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          type="number"
          label="Minimum Monthly Income"
          value={rule.customer_eligibility.income_criteria.min_monthly_income || ''}
          onChange={(e) => updateDeepNested('customer_eligibility', 'income_criteria', 'min_monthly_income', parseFloat(e.target.value))}
          InputProps={{ startAdornment: <InputAdornment position="start">₹</InputAdornment> }}
        />
      </Grid>
      
      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          type="number"
          label="Minimum Annual Income"
          value={rule.customer_eligibility.income_criteria.min_annual_income || ''}
          onChange={(e) => updateDeepNested('customer_eligibility', 'income_criteria', 'min_annual_income', parseFloat(e.target.value))}
          InputProps={{ startAdornment: <InputAdornment position="start">₹</InputAdornment> }}
        />
      </Grid>
      
      <Grid item xs={12} md={6}>
        <FormControl fullWidth>
          <InputLabel>Verification Methods</InputLabel>
          <Select
            multiple
            value={rule.customer_eligibility.income_criteria.verification_methods}
            onChange={(e) => updateDeepNested('customer_eligibility', 'income_criteria', 'verification_methods', e.target.value)}
            label="Verification Methods"
            renderValue={(selected) => (
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                {(selected as string[]).map((value) => (
                  <Chip key={value} label={value} size="small" />
                ))}
              </Box>
            )}
          >
            {verificationMethods.map((method) => (
              <MenuItem key={method} value={method}>{method.replace(/_/g, ' ')}</MenuItem>
            ))}
          </Select>
        </FormControl>
      </Grid>
      
      <Grid item xs={12} md={6}>
        <FormControlLabel
          control={
            <Switch
              checked={rule.customer_eligibility.income_criteria.require_proof}
              onChange={(e) => updateDeepNested('customer_eligibility', 'income_criteria', 'require_proof', e.target.checked)}
            />
          }
          label="Income Proof Required"
        />
      </Grid>
      
      <Grid item xs={12}>
        <Divider sx={{ my: 2 }} />
        <Typography variant="subtitle1" gutterBottom>Employment & Credit</Typography>
      </Grid>
      
      <Grid item xs={12} md={6}>
        <FormControl fullWidth>
          <InputLabel>Employment Types</InputLabel>
          <Select
            multiple
            value={rule.customer_eligibility.employment_types}
            onChange={(e) => updateNested('customer_eligibility', 'employment_types', e.target.value)}
            label="Employment Types"
            renderValue={(selected) => (
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                {(selected as string[]).map((value) => (
                  <Chip key={value} label={value.replace(/_/g, ' ')} size="small" />
                ))}
              </Box>
            )}
          >
            {employmentTypes.map((type) => (
              <MenuItem key={type} value={type}>{type.replace(/_/g, ' ')}</MenuItem>
            ))}
          </Select>
        </FormControl>
      </Grid>
      
      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          type="number"
          label="Minimum Credit Score"
          value={rule.customer_eligibility.credit_score_criteria?.min_credit_score || ''}
          onChange={(e) => updateDeepNested('customer_eligibility', 'credit_score_criteria', 'min_credit_score', parseInt(e.target.value))}
          InputProps={{ inputProps: { min: 300, max: 900 } }}
        />
      </Grid>
      
      <Grid item xs={12} md={4}>
        <FormControlLabel
          control={
            <Switch
              checked={rule.customer_eligibility.credit_score_criteria?.mandatory || false}
              onChange={(e) => updateDeepNested('customer_eligibility', 'credit_score_criteria', 'mandatory', e.target.checked)}
            />
          }
          label="Credit Score Mandatory"
        />
      </Grid>
      
      <Grid item xs={12} md={4}>
        <FormControlLabel
          control={
            <Switch
              checked={rule.customer_eligibility.credit_score_criteria?.allow_no_history || false}
              onChange={(e) => updateDeepNested('customer_eligibility', 'credit_score_criteria', 'allow_no_history', e.target.checked)}
            />
          }
          label="Allow No Credit History"
        />
      </Grid>
      
      <Grid item xs={12}>
        <Divider sx={{ my: 2 }} />
        <Typography variant="subtitle1" gutterBottom>Nationality & Residency</Typography>
      </Grid>
      
      <Grid item xs={12} md={6}>
        <FormControl fullWidth>
          <InputLabel>Allowed Residency Status</InputLabel>
          <Select
            multiple
            value={rule.customer_eligibility.allowed_residency_status}
            onChange={(e) => updateNested('customer_eligibility', 'allowed_residency_status', e.target.value)}
            label="Allowed Residency Status"
            renderValue={(selected) => (
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                {(selected as string[]).map((value) => (
                  <Chip key={value} label={value} size="small" />
                ))}
              </Box>
            )}
          >
            {residencyStatuses.map((status) => (
              <MenuItem key={status} value={status}>{status}</MenuItem>
            ))}
          </Select>
        </FormControl>
      </Grid>
      
      <Grid item xs={12}>
        <Divider sx={{ my: 2 }} />
        <Typography variant="subtitle1" gutterBottom>Co-applicant & Guarantor</Typography>
      </Grid>
      
      <Grid item xs={12} md={3}>
        <FormControlLabel
          control={
            <Switch
              checked={rule.customer_eligibility.co_applicant_rules?.required || false}
              onChange={(e) => updateDeepNested('customer_eligibility', 'co_applicant_rules', 'required', e.target.checked)}
            />
          }
          label="Co-applicant Required"
        />
      </Grid>
      
      <Grid item xs={12} md={3}>
        <TextField
          fullWidth
          type="number"
          label="Min Co-applicants"
          value={rule.customer_eligibility.co_applicant_rules?.min_count || 0}
          onChange={(e) => updateDeepNested('customer_eligibility', 'co_applicant_rules', 'min_count', parseInt(e.target.value))}
          InputProps={{ inputProps: { min: 0, max: 5 } }}
        />
      </Grid>
      
      <Grid item xs={12} md={3}>
        <FormControlLabel
          control={
            <Switch
              checked={rule.customer_eligibility.guarantor_rules?.required || false}
              onChange={(e) => updateDeepNested('customer_eligibility', 'guarantor_rules', 'required', e.target.checked)}
            />
          }
          label="Guarantor Required"
        />
      </Grid>
      
      <Grid item xs={12} md={3}>
        <TextField
          fullWidth
          type="number"
          label="Min Guarantors"
          value={rule.customer_eligibility.guarantor_rules?.min_count || 0}
          onChange={(e) => updateDeepNested('customer_eligibility', 'guarantor_rules', 'min_count', parseInt(e.target.value))}
          InputProps={{ inputProps: { min: 0, max: 5 } }}
        />
      </Grid>
      
      <Grid item xs={12}>
        <Divider sx={{ my: 2 }} />
        <Typography variant="subtitle1" gutterBottom>Additional Checks</Typography>
      </Grid>
      
      <Grid item xs={12} md={4}>
        <FormControlLabel
          control={
            <Switch
              checked={rule.customer_eligibility.existing_customer_required}
              onChange={(e) => updateNested('customer_eligibility', 'existing_customer_required', e.target.checked)}
            />
          }
          label="Existing Customer Required"
        />
      </Grid>
      
      <Grid item xs={12} md={4}>
        <FormControlLabel
          control={
            <Switch
              checked={rule.customer_eligibility.blacklist_check}
              onChange={(e) => updateNested('customer_eligibility', 'blacklist_check', e.target.checked)}
            />
          }
          label="Blacklist Check"
        />
      </Grid>
      
      <Grid item xs={12} md={4}>
        <FormControlLabel
          control={
            <Switch
              checked={rule.customer_eligibility.politically_exposed_person_check}
              onChange={(e) => updateNested('customer_eligibility', 'politically_exposed_person_check', e.target.checked)}
            />
          }
          label="PEP Check"
        />
      </Grid>
    </Grid>
  );

  const renderFinancialEligibility = () => (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Typography variant="h6" gutterBottom>Financial Eligibility Criteria</Typography>
      </Grid>
      
      <Grid item xs={12}>
        <Typography variant="subtitle1" gutterBottom>FOIR (Fixed Obligation to Income Ratio)</Typography>
      </Grid>
      
      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          type="number"
          label="Maximum FOIR %"
          value={rule.financial_eligibility.foir_criteria?.max_foir_percentage || ''}
          onChange={(e) => updateDeepNested('financial_eligibility', 'foir_criteria', 'max_foir_percentage', parseFloat(e.target.value))}
          InputProps={{ 
            endAdornment: <InputAdornment position="end">%</InputAdornment>,
            inputProps: { min: 0, max: 100 }
          }}
          helperText="Typically 40-60%"
        />
      </Grid>
      
      <Grid item xs={12} md={6}>
        <FormControlLabel
          control={
            <Switch
              checked={rule.financial_eligibility.foir_criteria?.include_proposed_emi || false}
              onChange={(e) => updateDeepNested('financial_eligibility', 'foir_criteria', 'include_proposed_emi', e.target.checked)}
            />
          }
          label="Include Proposed EMI in FOIR"
        />
      </Grid>
      
      <Grid item xs={12}>
        <Divider sx={{ my: 2 }} />
        <Typography variant="subtitle1" gutterBottom>DTI (Debt-to-Income Ratio)</Typography>
      </Grid>
      
      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          type="number"
          label="Maximum DTI %"
          value={rule.financial_eligibility.dti_criteria?.max_dti_percentage || ''}
          onChange={(e) => updateDeepNested('financial_eligibility', 'dti_criteria', 'max_dti_percentage', parseFloat(e.target.value))}
          InputProps={{ 
            endAdornment: <InputAdornment position="end">%</InputAdornment>,
            inputProps: { min: 0, max: 100 }
          }}
          helperText="Typically 30-50%"
        />
      </Grid>
      
      <Grid item xs={12} md={6}>
        <FormControlLabel
          control={
            <Switch
              checked={rule.financial_eligibility.dti_criteria?.include_all_obligations || false}
              onChange={(e) => updateDeepNested('financial_eligibility', 'dti_criteria', 'include_all_obligations', e.target.checked)}
            />
          }
          label="Include All Obligations"
        />
      </Grid>
      
      <Grid item xs={12}>
        <Divider sx={{ my: 2 }} />
        <Typography variant="subtitle1" gutterBottom>Existing Obligations</Typography>
      </Grid>
      
      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          type="number"
          label="Max Existing Loans"
          value={rule.financial_eligibility.existing_obligations?.max_existing_loans || ''}
          onChange={(e) => updateDeepNested('financial_eligibility', 'existing_obligations', 'max_existing_loans', parseInt(e.target.value))}
          InputProps={{ inputProps: { min: 0 } }}
        />
      </Grid>
      
      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          type="number"
          label="Max Existing EMI"
          value={rule.financial_eligibility.existing_obligations?.max_existing_emi || ''}
          onChange={(e) => updateDeepNested('financial_eligibility', 'existing_obligations', 'max_existing_emi', parseFloat(e.target.value))}
          InputProps={{ 
            startAdornment: <InputAdornment position="start">₹</InputAdornment>,
            inputProps: { min: 0 }
          }}
        />
      </Grid>
      
      <Grid item xs={12}>
        <Divider sx={{ my: 2 }} />
        <Typography variant="subtitle1" gutterBottom>Banking & ITR Requirements</Typography>
      </Grid>
      
      <Grid item xs={12} md={6}>
        <FormControlLabel
          control={
            <Switch
              checked={rule.financial_eligibility.banking_turnover?.required || false}
              onChange={(e) => updateDeepNested('financial_eligibility', 'banking_turnover', 'required', e.target.checked)}
            />
          }
          label="Banking Turnover Required"
        />
      </Grid>
      
      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          type="number"
          label="Min Monthly Turnover"
          value={rule.financial_eligibility.banking_turnover?.min_monthly_turnover || ''}
          onChange={(e) => updateDeepNested('financial_eligibility', 'banking_turnover', 'min_monthly_turnover', parseFloat(e.target.value))}
          InputProps={{ startAdornment: <InputAdornment position="start">₹</InputAdornment> }}
          disabled={!rule.financial_eligibility.banking_turnover?.required}
        />
      </Grid>
      
      <Grid item xs={12} md={6}>
        <FormControlLabel
          control={
            <Switch
              checked={rule.financial_eligibility.itr_criteria?.required || false}
              onChange={(e) => updateDeepNested('financial_eligibility', 'itr_criteria', 'required', e.target.checked)}
            />
          }
          label="ITR Required"
        />
      </Grid>
      
      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          type="number"
          label="Minimum ITR Years"
          value={rule.financial_eligibility.itr_criteria?.min_years || ''}
          onChange={(e) => updateDeepNested('financial_eligibility', 'itr_criteria', 'min_years', parseInt(e.target.value))}
          InputProps={{ inputProps: { min: 1, max: 5 } }}
          disabled={!rule.financial_eligibility.itr_criteria?.required}
        />
      </Grid>
      
      <Grid item xs={12}>
        <Divider sx={{ my: 2 }} />
        <Typography variant="subtitle1" gutterBottom>Additional Financial Criteria</Typography>
      </Grid>
      
      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          type="number"
          label="Min Net Worth"
          value={rule.financial_eligibility.min_net_worth || ''}
          onChange={(e) => updateNested('financial_eligibility', 'min_net_worth', parseFloat(e.target.value))}
          InputProps={{ startAdornment: <InputAdornment position="start">₹</InputAdornment> }}
        />
      </Grid>
      
      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          type="number"
          label="Min Liquid Assets"
          value={rule.financial_eligibility.min_liquid_assets || ''}
          onChange={(e) => updateNested('financial_eligibility', 'min_liquid_assets', parseFloat(e.target.value))}
          InputProps={{ startAdornment: <InputAdornment position="start">₹</InputAdornment> }}
        />
      </Grid>
    </Grid>
  );

  const renderGeographicEligibility = () => (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Typography variant="h6" gutterBottom>Geographic Eligibility Criteria</Typography>
      </Grid>
      
      <Grid item xs={12}>
        <Typography variant="subtitle1" gutterBottom>PIN Code Restrictions</Typography>
      </Grid>
      
      <Grid item xs={12} md={6}>
        <FormControl fullWidth>
          <InputLabel>Restriction Type</InputLabel>
          <Select
            value={rule.geographic_eligibility.pin_code_restriction?.type || 'NONE'}
            onChange={(e) => {
              if (e.target.value === 'NONE') {
                updateNested('geographic_eligibility', 'pin_code_restriction', null);
              } else {
                updateNested('geographic_eligibility', 'pin_code_restriction', { type: e.target.value, pin_codes: [] });
              }
            }}
            label="Restriction Type"
          >
            <MenuItem value="NONE">No Restriction</MenuItem>
            <MenuItem value="INCLUDE">Include Only</MenuItem>
            <MenuItem value="EXCLUDE">Exclude</MenuItem>
          </Select>
        </FormControl>
      </Grid>
      
      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          label="PIN Codes (comma-separated)"
          value={rule.geographic_eligibility.pin_code_restriction?.pin_codes?.join(', ') || ''}
          onChange={(e) => {
            const pins = e.target.value.split(',').map(p => p.trim()).filter(p => p);
            updateDeepNested('geographic_eligibility', 'pin_code_restriction', 'pin_codes', pins);
          }}
          disabled={!rule.geographic_eligibility.pin_code_restriction}
          helperText="e.g., 400001, 400002, 400003"
        />
      </Grid>
      
      <Grid item xs={12}>
        <Divider sx={{ my: 2 }} />
        <Typography variant="subtitle1" gutterBottom>State Restrictions</Typography>
      </Grid>
      
      <Grid item xs={12} md={6}>
        <FormControl fullWidth>
          <InputLabel>Restriction Type</InputLabel>
          <Select
            value={rule.geographic_eligibility.state_restriction?.type || 'NONE'}
            onChange={(e) => {
              if (e.target.value === 'NONE') {
                updateNested('geographic_eligibility', 'state_restriction', null);
              } else {
                updateNested('geographic_eligibility', 'state_restriction', { type: e.target.value, states: [] });
              }
            }}
            label="Restriction Type"
          >
            <MenuItem value="NONE">No Restriction</MenuItem>
            <MenuItem value="INCLUDE">Include Only</MenuItem>
            <MenuItem value="EXCLUDE">Exclude</MenuItem>
          </Select>
        </FormControl>
      </Grid>
      
      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          label="State Codes (comma-separated)"
          value={rule.geographic_eligibility.state_restriction?.states?.join(', ') || ''}
          onChange={(e) => {
            const states = e.target.value.split(',').map(s => s.trim()).filter(s => s);
            updateDeepNested('geographic_eligibility', 'state_restriction', 'states', states);
          }}
          disabled={!rule.geographic_eligibility.state_restriction}
          helperText="e.g., MH, DL, KA"
        />
      </Grid>
      
      <Grid item xs={12}>
        <Divider sx={{ my: 2 }} />
        <Typography variant="subtitle1" gutterBottom>Location Type Preferences</Typography>
      </Grid>
      
      <Grid item xs={12} md={3}>
        <FormControlLabel
          control={
            <Switch
              checked={rule.geographic_eligibility.allow_rural_areas}
              onChange={(e) => updateNested('geographic_eligibility', 'allow_rural_areas', e.target.checked)}
            />
          }
          label="Allow Rural"
        />
      </Grid>
      
      <Grid item xs={12} md={3}>
        <FormControlLabel
          control={
            <Switch
              checked={rule.geographic_eligibility.allow_semi_urban_areas}
              onChange={(e) => updateNested('geographic_eligibility', 'allow_semi_urban_areas', e.target.checked)}
            />
          }
          label="Allow Semi-Urban"
        />
      </Grid>
      
      <Grid item xs={12} md={3}>
        <FormControlLabel
          control={
            <Switch
              checked={rule.geographic_eligibility.allow_urban_areas}
              onChange={(e) => updateNested('geographic_eligibility', 'allow_urban_areas', e.target.checked)}
            />
          }
          label="Allow Urban"
        />
      </Grid>
      
      <Grid item xs={12} md={3}>
        <FormControlLabel
          control={
            <Switch
              checked={rule.geographic_eligibility.allow_metro_areas}
              onChange={(e) => updateNested('geographic_eligibility', 'allow_metro_areas', e.target.checked)}
            />
          }
          label="Allow Metro"
        />
      </Grid>
    </Grid>
  );

  const renderReviewAndSave = () => (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Typography variant="h6" gutterBottom>Review Eligibility Rule</Typography>
        <Alert severity="info" sx={{ mb: 2 }}>
          Please review all criteria before saving the eligibility rule.
        </Alert>
      </Grid>
      
      <Grid item xs={12}>
        <Paper sx={{ p: 2 }}>
          <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 600 }}>Basic Information</Typography>
          <Grid container spacing={1}>
            <Grid item xs={6}><Typography variant="body2" color="text.secondary">Rule Code:</Typography></Grid>
            <Grid item xs={6}><Typography variant="body2">{rule.rule_code}</Typography></Grid>
            
            <Grid item xs={6}><Typography variant="body2" color="text.secondary">Rule Name:</Typography></Grid>
            <Grid item xs={6}><Typography variant="body2">{rule.rule_name}</Typography></Grid>
            
            <Grid item xs={6}><Typography variant="body2" color="text.secondary">Status:</Typography></Grid>
            <Grid item xs={6}><Chip label={rule.status} size="small" color="primary" /></Grid>
            
            <Grid item xs={6}><Typography variant="body2" color="text.secondary">Priority:</Typography></Grid>
            <Grid item xs={6}><Typography variant="body2">{rule.priority}</Typography></Grid>
          </Grid>
        </Paper>
      </Grid>
      
      <Grid item xs={12}>
        <Paper sx={{ p: 2 }}>
          <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 600 }}>Customer Eligibility</Typography>
          <Grid container spacing={1}>
            <Grid item xs={6}><Typography variant="body2" color="text.secondary">Age Range:</Typography></Grid>
            <Grid item xs={6}><Typography variant="body2">{rule.customer_eligibility.age_criteria.min_age} - {rule.customer_eligibility.age_criteria.max_age} years</Typography></Grid>
            
            <Grid item xs={6}><Typography variant="body2" color="text.secondary">Min Monthly Income:</Typography></Grid>
            <Grid item xs={6}><Typography variant="body2">₹{rule.customer_eligibility.income_criteria.min_monthly_income?.toLocaleString() || 'N/A'}</Typography></Grid>
            
            <Grid item xs={6}><Typography variant="body2" color="text.secondary">Employment Types:</Typography></Grid>
            <Grid item xs={6}>
              <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                {rule.customer_eligibility.employment_types.map((type: string) => (
                  <Chip key={type} label={type} size="small" />
                ))}
              </Box>
            </Grid>
            
            <Grid item xs={6}><Typography variant="body2" color="text.secondary">Min Credit Score:</Typography></Grid>
            <Grid item xs={6}><Typography variant="body2">{rule.customer_eligibility.credit_score_criteria?.min_credit_score || 'N/A'}</Typography></Grid>
          </Grid>
        </Paper>
      </Grid>
      
      <Grid item xs={12}>
        <Paper sx={{ p: 2 }}>
          <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 600 }}>Financial Eligibility</Typography>
          <Grid container spacing={1}>
            <Grid item xs={6}><Typography variant="body2" color="text.secondary">Max FOIR:</Typography></Grid>
            <Grid item xs={6}><Typography variant="body2">{rule.financial_eligibility.foir_criteria?.max_foir_percentage || 'N/A'}%</Typography></Grid>
            
            <Grid item xs={6}><Typography variant="body2" color="text.secondary">Max DTI:</Typography></Grid>
            <Grid item xs={6}><Typography variant="body2">{rule.financial_eligibility.dti_criteria?.max_dti_percentage || 'N/A'}%</Typography></Grid>
            
            <Grid item xs={6}><Typography variant="body2" color="text.secondary">ITR Required:</Typography></Grid>
            <Grid item xs={6}><Typography variant="body2">{rule.financial_eligibility.itr_criteria?.required ? 'Yes' : 'No'}</Typography></Grid>
          </Grid>
        </Paper>
      </Grid>
      
      <Grid item xs={12}>
        <Paper sx={{ p: 2 }}>
          <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 600 }}>Geographic Eligibility</Typography>
          <Grid container spacing={1}>
            <Grid item xs={6}><Typography variant="body2" color="text.secondary">PIN Code Restriction:</Typography></Grid>
            <Grid item xs={6}><Typography variant="body2">{rule.geographic_eligibility.pin_code_restriction?.type || 'None'}</Typography></Grid>
            
            <Grid item xs={6}><Typography variant="body2" color="text.secondary">State Restriction:</Typography></Grid>
            <Grid item xs={6}><Typography variant="body2">{rule.geographic_eligibility.state_restriction?.type || 'None'}</Typography></Grid>
            
            <Grid item xs={6}><Typography variant="body2" color="text.secondary">Location Types:</Typography></Grid>
            <Grid item xs={6}>
              <Box sx={{ display: 'flex', gap: 0.5 }}>
                {rule.geographic_eligibility.allow_rural_areas && <Chip label="Rural" size="small" />}
                {rule.geographic_eligibility.allow_semi_urban_areas && <Chip label="Semi-Urban" size="small" />}
                {rule.geographic_eligibility.allow_urban_areas && <Chip label="Urban" size="small" />}
                {rule.geographic_eligibility.allow_metro_areas && <Chip label="Metro" size="small" />}
              </Box>
            </Grid>
          </Grid>
        </Paper>
      </Grid>
    </Grid>
  );

  const getStepContent = (step: number) => {
    switch (step) {
      case 0:
        return renderBasicInformation();
      case 1:
        return renderCustomerEligibility();
      case 2:
        return renderFinancialEligibility();
      case 3:
        return renderGeographicEligibility();
      case 4:
        return renderReviewAndSave();
      default:
        return 'Unknown step';
    }
  };

  return (
    <Box sx={{ width: '100%' }}>
      <Paper sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          {ruleId ? 'Edit Eligibility Rule' : 'Create New Eligibility Rule'}
        </Typography>
        
        <Stepper activeStep={activeStep} sx={{ pt: 3, pb: 5 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>
        
        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}
        
        {success && (
          <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(null)}>
            {success}
          </Alert>
        )}
        
        <Box sx={{ mb: 3 }}>
          {getStepContent(activeStep)}
        </Box>
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between', pt: 2 }}>
          <Button
            disabled={activeStep === 0}
            onClick={handleBack}
          >
            Back
          </Button>
          
          <Box>
            {onCancel && (
              <Button
                onClick={onCancel}
                startIcon={<CancelIcon />}
                sx={{ mr: 1 }}
              >
                Cancel
              </Button>
            )}
            
            {activeStep === steps.length - 1 ? (
              <Button
                variant="contained"
                onClick={handleSave}
                disabled={loading}
                startIcon={<SaveIcon />}
              >
                {loading ? 'Saving...' : ruleId ? 'Update Rule' : 'Create Rule'}
              </Button>
            ) : (
              <Button
                variant="contained"
                onClick={handleNext}
              >
                Next
              </Button>
            )}
          </Box>
        </Box>
      </Paper>
    </Box>
  );
};

export default EligibilityRuleBuilder;
