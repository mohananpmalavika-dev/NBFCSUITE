/**
 * Decision Dashboard Component
 * Analytics and statistics dashboard for decision engine
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  CircularProgress,
  Alert,
  Chip
} from '@mui/material';
import {
  CheckCircle as ApprovedIcon,
  Cancel as DeclinedIcon,
  RateReview as ReviewIcon,
  Assessment as StatsIcon
} from '@mui/icons-material';
import {
  decisionEngineService,
  DashboardSummary,
  formatDecisionOutcome,
  getDecisionOutcomeColor
} from '@/services/decisionEngine.service';
import { useRouter } from 'next/navigation';

export default function DecisionDashboard() {
  const router = useRouter();
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await decisionEngineService.getDashboardSummary();
      setSummary(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load dashboard');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight={400}>
        <CircularProgress />
      </Box>
    );
  }

  if (error || !summary) {
    return (
      <Alert severity="error">
        {error || 'Failed to load dashboard'}
      </Alert>
    );
  }

  const { today_stats, pending_decisions, needs_manual_review, recent_decisions } = summary;

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Decision Engine Dashboard
      </Typography>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="subtitle2" color="textSecondary">
                    Total Decisions (Today)
                  </Typography>
                  <Typography variant="h4">
                    {today_stats.total_decisions}
                  </Typography>
                </Box>
                <StatsIcon sx={{ fontSize: 48, color: 'primary.main', opacity: 0.3 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="subtitle2" color="textSecondary">
                    Approved
                  </Typography>
                  <Typography variant="h4" color="success.main">
                    {today_stats.approved + today_stats.approved_with_conditions}
                  </Typography>
                  <Typography variant="caption" color="textSecondary">
                    {today_stats.approval_rate.toFixed(1)}% approval rate
                  </Typography>
                </Box>
                <ApprovedIcon sx={{ fontSize: 48, color: 'success.main', opacity: 0.3 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="subtitle2" color="textSecondary">
                    Declined
                  </Typography>
                  <Typography variant="h4" color="error.main">
                    {today_stats.declined}
                  </Typography>
                </Box>
                <DeclinedIcon sx={{ fontSize: 48, color: 'error.main', opacity: 0.3 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="subtitle2" color="textSecondary">
                    Manual Review
                  </Typography>
                  <Typography variant="h4" color="warning.main">
                    {needs_manual_review}
                  </Typography>
                  <Typography variant="caption" color="textSecondary">
                    Needs attention
                  </Typography>
                </Box>
                <ReviewIcon sx={{ fontSize: 48, color: 'warning.main', opacity: 0.3 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Performance Metrics */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                Average Decision Score
              </Typography>
              <Typography variant="h3">
                {today_stats.avg_decision_score.toFixed(1)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                Average Confidence
              </Typography>
              <Typography variant="h3">
                {today_stats.avg_confidence_score.toFixed(1)}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                Avg Processing Time
              </Typography>
              <Typography variant="h3">
                {(today_stats.avg_processing_time_ms / 1000).toFixed(1)}s
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Recent Decisions */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Recent Decisions
          </Typography>
          <Box>
            {recent_decisions.map((decision) => (
              <Box
                key={decision.id}
                sx={{
                  p: 2,
                  mb: 2,
                  border: '1px solid',
                  borderColor: 'divider',
                  borderRadius: 1,
                  cursor: 'pointer',
                  '&:hover': {
                    bgcolor: 'action.hover'
                  }
                }}
                onClick={() => router.push(`/decision-engine/${decision.id}`)}
              >
                <Grid container spacing={2} alignItems="center">
                  <Grid item xs={12} sm={3}>
                    <Typography variant="caption" color="textSecondary">
                      Application ID
                    </Typography>
                    <Typography variant="body2" fontFamily="monospace">
                      {decision.application_id.substring(0, 12)}...
                    </Typography>
                  </Grid>
                  <Grid item xs={12} sm={2}>
                    <Typography variant="caption" color="textSecondary">
                      Amount
                    </Typography>
                    <Typography variant="body2">
                      ₹{decision.loan_amount.toLocaleString('en-IN')}
                    </Typography>
                  </Grid>
                  <Grid item xs={12} sm={2}>
                    <Typography variant="caption" color="textSecondary">
                      Outcome
                    </Typography>
                    <Box>
                      <Chip
                        label={formatDecisionOutcome(decision.decision_outcome)}
                        color={getDecisionOutcomeColor(decision.decision_outcome) as any}
                        size="small"
                      />
                    </Box>
                  </Grid>
                  <Grid item xs={12} sm={2}>
                    <Typography variant="caption" color="textSecondary">
                      Score
                    </Typography>
                    <Typography variant="body2">
                      {decision.decision_score?.toFixed(1) || 'N/A'}
                    </Typography>
                  </Grid>
                  <Grid item xs={12} sm={3}>
                    <Typography variant="caption" color="textSecondary">
                      Time
                    </Typography>
                    <Typography variant="body2">
                      {new Date(decision.request_time).toLocaleString('en-IN', {
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </Typography>
                  </Grid>
                </Grid>
              </Box>
            ))}
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
}
