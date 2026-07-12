'use client';

/**
 * CRM Opportunities Analytics Page
 * Win/Loss analysis and performance metrics
 */

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  Box, Card, CardContent, Typography, Grid, Stack, Button,
  CircularProgress, Alert, Table, TableBody, TableCell,
  TableContainer, TableHead, TableRow, Chip, Paper
} from '@mui/material';
import { ArrowBack as BackIcon, TrendingUp, TrendingDown } from '@mui/icons-material';
import { opportunityService, type WinLossAnalysis } from '@/services/crm/opportunityService';

export default function AnalyticsPage() {
  const router = useRouter();
  const [analysis, setAnalysis] = useState<WinLossAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await opportunityService.getWinLossAnalysis();
      setAnalysis(data);
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Failed to load analytics');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(value);
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Stack direction="row" alignItems="center" spacing={2} mb={3}>
        <Button startIcon={<BackIcon />} onClick={() => router.back()}>
          Back
        </Button>
        <Box>
          <Typography variant="h4">Win/Loss Analysis</Typography>
          <Typography variant="body2" color="text.secondary">
            Performance metrics and closed opportunity analysis
          </Typography>
        </Box>
      </Stack>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>
      )}

      {analysis && (
        <>
          {/* Summary Cards */}
          <Grid container spacing={3} mb={3}>
            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
                    <Box>
                      <Typography color="text.secondary" gutterBottom>
                        Win Rate
                      </Typography>
                      <Typography variant="h3" color="success.main">
                        {analysis.win_rate.toFixed(1)}%
                      </Typography>
                      <Typography variant="body2" color="text.secondary" mt={1}>
                        {analysis.won_count} won / {analysis.total_closed} closed
                      </Typography>
                    </Box>
                    <TrendingUp sx={{ color: 'success.main', fontSize: 40 }} />
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" gutterBottom>
                    Total Won Value
                  </Typography>
                  <Typography variant="h5" color="success.main">
                    {formatCurrency(analysis.total_won_value)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" mt={1}>
                    Avg: {formatCurrency(analysis.avg_won_deal_size)}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
                    <Box>
                      <Typography color="text.secondary" gutterBottom>
                        Total Lost Value
                      </Typography>
                      <Typography variant="h5" color="error.main">
                        {formatCurrency(analysis.total_lost_value)}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" mt={1}>
                        Avg: {formatCurrency(analysis.avg_lost_deal_size)}
                      </Typography>
                    </Box>
                    <TrendingDown sx={{ color: 'error.main', fontSize: 40 }} />
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          <Grid container spacing={3}>
            {/* Loss Reasons */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Loss Reasons
                  </Typography>
                  <TableContainer>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Reason</TableCell>
                          <TableCell align="right">Count</TableCell>
                          <TableCell align="right">%</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {Object.entries(analysis.loss_reasons).map(([reason, count]) => (
                          <TableRow key={reason}>
                            <TableCell>
                              {reason.replace('_', ' ').toUpperCase()}
                            </TableCell>
                            <TableCell align="right">{count}</TableCell>
                            <TableCell align="right">
                              {((count / analysis.lost_count) * 100).toFixed(1)}%
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </CardContent>
              </Card>
            </Grid>

            {/* Top Competitors */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Top Competitors
                  </Typography>
                  <TableContainer>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Competitor</TableCell>
                          <TableCell align="right">Losses</TableCell>
                          <TableCell align="right">Value</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {analysis.top_competitors.map((competitor) => (
                          <TableRow key={competitor.name}>
                            <TableCell>{competitor.name}</TableCell>
                            <TableCell align="right">{competitor.count}</TableCell>
                            <TableCell align="right">
                              {formatCurrency(competitor.total_value)}
                            </TableCell>
                          </TableRow>
                        ))}
                        {analysis.top_competitors.length === 0 && (
                          <TableRow>
                            <TableCell colSpan={3} align="center">
                              <Typography color="text.secondary">
                                No competitor data available
                              </Typography>
                            </TableCell>
                          </TableRow>
                        )}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </>
      )}
    </Box>
  );
}
