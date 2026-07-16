/**
 * Product Variant List Component
 * View, filter, and manage product variants
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
  Refresh as RefreshIcon,
  TrendingUp as PerformanceIcon
} from '@mui/icons-material';
import productLifecycleService, {
  ProductVariant,
  VariantType,
  VariantStatus
} from '@/services/productLifecycle.service';

interface VariantListProps {
  onCreateNew?: () => void;
  onEdit?: (variant: ProductVariant) => void;
  onViewPerformance?: (variant: ProductVariant) => void;
}

const VariantList: React.FC<VariantListProps> = ({
  onCreateNew,
  onEdit,
  onViewPerformance
}) => {
  const [variants, setVariants] = useState<ProductVariant[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Filters
  const [typeFilter, setTypeFilter] = useState<VariantType | ''>('');
  const [statusFilter, setStatusFilter] = useState<VariantStatus | ''>('');
  const [activeFilter, setActiveFilter] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState('');
  
  // Pagination
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [totalCount, setTotalCount] = useState(0);
  
  // Menu
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedVariant, setSelectedVariant] = useState<ProductVariant | null>(null);
  
  // Delete Dialog
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  
  // Statistics
  const [stats, setStats] = useState({
    total: 0,
    active: 0,
    promotional: 0,
    seasonal: 0
  });

  useEffect(() => {
    loadVariants();
  }, [typeFilter, statusFilter, activeFilter, page, rowsPerPage]);

  useEffect(() => {
    loadDashboardStats();
  }, []);

  const loadVariants = async () => {
    setLoading(true);
    setError(null);
    try {
      const params: any = {
        skip: page * rowsPerPage,
        limit: rowsPerPage
      };
      
      if (typeFilter) params.variant_type = typeFilter;
      if (statusFilter) params.status = statusFilter;
      if (activeFilter) params.is_active = activeFilter === 'active';
      
      const data = await productLifecycleService.listVariants(params);
      setVariants(data);
      setTotalCount(data.length); // In production, get from API response
    } catch (err: any) {
      setError(err.message || 'Failed to load variants');
    } finally {
      setLoading(false);
    }
  };

  const loadDashboardStats = async () => {
    try {
      const dashboard = await productLifecycleService.getLifecycleDashboard();
      setStats({
        total: dashboard.variants.total,
        active: dashboard.variants.active,
        promotional: dashboard.variants.by_type.PROMOTIONAL || 0,
        seasonal: dashboard.variants.by_type.SEASONAL || 0
      });
    } catch (err) {
      console.error('Failed to load stats:', err);
    }
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, variant: ProductVariant) => {
    setAnchorEl(event.currentTarget);
    setSelectedVariant(variant);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedVariant(null);
  };

  const handleEdit = () => {
    if (selectedVariant && onEdit) {
      onEdit(selectedVariant);
    }
    handleMenuClose();
  };

  const handleViewPerformance = () => {
    if (selectedVariant && onViewPerformance) {
      onViewPerformance(selectedVariant);
    }
    handleMenuClose();
  };

  const handleActivate = async () => {
    if (!selectedVariant) return;
    
    try {
      await productLifecycleService.activateVariant(selectedVariant.id);
      loadVariants();
      loadDashboardStats();
    } catch (err: any) {
      setError(err.message || 'Failed to activate variant');
    }
    handleMenuClose();
  };

  const handleDeactivate = async () => {
    if (!selectedVariant) return;
    
    try {
      await productLifecycleService.deactivateVariant(selectedVariant.id);
      loadVariants();
      loadDashboardStats();
    } catch (err: any) {
      setError(err.message || 'Failed to deactivate variant');
    }
    handleMenuClose();
  };

  const handleClone = async () => {
    if (!selectedVariant) return;
    
    const newName = prompt('Enter name for cloned variant:', `${selectedVariant.variant_name} (Copy)`);
    const newCode = prompt('Enter code for cloned variant:', `${selectedVariant.variant_code}-COPY`);
    
    if (newName && newCode) {
      try {
        await productLifecycleService.cloneVariant(selectedVariant.id, newCode, newName);
        loadVariants();
        loadDashboardStats();
      } catch (err: any) {
        setError(err.message || 'Failed to clone variant');
      }
    }
    handleMenuClose();
  };

  const handleDeleteClick = () => {
    setDeleteDialogOpen(true);
    handleMenuClose();
  };

  const handleDeleteConfirm = async () => {
    if (!selectedVariant) return;
    
    try {
      await productLifecycleService.deleteVariant(selectedVariant.id);
      loadVariants();
      loadDashboardStats();
      setDeleteDialogOpen(false);
      setSelectedVariant(null);
    } catch (err: any) {
      setError(err.message || 'Failed to delete variant');
    }
  };

  const getStatusColor = (status: VariantStatus) => {
    return productLifecycleService.getVariantStatusColor(status) as any;
  };

  const getTypeLabel = (type: VariantType) => {
    return productLifecycleService.getVariantTypeLabel(type);
  };

  const filteredVariants = variants.filter(variant => {
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      return (
        variant.variant_name.toLowerCase().includes(query) ||
        variant.variant_code.toLowerCase().includes(query) ||
        (variant.description && variant.description.toLowerCase().includes(query))
      );
    }
    return true;
  });

  return (
    <Box sx={{ p: 3 }}>
      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Variants
              </Typography>
              <Typography variant="h4">
                {stats.total}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Active Variants
              </Typography>
              <Typography variant="h4" color="success.main">
                {stats.active}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Promotional
              </Typography>
              <Typography variant="h4" color="info.main">
                {stats.promotional}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Seasonal
              </Typography>
              <Typography variant="h4" color="warning.main">
                {stats.seasonal}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Filters and Actions */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={2.5}>
              <TextField
                fullWidth
                label="Search"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search variants..."
              />
            </Grid>
            
            <Grid item xs={12} md={2}>
              <FormControl fullWidth>
                <InputLabel>Type</InputLabel>
                <Select
                  value={typeFilter}
                  onChange={(e) => setTypeFilter(e.target.value as VariantType | '')}
                  label="Type"
                >
                  <MenuItem value="">All</MenuItem>
                  {Object.values(VariantType).map((type) => (
                    <MenuItem key={type} value={type}>{getTypeLabel(type)}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={2}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value as VariantStatus | '')}
                  label="Status"
                >
                  <MenuItem value="">All</MenuItem>
                  {Object.values(VariantStatus).map((status) => (
                    <MenuItem key={status} value={status}>{status}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={1.5}>
              <FormControl fullWidth>
                <InputLabel>Active</InputLabel>
                <Select
                  value={activeFilter}
                  onChange={(e) => setActiveFilter(e.target.value)}
                  label="Active"
                >
                  <MenuItem value="">All</MenuItem>
                  <MenuItem value="active">Active Only</MenuItem>
                  <MenuItem value="inactive">Inactive Only</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={2}>
              <Button
                variant="outlined"
                startIcon={<RefreshIcon />}
                onClick={() => {
                  loadVariants();
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
                  New Variant
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

      {/* Variants Table */}
      <Card>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Variant Name</TableCell>
                <TableCell>Code</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Active</TableCell>
                <TableCell>Valid Period</TableCell>
                <TableCell>Applications</TableCell>
                <TableCell>Disbursements</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={9} align="center">
                    <CircularProgress />
                  </TableCell>
                </TableRow>
              ) : filteredVariants.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={9} align="center">
                    <Typography variant="body1" color="text.secondary" py={4}>
                      No variants found
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                filteredVariants.map((variant) => (
                  <TableRow key={variant.id} hover>
                    <TableCell>
                      <Typography variant="body2" fontWeight="medium">
                        {variant.variant_name}
                      </Typography>
                      {variant.marketing_name && (
                        <Typography variant="caption" color="text.secondary">
                          {variant.marketing_name}
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell>{variant.variant_code}</TableCell>
                    <TableCell>
                      <Chip
                        label={getTypeLabel(variant.variant_type)}
                        size="small"
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={variant.status}
                        color={getStatusColor(variant.status)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      {variant.is_active ? (
                        <ActiveIcon color="success" />
                      ) : (
                        <InactiveIcon color="disabled" />
                      )}
                    </TableCell>
                    <TableCell>
                      <Typography variant="caption" display="block">
                        From: {productLifecycleService.formatDate(variant.valid_from)}
                      </Typography>
                      {variant.valid_to && (
                        <Typography variant="caption" display="block">
                          To: {productLifecycleService.formatDate(variant.valid_to)}
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell>{variant.application_count}</TableCell>
                    <TableCell>{variant.disbursement_count}</TableCell>
                    <TableCell align="right">
                      <IconButton
                        size="small"
                        onClick={(e) => handleMenuOpen(e, variant)}
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
          count={totalCount}
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
        <MenuOption onClick={handleViewPerformance}>
          <PerformanceIcon fontSize="small" sx={{ mr: 1 }} />
          View Performance
        </MenuOption>
        {selectedVariant && !selectedVariant.is_active && (
          <MenuOption onClick={handleActivate}>
            <ActiveIcon fontSize="small" sx={{ mr: 1 }} />
            Activate
          </MenuOption>
        )}
        {selectedVariant && selectedVariant.is_active && (
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
            Are you sure you want to delete the variant "{selectedVariant?.variant_name}"?
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

export default VariantList;
