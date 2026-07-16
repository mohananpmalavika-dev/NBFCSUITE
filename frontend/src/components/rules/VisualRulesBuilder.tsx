/**
 * Visual Rules Builder
 * 
 * Complete visual interface for building business rules
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Stepper,
  Step,
  StepLabel,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Grid,
  Tabs,
  Tab,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  Save as SaveIcon,
  PlayArrow as TestIcon,
  Close as CloseIcon,
} from '@mui/icons-material';
import ConditionBuilder from './ConditionBuilder';
import ActionBuilder from './ActionBuilder';
import FormulaBuilder from './FormulaBuilder';
import RuleTestInterface from './RuleTestInterface';
import DecisionTableBuilder from './DecisionTableBuilder';
import ExecutionEngineConfig from './ExecutionEngineConfig';
import BatchScheduler from './BatchScheduler';
import RuleChainBuilder from './RuleChainBuilder';
import RuleVersionManager from './RuleVersionManager';
import RuleTestingInterface from './RuleTestingInterface';
import RuleLibrary from './RuleLibrary';
import rulesService from '../../services/rulesService';

interface VisualRulesBuilderProps {
  rulesetId?: string;
  onSave?: (ruleset: any) => void;
  onClose?: () => void;
}

const VisualRulesBuilder: React.FC<VisualRulesBuilderProps> = ({
  rulesetId,
  onSave,
  onClose,
}) => {
  const [activeStep, setActiveStep] = useState(0);
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(false);
  const [testDialogOpen, setTestDialogOpen] = useState(false);
  
  // Ruleset data
  const [rulesetName, setRulesetName] = useState('');
  const [entityType, setEntityType] = useState('');
  const [description, setDescription] = useState('');
  
  // Available fields
  const [availableFields, setAvailableFields] = useState([
    { name: 'age', type: 'number', label: 'Age' },
    { name: 'monthly_income', type: 'number', label: 'Monthly Income' },
    { name: 'credit_score', type: 'number', label: 'Credit Score' },
    { name: 'employment_type', type: 'string', label: 'Employment Type' },
    { name: 'loan_amount', type: 'number', label: 'Loan Amount' },
  ]);
  
  // Rules
  const [decisionRules, setDecisionRules] = useState<any[]>([]);
  const [validationRules, setValidationRules] = useState<any[]>([]);
  const [calculationRules, setCalculationRules] = useState<any[]>([]);
  const [eligibilityRules, setEligibilityRules] = useState<any[]>([]);
  const [decisionTables, setDecisionTables] = useState<any[]>([]);
  
  // Execution Engine
  const [executionConfig, setExecutionConfig] = useState<any>(null);
  const [ruleChains, setRuleChains] = useState<any[]>([]);
  const [batchSchedules, setBatchSchedules] = useState<any[]>([]);
  
  // Dialogs
  const [executionConfigOpen, setExecutionConfigOpen] = useState(false);
  const [chainBuilderOpen, setChainBuilderOpen] = useState(false);
  const [batchSchedulerOpen, setBatchSchedulerOpen] = useState(false);
  const [currentChain, setCurrentChain] = useState<any>(null);
  const [currentSchedule, setCurrentSchedule] = useState<any>(null);
  
  // Current rule being edited
  const [currentRule, setCurrentRule] = useState<any>(null);
  const [currentRuleType, setCurrentRuleType] = useState<string>('decision');
  const [currentTable, setCurrentTable] = useState<any>(null);
  const [tableBuilderOpen, setTableBuilderOpen] = useState(false);
  
  // Rule Management features
  const [versionManagerOpen, setVersionManagerOpen] = useState(false);
  const [testingInterfaceOpen, setTestingInterfaceOpen] = useState(false);
  const [libraryDialogOpen, setLibraryDialogOpen] = useState(false);
  const [managementTab, setManagementTab] = useState(0);
  
  const steps = ['Basic Info', 'Build Rules', 'Execution Settings', 'Management', 'Review & Save'];
  
  useEffect(() => {
    if (rulesetId && rulesetId !== 'new') {
      loadRuleset();
    }
  }, [rulesetId]);
  
  const loadRuleset = async () => {
    try {
      const data = await rulesService.getRuleset(rulesetId!);
      setRulesetName(data.ruleset_name);
      setEntityType(data.entity_type);
      setDescription(data.description);
      setDecisionRules(data.decision_rules || []);
      setValidationRules(data.validation_rules || []);
      setCalculationRules(data.calculation_rules || []);
      setEligibilityRules(data.eligibility_rules || []);
      setDecisionTables(data.decision_tables || []);
      
      // Load execution config
      if (data.execution_config) {
        setExecutionConfig(data.execution_config);
        setRuleChains(data.execution_config.rule_chains || []);
      }
    } catch (err) {
      console.error('Failed to load ruleset:', err);
    }
  };
  
  const handleSaveRuleset = async () => {
    setLoading(true);
    try {
      const ruleset = {
        ruleset_id: rulesetId === 'new' ? rulesService.generateRuleId('ruleset') : rulesetId,
        ruleset_name: rulesetName,
        entity_type: entityType,
        description,
        version: '1.0',
        is_active: true,
        decision_rules: decisionRules,
        validation_rules: validationRules,
        calculation_rules: calculationRules,
        eligibility_rules: eligibilityRules,
        decision_tables: decisionTables,
        routing_rules: [],
        pricing_rules: [],
        execution_config: executionConfig ? {
          ...executionConfig,
          rule_chains: ruleChains,
          ruleset_id: rulesetId === 'new' ? undefined : rulesetId,
        } : null,
      };
      
      if (rulesetId === 'new') {
        await rulesService.createRuleset(ruleset);
      } else {
        await rulesService.updateRuleset(rulesetId!, ruleset);
      }
      
      onSave?.(ruleset);
    } catch (err) {
      console.error('Failed to save ruleset:', err);
    } finally {
      setLoading(false);
    }
  };
  
  const handleAddRule = () => {
    const newRule: any = {
      rule_id: rulesService.generateRuleId(currentRuleType),
      rule_name: '',
      is_active: true,
    };
    
    if (currentRuleType === 'decision') {
      newRule.if_condition = {
        group_id: 'g1',
        logical_operator: 'and',
        conditions: [],
      };
      newRule.then_actions = [];
      newRule.else_actions = [];
      newRule.priority = 0;
    } else if (currentRuleType === 'validation') {
      newRule.conditions = {
        group_id: 'g1',
        logical_operator: 'and',
        conditions: [],
      };
      newRule.error_message = '';
      newRule.severity = 'error';
      newRule.stop_on_error = true;
    } else if (currentRuleType === 'calculation') {
      newRule.target_field = '';
      newRule.formula = '';
      newRule.formula_fields = [];
      newRule.rounding_mode = 'round';
    } else if (currentRuleType === 'eligibility') {
      newRule.criteria = [];
      newRule.all_must_pass = true;
      newRule.scoring_enabled = false;
    }
    
    setCurrentRule(newRule);
  };
  
  const handleSaveCurrentRule = () => {
    if (!currentRule) return;
    
    if (currentRuleType === 'decision') {
      setDecisionRules([...decisionRules.filter(r => r.rule_id !== currentRule.rule_id), currentRule]);
    } else if (currentRuleType === 'validation') {
      setValidationRules([...validationRules.filter(r => r.rule_id !== currentRule.rule_id), currentRule]);
    } else if (currentRuleType === 'calculation') {
      setCalculationRules([...calculationRules.filter(r => r.rule_id !== currentRule.rule_id), currentRule]);
    } else if (currentRuleType === 'eligibility') {
      setEligibilityRules([...eligibilityRules.filter(r => r.rule_id !== currentRule.rule_id), currentRule]);
    }
    
    setCurrentRule(null);
  };
  
  const handleOpenTableBuilder = (table?: any) => {
    setCurrentTable(table || null);
    setTableBuilderOpen(true);
  };
  
  const handleSaveTable = (table: any) => {
    if (currentTable) {
      // Update existing table
      setDecisionTables(decisionTables.map(t => 
        t.table_id === table.table_id ? table : t
      ));
    } else {
      // Add new table
      setDecisionTables([...decisionTables, table]);
    }
    setTableBuilderOpen(false);
    setCurrentTable(null);
  };
  
  const handleDeleteTable = (tableId: string) => {
    if (window.confirm('Delete this decision table?')) {
      setDecisionTables(decisionTables.filter(t => t.table_id !== tableId));
    }
  };
  
  // ==================== EXECUTION ENGINE HANDLERS ====================
  
  const handleSaveExecutionConfig = (config: any) => {
    setExecutionConfig(config);
    setExecutionConfigOpen(false);
  };
  
  const handleOpenChainBuilder = (chain?: any) => {
    setCurrentChain(chain || null);
    setChainBuilderOpen(true);
  };
  
  const handleSaveChain = (chain: any) => {
    if (currentChain) {
      // Update existing chain
      setRuleChains(ruleChains.map(c => c.chain_id === chain.chain_id ? chain : c));
    } else {
      // Add new chain
      setRuleChains([...ruleChains, chain]);
    }
    setChainBuilderOpen(false);
    setCurrentChain(null);
  };
  
  const handleDeleteChain = (chainId: string) => {
    if (window.confirm('Delete this rule chain?')) {
      setRuleChains(ruleChains.filter(c => c.chain_id !== chainId));
    }
  };
  
  const handleOpenBatchScheduler = (schedule?: any) => {
    setCurrentSchedule(schedule || null);
    setBatchSchedulerOpen(true);
  };
  
  const handleSaveBatchSchedule = async (schedule: any) => {
    try {
      if (currentSchedule) {
        await rulesService.updateBatchSchedule(schedule.schedule_id, schedule);
        setBatchSchedules(batchSchedules.map(s => 
          s.schedule_id === schedule.schedule_id ? schedule : s
        ));
      } else {
        const created = await rulesService.createBatchSchedule(schedule);
        setBatchSchedules([...batchSchedules, created]);
      }
      setBatchSchedulerOpen(false);
      setCurrentSchedule(null);
    } catch (err) {
      console.error('Failed to save batch schedule:', err);
    }
  };
  
  const handleDeleteBatchSchedule = async (scheduleId: string) => {
    if (window.confirm('Delete this batch schedule?')) {
      try {
        await rulesService.deleteBatchSchedule(scheduleId);
        setBatchSchedules(batchSchedules.filter(s => s.schedule_id !== scheduleId));
      } catch (err) {
        console.error('Failed to delete batch schedule:', err);
      }
    }
  };
  
  const getAvailableRules = () => {
    const rules: Array<{ rule_id: string; rule_name: string; rule_type: string }> = [];
    
    decisionRules.forEach(r => rules.push({ rule_id: r.rule_id, rule_name: r.rule_name, rule_type: 'decision' }));
    validationRules.forEach(r => rules.push({ rule_id: r.rule_id, rule_name: r.rule_name, rule_type: 'validation' }));
    calculationRules.forEach(r => rules.push({ rule_id: r.rule_id, rule_name: r.rule_name, rule_type: 'calculation' }));
    eligibilityRules.forEach(r => rules.push({ rule_id: r.rule_id, rule_name: r.rule_name, rule_type: 'eligibility' }));
    
    return rules;
  };
  
  const renderBasicInfo = () => (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <TextField
          fullWidth
          label="Ruleset Name"
          value={rulesetName}
          onChange={(e) => setRulesetName(e.target.value)}
          required
        />
      </Grid>
      <Grid item xs={12}>
        <TextField
          fullWidth
          label="Entity Type"
          value={entityType}
          onChange={(e) => setEntityType(e.target.value)}
          placeholder="e.g., loan_application, customer"
          required
        />
      </Grid>
      <Grid item xs={12}>
        <TextField
          fullWidth
          multiline
          rows={3}
          label="Description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
      </Grid>
    </Grid>
  );
  
  const renderRuleBuilder = () => {
    if (!currentRule && !tableBuilderOpen) {
      return (
        <Box>
          <Tabs value={activeTab} onChange={(e, v) => setActiveTab(v)} sx={{ mb: 3 }}>
            <Tab label="Rules" />
            <Tab label="Decision Tables" />
          </Tabs>
          
          {activeTab === 0 && (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Typography color="text.secondary" gutterBottom>
                Select a rule type and click "Add Rule" to start building
              </Typography>
              <Box sx={{ mt: 2 }}>
                <FormControl sx={{ minWidth: 200, mr: 2 }}>
                  <InputLabel>Rule Type</InputLabel>
                  <Select
                    value={currentRuleType}
                    onChange={(e) => setCurrentRuleType(e.target.value)}
                    label="Rule Type"
                  >
                    <MenuItem value="decision">Decision Rule</MenuItem>
                    <MenuItem value="validation">Validation Rule</MenuItem>
                    <MenuItem value="calculation">Calculation Rule</MenuItem>
                    <MenuItem value="eligibility">Eligibility Rule</MenuItem>
                  </Select>
                </FormControl>
                <Button variant="contained" onClick={handleAddRule}>
                  Add {currentRuleType} Rule
                </Button>
              </Box>
            </Box>
          )}
          
          {activeTab === 1 && (
            <Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="h6">Decision Tables ({decisionTables.length})</Typography>
                <Button variant="contained" onClick={() => handleOpenTableBuilder()}>
                  Create Decision Table
                </Button>
              </Box>
              
              {decisionTables.length === 0 ? (
                <Alert severity="info">
                  No decision tables yet. Create your first decision table to define tabular rules.
                </Alert>
              ) : (
                <Grid container spacing={2}>
                  {decisionTables.map((table) => (
                    <Grid item xs={12} sm={6} md={4} key={table.table_id}>
                      <Paper variant="outlined" sx={{ p: 2 }}>
                        <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                          {table.table_name}
                        </Typography>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          {table.description}
                        </Typography>
                        <Typography variant="caption" display="block">
                          Columns: {table.columns?.length || 0}
                        </Typography>
                        <Typography variant="caption" display="block">
                          Rows: {table.rows?.length || 0}
                        </Typography>
                        <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
                          <Button
                            size="small"
                            variant="outlined"
                            onClick={() => handleOpenTableBuilder(table)}
                          >
                            Edit
                          </Button>
                          <Button
                            size="small"
                            color="error"
                            onClick={() => handleDeleteTable(table.table_id)}
                          >
                            Delete
                          </Button>
                        </Box>
                      </Paper>
                    </Grid>
                  ))}
                </Grid>
              )}
            </Box>
          )}
        </Box>
      );
    }
    
    return (
      <Box>
        <TextField
          fullWidth
          label="Rule Name"
          value={currentRule.rule_name}
          onChange={(e) => setCurrentRule({ ...currentRule, rule_name: e.target.value })}
          sx={{ mb: 2 }}
        />
        
        {currentRuleType === 'decision' && (
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <ConditionBuilder
                conditionGroup={currentRule.if_condition}
                onChange={(updated) => setCurrentRule({ ...currentRule, if_condition: updated })}
                availableFields={availableFields}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <ActionBuilder
                actions={currentRule.then_actions}
                onChange={(updated) => setCurrentRule({ ...currentRule, then_actions: updated })}
                availableFields={availableFields}
                actionLabel="THEN Actions"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <ActionBuilder
                actions={currentRule.else_actions}
                onChange={(updated) => setCurrentRule({ ...currentRule, else_actions: updated })}
                availableFields={availableFields}
                actionLabel="ELSE Actions"
              />
            </Grid>
          </Grid>
        )}
        
        {currentRuleType === 'validation' && (
          <Box>
            <ConditionBuilder
              conditionGroup={currentRule.conditions}
              onChange={(updated) => setCurrentRule({ ...currentRule, conditions: updated })}
              availableFields={availableFields}
            />
            <TextField
              fullWidth
              label="Error Message"
              value={currentRule.error_message}
              onChange={(e) => setCurrentRule({ ...currentRule, error_message: e.target.value })}
              sx={{ mt: 2 }}
            />
          </Box>
        )}
        
        {currentRuleType === 'calculation' && (
          <Box>
            <TextField
              fullWidth
              label="Target Field"
              value={currentRule.target_field}
              onChange={(e) => setCurrentRule({ ...currentRule, target_field: e.target.value })}
              sx={{ mb: 2 }}
            />
            <FormulaBuilder
              formula={currentRule.formula}
              onChange={(formula) => setCurrentRule({ ...currentRule, formula })}
              availableFields={availableFields}
            />
          </Box>
        )}
        
        <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
          <Button variant="contained" onClick={handleSaveCurrentRule}>
            Save Rule
          </Button>
          <Button variant="outlined" onClick={() => setCurrentRule(null)}>
            Cancel
          </Button>
        </Box>
      </Box>
    );
  };
  
  const renderExecutionSettings = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        Execution Engine Configuration
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Configure how rules are executed: modes, priorities, chaining, and batch scheduling
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper variant="outlined" sx={{ p: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Box>
                <Typography variant="subtitle1" fontWeight="bold">
                  Execution Configuration
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {executionConfig ? (
                    <>Mode: {rulesService.getExecutionModeLabel(executionConfig.execution_mode)}</>
                  ) : (
                    'No configuration set (using defaults)'
                  )}
                </Typography>
              </Box>
              <Button
                variant={executionConfig ? 'outlined' : 'contained'}
                onClick={() => setExecutionConfigOpen(true)}
              >
                {executionConfig ? 'Edit Config' : 'Configure'}
              </Button>
            </Box>
          </Paper>
        </Grid>
        
        <Grid item xs={12}>
          <Paper variant="outlined" sx={{ p: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="subtitle1" fontWeight="bold">
                Rule Chains ({ruleChains.length})
              </Typography>
              <Button
                variant="contained"
                onClick={() => handleOpenChainBuilder()}
                size="small"
              >
                Create Chain
              </Button>
            </Box>
            
            {ruleChains.length === 0 ? (
              <Alert severity="info">
                No rule chains configured. Create chains for sequential rule execution with output pass-through.
              </Alert>
            ) : (
              <Grid container spacing={1}>
                {ruleChains.map((chain) => (
                  <Grid item xs={12} sm={6} key={chain.chain_id}>
                    <Box sx={{ p: 1, border: '1px solid', borderColor: 'divider', borderRadius: 1 }}>
                      <Typography variant="body2" fontWeight="bold">
                        {chain.chain_name}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {chain.steps.length} steps · {rulesService.getExecutionStrategyLabel(chain.execution_strategy)}
                      </Typography>
                      <Box sx={{ mt: 1, display: 'flex', gap: 1 }}>
                        <Button size="small" onClick={() => handleOpenChainBuilder(chain)}>
                          Edit
                        </Button>
                        <Button size="small" color="error" onClick={() => handleDeleteChain(chain.chain_id)}>
                          Delete
                        </Button>
                      </Box>
                    </Box>
                  </Grid>
                ))}
              </Grid>
            )}
          </Paper>
        </Grid>
        
        <Grid item xs={12}>
          <Paper variant="outlined" sx={{ p: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="subtitle1" fontWeight="bold">
                Batch Schedules ({batchSchedules.length})
              </Typography>
              <Button
                variant="contained"
                onClick={() => handleOpenBatchScheduler()}
                size="small"
              >
                Create Schedule
              </Button>
            </Box>
            
            {batchSchedules.length === 0 ? (
              <Alert severity="info">
                No batch schedules configured. Create schedules for automated rule execution at specific times.
              </Alert>
            ) : (
              <Grid container spacing={1}>
                {batchSchedules.map((schedule) => (
                  <Grid item xs={12} sm={6} key={schedule.schedule_id}>
                    <Box sx={{ p: 1, border: '1px solid', borderColor: 'divider', borderRadius: 1 }}>
                      <Typography variant="body2" fontWeight="bold">
                        {schedule.schedule_name}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {rulesService.formatCronExpression(schedule.cron_expression)} ({schedule.timezone})
                      </Typography>
                      <Box sx={{ mt: 1, display: 'flex', gap: 1 }}>
                        <Button size="small" onClick={() => handleOpenBatchScheduler(schedule)}>
                          Edit
                        </Button>
                        <Button size="small" color="error" onClick={() => handleDeleteBatchSchedule(schedule.schedule_id)}>
                          Delete
                        </Button>
                      </Box>
                    </Box>
                  </Grid>
                ))}
              </Grid>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
  
  const renderManagement = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        Rule Management
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Manage versions, run tests, and browse the rule library
      </Typography>
      
      <Tabs value={managementTab} onChange={(e, v) => setManagementTab(v)} sx={{ mb: 3 }}>
        <Tab label="Version Management" />
        <Tab label="Testing & Validation" />
        <Tab label="Rule Library" />
      </Tabs>
      
      {managementTab === 0 && rulesetId && rulesetId !== 'new' && (
        <RuleVersionManager
          rulesetId={rulesetId}
          onVersionChange={(version) => {
            // Reload ruleset when version changes
            loadRuleset();
          }}
        />
      )}
      
      {managementTab === 0 && (!rulesetId || rulesetId === 'new') && (
        <Alert severity="info">
          Version management is available after saving the ruleset for the first time.
        </Alert>
      )}
      
      {managementTab === 1 && rulesetId && rulesetId !== 'new' && (
        <RuleTestingInterface rulesetId={rulesetId} />
      )}
      
      {managementTab === 1 && (!rulesetId || rulesetId === 'new') && (
        <Alert severity="info">
          Testing features are available after saving the ruleset for the first time.
        </Alert>
      )}
      
      {managementTab === 2 && (
        <RuleLibrary
          onTemplateSelect={(template) => {
            // Template selected - could preview or auto-fill
            console.log('Template selected:', template);
          }}
          onCreateFromTemplate={(newRulesetId) => {
            // Navigate to the newly created ruleset
            if (onClose) onClose();
          }}
        />
      )}
    </Box>
  );
  
  const renderReview = () => (
    <Box>
      <Alert severity="info" sx={{ mb: 2 }}>
        Review your ruleset before saving
      </Alert>
      <Typography variant="h6" gutterBottom>
        {rulesetName}
      </Typography>
      <Typography variant="body2" color="text.secondary" gutterBottom>
        Entity Type: {entityType}
      </Typography>
      <Typography variant="body2" gutterBottom>
        {description}
      </Typography>
      <Box sx={{ mt: 2 }}>
        <Typography variant="subtitle2">Rules Summary:</Typography>
        <Typography variant="body2">• Decision Rules: {decisionRules.length}</Typography>
        <Typography variant="body2">• Validation Rules: {validationRules.length}</Typography>
        <Typography variant="body2">• Calculation Rules: {calculationRules.length}</Typography>
        <Typography variant="body2">• Eligibility Rules: {eligibilityRules.length}</Typography>
        <Typography variant="body2">• Decision Tables: {decisionTables.length}</Typography>
      </Box>
      {executionConfig && (
        <Box sx={{ mt: 2 }}>
          <Typography variant="subtitle2">Execution Settings:</Typography>
          <Typography variant="body2">
            • Mode: {rulesService.getExecutionModeLabel(executionConfig.execution_mode)}
          </Typography>
          <Typography variant="body2">
            • Priority Execution: {executionConfig.enable_priority_execution ? 'Enabled' : 'Disabled'}
          </Typography>
          <Typography variant="body2">
            • Rule Chaining: {executionConfig.enable_rule_chaining ? 'Enabled' : 'Disabled'}
          </Typography>
          <Typography variant="body2">• Rule Chains: {ruleChains.length}</Typography>
          <Typography variant="body2">• Batch Schedules: {batchSchedules.length}</Typography>
        </Box>
      )}
    </Box>
  );
  
  return (
    <Box>
      <Paper sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
          <Typography variant="h5">
            {rulesetId === 'new' ? 'Create' : 'Edit'} Ruleset
          </Typography>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button
              startIcon={<TestIcon />}
              onClick={() => setTestDialogOpen(true)}
              variant="outlined"
            >
              Test
            </Button>
            {onClose && (
              <Button startIcon={<CloseIcon />} onClick={onClose}>
                Close
              </Button>
            )}
          </Box>
        </Box>
        
        <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>
        
        <Box sx={{ mb: 3 }}>
          {activeStep === 0 && renderBasicInfo()}
          {activeStep === 1 && renderRuleBuilder()}
          {activeStep === 2 && renderExecutionSettings()}
          {activeStep === 3 && renderManagement()}
          {activeStep === 4 && renderReview()}
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
                startIcon={<SaveIcon />}
                onClick={handleSaveRuleset}
                disabled={loading}
              >
                {loading ? 'Saving...' : 'Save Ruleset'}
              </Button>
            )}
          </Box>
        </Box>
      </Paper>
      
      <Dialog
        open={testDialogOpen}
        onClose={() => setTestDialogOpen(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>Test Ruleset</DialogTitle>
        <DialogContent>
          {rulesetId && rulesetId !== 'new' && (
            <RuleTestInterface rulesetId={rulesetId} entityType={entityType} />
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setTestDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
      
      {/* Decision Table Builder Dialog */}
      {tableBuilderOpen && (
        <Dialog
          open={tableBuilderOpen}
          onClose={() => setTableBuilderOpen(false)}
          maxWidth="xl"
          fullWidth
        >
          <DialogContent>
            <DecisionTableBuilder
              table={currentTable}
              onSave={handleSaveTable}
              onCancel={() => {
                setTableBuilderOpen(false);
                setCurrentTable(null);
              }}
            />
          </DialogContent>
        </Dialog>
      )}
      
      {/* Execution Config Dialog */}
      {executionConfigOpen && (
        <Dialog
          open={executionConfigOpen}
          onClose={() => setExecutionConfigOpen(false)}
          maxWidth="lg"
          fullWidth
        >
          <DialogContent>
            <ExecutionEngineConfig
              rulesetId={rulesetId || 'new'}
              config={executionConfig}
              onSave={handleSaveExecutionConfig}
              onCancel={() => setExecutionConfigOpen(false)}
            />
          </DialogContent>
        </Dialog>
      )}
      
      {/* Rule Chain Builder Dialog */}
      {chainBuilderOpen && (
        <Dialog
          open={chainBuilderOpen}
          onClose={() => setChainBuilderOpen(false)}
          maxWidth="lg"
          fullWidth
        >
          <DialogContent>
            <RuleChainBuilder
              rulesetId={rulesetId || 'new'}
              availableRules={getAvailableRules()}
              chain={currentChain}
              onSave={handleSaveChain}
              onCancel={() => {
                setChainBuilderOpen(false);
                setCurrentChain(null);
              }}
            />
          </DialogContent>
        </Dialog>
      )}
      
      {/* Batch Scheduler Dialog */}
      {batchSchedulerOpen && (
        <Dialog
          open={batchSchedulerOpen}
          onClose={() => setBatchSchedulerOpen(false)}
          maxWidth="md"
          fullWidth
        >
          <DialogContent>
            <BatchScheduler
              rulesetId={rulesetId || 'new'}
              schedule={currentSchedule}
              onSave={handleSaveBatchSchedule}
              onCancel={() => {
                setBatchSchedulerOpen(false);
                setCurrentSchedule(null);
              }}
            />
          </DialogContent>
        </Dialog>
      )}
    </Box>
  );
};

export default VisualRulesBuilder;
