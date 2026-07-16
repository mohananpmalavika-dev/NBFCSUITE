'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { Container, Typography, Breadcrumbs, Link, Box } from '@mui/material';
import { Home as HomeIcon } from '@mui/icons-material';
import { VariantBuilder } from '@/components/product-lifecycle';
import { ProductVariant } from '@/services/productLifecycle.service';

/**
 * Create New Product Variant Page
 */
export default function NewVariantPage() {
  const router = useRouter();

  const handleSave = (variant: ProductVariant) => {
    // Navigate to variant list
    router.push('/product-lifecycle');
  };

  const handleCancel = () => {
    router.back();
  };

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
        <Typography color="text.primary">New Variant</Typography>
      </Breadcrumbs>

      {/* Page Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Create New Product Variant
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Configure a new product variant with custom settings
        </Typography>
      </Box>

      {/* Variant Builder */}
      <VariantBuilder 
        onSave={handleSave}
        onCancel={handleCancel}
      />
    </Container>
  );
}
