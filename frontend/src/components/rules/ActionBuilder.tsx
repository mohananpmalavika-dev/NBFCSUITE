/**
 * Action Builder Component
 * 
 * Visual builder for creating rule actions
 */

import React from 'react';
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
  IconButton,
  Card,
  CardContent,
  Stack,
  Chip,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  DragIndicator as DragIcon,
  ArrowUpward as UpIcon,
  ArrowDownward as DownIcon,
} from '@mui/icons-material';
import rulesService from '../../services/rulesService';

interface Action {
  action_id: string;
  action_type: string;
  target_field?: string;
  target_value?: any;
  formula?: string;
  message?: string;
  route_to?: string;
  order: number;
}

interface ActionBuilderProps {
  actions: Action[];
  onChange: (actions: Action[]) => void;
  availableFields: Array<{ name: string; type: string; label: string }>;
  actionLabel?: string;
}

const ActionBuilder: React.FC<ActionBuilderProps> = ({
  actions,
  onChange,
  availableFields,
  actionLabel = 'Actions',
}) => {
  const actionTypes = [
    { value: 'set_value', label: 'Set Value', icon: '📝' },
    { value: 'calculate', label: 'Calculate', icon: '🔢' },
    { value: 'show_message', label: 'Show Message', icon: 'ℹ️' },
    { value: 'show_error', label: 'Show Error', icon: '❌' },
    { value: 'show_warning', label: 'Show Warning', icon: '⚠️' },
    { value: 'route_to', label: 'Route To', icon: '🔀' },
    { value: 'call_api', label: 'Call API', icon: '🌐' },
    { value: 'send_email', label: 'Send Email', icon: '📧' },
    { value: 'send_notification', label: 'Send Notification', icon: '🔔' },
    { value: 'trigger_workflow', label: 'Trigger Workflow', icon: '⚙️' },
    { value: 'log_event', label: 'Log Event', icon: '📋' },
  ];
  
  const handleAddAction = () => {
    const newAction: Action = {
      action_id: rulesService.generateActionId(),
      action_type: 'set_value',
      order: actions.length,
    };
    
    onChange([...actions, newAction]);
  };
  
  const handleRemoveAction = (index: number) => {
    const newActions = actions.filter((_, i) => i !== index);
    // Reorder
    newActions.forEach((action, i) => {
      action.order = i;
    });
    onChange(newActions);
  };
  
  const handleUpdateAction = (index: number, updates: Partial<Action>) => {
    const newActions = [...actions];
    newActions[index] = { ...newActions[index], ...updates };
    onChange(newActions);
  };
  
  const handleMoveUp = (index: number) => {
    if (index === 0) return;
    const newActions = [...actions];
    [newActions[index - 1], newActions[index]] = [newActions[index], newActions[index - 1]];
    newActions.forEach((action, i) => {
      action.order = i;
    });
    onChange(newActions);
  };
  
  const handleMoveDown = (index: number) => {
    if (index === actions.length - 1) return;
    const newActions = [...actions];
    [newActions[index], newActions[index + 1]] = [newActions[index + 1], newActions[index]];
    newActions.forEach((action, i) => {
      action.order = i;
    });
    onChange(newActions);
  };
  
  const renderActionFields = (action: Action, index: number) => {
    const actionType = actionTypes.find(t => t.value === action.action_type);
    
    switch (action.action_type) {
      case 'set_value':
        return (
          <>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel size="small">Target Field</InputLabel>
              <Select
                size="small"
                value={action.target_field || ''}
                onChange={(e) => handleUpdateAction(index, { target_field: e.target.value })}
                label="Target Field"
              >
                {availableFields.map((f) => (
                  <MenuItem key={f.name} value={f.name}>
                    {f.label || f.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <TextField
              fullWidth
              size="small"
              label="Value"
              value={action.target_value || ''}
              onChange={(e) => handleUpdateAction(index, { target_value: e.target.value })}
            />
          </>
        );
      
      case 'calculate':
        return (
          <>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel size="small">Target Field</InputLabel>
              <Select
                size="small"
                value={action.target_field || ''}
                onChange={(e) => handleUpdateAction(index, { target_field: e.target.value })}
                label="Target Field"
              >
                {availableFields.map((f) => (
                  <MenuItem key={f.name} value={f.name}>
                    {f.label || f.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <TextField
              fullWidth
              size="small"
              label="Formula"
              value={action.formula || ''}
              onChange={(e) => handleUpdateAction(index, { formula: e.target.value })}
              placeholder="e.g., field1 + field2 * 0.18"
              multiline
              rows={2}
            />
          </>
        );
      
      case 'show_message':
      case 'show_error':
      case 'show_warning':
        return (
          <TextField
            fullWidth
            size="small"
            label="Message"
            value={action.message || ''}
            onChange={(e) => handleUpdateAction(index, { message: e.target.value })}
            multiline
            rows={2}
          />
        );
      
      case 'route_to':
        return (
          <TextField
            fullWidth
            size="small"
            label="Route Destination"
            value={action.route_to || ''}
            onChange={(e) => handleUpdateAction(index, { route_to: e.target.value })}
            placeholder="e.g., approval_step"
          />
        );
      
      case 'call_api':
        return (
          <TextField
            fullWidth
            size="small"
            label="API URL"
            value={action.target_value || ''}
            onChange={(e) => handleUpdateAction(index, { target_value: e.target.value })}
            placeholder="https://api.example.com/endpoint"
          />
        );
      
      case 'send_email':
      case 'send_notification':
        return (
          <>
            <TextField
              fullWidth
              size="small"
              label="Recipients (comma-separated)"
              value={action.target_value || ''}
              onChange={(e) => handleUpdateAction(index, { target_value: e.target.value })}
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              size="small"
              label="Message"
              value={action.message || ''}
              onChange={(e) => handleUpdateAction(index, { message: e.target.value })}
              multiline
              rows={2}
            />
          </>
        );
      
      case 'trigger_workflow':
        return (
          <TextField
            fullWidth
            size="small"
            label="Workflow ID"
            value={action.target_value || ''}
            onChange={(e) => handleUpdateAction(index, { target_value: e.target.value })}
          />
        );
      
      case 'log_event':
        return (
          <TextField
            fullWidth
            size="small"
            label="Event Description"
            value={action.message || ''}
            onChange={(e) => handleUpdateAction(index, { message: e.target.value })}
            multiline
            rows={2}
          />
        );
      
      default:
        return null;
    }
  };
  
  return (
    <Paper sx={{ p: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="subtitle1" fontWeight="bold">
          {actionLabel}
        </Typography>
        <Button
          size="small"
          startIcon={<AddIcon />}
          onClick={handleAddAction}
          variant="contained"
        >
          Add Action
        </Button>
      </Box>
      
      {actions.length === 0 && (
        <Box sx={{ textAlign: 'center', py: 3 }}>
          <Typography color="text.secondary">
            No actions added. Click "Add Action" to start.
          </Typography>
        </Box>
      )}
      
      <Stack spacing={2}>
        {actions.map((action, index) => {
          const actionType = actionTypes.find(t => t.value === action.action_type);
          
          return (
            <Card key={action.action_id} variant="outlined">
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Box sx={{ display: 'flex', gap: 0.5, mr: 2 }}>
                    <IconButton
                      size="small"
                      onClick={() => handleMoveUp(index)}
                      disabled={index === 0}
                    >
                      <UpIcon fontSize="small" />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleMoveDown(index)}
                      disabled={index === actions.length - 1}
                    >
                      <DownIcon fontSize="small" />
                    </IconButton>
                  </Box>
                  
                  <Chip
                    label={`#${index + 1}`}
                    size="small"
                    sx={{ mr: 1 }}
                  />
                  
                  <FormControl sx={{ minWidth: 200, mr: 2 }}>
                    <InputLabel size="small">Action Type</InputLabel>
                    <Select
                      size="small"
                      value={action.action_type}
                      onChange={(e) => handleUpdateAction(index, { action_type: e.target.value })}
                      label="Action Type"
                    >
                      {actionTypes.map((type) => (
                        <MenuItem key={type.value} value={type.value}>
                          {type.icon} {type.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                  
                  <Box sx={{ flex: 1 }} />
                  
                  <IconButton
                    size="small"
                    onClick={() => handleRemoveAction(index)}
                    color="error"
                  >
                    <DeleteIcon />
                  </IconButton>
                </Box>
                
                {renderActionFields(action, index)}
                
                <Box sx={{ mt: 2 }}>
                  <Chip
                    label={actionType?.label}
                    size="small"
                    color="primary"
                    variant="outlined"
                  />
                </Box>
              </CardContent>
            </Card>
          );
        })}
      </Stack>
    </Paper>
  );
};

export default ActionBuilder;
