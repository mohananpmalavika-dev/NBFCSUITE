/**
 * Score-Based Rates Step
 * Configure credit score tiers and associated rates
 */
import React from 'react';
import {
  Box,
  Grid,
  TextField,
  Typography,
  Card,
  CardContent,
  Button,
  IconButton,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  InputAdornment,
  Chip
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon
} from '@mui/icons-material';
import { ScoreBasedRate, PricingTier } from '@/services/creditPolicyService';

interface ScoreRatesStepProps {
  data: ScoreBasedRate[];
  onChange: (data: ScoreBasedRate[]) => void;
}

const defaultRate: Partial<ScoreBasedRate> = {
  min_score: 0,
  max_score: 0,
  pricing_tier: PricingTier.SUB_PRIME,
  base_rate: 12.0,
  rate_adjustment: 0.0,
  processing_fee_percent: 1.5,
  risk_premium_percent: 0.5,
  priority: 0
};

const ScoreRatesStep: React.FC<ScoreRatesStepProps> = ({ data, onChange }) => {
  const handleAdd = () => {
    onChange([...data, { ...defaultRate } as ScoreBasedRate]);
  };

  const handleRemove = (index: number) => {
    const newData = data.filter((_, i) => i !== index);
    onChange(newData);
  };

  const handleChange = (index: number, field: keyof ScoreBasedRate) => (
    event: React.ChangeEvent<HTMLInputElement | { value: unknown }>
  ) => {
    const newData = [...data];
    const value = event.target.type === 'number' 
      ? parseFloat(event.target.value as string)
      : event.target.value;
    
    newData[index] = {
      ...newData[index],
      [field]: value
    };
    onChange(newData);
  };

  const getTierColor = (tier: PricingTier) => {
    switch (tier) {
      case PricingTier.PRIME:
        return 'success';
      case PricingTier.NEAR_PRIME:
        return 'info';
      case PricingTier.SUB_PRIME:
        return 'warning';
      case PricingTier.HIGH_RISK:
        return 'error';
      default:
        return 'default';
    }
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h6">
            Score-Based Rate Tiers
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Define interest rates for different credit score ranges
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleAdd}
        >
          Add Tier
        </Button>
      </Box>

      {data.length === 0 ? (
        <Card>
          <CardContent>
            <Typography variant="body1" color="text.secondary" align="center" py={4}>
              No rate tiers defined. Click "Add Tier" to create your first tier.
            </Typography>
          </CardContent>
        </Card>
      ) : (
        <Grid container spacing={2}>
          {data.map((rate, index) => (
            <Grid item xs={12} key={index}>
              <Card>
                <CardContent>
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                    <Box display="flex" alignItems="center" gap={1}>
                      <Typography variant="subtitle1" fontWeight="bold">
                        Tier {index + 1}
                      </Typography>
                      <Chip 
                        label={rate.pricing_tier} 
                        color={getTierColor(rate.pricing_tier)}
                        size="small"
                      />
                    </Box>
                    <IconButton
                      color="error"
                      onClick={() => handleRemove(index)}
                      size="small"
                    >
                      <DeleteIcon />
                    </IconButton>
                  </Box>

                  <Grid container spacing={2}>
                    {/* Score Range */}
                    <Grid item xs={12} md={3}>
                      <TextField
                        fullWidth
                        required
                        type="number"
                        label="Min Score"
                        value={rate.min_score}
                        onChange={handleChange(index, 'min_score')}
                        InputProps={{
                          inputProps: { min: 300, max: 900 }
                        }}
                      />
                    </Grid>

                    <Grid item xs={12} md={3}>
                      <TextField
                        fullWidth
                        required
                        type="number"
                        label="Max Score"
                        value={rate.max_score}
                        onChange={handleChange(index, 'max_score')}
                        InputProps={{
                          inputProps: { min: 300, max: 900 }
                        }}
                      />
                    </Grid>

                    {/* Pricing Tier */}
                    <Grid item xs={12} md={6}>
                      <FormControl fullWidth required>
                        <InputLabel>Pricing Tier</InputLabel>
                        <Select
                          value={rate.pricing_tier}
                          onChange={handleChange(index, 'pricing_tier')}
                          label="Pricing Tier"
                        >
                          <MenuItem value={PricingTier.PRIME}>PRIME</MenuItem>
                          <MenuItem value={PricingTier.NEAR_PRIME}>NEAR PRIME</MenuItem>
                          <MenuItem value={PricingTier.SUB_PRIME}>SUB PRIME</MenuItem>
                          <MenuItem value={PricingTier.HIGH_RISK}>HIGH RISK</MenuItem>
                        </Select>
                      </FormControl>
                    </Grid>

                    {/* Rates */}
                    <Grid item xs={12} md={3}>
                      <TextField
                        fullWidth
                        required
                        type="number"
                        label="Base Rate"
                        value={rate.base_rate}
                        onChange={handleChange(index, 'base_rate')}
                        InputProps={{
                          endAdornment: <InputAdornment position="end">%</InputAdornment>,
                          inputProps: { step: 0.25, min: 0, max: 30 }
                        }}
                      />
                    </Grid>

                    <Grid item xs={12} md={3}>
                      <TextField
                        fullWidth
                        type="number"
                        label="Rate Adjustment"
                        value={rate.rate_adjustment}
                        onChange={handleChange(index, 'rate_adjustment')}
                        InputProps={{
                          endAdornment: <InputAdornment position="end">%</InputAdornment>,
                          inputProps: { step: 0.25, min: -5, max: 5 }
                        }}
                        helperText="Additional adjustment"
                      />
                    </Grid>

                    {/* Fees */}
                    <Grid item xs={12} md={3}>
                      <TextField
                        fullWidth
                        type="number"
                        label="Processing Fee"
                        value={rate.processing_fee_percent}
                        onChange={handleChange(index, 'processing_fee_percent')}
                        InputProps={{
                          endAdornment: <InputAdornment position="end">%</InputAdornment>,
                          inputProps: { step: 0.25, min: 0, max: 10 }
                        }}
                      />
                    </Grid>

                    <Grid item xs={12} md={3}>
                      <TextField
                        fullWidth
                        type="number"
                        label="Risk Premium"
                        value={rate.risk_premium_percent}
                        onChange={handleChange(index, 'risk_premium_percent')}
                        InputProps={{
                          endAdornment: <InputAdornment position="end">%</InputAdornment>,
                          inputProps: { step: 0.25, min: 0, max: 10 }
                        }}
                      />
                    </Grid>

                    {/* Limits */}
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        type="number"
                        label="Max Loan Amount"
                        value={rate.max_loan_amount || ''}
                        onChange={handleChange(index, 'max_loan_amount')}
                        InputProps={{
                          startAdornment: <InputAdornment position="start">₹</InputAdornment>,
                          inputProps: { step: 100000, min: 0 }
                        }}
                        helperText="Leave empty for no limit"
                      />
                    </Grid>

                    <Grid item xs={12} md={3}>
                      <TextField
                        fullWidth
                        type="number"
                        label="Max LTV Ratio"
                        value={rate.max_ltv_ratio || ''}
                        onChange={handleChange(index, 'max_ltv_ratio')}
                        InputProps={{
                          endAdornment: <InputAdornment position="end">%</InputAdornment>,
                          inputProps: { step: 5, min: 0, max: 100 }
                        }}
                        helperText="Optional"
                      />
                    </Grid>

                    <Grid item xs={12} md={3}>
                      <TextField
                        fullWidth
                        required
                        type="number"
                        label="Priority"
                        value={rate.priority}
                        onChange={handleChange(index, 'priority')}
                        InputProps={{
                          inputProps: { min: 0, max: 100 }
                        }}
                        helperText="Higher = more priority"
                      />
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {data.length > 0 && (
        <Box mt={3}>
          <Typography variant="body2" color="text.secondary">
            💡 Tip: Configure tiers from highest to lowest credit scores for best coverage. 
            Higher priority tiers are evaluated first when score ranges overlap.
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default ScoreRatesStep;
