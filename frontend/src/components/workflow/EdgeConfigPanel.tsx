/**
 * Edge Configuration Panel
 * Configure conditions on sequence flows
 */

import React, { useState, useEffect } from 'react';
import { Edge } from 'reactflow';
import {
  Box,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Typography,
  Stack,
  Switch,
  FormControlLabel,
  Divider,
} from '@mui/material';

interface EdgeConfigPanelProps {
  edge: Edge;
  onUpdate: (data: any) => void;
}

const EdgeConfigPanel: React.FC<EdgeConfigPanelProps> = ({ edge, onUpdate }) => {
  const [label, setLabel] = useState(edge.label || '');
  const [hasCondition, setHasCondition] = useState(!!edge.data?.condition);
  const [conditionType, setConditionType] = useState(edge.data?.condition?.type || 'simple');
  const [variable, setVariable] = useState(edge.data?.condition?.variable || '');
  const [operator, setOperator] = useState(edge.data?.condition?.operator || '==');
  const [value, setValue] = useState(edge.data?.condition?.value || '');
  const [script, setScript] = useState(edge.data?.condition?.script || '');

  useEffect(() => {
    setLabel(edge.label || '');
    setHasCondition(!!edge.data?.condition);
    if (edge.data?.condition) {
      setConditionType(edge.data.condition.type || 'simple');
      setVariable(edge.data.condition.variable || '');
      setOperator(edge.data.condition.operator || '==');
      setValue(edge.data.condition.value || '');
      setScript(edge.data.condition.script || '');
    }
  }, [edge]);

  const handleLabelChange = (newLabel: string) => {
    setLabel(newLabel);
    // Update label directly on edge
    onUpdate({ label: newLabel });
  };

  const handleConditionChange = () => {
    if (!hasCondition) {
      // Enable condition
      const condition = {
        type: 'simple',
        variable: '',
        operator: '==',
        value: '',
      };
      setHasCondition(true);
      onUpdate({ condition });
    } else {
      // Disable condition
      setHasCondition(false);
      onUpdate({ condition: null });
    }
  };

  const updateCondition = () => {
    const condition = conditionType === 'simple'
      ? {
          type: 'simple',
          variable,
          operator,
          value,
        }
      : {
          type: 'script',
          script,
          language: 'python',
        };
    
    onUpdate({ condition });
  };

  return (
    <Box>
      <Stack spacing={3}>
        <Box>
          <Typography variant="subtitle2" gutterBottom>
            Connection Properties
          </Typography>
          <Stack spacing={2}>
            <TextField
              fullWidth
              size="small"
              label="Label"
              value={label}
              onChange={(e) => handleLabelChange(e.target.value)}
              placeholder="e.g., Approved, Rejected"
            />
            <TextField
              fullWidth
              size="small"
              label="From Node"
              value={edge.source}
              disabled
            />
            <TextField
              fullWidth
              size="small"
              label="To Node"
              value={edge.target}
              disabled
            />
          </Stack>
        </Box>

        <Divider />

        <Box>
          <Typography variant="subtitle2" gutterBottom>
            Condition
          </Typography>
          <FormControlLabel
            control={
              <Switch
                checked={hasCondition}
                onChange={handleConditionChange}
              />
            }
            label="Enable Condition"
          />

          {hasCondition && (
            <Stack spacing={2} mt={2}>
              <FormControl fullWidth size="small">
                <InputLabel>Condition Type</InputLabel>
                <Select
                  value={conditionType}
                  onChange={(e) => {
                    setConditionType(e.target.value);
                    updateCondition();
                  }}
                  label="Condition Type"
                >
                  <MenuItem value="simple">Simple Comparison</MenuItem>
                  <MenuItem value="script">Script Expression</MenuItem>
                </Select>
              </FormControl>

              {conditionType === 'simple' && (
                <>
                  <TextField
                    fullWidth
                    size="small"
                    label="Variable Name"
                    value={variable}
                    onChange={(e) => {
                      setVariable(e.target.value);
                      updateCondition();
                    }}
                    placeholder="e.g., approval_status"
                  />

                  <FormControl fullWidth size="small">
                    <InputLabel>Operator</InputLabel>
                    <Select
                      value={operator}
                      onChange={(e) => {
                        setOperator(e.target.value);
                        updateCondition();
                      }}
                      label="Operator"
                    >
                      <MenuItem value="==">Equals (==)</MenuItem>
                      <MenuItem value="!=">Not Equals (!=)</MenuItem>
                      <MenuItem value=">">Greater Than (&gt;)</MenuItem>
                      <MenuItem value="<">Less Than (&lt;)</MenuItem>
                      <MenuItem value=">=">Greater or Equal (&gt;=)</MenuItem>
                      <MenuItem value="<=">Less or Equal (&lt;=)</MenuItem>
                      <MenuItem value="in">In List</MenuItem>
                      <MenuItem value="not_in">Not In List</MenuItem>
                    </Select>
                  </FormControl>

                  <TextField
                    fullWidth
                    size="small"
                    label="Value"
                    value={value}
                    onChange={(e) => {
                      setValue(e.target.value);
                      updateCondition();
                    }}
                    placeholder="e.g., approved"
                    helperText="Use JSON format for complex values"
                  />

                  <Typography variant="caption" color="textSecondary">
                    Example: variable = "status", operator = "==", value = "approved"
                  </Typography>
                </>
              )}

              {conditionType === 'script' && (
                <>
                  <TextField
                    fullWidth
                    size="small"
                    label="Python Expression"
                    multiline
                    rows={4}
                    value={script}
                    onChange={(e) => {
                      setScript(e.target.value);
                      updateCondition();
                    }}
                    placeholder="e.g., amount > 100000 and risk_score < 5"
                    helperText="Return True/False. Has access to workflow variables."
                  />

                  <Typography variant="caption" color="textSecondary">
                    Example: amount &gt; 100000 and approval_status == "approved"
                  </Typography>
                </>
              )}
            </Stack>
          )}
        </Box>

        <Box>
          <Typography variant="caption" color="textSecondary">
            Conditions are evaluated when workflow reaches a gateway. 
            For exclusive gateways (XOR), the first matching condition is taken.
            For inclusive gateways (OR), all matching conditions are taken.
            For parallel gateways (AND), all paths are taken regardless of conditions.
          </Typography>
        </Box>
      </Stack>
    </Box>
  );
};

export default EdgeConfigPanel;
