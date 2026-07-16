/**
 * Rule Test Interface Component
 * 
 * Test rules with sample data and view execution results
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Grid,
  Alert,
  Card,
  CardContent,
  Divider,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableRow,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  CircularProgress,
} from '@mui/material';
import {
  PlayArrow as RunIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  ExpandMore as ExpandIcon,
  Timer as TimerIcon,
} from '@mui/icons-material';
import rulesService from '../../services/rulesService';

interface RuleTestInterfaceProps {
  rulesetId: string;
  entityType: string;
}

const RuleTestInterface: React.FC<RuleTestInterfaceProps> = ({
  rulesetId,
  entityType,
}) => {
  const [testData, setTestData] = useState('{\n  \n}');
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [ruleset, setRuleset] = useState<any>(null);
  
  useEffect(() => {
    loadRuleset();
  }, [rulesetId]);
  
  const loadRuleset = async () => {
    try {
      const data = await rulesService.getRuleset(rulesetId);
      setRuleset(data);
      
      // Generate sample data based on rules
      const sampleData = generateSampleData(data);
      setTestData(JSON.stringify(sampleData, null, 2));
    } catch (err) {
      console.error('Failed to load ruleset:', err);
    }
  };
  
  const generateSampleData = (ruleset: any): any => {
    const sample: any = {};
    
    // Extract fields from all rules
    const allRules = [
      ...(ruleset.decision_rules || []),
      ...(ruleset.validation_rules || []),
      ...(ruleset.calculation_rules || []),
    ];
    
    allRules.forEach((rule: any) => {
      if (rule.if_condition?.conditions) {
        extractFieldsFromConditions(rule.if_condition.conditions, sample);
      }
      if (rule.conditions?.conditions) {
        extractFieldsFromConditions(rule.conditions.conditions, sample);
      }
    });
    
    return sample;
  };
  
  const extractFieldsFromConditions = (conditions: any[], sample: any) => {
    conditions.forEach((cond: any) => {
      if (cond.field) {
        // Set sample value based on field type
        if (cond.field_type === 'number') {
          sample[cond.field] = 0;
        } else if (cond.field_type === 'boolean') {
          sample[cond.field] = false;
        } else {
          sample[cond.field] = '';
        }
      }
      if (cond.conditions) {
        extractFieldsFromConditions(cond.conditions, sample);
      }
    });
  };
  
  const handleRunTest = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    
    try {
      const data = JSON.parse(testData);
      
      const context = {
        context_id: `test_${Date.now()}`,
        entity_type: entityType,
        data: data,
        tenant_id: 1, // Mock tenant
      };
      
      const executionResult = await rulesService.executeRules(rulesetId, context);
      setResult(executionResult);
    } catch (err: any) {
      setError(err.message || 'Test execution failed');
    } finally {
      setLoading(false);
    }
  };
  
  const renderTestResults = () => {
    if (!result) return null;
    
    return (
      <Box sx={{ mt: 3 }}>
        <Paper sx={{ p: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            {result.success ? (
              <SuccessIcon color="success" sx={{ mr: 1 }} />
            ) : (
              <ErrorIcon color="error" sx={{ mr: 1 }} />
            )}
            <Typography variant="h6">
              Test {result.success ? 'Passed' : 'Failed'}
            </Typography>
            <Box sx={{ flex: 1 }} />
            <Chip
              icon={<TimerIcon />}
              label={`${result.execution_time_ms.toFixed(2)} ms`}
              size="small"
              color="info"
            />
          </Box>
          
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                    Rules Executed
                  </Typography>
                  <Typography variant="h4">{result.rules_executed.length}</Typography>
                  <Box sx={{ mt: 1 }}>
                    {result.rules_matched.map((ruleId: string) => (
                      <Chip key={ruleId} label={ruleId} size="small" sx={{ mr: 0.5, mb: 0.5 }} />
                    ))}
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                    Validation Errors
                  </Typography>
                  <Typography variant="h4" color={result.validation_errors.length > 0 ? 'error' : 'success'}>
                    {result.validation_errors.length}
                  </Typography>
                  {result.validation_errors.length > 0 && (
                    <Box sx={{ mt: 1 }}>
                      {result.validation_errors.map((err: any, idx: number) => (
                        <Alert key={idx} severity="error" sx={{ mb: 0.5 }}>
                          {err.message}
                        </Alert>
                      ))}
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Grid>
          </Grid>
          
          <Divider sx={{ my: 2 }} />
          
          <Accordion>
            <AccordionSummary expandIcon={<ExpandIcon />}>
              <Typography variant="subtitle1">Output Data</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Box sx={{ bgcolor: 'grey.100', p: 2, borderRadius: 1, overflow: 'auto' }}>
                <pre style={{ margin: 0, fontSize: '12px' }}>
                  {JSON.stringify(result.output_data, null, 2)}
                </pre>
              </Box>
            </AccordionDetails>
          </Accordion>
          
          <Accordion>
            <AccordionSummary expandIcon={<ExpandIcon />}>
              <Typography variant="subtitle1">Calculated Fields</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <TableContainer>
                <Table size="small">
                  <TableBody>
                    {Object.entries(result.calculated_fields || {}).map(([key, value]) => (
                      <TableRow key={key}>
                        <TableCell><strong>{key}</strong></TableCell>
                        <TableCell>{String(value)}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </AccordionDetails>
          </Accordion>
          
          {result.is_eligible !== undefined && (
            <Accordion>
              <AccordionSummary expandIcon={<ExpandIcon />}>
                <Typography variant="subtitle1">Eligibility Result</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Box>
                  <Typography variant="body1">
                    <strong>Eligible:</strong> {result.is_eligible ? 'Yes' : 'No'}
                  </Typography>
                  {result.eligibility_score !== null && (
                    <Typography variant="body1">
                      <strong>Score:</strong> {result.eligibility_score}
                    </Typography>
                  )}
                </Box>
              </AccordionDetails>
            </Accordion>
          )}
          
          <Accordion>
            <AccordionSummary expandIcon={<ExpandIcon />}>
              <Typography variant="subtitle1">Execution Log</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Box sx={{ bgcolor: 'grey.100', p: 2, borderRadius: 1, maxHeight: 300, overflow: 'auto' }}>
                {result.execution_log.map((log: string, idx: number) => (
                  <Typography key={idx} variant="caption" display="block" sx={{ fontFamily: 'monospace' }}>
                    [{idx + 1}] {log}
                  </Typography>
                ))}
              </Box>
            </AccordionDetails>
          </Accordion>
        </Paper>
      </Box>
    );
  };
  
  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Rule Test Interface
      </Typography>
      
      <Paper sx={{ p: 2, mb: 2 }}>
        <Typography variant="subtitle1" gutterBottom>
          Test Data (JSON)
        </Typography>
        <TextField
          fullWidth
          multiline
          rows={12}
          value={testData}
          onChange={(e) => setTestData(e.target.value)}
          placeholder='{\n  "field1": "value1",\n  "field2": 123\n}'
          sx={{ fontFamily: 'monospace' }}
        />
        
        <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
          <Button
            variant="contained"
            startIcon={loading ? <CircularProgress size={20} /> : <RunIcon />}
            onClick={handleRunTest}
            disabled={loading}
          >
            {loading ? 'Running Test...' : 'Run Test'}
          </Button>
          <Button
            variant="outlined"
            onClick={() => setTestData(JSON.stringify(generateSampleData(ruleset), null, 2))}
          >
            Reset to Sample
          </Button>
        </Box>
        
        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}
      </Paper>
      
      {renderTestResults()}
    </Box>
  );
};

export default RuleTestInterface;
