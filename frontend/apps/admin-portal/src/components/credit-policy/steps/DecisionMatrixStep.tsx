/**
 * Decision Matrix Step
 * Configure decision rules based on multiple criteria
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
  FormControlLabel,
  Switch,
  Chip
} from '@mui/material';
import { Add as AddIcon, Delete as DeleteIcon } from '@mui/icons-material';
import { DecisionOutcome, DeclineReason } from '@/services/creditPolicy.service';

interface DecisionMatrixStepProps {
  data: any[];
  onChange: (data: any[]) => void;
}

const defaultRule = {
  rule_name: '',
  rule_priority: 0,
  decision_outcome: DecisionOutcome.MANUAL_REVIEW,
  is_active: true
};

const DecisionMatrixStep: React.FC<DecisionMatrixStepProps> = ({ data, onChange }) => {
  const handleAdd = () => {
    onChange([...data, { ...defaultRule }]);
  };

  const handleRemove = (index: number) => {
    onChange(data.filter((_, i) => i !== index));
  };

  const handleChange = (index: number, field: string) => (
    event: React.ChangeEvent<HTMLInputElement | { value: unknown }>
  ) => {
    const newData = [...data];
    const value = event.target.type === 'checkbox' 
      ? (event.target as HTMLInputElement).checked
      : event.target.type === 'number'
      ? parseFloat(event.target.value as string)
      : event.target.value;
    
    newData[index] = {
      ...newData[index],
      [field]: value
    };
    onChange(newData);
  };

  const handleRangeChange = (index: number, field: string, key: 'min' | 'max') => (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const newData = [...data];
    newData[index] = {
      ...newData[index],
      [field]: {
        ...(newData[index][field] || {}),
        [key]: parseFloat(event.target.value)
      }
    };
    onChange(newData);
  };

  const getOutcomeColor = (outcome: DecisionOutcome) => {
    switch (outcome) {
      case DecisionOutcome.AUTO_APPROVED: return 'success';
      case DecisionOutcome.MANUAL_REVIEW: return 'warning';
      case DecisionOutcome.DECLINED: return 'error';
      case DecisionOutcome.COUNTER_OFFER: return 'info';
      default: return 'default';
    }
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h6">Decision Matrix Rules</Typography>
          <Typography variant="body2" color="text.secondary">
            Define priority-based decision rules
          </Typography>
        </Box>
        <Button variant="contained" startIcon={<AddIcon />} onClick={handleAdd}>
          Add Rule
        </Button>
      </Box>

      {data.length === 0 ? (
        <Card>
          <CardContent>
            <Typography variant="body1" color="text.secondary" align="center" py={4}>
              No decision rules configured. Click "Add Rule" to create one.
            </Typography>
          </CardContent>
        </Card>
      ) : (
        <Grid container spacing={2}>
          {data.map((rule, index) => (
            <Grid item xs={12} key={index}>
              <Card>
                <CardContent>
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                    <Box display="flex" alignItems="center" gap={1}>
                      <Typography variant="subtitle1" fontWeight="bold">
                        Rule {index + 1}
                      </Typography>
                      <Chip 
                        label={rule.decision_outcome} 
                        color={getOutcomeColor(rule.decision_outcome)}
                        size="small"
                      />
                    </Box>
                    <IconButton color="error" onClick={() => handleRemove(index)} size="small">
                      <DeleteIcon />
                    </IconButton>
                  </Box>

                  <Grid container spacing={2}>
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        required
                        label="Rule Name"
                        value={rule.rule_name}
                        onChange={handleChange(index, 'rule_name')}
                        placeholder="e.g., High Score Auto Approve"
                      />
                    </Grid>

                    <Grid item xs={12} md={3}>
                      <TextField
                        fullWidth
                        type="number"
                        label="Priority"
                        value={rule.rule_priority}
                        onChange={handleChange(index, 'rule_priority')}
                        helperText="Higher = First"
                      />
                    </Grid>

                    <Grid item xs={12} md={3}>
                      <FormControlLabel
                        control={
                          <Switch
                            checked={rule.is_active}
                            onChange={handleChange(index, 'is_active')}
                          />
                        }
                        label="Active"
                      />
                    </Grid>

                    {/* Credit Score Range */}
                    <Grid item xs={12}>
                      <Typography variant="body2" gutterBottom>Credit Score Range</Typography>
                      <Grid container spacing={2}>
                        <Grid item xs={6}>
                          <TextField
                            fullWidth
                            type="number"
                            label="Min Score"
                            value={rule.credit_score_range?.min || ''}
                            onChange={handleRangeChange(index, 'credit_score_range', 'min')}
                          />
                        </Grid>
                        <Grid item xs={6}>
                          <TextField
                            fullWidth
                            type="number"
                            label="Max Score"
                            value={rule.credit_score_range?.max || ''}
                            onChange={handleRangeChange(index, 'credit_score_range', 'max')}
                          />
                        </Grid>
                      </Grid>
                    </Grid>

                    {/* Loan Amount Range */}
                    <Grid item xs={12}>
                      <Typography variant="body2" gutterBottom>Loan Amount Range</Typography>
                      <Grid container spacing={2}>
                        <Grid item xs={6}>
                          <TextField
                            fullWidth
                            type="number"
                            label="Min Amount"
                            value={rule.loan_amount_range?.min || ''}
                            onChange={handleRangeChange(index, 'loan_amount_range', 'min')}
                          />
                        </Grid>
                        <Grid item xs={6}>
                          <TextField
                            fullWidth
                            type="number"
                            label="Max Amount"
                            value={rule.loan_amount_range?.max || ''}
                            onChange={handleRangeChange(index, 'loan_amount_range', 'max')}
                          />
                        </Grid>
                      </Grid>
                    </Grid>

                    {/* DTI Range */}
                    <Grid item xs={12}>
                      <Typography variant="body2" gutterBottom>DTI Ratio Range (%)</Typography>
                      <Grid container spacing={2}>
                        <Grid item xs={6}>
                          <TextField
                            fullWidth
                            type="number"
                            label="Min DTI"
                            value={rule.dti_range?.min || ''}
                            onChange={handleRangeChange(index, 'dti_range', 'min')}
                          />
                        </Grid>
                        <Grid item xs={6}>
                          <TextField
                            fullWidth
                            type="number"
                            label="Max DTI"
                            value={rule.dti_range?.max || ''}
                            onChange={handleRangeChange(index, 'dti_range', 'max')}
                          />
                        </Grid>
                      </Grid>
                    </Grid>

                    {/* Decision Outcome */}
                    <Grid item xs={12} md={6}>
                      <FormControl fullWidth required>
                        <InputLabel>Decision Outcome</InputLabel>
                        <Select
                          value={rule.decision_outcome}
                          onChange={handleChange(index, 'decision_outcome')}
                          label="Decision Outcome"
                        >
                          {Object.values(DecisionOutcome).map((outcome) => (
                            <MenuItem key={outcome} value={outcome}>
                              {outcome.replace(/_/g, ' ')}
                            </MenuItem>
                          ))}
                        </Select>
                      </FormControl>
                    </Grid>

                    {/* Decline Reason (if DECLINED) */}
                    {rule.decision_outcome === DecisionOutcome.DECLINED && (
                      <Grid item xs={12} md={6}>
                        <FormControl fullWidth>
                          <InputLabel>Decline Reason</InputLabel>
                          <Select
                            value={rule.decline_reason || ''}
                            onChange={handleChange(index, 'decline_reason')}
                            label="Decline Reason"
                          >
                            {Object.values(DeclineReason).map((reason) => (
                              <MenuItem key={reason} value={reason}>
                                {reason.replace(/_/g, ' ')}
                              </MenuItem>
                            ))}
                          </Select>
                        </FormControl>
                      </Grid>
                    )}

                    {/* Review Level (if MANUAL_REVIEW) */}
                    {rule.decision_outcome === DecisionOutcome.MANUAL_REVIEW && (
                      <Grid item xs={12} md={6}>
                        <FormControl fullWidth>
                          <InputLabel>Review Level</InputLabel>
                          <Select
                            value={rule.review_level || ''}
                            onChange={handleChange(index, 'review_level')}
                            label="Review Level"
                          >
                            <MenuItem value="L1">Level 1</MenuItem>
                            <MenuItem value="L2">Level 2</MenuItem>
                            <MenuItem value="L3">Level 3</MenuItem>
                            <MenuItem value="COMMITTEE">Committee</MenuItem>
                          </Select>
                        </FormControl>
                      </Grid>
                    )}

                    {rule.decision_outcome === DecisionOutcome.DECLINED && (
                      <Grid item xs={12}>
                        <TextField
                          fullWidth
                          multiline
                          rows={2}
                          label="Decline Message"
                          value={rule.decline_message || ''}
                          onChange={handleChange(index, 'decline_message')}
                          placeholder="Message to display to customer..."
                        />
                      </Grid>
                    )}

                    {rule.decision_outcome === DecisionOutcome.MANUAL_REVIEW && (
                      <Grid item xs={12}>
                        <TextField
                          fullWidth
                          multiline
                          rows={2}
                          label="Review Instructions"
                          value={rule.review_instructions || ''}
                          onChange={handleChange(index, 'review_instructions')}
                          placeholder="Instructions for the reviewer..."
                        />
                      </Grid>
                    )}
                  </Grid>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  );
};

export default DecisionMatrixStep;
