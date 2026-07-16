/**
 * Decision Details Page
 * Page showing complete decision details with all check results
 */
'use client';

import React from 'react';
import { Box } from '@mui/material';
import { DecisionDetails } from '@/components/decision-engine';

interface DecisionDetailsPageProps {
  params: {
    id: string;
  };
}

export default function DecisionDetailsPage({ params }: DecisionDetailsPageProps) {
  return (
    <Box sx={{ p: 3 }}>
      <DecisionDetails decisionId={params.id} />
    </Box>
  );
}
