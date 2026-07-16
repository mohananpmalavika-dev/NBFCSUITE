'use client';

import React, { useState } from 'react';
import { Box, Container, Typography, Breadcrumbs, Link } from '@mui/material';
import { Home as HomeIcon } from '@mui/icons-material';
import { CreditPolicyList } from '@/components/credit-policy';

/**
 * Credit Policy Management Page
 * Lists all credit policies with CRUD operations
 */
export default function CreditPolicyPage() {
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
        <Typography color="text.primary">Credit Policy</Typography>
      </Breadcrumbs>

      {/* Page Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Credit Policy Management
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Manage risk-based pricing, credit decisioning, and exposure limits
        </Typography>
      </Box>

      {/* Credit Policy List Component */}
      <CreditPolicyList />
    </Container>
  );
}
