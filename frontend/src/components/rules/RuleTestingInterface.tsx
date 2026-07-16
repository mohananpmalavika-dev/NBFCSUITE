/**
 * Rule Testing Interface Component
 * 
 * Test rules with dry-run, what-if analysis, and impact assessment
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Divider,
  Grid,
  Card,
  CardContent,
  Chip,
  Alert,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  CircularProgress,
  LinearProgress,
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
  Assessment as AssessmentIcon,
  CompareArrows as CompareIcon,
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  ExpandMore as ExpandMoreIcon,
  Code as CodeIcon,
  Science as ScienceIcon,
} from '@mui/icons-material';

export interface TestCase {
  test_case_id: string;
  test_case_name: string;
  ruleset_id: string;
  input_data: any;
  expected_output?: any;
  assertions: Assertion[];
  created_at?: string;
}

export interface Assertion {
  type: string;
  field: string;
  operator: string;
  expected: any;
}

export interface TestResult {
  test_result_id: string;
  test_case_id: string;
  ruleset_id: string;
  execution_mode: string;
  passed: boolean;
  execution_result: any;
  assertions_passed: number;
  assertions_failed: number;
  assertion_details: any[];
  execution_time_ms: number;
  matches_expected?: boolean;
  output_diff?: any;
  executed_at: string;
}

export interface ImpactAssessment {
  assessment_id: string;
  ruleset_id: string;
  sample_size: number;
  affected_count: number;
  affected_percentage: number;
  result_changes: any[];
  risk_level: string;
  risk_factors: string[];
  recommendations: string[];
  assessed_at: string;
}

interface RuleTestingInterfaceProps {
  rulesetId: string;
}

const RuleTestingInterface: React.FC<RuleTestingInterfaceProps> = ({ rulesetId }) => {
  const [activeTab, setActiveTab] = useState(0);
  const [testCases, setTestCases] = useState<TestCase[]>([]);
  const [testResults, setTestResults] = useState<TestResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Dialog states
  const [createTestDialogOpen, setCreateTestDialogOpen] = useState(false);
  const [whatIfDialogOpen, setWhatIfDialogOpen] = useState(false);
  const [impactDialogOpen, setImpactDialogOpen] = useState(false);
  const [resultDetailDialog, setResultDetailDialog] = useState(false);

  // Form states
  const [testCaseName, setTestCaseName] = useState('');
  const [inputData, setInputData] = useState('{}');
  const [expectedOutput, setExpectedOutput] = useState('{}');
  const [assertions, setAssertions] = useState<Assertion[]>([]);
  const [selectedTestCase, setSelectedTestCase] = useState<TestCase | null>(null);
  const [selectedResult, setSelectedResult] = useState<TestResult | null>(null);

  // What-if states
  const [whatIfInput, setWhatIfInput] = useState('{}');
  const [whatIfModifications, setWhatIfModifications] = useState('{}');
  const [whatIfResult, setWhatIfResult] = useState<any>(null);

  // Impact assessment states
  const [newRulesetId, setNewRulesetId] = useState('');
  const [sampleData, setSampleData] = useState('[]');
  const [impactResult, setImpactResult] = useState<ImpactAssessment | null>(null);

  useEffect(() => {
    loadTestCases();
    loadTestResults();
  }, [rulesetId]);

  const loadTestCases = async () => {
    try {
      const response = await fetch(`/api/rules/test-cases?ruleset_id=${rulesetId}`);
      const data = await response.json();
      if (data.success) {
        setTestCases(data.data);
      }
    } catch (err) {
      console.error('Error loading test cases:', err);
    }
  };

  const loadTestResults = async () => {
    try {
      const response = await fetch(`/api/rules/test-results?ruleset_id=${rulesetId}`);
      const data = await response.json();
      if (data.success) {
        setTestResults(data.data);
      }
    } catch (err) {
      console.error('Error loading test results:', err);
    }
  };


  const handleCreateTestCase = async () => {
    setLoading(true);
    setError(null);
    try {
      const parsedInput = JSON.parse(inputData);
      const parsedExpected = expectedOutput ? JSON.parse(expectedOutput) : null;

      const response = await fetch('/api/rules/test-cases', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          test_case_name: testCaseName,
          ruleset_id: rulesetId,
          input_data: parsedInput,
          expected_output: parsedExpected,
          assertions: assertions,
        }),
      });
      const data = await response.json();
      if (data.success) {
        setSuccess('Test case created successfully');
        setCreateTestDialogOpen(false);
        resetTestCaseForm();
        loadTestCases();
      } else {
        setError(data.detail || 'Failed to create test case');
      }
    } catch (err: any) {
      setError(err.message || 'Error creating test case');
    } finally {
      setLoading(false);
    }
  };

  const handleRunTest = async (testCaseId: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/rules/test/dry-run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ruleset_id: rulesetId,
          test_case_id: testCaseId,
        }),
      });
      const data = await response.json();
      if (data.success) {
        setSuccess(`Test ${data.data.passed ? 'passed' : 'failed'}`);
        loadTestResults();
        setSelectedResult(data.data);
        setResultDetailDialog(true);
      } else {
        setError(data.detail || 'Failed to run test');
      }
    } catch (err) {
      setError('Error running test');
    } finally {
      setLoading(false);
    }
  };

  const handleWhatIfAnalysis = async () => {
    setLoading(true);
    setError(null);
    try {
      const parsedInput = JSON.parse(whatIfInput);
      const parsedMods = JSON.parse(whatIfModifications);

      const response = await fetch('/api/rules/test/what-if', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ruleset_id: rulesetId,
          input_data: parsedInput,
          modifications: parsedMods,
        }),
      });
      const data = await response.json();
      if (data.success) {
        setWhatIfResult(data.data);
        setSuccess('What-if analysis completed');
      } else {
        setError(data.detail || 'Failed to run what-if analysis');
      }
    } catch (err: any) {
      setError(err.message || 'Error running what-if analysis');
    } finally {
      setLoading(false);
    }
  };

  const handleImpactAssessment = async () => {
    setLoading(true);
    setError(null);
    try {
      const parsedSamples = JSON.parse(sampleData);

      const response = await fetch('/api/rules/test/impact-assessment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          current_ruleset_id: rulesetId,
          new_ruleset_id: newRulesetId,
          sample_data: parsedSamples,
        }),
      });
      const data = await response.json();
      if (data.success) {
        setImpactResult(data.data);
        setSuccess('Impact assessment completed');
      } else {
        setError(data.detail || 'Failed to run impact assessment');
      }
    } catch (err: any) {
      setError(err.message || 'Error running impact assessment');
    } finally {
      setLoading(false);
    }
  };

  const handleBatchTest = async () => {
    setLoading(true);
    setError(null);
    try {
      const testCaseIds = testCases.map(tc => tc.test_case_id);
      const response = await fetch('/api/rules/test/batch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ruleset_id: rulesetId,
          test_case_ids: testCaseIds,
        }),
      });
      const data = await response.json();
      if (data.success) {
        const summary = data.data.summary;
        setSuccess(`Batch test completed: ${summary.passed}/${summary.total} passed (${summary.pass_rate.toFixed(1)}%)`);
        loadTestResults();
      } else {
        setError(data.detail || 'Failed to run batch test');
      }
    } catch (err) {
      setError('Error running batch test');
    } finally {
      setLoading(false);
    }
  };

  const addAssertion = () => {
    setAssertions([
      ...assertions,
      { type: 'field_check', field: '', operator: 'equals', expected: '' },
    ]);
  };

  const updateAssertion = (index: number, field: keyof Assertion, value: any) => {
    const updated = [...assertions];
    updated[index] = { ...updated[index], [field]: value };
    setAssertions(updated);
  };

  const removeAssertion = (index: number) => {
    setAssertions(assertions.filter((_, i) => i !== index));
  };

  const resetTestCaseForm = () => {
    setTestCaseName('');
    setInputData('{}');
    setExpectedOutput('{}');
    setAssertions([]);
  };

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'critical': return 'error';
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'success';
      default: return 'default';
    }
  };


  return (
    <Box sx={{ p: 3 }}>
      <Paper sx={{ p: 3 }}>
        {/* Header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h5">Rule Testing</Typography>
          <Box>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => setCreateTestDialogOpen(true)}
              sx={{ mr: 1 }}
            >
              New Test Case
            </Button>
            <Button
              variant="outlined"
              startIcon={<PlayIcon />}
              onClick={handleBatchTest}
              disabled={testCases.length === 0 || loading}
              sx={{ mr: 1 }}
            >
              Run All Tests
            </Button>
            <Button
              variant="outlined"
              startIcon={<CompareIcon />}
              onClick={() => setWhatIfDialogOpen(true)}
            >
              What-If
            </Button>
            <Button
              variant="outlined"
              startIcon={<AssessmentIcon />}
              onClick={() => setImpactDialogOpen(true)}
              sx={{ ml: 1 }}
            >
              Impact Assessment
            </Button>
          </Box>
        </Box>

        <Divider sx={{ mb: 3 }} />

        {/* Alerts */}
        {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>{error}</Alert>}
        {success && <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(null)}>{success}</Alert>}

        {/* Tabs */}
        <Tabs value={activeTab} onChange={(e, v) => setActiveTab(v)} sx={{ mb: 3 }}>
          <Tab label={`Test Cases (${testCases.length})`} />
          <Tab label={`Test Results (${testResults.length})`} />
        </Tabs>

        {/* Test Cases Tab */}
        {activeTab === 0 && (
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Test Name</TableCell>
                  <TableCell>Assertions</TableCell>
                  <TableCell>Expected Output</TableCell>
                  <TableCell>Created</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {testCases.map((testCase) => (
                  <TableRow key={testCase.test_case_id}>
                    <TableCell>{testCase.test_case_name}</TableCell>
                    <TableCell>
                      <Chip label={`${testCase.assertions.length} assertions`} size="small" />
                    </TableCell>
                    <TableCell>
                      {testCase.expected_output ? (
                        <CheckIcon color="success" fontSize="small" />
                      ) : (
                        <Typography variant="caption" color="text.secondary">None</Typography>
                      )}
                    </TableCell>
                    <TableCell>
                      {testCase.created_at && (
                        <Typography variant="caption">
                          {new Date(testCase.created_at).toLocaleDateString()}
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell>
                      <Button
                        size="small"
                        variant="contained"
                        startIcon={<PlayIcon />}
                        onClick={() => handleRunTest(testCase.test_case_id)}
                        disabled={loading}
                      >
                        Run Test
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
                {testCases.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={5} align="center">
                      <Typography variant="body2" color="text.secondary">
                        No test cases created yet
                      </Typography>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        )}

        {/* Test Results Tab */}
        {activeTab === 1 && (
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Status</TableCell>
                  <TableCell>Test Case</TableCell>
                  <TableCell>Assertions</TableCell>
                  <TableCell>Execution Time</TableCell>
                  <TableCell>Executed</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {testResults.map((result) => (
                  <TableRow key={result.test_result_id}>
                    <TableCell>
                      {result.passed ? (
                        <Chip icon={<CheckIcon />} label="PASSED" color="success" size="small" />
                      ) : (
                        <Chip icon={<ErrorIcon />} label="FAILED" color="error" size="small" />
                      )}
                    </TableCell>
                    <TableCell>{result.test_case_id}</TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        ✓ {result.assertions_passed} / ✗ {result.assertions_failed}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="caption">{result.execution_time_ms}ms</Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="caption">
                        {new Date(result.executed_at).toLocaleString()}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Button
                        size="small"
                        onClick={() => {
                          setSelectedResult(result);
                          setResultDetailDialog(true);
                        }}
                      >
                        Details
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
                {testResults.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={6} align="center">
                      <Typography variant="body2" color="text.secondary">
                        No test results yet
                      </Typography>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        )}


      {/* Create Test Case Dialog */}
      <Dialog open={createTestDialogOpen} onClose={() => setCreateTestDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Create Test Case</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <TextField
              fullWidth
              label="Test Case Name"
              value={testCaseName}
              onChange={(e) => setTestCaseName(e.target.value)}
              sx={{ mb: 2 }}
            />

            <TextField
              fullWidth
              label="Input Data (JSON)"
              multiline
              rows={4}
              value={inputData}
              onChange={(e) => setInputData(e.target.value)}
              sx={{ mb: 2 }}
              helperText="JSON object with test input data"
            />

            <TextField
              fullWidth
              label="Expected Output (JSON, Optional)"
              multiline
              rows={3}
              value={expectedOutput}
              onChange={(e) => setExpectedOutput(e.target.value)}
              sx={{ mb: 2 }}
              helperText="Expected output to compare against"
            />

            <Box sx={{ mb: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                <Typography variant="subtitle2">Assertions</Typography>
                <Button size="small" startIcon={<AddIcon />} onClick={addAssertion}>
                  Add Assertion
                </Button>
              </Box>

              {assertions.map((assertion, index) => (
                <Card key={index} sx={{ mb: 1, p: 2 }}>
                  <Grid container spacing={2} alignItems="center">
                    <Grid item xs={3}>
                      <TextField
                        fullWidth
                        size="small"
                        label="Field"
                        value={assertion.field}
                        onChange={(e) => updateAssertion(index, 'field', e.target.value)}
                      />
                    </Grid>
                    <Grid item xs={3}>
                      <FormControl fullWidth size="small">
                        <InputLabel>Operator</InputLabel>
                        <Select
                          value={assertion.operator}
                          onChange={(e) => updateAssertion(index, 'operator', e.target.value)}
                          label="Operator"
                        >
                          <MenuItem value="equals">Equals</MenuItem>
                          <MenuItem value="not_equals">Not Equals</MenuItem>
                          <MenuItem value="greater_than">Greater Than</MenuItem>
                          <MenuItem value="less_than">Less Than</MenuItem>
                          <MenuItem value="contains">Contains</MenuItem>
                          <MenuItem value="is_null">Is Null</MenuItem>
                          <MenuItem value="is_not_null">Is Not Null</MenuItem>
                        </Select>
                      </FormControl>
                    </Grid>
                    <Grid item xs={4}>
                      <TextField
                        fullWidth
                        size="small"
                        label="Expected Value"
                        value={assertion.expected}
                        onChange={(e) => updateAssertion(index, 'expected', e.target.value)}
                      />
                    </Grid>
                    <Grid item xs={2}>
                      <IconButton size="small" onClick={() => removeAssertion(index)}>
                        <DeleteIcon />
                      </IconButton>
                    </Grid>
                  </Grid>
                </Card>
              ))}
            </Box>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateTestDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleCreateTestCase}
            disabled={!testCaseName || !inputData || loading}
          >
            Create Test Case
          </Button>
        </DialogActions>
      </Dialog>

      {/* Test Result Detail Dialog */}
      <Dialog open={resultDetailDialog} onClose={() => setResultDetailDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Test Result Details</DialogTitle>
        <DialogContent>
          {selectedResult && (
            <Box sx={{ pt: 2 }}>
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={3}>
                  <Card>
                    <CardContent>
                      <Typography variant="h4">
                        {selectedResult.passed ? <CheckIcon color="success" /> : <ErrorIcon color="error" />}
                      </Typography>
                      <Typography variant="caption">
                        {selectedResult.passed ? 'PASSED' : 'FAILED'}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={3}>
                  <Card>
                    <CardContent>
                      <Typography variant="h5">{selectedResult.assertions_passed}</Typography>
                      <Typography variant="caption">Passed</Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={3}>
                  <Card>
                    <CardContent>
                      <Typography variant="h5">{selectedResult.assertions_failed}</Typography>
                      <Typography variant="caption">Failed</Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={3}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6">{selectedResult.execution_time_ms}ms</Typography>
                      <Typography variant="caption">Execution Time</Typography>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>

              <Accordion defaultExpanded>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography variant="subtitle1">Assertion Results</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <List>
                    {selectedResult.assertion_details.map((detail: any, idx: number) => (
                      <ListItem key={idx}>
                        <ListItemText
                          primary={
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              {detail.passed ? <CheckIcon color="success" fontSize="small" /> : <ErrorIcon color="error" fontSize="small" />}
                              <Typography variant="body2">
                                {detail.assertion.field} {detail.assertion.operator} {detail.assertion.expected}
                              </Typography>
                            </Box>
                          }
                          secondary={`Actual: ${JSON.stringify(detail.actual_value)}`}
                        />
                      </ListItem>
                    ))}
                  </List>
                </AccordionDetails>
              </Accordion>

              {selectedResult.output_diff && (
                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Typography variant="subtitle1">Output Differences</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <pre style={{ overflow: 'auto', maxHeight: 300 }}>
                      {JSON.stringify(selectedResult.output_diff, null, 2)}
                    </pre>
                  </AccordionDetails>
                </Accordion>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setResultDetailDialog(false)}>Close</Button>
        </DialogActions>
      </Dialog>


      {/* What-If Analysis Dialog */}
      <Dialog open={whatIfDialogOpen} onClose={() => setWhatIfDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <ScienceIcon />
            What-If Analysis
          </Box>
        </DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <Alert severity="info" sx={{ mb: 2 }}>
              Test how rule results change when you modify input values
            </Alert>

            <TextField
              fullWidth
              label="Base Input Data (JSON)"
              multiline
              rows={4}
              value={whatIfInput}
              onChange={(e) => setWhatIfInput(e.target.value)}
              sx={{ mb: 2 }}
            />

            <TextField
              fullWidth
              label="Modifications (JSON)"
              multiline
              rows={3}
              value={whatIfModifications}
              onChange={(e) => setWhatIfModifications(e.target.value)}
              sx={{ mb: 2 }}
              helperText="Fields to modify and their new values"
            />

            <Button
              fullWidth
              variant="contained"
              onClick={handleWhatIfAnalysis}
              disabled={loading}
              sx={{ mb: 2 }}
            >
              Run Analysis
            </Button>

            {whatIfResult && (
              <Box>
                <Typography variant="subtitle1" sx={{ mb: 1 }}>Results</Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Card sx={{ bgcolor: 'grey.100' }}>
                      <CardContent>
                        <Typography variant="subtitle2">Base Result</Typography>
                        <pre style={{ overflow: 'auto', maxHeight: 200, fontSize: '0.75rem' }}>
                          {JSON.stringify(whatIfResult.base_result?.output_data, null, 2)}
                        </pre>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={6}>
                    <Card sx={{ bgcolor: 'info.light' }}>
                      <CardContent>
                        <Typography variant="subtitle2">Modified Result</Typography>
                        <pre style={{ overflow: 'auto', maxHeight: 200, fontSize: '0.75rem' }}>
                          {JSON.stringify(whatIfResult.modified_result?.output_data, null, 2)}
                        </pre>
                      </CardContent>
                    </Card>
                  </Grid>
                </Grid>

                <Alert severity="info" sx={{ mt: 2 }}>
                  {whatIfResult.impact_summary}
                </Alert>

                {whatIfResult.comparison?.field_changes && Object.keys(whatIfResult.comparison.field_changes).length > 0 && (
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="subtitle2" sx={{ mb: 1 }}>Field Changes</Typography>
                    <List dense>
                      {Object.entries(whatIfResult.comparison.field_changes).map(([field, change]: [string, any]) => (
                        <ListItem key={field}>
                          <ListItemText
                            primary={field}
                            secondary={`${JSON.stringify(change.before)} → ${JSON.stringify(change.after)}`}
                          />
                        </ListItem>
                      ))}
                    </List>
                  </Box>
                )}
              </Box>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setWhatIfDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Impact Assessment Dialog */}
      <Dialog open={impactDialogOpen} onClose={() => setImpactDialogOpen(false)} maxWidth="lg" fullWidth>
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <AssessmentIcon />
            Impact Assessment
          </Box>
        </DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <Alert severity="warning" sx={{ mb: 2 }}>
              Assess the impact of rule changes before activation
            </Alert>

            <TextField
              fullWidth
              label="New Ruleset ID"
              value={newRulesetId}
              onChange={(e) => setNewRulesetId(e.target.value)}
              sx={{ mb: 2 }}
              helperText="ID of the new ruleset to compare against"
            />

            <TextField
              fullWidth
              label="Sample Data (JSON Array)"
              multiline
              rows={5}
              value={sampleData}
              onChange={(e) => setSampleData(e.target.value)}
              sx={{ mb: 2 }}
              helperText="Array of sample input data to test both rulesets"
            />

            <Button
              fullWidth
              variant="contained"
              onClick={handleImpactAssessment}
              disabled={!newRulesetId || loading}
              sx={{ mb: 3 }}
            >
              {loading ? <CircularProgress size={24} /> : 'Run Impact Assessment'}
            </Button>

            {impactResult && (
              <Box>
                <Grid container spacing={2} sx={{ mb: 3 }}>
                  <Grid item xs={3}>
                    <Card>
                      <CardContent>
                        <Typography variant="h4">{impactResult.sample_size}</Typography>
                        <Typography variant="caption">Total Samples</Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={3}>
                    <Card>
                      <CardContent>
                        <Typography variant="h4">{impactResult.affected_count}</Typography>
                        <Typography variant="caption">Affected</Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={3}>
                    <Card>
                      <CardContent>
                        <Typography variant="h4">{impactResult.affected_percentage.toFixed(1)}%</Typography>
                        <Typography variant="caption">Impact Rate</Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={3}>
                    <Card sx={{ bgcolor: getRiskColor(impactResult.risk_level) + '.light' }}>
                      <CardContent>
                        <Typography variant="h6">{impactResult.risk_level.toUpperCase()}</Typography>
                        <Typography variant="caption">Risk Level</Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                </Grid>

                {impactResult.risk_factors.length > 0 && (
                  <Alert severity={getRiskColor(impactResult.risk_level)} sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" sx={{ mb: 1 }}>Risk Factors:</Typography>
                    <List dense>
                      {impactResult.risk_factors.map((factor, idx) => (
                        <ListItem key={idx}>
                          <Typography variant="body2">• {factor}</Typography>
                        </ListItem>
                      ))}
                    </List>
                  </Alert>
                )}

                {impactResult.recommendations.length > 0 && (
                  <Card sx={{ bgcolor: 'info.light', mb: 2 }}>
                    <CardContent>
                      <Typography variant="subtitle2" sx={{ mb: 1 }}>Recommendations:</Typography>
                      <List dense>
                        {impactResult.recommendations.map((rec, idx) => (
                          <ListItem key={idx}>
                            <Typography variant="body2">{rec}</Typography>
                          </ListItem>
                        ))}
                      </List>
                    </CardContent>
                  </Card>
                )}

                {impactResult.result_changes.length > 0 && (
                  <Accordion>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                      <Typography variant="subtitle1">Detailed Changes ({impactResult.result_changes.length})</Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                      <Box sx={{ maxHeight: 300, overflow: 'auto' }}>
                        {impactResult.result_changes.slice(0, 10).map((change: any, idx: number) => (
                          <Card key={idx} sx={{ mb: 1, p: 1 }}>
                            <Typography variant="caption" fontWeight="bold">Sample {change.sample_index + 1}</Typography>
                            <List dense>
                              {change.changes.map((c: any, i: number) => (
                                <ListItem key={i}>
                                  <Typography variant="body2" fontSize="0.75rem">
                                    {c.field}: {JSON.stringify(c.current_value)} → {JSON.stringify(c.new_value)}
                                  </Typography>
                                </ListItem>
                              ))}
                            </List>
                          </Card>
                        ))}
                        {impactResult.result_changes.length > 10 && (
                          <Typography variant="caption" color="text.secondary">
                            ... and {impactResult.result_changes.length - 10} more changes
                          </Typography>
                        )}
                      </Box>
                    </AccordionDetails>
                  </Accordion>
                )}
              </Box>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setImpactDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
      </Paper>
    </Box>
  );
};

export default RuleTestingInterface;
