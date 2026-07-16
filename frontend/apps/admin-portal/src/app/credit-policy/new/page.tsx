'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { Box, Container, Typography, Breadcrumbs, Link } from '@mui/material';
import { Home as HomeIcon } from '@mui/icons-material';
import { CreditPolicyBuilder } from '@/components/credit-policy';

/**
 * Create New Credit Policy Page
 * Multi-step wizard for creating credit policies
 */
export default function NewCreditPolicyPage() {
  const router = useRouter();

  const handleSave = () => {
    // Navigate back to list after successful save
    router.push('/credit-policy');
  };

  const handleCancel = () => {
    // Navigate back to list on cancel
    router.push('/credit-policy');
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
        <Link
          underline="hover"
          color="inherit"
          href="/credit-policy"
        >
          Credit Policy
        </Link>
        <Typography color="text.primary">New Policy</Typography>
      </Breadcrumbs>

      {/* Page Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Create New Credit Policy
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Configure risk-based pricing, credit decisioning rules, and exposure limits
        </Typography>
      </Box>

      {/* Credit Policy Builder Component */}
      <CreditPolicyBuilder
        onSave={handleSave}
        onCancel={handleCancel}
      />
    </Container>
  );
}
