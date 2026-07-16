/**
 * SLA Configurator Component
 * 
 * Configure SLA settings and escalation rules
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Button,
  Grid,
  Card,
  CardContent,
  CardActions,
  IconButton,
  Chip,
  Switch,
  FormControlLabel,
  Divider,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Stepper,
  Step,
  StepLabel,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  ExpandMore as ExpandMoreIcon,
  AccessTime as TimeIcon,
  Notifications as NotifyIcon,
  TrendingUp as EscalateIcon,
  Save as SaveIcon,
} from '@mui/icons-material';
import slaService, { SLAEscalationConfig, EscalationRule } from '../../services/slaService';

interface SLAConfiguratorProps {
  entityType: string;
  onSave?: (config: SLAEscalationConfig) => void;
  existingConfig?: SLAEscalationConfig;
}

const SLAConfigurator: React.FC<SLAConfiguratorProps> = ({
  entityType,
  onSave,
  existingConfig
}) => {
  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  // SLA Configuration
  const [configName, setConfigName] = useState(existingConfig?.name || '');
  const [slaName, setSlaName] = useState(existingConfig?.sla.name || '');
  const [slaType, setSlaType] = useState<string>(existingConfig?.sla.sla_type || 'resolution_time');
  const [timeValue, setTimeValue] = useState(existingConfig?.sla.time_value || 24);
  const [timeUnit, setTimeUnit] = useState(existingConfig?.sla.time_unit || 'hours');
  const [calculationType, setCalculationType] = useState(existingConfig?.sla.calculation_type || 'business_hours');
  const [warningThreshold, setWarningThreshold] = useState(existingConfig?.sla.warning_threshold || 70);
  const [criticalThreshold, setCriticalThreshold] = useState(existingConfig?.sla.critical_threshold || 90);
  const [allowPause, setAllowPause] = useState(existingConfig?.sla.allow_pause ?? true);
  const [pauseOnCustomer, setPauseOnCustomer] = useState(existingConfig?.sla.pause_on_customer_action ?? true);

  // Business Hours
  const [businessHoursEnabled, setBusinessHoursEnabled] = useState(
    existingConfig?.sla.business_hours_config?.enabled ?? true
  );
  const [businessHours, setBusinessHours] = useState({
    monday: { start: '09:00', end: '17:00' },
    tuesday: { start: '09:00', end: '17:00' },
    wednesday: { start: '09:00', end: '17:00' },
    thursday: { start: '09:00', end: '17:00' },
    friday: { start: '09:00', end: '17:00' },
    saturday: null,
    sunday: null,
  });

  // Escalation Rules
  const [escalationRules, setEscalationRules] = useState<Partial<EscalationRule>[]>(
    existingConfig?.escalation_rules || []
  );

  const steps = ['Basic Settings', 'Business Hours', 'Escalation Rules', 'Review'];

  const handleAddEscalationRule = () => {
    setEscalationRules([
      ...escalationRules,
      {
        name: '',
        trigger_after_hours: 2,
        escalation_type: 'soft',
        send_reminder_to_assignee: true,
        notify_supervisor: false,
        escalate_to_next_level: false,
        repeat_escalation: false,
        max_escalations: 3,
        is_active: true,
      }
    ]);
  };

  const handleRemoveEscalationRule = (index: number) => {
    setEscalationRules(escalationRules.filter((_, i) => i !== index));
  };

  const handleUpdateEscalationRule = (index: number, field: string, value: any) => {
    const updated = [...escalationRules];
    updated[index] = { ...updated[index], [field]: value };
    setEscalationRules(updated);
  };

  const handleSave = async () => {
    setLoading(true);
    setError(null);

    try {
      const config: any = {
        name: configName,
        entity_type: entityType,
        sla: {
          name: slaName,
          entity_type: entityType,
          sla_type: slaType,
          time_value: timeValue,
          time_unit: timeUnit,
          calculation_type: calculationType,
          warning_threshold: warningThreshold,
          critical_threshold: criticalThreshold,
          allow_pause: allowPause,
          pause_on_customer_action: pauseOnCustomer,
          business_hours_config: businessHoursEnabled ? {
            enabled: true,
            ...businessHours,
            timezone: 'Asia/Kolkata'
          } : undefined
        },
        escalation_rules: escalationRules.map((rule, idx) => ({
          ...rule,
          name: rule.name || `Escalation Level ${idx + 1}`
        })),
        send_breach_notification: true
      };

      const result = await slaService.createConfiguration(config);
      setSuccess(true);
      
      if (onSave) {
        onSave(result);
      }
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Failed to save SLA configuration');
    } finally {
      setLoading(false);
    }
  };

  const renderBasicSettings = () => (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <TextField
          fullWidth
          label="Configuration Name"
          value={configName}
          onChange={(e) => setConfigName(e.target.value)}
          placeholder="e.g., Loan Approval SLA"
          required
        />
      </Grid>

      <Grid item xs={12}>
        <TextField
          fullWidth
          label="SLA Name"
          value={slaName}
          onChange={(e) => setSlaName(e.target.value)}
          placeholder="e.g., Loan Processing Time"
          required
        />
      </Grid>

      <Grid item xs={12} md={6}>
        <FormControl fullWidth>
          <InputLabel>SLA Type</InputLabel>
          <Select
            value={slaType}
            onChange={(e) => setSlaType(e.target.value)}
            label="SLA Type"
          >
            <MenuItem value="response_time">Response Time</MenuItem>
            <MenuItem value="resolution_time">Resolution Time</MenuItem>
            <MenuItem value="approval_time">Approval Time</MenuItem>
          </Select>
        </FormControl>
      </Grid>

      <Grid item xs={12} md={6}>
        <FormControl fullWidth>
          <InputLabel>Calculation Type</InputLabel>
          <Select
            value={calculationType}
            onChange={(e) => setCalculationType(e.target.value)}
            label="Calculation Type"
          >
            <MenuItem value="calendar_hours">Calendar Hours (24/7)</MenuItem>
            <MenuItem value="business_hours">Business Hours Only</MenuItem>
            <MenuItem value="working_days">Working Days Only</MenuItem>
          </Select>
        </FormControl>
      </Grid>

      <Grid item xs={6} md={3}>
        <TextField
          fullWidth
          type="number"
          label="Time Value"
          value={timeValue}
          onChange={(e) => setTimeValue(parseInt(e.target.value))}
          required
        />
      </Grid>

      <Grid item xs={6} md={3}>
        <FormControl fullWidth>
          <InputLabel>Unit</InputLabel>
          <Select
            value={timeUnit}
            onChange={(e) => setTimeUnit(e.target.value)}
            label="Unit"
          >
            <MenuItem value="minutes">Minutes</MenuItem>
            <MenuItem value="hours">Hours</MenuItem>
            <MenuItem value="days">Days</MenuItem>
          </Select>
        </FormControl>
      </Grid>

      <Grid item xs={6} md={3}>
        <TextField
          fullWidth
          type="number"
          label="Warning Threshold (%)"
          value={warningThreshold}
          onChange={(e) => setWarningThreshold(parseFloat(e.target.value))}
          inputProps={{ min: 0, max: 100 }}
        />
      </Grid>

      <Grid item xs={6} md={3}>
        <TextField
          fullWidth
          type="number"
          label="Critical Threshold (%)"
          value={criticalThreshold}
          onChange={(e) => setCriticalThreshold(parseFloat(e.target.value))}
          inputProps={{ min: 0, max: 100 }}
        />
      </Grid>

      <Grid item xs={12} md={6}>
        <FormControlLabel
          control={
            <Switch
              checked={allowPause}
              onChange={(e) => setAllowPause(e.target.checked)}
            />
          }
          label="Allow SLA Pause"
        />
      </Grid>

      <Grid item xs={12} md={6}>
        <FormControlLabel
          control={
            <Switch
              checked={pauseOnCustomer}
              onChange={(e) => setPauseOnCustomer(e.target.checked)}
            />
          }
          label="Pause on Customer Action"
        />
      </Grid>
    </Grid>
  );

  const renderBusinessHours = () => (
    <Box>
      <FormControlLabel
        control={
          <Switch
            checked={businessHoursEnabled}
            onChange={(e) => setBusinessHoursEnabled(e.target.checked)}
          />
        }
        label="Enable Business Hours Calculation"
      />

      {businessHoursEnabled && (
        <Grid container spacing={2} sx={{ mt: 2 }}>
          {['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'].map((day) => (
            <Grid item xs={12} key={day}>
              <Paper sx={{ p: 2 }}>
                <Grid container spacing={2} alignItems="center">
                  <Grid item xs={3}>
                    <Typography variant="body1" sx={{ textTransform: 'capitalize' }}>
                      {day}
                    </Typography>
                  </Grid>
                  <Grid item xs={3}>
                    <TextField
                      fullWidth
                      type="time"
                      label="Start"
                      value={businessHours[day as keyof typeof businessHours]?.start || '09:00'}
                      onChange={(e) => setBusinessHours({
                        ...businessHours,
                        [day]: { ...businessHours[day as keyof typeof businessHours], start: e.target.value } as any
                      })}
                      disabled={!businessHours[day as keyof typeof businessHours]}
                    />
                  </Grid>
                  <Grid item xs={3}>
                    <TextField
                      fullWidth
                      type="time"
                      label="End"
                      value={businessHours[day as keyof typeof businessHours]?.end || '17:00'}
                      onChange={(e) => setBusinessHours({
                        ...businessHours,
                        [day]: { ...businessHours[day as keyof typeof businessHours], end: e.target.value } as any
                      })}
                      disabled={!businessHours[day as keyof typeof businessHours]}
                    />
                  </Grid>
                  <Grid item xs={3}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={!!businessHours[day as keyof typeof businessHours]}
                          onChange={(e) => setBusinessHours({
                            ...businessHours,
                            [day]: e.target.checked ? { start: '09:00', end: '17:00' } : null
                          })}
                        />
                      }
                      label="Working Day"
                    />
                  </Grid>
                </Grid>
              </Paper>
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  );

  const renderEscalationRules = () => (
    <Box>
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h6">Escalation Rules</Typography>
        <Button
          startIcon={<AddIcon />}
          onClick={handleAddEscalationRule}
          variant="contained"
        >
          Add Rule
        </Button>
      </Box>

      {escalationRules.length === 0 && (
        <Alert severity="info">
          No escalation rules defined. Click "Add Rule" to create escalation rules.
        </Alert>
      )}

      {escalationRules.map((rule, index) => (
        <Accordion key={index} defaultExpanded={index === escalationRules.length - 1}>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
              <Typography>
                {rule.name || `Rule ${index + 1}`}
              </Typography>
              <Chip
                label={rule.escalation_type}
                size="small"
                color={rule.escalation_type === 'hard' ? 'error' : rule.escalation_type === 'notify' ? 'warning' : 'default'}
              />
              <Typography variant="body2" color="text.secondary" sx={{ ml: 'auto' }}>
                Trigger: {rule.trigger_after_hours}h
              </Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Rule Name"
                  value={rule.name || ''}
                  onChange={(e) => handleUpdateEscalationRule(index, 'name', e.target.value)}
                  placeholder="e.g., 2 Hour Reminder"
                />
              </Grid>

              <Grid item xs={6}>
                <TextField
                  fullWidth
                  type="number"
                  label="Trigger After (hours)"
                  value={rule.trigger_after_hours || 0}
                  onChange={(e) => handleUpdateEscalationRule(index, 'trigger_after_hours', parseFloat(e.target.value))}
                />
              </Grid>

              <Grid item xs={6}>
                <FormControl fullWidth>
                  <InputLabel>Escalation Type</InputLabel>
                  <Select
                    value={rule.escalation_type || 'soft'}
                    onChange={(e) => handleUpdateEscalationRule(index, 'escalation_type', e.target.value)}
                    label="Escalation Type"
                  >
                    <MenuItem value="soft">Soft (Reminder)</MenuItem>
                    <MenuItem value="notify">Notify Supervisor</MenuItem>
                    <MenuItem value="hard">Hard (Auto-Transfer)</MenuItem>
                    <MenuItem value="multi_level">Multi-Level</MenuItem>
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={rule.send_reminder_to_assignee ?? true}
                      onChange={(e) => handleUpdateEscalationRule(index, 'send_reminder_to_assignee', e.target.checked)}
                    />
                  }
                  label="Send Reminder to Assignee"
                />
              </Grid>

              <Grid item xs={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={rule.notify_supervisor ?? false}
                      onChange={(e) => handleUpdateEscalationRule(index, 'notify_supervisor', e.target.checked)}
                    />
                  }
                  label="Notify Supervisor"
                />
              </Grid>

              {rule.escalation_type === 'hard' && (
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={rule.escalate_to_next_level ?? false}
                        onChange={(e) => handleUpdateEscalationRule(index, 'escalate_to_next_level', e.target.checked)}
                      />
                    }
                    label="Auto-Escalate to Next Level"
                  />
                </Grid>
              )}

              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={rule.repeat_escalation ?? false}
                      onChange={(e) => handleUpdateEscalationRule(index, 'repeat_escalation', e.target.checked)}
                    />
                  }
                  label="Repeat Escalation"
                />
              </Grid>

              {rule.repeat_escalation && (
                <>
                  <Grid item xs={6}>
                    <TextField
                      fullWidth
                      type="number"
                      label="Repeat Interval (hours)"
                      value={rule.repeat_interval_hours || 1}
                      onChange={(e) => handleUpdateEscalationRule(index, 'repeat_interval_hours', parseFloat(e.target.value))}
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <TextField
                      fullWidth
                      type="number"
                      label="Max Escalations"
                      value={rule.max_escalations || 3}
                      onChange={(e) => handleUpdateEscalationRule(index, 'max_escalations', parseInt(e.target.value))}
                    />
                  </Grid>
                </>
              )}

              <Grid item xs={12}>
                <Button
                  startIcon={<DeleteIcon />}
                  onClick={() => handleRemoveEscalationRule(index)}
                  color="error"
                  variant="outlined"
                  fullWidth
                >
                  Remove Rule
                </Button>
              </Grid>
            </Grid>
          </AccordionDetails>
        </Accordion>
      ))}
    </Box>
  );

  const renderReview = () => (
    <Box>
      <Card sx={{ mb: 2 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>SLA Configuration</Typography>
          <Grid container spacing={2}>
            <Grid item xs={6}>
              <Typography variant="body2" color="text.secondary">Name:</Typography>
              <Typography variant="body1">{configName}</Typography>
            </Grid>
            <Grid item xs={6}>
              <Typography variant="body2" color="text.secondary">Entity Type:</Typography>
              <Typography variant="body1">{entityType}</Typography>
            </Grid>
            <Grid item xs={6}>
              <Typography variant="body2" color="text.secondary">SLA Duration:</Typography>
              <Typography variant="body1">{timeValue} {timeUnit}</Typography>
            </Grid>
            <Grid item xs={6}>
              <Typography variant="body2" color="text.secondary">Calculation:</Typography>
              <Typography variant="body1">{calculationType}</Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>Escalation Rules ({escalationRules.length})</Typography>
          {escalationRules.map((rule, index) => (
            <Box key={index} sx={{ mb: 1 }}>
              <Typography variant="body2">
                • {rule.name || `Rule ${index + 1}`} - Trigger after {rule.trigger_after_hours}h ({rule.escalation_type})
              </Typography>
            </Box>
          ))}
        </CardContent>
      </Card>
    </Box>
  );

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>
        SLA Configuration
      </Typography>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      {success && <Alert severity="success" sx={{ mb: 2 }}>SLA configuration saved successfully!</Alert>}

      <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
        {steps.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>

      <Box sx={{ mb: 3 }}>
        {activeStep === 0 && renderBasicSettings()}
        {activeStep === 1 && renderBusinessHours()}
        {activeStep === 2 && renderEscalationRules()}
        {activeStep === 3 && renderReview()}
      </Box>

      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
        <Button
          disabled={activeStep === 0}
          onClick={() => setActiveStep(activeStep - 1)}
        >
          Back
        </Button>
        <Box>
          {activeStep < steps.length - 1 ? (
            <Button
              variant="contained"
              onClick={() => setActiveStep(activeStep + 1)}
            >
              Next
            </Button>
          ) : (
            <Button
              variant="contained"
              color="primary"
              startIcon={<SaveIcon />}
              onClick={handleSave}
              disabled={loading}
            >
              {loading ? 'Saving...' : 'Save Configuration'}
            </Button>
          )}
        </Box>
      </Box>
    </Paper>
  );
};

export default SLAConfigurator;
