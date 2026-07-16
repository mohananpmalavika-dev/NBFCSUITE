/**
 * Type-Specific Step - Variant Builder
 * Configuration specific to variant type (Promotional, Seasonal, etc.)
 */
import React from 'react';
import {
  Grid,
  TextField,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Checkbox,
  FormControlLabel,
  Box
} from '@mui/material';
import {
  VariantType,
  Season,
  CustomerSegment
} from '@/services/productLifecycle.service';

interface TypeSpecificStepProps {
  variantType: VariantType;
  data: any;
  onChange: (data: any) => void;
}

const TypeSpecificStep: React.FC<TypeSpecificStepProps> = ({
  variantType,
  data,
  onChange
}) => {
  const handleChange = (field: string, value: any) => {
    onChange({ ...data, [field]: value });
  };

  const renderPromotionalFields = () => (
    <>
      <Grid item xs={12}>
        <Typography variant="subtitle1" gutterBottom>
          Promotional Configuration
        </Typography>
      </Grid>

      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          label="Promotion Name"
          value={data.promotion_name || ''}
          onChange={(e) => handleChange('promotion_name', e.target.value)}
        />
      </Grid>

      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          label="Campaign Name"
          value={data.campaign_name || ''}
          onChange={(e) => handleChange('campaign_name', e.target.value)}
        />
      </Grid>

      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          type="date"
          label="Promotion Start Date"
          value={data.promotion_start_date || ''}
          onChange={(e) => handleChange('promotion_start_date', e.target.value)}
          InputLabelProps={{ shrink: true }}
        />
      </Grid>

      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          type="date"
          label="Promotion End Date"
          value={data.promotion_end_date || ''}
          onChange={(e) => handleChange('promotion_end_date', e.target.value)}
          InputLabelProps={{ shrink: true }}
        />
      </Grid>

      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          type="number"
          label="Special Rate Discount (%)"
          value={data.special_rate_discount || ''}
          onChange={(e) => handleChange('special_rate_discount', parseFloat(e.target.value))}
          inputProps={{ step: 0.1, min: 0 }}
        />
      </Grid>

      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          type="number"
          label="Cashback Amount"
          value={data.cashback_amount || ''}
          onChange={(e) => handleChange('cashback_amount', parseFloat(e.target.value))}
          inputProps={{ step: 100, min: 0 }}
        />
      </Grid>

      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          type="number"
          label="Max Applications"
          value={data.max_applications || ''}
          onChange={(e) => handleChange('max_applications', parseInt(e.target.value))}
          inputProps={{ step: 1, min: 1 }}
        />
      </Grid>

      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          type="number"
          label="Min Credit Score"
          value={data.min_credit_score || ''}
          onChange={(e) => handleChange('min_credit_score', parseInt(e.target.value))}
          inputProps={{ step: 1, min: 300, max: 900 }}
        />
      </Grid>

      <Grid item xs={12}>
        <FormControlLabel
          control={
            <Checkbox
              checked={data.requires_referral_code || false}
              onChange={(e) => handleChange('requires_referral_code', e.target.checked)}
            />
          }
          label="Requires Referral Code"
        />
      </Grid>
    </>
  );

  const renderSeasonalFields = () => (
    <>
      <Grid item xs={12}>
        <Typography variant="subtitle1" gutterBottom>
          Seasonal Configuration
        </Typography>
      </Grid>

      <Grid item xs={12} md={6}>
        <FormControl fullWidth>
          <InputLabel>Season</InputLabel>
          <Select
            value={data.season || Season.FESTIVE}
            onChange={(e) => handleChange('season', e.target.value)}
            label="Season"
          >
            {Object.values(Season).map((season) => (
              <MenuItem key={season} value={season}>{season}</MenuItem>
            ))}
          </Select>
        </FormControl>
      </Grid>

      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          type="number"
          label="Season Year"
          value={data.season_year || new Date().getFullYear()}
          onChange={(e) => handleChange('season_year', parseInt(e.target.value))}
          inputProps={{ step: 1, min: 2024 }}
        />
      </Grid>

      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          type="date"
          label="Season Start Date"
          value={data.season_start_date || ''}
          onChange={(e) => handleChange('season_start_date', e.target.value)}
          InputLabelProps={{ shrink: true }}
        />
      </Grid>

      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          type="date"
          label="Season End Date"
          value={data.season_end_date || ''}
          onChange={(e) => handleChange('season_end_date', e.target.value)}
          InputLabelProps={{ shrink: true }}
        />
      </Grid>

      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          type="number"
          label="Seasonal Rate Adjustment (%)"
          value={data.seasonal_rate_adjustment || ''}
          onChange={(e) => handleChange('seasonal_rate_adjustment', parseFloat(e.target.value))}
          inputProps={{ step: 0.1 }}
          helperText="Positive or negative adjustment"
        />
      </Grid>

      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          type="number"
          label="Festive Bonus (₹)"
          value={data.festive_bonus || ''}
          onChange={(e) => handleChange('festive_bonus', parseFloat(e.target.value))}
          inputProps={{ step: 100, min: 0 }}
        />
      </Grid>

      <Grid item xs={12}>
        <FormControlLabel
          control={
            <Checkbox
              checked={data.holiday_moratorium || false}
              onChange={(e) => handleChange('holiday_moratorium', e.target.checked)}
            />
          }
          label="Holiday Moratorium (EMI Holiday)"
        />
      </Grid>

      {data.holiday_moratorium && (
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            type="number"
            label="Moratorium Months"
            value={data.moratorium_months || ''}
            onChange={(e) => handleChange('moratorium_months', parseInt(e.target.value))}
            inputProps={{ step: 1, min: 1, max: 6 }}
          />
        </Grid>
      )}
    </>
  );

  const renderGeographyFields = () => (
    <>
      <Grid item xs={12}>
        <Typography variant="subtitle1" gutterBottom>
          Geography Targeting
        </Typography>
      </Grid>

      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          label="Allowed States (comma-separated)"
          value={(data.allowed_states || []).join(', ')}
          onChange={(e) => handleChange('allowed_states', e.target.value.split(',').map((s: string) => s.trim()).filter(Boolean))}
          placeholder="Maharashtra, Karnataka, Tamil Nadu"
        />
      </Grid>

      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          label="Allowed Cities (comma-separated)"
          value={(data.allowed_cities || []).join(', ')}
          onChange={(e) => handleChange('allowed_cities', e.target.value.split(',').map((s: string) => s.trim()).filter(Boolean))}
          placeholder="Mumbai, Bangalore, Chennai"
        />
      </Grid>

      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          type="number"
          label="Regional Rate Adjustment (%)"
          value={data.regional_rate_adjustment || ''}
          onChange={(e) => handleChange('regional_rate_adjustment', parseFloat(e.target.value))}
          inputProps={{ step: 0.1 }}
        />
      </Grid>

      <Grid item xs={12}>
        <FormControlLabel
          control={
            <Checkbox
              checked={data.is_metro || false}
              onChange={(e) => handleChange('is_metro', e.target.checked)}
            />
          }
          label="Metro Cities Only"
        />
      </Grid>

      <Grid item xs={12}>
        <FormControlLabel
          control={
            <Checkbox
              checked={data.requires_local_verification || false}
              onChange={(e) => handleChange('requires_local_verification', e.target.checked)}
            />
          }
          label="Requires Local Verification"
        />
      </Grid>
    </>
  );

  const renderSegmentFields = () => (
    <>
      <Grid item xs={12}>
        <Typography variant="subtitle1" gutterBottom>
          Customer Segment Targeting
        </Typography>
      </Grid>

      <Grid item xs={12}>
        <FormControl fullWidth>
          <InputLabel>Target Segments</InputLabel>
          <Select
            multiple
            value={data.target_segments || []}
            onChange={(e) => handleChange('target_segments', e.target.value)}
            label="Target Segments"
          >
            {Object.values(CustomerSegment).map((segment) => (
              <MenuItem key={segment} value={segment}>{segment}</MenuItem>
            ))}
          </Select>
        </FormControl>
      </Grid>

      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          type="number"
          label="Minimum Age"
          value={data.min_age || ''}
          onChange={(e) => handleChange('min_age', parseInt(e.target.value))}
          inputProps={{ step: 1, min: 18 }}
        />
      </Grid>

      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          type="number"
          label="Maximum Age"
          value={data.max_age || ''}
          onChange={(e) => handleChange('max_age', parseInt(e.target.value))}
          inputProps={{ step: 1, min: 18 }}
        />
      </Grid>

      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          type="number"
          label="Minimum Income (₹)"
          value={data.min_income || ''}
          onChange={(e) => handleChange('min_income', parseFloat(e.target.value))}
          inputProps={{ step: 1000, min: 0 }}
        />
      </Grid>

      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          type="number"
          label="Segment Rate Benefit (%)"
          value={data.segment_rate_benefit || ''}
          onChange={(e) => handleChange('segment_rate_benefit', parseFloat(e.target.value))}
          inputProps={{ step: 0.1, min: 0 }}
        />
      </Grid>

      <Grid item xs={12}>
        <FormControlLabel
          control={
            <Checkbox
              checked={data.priority_processing || false}
              onChange={(e) => handleChange('priority_processing', e.target.checked)}
            />
          }
          label="Priority Processing"
        />
      </Grid>

      <Grid item xs={12}>
        <FormControlLabel
          control={
            <Checkbox
              checked={data.dedicated_relationship_manager || false}
              onChange={(e) => handleChange('dedicated_relationship_manager', e.target.checked)}
            />
          }
          label="Dedicated Relationship Manager"
        />
      </Grid>
    </>
  );

  const renderStandardFields = () => (
    <Grid item xs={12}>
      <Box sx={{ p: 3, bgcolor: 'background.paper', borderRadius: 1, textAlign: 'center' }}>
        <Typography variant="body1" color="text.secondary">
          No additional configuration required for Standard variant type.
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          Standard variants use the base product configuration with any overrides from the previous step.
        </Typography>
      </Box>
    </Grid>
  );

  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Typography variant="h6" gutterBottom>
          Type-Specific Configuration
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          Configure settings specific to the {variantType} variant type
        </Typography>
      </Grid>

      {variantType === VariantType.PROMOTIONAL && renderPromotionalFields()}
      {variantType === VariantType.SEASONAL && renderSeasonalFields()}
      {variantType === VariantType.GEOGRAPHY_SPECIFIC && renderGeographyFields()}
      {variantType === VariantType.SEGMENT_SPECIFIC && renderSegmentFields()}
      {variantType === VariantType.STANDARD && renderStandardFields()}
      {variantType === VariantType.LIMITED_EDITION && renderStandardFields()}
      {variantType === VariantType.EMPLOYEE_SPECIAL && renderStandardFields()}
    </Grid>
  );
};

export default TypeSpecificStep;
