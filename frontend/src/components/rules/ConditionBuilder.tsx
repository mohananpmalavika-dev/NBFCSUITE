/**
 * Condition Builder Component
 * 
 * Visual builder for creating rule conditions with AND/OR/NOT logic
 */

import React, { useState } from 'react';
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
  Chip,
  Card,
  CardContent,
  Stack,
  Divider,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  ContentCopy as CopyIcon,
  AccountTree as GroupIcon,
} from '@mui/icons-material';
import rulesService from '../../services/rulesService';

interface Condition {
  condition_id: string;
  field: string;
  field_type: string;
  operator: string;
  value: any;
  value2?: any;
}

interface ConditionGroup {
  group_id: string;
  logical_operator: 'and' | 'or' | 'not';
  conditions: (Condition | ConditionGroup)[];
}

interface ConditionBuilderProps {
  conditionGroup: ConditionGroup;
  onChange: (conditionGroup: ConditionGroup) => void;
  availableFields: Array<{ name: string; type: string; label: string }>;
  depth?: number;
}

const ConditionBuilder: React.FC<ConditionBuilderProps> = ({
  conditionGroup,
  onChange,
  availableFields,
  depth = 0,
}) => {
  const maxDepth = 3;
  
  const handleAddCondition = () => {
    const newCondition: Condition = {
      condition_id: rulesService.generateConditionId(),
      field: availableFields[0]?.name || '',
      field_type: availableFields[0]?.type || 'string',
      operator: 'equals',
      value: '',
    };
    
    onChange({
      ...conditionGroup,
      conditions: [...conditionGroup.conditions, newCondition],
    });
  };
  
  const handleAddGroup = () => {
    if (depth >= maxDepth) return;
    
    const newGroup: ConditionGroup = {
      group_id: `group_${Date.now()}`,
      logical_operator: 'and',
      conditions: [],
    };
    
    onChange({
      ...conditionGroup,
      conditions: [...conditionGroup.conditions, newGroup],
    });
  };
  
  const handleRemoveCondition = (index: number) => {
    const newConditions = conditionGroup.conditions.filter((_, i) => i !== index);
    onChange({ ...conditionGroup, conditions: newConditions });
  };
  
  const handleUpdateCondition = (index: number, updates: Partial<Condition>) => {
    const newConditions = [...conditionGroup.conditions];
    newConditions[index] = { ...newConditions[index] as Condition, ...updates };
    onChange({ ...conditionGroup, conditions: newConditions });
  };
  
  const handleUpdateGroup = (index: number, updatedGroup: ConditionGroup) => {
    const newConditions = [...conditionGroup.conditions];
    newConditions[index] = updatedGroup;
    onChange({ ...conditionGroup, conditions: newConditions });
  };
  
  const handleLogicalOperatorChange = (operator: 'and' | 'or' | 'not') => {
    onChange({ ...conditionGroup, logical_operator: operator });
  };
  
  const handleFieldChange = (index: number, fieldName: string) => {
    const field = availableFields.find(f => f.name === fieldName);
    if (field) {
      handleUpdateCondition(index, {
        field: fieldName,
        field_type: field.type,
        operator: 'equals',
        value: '',
      });
    }
  };
  
  const renderCondition = (condition: Condition, index: number) => {
    const field = availableFields.find(f => f.name === condition.field);
    const operators = rulesService.getOperatorsByType(condition.field_type);
    const currentOperator = operators.find(op => op.value === condition.operator);
    const needsValue2 = condition.operator === 'between';
    const needsNoValue = ['is_null', 'is_not_null'].includes(condition.operator);
    
    return (
      <Card key={condition.condition_id} variant="outlined" sx={{ mb: 1 }}>
        <CardContent>
          <Stack direction="row" spacing={2} alignItems="center">
            <FormControl sx={{ minWidth: 180 }}>
              <InputLabel size="small">Field</InputLabel>
              <Select
                size="small"
                value={condition.field}
                onChange={(e) => handleFieldChange(index, e.target.value)}
                label="Field"
              >
                {availableFields.map((f) => (
                  <MenuItem key={f.name} value={f.name}>
                    {f.label || f.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            
            <FormControl sx={{ minWidth: 200 }}>
              <InputLabel size="small">Operator</InputLabel>
              <Select
                size="small"
                value={condition.operator}
                onChange={(e) => handleUpdateCondition(index, { operator: e.target.value })}
                label="Operator"
              >
                {operators.map((op) => (
                  <MenuItem key={op.value} value={op.value}>
                    {op.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            
            {!needsNoValue && (
              <TextField
                size="small"
                label="Value"
                value={condition.value}
                onChange={(e) => handleUpdateCondition(index, { value: e.target.value })}
                type={condition.field_type === 'number' ? 'number' : 'text'}
                sx={{ minWidth: 150 }}
              />
            )}
            
            {needsValue2 && (
              <TextField
                size="small"
                label="Value 2"
                value={condition.value2 || ''}
                onChange={(e) => handleUpdateCondition(index, { value2: e.target.value })}
                type={condition.field_type === 'number' ? 'number' : 'text'}
                sx={{ minWidth: 150 }}
              />
            )}
            
            <Box sx={{ flex: 1 }} />
            
            <IconButton
              size="small"
              onClick={() => handleRemoveCondition(index)}
              color="error"
            >
              <DeleteIcon />
            </IconButton>
          </Stack>
          
          <Box sx={{ mt: 1 }}>
            <Chip
              label={`${field?.label || condition.field} ${currentOperator?.label} ${condition.value}`}
              size="small"
              color="primary"
              variant="outlined"
            />
          </Box>
        </CardContent>
      </Card>
    );
  };
  
  const isCondition = (item: any): item is Condition => {
    return 'condition_id' in item;
  };
  
  return (
    <Paper
      sx={{
        p: 2,
        bgcolor: depth > 0 ? 'grey.50' : 'white',
        border: depth > 0 ? '2px dashed' : '1px solid',
        borderColor: depth > 0 ? 'primary.main' : 'divider',
      }}
    >
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {depth > 0 && <GroupIcon color="primary" />}
          <Typography variant="subtitle2" color="text.secondary">
            {depth === 0 ? 'IF Conditions' : `Nested Group (Level ${depth})`}
          </Typography>
        </Box>
        
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            size="small"
            startIcon={<AddIcon />}
            onClick={handleAddCondition}
            variant="outlined"
          >
            Add Condition
          </Button>
          {depth < maxDepth && (
            <Button
              size="small"
              startIcon={<GroupIcon />}
              onClick={handleAddGroup}
              variant="outlined"
              color="secondary"
            >
              Add Group
            </Button>
          )}
        </Box>
      </Box>
      
      {conditionGroup.conditions.length > 1 && (
        <Box sx={{ mb: 2 }}>
          <Typography variant="caption" sx={{ mr: 1 }}>
            Logical Operator:
          </Typography>
          <Select
            size="small"
            value={conditionGroup.logical_operator}
            onChange={(e) => handleLogicalOperatorChange(e.target.value as any)}
            sx={{ minWidth: 100 }}
          >
            <MenuItem value="and">AND (All must match)</MenuItem>
            <MenuItem value="or">OR (Any must match)</MenuItem>
            <MenuItem value="not">NOT (None must match)</MenuItem>
          </Select>
        </Box>
      )}
      
      {conditionGroup.conditions.length === 0 && (
        <Box sx={{ textAlign: 'center', py: 3 }}>
          <Typography color="text.secondary">
            No conditions added. Click "Add Condition" to start building.
          </Typography>
        </Box>
      )}
      
      <Stack spacing={1}>
        {conditionGroup.conditions.map((item, index) => (
          <React.Fragment key={index}>
            {index > 0 && (
              <Box sx={{ display: 'flex', justifyContent: 'center', my: 1 }}>
                <Chip
                  label={conditionGroup.logical_operator.toUpperCase()}
                  size="small"
                  color="primary"
                />
              </Box>
            )}
            
            {isCondition(item) ? (
              renderCondition(item, index)
            ) : (
              <ConditionBuilder
                conditionGroup={item}
                onChange={(updated) => handleUpdateGroup(index, updated)}
                availableFields={availableFields}
                depth={depth + 1}
              />
            )}
          </React.Fragment>
        ))}
      </Stack>
    </Paper>
  );
};

export default ConditionBuilder;
