/**
 * Decision Details Component
 * Displays complete decision information with all check results
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  CircularProgress,
  Alert,
  Button,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Table,
  TableBody,
  TableCell,
  TableRow,
  LinearProgress
} from '@mui/material';
import {
  ArrowBack as BackIcon,
  ExpandMore as ExpandMoreIcon,
  Refresh as RefreshIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  Warning as WarningIcon
} from '@mui/icons-material';
import { useRouter } from 'next/navigation';
import {
  decisionEngineService,
  DecisionDetails as DecisionDetailsType,
  formatDecisionOutcome,
  getDecisionOutcomeColor,
  formatCheckResult,
  getCheckResultColor,
  formatFraudRiskLevel,
  getFraudRiskColor,
  formatDuration,
  getScoreColor
} from '@/services/decisionEngine.service';

interface DecisionDetailsProps {
  decisionId: string;
}

export default function DecisionDetails({ decisionId }: DecisionDetailsProps) {
  const router = useRouter();
  const [details, setDetails] = useState<DecisionDetailsType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [rerunning, setRerunning] = useState(false);

  useEffect(() => {
    loadDecisionDetails();
  }, [decisionId]);

  const loadDecisionDetails = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await decisionEngineService.getDecisionDetails(decisionId);
      setDetails(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load decision details');
    } finally {
      setLoading(false);
    }
  };

  const handleRerun = async () => {
    try {
      setRerunning(true);
      const newDecision = await decisionEngineService.rerunDecision(decisionId);
      router.push(`/decision-engine/${newDecision.id}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to rerun decision');
    } finally {
      setRerunning(false);
    }
  };

  const handleBack = () => {
    router.push('/decision-engine');
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight={400}>
        <CircularProgress />
      </Box>
    );
  }

  if (error || !details) {
    return (
      <Box>
        <Alert severity="error" sx={{ mb: 2 }}>
          {error || 'Decision not found'}
        </Alert>
        <Button startIcon={<BackIcon />} onClick={handleBack}>
          Back to List
        </Button>
      </Box>
    );
  }

  const { decision } = details;

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box display="flex" alignItems="center">
          <Button startIcon={<BackIcon />} onClick={handleBack} sx={{ mr: 2 }}>
            Back
          </Button>
          <Typography variant="h4" component="h1">
            Decision Details
          </Typography>
        </Box>
        <Button
          variant="outlined"
          startIcon={rerunning ? <CircularProgress size={20} /> : <RefreshIcon />}
          onClick={handleRerun}
          disabled={rerunning}
        >
          Rerun Decision
        </Button>
      </Box>

      {/* Decision Summary */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Decision Summary
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" color="textSecondary">
                Application ID
              </Typography>
              <Typography variant="body1" fontFamily="monospace">
                {decision.application_id}
              </Typography>
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" color="textSecondary">
                Customer ID
              </Typography>
              <Typography variant="body1" fontFamily="monospace">
                {decision.customer_id}
              </Typography>
            </Grid>
            <Grid item xs={12} md={3}>
              <Typography variant="subtitle2" color="textSecondary">
                Requested Amount
              </Typography>
              <Typography variant="h6">
                ₹{decision.loan_amount.toLocaleString('en-IN')}
              </Typography>
            </Grid>
            <Grid item xs={12} md={3}>
              <Typography variant="subtitle2" color="textSecondary">
                Tenure
              </Typography>
              <Typography variant="h6">
                {decision.tenure_months} months
              </Typography>
            </Grid>
            <Grid item xs={12} md={3}>
              <Typography variant="subtitle2" color="textSecondary">
                Decision Outcome
              </Typography>
              <Chip
                label={formatDecisionOutcome(decision.decision_outcome)}
                color={getDecisionOutcomeColor(decision.decision_outcome) as any}
                size="medium"
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <Typography variant="subtitle2" color="textSecondary">
                Processing Time
              </Typography>
              <Typography variant="h6">
                {formatDuration(decision.total_duration_ms)}
              </Typography>
            </Grid>
          </Grid>

          <Divider sx={{ my: 2 }} />

          <Grid container spacing={3}>
            <Grid item xs={12} md={3}>
              <Typography variant="subtitle2" color="textSecondary">
                Decision Score
              </Typography>
              <Box display="flex" alignItems="center" gap={1}>
                <Typography variant="h5">
                  {decision.decision_score?.toFixed(1) || 'N/A'}
                </Typography>
                <Chip
                  size="small"
                  label={decision.decision_score ? `${decision.decision_score >= 70 ? 'Good' : decision.decision_score >= 55 ? 'Fair' : 'Poor'}` : 'N/A'}
                  color={getScoreColor(decision.decision_score) as any}
                />
              </Box>
            </Grid>
            <Grid item xs={12} md={3}>
              <Typography variant="subtitle2" color="textSecondary">
                Confidence Score
              </Typography>
              <Typography variant="h5">
                {decision.confidence_score?.toFixed(1) || 'N/A'}%
              </Typography>
            </Grid>
            <Grid item xs={12} md={3}>
              <Typography variant="subtitle2" color="textSecondary">
                Fraud Risk
              </Typography>
              <Chip
                label={formatFraudRiskLevel(decision.fraud_risk_level)}
                color={getFraudRiskColor(decision.fraud_risk_level) as any}
                size="medium"
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <Typography variant="subtitle2" color="textSecondary">
                Checks Status
              </Typography>
              <Box display="flex" gap={1}>
                <Chip
                  icon={<CheckCircleIcon />}
                  label={`${decision.passed_checks} Passed`}
                  color="success"
                  size="small"
                />
                <Chip
                  icon={<CancelIcon />}
                  label={`${decision.failed_checks} Failed`}
                  color="error"
                  size="small"
                />
                <Chip
                  icon={<WarningIcon />}
                  label={`${decision.warning_checks} Warning`}
                  color="warning"
                  size="small"
                />
              </Box>
            </Grid>
          </Grid>

          {decision.approved_amount && (
            <>
              <Divider sx={{ my: 2 }} />
              <Grid container spacing={3}>
                <Grid item xs={12} md={4}>
                  <Typography variant="subtitle2" color="textSecondary">
                    Approved Amount
                  </Typography>
                  <Typography variant="h5" color="success.main">
                    ₹{decision.approved_amount.toLocaleString('en-IN')}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Typography variant="subtitle2" color="textSecondary">
                    Approved Rate
                  </Typography>
                  <Typography variant="h5" color="success.main">
                    {decision.approved_rate}% p.a.
                  </Typography>
                </Grid>
              </Grid>
            </>
          )}

          {decision.decline_reasons && decision.decline_reasons.length > 0 && (
            <>
              <Divider sx={{ my: 2 }} />
              <Typography variant="subtitle2" color="error" gutterBottom>
                Decline Reasons
              </Typography>
              {decision.decline_reasons.map((reason, idx) => (
                <Chip key={idx} label={reason} color="error" size="small" sx={{ mr: 1, mb: 1 }} />
              ))}
            </>
          )}

          {decision.conditions && decision.conditions.length > 0 && (
            <>
              <Divider sx={{ my: 2 }} />
              <Typography variant="subtitle2" color="warning.main" gutterBottom>
                Conditions
              </Typography>
              {decision.conditions.map((condition, idx) => (
                <Chip key={idx} label={condition} color="warning" size="small" sx={{ mr: 1, mb: 1 }} />
              ))}
            </>
          )}
        </CardContent>
      </Card>

      {/* Check Results */}
      <Typography variant="h6" gutterBottom sx={{ mt: 2, mb: 2 }}>
        Check Results
      </Typography>

      {/* Bureau Checks */}
      {details.bureau_checks.map((check, idx) => (
        <Accordion key={idx} defaultExpanded={idx === 0}>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Box display="flex" alignItems="center" gap={2} width="100%">
              <Typography variant="subtitle1">
                Bureau Check - {check.bureau_provider}
              </Typography>
              <Chip
                label={formatCheckResult(check.result)}
                color={getCheckResultColor(check.result) as any}
                size="small"
              />
              <Typography variant="caption" color="textSecondary" sx={{ ml: 'auto' }}>
                {formatDuration(check.duration_ms)}
              </Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Table size="small">
              <TableBody>
                <TableRow>
                  <TableCell>Credit Score</TableCell>
                  <TableCell>
                    <Typography variant="h6" color={getScoreColor((check.credit_score || 0) / 9)}>
                      {check.credit_score || 'N/A'}
                    </Typography>
                  </TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Total Accounts</TableCell>
                  <TableCell>{check.total_accounts || 'N/A'}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Active Accounts</TableCell>
                  <TableCell>{check.active_accounts || 'N/A'}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Total Outstanding</TableCell>
                  <TableCell>₹{check.total_outstanding?.toLocaleString('en-IN') || 'N/A'}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Credit Utilization</TableCell>
                  <TableCell>{check.credit_utilization}%</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Max DPD (Last 12M)</TableCell>
                  <TableCell>{check.max_dpd_last_12m} days</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Enquiries (Last 6M)</TableCell>
                  <TableCell>{check.enquiries_last_6m}</TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </AccordionDetails>
        </Accordion>
      ))}

      {/* Bank Statement Analysis */}
      {details.bank_analysis.map((check, idx) => (
        <Accordion key={idx}>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Box display="flex" alignItems="center" gap={2} width="100%">
              <Typography variant="subtitle1">Bank Statement Analysis</Typography>
              <Chip
                label={formatCheckResult(check.result)}
                color={getCheckResultColor(check.result) as any}
                size="small"
              />
              <Typography variant="caption" color="textSecondary" sx={{ ml: 'auto' }}>
                {formatDuration(check.duration_ms)}
              </Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Table size="small">
              <TableBody>
                <TableRow>
                  <TableCell>Bank Name</TableCell>
                  <TableCell>{check.bank_name || 'N/A'}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Statement Period</TableCell>
                  <TableCell>{check.statement_period_months} months</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Average Monthly Credit</TableCell>
                  <TableCell>₹{check.average_monthly_credit?.toLocaleString('en-IN') || 'N/A'}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Salary Amount</TableCell>
                  <TableCell>₹{check.salary_amount?.toLocaleString('en-IN') || 'N/A'}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Salary Regularity Score</TableCell>
                  <TableCell>{check.salary_regularity_score?.toFixed(1)}%</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Average Monthly Debit</TableCell>
                  <TableCell>₹{check.average_monthly_debit?.toLocaleString('en-IN') || 'N/A'}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>EMI Deductions</TableCell>
                  <TableCell>₹{check.emi_deductions?.toLocaleString('en-IN') || 'N/A'}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Bounced Cheques</TableCell>
                  <TableCell>
                    <Chip
                      label={check.bounced_cheques_count || 0}
                      color={check.bounced_cheques_count === 0 ? 'success' : 'error'}
                      size="small"
                    />
                  </TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Banking Behavior Score</TableCell>
                  <TableCell>
                    <Typography color={getScoreColor(check.banking_behavior_score)}>
                      {check.banking_behavior_score?.toFixed(1)}
                    </Typography>
                  </TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Calculated DTI</TableCell>
                  <TableCell>
                    <Typography color={check.calculated_dti && check.calculated_dti > 50 ? 'error' : 'success'}>
                      {check.calculated_dti?.toFixed(2)}%
                    </Typography>
                  </TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </AccordionDetails>
        </Accordion>
      ))}

      {/* KYC Verification */}
      {details.kyc_verification.map((check, idx) => (
        <Accordion key={idx}>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Box display="flex" alignItems="center" gap={2} width="100%">
              <Typography variant="subtitle1">KYC Verification</Typography>
              <Chip
                label={formatCheckResult(check.result)}
                color={getCheckResultColor(check.result) as any}
                size="small"
              />
              <Typography variant="caption" color="textSecondary" sx={{ ml: 'auto' }}>
                {formatDuration(check.duration_ms)}
              </Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>Aadhaar Verification</Typography>
                <Table size="small">
                  <TableBody>
                    <TableRow>
                      <TableCell>Verified</TableCell>
                      <TableCell>
                        <Chip
                          label={check.aadhaar_verified ? 'Yes' : 'No'}
                          color={check.aadhaar_verified ? 'success' : 'error'}
                          size="small"
                        />
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Name Match</TableCell>
                      <TableCell>
                        <Chip
                          label={check.aadhaar_name_match ? 'Yes' : 'No'}
                          color={check.aadhaar_name_match ? 'success' : 'error'}
                          size="small"
                        />
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Address Match</TableCell>
                      <TableCell>
                        <Chip
                          label={check.aadhaar_address_match ? 'Yes' : 'No'}
                          color={check.aadhaar_address_match ? 'success' : 'error'}
                          size="small"
                        />
                      </TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>PAN Verification</Typography>
                <Table size="small">
                  <TableBody>
                    <TableRow>
                      <TableCell>Verified</TableCell>
                      <TableCell>
                        <Chip
                          label={check.pan_verified ? 'Yes' : 'No'}
                          color={check.pan_verified ? 'success' : 'error'}
                          size="small"
                        />
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Name Match</TableCell>
                      <TableCell>
                        <Chip
                          label={check.pan_name_match ? 'Yes' : 'No'}
                          color={check.pan_name_match ? 'success' : 'error'}
                          size="small"
                        />
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Status</TableCell>
                      <TableCell>{check.pan_status || 'N/A'}</TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </Grid>
              <Grid item xs={12}>
                <Table size="small">
                  <TableBody>
                    <TableRow>
                      <TableCell>Address Verified</TableCell>
                      <TableCell>
                        <Chip
                          label={check.address_verified ? 'Yes' : 'No'}
                          color={check.address_verified ? 'success' : 'error'}
                          size="small"
                        />
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Employment Verified</TableCell>
                      <TableCell>
                        <Chip
                          label={check.employment_verified ? 'Yes' : 'No'}
                          color={check.employment_verified ? 'success' : 'error'}
                          size="small"
                        />
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>KYC Score</TableCell>
                      <TableCell>
                        <Typography color={getScoreColor(check.kyc_score)}>
                          {check.kyc_score?.toFixed(1)}
                        </Typography>
                      </TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </Grid>
            </Grid>
          </AccordionDetails>
        </Accordion>
      ))}

      {/* Fraud Checks */}
      {details.fraud_checks.map((check, idx) => (
        <Accordion key={idx}>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Box display="flex" alignItems="center" gap={2} width="100%">
              <Typography variant="subtitle1">Fraud Check</Typography>
              <Chip
                label={formatCheckResult(check.result)}
                color={getCheckResultColor(check.result) as any}
                size="small"
              />
              <Chip
                label={formatFraudRiskLevel(check.fraud_risk_level)}
                color={getFraudRiskColor(check.fraud_risk_level) as any}
                size="small"
              />
              <Typography variant="caption" color="textSecondary" sx={{ ml: 'auto' }}>
                {formatDuration(check.duration_ms)}
              </Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>Device Information</Typography>
                <Table size="small">
                  <TableBody>
                    <TableRow>
                      <TableCell>Device Type</TableCell>
                      <TableCell>{check.device_type || 'N/A'}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Device Risk Score</TableCell>
                      <TableCell>{check.device_risk_score?.toFixed(1)}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>IP Address</TableCell>
                      <TableCell>{check.ip_address || 'N/A'}</TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>Location</Typography>
                <Table size="small">
                  <TableBody>
                    <TableRow>
                      <TableCell>Country</TableCell>
                      <TableCell>{check.geo_country || 'N/A'}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>State</TableCell>
                      <TableCell>{check.geo_state || 'N/A'}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>City</TableCell>
                      <TableCell>{check.geo_city || 'N/A'}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Geo Risk Score</TableCell>
                      <TableCell>{check.geo_risk_score?.toFixed(1)}</TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="subtitle2" gutterBottom>Velocity Check</Typography>
                <Table size="small">
                  <TableBody>
                    <TableRow>
                      <TableCell>Applications (Last 24h)</TableCell>
                      <TableCell>
                        <Chip
                          label={check.applications_last_24h}
                          color={check.applications_last_24h > 2 ? 'error' : 'success'}
                          size="small"
                        />
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Applications (Last 7d)</TableCell>
                      <TableCell>{check.applications_last_7d}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Applications (Last 30d)</TableCell>
                      <TableCell>{check.applications_last_30d}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Velocity Risk Score</TableCell>
                      <TableCell>{check.velocity_risk_score?.toFixed(1)}</TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="subtitle2" gutterBottom>Duplicate & Blacklist Check</Typography>
                <Table size="small">
                  <TableBody>
                    <TableRow>
                      <TableCell>Duplicate Applications</TableCell>
                      <TableCell>
                        <Chip
                          label={check.duplicate_applications}
                          color={check.duplicate_applications > 0 ? 'error' : 'success'}
                          size="small"
                        />
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Duplicate Phone</TableCell>
                      <TableCell>
                        <Chip
                          label={check.duplicate_phone ? 'Yes' : 'No'}
                          color={check.duplicate_phone ? 'error' : 'success'}
                          size="small"
                        />
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Duplicate Email</TableCell>
                      <TableCell>
                        <Chip
                          label={check.duplicate_email ? 'Yes' : 'No'}
                          color={check.duplicate_email ? 'error' : 'success'}
                          size="small"
                        />
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Blacklisted</TableCell>
                      <TableCell>
                        <Chip
                          label={check.blacklisted ? 'Yes' : 'No'}
                          color={check.blacklisted ? 'error' : 'success'}
                          size="small"
                        />
                      </TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="subtitle2" gutterBottom>Overall Fraud Assessment</Typography>
                <Table size="small">
                  <TableBody>
                    <TableRow>
                      <TableCell>Fraud Score</TableCell>
                      <TableCell>
                        <Typography variant="h6" color={getFraudRiskColor(check.fraud_risk_level)}>
                          {check.fraud_score?.toFixed(1)}
                        </Typography>
                      </TableCell>
                    </TableRow>
                    {check.fraud_indicators && check.fraud_indicators.length > 0 && (
                      <TableRow>
                        <TableCell>Fraud Indicators</TableCell>
                        <TableCell>
                          {check.fraud_indicators.map((indicator, i) => (
                            <Chip
                              key={i}
                              label={indicator}
                              color="error"
                              size="small"
                              sx={{ mr: 1, mb: 1 }}
                            />
                          ))}
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </Grid>
            </Grid>
          </AccordionDetails>
        </Accordion>
      ))}

      {/* Eligibility Checks */}
      {details.eligibility_checks.map((check, idx) => (
        <Accordion key={idx}>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Box display="flex" alignItems="center" gap={2} width="100%">
              <Typography variant="subtitle1">Eligibility Check</Typography>
              <Chip
                label={formatCheckResult(check.result)}
                color={getCheckResultColor(check.result) as any}
                size="small"
              />
              <Chip
                label={check.overall_eligible ? 'Eligible' : 'Not Eligible'}
                color={check.overall_eligible ? 'success' : 'error'}
                size="small"
              />
              <Typography variant="caption" color="textSecondary" sx={{ ml: 'auto' }}>
                {formatDuration(check.duration_ms)}
              </Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Table size="small">
              <TableBody>
                <TableRow>
                  <TableCell>Age</TableCell>
                  <TableCell>
                    {check.age} years
                    <Chip
                      label={check.age_eligible ? 'Eligible' : 'Not Eligible'}
                      color={check.age_eligible ? 'success' : 'error'}
                      size="small"
                      sx={{ ml: 1 }}
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="caption" color="textSecondary">
                      Range: {check.min_age}-{check.max_age} years
                    </Typography>
                  </TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Monthly Income</TableCell>
                  <TableCell>
                    ₹{check.monthly_income?.toLocaleString('en-IN')}
                    <Chip
                      label={check.income_eligible ? 'Eligible' : 'Not Eligible'}
                      color={check.income_eligible ? 'success' : 'error'}
                      size="small"
                      sx={{ ml: 1 }}
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="caption" color="textSecondary">
                      Min: ₹{check.min_income.toLocaleString('en-IN')}
                    </Typography>
                  </TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>DTI Ratio</TableCell>
                  <TableCell>
                    {check.dti_ratio?.toFixed(2)}%
                    <Chip
                      label={check.dti_eligible ? 'Eligible' : 'Not Eligible'}
                      color={check.dti_eligible ? 'success' : 'error'}
                      size="small"
                      sx={{ ml: 1 }}
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="caption" color="textSecondary">
                      Max: {check.max_dti}%
                    </Typography>
                  </TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Employment</TableCell>
                  <TableCell>
                    {check.employment_type} ({check.employment_duration_months} months)
                    <Chip
                      label={check.employment_eligible ? 'Eligible' : 'Not Eligible'}
                      color={check.employment_eligible ? 'success' : 'error'}
                      size="small"
                      sx={{ ml: 1 }}
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="caption" color="textSecondary">
                      Min: {check.min_employment_months} months
                    </Typography>
                  </TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Credit Score</TableCell>
                  <TableCell>
                    {check.credit_score}
                    <Chip
                      label={check.credit_score_eligible ? 'Eligible' : 'Not Eligible'}
                      color={check.credit_score_eligible ? 'success' : 'error'}
                      size="small"
                      sx={{ ml: 1 }}
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="caption" color="textSecondary">
                      Min: {check.min_credit_score}
                    </Typography>
                  </TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Loan Amount</TableCell>
                  <TableCell>
                    ₹{check.requested_amount.toLocaleString('en-IN')}
                    <Chip
                      label={check.amount_eligible ? 'Eligible' : 'Not Eligible'}
                      color={check.amount_eligible ? 'success' : 'error'}
                      size="small"
                      sx={{ ml: 1 }}
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="caption" color="textSecondary">
                      Range: ₹{check.min_loan_amount.toLocaleString('en-IN')} - ₹{check.max_loan_amount.toLocaleString('en-IN')}
                    </Typography>
                  </TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Eligibility Score</TableCell>
                  <TableCell colSpan={2}>
                    <Box display="flex" alignItems="center" gap={2}>
                      <Typography variant="h6" color={getScoreColor(check.eligibility_score)}>
                        {check.eligibility_score?.toFixed(1)}
                      </Typography>
                      <LinearProgress
                        variant="determinate"
                        value={check.eligibility_score || 0}
                        sx={{ flexGrow: 1, height: 8, borderRadius: 4 }}
                      />
                    </Box>
                  </TableCell>
                </TableRow>
                {check.failed_criteria && check.failed_criteria.length > 0 && (
                  <TableRow>
                    <TableCell>Failed Criteria</TableCell>
                    <TableCell colSpan={2}>
                      {check.failed_criteria.map((criteria, i) => (
                        <Chip
                          key={i}
                          label={criteria}
                          color="error"
                          size="small"
                          sx={{ mr: 1, mb: 1 }}
                        />
                      ))}
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </AccordionDetails>
        </Accordion>
      ))}

      {/* Audit Trail */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Audit Trail
          </Typography>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Timestamp</TableCell>
                <TableCell>Action</TableCell>
                <TableCell>Details</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {details.audit_trail.map((audit) => (
                <TableRow key={audit.id}>
                  <TableCell>
                    {new Date(audit.timestamp).toLocaleString('en-IN')}
                  </TableCell>
                  <TableCell>
                    <Chip label={audit.action} size="small" variant="outlined" />
                  </TableCell>
                  <TableCell>{audit.details}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </Box>
  );
}
