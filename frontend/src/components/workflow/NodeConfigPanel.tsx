/**
 * Node Configuration Panel
 * Property panel for configuring BPMN nodes
 */

import React, { useState, useEffect } from 'react';
import { Node } from 'reactflow';
import {
  Box,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Typography,
  Stack,
  Divider,
  Chip,
} from '@mui/material';

interface NodeConfigPanelProps {
  node: Node;
  onUpdate: (data: any) => void;
}

const NodeConfigPanel: React.FC<NodeConfigPanelProps> = ({ node, onUpdate }) => {
  const [label, setLabel] = useState(node.data.label);
  const [description, setDescription] = useState(node.data.description || '');
  const [config, setConfig] = useState(node.data.config || {});

  useEffect(() => {
    setLabel(node.data.label);
    setDescription(node.data.description || '');
    setConfig(node.data.config || {});
  }, [node]);

  const handleChange = (field: string, value: any) => {
    const newConfig = { ...config, [field]: value };
    setConfig(newConfig);
    onUpdate({ config: newConfig });
  };

  const handleLabelChange = (value: string) => {
    setLabel(value);
    onUpdate({ label: value });
  };

  const handleDescriptionChange = (value: string) => {
    setDescription(value);
    onUpdate({ description: value });
  };

  const renderUserTaskConfig = () => (
    <Stack spacing={2}>
      <FormControl fullWidth size="small">
        <InputLabel>Assignment Type</InputLabel>
        <Select
          value={config.assignment_type || 'role'}
          onChange={(e) => handleChange('assignment_type', e.target.value)}
          label="Assignment Type"
        >
          <MenuItem value="direct">Direct (Specific User)</MenuItem>
          <MenuItem value="role">Role-Based</MenuItem>
          <MenuItem value="expression">Expression</MenuItem>
        </Select>
      </FormControl>

      {config.assignment_type === 'role' && (
        <TextField
          fullWidth
          size="small"
          label="Assigned Role"
          value={config.assigned_role || ''}
          onChange={(e) => handleChange('assigned_role', e.target.value)}
          placeholder="e.g., loan_officer, manager"
        />
      )}

      {config.assignment_type === 'direct' && (
        <TextField
          fullWidth
          size="small"
          label="Assigned User ID"
          type="number"
          value={config.assigned_user_id || ''}
          onChange={(e) => handleChange('assigned_user_id', parseInt(e.target.value))}
        />
      )}

      <FormControl fullWidth size="small">
        <InputLabel>Priority</InputLabel>
        <Select
          value={config.priority || 'normal'}
          onChange={(e) => handleChange('priority', e.target.value)}
          label="Priority"
        >
          <MenuItem value="low">Low</MenuItem>
          <MenuItem value="normal">Normal</MenuItem>
          <MenuItem value="high">High</MenuItem>
          <MenuItem value="urgent">Urgent</MenuItem>
        </Select>
      </FormControl>

      <TextField
        fullWidth
        size="small"
        label="Due Date Expression"
        value={config.due_date || ''}
        onChange={(e) => handleChange('due_date', e.target.value)}
        placeholder="e.g., +3d (3 days from now)"
        helperText="Format: +Xd/h/w/m (days/hours/weeks/months)"
      />
    </Stack>
  );

  const renderServiceTaskConfig = () => (
    <Stack spacing={2}>
      <FormControl fullWidth size="small">
        <InputLabel>Implementation</InputLabel>
        <Select
          value={config.implementation || 'api'}
          onChange={(e) => handleChange('implementation', e.target.value)}
          label="Implementation"
        >
          <MenuItem value="api">API Call</MenuItem>
          <MenuItem value="expression">Expression</MenuItem>
        </Select>
      </FormControl>

      {config.implementation === 'api' && (
        <>
          <TextField
            fullWidth
            size="small"
            label="API Endpoint"
            value={config.api_endpoint || ''}
            onChange={(e) => handleChange('api_endpoint', e.target.value)}
            placeholder="https://api.example.com/endpoint"
          />

          <FormControl fullWidth size="small">
            <InputLabel>HTTP Method</InputLabel>
            <Select
              value={config.api_method || 'POST'}
              onChange={(e) => handleChange('api_method', e.target.value)}
              label="HTTP Method"
            >
              <MenuItem value="GET">GET</MenuItem>
              <MenuItem value="POST">POST</MenuItem>
              <MenuItem value="PUT">PUT</MenuItem>
              <MenuItem value="DELETE">DELETE</MenuItem>
            </Select>
          </FormControl>

          <TextField
            fullWidth
            size="small"
            label="Result Variable"
            value={config.result_variable || ''}
            onChange={(e) => handleChange('result_variable', e.target.value)}
            placeholder="Variable name to store result"
          />

          <FormControlLabel
            control={
              <Switch
                checked={config.retry_enabled || false}
                onChange={(e) => handleChange('retry_enabled', e.target.checked)}
              />
            }
            label="Enable Retry"
          />

          {config.retry_enabled && (
            <TextField
              fullWidth
              size="small"
              type="number"
              label="Max Retries"
              value={config.max_retries || 3}
              onChange={(e) => handleChange('max_retries', parseInt(e.target.value))}
            />
          )}
        </>
      )}

      {config.implementation === 'expression' && (
        <TextField
          fullWidth
          size="small"
          label="Expression"
          multiline
          rows={3}
          value={config.expression || ''}
          onChange={(e) => handleChange('expression', e.target.value)}
          placeholder="Python expression"
        />
      )}
    </Stack>
  );

  const renderScriptTaskConfig = () => (
    <Stack spacing={2}>
      <FormControl fullWidth size="small">
        <InputLabel>Script Format</InputLabel>
        <Select
          value={config.script_format || 'python'}
          onChange={(e) => handleChange('script_format', e.target.value)}
          label="Script Format"
        >
          <MenuItem value="python">Python</MenuItem>
          <MenuItem value="javascript">JavaScript</MenuItem>
        </Select>
      </FormControl>

      <TextField
        fullWidth
        size="small"
        label="Script"
        multiline
        rows={8}
        value={config.script || ''}
        onChange={(e) => handleChange('script', e.target.value)}
        placeholder="Enter script code..."
        helperText="Script has access to workflow variables"
      />

      <TextField
        fullWidth
        size="small"
        label="Result Variable"
        value={config.result_variable || ''}
        onChange={(e) => handleChange('result_variable', e.target.value)}
        placeholder="Variable name to store result"
      />

      <TextField
        fullWidth
        size="small"
        type="number"
        label="Timeout (seconds)"
        value={config.timeout || 300}
        onChange={(e) => handleChange('timeout', parseInt(e.target.value))}
      />
    </Stack>
  );

  const renderGatewayConfig = () => (
    <Stack spacing={2}>
      <Typography variant="body2" color="textSecondary">
        Gateway splits workflow into multiple paths based on conditions.
      </Typography>
      <Chip
        label={
          node.type === 'exclusive_gateway'
            ? 'XOR - One path only'
            : node.type === 'parallel_gateway'
            ? 'AND - All paths'
            : 'OR - Multiple matching paths'
        }
        color="primary"
        size="small"
      />
      <Typography variant="caption" color="textSecondary">
        Configure conditions on outgoing connections
      </Typography>
    </Stack>
  );

  const renderNodeSpecificConfig = () => {
    if (node.type === 'user_task') {
      return renderUserTaskConfig();
    } else if (node.type === 'service_task') {
      return renderServiceTaskConfig();
    } else if (node.type === 'script_task') {
      return renderScriptTaskConfig();
    } else if (node.type?.includes('gateway')) {
      return renderGatewayConfig();
    }
    return null;
  };

  return (
    <Box>
      <Stack spacing={3}>
        <Box>
          <Typography variant="subtitle2" gutterBottom>
            Basic Properties
          </Typography>
          <Stack spacing={2}>
            <TextField
              fullWidth
              size="small"
              label="Node Label"
              value={label}
              onChange={(e) => handleLabelChange(e.target.value)}
            />
            <TextField
              fullWidth
              size="small"
              label="Description"
              multiline
              rows={2}
              value={description}
              onChange={(e) => handleDescriptionChange(e.target.value)}
            />
            <TextField
              fullWidth
              size="small"
              label="Node ID"
              value={node.id}
              disabled
              helperText="Auto-generated unique identifier"
            />
          </Stack>
        </Box>

        <Divider />

        <Box>
          <Typography variant="subtitle2" gutterBottom>
            Configuration
          </Typography>
          {renderNodeSpecificConfig()}
        </Box>
      </Stack>
    </Box>
  );
};

export default NodeConfigPanel;
