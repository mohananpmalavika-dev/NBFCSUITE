/**
 * New Decision Request Page
 * Page for submitting new decision requests
 */
'use client';

import React from 'react';
import { Box } from '@mui/material';
import { DecisionRequestForm } from '@/components/decision-engine';

export default function NewDecisionPage() {
  return (
    <Box sx={{ p: 3 }}>
      <DecisionRequestForm />
    </Box>
  );
}
