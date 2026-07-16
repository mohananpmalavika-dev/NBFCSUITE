/**
 * Decision List Component
 * Displays list of all decision requests with filters
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Chip,
  Button,
  TextField,
  Grid,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  CircularProgress,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Visibility as ViewIcon,
  Refresh as RefreshIcon,
  Search as SearchIcon
} from '@mui/icons-material';
import { useRouter } from 'next/navigation';
import {
  decisionEngineService,
  DecisionRequest,
  DecisionStatus,
  DecisionOutcome,
  formatDecisionOutcome,
  getDecisionOutcomeColor,
  formatDecisionStatus,
  getDecisionStatusColor,
  formatDuration,
  getScoreColor
} from '@/services/decisionEngine.service';

export default function DecisionList() {
  const router = useRouter();
  const [decisions, setDecisions] = useState<DecisionRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(25);
  const [totalCount, setTotalCount] = useState(0);

  // Filters
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [outcomeFilter, setOutcomeFilter] = useState<string>('');
  const [searchCustomer, setSearchCustomer] = useState('');

  useEffect(() => {
    loadDecisions();
  }, [page, rowsPerPage, statusFilter, outcomeFilter]);

  const loadDecisions = async () => {
    try {
      setLoading(true);
      const params: any = {
        skip: page * rowsPerPage,
        limit: rowsPerPage
      };

      if (statusFilter) params.status = statusFilter;
      if (outcomeFilter) params.outcome = outcomeFilter;
      if (searchCustomer) params.customer_id = searchCustomer;

      const response = await decisionEngineService.listDecisions(params);
      setDecisions(response.data);
      setTotalCount(response.pagination?.total || response.data.length);
    } catch (error) {
      console.error('Failed to load decisions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleViewDetails = (decisionId: string) => {
    router.push(`/decision-engine/${decisionId}`);
  };

  const handleRefresh = () => {
    loadDecisions();
  };

  const handleSearch = () => {
    setPage(0);
    loadDecisions();
  };

  const handleNewDecision = () => {
    router.push('/decision-engine/new');
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Decision Engine
        </Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={handleRefresh}
            sx={{ mr: 2 }}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            color="primary"
            onClick={handleNewDecision}
          >
            New Decision Request
          </Button>
        </Box>
      </Box>

      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Status</InputLabel>
                <Select
                  value={statusFilter}
                  label="Status"
                  onChange={(e) => setStatusFilter(e.target.value)}
                >
                  <MenuItem value="">All</MenuItem>
                  <MenuItem value={DecisionStatus.PENDING}>Pending</MenuItem>
                  <MenuItem value={DecisionStatus.IN_PROGRESS}>In Progress</MenuItem>
                  <MenuItem value={DecisionStatus.COMPLETED}>Completed</MenuItem>
                  <MenuItem value={DecisionStatus.FAILED}>Failed</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Outcome</InputLabel>
                <Select
                  value={outcomeFilter}
                  label="Outcome"
                  onChange={(e) => setOutcomeFilter(e.target.value)}
                >
                  <MenuItem value="">All</MenuItem>
                  <MenuItem value={DecisionOutcome.APPROVED}>Approved</MenuItem>
                  <MenuItem value={DecisionOutcome.APPROVED_WITH_CONDITIONS}>
                    Approved with Conditions
                  </MenuItem>
                  <MenuItem value={DecisionOutcome.DECLINED}>Declined</MenuItem>
                  <MenuItem value={DecisionOutcome.MANUAL_REVIEW}>Manual Review</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} sm={6} md={4}>
              <TextField
                fullWidth
                size="small"
                label="Search Customer ID"
                value={searchCustomer}
                onChange={(e) => setSearchCustomer(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              />
            </Grid>

            <Grid item xs={12} sm={6} md={2}>
              <Button
                fullWidth
                variant="contained"
                startIcon={<SearchIcon />}
                onClick={handleSearch}
              >
                Search
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Decisions Table */}
      <Card>
        <CardContent>
          {loading ? (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight={400}>
              <CircularProgress />
            </Box>
          ) : decisions.length === 0 ? (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight={400}>
              <Typography variant="body1" color="textSecondary">
                No decisions found
              </Typography>
            </Box>
          ) : (
            <>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Application ID</TableCell>
                      <TableCell>Customer ID</TableCell>
                      <TableCell align="right">Loan Amount</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Outcome</TableCell>
                      <TableCell align="center">Score</TableCell>
                      <TableCell align="center">Confidence</TableCell>
                      <TableCell align="center">Duration</TableCell>
                      <TableCell>Request Time</TableCell>
                      <TableCell align="center">Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {decisions.map((decision) => (
                      <TableRow key={decision.id} hover>
                        <TableCell>
                          <Typography variant="body2" fontFamily="monospace">
                            {decision.application_id.substring(0, 8)}...
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" fontFamily="monospace">
                            {decision.customer_id.substring(0, 8)}...
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="body2">
                            ₹{decision.loan_amount.toLocaleString('en-IN')}
                          </Typography>
                          {decision.approved_amount && decision.approved_amount !== decision.loan_amount && (
                            <Typography variant="caption" color="success.main">
                              ₹{decision.approved_amount.toLocaleString('en-IN')} approved
                            </Typography>
                          )}
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={formatDecisionStatus(decision.status)}
                            color={getDecisionStatusColor(decision.status) as any}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          {decision.decision_outcome ? (
                            <Chip
                              label={formatDecisionOutcome(decision.decision_outcome)}
                              color={getDecisionOutcomeColor(decision.decision_outcome) as any}
                              size="small"
                            />
                          ) : (
                            <Typography variant="caption" color="textSecondary">
                              Pending
                            </Typography>
                          )}
                        </TableCell>
                        <TableCell align="center">
                          {decision.decision_score !== undefined ? (
                            <Chip
                              label={decision.decision_score.toFixed(1)}
                              color={getScoreColor(decision.decision_score) as any}
                              size="small"
                            />
                          ) : (
                            '-'
                          )}
                        </TableCell>
                        <TableCell align="center">
                          {decision.confidence_score !== undefined ? (
                            <Typography variant="body2">
                              {decision.confidence_score.toFixed(1)}%
                            </Typography>
                          ) : (
                            '-'
                          )}
                        </TableCell>
                        <TableCell align="center">
                          <Typography variant="body2">
                            {formatDuration(decision.total_duration_ms)}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {new Date(decision.request_time).toLocaleString('en-IN')}
                          </Typography>
                        </TableCell>
                        <TableCell align="center">
                          <Tooltip title="View Details">
                            <IconButton
                              size="small"
                              color="primary"
                              onClick={() => handleViewDetails(decision.id)}
                            >
                              <ViewIcon />
                            </IconButton>
                          </Tooltip>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>

              <TablePagination
                rowsPerPageOptions={[10, 25, 50, 100]}
                component="div"
                count={totalCount}
                rowsPerPage={rowsPerPage}
                page={page}
                onPageChange={handleChangePage}
                onRowsPerPageChange={handleChangeRowsPerPage}
              />
            </>
          )}
        </CardContent>
      </Card>
    </Box>
  );
}
