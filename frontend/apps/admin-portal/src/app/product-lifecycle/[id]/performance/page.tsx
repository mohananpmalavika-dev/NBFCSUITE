'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import {
  Container,
  Typography,
  Breadcrumbs,
  Link,
  Box,
  Card,
  CardContent,
  Grid,
  CircularProgress,
  Alert,
  Chip
} from '@mui/material';
import { Home as HomeIcon } from '@mui/icons-material';
import productLifecycleService, { 
  VariantPerformance 
} from '@/services/productLifecycle.service';

/**
 * Product Variant Performance Page
 */
export default function VariantPerformancePage() {
  const router = useRouter();
  const params = useParams();
  const variantId = params.id as string;

  const [performance, setPerformance] = useState<VariantPerformance | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadPerformance();
  }, [variantId]);

  const loadPerformance = async () => {
    try {
      const data = await productLifecycleService.getVariantPerformance(variantId);
      setPerformance(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load performance data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4, textAlign: 'center' }}>
        <CircularProgress />
      </Container>
    );
  }

  if (error || !performance) {
    return (
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error">{error || 'Performance data not found'}</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Breadcrumbs */}
      <Breadcrumbs sx={{ mb: 2 }}>
        <Link
          underline="hover"
          sx={{ display: 'flex', alignItems: 'center' }}
          color="inherit"
          href="/dashboard"
        >
          <HomeIcon sx={{ mr: 0.5 }} fontSize="inherit" />
          Dashboard
        </Link>
        <Link
          underline="hover"
          color="inherit"
          href="/product-lifecycle"
        >
          Product Lifecycle
        </Link>
        <Typography color="text.primary">Performance</Typography>
      </Breadcrumbs>

      {/* Page Header */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <Typography variant="h4" component="h1" gutterBottom>
              Variant Performance
            </Typography>
            <Typography variant="body1" color="text.secondary">
              {performance.variant_name} ({performance.variant_code})
            </Typography>
          </div>
          <Box>
            <Chip 
              label={performance.status} 
              color={performance.is_active ? 'success' : 'default'} 
            />
          </Box>
        </Box>
      </Box>

      {/* Performance Metrics */}
      <Grid container spacing={3}>
        {/* Validity Period */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Validity Period
              </Typography>
              <Typography variant="body1">
                From: {productLifecycleService.formatDate(performance.validity.valid_from)}
              </Typography>
              {performance.validity.valid_to && (
                <Typography variant="body1">
                  To: {productLifecycleService.formatDate(performance.validity.valid_to)}
                </Typography>
              )}
              <Typography variant="caption" color="text.secondary">
                Days Active: {performance.validity.days_active}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Applications */}
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Applications
              </Typography>
              <Typography variant="h4">
                {performance.usage.application_count}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Disbursements */}
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Disbursements
              </Typography>
              <Typography variant="h4" color="success.main">
                {performance.usage.disbursement_count}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Conversion Rate */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Conversion Rate
              </Typography>
              <Typography variant="h4" color="primary.main">
                {performance.usage.conversion_rate.toFixed(2)}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Total Disbursed */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Disbursed
              </Typography>
              <Typography variant="h4">
                {productLifecycleService.formatCurrency(performance.usage.total_disbursed_amount)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Average Disbursement */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Average Disbursement
              </Typography>
              <Typography variant="h4">
                {productLifecycleService.formatCurrency(performance.usage.average_disbursement)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Promotional Metrics (if applicable) */}
        {performance.promotional && (
          <>
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
                Promotional Metrics
              </Typography>
            </Grid>

            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Promotion Name
                  </Typography>
                  <Typography variant="h6">
                    {performance.promotional.promotion_name}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Application Utilization
                  </Typography>
                  <Typography variant="h4">
                    {performance.promotional.utilization_rate.toFixed(2)}%
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {performance.promotional.current_applications} / {performance.promotional.max_applications || 'Unlimited'}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Disbursement Utilization
                  </Typography>
                  <Typography variant="h6">
                    {productLifecycleService.formatCurrency(performance.promotional.current_disbursement)}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    of {performance.promotional.max_disbursement 
                      ? productLifecycleService.formatCurrency(performance.promotional.max_disbursement) 
                      : 'Unlimited'}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </>
        )}
      </Grid>
    </Container>
  );
}
