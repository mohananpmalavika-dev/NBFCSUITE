/**
 * Marketing Step - Variant Builder
 * Marketing content and customer-facing information
 */
import React from 'react';
import {
  Grid,
  TextField,
  Typography
} from '@mui/material';
import { ProductVariantCreate } from '@/services/productLifecycle.service';

interface MarketingStepProps {
  data: Partial<ProductVariantCreate>;
  onChange: (data: Partial<ProductVariantCreate>) => void;
}

const MarketingStep: React.FC<MarketingStepProps> = ({
  data,
  onChange
}) => {
  const handleChange = (field: keyof ProductVariantCreate, value: any) => {
    onChange({ [field]: value });
  };

  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Typography variant="h6" gutterBottom>
          Marketing Content
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          Customer-facing content for this variant (optional)
        </Typography>
      </Grid>

      <Grid item xs={12}>
        <TextField
          fullWidth
          label="Marketing Name"
          value={data.marketing_name || ''}
          onChange={(e) => handleChange('marketing_name', e.target.value)}
          helperText="Customer-facing name (if different from variant name)"
        />
      </Grid>

      <Grid item xs={12}>
        <TextField
          fullWidth
          label="Tagline"
          value={data.tagline || ''}
          onChange={(e) => handleChange('tagline', e.target.value)}
          helperText="Short catchy tagline (e.g., 'Festival Special - Limited Time Offer!')"
          inputProps={{ maxLength: 100 }}
        />
      </Grid>

      <Grid item xs={12}>
        <TextField
          fullWidth
          multiline
          rows={4}
          label="Promotional Message"
          value={data.promotional_message || ''}
          onChange={(e) => handleChange('promotional_message', e.target.value)}
          helperText="Detailed promotional message for customers"
        />
      </Grid>

      <Grid item xs={12}>
        <TextField
          fullWidth
          multiline
          rows={6}
          label="Terms and Conditions"
          value={data.terms_and_conditions || ''}
          onChange={(e) => handleChange('terms_and_conditions', e.target.value)}
          helperText="Terms and conditions specific to this variant"
        />
      </Grid>
    </Grid>
  );
};

export default MarketingStep;
