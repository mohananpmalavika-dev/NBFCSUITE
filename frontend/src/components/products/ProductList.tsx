import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  CardActions,
  Typography,
  Button,
  IconButton,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  InputAdornment,
  Divider,
  Menu,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  FileCopy as CloneIcon,
  Visibility as ViewIcon,
  Search as SearchIcon,
  FilterList as FilterIcon,
  MoreVert as MoreVertIcon,
  PlayArrow as ActivateIcon,
  Stop as DeactivateIcon,
  Calculate as CalculateIcon,
  Refresh as RefreshIcon,
  Star as StarIcon,
  StarBorder as StarBorderIcon,
} from '@mui/icons-material';
import { productsService } from '../../services/productsService';
import ProductBuilder from './ProductBuilder';

interface Product {
  id: string;
  product_code: string;
  product_name: string;
  category: string;
  description: string;
  status: string;
  effective_date: string;
  expiry_date?: string;
  interest_config: any;
  tenure_config: any;
  amount_config: any;
  is_featured: boolean;
}

interface ProductStats {
  total_products: number;
  active_products: number;
  draft_products: number;
  featured_products: number;
  total_categories: number;
}

interface CalculationDialog {
  open: boolean;
  productId: string;
  amount: number;
  tenure: number;
  result?: any;
}

const ProductList: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [filteredProducts, setFilteredProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  // Filters
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('ALL');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [minAmount, setMinAmount] = useState<number | ''>('');
  const [maxAmount, setMaxAmount] = useState<number | ''>('');
  const [featuredOnly, setFeaturedOnly] = useState(false);
  
  // Stats
  const [stats, setStats] = useState<ProductStats>({
    total_products: 0,
    active_products: 0,
    draft_products: 0,
    featured_products: 0,
    total_categories: 0,
  });
  
  // Dialogs
  const [builderOpen, setBuilderOpen] = useState(false);
  const [selectedProductId, setSelectedProductId] = useState<string | undefined>();
  const [deleteDialog, setDeleteDialog] = useState<{ open: boolean; productId: string | null }>({
    open: false,
    productId: null,
  });
  const [calculationDialog, setCalculationDialog] = useState<CalculationDialog>({
    open: false,
    productId: '',
    amount: 0,
    tenure: 12,
  });
  
  // Menu
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);

  useEffect(() => {
    loadProducts();
    loadStats();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [products, searchTerm, categoryFilter, statusFilter, minAmount, maxAmount, featuredOnly]);

  const loadProducts = async () => {
    try {
      setLoading(true);
      const data = await productsService.listProducts({
        category: categoryFilter !== 'ALL' ? categoryFilter : undefined,
        status: statusFilter !== 'ALL' ? statusFilter : undefined,
        is_featured: featuredOnly || undefined,
        min_amount: minAmount || undefined,
        max_amount: maxAmount || undefined,
      });
      setProducts(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load products');
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const data = await productsService.getStats();
      setStats(data);
    } catch (err: any) {
      console.error('Failed to load stats:', err);
    }
  };

  const applyFilters = () => {
    let filtered = [...products];
    
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(
        (p) =>
          p.product_code.toLowerCase().includes(term) ||
          p.product_name.toLowerCase().includes(term) ||
          p.description.toLowerCase().includes(term)
      );
    }
    
    if (categoryFilter !== 'ALL') {
      filtered = filtered.filter((p) => p.category === categoryFilter);
    }
    
    if (statusFilter !== 'ALL') {
      filtered = filtered.filter((p) => p.status === statusFilter);
    }
    
    if (minAmount) {
      filtered = filtered.filter((p) => p.amount_config.min_amount >= minAmount);
    }
    
    if (maxAmount) {
      filtered = filtered.filter((p) => p.amount_config.max_amount <= maxAmount);
    }
    
    if (featuredOnly) {
      filtered = filtered.filter((p) => p.is_featured);
    }
    
    setFilteredProducts(filtered);
  };

  const handleCreateProduct = () => {
    setSelectedProductId(undefined);
    setBuilderOpen(true);
  };

  const handleEditProduct = (productId: string) => {
    setSelectedProductId(productId);
    setBuilderOpen(true);
    handleMenuClose();
  };

  const handleCloneProduct = async (productId: string) => {
    try {
      setLoading(true);
      const newCode = prompt('Enter new product code:');
      if (!newCode) return;
      
      await productsService.cloneProduct(productId, { new_product_code: newCode });
      setSuccess('Product cloned successfully');
      loadProducts();
    } catch (err: any) {
      setError(err.message || 'Failed to clone product');
    } finally {
      setLoading(false);
      handleMenuClose();
    }
  };

  const handleDeleteProduct = async () => {
    if (!deleteDialog.productId) return;
    
    try {
      setLoading(true);
      await productsService.deleteProduct(deleteDialog.productId);
      setSuccess('Product deleted successfully');
      loadProducts();
      loadStats();
    } catch (err: any) {
      setError(err.message || 'Failed to delete product');
    } finally {
      setLoading(false);
      setDeleteDialog({ open: false, productId: null });
    }
  };

  const handleActivateProduct = async (productId: string) => {
    try {
      setLoading(true);
      await productsService.activateProduct(productId);
      setSuccess('Product activated successfully');
      loadProducts();
      loadStats();
    } catch (err: any) {
      setError(err.message || 'Failed to activate product');
    } finally {
      setLoading(false);
      handleMenuClose();
    }
  };

  const handleDeactivateProduct = async (productId: string) => {
    try {
      setLoading(true);
      await productsService.deactivateProduct(productId);
      setSuccess('Product deactivated successfully');
      loadProducts();
      loadStats();
    } catch (err: any) {
      setError(err.message || 'Failed to deactivate product');
    } finally {
      setLoading(false);
      handleMenuClose();
    }
  };

  const handleCalculateEMI = async () => {
    try {
      setLoading(true);
      const result = await productsService.calculateEMI(calculationDialog.productId, {
        loan_amount: calculationDialog.amount,
        tenure_months: calculationDialog.tenure,
      });
      setCalculationDialog((prev) => ({ ...prev, result }));
    } catch (err: any) {
      setError(err.message || 'Failed to calculate EMI');
    } finally {
      setLoading(false);
    }
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, product: Product) => {
    setAnchorEl(event.currentTarget);
    setSelectedProduct(product);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedProduct(null);
  };

  const handleProductSaved = () => {
    setBuilderOpen(false);
    loadProducts();
    loadStats();
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ACTIVE':
        return 'success';
      case 'INACTIVE':
        return 'error';
      case 'DRAFT':
        return 'warning';
      case 'COMING_SOON':
        return 'info';
      default:
        return 'default';
    }
  };

  const categories = [
    'ALL',
    'PERSONAL_LOAN',
    'HOME_LOAN',
    'BUSINESS_LOAN',
    'GOLD_LOAN',
    'VEHICLE_LOAN',
    'EDUCATION_LOAN',
    'LAP',
    'MSME_LOAN',
    'AGRICULTURE_LOAN',
  ];

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Product Configuration</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleCreateProduct}
        >
          Create Product
        </Button>
      </Box>

      {/* Alerts */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}
      
      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}

      {/* Stats Cards */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom variant="body2">
                Total Products
              </Typography>
              <Typography variant="h4">{stats.total_products}</Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom variant="body2">
                Active Products
              </Typography>
              <Typography variant="h4" color="success.main">{stats.active_products}</Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom variant="body2">
                Draft Products
              </Typography>
              <Typography variant="h4" color="warning.main">{stats.draft_products}</Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom variant="body2">
                Featured
              </Typography>
              <Typography variant="h4" color="primary.main">{stats.featured_products}</Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom variant="body2">
                Categories
              </Typography>
              <Typography variant="h4">{stats.total_categories}</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={3}>
            <TextField
              fullWidth
              size="small"
              placeholder="Search products..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
            />
          </Grid>
          
          <Grid item xs={12} sm={6} md={2}>
            <FormControl fullWidth size="small">
              <InputLabel>Category</InputLabel>
              <Select
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value)}
                label="Category"
              >
                {categories.map((cat) => (
                  <MenuItem key={cat} value={cat}>
                    {cat.replace(/_/g, ' ')}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} sm={6} md={2}>
            <FormControl fullWidth size="small">
              <InputLabel>Status</InputLabel>
              <Select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                label="Status"
              >
                <MenuItem value="ALL">All</MenuItem>
                <MenuItem value="ACTIVE">Active</MenuItem>
                <MenuItem value="INACTIVE">Inactive</MenuItem>
                <MenuItem value="DRAFT">Draft</MenuItem>
                <MenuItem value="COMING_SOON">Coming Soon</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} sm={6} md={2}>
            <TextField
              fullWidth
              size="small"
              type="number"
              label="Min Amount"
              value={minAmount}
              onChange={(e) => setMinAmount(e.target.value ? parseFloat(e.target.value) : '')}
              InputProps={{ startAdornment: <InputAdornment position="start">₹</InputAdornment> }}
            />
          </Grid>
          
          <Grid item xs={12} sm={6} md={2}>
            <TextField
              fullWidth
              size="small"
              type="number"
              label="Max Amount"
              value={maxAmount}
              onChange={(e) => setMaxAmount(e.target.value ? parseFloat(e.target.value) : '')}
              InputProps={{ startAdornment: <InputAdornment position="start">₹</InputAdornment> }}
            />
          </Grid>
          
          <Grid item xs={12} sm={6} md={1}>
            <Button
              fullWidth
              variant="outlined"
              startIcon={<RefreshIcon />}
              onClick={loadProducts}
            >
              Refresh
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {/* Product Grid */}
      {loading && filteredProducts.length === 0 ? (
        <Typography>Loading products...</Typography>
      ) : filteredProducts.length === 0 ? (
        <Alert severity="info">No products found. Create your first product to get started.</Alert>
      ) : (
        <Grid container spacing={3}>
          {filteredProducts.map((product) => (
            <Grid item xs={12} sm={6} md={4} key={product.id}>
              <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <CardContent sx={{ flexGrow: 1 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                    <Box>
                      <Typography variant="h6" component="div">
                        {product.product_name}
                        {product.is_featured && (
                          <StarIcon sx={{ ml: 1, color: 'gold', fontSize: 20, verticalAlign: 'middle' }} />
                        )}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {product.product_code}
                      </Typography>
                    </Box>
                    <IconButton
                      size="small"
                      onClick={(e) => handleMenuOpen(e, product)}
                    >
                      <MoreVertIcon />
                    </IconButton>
                  </Box>
                  
                  <Box sx={{ mb: 1 }}>
                    <Chip
                      label={product.category.replace(/_/g, ' ')}
                      size="small"
                      sx={{ mr: 1, mb: 1 }}
                    />
                    <Chip
                      label={product.status}
                      size="small"
                      color={getStatusColor(product.status) as any}
                    />
                  </Box>
                  
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    {product.description}
                  </Typography>
                  
                  <Divider sx={{ my: 1 }} />
                  
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      <strong>Interest Rate:</strong> {product.interest_config.base_rate}%
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      <strong>Tenure:</strong> {product.tenure_config.min_tenure}-{product.tenure_config.max_tenure} months
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      <strong>Amount:</strong> ₹{product.amount_config.min_amount.toLocaleString()} - ₹{product.amount_config.max_amount.toLocaleString()}
                    </Typography>
                  </Box>
                </CardContent>
                
                <CardActions>
                  <Button
                    size="small"
                    startIcon={<EditIcon />}
                    onClick={() => handleEditProduct(product.id)}
                  >
                    Edit
                  </Button>
                  <Button
                    size="small"
                    startIcon={<CalculateIcon />}
                    onClick={() =>
                      setCalculationDialog({
                        open: true,
                        productId: product.id,
                        amount: product.amount_config.min_amount,
                        tenure: product.tenure_config.min_tenure,
                      })
                    }
                  >
                    Calculate
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Action Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={() => selectedProduct && handleEditProduct(selectedProduct.id)}>
          <ListItemIcon>
            <EditIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Edit</ListItemText>
        </MenuItem>
        
        <MenuItem onClick={() => selectedProduct && handleCloneProduct(selectedProduct.id)}>
          <ListItemIcon>
            <CloneIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Clone</ListItemText>
        </MenuItem>
        
        {selectedProduct?.status !== 'ACTIVE' && (
          <MenuItem onClick={() => selectedProduct && handleActivateProduct(selectedProduct.id)}>
            <ListItemIcon>
              <ActivateIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText>Activate</ListItemText>
          </MenuItem>
        )}
        
        {selectedProduct?.status === 'ACTIVE' && (
          <MenuItem onClick={() => selectedProduct && handleDeactivateProduct(selectedProduct.id)}>
            <ListItemIcon>
              <DeactivateIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText>Deactivate</ListItemText>
          </MenuItem>
        )}
        
        <Divider />
        
        <MenuItem
          onClick={() => {
            if (selectedProduct) {
              setDeleteDialog({ open: true, productId: selectedProduct.id });
              handleMenuClose();
            }
          }}
          sx={{ color: 'error.main' }}
        >
          <ListItemIcon>
            <DeleteIcon fontSize="small" color="error" />
          </ListItemIcon>
          <ListItemText>Delete</ListItemText>
        </MenuItem>
      </Menu>

      {/* Product Builder Dialog */}
      <Dialog
        open={builderOpen}
        onClose={() => setBuilderOpen(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogContent>
          <ProductBuilder
            productId={selectedProductId}
            onSave={handleProductSaved}
            onCancel={() => setBuilderOpen(false)}
          />
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialog.open}
        onClose={() => setDeleteDialog({ open: false, productId: null })}
      >
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
          <Typography>Are you sure you want to delete this product? This action cannot be undone.</Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialog({ open: false, productId: null })}>
            Cancel
          </Button>
          <Button onClick={handleDeleteProduct} color="error" variant="contained">
            Delete
          </Button>
        </DialogActions>
      </Dialog>

      {/* EMI Calculator Dialog */}
      <Dialog
        open={calculationDialog.open}
        onClose={() => setCalculationDialog({ open: false, productId: '', amount: 0, tenure: 12 })}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>EMI Calculator</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                type="number"
                label="Loan Amount"
                value={calculationDialog.amount}
                onChange={(e) =>
                  setCalculationDialog((prev) => ({ ...prev, amount: parseFloat(e.target.value) }))
                }
                InputProps={{ startAdornment: <InputAdornment position="start">₹</InputAdornment> }}
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                type="number"
                label="Tenure (months)"
                value={calculationDialog.tenure}
                onChange={(e) =>
                  setCalculationDialog((prev) => ({ ...prev, tenure: parseInt(e.target.value) }))
                }
              />
            </Grid>
            
            {calculationDialog.result && (
              <>
                <Grid item xs={12}>
                  <Divider sx={{ my: 2 }} />
                  <Typography variant="h6" gutterBottom>Calculation Results</Typography>
                </Grid>
                
                <Grid item xs={12} md={4}>
                  <Paper sx={{ p: 2, bgcolor: 'primary.light' }}>
                    <Typography variant="body2" color="text.secondary">Monthly EMI</Typography>
                    <Typography variant="h5">₹{calculationDialog.result.emi?.toLocaleString()}</Typography>
                  </Paper>
                </Grid>
                
                <Grid item xs={12} md={4}>
                  <Paper sx={{ p: 2, bgcolor: 'info.light' }}>
                    <Typography variant="body2" color="text.secondary">Total Interest</Typography>
                    <Typography variant="h5">₹{calculationDialog.result.total_interest?.toLocaleString()}</Typography>
                  </Paper>
                </Grid>
                
                <Grid item xs={12} md={4}>
                  <Paper sx={{ p: 2, bgcolor: 'success.light' }}>
                    <Typography variant="body2" color="text.secondary">Total Amount</Typography>
                    <Typography variant="h5">₹{calculationDialog.result.total_payment?.toLocaleString()}</Typography>
                  </Paper>
                </Grid>
                
                {calculationDialog.result.amortization_schedule && (
                  <Grid item xs={12}>
                    <Typography variant="subtitle1" gutterBottom sx={{ mt: 2 }}>Amortization Schedule</Typography>
                    <TableContainer component={Paper} sx={{ maxHeight: 300 }}>
                      <Table size="small" stickyHeader>
                        <TableHead>
                          <TableRow>
                            <TableCell>Month</TableCell>
                            <TableCell align="right">EMI</TableCell>
                            <TableCell align="right">Principal</TableCell>
                            <TableCell align="right">Interest</TableCell>
                            <TableCell align="right">Balance</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {calculationDialog.result.amortization_schedule.map((row: any, index: number) => (
                            <TableRow key={index}>
                              <TableCell>{row.month}</TableCell>
                              <TableCell align="right">₹{row.emi?.toLocaleString()}</TableCell>
                              <TableCell align="right">₹{row.principal?.toLocaleString()}</TableCell>
                              <TableCell align="right">₹{row.interest?.toLocaleString()}</TableCell>
                              <TableCell align="right">₹{row.balance?.toLocaleString()}</TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </Grid>
                )}
              </>
            )}
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCalculationDialog({ open: false, productId: '', amount: 0, tenure: 12 })}>
            Close
          </Button>
          <Button onClick={handleCalculateEMI} variant="contained" disabled={loading}>
            {loading ? 'Calculating...' : 'Calculate'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ProductList;
