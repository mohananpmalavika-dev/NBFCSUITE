/**
 * Product Variant Builder - Multi-Step Wizard
 * Create and edit product variants with type-specific configuration
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Stepper,
  Step,
  StepLabel,
  Button,
  Typography,
  Alert
} from '@mui/material';
import productLifecycleService, {
  ProductVariant,
  ProductVariantCreate,
  VariantType
} from '@/services/productLifecycle.service';

// Import step components
import BasicInfoStep from './steps/BasicInfoStep';
import ConfigurationStep from './steps/ConfigurationStep';
import TypeSpecificStep from './steps/TypeSpecificStep';
import MarketingStep from './steps/MarketingStep';
import ReviewStep from './steps/ReviewStep';

interface VariantBuilderProps {
  variant?: ProductVariant;
  onSave?: (variant: ProductVariant) => void;
  onCancel?: () => void;
}

const steps = [
  'Basic Information',
  'Configuration Overrides',
  'Type-Specific Settings',
  'Marketing Content',
  'Review & Submit'
];

const VariantBuilder: React.FC<VariantBuilderProps> = ({
  variant,
  onSave,
  onCancel
}) => {
  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Form data
  const [formData, setFormData] = useState<Partial<ProductVariantCreate>>({
    variant_type: VariantType.STANDARD,
    priority: 0,
    valid_from: new Date().toISOString().split('T')[0]
  });

  // Type-specific configuration
  const [typeSpecificData, setTypeSpecificData] = useState<any>({});

  useEffect(() => {
    if (variant) {
      // Populate form with existing variant data
      setFormData({
        base_product_id: variant.base_product_id,
        variant_code: variant.variant_code,
        variant_name: variant.variant_name,
        variant_type: variant.variant_type,
        description: variant.description,
        valid_from: variant.valid_from,
        valid_to: variant.valid_to,
        interest_rate_override: variant.interest_rate_override,
        tenure_override: variant.tenure_override,
        amount_override: variant.amount_override,
        fee_override: variant.fee_override,
        eligibility_override: variant.eligibility_override,
        priority: variant.priority,
        marketing_name: variant.marketing_name,
        tagline: variant.tagline,
        promotional_message: variant.promotional_message,
        terms_and_conditions: variant.terms_and_conditions
      });
    }
  }, [variant]);

  const handleNext = () => {
    setActiveStep((prevStep) => prevStep + 1);
    setError(null);
  };

  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
    setError(null);
  };

  const handleDataChange = (data: Partial<ProductVariantCreate>) => {
    setFormData((prev) => ({ ...prev, ...data }));
  };

  const handleTypeSpecificDataChange = (data: any) => {
    setTypeSpecificData((prev) => ({ ...prev, ...data }));
  };

  const handleSubmit = async () => {
    setLoading(true);
    setError(null);

    try {
      // Validate required fields
      if (!formData.base_product_id) {
        throw new Error('Base product is required');
      }
      if (!formData.variant_code) {
        throw new Error('Variant code is required');
      }
      if (!formData.variant_name) {
        throw new Error('Variant name is required');
      }

      let savedVariant: ProductVariant;

      if (variant) {
        // Update existing variant
        const updateData = {
          variant_name: formData.variant_name,
          description: formData.description,
          valid_to: formData.valid_to,
          interest_rate_override: formData.interest_rate_override,
          tenure_override: formData.tenure_override,
          amount_override: formData.amount_override,
          fee_override: formData.fee_override,
          priority: formData.priority,
          marketing_name: formData.marketing_name,
          tagline: formData.tagline,
          promotional_message: formData.promotional_message
        };
        savedVariant = await productLifecycleService.updateVariant(variant.id, updateData);
      } else {
        // Create new variant
        savedVariant = await productLifecycleService.createVariant(formData as ProductVariantCreate);
      }

      // Create type-specific configuration
      if (typeSpecificData && Object.keys(typeSpecificData).length > 0) {
        await createTypeSpecificConfig(savedVariant.id, formData.variant_type!, typeSpecificData);
      }

      if (onSave) {
        onSave(savedVariant);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to save variant');
    } finally {
      setLoading(false);
    }
  };

  const createTypeSpecificConfig = async (
    variantId: string,
    variantType: VariantType,
    data: any
  ) => {
    switch (variantType) {
      case VariantType.PROMOTIONAL:
        await productLifecycleService.createPromotionalProduct(variantId, data);
        break;
      case VariantType.SEASONAL:
        await productLifecycleService.createSeasonalProduct(variantId, data);
        break;
      case VariantType.GEOGRAPHY_SPECIFIC:
        await productLifecycleService.createGeographySpecificProduct(variantId, data);
        break;
      case VariantType.SEGMENT_SPECIFIC:
        await productLifecycleService.createSegmentSpecificProduct(variantId, data);
        break;
    }
  };

  const getStepContent = (step: number) => {
    switch (step) {
      case 0:
        return (
          <BasicInfoStep
            data={formData}
            onChange={handleDataChange}
            editMode={!!variant}
          />
        );
      case 1:
        return (
          <ConfigurationStep
            data={formData}
            onChange={handleDataChange}
          />
        );
      case 2:
        return (
          <TypeSpecificStep
            variantType={formData.variant_type!}
            data={typeSpecificData}
            onChange={handleTypeSpecificDataChange}
          />
        );
      case 3:
        return (
          <MarketingStep
            data={formData}
            onChange={handleDataChange}
          />
        );
      case 4:
        return (
          <ReviewStep
            formData={formData}
            typeSpecificData={typeSpecificData}
          />
        );
      default:
        return null;
    }
  };

  const isStepValid = (step: number): boolean => {
    switch (step) {
      case 0:
        return !!(
          formData.base_product_id &&
          formData.variant_code &&
          formData.variant_name &&
          formData.variant_type &&
          formData.valid_from
        );
      case 1:
        return true; // Configuration is optional
      case 2:
        return true; // Type-specific is optional
      case 3:
        return true; // Marketing is optional
      case 4:
        return true; // Review step
      default:
        return false;
    }
  };

  return (
    <Box sx={{ width: '100%' }}>
      <Card>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            {variant ? 'Edit Variant' : 'Create New Variant'}
          </Typography>
          
          <Stepper activeStep={activeStep} sx={{ mt: 3, mb: 4 }}>
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

          <Box sx={{ minHeight: 400 }}>
            {getStepContent(activeStep)}
          </Box>

          <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
            <Button
              onClick={onCancel}
              disabled={loading}
            >
              Cancel
            </Button>
            
            <Box>
              {activeStep > 0 && (
                <Button
                  onClick={handleBack}
                  sx={{ mr: 1 }}
                  disabled={loading}
                >
                  Back
                </Button>
              )}
              
              {activeStep < steps.length - 1 ? (
                <Button
                  variant="contained"
                  onClick={handleNext}
                  disabled={!isStepValid(activeStep) || loading}
                >
                  Next
                </Button>
              ) : (
                <Button
                  variant="contained"
                  onClick={handleSubmit}
                  disabled={loading}
                >
                  {loading ? 'Saving...' : variant ? 'Update Variant' : 'Create Variant'}
                </Button>
              )}
            </Box>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default VariantBuilder;
