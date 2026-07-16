/**
 * Risk Pricing Configuration Step
 * Base rates, weight distribution, fee ranges
 */
import React from 'react';
import {
  Box,
  Grid,
  TextField,
  Typography,
  Card,
  CardContent,
  Divider,
  Slider,
  InputAdornment
} from '@mui/material';
import { RiskBasedPricing } from '@/services/creditPolicy.service';

interface RiskPricingStepProps {
  data: Partial<RiskBasedPricing>;
  onChange: (data: Partial<RiskBasedPricing>) => void;
}

const RiskPricingStep: React.FC<RiskPricingStepProps> = ({ data, onChange }) => {
  const handleChange = (field: keyof RiskBasedPricing) => (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const value = event.target.type === 'number' 
      ? parseFloat(event.target.value) 
      : event.target.value;
    
    onChange({
      ...data,
      [field]: value
    });
  };

  const handleWeightChange = (field: keyof RiskBasedPricing) => (
    event: Event, value: number | number[]
  ) => {
    onChange({
      ...data,
      [field]: (value as number) / 100
    });
  };

  const handleRangeChange = (field: 'processing_fee_range' | 'risk_premium_range', key: 'min' | 'max') => (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    onChange({
      ...data,
      [field]: {
        ...((data[field] as any) || {}),
        [key]: parseFloat(event.target.value)
      }
    });
  };

  const totalWeight = (
    (data.credit_score_weight || 0) +
    (data.ltv_weight || 0) +
    (data.dti_weight || 0) +
    (data.other_factors_weight || 0)
  ) * 100;

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Risk-Based Pricing Configuration
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Configure base rates and risk factor weights
      </Typography>

      {/* Base Rates */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="subtitle1" gutterBottom fontWeight="bold">
            Interest Rate Configuration
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <TextField
                required
                fullWidth
                type="number"
                label="Base Interest Rate"
                value={data.base_interest_rate || ''}
                onChange={handleChange('base_interest_rate')}
                InputProps={{
                  endAdornment: <InputAdornment position="end">%</InputAdornment>,
                  inputProps: { step: 0.25, min: 0, max: 30 }
                }}
                helperText="Starting point for rate calculation"
              />
            </Grid>

            <Grid item xs={12} md={4}>
              <TextField
                required
                fullWidth
                type="number"
                label="Minimum Interest Rate"
                value={data.min_interest_rate || ''}
                onChange={handleChange('min_interest_rate')}
                InputProps={{
                  endAdornment: <InputAdornment position="end">%</InputAdornment>,
                  inputProps: { step: 0.25, min: 0, max: 30 }
                }}
                helperText="Lowest rate possible"
              />
            </Grid>

            <Grid item xs={12} md={4}>
              <TextField
                required
                fullWidth
                type="number"
                label="Maximum Interest Rate"
                value={data.max_interest_rate || ''}
                onChange={handleChange('max_interest_rate')}
                InputProps={{
                  endAdornment: <InputAdornment position="end">%</InputAdornment>,
                  inputProps: { step: 0.25, min: 0, max: 30 }
                }}
                helperText="Highest rate possible"
              />
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Risk Factor Weights */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="subtitle1" gutterBottom fontWeight="bold">
            Risk Factor Weights
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Adjust the importance of each risk factor in rate calculation. Total should equal 100%.
          </Typography>

          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography gutterBottom>
                Credit Score Weight: {((data.credit_score_weight || 0) * 100).toFixed(0)}%
              </Typography>
              <Slider
                value={(data.credit_score_weight || 0) * 100}
                onChange={handleWeightChange('credit_score_weight')}
                min={0}
                max={100}
                step={5}
                marks
                valueLabelDisplay="auto"
              />
            </Grid>

            <Grid item xs={12}>
              <Typography gutterBottom>
                LTV Weight: {((data.ltv_weight || 0) * 100).toFixed(0)}%
              </Typography>
              <Slider
                value={(data.ltv_weight || 0) * 100}
                onChange={handleWeightChange('ltv_weight')}
                min={0}
                max={100}
                step={5}
                marks
                valueLabelDisplay="auto"
              />
            </Grid>

            <Grid item xs={12}>
              <Typography gutterBottom>
                DTI Weight: {((data.dti_weight || 0) * 100).toFixed(0)}%
              </Typography>
              <Slider
                value={(data.dti_weight || 0) * 100}
                onChange={handleWeightChange('dti_weight')}
                min={0}
                max={100}
                step={5}
                marks
                valueLabelDisplay="auto"
              />
            </Grid>

            <Grid item xs={12}>
              <Typography gutterBottom>
                Other Factors Weight: {((data.other_factors_weight || 0) * 100).toFixed(0)}%
              </Typography>
              <Slider
                value={(data.other_factors_weight || 0) * 100}
                onChange={handleWeightChange('other_factors_weight')}
                min={0}
                max={100}
                step={5}
                marks
                valueLabelDisplay="auto"
              />
            </Grid>

            <Grid item xs={12}>
              <Divider />
              <Typography 
                variant="body1" 
                sx={{ mt: 2 }}
                color={totalWeight === 100 ? 'success.main' : 'error.main'}
              >
                Total Weight: {totalWeight.toFixed(0)}% {totalWeight !== 100 && '(Should be 100%)'}
              </Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Fee Ranges */}
      <Card>
        <CardContent>
          <Typography variant="subtitle1" gutterBottom fontWeight="bold">
            Fee Ranges
          </Typography>
          
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Typography variant="body2" gutterBottom>
                Processing Fee Range
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    type="number"
                    label="Minimum"
                    value={data.processing_fee_range?.min || ''}
                    onChange={handleRangeChange('processing_fee_range', 'min')}
                    InputProps={{
                      endAdornment: <InputAdornment position="end">%</InputAdornment>,
                      inputProps: { step: 0.25, min: 0, max: 10 }
                    }}
                  />
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    type="number"
                    label="Maximum"
                    value={data.processing_fee_range?.max || ''}
                    onChange={handleRangeChange('processing_fee_range', 'max')}
                    InputProps={{
                      endAdornment: <InputAdornment position="end">%</InputAdornment>,
                      inputProps: { step: 0.25, min: 0, max: 10 }
                    }}
                  />
                </Grid>
              </Grid>
            </Grid>

            <Grid item xs={12} md={6}>
              <Typography variant="body2" gutterBottom>
                Risk Premium Range
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    type="number"
                    label="Minimum"
                    value={data.risk_premium_range?.min || ''}
                    onChange={handleRangeChange('risk_premium_range', 'min')}
                    InputProps={{
                      endAdornment: <InputAdornment position="end">%</InputAdornment>,
                      inputProps: { step: 0.25, min: 0, max: 10 }
                    }}
                  />
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    type="number"
                    label="Maximum"
                    value={data.risk_premium_range?.max || ''}
                    onChange={handleRangeChange('risk_premium_range', 'max')}
                    InputProps={{
                      endAdornment: <InputAdornment position="end">%</InputAdornment>,
                      inputProps: { step: 0.25, min: 0, max: 10 }
                    }}
                  />
                </Grid>
              </Grid>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    </Box>
  );
};

export default RiskPricingStep;
