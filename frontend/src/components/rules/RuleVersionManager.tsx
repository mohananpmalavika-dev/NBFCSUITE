/**
 * Rule Version Manager Component
 * 
 * Manage rule versions: create, compare, activate, rollback, and view history
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
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Stepper,
  Step,
  StepLabel,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Tabs,
  Tab,
} from '@mui/material';
import {
  Add as AddIcon,
  Compare as CompareIcon,
  History as HistoryIcon,
  Check as CheckIcon,
  Undo as UndoIcon,
  Archive as ArchiveIcon,
  Visibility as VisibilityIcon,
  Edit as EditIcon,
  GetApp as DownloadIcon,
  Circle as CircleIcon,
} from '@mui/icons-material';

export interface RuleVersion {
  version_id: string;
  version_number: string;
  version_name: string;
  ruleset_id: string;
  status: 'draft' | 'active' | 'inactive' | 'archived';
  change_type: 'created' | 'modified' | 'deleted' | 'restored';
  change_summary: string;
  ruleset_snapshot: any;
  parent_version_id?: string;
  created_by?: number;
  created_at: string;
  activated_by?: number;
  activated_at?: string;
  effective_from?: string;
  effective_to?: string;
}

export interface VersionComparison {
  version1_id: string;
  version2_id: string;
  version1_number: string;
  version2_number: string;
  added_rules: any[];
  modified_rules: any[];
  deleted_rules: any[];
  field_changes: any;
  comparison_summary: string;
}

interface RuleVersionManagerProps {
  rulesetId: string;
  onVersionChange?: (version: RuleVersion) => void;
}

const RuleVersionManager: React.FC<RuleVersionManagerProps> = ({
  rulesetId,
  onVersionChange,
}) => {
  const [versions, setVersions] = useState<RuleVersion[]>([]);
  const [selectedVersion, setSelectedVersion] = useState<RuleVersion | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState(0);

  
  // Dialog states
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [compareDialogOpen, setCompareDialogOpen] = useState(false);
  const [activateDialogOpen, setActivateDialogOpen] = useState(false);
  const [rollbackDialogOpen, setRollbackDialogOpen] = useState(false);
  const [historyDialogOpen, setHistoryDialogOpen] = useState(false);
  
  // Form states
  const [newVersionName, setNewVersionName] = useState('');
  const [changeSummary, setChangeSummary] = useState('');
  const [changeType, setChangeType] = useState<'created' | 'modified' | 'deleted' | 'restored'>('modified');
  const [effectiveFrom, setEffectiveFrom] = useState('');
  const [rollbackReason, setRollbackReason] = useState('');
  
  // Comparison state
  const [compareVersion1, setCompareVersion1] = useState('');
  const [compareVersion2, setCompareVersion2] = useState('');
  const [comparisonResult, setComparisonResult] = useState<VersionComparison | null>(null);
  
  // History state
  const [auditTrail, setAuditTrail] = useState<any[]>([]);

  useEffect(() => {
    loadVersions();
  }, [rulesetId]);

  const loadVersions = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`/api/rules/versions?ruleset_id=${rulesetId}`);
      const data = await response.json();
      if (data.success) {
        setVersions(data.data);
      } else {
        setError('Failed to load versions');
      }
    } catch (err) {
      setError('Error loading versions');
    } finally {
      setLoading(false);
    }
  };


  const handleCreateVersion = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/rules/versions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ruleset_id: rulesetId,
          version_name: newVersionName,
          change_summary: changeSummary,
          change_type: changeType,
        }),
      });
      const data = await response.json();
      if (data.success) {
        setSuccess('Version created successfully');
        setCreateDialogOpen(false);
        setNewVersionName('');
        setChangeSummary('');
        loadVersions();
      } else {
        setError(data.detail || 'Failed to create version');
      }
    } catch (err) {
      setError('Error creating version');
    } finally {
      setLoading(false);
    }
  };

  const handleActivateVersion = async () => {
    if (!selectedVersion) return;
    
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`/api/rules/versions/${selectedVersion.version_id}/activate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          effective_from: effectiveFrom || null,
        }),
      });
      const data = await response.json();
      if (data.success) {
        setSuccess('Version activated successfully');
        setActivateDialogOpen(false);
        setEffectiveFrom('');
        loadVersions();
        if (onVersionChange) {
          onVersionChange(data.data);
        }
      } else {
        setError(data.detail || 'Failed to activate version');
      }
    } catch (err) {
      setError('Error activating version');
    } finally {
      setLoading(false);
    }
  };


  const handleCompareVersions = async () => {
    if (!compareVersion1 || !compareVersion2) return;
    
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/rules/versions/compare', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          version1_id: compareVersion1,
          version2_id: compareVersion2,
        }),
      });
      const data = await response.json();
      if (data.success) {
        setComparisonResult(data.data);
      } else {
        setError(data.detail || 'Failed to compare versions');
      }
    } catch (err) {
      setError('Error comparing versions');
    } finally {
      setLoading(false);
    }
  };

  const handleRollback = async () => {
    if (!selectedVersion) return;
    
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`/api/rules/versions/${selectedVersion.version_id}/rollback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          rollback_reason: rollbackReason,
        }),
      });
      const data = await response.json();
      if (data.success) {
        setSuccess(data.message || 'Rollback successful');
        setRollbackDialogOpen(false);
        setRollbackReason('');
        loadVersions();
        if (onVersionChange) {
          onVersionChange(data.data);
        }
      } else {
        setError(data.detail || 'Failed to rollback');
      }
    } catch (err) {
      setError('Error during rollback');
    } finally {
      setLoading(false);
    }
  };

  const handleArchiveVersion = async (versionId: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`/api/rules/versions/${versionId}/archive`, {
        method: 'POST',
      });
      const data = await response.json();
      if (data.success) {
        setSuccess('Version archived successfully');
        loadVersions();
      } else {
        setError(data.detail || 'Failed to archive version');
      }
    } catch (err) {
      setError('Error archiving version');
    } finally {
      setLoading(false);
    }
  };

  const loadVersionHistory = async (versionId: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`/api/rules/versions/${versionId}/history`);
      const data = await response.json();
      if (data.success) {
        setAuditTrail(data.data.audit_trail || []);
      } else {
        setError('Failed to load version history');
      }
    } catch (err) {
      setError('Error loading version history');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'success';
      case 'draft': return 'info';
      case 'inactive': return 'warning';
      case 'archived': return 'default';
      default: return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return <CheckIcon fontSize="small" />;
      case 'draft': return <EditIcon fontSize="small" />;
      case 'inactive': return <CircleIcon fontSize="small" />;
      case 'archived': return <ArchiveIcon fontSize="small" />;
      default: return <CircleIcon fontSize="small" />;
    }
  };


  return (
    <Box sx={{ p: 3 }}>
      <Paper sx={{ p: 3 }}>
        {/* Header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h5">Version Management</Typography>
          <Box>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => setCreateDialogOpen(true)}
              sx={{ mr: 1 }}
            >
              Create Version
            </Button>
            <Button
              variant="outlined"
              startIcon={<CompareIcon />}
              onClick={() => setCompareDialogOpen(true)}
              disabled={versions.length < 2}
            >
              Compare Versions
            </Button>
          </Box>
        </Box>

        <Divider sx={{ mb: 3 }} />

        {/* Alerts */}
        {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>{error}</Alert>}
        {success && <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(null)}>{success}</Alert>}

        {/* Tabs */}
        <Tabs value={activeTab} onChange={(e, v) => setActiveTab(v)} sx={{ mb: 3 }}>
          <Tab label="All Versions" />
          <Tab label="Active" />
          <Tab label="Draft" />
          <Tab label="Archived" />
        </Tabs>

        {/* Version List */}
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Version</TableCell>
                <TableCell>Name</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Change Type</TableCell>
                <TableCell>Summary</TableCell>
                <TableCell>Created</TableCell>
                <TableCell>Effective Period</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {versions
                .filter((v) => {
                  if (activeTab === 0) return true;
                  if (activeTab === 1) return v.status === 'active';
                  if (activeTab === 2) return v.status === 'draft';
                  if (activeTab === 3) return v.status === 'archived';
                  return true;
                })
                .map((version) => (
                  <TableRow key={version.version_id}>
                    <TableCell>
                      <Typography variant="body2" fontWeight="bold">
                        v{version.version_number}
                      </Typography>
                    </TableCell>
                    <TableCell>{version.version_name}</TableCell>
                    <TableCell>
                      <Chip
                        icon={getStatusIcon(version.status)}
                        label={version.status.toUpperCase()}
                        color={getStatusColor(version.status)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip label={version.change_type} size="small" variant="outlined" />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" noWrap sx={{ maxWidth: 200 }}>
                        {version.change_summary}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="caption">
                        {new Date(version.created_at).toLocaleDateString()}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      {version.effective_from && (
                        <Typography variant="caption">
                          {new Date(version.effective_from).toLocaleDateString()}
                          {version.effective_to && ` - ${new Date(version.effective_to).toLocaleDateString()}`}
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Tooltip title="View Details">
                          <IconButton size="small" onClick={() => setSelectedVersion(version)}>
                            <VisibilityIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                        {version.status === 'draft' && (
                          <Tooltip title="Activate">
                            <IconButton
                              size="small"
                              color="primary"
                              onClick={() => {
                                setSelectedVersion(version);
                                setActivateDialogOpen(true);
                              }}
                            >
                              <CheckIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        )}
                        {version.status !== 'active' && version.status !== 'archived' && (
                          <Tooltip title="Rollback to this version">
                            <IconButton
                              size="small"
                              color="warning"
                              onClick={() => {
                                setSelectedVersion(version);
                                setRollbackDialogOpen(true);
                              }}
                            >
                              <UndoIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        )}
                        {version.status !== 'archived' && version.status !== 'active' && (
                          <Tooltip title="Archive">
                            <IconButton
                              size="small"
                              onClick={() => handleArchiveVersion(version.version_id)}
                            >
                              <ArchiveIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        )}
                        <Tooltip title="View History">
                          <IconButton
                            size="small"
                            onClick={() => {
                              setSelectedVersion(version);
                              loadVersionHistory(version.version_id);
                              setHistoryDialogOpen(true);
                            }}
                          >
                            <HistoryIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
            </TableBody>
          </Table>
        </TableContainer>


      {/* Create Version Dialog */}
      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Version</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <TextField
              fullWidth
              label="Version Name"
              value={newVersionName}
              onChange={(e) => setNewVersionName(e.target.value)}
              sx={{ mb: 2 }}
            />
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Change Type</InputLabel>
              <Select
                value={changeType}
                onChange={(e) => setChangeType(e.target.value as any)}
                label="Change Type"
              >
                <MenuItem value="created">Created</MenuItem>
                <MenuItem value="modified">Modified</MenuItem>
                <MenuItem value="deleted">Deleted</MenuItem>
                <MenuItem value="restored">Restored</MenuItem>
              </Select>
            </FormControl>
            <TextField
              fullWidth
              label="Change Summary"
              multiline
              rows={4}
              value={changeSummary}
              onChange={(e) => setChangeSummary(e.target.value)}
              helperText="Describe what changed in this version"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleCreateVersion}
            disabled={!newVersionName || !changeSummary || loading}
          >
            Create Version
          </Button>
        </DialogActions>
      </Dialog>

      {/* Activate Version Dialog */}
      <Dialog open={activateDialogOpen} onClose={() => setActivateDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Activate Version</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <Alert severity="info" sx={{ mb: 2 }}>
              Activating this version will deactivate all other active versions for this ruleset.
            </Alert>
            {selectedVersion && (
              <Card sx={{ mb: 2 }}>
                <CardContent>
                  <Typography variant="subtitle2">Version: v{selectedVersion.version_number}</Typography>
                  <Typography variant="body2">{selectedVersion.version_name}</Typography>
                  <Typography variant="caption" color="text.secondary">
                    {selectedVersion.change_summary}
                  </Typography>
                </CardContent>
              </Card>
            )}
            <TextField
              fullWidth
              type="datetime-local"
              label="Effective From (optional)"
              value={effectiveFrom}
              onChange={(e) => setEffectiveFrom(e.target.value)}
              InputLabelProps={{ shrink: true }}
              helperText="Leave empty to activate immediately"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setActivateDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            color="primary"
            onClick={handleActivateVersion}
            disabled={loading}
          >
            Activate
          </Button>
        </DialogActions>
      </Dialog>


      {/* Rollback Dialog */}
      <Dialog open={rollbackDialogOpen} onClose={() => setRollbackDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Rollback to Version</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <Alert severity="warning" sx={{ mb: 2 }}>
              This will create a new version based on the selected version. The current active version will be deactivated.
            </Alert>
            {selectedVersion && (
              <Card sx={{ mb: 2 }}>
                <CardContent>
                  <Typography variant="subtitle2">Rolling back to: v{selectedVersion.version_number}</Typography>
                  <Typography variant="body2">{selectedVersion.version_name}</Typography>
                </CardContent>
              </Card>
            )}
            <TextField
              fullWidth
              label="Rollback Reason"
              multiline
              rows={3}
              value={rollbackReason}
              onChange={(e) => setRollbackReason(e.target.value)}
              required
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRollbackDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            color="warning"
            onClick={handleRollback}
            disabled={!rollbackReason || loading}
          >
            Rollback
          </Button>
        </DialogActions>
      </Dialog>

      {/* Compare Versions Dialog */}
      <Dialog open={compareDialogOpen} onClose={() => setCompareDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Compare Versions</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <Grid container spacing={2} sx={{ mb: 3 }}>
              <Grid item xs={6}>
                <FormControl fullWidth>
                  <InputLabel>Version 1</InputLabel>
                  <Select
                    value={compareVersion1}
                    onChange={(e) => setCompareVersion1(e.target.value)}
                    label="Version 1"
                  >
                    {versions.map((v) => (
                      <MenuItem key={v.version_id} value={v.version_id}>
                        v{v.version_number} - {v.version_name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={6}>
                <FormControl fullWidth>
                  <InputLabel>Version 2</InputLabel>
                  <Select
                    value={compareVersion2}
                    onChange={(e) => setCompareVersion2(e.target.value)}
                    label="Version 2"
                  >
                    {versions.map((v) => (
                      <MenuItem key={v.version_id} value={v.version_id}>
                        v{v.version_number} - {v.version_name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
            </Grid>

            <Button
              variant="contained"
              fullWidth
              onClick={handleCompareVersions}
              disabled={!compareVersion1 || !compareVersion2 || loading}
              sx={{ mb: 3 }}
            >
              Compare
            </Button>

            {comparisonResult && (
              <Box>
                <Alert severity="info" sx={{ mb: 2 }}>
                  {comparisonResult.comparison_summary}
                </Alert>

                <Grid container spacing={2}>
                  <Grid item xs={4}>
                    <Card sx={{ bgcolor: 'success.light', color: 'success.contrastText' }}>
                      <CardContent>
                        <Typography variant="h4">{comparisonResult.added_rules.length}</Typography>
                        <Typography variant="body2">Rules Added</Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={4}>
                    <Card sx={{ bgcolor: 'warning.light', color: 'warning.contrastText' }}>
                      <CardContent>
                        <Typography variant="h4">{comparisonResult.modified_rules.length}</Typography>
                        <Typography variant="body2">Rules Modified</Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={4}>
                    <Card sx={{ bgcolor: 'error.light', color: 'error.contrastText' }}>
                      <CardContent>
                        <Typography variant="h4">{comparisonResult.deleted_rules.length}</Typography>
                        <Typography variant="body2">Rules Deleted</Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                </Grid>

                {comparisonResult.modified_rules.length > 0 && (
                  <Box sx={{ mt: 3 }}>
                    <Typography variant="subtitle1" sx={{ mb: 1 }}>Modified Rules</Typography>
                    <List>
                      {comparisonResult.modified_rules.map((rule: any, idx: number) => (
                        <ListItem key={idx}>
                          <ListItemText
                            primary={rule.rule_name}
                            secondary={`${Object.keys(rule.changes || {}).length} field(s) changed`}
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
          <Button onClick={() => {
            setCompareDialogOpen(false);
            setComparisonResult(null);
          }}>
            Close
          </Button>
        </DialogActions>
      </Dialog>


      {/* History Dialog */}
      <Dialog open={historyDialogOpen} onClose={() => setHistoryDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Version History</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            {selectedVersion && (
              <Card sx={{ mb: 3 }}>
                <CardContent>
                  <Typography variant="h6">v{selectedVersion.version_number} - {selectedVersion.version_name}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    {selectedVersion.change_summary}
                  </Typography>
                </CardContent>
              </Card>
            )}

            {auditTrail.length > 0 ? (
              <Stepper orientation="vertical">
                {auditTrail.map((entry: any, index: number) => (
                  <Step key={index} active>
                    <StepLabel>
                      <Typography variant="subtitle2">{entry.action}</Typography>
                      <Typography variant="caption" color="text.secondary">
                        {new Date(entry.timestamp).toLocaleString()}
                        {entry.user_name && ` by ${entry.user_name}`}
                      </Typography>
                    </StepLabel>
                    {entry.details && (
                      <Box sx={{ pl: 4, pb: 2 }}>
                        <Typography variant="body2">{entry.details}</Typography>
                      </Box>
                    )}
                  </Step>
                ))}
              </Stepper>
            ) : (
              <Alert severity="info">No history available for this version</Alert>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setHistoryDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
      </Paper>
    </Box>
  );
};

export default RuleVersionManager;
