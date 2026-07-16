'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { Box, Container, Typography, Breadcrumbs, Link } from '@mui/material';
import { Home as HomeIcon } from '@mui/icons-material';
import { VariantList } from '@/components/product-lifecycle';
import { ProductVariant } from '@/services/productLifecycle.service';

/**
 * Product Lifecycle Management - Main Page
 * Lists all product variants with CRUD operations
 */
export default function ProductLifecyclePage() {
  const router = useRouter();

  const handleCreateNew = () => {
    router.push('/product-lifecycle/new');
  };

  const handleEdit = (variant: ProductVariant) => {
    router.push(`/product-lifecycle/${variant.id}/edit`);
  };

  const handleViewPerformance = (variant: ProductVariant) => {
    router.push(`/product-lifecycle/${variant.id}/performance`);
  };

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
        <Typography color="text.primary">Product Lifecycle</Typography>
      </Breadcrumbs>

      {/* Page Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Product Lifecycle Management
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Manage product variants, promotional offers, seasonal products, and product sunset
        </Typography>
      </Box>

      {/* Variant List Component */}
      <VariantList 
        onCreateNew={handleCreateNew}
        onEdit={handleEdit}
        onViewPerformance={handleViewPerformance}
      />
    </Container>
  );
}
