/**
 * Decision Engine List Page
 * Main page showing all decision requests
 */
'use client';

import React from 'react';
import { Box } from '@mui/material';
import { DecisionList } from '@/components/decision-engine';

export default function DecisionEnginePage() {
  return (
    <Box sx={{ p: 3 }}>
      <DecisionList />
    </Box>
  );
}
