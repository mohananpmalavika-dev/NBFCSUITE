'use client';

import React from 'react';
import { useRouter, useParams } from 'next/navigation';
import { Box, Container, Typography, Breadcrumbs, Link } from '@mui/material';
import { Home as HomeIcon } from '@mui/icons-material';
import { CreditPolicyBuilder } from '@/components/credit-policy';

/**
 * Edit Credit Policy Page
 * Multi-step wizard for editing existing credit policies
 */
export default function EditCreditPolicyPage() {
  const router = useRouter();
  const params = useParams();
  const policyId = params.id as string;

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
        <Typography color="text.primary">Edit Policy</Typography>
      </Breadcrumbs>

      {/* Page Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Edit Credit Policy
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Update risk-based pricing, credit decisioning rules, and exposure limits
        </Typography>
      </Box>

      {/* Credit Policy Builder Component */}
      <CreditPolicyBuilder
        policyId={policyId}
        onSave={handleSave}
        onCancel={handleCancel}
      />
    </Container>
  );
}
