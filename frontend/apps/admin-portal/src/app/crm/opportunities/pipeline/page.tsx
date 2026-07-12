'use client';

/**
 * CRM Opportunities Pipeline View
 * Visual sales pipeline with drag-and-drop stage management
 */

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  Box, Card, CardContent, Typography, Grid, Stack, Chip, Button,
  CircularProgress, Alert
} from '@mui/material';
import { ArrowBack as BackIcon } from '@mui/icons-material';
import { opportunityService, type PipelineOverview } from '@/services/crm/opportunityService';

export default function PipelinePage() {
  const router = useRouter();
  const [pipeline, setPipeline] = useState<PipelineOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadPipeline();
  }, []);

  const loadPipeline = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await opportunityService.getPipelineOverview();
      setPipeline(data);
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Failed to load pipeline');
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
          <Typography variant="h4">Sales Pipeline</Typography>
          <Typography variant="body2" color="text.secondary">
            Visual overview of opportunities by stage
          </Typography>
        </Box>
      </Stack>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>
      )}

      {pipeline && (
        <>
          {/* Summary Cards */}
          <Grid container spacing={3} mb={3}>
            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" gutterBottom>
                    Total Opportunities
                  </Typography>
                  <Typography variant="h4">
                    {pipeline.total_opportunities}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" gutterBottom>
                    Total Pipeline Value
                  </Typography>
                  <Typography variant="h5">
                    {formatCurrency(pipeline.total_value)}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" gutterBottom>
                    Weighted Value
                  </Typography>
                  <Typography variant="h5" color="primary">
                    {formatCurrency(pipeline.weighted_pipeline_value)}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" gutterBottom>
                    Average Deal Size
                  </Typography>
                  <Typography variant="h5">
                    {formatCurrency(pipeline.avg_deal_size)}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Pipeline Stages */}
          <Grid container spacing={2}>
            {pipeline.stages.map((stage) => (
              <Grid item xs={12} md={4} lg={2} key={stage.stage}>
                <Card sx={{ height: '100%', bgcolor: 'background.default' }}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      {stage.stage_name}
                    </Typography>
                    <Chip
                      label={`${stage.count} deals`}
                      size="small"
                      color="primary"
                      sx={{ mb: 2 }}
                    />
                    <Stack spacing={1}>
                      <Box>
                        <Typography variant="caption" color="text.secondary">
                          Total Value
                        </Typography>
                        <Typography variant="body2" fontWeight={500}>
                          {formatCurrency(stage.total_value)}
                        </Typography>
                      </Box>
                      <Box>
                        <Typography variant="caption" color="text.secondary">
                          Weighted Value
                        </Typography>
                        <Typography variant="body2" fontWeight={500} color="primary">
                          {formatCurrency(stage.weighted_value)}
                        </Typography>
                      </Box>
                      <Box>
                        <Typography variant="caption" color="text.secondary">
                          Avg. Probability
                        </Typography>
                        <Typography variant="body2">
                          {stage.avg_probability.toFixed(1)}%
                        </Typography>
                      </Box>
                    </Stack>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </>
      )}
    </Box>
  );
}
