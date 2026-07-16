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
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { productsService } from '../../services/productsService';

interface RateCardEntry {
  segment?: string;
  min_amount?: number;
  max_amount?: number;
  rate: number;
}

interface InterestConfig {
  calculation_method: string;
  rate_type: string;
  base_rate: number;
  min_rate?: number;
  max_rate?: number;
  rate_revision_frequency?: string;
  rate_card: RateCardEntry[];
  enable_floating_rate: boolean;
  rate_reset_rules?: string;
}

interface TenureConfig {
  min_tenure: number;
  max_tenure: number;
  allowed_tenures: number[];
  tenure_based_pricing: boolean;
}

interface AmountConfig {
  min_amount: number;
  max_amount: number;
  amount_rounding?: number;
  enable_ltv: boolean;
  max_ltv_percentage?: number;
  amount_slabs: Array<{ min: number; max: number; rate_adjustment?: number }>;
}

interface FeeChargeConfig {
  charge_type: string;
  flat_amount?: number;
  percentage?: number;
  min_amount?: number;
  max_amount?: number;
  gst_applicable: boolean;
  waivable: boolean;
}

interface FeesConfig {
  processing_fee?: FeeChargeConfig;
  documentation_charges?: FeeChargeConfig;
  valuation_charges?: FeeChargeConfig;
  legal_charges?: FeeChargeConfig;
  stamp_duty?: FeeChargeConfig;
  prepayment_charges?: FeeChargeConfig;
  penal_charges?: FeeChargeConfig;
  bounce_charges?: FeeChargeConfig;
  late_payment_charges?: FeeChargeConfig;
  foreclosure_charges?: FeeChargeConfig;
  part_payment_charges?: FeeChargeConfig;
}

interface EMIConfig {
  emi_type: string;
  emi_start_date_option: string;
  grace_period_months?: number;
  moratorium_period_months?: number;
  enable_bullet_payment: boolean;
  enable_balloon_payment: boolean;
  balloon_payment_percentage?: number;
  enable_step_emi: boolean;
  step_up_percentage?: number;
  step_down_percentage?: number;
  emi_rounding?: number;
  enable_prepayment: boolean;
  enable_part_payment: boolean;
}

interface Product {
  id?: string;
  product_code: string;
  product_name: string;
  category: string;
  description: string;
  status: string;
  effective_date: string;
  expiry_date?: string;
  interest_config: InterestConfig;
  tenure_config: TenureConfig;
  amount_config: AmountConfig;
  fees_config: FeesConfig;
  emi_config: EMIConfig;
  eligibility_criteria?: any;
  document_requirements?: any[];
  is_featured: boolean;
}

const steps = [
  'Basic Information',
  'Interest Configuration',
  'Tenure & Amount',
  'Fees & Charges',
  'EMI Configuration',
  'Review & Save',
];

const categories = [
  'PERSONAL_LOAN',
  'HOME_LOAN',
  'BUSINESS_LOAN',
  'GOLD_LOAN',
  'VEHICLE_LOAN',
  'EDUCATION_LOAN',
  'LAP',
  'MSME_LOAN',
  'AGRICULTURE_LOAN',
];

const calculationMethods = ['REDUCING_BALANCE', 'FLAT_RATE', 'SIMPLE_INTEREST', 'COMPOUND_INTEREST'];
const rateTypes = ['FIXED', 'FLOATING', 'HYBRID'];
const revisionFrequencies = ['MONTHLY', 'QUARTERLY', 'HALF_YEARLY', 'YEARLY', 'NONE'];
const chargeTypes = ['FLAT', 'PERCENTAGE', 'SLAB_BASED'];
const emiTypes = ['STANDARD', 'STEP_UP', 'STEP_DOWN', 'FLEXIBLE'];
const emiStartOptions = ['FIRST_OF_MONTH', 'DISBURSEMENT_DATE', 'CUSTOM_DATE', 'NEXT_MONTH'];

interface ProductBuilderProps {
  productId?: string;
  onSave?: (product: Product) => void;
  onCancel?: () => void;
}

const ProductBuilder: React.FC<ProductBuilderProps> = ({ productId, onSave, onCancel }) => {
  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const [product, setProduct] = useState<Product>({
    product_code: '',
    product_name: '',
    category: 'PERSONAL_LOAN',
    description: '',
    status: 'DRAFT',
    effective_date: new Date().toISOString().split('T')[0],
    interest_config: {
      calculation_method: 'REDUCING_BALANCE',
      rate_type: 'FIXED',
      base_rate: 12.0,
      rate_card: [],
      enable_floating_rate: false,
    },
    tenure_config: {
      min_tenure: 12,
      max_tenure: 60,
      allowed_tenures: [12, 24, 36, 48, 60],
      tenure_based_pricing: false,
    },
    amount_config: {
      min_amount: 50000,
      max_amount: 500000,
      enable_ltv: false,
      amount_slabs: [],
    },
    fees_config: {
      processing_fee: {
        charge_type: 'PERCENTAGE',
        percentage: 2.0,
        gst_applicable: true,
        waivable: false,
      },
    },
    emi_config: {
      emi_type: 'STANDARD',
      emi_start_date_option: 'FIRST_OF_MONTH',
      enable_bullet_payment: false,
      enable_balloon_payment: false,
      enable_step_emi: false,
      enable_prepayment: true,
      enable_part_payment: true,
    },
    is_featured: false,
  });

  useEffect(() => {
    if (productId) {
      loadProduct();
    }
  }, [productId]);

  const loadProduct = async () => {
    try {
      setLoading(true);
      const data = await productsService.getProduct(productId!);
      setProduct(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load product');
    } finally {
      setLoading(false);
    }
  };

  const handleNext = () => {
    setActiveStep((prev) => prev + 1);
  };

  const handleBack = () => {
    setActiveStep((prev) => prev - 1);
  };

  const handleSave = async () => {
    try {
      setLoading(true);
      setError(null);
      
      let savedProduct;
      if (productId) {
        savedProduct = await productsService.updateProduct(productId, product);
        setSuccess('Product updated successfully');
      } else {
        savedProduct = await productsService.createProduct(product);
        setSuccess('Product created successfully');
      }
      
      if (onSave) {
        onSave(savedProduct);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to save product');
    } finally {
      setLoading(false);
    }
  };

  const updateProduct = (field: string, value: any) => {
    setProduct((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const updateNestedConfig = (config: string, field: string, value: any) => {
    setProduct((prev) => ({
      ...prev,
      [config]: {
        ...(prev as any)[config],
        [field]: value,
      },
    }));
  };

  const addRateCardEntry = () => {
    const newEntry: RateCardEntry = {
      segment: '',
      min_amount: 0,
      max_amount: 0,
      rate: product.interest_config.base_rate,
    };
    setProduct((prev) => ({
      ...prev,
      interest_config: {
        ...prev.interest_config,
        rate_card: [...prev.interest_config.rate_card, newEntry],
      },
    }));
  };

  const updateRateCardEntry = (index: number, field: string, value: any) => {
    const updatedRateCard = [...product.interest_config.rate_card];
    updatedRateCard[index] = {
      ...updatedRateCard[index],
      [field]: value,
    };
    setProduct((prev) => ({
      ...prev,
      interest_config: {
        ...prev.interest_config,
        rate_card: updatedRateCard,
      },
    }));
  };

  const removeRateCardEntry = (index: number) => {
    setProduct((prev) => ({
      ...prev,
      interest_config: {
        ...prev.interest_config,
        rate_card: prev.interest_config.rate_card.filter((_, i) => i !== index),
      },
    }));
  };

  const addAmountSlab = () => {
    const newSlab = {
      min: 0,
      max: 0,
      rate_adjustment: 0,
    };
    setProduct((prev) => ({
      ...prev,
      amount_config: {
        ...prev.amount_config,
        amount_slabs: [...prev.amount_config.amount_slabs, newSlab],
      },
    }));
  };

  const updateAmountSlab = (index: number, field: string, value: any) => {
    const updatedSlabs = [...product.amount_config.amount_slabs];
    updatedSlabs[index] = {
      ...updatedSlabs[index],
      [field]: value,
    };
    setProduct((prev) => ({
      ...prev,
      amount_config: {
        ...prev.amount_config,
        amount_slabs: updatedSlabs,
      },
    }));
  };

  const removeAmountSlab = (index: number) => {
    setProduct((prev) => ({
      ...prev,
      amount_config: {
        ...prev.amount_config,
        amount_slabs: prev.amount_config.amount_slabs.filter((_, i) => i !== index),
      },
    }));
  };

  const updateFeeCharge = (feeName: string, field: string, value: any) => {
    setProduct((prev) => ({
      ...prev,
      fees_config: {
        ...prev.fees_config,
        [feeName]: {
          ...(prev.fees_config as any)[feeName],
          [field]: value,
        },
      },
    }));
  };

  const renderBasicInformation = () => (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Typography variant="h6" gutterBottom>Basic Product Information</Typography>
      </Grid>
      
      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          label="Product Code"
          value={product.product_code}
          onChange={(e) => updateProduct('product_code', e.target.value)}
          required
          helperText="Unique identifier for the product"
        />
      </Grid>
      
      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          label="Product Name"
          value={product.product_name}
          onChange={(e) => updateProduct('product_name', e.target.value)}
          required
        />
      </Grid>
      
      <Grid item xs={12} md={6}>
        <FormControl fullWidth>
          <InputLabel>Product Category</InputLabel>
          <Select
            value={product.category}
            onChange={(e) => updateProduct('category', e.target.value)}
            label="Product Category"
          >
            {categories.map((cat) => (
              <MenuItem key={cat} value={cat}>
                {cat.replace(/_/g, ' ')}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Grid>
      
      <Grid item xs={12} md={6}>
        <FormControl fullWidth>
          <InputLabel>Status</InputLabel>
          <Select
            value={product.status}
            onChange={(e) => updateProduct('status', e.target.value)}
            label="Status"
          >
            <MenuItem value="DRAFT">Draft</MenuItem>
            <MenuItem value="ACTIVE">Active</MenuItem>
            <MenuItem value="INACTIVE">Inactive</MenuItem>
            <MenuItem value="COMING_SOON">Coming Soon</MenuItem>
          </Select>
        </FormControl>
      </Grid>
      
      <Grid item xs={12}>
        <TextField
          fullWidth
          multiline
          rows={3}
          label="Description"
          value={product.description}
          onChange={(e) => updateProduct('description', e.target.value)}
        />
      </Grid>
      
      <Grid item xs={12} md={6}>
        <LocalizationProvider dateAdapter={AdapterDateFns}>
          <DatePicker
            label="Effective Date"
            value={new Date(product.effective_date)}
            onChange={(date) => updateProduct('effective_date', date?.toISOString().split('T')[0])}
            slotProps={{ textField: { fullWidth: true } }}
          />
        </LocalizationProvider>
      </Grid>
      
      <Grid item xs={12} md={6}>
        <LocalizationProvider dateAdapter={AdapterDateFns}>
          <DatePicker
            label="Expiry Date (Optional)"
            value={product.expiry_date ? new Date(product.expiry_date) : null}
            onChange={(date) => updateProduct('expiry_date', date?.toISOString().split('T')[0])}
            slotProps={{ textField: { fullWidth: true } }}
          />
        </LocalizationProvider>
      </Grid>
      
      <Grid item xs={12}>
        <FormControlLabel
          control={
            <Switch
              checked={product.is_featured}
              onChange={(e) => updateProduct('is_featured', e.target.checked)}
            />
          }
          label="Featured Product"
        />
      </Grid>
    </Grid>
  );

  const renderInterestConfiguration = () => (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Typography variant="h6" gutterBottom>Interest Configuration</Typography>
      </Grid>
      
      <Grid item xs={12} md={6}>
        <FormControl fullWidth>
          <InputLabel>Calculation Method</InputLabel>
          <Select
            value={product.interest_config.calculation_method}
            onChange={(e) => updateNestedConfig('interest_config', 'calculation_method', e.target.value)}
            label="Calculation Method"
          >
            {calculationMethods.map((method) => (
              <MenuItem key={method} value={method}>
                {method.replace(/_/g, ' ')}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Grid>
      
      <Grid item xs={12} md={6}>
        <FormControl fullWidth>
          <InputLabel>Rate Type</InputLabel>
          <Select
            value={product.interest_config.rate_type}
            onChange={(e) => updateNestedConfig('interest_config', 'rate_type', e.target.value)}
            label="Rate Type"
          >
            {rateTypes.map((type) => (
              <MenuItem key={type} value={type}>{type}</MenuItem>
            ))}
          </Select>
        </FormControl>
      </Grid>
      
      <Grid item xs={12} md={4}>
        <TextField
          fullWidth
          type="number"
          label="Base Interest Rate (%)"
          value={product.interest_config.base_rate}
          onChange={(e) => updateNestedConfig('interest_config', 'base_rate', parseFloat(e.target.value))}
          InputProps={{ inputProps: { min: 0, max: 100, step: 0.1 } }}
        />
      </Grid>
      
      <Grid item xs={12} md={4}>
        <TextField
          fullWidth
          type="number"
          label="Minimum Rate (%)"
          value={product.interest_config.min_rate || ''}
          onChange={(e) => updateNestedConfig('interest_config', 'min_rate', parseFloat(e.target.value))}
          InputProps={{ inputProps: { min: 0, max: 100, step: 0.1 } }}
        />
      </Grid>
      
      <Grid item xs={12} md={4}>
        <TextField
          fullWidth
          type="number"
          label="Maximum Rate (%)"
          value={product.interest_config.max_rate || ''}
          onChange={(e) => updateNestedConfig('interest_config', 'max_rate', parseFloat(e.target.value))}
          InputProps={{ inputProps: { min: 0, max: 100, step: 0.1 } }}
        />
      </Grid>
      
      <Grid item xs={12} md={6}>
        <FormControl fullWidth>
          <InputLabel>Rate Revision Frequency</InputLabel>
          <Select
            value={product.interest_config.rate_revision_frequency || 'NONE'}
            onChange={(e) => updateNestedConfig('interest_config', 'rate_revision_frequency', e.target.value)}
            label="Rate Revision Frequency"
          >
            {revisionFrequencies.map((freq) => (
              <MenuItem key={freq} value={freq}>{freq}</MenuItem>
            ))}
          </Select>
        </FormControl>
      </Grid>
      
      <Grid item xs={12} md={6}>
        <FormControlLabel
          control={
            <Switch
              checked={product.interest_config.enable_floating_rate}
              onChange={(e) => updateNestedConfig('interest_config', 'enable_floating_rate', e.target.checked)}
            />
          }
          label="Enable Floating Rate"
        />
      </Grid>
      
      <Grid item xs={12}>
        <Divider sx={{ my: 2 }} />
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="subtitle1">Rate Card (Segment/Slab-wise Rates)</Typography>
          <Button
            startIcon={<AddIcon />}
            onClick={addRateCardEntry}
            variant="outlined"
            size="small"
          >
            Add Rate Card Entry
          </Button>
        </Box>
        
        {product.interest_config.rate_card.length > 0 && (
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Segment</TableCell>
                <TableCell>Min Amount</TableCell>
                <TableCell>Max Amount</TableCell>
                <TableCell>Rate (%)</TableCell>
                <TableCell>Action</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {product.interest_config.rate_card.map((entry, index) => (
                <TableRow key={index}>
                  <TableCell>
                    <TextField
                      size="small"
                      value={entry.segment || ''}
                      onChange={(e) => updateRateCardEntry(index, 'segment', e.target.value)}
                      placeholder="e.g., Salaried"
                    />
                  </TableCell>
                  <TableCell>
                    <TextField
                      size="small"
                      type="number"
                      value={entry.min_amount || 0}
                      onChange={(e) => updateRateCardEntry(index, 'min_amount', parseFloat(e.target.value))}
                    />
                  </TableCell>
                  <TableCell>
                    <TextField
                      size="small"
                      type="number"
                      value={entry.max_amount || 0}
                      onChange={(e) => updateRateCardEntry(index, 'max_amount', parseFloat(e.target.value))}
                    />
                  </TableCell>
                  <TableCell>
                    <TextField
                      size="small"
                      type="number"
                      value={entry.rate}
                      onChange={(e) => updateRateCardEntry(index, 'rate', parseFloat(e.target.value))}
                      InputProps={{ inputProps: { step: 0.1 } }}
                    />
                  </TableCell>
                  <TableCell>
                    <IconButton
                      size="small"
                      onClick={() => removeRateCardEntry(index)}
                      color="error"
                    >
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </Grid>
      
      {product.interest_config.enable_floating_rate && (
        <Grid item xs={12}>
          <TextField
            fullWidth
            multiline
            rows={2}
            label="Rate Reset Rules"
            value={product.interest_config.rate_reset_rules || ''}
            onChange={(e) => updateNestedConfig('interest_config', 'rate_reset_rules', e.target.value)}
            helperText="Describe the rules for rate reset in floating rate products"
          />
        </Grid>
      )}
    </Grid>
  );

  const renderTenureAndAmount = () => (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Typography variant="h6" gutterBottom>Tenure Configuration</Typography>
      </Grid>
      
      <Grid item xs={12} md={4}>
        <TextField
          fullWidth
          type="number"
          label="Minimum Tenure (months)"
          value={product.tenure_config.min_tenure}
          onChange={(e) => updateNestedConfig('tenure_config', 'min_tenure', parseInt(e.target.value))}
          InputProps={{ inputProps: { min: 1 } }}
        />
      </Grid>
      
      <Grid item xs={12} md={4}>
        <TextField
          fullWidth
          type="number"
          label="Maximum Tenure (months)"
          value={product.tenure_config.max_tenure}
          onChange={(e) => updateNestedConfig('tenure_config', 'max_tenure', parseInt(e.target.value))}
          InputProps={{ inputProps: { min: 1 } }}
        />
      </Grid>
      
      <Grid item xs={12} md={4}>
        <FormControlLabel
          control={
            <Switch
              checked={product.tenure_config.tenure_based_pricing}
              onChange={(e) => updateNestedConfig('tenure_config', 'tenure_based_pricing', e.target.checked)}
            />
          }
          label="Tenure-Based Pricing"
        />
      </Grid>
      
      <Grid item xs={12}>
        <TextField
          fullWidth
          label="Allowed Tenures (comma-separated months)"
          value={product.tenure_config.allowed_tenures.join(', ')}
          onChange={(e) => {
            const tenures = e.target.value.split(',').map(t => parseInt(t.trim())).filter(t => !isNaN(t));
            updateNestedConfig('tenure_config', 'allowed_tenures', tenures);
          }}
          helperText="e.g., 12, 24, 36, 48, 60"
        />
      </Grid>
      
      <Grid item xs={12}>
        <Divider sx={{ my: 2 }} />
        <Typography variant="h6" gutterBottom>Amount Configuration</Typography>
      </Grid>
      
      <Grid item xs={12} md={4}>
        <TextField
          fullWidth
          type="number"
          label="Minimum Amount"
          value={product.amount_config.min_amount}
          onChange={(e) => updateNestedConfig('amount_config', 'min_amount', parseFloat(e.target.value))}
          InputProps={{
            startAdornment: <InputAdornment position="start">₹</InputAdornment>,
            inputProps: { min: 0 }
          }}
        />
      </Grid>
      
      <Grid item xs={12} md={4}>
        <TextField
          fullWidth
          type="number"
          label="Maximum Amount"
          value={product.amount_config.max_amount}
          onChange={(e) => updateNestedConfig('amount_config', 'max_amount', parseFloat(e.target.value))}
          InputProps={{
            startAdornment: <InputAdornment position="start">₹</InputAdornment>,
            inputProps: { min: 0 }
          }}
        />
      </Grid>
      
      <Grid item xs={12} md={4}>
        <TextField
          fullWidth
          type="number"
          label="Amount Rounding"
          value={product.amount_config.amount_rounding || ''}
          onChange={(e) => updateNestedConfig('amount_config', 'amount_rounding', parseFloat(e.target.value))}
          InputProps={{
            startAdornment: <InputAdornment position="start">₹</InputAdornment>,
          }}
          helperText="Round to nearest (e.g., 1000)"
        />
      </Grid>
      
      <Grid item xs={12} md={6}>
        <FormControlLabel
          control={
            <Switch
              checked={product.amount_config.enable_ltv}
              onChange={(e) => updateNestedConfig('amount_config', 'enable_ltv', e.target.checked)}
            />
          }
          label="Enable LTV (Loan-to-Value)"
        />
      </Grid>
      
      {product.amount_config.enable_ltv && (
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            type="number"
            label="Maximum LTV Percentage"
            value={product.amount_config.max_ltv_percentage || ''}
            onChange={(e) => updateNestedConfig('amount_config', 'max_ltv_percentage', parseFloat(e.target.value))}
            InputProps={{
              endAdornment: <InputAdornment position="end">%</InputAdornment>,
              inputProps: { min: 0, max: 100 }
            }}
          />
        </Grid>
      )}
      
      <Grid item xs={12}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="subtitle1">Amount Slabs (with Rate Adjustments)</Typography>
          <Button
            startIcon={<AddIcon />}
            onClick={addAmountSlab}
            variant="outlined"
            size="small"
          >
            Add Slab
          </Button>
        </Box>
        
        {product.amount_config.amount_slabs.length > 0 && (
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Min Amount</TableCell>
                <TableCell>Max Amount</TableCell>
                <TableCell>Rate Adjustment (%)</TableCell>
                <TableCell>Action</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {product.amount_config.amount_slabs.map((slab, index) => (
                <TableRow key={index}>
                  <TableCell>
                    <TextField
                      size="small"
                      type="number"
                      value={slab.min}
                      onChange={(e) => updateAmountSlab(index, 'min', parseFloat(e.target.value))}
                      InputProps={{ startAdornment: <InputAdornment position="start">₹</InputAdornment> }}
                    />
                  </TableCell>
                  <TableCell>
                    <TextField
                      size="small"
                      type="number"
                      value={slab.max}
                      onChange={(e) => updateAmountSlab(index, 'max', parseFloat(e.target.value))}
                      InputProps={{ startAdornment: <InputAdornment position="start">₹</InputAdornment> }}
                    />
                  </TableCell>
                  <TableCell>
                    <TextField
                      size="small"
                      type="number"
                      value={slab.rate_adjustment || 0}
                      onChange={(e) => updateAmountSlab(index, 'rate_adjustment', parseFloat(e.target.value))}
                      InputProps={{ inputProps: { step: 0.1 } }}
                    />
                  </TableCell>
                  <TableCell>
                    <IconButton
                      size="small"
                      onClick={() => removeAmountSlab(index)}
                      color="error"
                    >
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </Grid>
    </Grid>
  );

  const renderFeeChargeConfig = (feeName: string, label: string) => {
    const feeConfig = (product.fees_config as any)[feeName] || {
      charge_type: 'FLAT',
      gst_applicable: true,
      waivable: false,
    };
    
    return (
      <Accordion key={feeName}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography>{label}</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Grid container spacing={2}>
            <Grid item xs={12} md={4}>
              <FormControl fullWidth size="small">
                <InputLabel>Charge Type</InputLabel>
                <Select
                  value={feeConfig.charge_type}
                  onChange={(e) => updateFeeCharge(feeName, 'charge_type', e.target.value)}
                  label="Charge Type"
                >
                  {chargeTypes.map((type) => (
                    <MenuItem key={type} value={type}>{type.replace(/_/g, ' ')}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            {feeConfig.charge_type === 'FLAT' && (
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  size="small"
                  type="number"
                  label="Flat Amount"
                  value={feeConfig.flat_amount || ''}
                  onChange={(e) => updateFeeCharge(feeName, 'flat_amount', parseFloat(e.target.value))}
                  InputProps={{ startAdornment: <InputAdornment position="start">₹</InputAdornment> }}
                />
              </Grid>
            )}
            
            {feeConfig.charge_type === 'PERCENTAGE' && (
              <>
                <Grid item xs={12} md={4}>
                  <TextField
                    fullWidth
                    size="small"
                    type="number"
                    label="Percentage"
                    value={feeConfig.percentage || ''}
                    onChange={(e) => updateFeeCharge(feeName, 'percentage', parseFloat(e.target.value))}
                    InputProps={{ endAdornment: <InputAdornment position="end">%</InputAdornment> }}
                  />
                </Grid>
                <Grid item xs={12} md={4}>
                  <TextField
                    fullWidth
                    size="small"
                    type="number"
                    label="Min Amount"
                    value={feeConfig.min_amount || ''}
                    onChange={(e) => updateFeeCharge(feeName, 'min_amount', parseFloat(e.target.value))}
                    InputProps={{ startAdornment: <InputAdornment position="start">₹</InputAdornment> }}
                  />
                </Grid>
                <Grid item xs={12} md={4}>
                  <TextField
                    fullWidth
                    size="small"
                    type="number"
                    label="Max Amount"
                    value={feeConfig.max_amount || ''}
                    onChange={(e) => updateFeeCharge(feeName, 'max_amount', parseFloat(e.target.value))}
                    InputProps={{ startAdornment: <InputAdornment position="start">₹</InputAdornment> }}
                  />
                </Grid>
              </>
            )}
            
            <Grid item xs={12} md={6}>
              <FormControlLabel
                control={
                  <Switch
                    checked={feeConfig.gst_applicable}
                    onChange={(e) => updateFeeCharge(feeName, 'gst_applicable', e.target.checked)}
                  />
                }
                label="GST Applicable"
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <FormControlLabel
                control={
                  <Switch
                    checked={feeConfig.waivable}
                    onChange={(e) => updateFeeCharge(feeName, 'waivable', e.target.checked)}
                  />
                }
                label="Waivable"
              />
            </Grid>
          </Grid>
        </AccordionDetails>
      </Accordion>
    );
  };

  const renderFeesAndCharges = () => {
    const fees = [
      { name: 'processing_fee', label: 'Processing Fee' },
      { name: 'documentation_charges', label: 'Documentation Charges' },
      { name: 'valuation_charges', label: 'Valuation Charges' },
      { name: 'legal_charges', label: 'Legal Charges' },
      { name: 'stamp_duty', label: 'Stamp Duty' },
      { name: 'prepayment_charges', label: 'Prepayment Charges' },
      { name: 'penal_charges', label: 'Penal Charges' },
      { name: 'bounce_charges', label: 'Bounce Charges' },
      { name: 'late_payment_charges', label: 'Late Payment Charges' },
      { name: 'foreclosure_charges', label: 'Foreclosure Charges' },
      { name: 'part_payment_charges', label: 'Part Payment Charges' },
    ];
    
    return (
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Typography variant="h6" gutterBottom>Fees & Charges Configuration</Typography>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Configure various fees and charges for this product. Expand each section to set the charge type and amount.
          </Typography>
        </Grid>
        
        <Grid item xs={12}>
          {fees.map(({ name, label }) => renderFeeChargeConfig(name, label))}
        </Grid>
      </Grid>
    );
  };

  const renderEMIConfiguration = () => (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Typography variant="h6" gutterBottom>EMI Configuration</Typography>
      </Grid>
      
      <Grid item xs={12} md={6}>
        <FormControl fullWidth>
          <InputLabel>EMI Type</InputLabel>
          <Select
            value={product.emi_config.emi_type}
            onChange={(e) => updateNestedConfig('emi_config', 'emi_type', e.target.value)}
            label="EMI Type"
          >
            {emiTypes.map((type) => (
              <MenuItem key={type} value={type}>{type.replace(/_/g, ' ')}</MenuItem>
            ))}
          </Select>
        </FormControl>
      </Grid>
      
      <Grid item xs={12} md={6}>
        <FormControl fullWidth>
          <InputLabel>EMI Start Date Option</InputLabel>
          <Select
            value={product.emi_config.emi_start_date_option}
            onChange={(e) => updateNestedConfig('emi_config', 'emi_start_date_option', e.target.value)}
            label="EMI Start Date Option"
          >
            {emiStartOptions.map((option) => (
              <MenuItem key={option} value={option}>{option.replace(/_/g, ' ')}</MenuItem>
            ))}
          </Select>
        </FormControl>
      </Grid>
      
      <Grid item xs={12} md={4}>
        <TextField
          fullWidth
          type="number"
          label="Grace Period (months)"
          value={product.emi_config.grace_period_months || ''}
          onChange={(e) => updateNestedConfig('emi_config', 'grace_period_months', parseInt(e.target.value))}
          InputProps={{ inputProps: { min: 0 } }}
        />
      </Grid>
      
      <Grid item xs={12} md={4}>
        <TextField
          fullWidth
          type="number"
          label="Moratorium Period (months)"
          value={product.emi_config.moratorium_period_months || ''}
          onChange={(e) => updateNestedConfig('emi_config', 'moratorium_period_months', parseInt(e.target.value))}
          InputProps={{ inputProps: { min: 0 } }}
        />
      </Grid>
      
      <Grid item xs={12} md={4}>
        <TextField
          fullWidth
          type="number"
          label="EMI Rounding"
          value={product.emi_config.emi_rounding || ''}
          onChange={(e) => updateNestedConfig('emi_config', 'emi_rounding', parseFloat(e.target.value))}
          InputProps={{
            startAdornment: <InputAdornment position="start">₹</InputAdornment>,
          }}
          helperText="Round EMI to nearest (e.g., 10)"
        />
      </Grid>
      
      <Grid item xs={12}>
        <Divider sx={{ my: 2 }} />
        <Typography variant="subtitle1" gutterBottom>Payment Options</Typography>
      </Grid>
      
      <Grid item xs={12} md={6}>
        <FormControlLabel
          control={
            <Switch
              checked={product.emi_config.enable_bullet_payment}
              onChange={(e) => updateNestedConfig('emi_config', 'enable_bullet_payment', e.target.checked)}
            />
          }
          label="Enable Bullet Payment"
        />
      </Grid>
      
      <Grid item xs={12} md={6}>
        <FormControlLabel
          control={
            <Switch
              checked={product.emi_config.enable_balloon_payment}
              onChange={(e) => updateNestedConfig('emi_config', 'enable_balloon_payment', e.target.checked)}
            />
          }
          label="Enable Balloon Payment"
        />
      </Grid>
      
      {product.emi_config.enable_balloon_payment && (
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            type="number"
            label="Balloon Payment Percentage"
            value={product.emi_config.balloon_payment_percentage || ''}
            onChange={(e) => updateNestedConfig('emi_config', 'balloon_payment_percentage', parseFloat(e.target.value))}
            InputProps={{ endAdornment: <InputAdornment position="end">%</InputAdornment> }}
          />
        </Grid>
      )}
      
      <Grid item xs={12} md={6}>
        <FormControlLabel
          control={
            <Switch
              checked={product.emi_config.enable_prepayment}
              onChange={(e) => updateNestedConfig('emi_config', 'enable_prepayment', e.target.checked)}
            />
          }
          label="Enable Prepayment"
        />
      </Grid>
      
      <Grid item xs={12} md={6}>
        <FormControlLabel
          control={
            <Switch
              checked={product.emi_config.enable_part_payment}
              onChange={(e) => updateNestedConfig('emi_config', 'enable_part_payment', e.target.checked)}
            />
          }
          label="Enable Part Payment"
        />
      </Grid>
      
      <Grid item xs={12}>
        <Divider sx={{ my: 2 }} />
        <Typography variant="subtitle1" gutterBottom>Step EMI Options</Typography>
      </Grid>
      
      <Grid item xs={12} md={6}>
        <FormControlLabel
          control={
            <Switch
              checked={product.emi_config.enable_step_emi}
              onChange={(e) => updateNestedConfig('emi_config', 'enable_step_emi', e.target.checked)}
            />
          }
          label="Enable Step EMI"
        />
      </Grid>
      
      {product.emi_config.enable_step_emi && (
        <>
          {product.emi_config.emi_type === 'STEP_UP' && (
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                type="number"
                label="Step Up Percentage"
                value={product.emi_config.step_up_percentage || ''}
                onChange={(e) => updateNestedConfig('emi_config', 'step_up_percentage', parseFloat(e.target.value))}
                InputProps={{ endAdornment: <InputAdornment position="end">%</InputAdornment> }}
              />
            </Grid>
          )}
          
          {product.emi_config.emi_type === 'STEP_DOWN' && (
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                type="number"
                label="Step Down Percentage"
                value={product.emi_config.step_down_percentage || ''}
                onChange={(e) => updateNestedConfig('emi_config', 'step_down_percentage', parseFloat(e.target.value))}
                InputProps={{ endAdornment: <InputAdornment position="end">%</InputAdornment> }}
              />
            </Grid>
          )}
        </>
      )}
    </Grid>
  );

  const renderReviewAndSave = () => (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Typography variant="h6" gutterBottom>Review Product Configuration</Typography>
        <Alert severity="info" sx={{ mb: 2 }}>
          Please review all the details before saving the product configuration.
        </Alert>
      </Grid>
      
      <Grid item xs={12}>
        <Paper sx={{ p: 2 }}>
          <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 600 }}>Basic Information</Typography>
          <Grid container spacing={1}>
            <Grid item xs={6}><Typography variant="body2" color="text.secondary">Product Code:</Typography></Grid>
            <Grid item xs={6}><Typography variant="body2">{product.product_code}</Typography></Grid>
            
            <Grid item xs={6}><Typography variant="body2" color="text.secondary">Product Name:</Typography></Grid>
            <Grid item xs={6}><Typography variant="body2">{product.product_name}</Typography></Grid>
            
            <Grid item xs={6}><Typography variant="body2" color="text.secondary">Category:</Typography></Grid>
            <Grid item xs={6}><Chip label={product.category} size="small" /></Grid>
            
            <Grid item xs={6}><Typography variant="body2" color="text.secondary">Status:</Typography></Grid>
            <Grid item xs={6}><Chip label={product.status} size="small" color="primary" /></Grid>
            
            <Grid item xs={6}><Typography variant="body2" color="text.secondary">Effective Date:</Typography></Grid>
            <Grid item xs={6}><Typography variant="body2">{product.effective_date}</Typography></Grid>
          </Grid>
        </Paper>
      </Grid>
      
      <Grid item xs={12}>
        <Paper sx={{ p: 2 }}>
          <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 600 }}>Interest Configuration</Typography>
          <Grid container spacing={1}>
            <Grid item xs={6}><Typography variant="body2" color="text.secondary">Calculation Method:</Typography></Grid>
            <Grid item xs={6}><Typography variant="body2">{product.interest_config.calculation_method}</Typography></Grid>
            
            <Grid item xs={6}><Typography variant="body2" color="text.secondary">Base Rate:</Typography></Grid>
            <Grid item xs={6}><Typography variant="body2">{product.interest_config.base_rate}%</Typography></Grid>
            
            <Grid item xs={6}><Typography variant="body2" color="text.secondary">Rate Type:</Typography></Grid>
            <Grid item xs={6}><Typography variant="body2">{product.interest_config.rate_type}</Typography></Grid>
            
            <Grid item xs={6}><Typography variant="body2" color="text.secondary">Rate Card Entries:</Typography></Grid>
            <Grid item xs={6}><Typography variant="body2">{product.interest_config.rate_card.length} entries</Typography></Grid>
          </Grid>
        </Paper>
      </Grid>
      
      <Grid item xs={12}>
        <Paper sx={{ p: 2 }}>
          <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 600 }}>Tenure & Amount</Typography>
          <Grid container spacing={1}>
            <Grid item xs={6}><Typography variant="body2" color="text.secondary">Tenure Range:</Typography></Grid>
            <Grid item xs={6}><Typography variant="body2">{product.tenure_config.min_tenure} - {product.tenure_config.max_tenure} months</Typography></Grid>
            
            <Grid item xs={6}><Typography variant="body2" color="text.secondary">Amount Range:</Typography></Grid>
            <Grid item xs={6}><Typography variant="body2">₹{product.amount_config.min_amount.toLocaleString()} - ₹{product.amount_config.max_amount.toLocaleString()}</Typography></Grid>
            
            <Grid item xs={6}><Typography variant="body2" color="text.secondary">LTV Enabled:</Typography></Grid>
            <Grid item xs={6}><Typography variant="body2">{product.amount_config.enable_ltv ? 'Yes' : 'No'}</Typography></Grid>
          </Grid>
        </Paper>
      </Grid>
      
      <Grid item xs={12}>
        <Paper sx={{ p: 2 }}>
          <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 600 }}>EMI Configuration</Typography>
          <Grid container spacing={1}>
            <Grid item xs={6}><Typography variant="body2" color="text.secondary">EMI Type:</Typography></Grid>
            <Grid item xs={6}><Typography variant="body2">{product.emi_config.emi_type}</Typography></Grid>
            
            <Grid item xs={6}><Typography variant="body2" color="text.secondary">Start Date Option:</Typography></Grid>
            <Grid item xs={6}><Typography variant="body2">{product.emi_config.emi_start_date_option}</Typography></Grid>
            
            <Grid item xs={6}><Typography variant="body2" color="text.secondary">Prepayment:</Typography></Grid>
            <Grid item xs={6}><Typography variant="body2">{product.emi_config.enable_prepayment ? 'Allowed' : 'Not Allowed'}</Typography></Grid>
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
        return renderInterestConfiguration();
      case 2:
        return renderTenureAndAmount();
      case 3:
        return renderFeesAndCharges();
      case 4:
        return renderEMIConfiguration();
      case 5:
        return renderReviewAndSave();
      default:
        return 'Unknown step';
    }
  };

  return (
    <Box sx={{ width: '100%' }}>
      <Paper sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          {productId ? 'Edit Product' : 'Create New Product'}
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
                {loading ? 'Saving...' : productId ? 'Update Product' : 'Create Product'}
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

export default ProductBuilder;
