/**
 * Formula Builder Component
 * 
 * Visual builder for creating calculation formulas
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Chip,
  Stack,
  Grid,
  Card,
  CardContent,
  Divider,
  Alert,
} from '@mui/material';
import {
  Functions as FunctionIcon,
  Calculate as CalcIcon,
} from '@mui/icons-material';
import rulesService from '../../services/rulesService';

interface FormulaBuilderProps {
  formula: string;
  onChange: (formula: string) => void;
  availableFields: Array<{ name: string; type: string; label: string }>;
}

const FormulaBuilder: React.FC<FormulaBuilderProps> = ({
  formula,
  onChange,
  availableFields,
}) => {
  const [functions, setFunctions] = useState<any[]>([]);
  const [selectedFunction, setSelectedFunction] = useState<any>(null);
  
  useEffect(() => {
    loadFunctions();
  }, []);
  
  const loadFunctions = async () => {
    try {
      const funcs = await rulesService.getFormulaFunctions();
      setFunctions(funcs);
    } catch (err) {
      console.error('Failed to load functions:', err);
    }
  };
  
  const operators = [
    { symbol: '+', label: 'Add' },
    { symbol: '-', label: 'Subtract' },
    { symbol: '*', label: 'Multiply' },
    { symbol: '/', label: 'Divide' },
    { symbol: '%', label: 'Modulo' },
    { symbol: '(', label: 'Open Paren' },
    { symbol: ')', label: 'Close Paren' },
  ];
  
  const insertText = (text: string) => {
    onChange(formula + text);
  };
  
  const insertField = (fieldName: string) => {
    insertText(` ${fieldName} `);
  };
  
  const insertOperator = (op: string) => {
    insertText(` ${op} `);
  };
  
  const insertFunction = (func: any) => {
    const syntax = func.syntax.replace(func.function_name, func.function_name.toLowerCase());
    insertText(syntax);
    setSelectedFunction(func);
  };
  
  const clear = () => {
    onChange('');
  };
  
  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
        <CalcIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
        Formula Builder
      </Typography>
      
      <TextField
        fullWidth
        multiline
        rows={3}
        value={formula}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Enter formula or use buttons below"
        sx={{ mb: 2 }}
        label="Formula"
      />
      
      <Stack spacing={2}>
        <Box>
          <Typography variant="caption" color="text.secondary" gutterBottom display="block">
            Fields
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
            {availableFields.filter(f => f.type === 'number').map((field) => (
              <Chip
                key={field.name}
                label={field.label || field.name}
                onClick={() => insertField(field.name)}
                size="small"
                clickable
                color="primary"
                variant="outlined"
              />
            ))}
          </Box>
        </Box>
        
        <Divider />
        
        <Box>
          <Typography variant="caption" color="text.secondary" gutterBottom display="block">
            Operators
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
            {operators.map((op) => (
              <Button
                key={op.symbol}
                size="small"
                onClick={() => insertOperator(op.symbol)}
                variant="outlined"
                sx={{ minWidth: 40 }}
              >
                {op.symbol}
              </Button>
            ))}
          </Box>
        </Box>
        
        <Divider />
        
        <Box>
          <Typography variant="caption" color="text.secondary" gutterBottom display="block">
            Functions
          </Typography>
          <Grid container spacing={1}>
            {functions.map((func) => (
              <Grid item xs={6} sm={4} md={3} key={func.function_name}>
                <Button
                  fullWidth
                  size="small"
                  onClick={() => insertFunction(func)}
                  variant="outlined"
                  color="secondary"
                >
                  {func.function_name}
                </Button>
              </Grid>
            ))}
          </Grid>
        </Box>
        
        {selectedFunction && (
          <Alert severity="info">
            <Typography variant="body2" fontWeight="bold">
              {selectedFunction.function_name}
            </Typography>
            <Typography variant="caption" display="block">
              {selectedFunction.description}
            </Typography>
            <Typography variant="caption" display="block" sx={{ mt: 1 }}>
              Example: {selectedFunction.example}
            </Typography>
          </Alert>
        )}
        
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button size="small" onClick={clear} variant="outlined" color="error">
            Clear
          </Button>
        </Box>
      </Stack>
    </Paper>
  );
};

export default FormulaBuilder;
