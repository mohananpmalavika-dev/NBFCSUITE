/**
 * Review Step - Variant Builder
 * Review all configuration before submission
 */
import React from 'react';
import {
  Grid,
  Typography,
  Card,
  CardContent,
  Box,
  Chip,
  Divider
} from '@mui/material';
import {
  ProductVariantCreate,
  VariantType
} from '@/services/productLifecycle.service';
import productLifecycleService from '@/services/productLifecycle.service';

interface ReviewStepProps {
  formData: Partial<ProductVariantCreate>;
  typeSpecificData: any;
}

const ReviewStep: React.FC<ReviewStepProps> = ({
  formData,
  typeSpecificData
}) => {
  const InfoRow = ({ label, value }: { label: string; value: any }) => (
    <Box sx={{ display: 'flex', py: 1 }}>
      <Typography variant="body2" color="text.secondary" sx={{ minWidth: 180 }}>
        {label}:
      </Typography>
      <Typography variant="body2" fontWeight="medium">
        {value || 'Not set'}
      </Typography>
    </Box>
  );

  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Typography variant="h6" gutterBottom>
          Review & Submit
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          Please review all information before creating the variant
        </Typography>
      </Grid>

      {/* Basic Information */}
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="subtitle1" gutterBottom>
              Basic Information
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            <InfoRow label="Variant Code" value={formData.variant_code} />
            <InfoRow label="Variant Name" value={formData.variant_name} />
            <InfoRow 
              label="Variant Type" 
              value={formData.variant_type && productLifecycleService.getVariantTypeLabel(formData.variant_type)} 
            />
            <InfoRow label="Priority" value={formData.priority} />
            <InfoRow label="Description" value={formData.description} />
            <InfoRow 
              label="Valid From" 
              value={formData.valid_from && productLifecycleService.formatDate(formData.valid_from)} 
            />
            <InfoRow 
              label="Valid To" 
              value={formData.valid_to && productLifecycleService.formatDate(formData.valid_to)} 
            />
          </CardContent>
        </Card>
      </Grid>

      {/* Configuration Overrides */}
      {(formData.interest_rate_override || formData.tenure_override || 
        formData.amount_override || formData.fee_override) && (
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="subtitle1" gutterBottom>
                Configuration Overrides
              </Typography>
              <Divider sx={{ mb: 2 }} />
              
              {formData.interest_rate_override && (
                <>
                  <Typography variant="body2" fontWeight="medium" sx={{ mt: 1 }}>
                    Interest Rate Override:
                  </Typography>
                  {formData.interest_rate_override.base && (
                    <InfoRow label="Base Rate" value={`${formData.interest_rate_override.base}%`} />
                  )}
                  {formData.interest_rate_override.min && (
                    <InfoRow label="Min Rate" value={`${formData.interest_rate_override.min}%`} />
                  )}
                  {formData.interest_rate_override.max && (
                    <InfoRow label="Max Rate" value={`${formData.interest_rate_override.max}%`} />
                  )}
                </>
              )}

              {formData.tenure_override && (
                <>
                  <Typography variant="body2" fontWeight="medium" sx={{ mt: 2 }}>
                    Tenure Override:
                  </Typography>
                  {formData.tenure_override.min && (
                    <InfoRow label="Min Tenure" value={`${formData.tenure_override.min} months`} />
                  )}
                  {formData.tenure_override.max && (
                    <InfoRow label="Max Tenure" value={`${formData.tenure_override.max} months`} />
                  )}
                </>
              )}

              {formData.amount_override && (
                <>
                  <Typography variant="body2" fontWeight="medium" sx={{ mt: 2 }}>
                    Amount Override:
                  </Typography>
                  {formData.amount_override.min && (
                    <InfoRow 
                      label="Min Amount" 
                      value={productLifecycleService.formatCurrency(formData.amount_override.min)} 
                    />
                  )}
                  {formData.amount_override.max && (
                    <InfoRow 
                      label="Max Amount" 
                      value={productLifecycleService.formatCurrency(formData.amount_override.max)} 
                    />
                  )}
                </>
              )}

              {formData.fee_override && (
                <>
                  <Typography variant="body2" fontWeight="medium" sx={{ mt: 2 }}>
                    Fee Override:
                  </Typography>
                  {Object.entries(formData.fee_override).map(([key, value]) => (
                    <InfoRow key={key} label={key.replace(/_/g, ' ')} value={`${value}%`} />
                  ))}
                </>
              )}
            </CardContent>
          </Card>
        </Grid>
      )}

      {/* Type-Specific Configuration */}
      {Object.keys(typeSpecificData).length > 0 && (
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="subtitle1" gutterBottom>
                Type-Specific Configuration
              </Typography>
              <Divider sx={{ mb: 2 }} />
              
              {Object.entries(typeSpecificData).map(([key, value]) => {
                if (typeof value === 'boolean') {
                  return value ? (
                    <Box key={key} sx={{ py: 0.5 }}>
                      <Chip label={key.replace(/_/g, ' ')} size="small" color="primary" />
                    </Box>
                  ) : null;
                }
                
                if (Array.isArray(value)) {
                  return value.length > 0 ? (
                    <InfoRow key={key} label={key.replace(/_/g, ' ')} value={value.join(', ')} />
                  ) : null;
                }
                
                return (
                  <InfoRow 
                    key={key} 
                    label={key.replace(/_/g, ' ')} 
                    value={typeof value === 'number' ? value.toString() : value} 
                  />
                );
              })}
            </CardContent>
          </Card>
        </Grid>
      )}

      {/* Marketing Content */}
      {(formData.marketing_name || formData.tagline || formData.promotional_message) && (
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="subtitle1" gutterBottom>
                Marketing Content
              </Typography>
              <Divider sx={{ mb: 2 }} />
              
              <InfoRow label="Marketing Name" value={formData.marketing_name} />
              <InfoRow label="Tagline" value={formData.tagline} />
              {formData.promotional_message && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Promotional Message:
                  </Typography>
                  <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                    {formData.promotional_message}
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      )}
    </Grid>
  );
};

export default ReviewStep;
