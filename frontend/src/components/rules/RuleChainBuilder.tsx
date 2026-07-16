/**
 * Rule Chain Builder Component
 * 
 * Build and configure rule chains with sequential execution
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Divider,
  Grid,
  Card,
  CardContent,
  CardActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Alert,
  Chip,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
} from '@mui/material';
import {
  Save as SaveIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  ArrowUpward as ArrowUpwardIcon,
  ArrowDownward as ArrowDownwardIcon,
  Link as LinkIcon,
  PlayArrow as PlayArrowIcon,
  Info as InfoIcon,
  DragIndicator as DragIndicatorIcon,
} from '@mui/icons-material';

export interface RuleChainStep {
  step_id: string;
  step_name: string;
  step_order: number;
  rule_id: string;
  rule_type: string;
  is_active: boolean;
  skip_on_condition?: string;
  pass_output_to_next: boolean;
  output_field_mappings?: { [key: string]: string };
  stop_on_failure: boolean;
  failure_action?: string;
  max_retries: number;
  retry_delay_seconds: number;
  description?: string;
}

export interface RuleChain {
  chain_id: string;
  chain_name: string;
  description?: string;
  steps: RuleChainStep[];
  execution_strategy: string;
  required_inputs: string[];
  expected_outputs: string[];
  share_context: boolean;
  initial_context?: any;
  is_active: boolean;
  version: string;
  tags: string[];
}

interface RuleChainBuilderProps {
  rulesetId: string;
  availableRules: Array<{ rule_id: string; rule_name: string; rule_type: string }>;
  chain?: RuleChain;
  onSave: (chain: RuleChain) => void;
  onCancel: () => void;
}

const RuleChainBuilder: React.FC<RuleChainBuilderProps> = ({
  rulesetId,
  availableRules,
  chain,
  onSave,
  onCancel,
}) => {
  const [formData, setFormData] = useState<RuleChain>({
    chain_id: chain?.chain_id || '',
    chain_name: chain?.chain_name || '',
    description: chain?.description || '',
    steps: chain?.steps || [],
    execution_strategy: chain?.execution_strategy || 'stop_on_first_failure',
    required_inputs: chain?.required_inputs || [],
    expected_outputs: chain?.expected_outputs || [],
    share_context: chain?.share_context !== false,
    initial_context: chain?.initial_context || {},
    is_active: chain?.is_active !== false,
    version: chain?.version || '1.0',
    tags: chain?.tags || [],
  });

  const [stepDialogOpen, setStepDialogOpen] = useState(false);
  const [editingStep, setEditingStep] = useState<RuleChainStep | null>(null);
  const [editingStepIndex, setEditingStepIndex] = useState<number | null>(null);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const [newInput, setNewInput] = useState('');
  const [newOutput, setNewOutput] = useState('');
  const [newTag, setNewTag] = useState('');

  const executionStrategies = [
    { value: 'stop_on_first_failure', label: 'Stop on First Failure' },
    { value: 'continue_on_failure', label: 'Continue on Failure' },
    { value: 'collect_all_violations', label: 'Collect All Violations' },
  ];

  const failureActions = [
    { value: 'skip_remaining', label: 'Skip Remaining Steps' },
    { value: 'continue', label: 'Continue' },
    { value: 'retry', label: 'Retry' },
  ];

  const handleTextChange = (field: keyof RuleChain) => (event: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [field]: event.target.value,
    });
  };

  const handleSwitchChange = (field: keyof RuleChain) => (event: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [field]: event.target.checked,
    });
  };

  const handleAddInput = () => {
    if (newInput.trim() && !formData.required_inputs.includes(newInput.trim())) {
      setFormData({
        ...formData,
        required_inputs: [...formData.required_inputs, newInput.trim()],
      });
      setNewInput('');
    }
  };

  const handleRemoveInput = (index: number) => {
    const updated = [...formData.required_inputs];
    updated.splice(index, 1);
    setFormData({
      ...formData,
      required_inputs: updated,
    });
  };

  const handleAddOutput = () => {
    if (newOutput.trim() && !formData.expected_outputs.includes(newOutput.trim())) {
      setFormData({
        ...formData,
        expected_outputs: [...formData.expected_outputs, newOutput.trim()],
      });
      setNewOutput('');
    }
  };

  const handleRemoveOutput = (index: number) => {
    const updated = [...formData.expected_outputs];
    updated.splice(index, 1);
    setFormData({
      ...formData,
      expected_outputs: updated,
    });
  };

  const handleAddTag = () => {
    if (newTag.trim() && !formData.tags.includes(newTag.trim())) {
      setFormData({
        ...formData,
        tags: [...formData.tags, newTag.trim()],
      });
      setNewTag('');
    }
  };

  const handleRemoveTag = (index: number) => {
    const updated = [...formData.tags];
    updated.splice(index, 1);
    setFormData({
      ...formData,
      tags: updated,
    });
  };

  const handleAddStep = () => {
    setEditingStep({
      step_id: `step_${Date.now()}`,
      step_name: '',
      step_order: formData.steps.length,
      rule_id: '',
      rule_type: '',
      is_active: true,
      pass_output_to_next: true,
      stop_on_failure: true,
      max_retries: 0,
      retry_delay_seconds: 0,
    });
    setEditingStepIndex(null);
    setStepDialogOpen(true);
  };

  const handleEditStep = (index: number) => {
    setEditingStep({ ...formData.steps[index] });
    setEditingStepIndex(index);
    setStepDialogOpen(true);
  };

  const handleSaveStep = (step: RuleChainStep) => {
    const steps = [...formData.steps];
    
    if (editingStepIndex !== null) {
      steps[editingStepIndex] = step;
    } else {
      steps.push(step);
    }
    
    // Reorder steps
    steps.forEach((s, i) => s.step_order = i);
    
    setFormData({
      ...formData,
      steps,
    });
    
    setStepDialogOpen(false);
    setEditingStep(null);
    setEditingStepIndex(null);
  };

  const handleDeleteStep = (index: number) => {
    const steps = [...formData.steps];
    steps.splice(index, 1);
    steps.forEach((s, i) => s.step_order = i);
    
    setFormData({
      ...formData,
      steps,
    });
  };

  const handleMoveStep = (index: number, direction: 'up' | 'down') => {
    const steps = [...formData.steps];
    const newIndex = direction === 'up' ? index - 1 : index + 1;
    
    if (newIndex >= 0 && newIndex < steps.length) {
      [steps[index], steps[newIndex]] = [steps[newIndex], steps[index]];
      steps.forEach((s, i) => s.step_order = i);
      
      setFormData({
        ...formData,
        steps,
      });
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.chain_name.trim()) {
      newErrors.chain_name = 'Chain name is required';
    }

    if (formData.steps.length === 0) {
      newErrors.steps = 'At least one step is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = () => {
    if (validateForm()) {
      onSave(formData);
    }
  };

  return (
    <Box>
      <Paper elevation={2} sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <LinkIcon color="primary" />
          Rule Chain Builder
        </Typography>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Create sequential rule execution chains with output pass-through
        </Typography>
        <Divider sx={{ my: 2 }} />

        {/* Basic Settings */}
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Chain Name"
              value={formData.chain_name}
              onChange={handleTextChange('chain_name')}
              error={!!errors.chain_name}
              helperText={errors.chain_name}
              required
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              multiline
              rows={2}
              label="Description"
              value={formData.description}
              onChange={handleTextChange('description')}
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <FormControlLabel
              control={
                <Switch
                  checked={formData.is_active}
                  onChange={handleSwitchChange('is_active')}
                  color="primary"
                />
              }
              label="Active"
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <FormControlLabel
              control={
                <Switch
                  checked={formData.share_context}
                  onChange={handleSwitchChange('share_context')}
                  color="primary"
                />
              }
              label="Share Context Across Steps"
            />
          </Grid>

          {/* Execution Strategy */}
          <Grid item xs={12}>
            <FormControl fullWidth>
              <InputLabel>Execution Strategy</InputLabel>
              <Select
                value={formData.execution_strategy}
                label="Execution Strategy"
                onChange={(e) => setFormData({ ...formData, execution_strategy: e.target.value })}
              >
                {executionStrategies.map((strategy) => (
                  <MenuItem key={strategy.value} value={strategy.value}>
                    {strategy.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          {/* Required Inputs */}
          <Grid item xs={12}>
            <Typography variant="subtitle1" gutterBottom>
              Required Input Fields
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
              <TextField
                size="small"
                placeholder="e.g., credit_score"
                value={newInput}
                onChange={(e) => setNewInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleAddInput()}
                fullWidth
              />
              <Button
                variant="outlined"
                startIcon={<AddIcon />}
                onClick={handleAddInput}
              >
                Add
              </Button>
            </Box>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {formData.required_inputs.map((input, index) => (
                <Chip
                  key={index}
                  label={input}
                  onDelete={() => handleRemoveInput(index)}
                  color="primary"
                  variant="outlined"
                />
              ))}
            </Box>
          </Grid>

          {/* Expected Outputs */}
          <Grid item xs={12}>
            <Typography variant="subtitle1" gutterBottom>
              Expected Output Fields
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
              <TextField
                size="small"
                placeholder="e.g., approval_status"
                value={newOutput}
                onChange={(e) => setNewOutput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleAddOutput()}
                fullWidth
              />
              <Button
                variant="outlined"
                startIcon={<AddIcon />}
                onClick={handleAddOutput}
              >
                Add
              </Button>
            </Box>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {formData.expected_outputs.map((output, index) => (
                <Chip
                  key={index}
                  label={output}
                  onDelete={() => handleRemoveOutput(index)}
                  color="secondary"
                  variant="outlined"
                />
              ))}
            </Box>
          </Grid>

          {/* Tags */}
          <Grid item xs={12}>
            <Typography variant="subtitle1" gutterBottom>
              Tags
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
              <TextField
                size="small"
                placeholder="e.g., loan-approval"
                value={newTag}
                onChange={(e) => setNewTag(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleAddTag()}
                fullWidth
              />
              <Button
                variant="outlined"
                startIcon={<AddIcon />}
                onClick={handleAddTag}
              >
                Add
              </Button>
            </Box>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {formData.tags.map((tag, index) => (
                <Chip
                  key={index}
                  label={tag}
                  onDelete={() => handleRemoveTag(index)}
                  size="small"
                />
              ))}
            </Box>
          </Grid>
        </Grid>

        {/* Chain Steps */}
        <Box sx={{ mt: 4 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">
              Chain Steps ({formData.steps.length})
            </Typography>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={handleAddStep}
            >
              Add Step
            </Button>
          </Box>

          {errors.steps && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {errors.steps}
            </Alert>
          )}

          {formData.steps.length === 0 ? (
            <Alert severity="info">
              No steps configured. Click "Add Step" to create the first step in your chain.
            </Alert>
          ) : (
            <List>
              {formData.steps.map((step, index) => {
                const rule = availableRules.find(r => r.rule_id === step.rule_id);
                
                return (
                  <Card key={step.step_id} variant="outlined" sx={{ mb: 2 }}>
                    <CardContent>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        <Box sx={{ display: 'flex', flexDirection: 'column' }}>
                          <IconButton
                            size="small"
                            onClick={() => handleMoveStep(index, 'up')}
                            disabled={index === 0}
                          >
                            <ArrowUpwardIcon />
                          </IconButton>
                          <IconButton
                            size="small"
                            onClick={() => handleMoveStep(index, 'down')}
                            disabled={index === formData.steps.length - 1}
                          >
                            <ArrowDownwardIcon />
                          </IconButton>
                        </Box>

                        <Box sx={{ flexGrow: 1 }}>
                          <Typography variant="subtitle1" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            Step {index + 1}: {step.step_name}
                            {!step.is_active && <Chip label="Inactive" size="small" />}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Rule: {rule?.rule_name || step.rule_id} ({step.rule_type})
                          </Typography>
                          <Box sx={{ mt: 1, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                            {step.pass_output_to_next && (
                              <Chip label="Pass Output" size="small" color="primary" variant="outlined" />
                            )}
                            {step.stop_on_failure && (
                              <Chip label="Stop on Failure" size="small" color="error" variant="outlined" />
                            )}
                            {step.max_retries > 0 && (
                              <Chip label={`Retry ${step.max_retries}x`} size="small" color="info" variant="outlined" />
                            )}
                          </Box>
                        </Box>

                        <Box>
                          <IconButton onClick={() => handleEditStep(index)}>
                            <EditIcon />
                          </IconButton>
                          <IconButton onClick={() => handleDeleteStep(index)} color="error">
                            <DeleteIcon />
                          </IconButton>
                        </Box>
                      </Box>
                    </CardContent>
                  </Card>
                );
              })}
            </List>
          )}
        </Box>

        {/* Action Buttons */}
        <Box sx={{ mt: 3, display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
          <Button variant="outlined" onClick={onCancel}>
            Cancel
          </Button>
          <Button
            variant="contained"
            startIcon={<SaveIcon />}
            onClick={handleSubmit}
            color="primary"
          >
            Save Chain
          </Button>
        </Box>
      </Paper>

      {/* Step Dialog */}
      <StepEditorDialog
        open={stepDialogOpen}
        step={editingStep}
        availableRules={availableRules}
        onSave={handleSaveStep}
        onCancel={() => {
          setStepDialogOpen(false);
          setEditingStep(null);
          setEditingStepIndex(null);
        }}
      />
    </Box>
  );
};

// Step Editor Dialog Component
interface StepEditorDialogProps {
  open: boolean;
  step: RuleChainStep | null;
  availableRules: Array<{ rule_id: string; rule_name: string; rule_type: string }>;
  onSave: (step: RuleChainStep) => void;
  onCancel: () => void;
}

const StepEditorDialog: React.FC<StepEditorDialogProps> = ({
  open,
  step,
  availableRules,
  onSave,
  onCancel,
}) => {
  const [formData, setFormData] = useState<RuleChainStep | null>(step);
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    setFormData(step);
  }, [step]);

  if (!formData) return null;

  const handleTextChange = (field: keyof RuleChainStep) => (event: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [field]: event.target.value,
    });
  };

  const handleNumberChange = (field: keyof RuleChainStep) => (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(event.target.value, 10);
    if (!isNaN(value)) {
      setFormData({
        ...formData,
        [field]: value,
      });
    }
  };

  const handleSwitchChange = (field: keyof RuleChainStep) => (event: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [field]: event.target.checked,
    });
  };

  const handleRuleSelect = (ruleId: string) => {
    const rule = availableRules.find(r => r.rule_id === ruleId);
    if (rule) {
      setFormData({
        ...formData,
        rule_id: rule.rule_id,
        rule_type: rule.rule_type,
      });
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.step_name.trim()) {
      newErrors.step_name = 'Step name is required';
    }

    if (!formData.rule_id) {
      newErrors.rule_id = 'Rule selection is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSave = () => {
    if (validateForm()) {
      onSave(formData);
    }
  };

  return (
    <Dialog open={open} onClose={onCancel} maxWidth="md" fullWidth>
      <DialogTitle>
        {step?.step_id ? 'Edit Step' : 'Add Step'}
      </DialogTitle>
      <DialogContent>
        <Grid container spacing={2} sx={{ mt: 1 }}>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Step Name"
              value={formData.step_name}
              onChange={handleTextChange('step_name')}
              error={!!errors.step_name}
              helperText={errors.step_name}
              required
            />
          </Grid>

          <Grid item xs={12}>
            <FormControl fullWidth error={!!errors.rule_id} required>
              <InputLabel>Select Rule</InputLabel>
              <Select
                value={formData.rule_id}
                label="Select Rule"
                onChange={(e) => handleRuleSelect(e.target.value)}
              >
                {availableRules.map((rule) => (
                  <MenuItem key={rule.rule_id} value={rule.rule_id}>
                    {rule.rule_name} ({rule.rule_type})
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              multiline
              rows={2}
              label="Description"
              value={formData.description || ''}
              onChange={handleTextChange('description')}
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <FormControlLabel
              control={
                <Switch
                  checked={formData.is_active}
                  onChange={handleSwitchChange('is_active')}
                  color="primary"
                />
              }
              label="Active"
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <FormControlLabel
              control={
                <Switch
                  checked={formData.pass_output_to_next}
                  onChange={handleSwitchChange('pass_output_to_next')}
                  color="primary"
                />
              }
              label="Pass Output to Next Step"
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <FormControlLabel
              control={
                <Switch
                  checked={formData.stop_on_failure}
                  onChange={handleSwitchChange('stop_on_failure')}
                  color="primary"
                />
              }
              label="Stop on Failure"
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Max Retries"
              type="number"
              value={formData.max_retries}
              onChange={handleNumberChange('max_retries')}
              inputProps={{ min: 0, max: 10 }}
            />
          </Grid>

          {formData.max_retries > 0 && (
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Retry Delay (seconds)"
                type="number"
                value={formData.retry_delay_seconds}
                onChange={handleNumberChange('retry_delay_seconds')}
                inputProps={{ min: 0, max: 300 }}
              />
            </Grid>
          )}

          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Skip Condition (optional)"
              value={formData.skip_on_condition || ''}
              onChange={handleTextChange('skip_on_condition')}
              helperText="Python expression to skip this step (e.g., credit_score < 700)"
            />
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={onCancel}>Cancel</Button>
        <Button onClick={handleSave} variant="contained" color="primary">
          Save Step
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default RuleChainBuilder;
