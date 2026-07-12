'use client';

/**
 * CRM Opportunities List Page
 * Sales pipeline overview with stage-wise tracking
 */

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  Box, Button, Card, CardContent, Typography, TextField, MenuItem,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Paper, Chip, IconButton, InputAdornment, Grid, Stack, Tooltip,
  Dialog, DialogTitle, DialogContent, DialogActions, Alert
} from '@mui/material';
import {
  Add as AddIcon,
  Search as SearchIcon,
  Visibility as ViewIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  FilterList as FilterIcon,
  TrendingUp as TrendingUpIcon,
  Assessment as AssessmentIcon
} from '@mui/icons-material';
import { opportunityService, type Opportunity, type OpportunityFilters } from '@/services/crm/opportunityService';

const STAGE_COLORS: Record<string, string> = {
  prospecting: 'default',
  qualification: 'info',
  needs_analysis: 'primary',
  proposal: 'secondary',
  negotiation: 'warning',
  closed_won: 'success',
  closed_lost: 'error'
};

const PRIORITY_COLORS: Record<string, 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning'> = {
  low: 'default',
  medium: 'info',
  high: 'warning',
  critical: 'error'
};

export default function OpportunitiesPage() {
  const router = useRouter();
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [totalCount, setTotalCount] = useState(0);
  const [filters, setFilters] = useState<OpportunityFilters>({
    skip: 0,
    limit: 50
  });
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedOpportunity, setSelectedOpportunity] = useState<string | null>(null);

  useEffect(() => {
    loadOpportunities();
  }, [filters]);

  const loadOpportunities = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await opportunityService.getOpportunities(filters);
      setOpportunities(response.items);
      setTotalCount(response.total);
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Failed to load opportunities');
      console.error('Error loading opportunities:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (value: string) => {
    setFilters(prev => ({ ...prev, search: value, skip: 0 }));
  };

  const handleFilterChange = (field: keyof OpportunityFilters, value: any) => {
    setFilters(prev => ({ ...prev, [field]: value, skip: 0 }));
  };

  const handleDeleteClick = (opportunityId: string) => {
    setSelectedOpportunity(opportunityId);
    setDeleteDialogOpen(true);
  };

  const handleDelete = async () => {
    if (!selectedOpportunity) return;

    try {
      await opportunityService.deleteOpportunity(selectedOpportunity);
      setDeleteDialogOpen(false);
      setSelectedOpportunity(null);
      loadOpportunities();
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Failed to delete opportunity');
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(value);
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" gutterBottom>
            Opportunities
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Manage sales pipeline and track opportunities
          </Typography>
        </Box>
        <Stack direction="row" spacing={2}>
          <Button
            variant="outlined"
            startIcon={<AssessmentIcon />}
            onClick={() => router.push('/crm/opportunities/analytics')}
          >
            Analytics
          </Button>
          <Button
            variant="outlined"
            startIcon={<TrendingUpIcon />}
            onClick={() => router.push('/crm/opportunities/pipeline')}
          >
            Pipeline View
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => router.push('/crm/opportunities/new')}
          >
            New Opportunity
          </Button>
        </Stack>
      </Stack>

      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2}>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                placeholder="Search opportunities..."
                value={filters.search || ''}
                onChange={(e) => handleSearch(e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon />
                    </InputAdornment>
                  ),
                }}
              />
            </Grid>
            <Grid item xs={12} md={2}>
              <TextField
                fullWidth
                select
                label="Stage"
                value={filters.stage || ''}
                onChange={(e) => handleFilterChange('stage', e.target.value)}
              >
                <MenuItem value="">All Stages</MenuItem>
                <MenuItem value="prospecting">Prospecting</MenuItem>
                <MenuItem value="qualification">Qualification</MenuItem>
                <MenuItem value="needs_analysis">Needs Analysis</MenuItem>
                <MenuItem value="proposal">Proposal</MenuItem>
                <MenuItem value="negotiation">Negotiation</MenuItem>
                <MenuItem value="closed_won">Closed Won</MenuItem>
                <MenuItem value="closed_lost">Closed Lost</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={12} md={2}>
              <TextField
                fullWidth
                select
                label="Priority"
                value={filters.priority || ''}
                onChange={(e) => handleFilterChange('priority', e.target.value)}
              >
                <MenuItem value="">All Priorities</MenuItem>
                <MenuItem value="low">Low</MenuItem>
                <MenuItem value="medium">Medium</MenuItem>
                <MenuItem value="high">High</MenuItem>
                <MenuItem value="critical">Critical</MenuItem>
              </TextField>
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

      {/* Opportunities Table */}
      <Card>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Opportunity</TableCell>
                <TableCell>Account</TableCell>
                <TableCell>Stage</TableCell>
                <TableCell>Priority</TableCell>
                <TableCell align="right">Value</TableCell>
                <TableCell align="right">Probability</TableCell>
                <TableCell align="right">Weighted Value</TableCell>
                <TableCell>Expected Close</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={9} align="center">
                    Loading...
                  </TableCell>
                </TableRow>
              ) : opportunities.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={9} align="center">
                    <Typography color="text.secondary">
                      No opportunities found
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                opportunities.map((opp) => (
                  <TableRow key={opp.id} hover>
                    <TableCell>
                      <Typography variant="body2" fontWeight={500}>
                        {opp.opportunity_name}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {opp.opportunity_number}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {opp.account_name || '-'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={opp.stage.replace('_', ' ').toUpperCase()}
                        color={STAGE_COLORS[opp.stage] as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={opp.priority.toUpperCase()}
                        color={PRIORITY_COLORS[opp.priority]}
                        size="small"
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell align="right">
                      {formatCurrency(opp.estimated_value)}
                    </TableCell>
                    <TableCell align="right">
                      {opp.probability}%
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="body2" fontWeight={500}>
                        {formatCurrency(opp.weighted_value)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      {formatDate(opp.expected_close_date)}
                    </TableCell>
                    <TableCell align="right">
                      <Stack direction="row" spacing={1} justifyContent="flex-end">
                        <Tooltip title="View">
                          <IconButton
                            size="small"
                            onClick={() => router.push(`/crm/opportunities/${opp.id}`)}
                          >
                            <ViewIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Edit">
                          <IconButton
                            size="small"
                            onClick={() => router.push(`/crm/opportunities/${opp.id}/edit`)}
                          >
                            <EditIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Delete">
                          <IconButton
                            size="small"
                            color="error"
                            onClick={() => handleDeleteClick(opp.id)}
                          >
                            <DeleteIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </Stack>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Card>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
          Are you sure you want to delete this opportunity? This action cannot be undone.
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleDelete} color="error" variant="contained">
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
