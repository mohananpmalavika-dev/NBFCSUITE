/**
 * Basic Info Step - Variant Builder
 * Core variant information
 */
import React from 'react';
import {
  Grid,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Typography
} from '@mui/material';
import {
  ProductVariantCreate,
  VariantType
} from '@/services/productLifecycle.service';

interface BasicInfoStepProps {
  data: Partial<ProductVariantCreate>;
  onChange: (data: Partial<ProductVariantCreate>) => void;
  editMode?: boolean;
}

const BasicInfoStep: React.FC<BasicInfoStepProps> = ({
  data,
  onChange,
  editMode = false
}) => {
  const handleChange = (field: keyof ProductVariantCreate, value: any) => {
    onChange({ [field]: value });
  };

  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Typography variant="h6" gutterBottom>
          Basic Information
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          Enter the core details for this product variant
        </Typography>
      </Grid>

      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          required
          label="Base Product ID"
          value={data.base_product_id || ''}
          onChange={(e) => handleChange('base_product_id', e.target.value)}
          disabled={editMode}
          helperText="The parent product this variant belongs to"
        />
      </Grid>

      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          required
          label="Variant Code"
          value={data.variant_code || ''}
          onChange={(e) => handleChange('variant_code', e.target.value.toUpperCase())}
          disabled={editMode}
          helperText="Unique code (e.g., PL001-FESTIVE)"
          inputProps={{ style: { textTransform: 'uppercase' } }}
        />
      </Grid>

      <Grid item xs={12}>
        <TextField
          fullWidth
          required
          label="Variant Name"
          value={data.variant_name || ''}
          onChange={(e) => handleChange('variant_name', e.target.value)}
          helperText="Full name of the variant"
        />
      </Grid>

      <Grid item xs={12} md={6}>
        <FormControl fullWidth required>
          <InputLabel>Variant Type</InputLabel>
          <Select
            value={data.variant_type || VariantType.STANDARD}
            onChange={(e) => handleChange('variant_type', e.target.value)}
            label="Variant Type"
            disabled={editMode}
          >
            <MenuItem value={VariantType.STANDARD}>Standard</MenuItem>
            <MenuItem value={VariantType.PROMOTIONAL}>Promotional</MenuItem>
            <MenuItem value={VariantType.SEASONAL}>Seasonal</MenuItem>
            <MenuItem value={VariantType.GEOGRAPHY_SPECIFIC}>Geography-Specific</MenuItem>
            <MenuItem value={VariantType.SEGMENT_SPECIFIC}>Segment-Specific</MenuItem>
            <MenuItem value={VariantType.LIMITED_EDITION}>Limited Edition</MenuItem>
            <MenuItem value={VariantType.EMPLOYEE_SPECIAL}>Employee Special</MenuItem>
          </Select>
        </FormControl>
      </Grid>

      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          type="number"
          label="Priority"
          value={data.priority || 0}
          onChange={(e) => handleChange('priority', parseInt(e.target.value))}
          helperText="Higher priority variants shown first (0-100)"
          inputProps={{ min: 0, max: 100 }}
        />
      </Grid>

      <Grid item xs={12}>
        <TextField
          fullWidth
          multiline
          rows={3}
          label="Description"
          value={data.description || ''}
          onChange={(e) => handleChange('description', e.target.value)}
          helperText="Internal description of the variant"
        />
      </Grid>

      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          required
          type="date"
          label="Valid From"
          value={data.valid_from || ''}
          onChange={(e) => handleChange('valid_from', e.target.value)}
          InputLabelProps={{ shrink: true }}
          helperText="Start date for this variant"
        />
      </Grid>

      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          type="date"
          label="Valid To"
          value={data.valid_to || ''}
          onChange={(e) => handleChange('valid_to', e.target.value)}
          InputLabelProps={{ shrink: true }}
          helperText="End date (optional, leave blank for no expiry)"
        />
      </Grid>
    </Grid>
  );
};

export default BasicInfoStep;
