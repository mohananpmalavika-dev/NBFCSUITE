/**
 * Decision Engine Dashboard Page
 * Analytics and statistics page for decision engine
 */
'use client';

import React from 'react';
import { Box } from '@mui/material';
import { DecisionDashboard } from '@/components/decision-engine';

export default function DecisionEngineDashboardPage() {
  return (
    <Box sx={{ p: 3 }}>
      <DecisionDashboard />
    </Box>
  );
}
