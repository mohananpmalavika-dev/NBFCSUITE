/**
 * Execution Engine Configuration Component
 * 
 * Configure execution modes, priorities, and chaining for rule engine
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  FormControl,
  FormControlLabel,
  FormLabel,
  Radio,
  RadioGroup,
  Switch,
  TextField,
  Button,
  Divider,
  Grid,
  Card,
  CardContent,
  Chip,
  Alert,
  Select,
  MenuItem,
  InputLabel,
  IconButton,
  Tooltip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  Save as SaveIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
  Info as InfoIcon,
  ExpandMore as ExpandMoreIcon,
  PlayArrow as PlayIcon,
  Schedule as ScheduleIcon,
  TouchApp as TouchAppIcon,
  Speed as SpeedIcon,
  Link as LinkIcon,
} from '@mui/icons-material';

export interface ExecutionEngineConfig {
  config_id: string;
  config_name: string;
  execution_mode: 'real_time' | 'batch' | 'on_demand';
  trigger_events?: string[];
  trigger_conditions?: any;
  batch_schedule?: any;
  enable_priority_execution: boolean;
  priority_rules?: { [key: string]: number };
  enable_rule_chaining: boolean;
  rule_chains: any[];
  max_execution_time_seconds: number;
  enable_caching: boolean;
  cache_ttl_seconds: number;
  enable_execution_logging: boolean;
  log_level: string;
  enable_metrics: boolean;
  ruleset_id?: string;
  is_active: boolean;
}

interface ExecutionEngineConfigProps {
  rulesetId: string;
  config?: ExecutionEngineConfig;
  onSave: (config: ExecutionEngineConfig) => void;
  onCancel: () => void;
}

const ExecutionEngineConfigComponent: React.FC<ExecutionEngineConfigProps> = ({
  rulesetId,
  config,
  onSave,
  onCancel,
}) => {
  const [formData, setFormData] = useState<ExecutionEngineConfig>({
    config_id: config?.config_id || '',
    config_name: config?.config_name || 'Execution Config',
    execution_mode: config?.execution_mode || 'on_demand',
    trigger_events: config?.trigger_events || [],
    enable_priority_execution: config?.enable_priority_execution || false,
    priority_rules: config?.priority_rules || {},
    enable_rule_chaining: config?.enable_rule_chaining || false,
    rule_chains: config?.rule_chains || [],
    max_execution_time_seconds: config?.max_execution_time_seconds || 60,
    enable_caching: config?.enable_caching || false,
    cache_ttl_seconds: config?.cache_ttl_seconds || 300,
    enable_execution_logging: config?.enable_execution_logging !== false,
    log_level: config?.log_level || 'INFO',
    enable_metrics: config?.enable_metrics || false,
    ruleset_id: rulesetId,
    is_active: config?.is_active !== false,
  });

  const [newEvent, setNewEvent] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleExecutionModeChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      execution_mode: event.target.value as any,
    });
  };

  const handleSwitchChange = (field: keyof ExecutionEngineConfig) => (event: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [field]: event.target.checked,
    });
  };

  const handleTextChange = (field: keyof ExecutionEngineConfig) => (event: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [field]: event.target.value,
    });
  };

  const handleNumberChange = (field: keyof ExecutionEngineConfig) => (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(event.target.value, 10);
    if (!isNaN(value)) {
      setFormData({
        ...formData,
        [field]: value,
      });
    }
  };

  const handleAddTriggerEvent = () => {
    if (newEvent.trim()) {
      setFormData({
        ...formData,
        trigger_events: [...(formData.trigger_events || []), newEvent.trim()],
      });
      setNewEvent('');
    }
  };

  const handleRemoveTriggerEvent = (index: number) => {
    const updated = [...(formData.trigger_events || [])];
    updated.splice(index, 1);
    setFormData({
      ...formData,
      trigger_events: updated,
    });
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.config_name.trim()) {
      newErrors.config_name = 'Configuration name is required';
    }

    if (formData.max_execution_time_seconds < 1 || formData.max_execution_time_seconds > 3600) {
      newErrors.max_execution_time_seconds = 'Must be between 1 and 3600 seconds';
    }

    if (formData.enable_caching && (formData.cache_ttl_seconds < 1 || formData.cache_ttl_seconds > 86400)) {
      newErrors.cache_ttl_seconds = 'Must be between 1 and 86400 seconds';
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
      <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <SpeedIcon color="primary" />
          Execution Engine Configuration
        </Typography>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Configure how and when rules are executed
        </Typography>
        <Divider sx={{ my: 2 }} />

        {/* Basic Settings */}
        <Box sx={{ mb: 3 }}>
          <TextField
            fullWidth
            label="Configuration Name"
            value={formData.config_name}
            onChange={handleTextChange('config_name')}
            error={!!errors.config_name}
            helperText={errors.config_name}
            sx={{ mb: 2 }}
          />

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
        </Box>

        {/* Execution Mode */}
        <Accordion defaultExpanded>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="h6">Execution Mode</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <FormControl component="fieldset" fullWidth>
              <RadioGroup
                value={formData.execution_mode}
                onChange={handleExecutionModeChange}
              >
                <Card variant="outlined" sx={{ mb: 2 }}>
                  <CardContent>
                    <FormControlLabel
                      value="real_time"
                      control={<Radio />}
                      label={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <PlayIcon color="success" />
                          <Typography variant="subtitle1">Real-Time</Typography>
                        </Box>
                      }
                    />
                    <Typography variant="body2" color="text.secondary" sx={{ ml: 4 }}>
                      Execute rules immediately on every transaction. Optimized for speed and low latency.
                    </Typography>
                  </CardContent>
                </Card>

                <Card variant="outlined" sx={{ mb: 2 }}>
                  <CardContent>
                    <FormControlLabel
                      value="batch"
                      control={<Radio />}
                      label={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <ScheduleIcon color="info" />
                          <Typography variant="subtitle1">Batch</Typography>
                        </Box>
                      }
                    />
                    <Typography variant="body2" color="text.secondary" sx={{ ml: 4 }}>
                      Execute rules at scheduled intervals. Suitable for bulk processing and reports.
                    </Typography>
                  </CardContent>
                </Card>

                <Card variant="outlined">
                  <CardContent>
                    <FormControlLabel
                      value="on_demand"
                      control={<Radio />}
                      label={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <TouchAppIcon color="warning" />
                          <Typography variant="subtitle1">On-Demand</Typography>
                        </Box>
                      }
                    />
                    <Typography variant="body2" color="text.secondary" sx={{ ml: 4 }}>
                      Execute rules only when explicitly triggered by user or API call.
                    </Typography>
                  </CardContent>
                </Card>
              </RadioGroup>
            </FormControl>

            {/* Trigger Events for Real-Time Mode */}
            {formData.execution_mode === 'real_time' && (
              <Box sx={{ mt: 3 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Trigger Events
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Specify events that trigger rule execution
                </Typography>
                
                <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                  <TextField
                    size="small"
                    placeholder="e.g., loan_application_submitted"
                    value={newEvent}
                    onChange={(e) => setNewEvent(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleAddTriggerEvent()}
                    fullWidth
                  />
                  <Button
                    variant="outlined"
                    startIcon={<AddIcon />}
                    onClick={handleAddTriggerEvent}
                  >
                    Add
                  </Button>
                </Box>

                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {formData.trigger_events?.map((event, index) => (
                    <Chip
                      key={index}
                      label={event}
                      onDelete={() => handleRemoveTriggerEvent(index)}
                      color="primary"
                      variant="outlined"
                    />
                  ))}
                </Box>
              </Box>
            )}
          </AccordionDetails>
        </Accordion>

        {/* Priority Execution */}
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="h6">Priority-Based Execution</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <FormControlLabel
              control={
                <Switch
                  checked={formData.enable_priority_execution}
                  onChange={handleSwitchChange('enable_priority_execution')}
                  color="primary"
                />
              }
              label="Enable Priority Execution"
            />
            <Alert severity="info" sx={{ mt: 2 }}>
              When enabled, rules execute in priority order (highest first). 
              Configure priorities in individual rule settings.
            </Alert>
          </AccordionDetails>
        </Accordion>

        {/* Rule Chaining */}
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <LinkIcon />
              Rule Chaining
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            <FormControlLabel
              control={
                <Switch
                  checked={formData.enable_rule_chaining}
                  onChange={handleSwitchChange('enable_rule_chaining')}
                  color="primary"
                />
              }
              label="Enable Rule Chaining"
            />
            <Alert severity="info" sx={{ mt: 2 }}>
              When enabled, rules execute in sequence with output pass-through. 
              Configure chains in the Rule Chain Builder.
            </Alert>
            {formData.enable_rule_chaining && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  {formData.rule_chains.length} chain(s) configured
                </Typography>
              </Box>
            )}
          </AccordionDetails>
        </Accordion>

        {/* Performance Settings */}
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="h6">Performance Settings</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Max Execution Time (seconds)"
                  type="number"
                  value={formData.max_execution_time_seconds}
                  onChange={handleNumberChange('max_execution_time_seconds')}
                  error={!!errors.max_execution_time_seconds}
                  helperText={errors.max_execution_time_seconds || 'Maximum time for rule execution'}
                  inputProps={{ min: 1, max: 3600 }}
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.enable_caching}
                      onChange={handleSwitchChange('enable_caching')}
                      color="primary"
                    />
                  }
                  label="Enable Caching"
                />
              </Grid>

              {formData.enable_caching && (
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Cache TTL (seconds)"
                    type="number"
                    value={formData.cache_ttl_seconds}
                    onChange={handleNumberChange('cache_ttl_seconds')}
                    error={!!errors.cache_ttl_seconds}
                    helperText={errors.cache_ttl_seconds || 'Time-to-live for cached results'}
                    inputProps={{ min: 1, max: 86400 }}
                  />
                </Grid>
              )}
            </Grid>
          </AccordionDetails>
        </Accordion>

        {/* Monitoring & Logging */}
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="h6">Monitoring & Logging</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.enable_execution_logging}
                      onChange={handleSwitchChange('enable_execution_logging')}
                      color="primary"
                    />
                  }
                  label="Enable Execution Logging"
                />
              </Grid>

              {formData.enable_execution_logging && (
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <InputLabel>Log Level</InputLabel>
                    <Select
                      value={formData.log_level}
                      label="Log Level"
                      onChange={(e) => setFormData({ ...formData, log_level: e.target.value })}
                    >
                      <MenuItem value="DEBUG">DEBUG</MenuItem>
                      <MenuItem value="INFO">INFO</MenuItem>
                      <MenuItem value="WARNING">WARNING</MenuItem>
                      <MenuItem value="ERROR">ERROR</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
              )}

              <Grid item xs={12} md={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.enable_metrics}
                      onChange={handleSwitchChange('enable_metrics')}
                      color="primary"
                    />
                  }
                  label="Enable Performance Metrics"
                />
              </Grid>
            </Grid>
          </AccordionDetails>
        </Accordion>

        {/* Action Buttons */}
        <Box sx={{ mt: 3, display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
          <Button
            variant="outlined"
            onClick={onCancel}
          >
            Cancel
          </Button>
          <Button
            variant="contained"
            startIcon={<SaveIcon />}
            onClick={handleSubmit}
            color="primary"
          >
            Save Configuration
          </Button>
        </Box>
      </Paper>
    </Box>
  );
};

export default ExecutionEngineConfigComponent;
