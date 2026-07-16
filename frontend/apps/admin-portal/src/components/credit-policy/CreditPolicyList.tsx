/**
 * Credit Policy List Component
 * View, filter, and manage credit policies
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Grid,
  Typography,
  Button,
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
  TablePagination,
  Paper,
  Chip,
  IconButton,
  Menu,
  MenuItem as MenuOption,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import {
  Add as AddIcon,
  MoreVert as MoreIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  FileCopy as CopyIcon,
  CheckCircle as ActiveIcon,
  Cancel as InactiveIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import creditPolicyService, {
  CreditPolicy,
  PolicyStatus
} from '@/services/creditPolicy.service';

interface CreditPolicyListProps {
  onCreateNew?: () => void;
  onEdit?: (policy: CreditPolicy) => void;
}

const CreditPolicyList: React.FC<CreditPolicyListProps> = ({
  onCreateNew,
  onEdit
}) => {
  const [policies, setPolicies] = useState<CreditPolicy[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Filters
  const [statusFilter, setStatusFilter] = useState<PolicyStatus | ''>('');
  const [activeFilter, setActiveFilter] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState('');
  
  // Pagination
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  
  // Menu
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedPolicy, setSelectedPolicy] = useState<CreditPolicy | null>(null);
  
  // Delete Dialog
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  
  // Statistics
  const [stats, setStats] = useState({
    total: 0,
    active: 0,
    draft: 0
  });

  useEffect(() => {
    loadPolicies();
    loadDashboardStats();
  }, [statusFilter, activeFilter]);

  const loadPolicies = async () => {
    setLoading(true);
    setError(null);
    try {
      const params: any = {
        skip: page * rowsPerPage,
        limit: rowsPerPage
      };
      
      if (statusFilter) params.status = statusFilter;
      if (activeFilter) params.is_active = activeFilter === 'active';
      
      const data = await creditPolicyService.listPolicies(params);
      setPolicies(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load policies');
    } finally {
      setLoading(false);
    }
  };

  const loadDashboardStats = async () => {
    try {
      const summary = await creditPolicyService.getDashboardSummary();
      setStats({
        total: summary.total_policies,
        active: summary.active_policies,
        draft: summary.draft_policies
      });
    } catch (err) {
      console.error('Failed to load stats:', err);
    }
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, policy: CreditPolicy) => {
    setAnchorEl(event.currentTarget);
    setSelectedPolicy(policy);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedPolicy(null);
  };

  const handleEdit = () => {
    if (selectedPolicy && onEdit) {
      onEdit(selectedPolicy);
    }
    handleMenuClose();
  };

  const handleActivate = async () => {
    if (!selectedPolicy) return;
    
    try {
      await creditPolicyService.activatePolicy(selectedPolicy.id);
      loadPolicies();
      loadDashboardStats();
    } catch (err: any) {
      setError(err.message || 'Failed to activate policy');
    }
    handleMenuClose();
  };

  const handleDeactivate = async () => {
    if (!selectedPolicy) return;
    
    try {
      await creditPolicyService.deactivatePolicy(selectedPolicy.id);
      loadPolicies();
      loadDashboardStats();
    } catch (err: any) {
      setError(err.message || 'Failed to deactivate policy');
    }
    handleMenuClose();
  };

  const handleClone = async () => {
    if (!selectedPolicy) return;
    
    const newName = prompt('Enter name for cloned policy:', `${selectedPolicy.name} (Copy)`);
    const newCode = prompt('Enter code for cloned policy:', `${selectedPolicy.code}-COPY`);
    
    if (newName && newCode) {
      try {
        await creditPolicyService.clonePolicy(selectedPolicy.id, newName, newCode);
        loadPolicies();
        loadDashboardStats();
      } catch (err: any) {
        setError(err.message || 'Failed to clone policy');
      }
    }
    handleMenuClose();
  };

  const handleDeleteClick = () => {
    setDeleteDialogOpen(true);
    handleMenuClose();
  };

  const handleDeleteConfirm = async () => {
    if (!selectedPolicy) return;
    
    try {
      await creditPolicyService.deletePolicy(selectedPolicy.id);
      loadPolicies();
      loadDashboardStats();
      setDeleteDialogOpen(false);
      setSelectedPolicy(null);
    } catch (err: any) {
      setError(err.message || 'Failed to delete policy');
    }
  };

  const getStatusColor = (status: PolicyStatus) => {
    switch (status) {
      case PolicyStatus.ACTIVE: return 'success';
      case PolicyStatus.DRAFT: return 'warning';
      case PolicyStatus.INACTIVE: return 'default';
      case PolicyStatus.ARCHIVED: return 'error';
      default: return 'default';
    }
  };

  const filteredPolicies = policies.filter(policy => {
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      return (
        policy.name.toLowerCase().includes(query) ||
        policy.code.toLowerCase().includes(query) ||
        (policy.description && policy.description.toLowerCase().includes(query))
      );
    }
    return true;
  });

  return (
    <Box sx={{ p: 3 }}>
      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Policies
              </Typography>
              <Typography variant="h4">
                {stats.total}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Active Policies
              </Typography>
              <Typography variant="h4" color="success.main">
                {stats.active}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Draft Policies
              </Typography>
              <Typography variant="h4" color="warning.main">
                {stats.draft}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Filters and Actions */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={3}>
              <TextField
                fullWidth
                label="Search"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search policies..."
              />
            </Grid>
            
            <Grid item xs={12} md={2}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value as PolicyStatus | '')}
                  label="Status"
                >
                  <MenuItem value="">All</MenuItem>
                  {Object.values(PolicyStatus).map((status) => (
                    <MenuItem key={status} value={status}>{status}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={2}>
              <FormControl fullWidth>
                <InputLabel>Active Status</InputLabel>
                <Select
                  value={activeFilter}
                  onChange={(e) => setActiveFilter(e.target.value)}
                  label="Active Status"
                >
                  <MenuItem value="">All</MenuItem>
                  <MenuItem value="active">Active Only</MenuItem>
                  <MenuItem value="inactive">Inactive Only</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={3}>
              <Button
                variant="outlined"
                startIcon={<RefreshIcon />}
                onClick={() => {
                  loadPolicies();
                  loadDashboardStats();
                }}
                fullWidth
              >
                Refresh
              </Button>
            </Grid>

            <Grid item xs={12} md={2}>
              {onCreateNew && (
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={onCreateNew}
                  fullWidth
                >
                  New Policy
                </Button>
              )}
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Policies Table */}
      <Card>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Policy Name</TableCell>
                <TableCell>Code</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Active</TableCell>
                <TableCell>Version</TableCell>
                <TableCell>Effective From</TableCell>
                <TableCell>Created</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={8} align="center">
                    <CircularProgress />
                  </TableCell>
                </TableRow>
              ) : filteredPolicies.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={8} align="center">
                    <Typography variant="body1" color="text.secondary" py={4}>
                      No policies found
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                filteredPolicies.map((policy) => (
                  <TableRow key={policy.id} hover>
                    <TableCell>
                      <Typography variant="body2" fontWeight="medium">
                        {policy.name}
                      </Typography>
                      {policy.description && (
                        <Typography variant="caption" color="text.secondary">
                          {policy.description.substring(0, 60)}
                          {policy.description.length > 60 && '...'}
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell>{policy.code}</TableCell>
                    <TableCell>
                      <Chip
                        label={policy.status}
                        color={getStatusColor(policy.status)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      {policy.is_active ? (
                        <ActiveIcon color="success" />
                      ) : (
                        <InactiveIcon color="disabled" />
                      )}
                    </TableCell>
                    <TableCell>{policy.version}</TableCell>
                    <TableCell>
                      {policy.effective_from 
                        ? new Date(policy.effective_from).toLocaleDateString()
                        : 'N/A'}
                    </TableCell>
                    <TableCell>
                      {new Date(policy.created_at).toLocaleDateString()}
                    </TableCell>
                    <TableCell align="right">
                      <IconButton
                        size="small"
                        onClick={(e) => handleMenuOpen(e, policy)}
                      >
                        <MoreIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
        
        <TablePagination
          component="div"
          count={stats.total}
          page={page}
          onPageChange={(_, newPage) => setPage(newPage)}
          rowsPerPage={rowsPerPage}
          onRowsPerPageChange={(e) => {
            setRowsPerPage(parseInt(e.target.value, 10));
            setPage(0);
          }}
        />
      </Card>

      {/* Actions Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuOption onClick={handleEdit}>
          <EditIcon fontSize="small" sx={{ mr: 1 }} />
          Edit
        </MenuOption>
        {selectedPolicy && !selectedPolicy.is_active && (
          <MenuOption onClick={handleActivate}>
            <ActiveIcon fontSize="small" sx={{ mr: 1 }} />
            Activate
          </MenuOption>
        )}
        {selectedPolicy && selectedPolicy.is_active && (
          <MenuOption onClick={handleDeactivate}>
            <InactiveIcon fontSize="small" sx={{ mr: 1 }} />
            Deactivate
          </MenuOption>
        )}
        <MenuOption onClick={handleClone}>
          <CopyIcon fontSize="small" sx={{ mr: 1 }} />
          Clone
        </MenuOption>
        <MenuOption onClick={handleDeleteClick}>
          <DeleteIcon fontSize="small" sx={{ mr: 1 }} color="error" />
          Delete
        </MenuOption>
      </Menu>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete the policy "{selectedPolicy?.name}"?
            This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleDeleteConfirm} color="error" variant="contained">
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default CreditPolicyList;
