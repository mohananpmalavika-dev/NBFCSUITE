/**
 * Escalation History Component
 * 
 * Display escalation history for SLA instances
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Timeline,
  TimelineItem,
  TimelineSeparator,
  TimelineConnector,
  TimelineContent,
  TimelineDot,
  TimelineOppositeContent,
  Card,
  CardContent,
  Chip,
  List,
  ListItem,
  ListItemText,
  Divider,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  NotificationsActive as SoftIcon,
  TrendingUp as HardIcon,
  Warning as NotifyIcon,
  AccountTree as MultiLevelIcon,
} from '@mui/icons-material';
import slaService from '../../services/slaService';

interface EscalationHistoryProps {
  slaInstanceId: number;
}

interface EscalationEvent {
  event_id: number;
  created_at: string;
  event_data: {
    rule_id: string;
    rule_name: string;
    escalation_type: string;
    sla_percentage: number;
    time_elapsed_minutes: number;
    actions: string[];
  };
}

const EscalationHistory: React.FC<EscalationHistoryProps> = ({ slaInstanceId }) => {
  const [loading, setLoading] = useState(true);
  const [history, setHistory] = useState<EscalationEvent[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadHistory();
  }, [slaInstanceId]);

  const loadHistory = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await slaService.getEscalationHistory(slaInstanceId);
      setHistory(data);
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Failed to load escalation history');
    } finally {
      setLoading(false);
    }
  };

  const getEscalationIcon = (type: string) => {
    switch (type) {
      case 'soft':
        return <SoftIcon />;
      case 'hard':
        return <HardIcon />;
      case 'notify':
        return <NotifyIcon />;
      case 'multi_level':
        return <MultiLevelIcon />;
      default:
        return <NotifyIcon />;
    }
  };

  const getEscalationColor = (type: string) => {
    switch (type) {
      case 'soft':
        return 'info';
      case 'hard':
        return 'error';
      case 'notify':
        return 'warning';
      case 'multi_level':
        return 'secondary';
      default:
        return 'default';
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  if (history.length === 0) {
    return (
      <Paper sx={{ p: 3 }}>
        <Alert severity="info">No escalations have been triggered for this SLA instance.</Alert>
      </Paper>
    );
  }

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Escalation History
      </Typography>
      <Typography variant="body2" color="text.secondary" gutterBottom>
        {history.length} escalation{history.length !== 1 ? 's' : ''} triggered
      </Typography>

      <Timeline position="right" sx={{ mt: 3 }}>
        {history.map((event, index) => (
          <TimelineItem key={event.event_id}>
            <TimelineOppositeContent color="text.secondary" sx={{ flex: 0.3 }}>
              <Typography variant="body2">
                {new Date(event.created_at).toLocaleString()}
              </Typography>
              <Typography variant="caption">
                {slaService.formatDuration(event.event_data.time_elapsed_minutes)} elapsed
              </Typography>
            </TimelineOppositeContent>

            <TimelineSeparator>
              <TimelineDot color={getEscalationColor(event.event_data.escalation_type) as any}>
                {getEscalationIcon(event.event_data.escalation_type)}
              </TimelineDot>
              {index < history.length - 1 && <TimelineConnector />}
            </TimelineSeparator>

            <TimelineContent>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                    <Box>
                      <Typography variant="h6" component="div">
                        {event.event_data.rule_name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Rule ID: {event.event_data.rule_id}
                      </Typography>
                    </Box>
                    <Chip
                      label={event.event_data.escalation_type}
                      color={getEscalationColor(event.event_data.escalation_type) as any}
                      size="small"
                    />
                  </Box>

                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      SLA Progress: {event.event_data.sla_percentage.toFixed(1)}%
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Time Elapsed: {slaService.formatDuration(event.event_data.time_elapsed_minutes)}
                    </Typography>
                  </Box>

                  <Divider sx={{ my: 2 }} />

                  <Typography variant="subtitle2" gutterBottom>
                    Actions Taken:
                  </Typography>
                  <List dense>
                    {event.event_data.actions.map((action, idx) => (
                      <ListItem key={idx}>
                        <ListItemText
                          primary={action}
                          primaryTypographyProps={{
                            variant: 'body2'
                          }}
                        />
                      </ListItem>
                    ))}
                  </List>
                </CardContent>
              </Card>
            </TimelineContent>
          </TimelineItem>
        ))}
      </Timeline>
    </Paper>
  );
};

export default EscalationHistory;
