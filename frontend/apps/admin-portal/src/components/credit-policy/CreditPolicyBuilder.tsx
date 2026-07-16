/**
 * Credit Policy Builder Component
 * Multi-step wizard for creating/editing credit policies
 */
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
  Card,
  CardContent,
  Alert,
  CircularProgress
} from '@mui/material';
import { Save as SaveIcon, Cancel as CancelIcon } from '@mui/icons-material';
import creditPolicyService, {
  CreditPolicy,
  PolicyStatus,
  RiskBasedPricing,
  ScoreBasedRate,
  PricingTier
} from '@/services/creditPolicy.service';

// Step components
import BasicInfoStep from './steps/BasicInfoStep';
import RiskPricingStep from './steps/RiskPricingStep';
import ScoreRatesStep from './steps/ScoreRatesStep';
import AutoApprovalStep from './steps/AutoApprovalStep';
import ReviewTriggersStep from './steps/ReviewTriggersStep';
import DecisionMatrixStep from './steps/DecisionMatrixStep';
import ExposureLimitsStep from './steps/ExposureLimitsStep';

interface CreditPolicyBuilderProps {
  policyId?: string;
  onSave?: (policy: CreditPolicy) => void;
  onCancel?: () => void;
}

const steps = [
  'Basic Information',
  'Risk Pricing',
  'Score-Based Rates',
  'Auto-Approval',
  'Review Triggers',
  'Decision Matrix',
  'Exposure Limits'
];

const CreditPolicyBuilder: React.FC<CreditPolicyBuilderProps> = ({
  policyId,
  onSave,
  onCancel
}) => {
  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  // Policy data state
  const [policyData, setPolicyData] = useState<Partial<CreditPolicy>>({
    name: '',
    code: '',
    description: '',
    status: PolicyStatus.DRAFT,
    version: '1.0'
  });

  const [riskPricing, setRiskPricing] = useState<Partial<RiskBasedPricing>>({
    base_interest_rate: 12.0,
    min_interest_rate: 10.0,
    max_interest_rate: 18.0,
    credit_score_weight: 0.4,
    ltv_weight: 0.3,
    dti_weight: 0.2,
    other_factors_weight: 0.1,
    processing_fee_range: { min: 1.0, max: 3.0 },
    risk_premium_range: { min: 0.0, max: 2.0 }
  });

  const [scoreRates, setScoreRates] = useState<ScoreBasedRate[]>([]);
  const [autoApprovalCriteria, setAutoApprovalCriteria] = useState<any>({});
  const [manualReviewTriggers, setManualReviewTriggers] = useState<any[]>([]);
  const [decisionMatrix, setDecisionMatrix] = useState<any[]>([]);
  const [exposureLimits, setExposureLimits] = useState<any[]>([]);

  useEffect(() => {
    if (policyId) {
      loadPolicy();
    }
  }, [policyId]);

  const loadPolicy = async () => {
    setLoading(true);
    setError(null);
    try {
      const policy = await creditPolicyService.getPolicy(policyId!);
      setPolicyData(policy);
      // Load related configurations would go here
    } catch (err: any) {
      setError(err.message || 'Failed to load policy');
    } finally {
      setLoading(false);
    }
  };

  const handleNext = () => {
    setActiveStep((prevStep) => prevStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
  };

  const handleSave = async (activate: boolean = false) => {
    setSaving(true);
    setError(null);
    
    try {
      let policy: CreditPolicy;
      
      if (policyId) {
        // Update existing policy
        policy = await creditPolicyService.updatePolicy(policyId, policyData);
      } else {
        // Create new policy
        policy = await creditPolicyService.createPolicy(policyData);
      }

      // Save related configurations
      // (In production, these would be separate API calls)
      
      if (activate) {
        policy = await creditPolicyService.activatePolicy(policy.id);
      }

      if (onSave) {
        onSave(policy);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to save policy');
    } finally {
      setSaving(false);
    }
  };

  const getStepContent = (step: number) => {
    switch (step) {
      case 0:
        return (
          <BasicInfoStep
            data={policyData}
            onChange={setPolicyData}
          />
        );
      case 1:
        return (
          <RiskPricingStep
            data={riskPricing}
            onChange={setRiskPricing}
          />
        );
      case 2:
        return (
          <ScoreRatesStep
            data={scoreRates}
            onChange={setScoreRates}
          />
        );
      case 3:
        return (
          <AutoApprovalStep
            data={autoApprovalCriteria}
            onChange={setAutoApprovalCriteria}
          />
        );
      case 4:
        return (
          <ReviewTriggersStep
            data={manualReviewTriggers}
            onChange={setManualReviewTriggers}
          />
        );
      case 5:
        return (
          <DecisionMatrixStep
            data={decisionMatrix}
            onChange={setDecisionMatrix}
          />
        );
      case 6:
        return (
          <ExposureLimitsStep
            data={exposureLimits}
            onChange={setExposureLimits}
          />
        );
      default:
        return 'Unknown step';
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ width: '100%', p: 3 }}>
      <Paper elevation={3} sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          {policyId ? 'Edit Credit Policy' : 'Create New Credit Policy'}
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        <Box sx={{ minHeight: '400px', mb: 3 }}>
          {getStepContent(activeStep)}
        </Box>

        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 3 }}>
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
              <>
                <Button
                  variant="outlined"
                  onClick={() => handleSave(false)}
                  disabled={saving}
                  startIcon={<SaveIcon />}
                  sx={{ mr: 1 }}
                >
                  Save as Draft
                </Button>
                <Button
                  variant="contained"
                  onClick={() => handleSave(true)}
                  disabled={saving}
                  startIcon={<SaveIcon />}
                >
                  Save & Activate
                </Button>
              </>
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

export default CreditPolicyBuilder;
