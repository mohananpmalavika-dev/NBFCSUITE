/**
 * Approval Chain Configurator
 * Visual configurator for approval workflows
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  IconButton,
  Stack,
  Card,
  CardContent,
  CardActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Stepper,
  Step,
  StepLabel,
  Switch,
  FormControlLabel,
  Grid,
  Tooltip,
  Divider,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Save as SaveIcon,
  ArrowForward,
  CallSplit,
  AccountTree,
  Person,
  Group,
} from '@mui/icons-material';
import approvalService, { ApprovalChain, ApprovalLevel } from '../../services/approvalService';

interface ApprovalChainConfiguratorProps {
  chainId?: string;
  onSave?: (chain: ApprovalChain) => void;
}

const ApprovalChainConfigurator: React.FC<ApprovalChainConfiguratorProps> = ({
  chainId,
  onSave,
}) => {
  const [chain, setChain] = useState<ApprovalChain>({
    chain_id: '',
    name: '',
    description: '',
    entity_type: '',
    levels: [],
    overall_type: 'sequential',
    maker_checker_enabled: false,
    version: 1,
  });

  const [editingLevel, setEditingLevel] = useState<ApprovalLevel | null>(null);
  const [levelDialog, setLevelDialog] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (chainId) {
      loadChain();
    }
  }, [chainId]);

  const loadChain = async () => {
    setLoading(true);
    try {
      const response = await approvalService.getApprovalChain(chainId!);
      setChain(response.chain);
    } catch (error) {
      console.error('Failed to load approval chain:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddLevel = () => {
    setEditingLevel({
      level: chain.levels.length + 1,
      name: '',
      assigned_roles: [],
      approval_type: 'sequential',
      sla_hours: 24,
    });
    setLevelDialog(true);
  };

  const handleEditLevel = (level: ApprovalLevel) => {
    setEditingLevel({ ...level });
    setLevelDialog(true);
  };

  const handleSaveLevel = () => {
    if (!editingLevel) return;

    const existingIndex = chain.levels.findIndex((l) => l.level === editingLevel.level);
    
    if (existingIndex >= 0) {
      // Update existing
      const newLevels = [...chain.levels];
      newLevels[existingIndex] = editingLevel;
      setChain({ ...chain, levels: newLevels });
    } else {
      // Add new
      setChain({
        ...chain,
        levels: [...chain.levels, editingLevel],
      });
    }

    setLevelDialog(false);
    setEditingLevel(null);
  };

  const handleDeleteLevel = (levelNumber: number) => {
    setChain({
      ...chain,
      levels: chain.levels.filter((l) => l.level !== levelNumber),
    });
  };

  const handleSaveChain = async () => {
    setLoading(true);
    try {
      if (chainId) {
        await approvalService.updateApprovalChain(chainId, chain);
      } else {
        await approvalService.createApprovalChain(chain);
      }
      
      if (onSave) {
        onSave(chain);
      }
    } catch (error) {
      console.error('Failed to save approval chain:', error);
    } finally {
      setLoading(false);
    }
  };

  const getApprovalTypeIcon = (type: string) => {
    switch (type) {
      case 'sequential':
        return <ArrowForward />;
      case 'parallel':
        return <AccountTree />;
      case 'any_one':
        return <CallSplit />;
      case 'majority':
        return <Group />;
      default:
        return <Person />;
    }
  };

  const getApprovalTypeLabel = (type: string) => {
    switch (type) {
      case 'sequential':
        return 'Sequential (One after another)';
      case 'parallel':
        return 'Parallel (All must approve)';
      case 'any_one':
        return 'Any One (First wins)';
      case 'majority':
        return 'Majority (Threshold-based)';
      default:
        return type;
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" fontWeight="bold">
          {chainId ? 'Edit' : 'Create'} Approval Chain
        </Typography>
        <Button
          variant="contained"
          startIcon={<SaveIcon />}
          onClick={handleSaveChain}
          disabled={!chain.name || chain.levels.length === 0 || loading}
        >
          Save Chain
        </Button>
      </Stack>

      {/* Basic Configuration */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Basic Configuration
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Chain Name"
              value={chain.name}
              onChange={(e) => setChain({ ...chain, name: e.target.value })}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Chain ID"
              value={chain.chain_id}
              onChange={(e) => setChain({ ...chain, chain_id: e.target.value })}
              placeholder="e.g., loan_approval_standard"
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              multiline
              rows={2}
              label="Description"
              value={chain.description}
              onChange={(e) => setChain({ ...chain, description: e.target.value })}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Entity Type"
              value={chain.entity_type}
              onChange={(e) => setChain({ ...chain, entity_type: e.target.value })}
              placeholder="e.g., loan_application"
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Overall Type</InputLabel>
              <Select
                value={chain.overall_type}
                onChange={(e) =>
                  setChain({ ...chain, overall_type: e.target.value as any })
                }
                label="Overall Type"
              >
                <MenuItem value="sequential">Sequential</MenuItem>
                <MenuItem value="parallel">Parallel</MenuItem>
                <MenuItem value="any_one">Any One</MenuItem>
                <MenuItem value="majority">Majority</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12}>
            <FormControlLabel
              control={
                <Switch
                  checked={chain.maker_checker_enabled}
                  onChange={(e) =>
                    setChain({ ...chain, maker_checker_enabled: e.target.checked })
                  }
                />
              }
              label="Enable Maker-Checker (No self-approval)"
            />
          </Grid>
        </Grid>
      </Paper>

      {/* Approval Levels */}
      <Paper sx={{ p: 3 }}>
        <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">Approval Levels</Typography>
          <Button startIcon={<AddIcon />} onClick={handleAddLevel} variant="outlined">
            Add Level
          </Button>
        </Stack>

        {chain.levels.length === 0 ? (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="body1" color="textSecondary">
              No approval levels defined. Click "Add Level" to create one.
            </Typography>
          </Box>
        ) : (
          <Stepper orientation="vertical">
            {chain.levels.map((level, index) => (
              <Step key={level.level} active>
                <StepLabel>
                  <Stack direction="row" spacing={2} alignItems="center">
                    <Typography variant="subtitle1" fontWeight="bold">
                      Level {level.level}: {level.name}
                    </Typography>
                    <Chip
                      icon={getApprovalTypeIcon(level.approval_type)}
                      label={level.approval_type}
                      size="small"
                      color="primary"
                    />
                  </Stack>
                </StepLabel>
                <Box sx={{ ml: 4, mt: 1 }}>
                  <Card variant="outlined">
                    <CardContent>
                      <Grid container spacing={2}>
                        <Grid item xs={12} md={6}>
                          <Typography variant="body2" color="textSecondary">
                            Type
                          </Typography>
                          <Typography variant="body1">
                            {getApprovalTypeLabel(level.approval_type)}
                          </Typography>
                        </Grid>
                        <Grid item xs={12} md={6}>
                          <Typography variant="body2" color="textSecondary">
                            SLA
                          </Typography>
                          <Typography variant="body1">
                            {level.sla_hours || 24} hours
                          </Typography>
                        </Grid>
                        {level.assigned_roles && level.assigned_roles.length > 0 && (
                          <Grid item xs={12}>
                            <Typography variant="body2" color="textSecondary">
                              Assigned Roles
                            </Typography>
                            <Stack direction="row" spacing={1} mt={0.5}>
                              {level.assigned_roles.map((role, idx) => (
                                <Chip key={idx} label={role} size="small" />
                              ))}
                            </Stack>
                          </Grid>
                        )}
                        {level.approval_type === 'majority' && (
                          <Grid item xs={12}>
                            <Typography variant="body2" color="textSecondary">
                              Threshold
                            </Typography>
                            <Typography variant="body1">
                              {level.threshold
                                ? `${level.threshold} approvals required`
                                : `${level.threshold_percentage}% must approve`}
                            </Typography>
                          </Grid>
                        )}
                      </Grid>
                    </CardContent>
                    <CardActions>
                      <Button
                        size="small"
                        startIcon={<EditIcon />}
                        onClick={() => handleEditLevel(level)}
                      >
                        Edit
                      </Button>
                      <Button
                        size="small"
                        color="error"
                        startIcon={<DeleteIcon />}
                        onClick={() => handleDeleteLevel(level.level)}
                      >
                        Delete
                      </Button>
                    </CardActions>
                  </Card>
                </Box>
              </Step>
            ))}
          </Stepper>
        )}
      </Paper>

      {/* Level Edit Dialog */}
      <Dialog
        open={levelDialog}
        onClose={() => setLevelDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {editingLevel?.level ? `Edit Level ${editingLevel.level}` : 'Add Level'}
        </DialogTitle>
        <DialogContent>
          {editingLevel && (
            <Stack spacing={2} sx={{ mt: 2 }}>
              <TextField
                fullWidth
                label="Level Name"
                value={editingLevel.name}
                onChange={(e) =>
                  setEditingLevel({ ...editingLevel, name: e.target.value })
                }
              />

              <FormControl fullWidth>
                <InputLabel>Approval Type</InputLabel>
                <Select
                  value={editingLevel.approval_type}
                  onChange={(e) =>
                    setEditingLevel({
                      ...editingLevel,
                      approval_type: e.target.value as any,
                    })
                  }
                  label="Approval Type"
                >
                  <MenuItem value="sequential">Sequential (One by one)</MenuItem>
                  <MenuItem value="parallel">Parallel (All must approve)</MenuItem>
                  <MenuItem value="any_one">Any One (First wins)</MenuItem>
                  <MenuItem value="majority">Majority (Threshold)</MenuItem>
                </Select>
              </FormControl>

              <TextField
                fullWidth
                label="Assigned Roles (comma-separated)"
                value={editingLevel.assigned_roles?.join(', ') || ''}
                onChange={(e) =>
                  setEditingLevel({
                    ...editingLevel,
                    assigned_roles: e.target.value.split(',').map((r) => r.trim()),
                  })
                }
                placeholder="e.g., loan_officer, branch_manager"
              />

              <TextField
                fullWidth
                type="number"
                label="SLA Hours"
                value={editingLevel.sla_hours || 24}
                onChange={(e) =>
                  setEditingLevel({
                    ...editingLevel,
                    sla_hours: parseInt(e.target.value),
                  })
                }
              />

              {editingLevel.approval_type === 'majority' && (
                <>
                  <TextField
                    fullWidth
                    type="number"
                    label="Threshold (number of approvals)"
                    value={editingLevel.threshold || ''}
                    onChange={(e) =>
                      setEditingLevel({
                        ...editingLevel,
                        threshold: parseInt(e.target.value) || undefined,
                      })
                    }
                  />
                  <Typography variant="caption" color="textSecondary">
                    OR
                  </Typography>
                  <TextField
                    fullWidth
                    type="number"
                    label="Threshold Percentage"
                    value={editingLevel.threshold_percentage || ''}
                    onChange={(e) =>
                      setEditingLevel({
                        ...editingLevel,
                        threshold_percentage: parseFloat(e.target.value) || undefined,
                      })
                    }
                    inputProps={{ min: 0, max: 100, step: 1 }}
                  />
                </>
              )}
            </Stack>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setLevelDialog(false)}>Cancel</Button>
          <Button onClick={handleSaveLevel} variant="contained">
            Save Level
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ApprovalChainConfigurator;
