'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { Container, Typography, Breadcrumbs, Link, Box, CircularProgress, Alert } from '@mui/material';
import { Home as HomeIcon } from '@mui/icons-material';
import { VariantBuilder } from '@/components/product-lifecycle';
import productLifecycleService, { ProductVariant } from '@/services/productLifecycle.service';

/**
 * Edit Product Variant Page
 */
export default function EditVariantPage() {
  const router = useRouter();
  const params = useParams();
  const variantId = params.id as string;

  const [variant, setVariant] = useState<ProductVariant | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadVariant();
  }, [variantId]);

  const loadVariant = async () => {
    try {
      const data = await productLifecycleService.getVariant(variantId);
      setVariant(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load variant');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = (updatedVariant: ProductVariant) => {
    router.push('/product-lifecycle');
  };

  const handleCancel = () => {
    router.back();
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4, textAlign: 'center' }}>
        <CircularProgress />
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
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
        <Typography color="text.primary">Edit Variant</Typography>
      </Breadcrumbs>

      {/* Page Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Edit Product Variant
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Update variant configuration: {variant?.variant_name}
        </Typography>
      </Box>

      {/* Variant Builder */}
      {variant && (
        <VariantBuilder 
          variant={variant}
          onSave={handleSave}
          onCancel={handleCancel}
        />
      )}
    </Container>
  );
}
