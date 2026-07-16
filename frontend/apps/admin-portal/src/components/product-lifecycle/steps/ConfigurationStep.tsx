/**
 * Configuration Step - Variant Builder
 * Configuration overrides for rates, tenure, amount, fees
 */
import React from 'react';
import {
  Grid,
  TextField,
  Typography,
  Box,
  Divider
} from '@mui/material';
import { ProductVariantCreate } from '@/services/productLifecycle.service';

interface ConfigurationStepProps {
  data: Partial<ProductVariantCreate>;
  onChange: (data: Partial<ProductVariantCreate>) => void;
}

const ConfigurationStep: React.FC<ConfigurationStepProps> = ({
  data,
  onChange
}) => {
  const handleRateChange = (field: string, value: string) => {
    const numValue = value ? parseFloat(value) : undefined;
    onChange({
      interest_rate_override: {
        ...data.interest_rate_override,
        [field]: numValue
      }
    });
  };

  const handleTenureChange = (field: string, value: string) => {
    const numValue = value ? parseInt(value) : undefined;
    onChange({
      tenure_override: {
        ...data.tenure_override,
        [field]: numValue
      }
    });
  };

  const handleAmountChange = (field: string, value: string) => {
    const numValue = value ? parseFloat(value) : undefined;
    onChange({
      amount_override: {
        ...data.amount_override,
        [field]: numValue
      }
    });
  };

  const handleFeeChange = (field: string, value: string) => {
    const numValue = value ? parseFloat(value) : undefined;
    onChange({
      fee_override: {
        ...data.fee_override,
        [field]: numValue
      }
    });
  };

  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Typography variant="h6" gutterBottom>
          Configuration Overrides
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          Override base product configuration (leave blank to use defaults)
        </Typography>
      </Grid>

      {/* Interest Rate Override */}
      <Grid item xs={12}>
        <Typography variant="subtitle1" gutterBottom>
          Interest Rate Override
        </Typography>
      </Grid>

      <Grid item xs={12} md={4}>
        <TextField
          fullWidth
          type="number"
          label="Base Rate (%)"
          value={data.interest_rate_override?.base || ''}
          onChange={(e) => handleRateChange('base', e.target.value)}
          inputProps={{ step: 0.01, min: 0 }}
        />
      </Grid>

      <Grid item xs={12} md={4}>
        <TextField
          fullWidth
          type="number"
          label="Minimum Rate (%)"
          value={data.interest_rate_override?.min || ''}
          onChange={(e) => handleRateChange('min', e.target.value)}
          inputProps={{ step: 0.01, min: 0 }}
        />
      </Grid>

      <Grid item xs={12} md={4}>
        <TextField
          fullWidth
          type="number"
          label="Maximum Rate (%)"
          value={data.interest_rate_override?.max || ''}
          onChange={(e) => handleRateChange('max', e.target.value)}
          inputProps={{ step: 0.01, min: 0 }}
        />
      </Grid>

      <Grid item xs={12}>
        <Divider sx={{ my: 2 }} />
      </Grid>

      {/* Tenure Override */}
      <Grid item xs={12}>
        <Typography variant="subtitle1" gutterBottom>
          Tenure Override (Months)
        </Typography>
      </Grid>

      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          type="number"
          label="Minimum Tenure"
          value={data.tenure_override?.min || ''}
          onChange={(e) => handleTenureChange('min', e.target.value)}
          inputProps={{ step: 1, min: 1 }}
        />
      </Grid>

      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          type="number"
          label="Maximum Tenure"
          value={data.tenure_override?.max || ''}
          onChange={(e) => handleTenureChange('max', e.target.value)}
          inputProps={{ step: 1, min: 1 }}
        />
      </Grid>

      <Grid item xs={12}>
        <Divider sx={{ my: 2 }} />
      </Grid>

      {/* Amount Override */}
      <Grid item xs={12}>
        <Typography variant="subtitle1" gutterBottom>
          Loan Amount Override (₹)
        </Typography>
      </Grid>

      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          type="number"
          label="Minimum Amount"
          value={data.amount_override?.min || ''}
          onChange={(e) => handleAmountChange('min', e.target.value)}
          inputProps={{ step: 1000, min: 0 }}
        />
      </Grid>

      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          type="number"
          label="Maximum Amount"
          value={data.amount_override?.max || ''}
          onChange={(e) => handleAmountChange('max', e.target.value)}
          inputProps={{ step: 1000, min: 0 }}
        />
      </Grid>

      <Grid item xs={12}>
        <Divider sx={{ my: 2 }} />
      </Grid>

      {/* Fee Override */}
      <Grid item xs={12}>
        <Typography variant="subtitle1" gutterBottom>
          Fee Override (%)
        </Typography>
      </Grid>

      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          type="number"
          label="Processing Fee (%)"
          value={data.fee_override?.processing_fee || ''}
          onChange={(e) => handleFeeChange('processing_fee', e.target.value)}
          inputProps={{ step: 0.1, min: 0 }}
        />
      </Grid>

      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          type="number"
          label="Prepayment Fee (%)"
          value={data.fee_override?.prepayment_fee || ''}
          onChange={(e) => handleFeeChange('prepayment_fee', e.target.value)}
          inputProps={{ step: 0.1, min: 0 }}
        />
      </Grid>

      <Grid item xs={12}>
        <Box sx={{ mt: 2, p: 2, bgcolor: 'info.lighter', borderRadius: 1 }}>
          <Typography variant="body2" color="info.main">
            💡 Tip: Leave fields blank to use the base product's default values
          </Typography>
        </Box>
      </Grid>
    </Grid>
  );
};

export default ConfigurationStep;
