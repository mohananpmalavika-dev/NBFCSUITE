/**
 * Alerts Sidebar Component
 * 
 * Real-time alert monitoring and management
 * Features:
 * - Active alerts display
 * - Alert severity filtering
 * - Quick acknowledgment
 * - Alert history
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Drawer,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  Chip,
  Badge,
  Divider,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  CircularProgress
} from '@mui/material';
import {
  Warning,
  Error,
  Info,
  CheckCircle,
  Close,
  Notifications,
  NotificationsActive,
  Refresh
} from '@mui/icons-material';
import monitoringService, { ActiveAlert } from '../../../services/monitoringService';

interface AlertsSidebarProps {
  open: boolean;
  onClose: () => void;
  onAlertClick?: (alert: ActiveAlert) => void;
}

const AlertsSidebar: React.FC<AlertsSidebarProps> = ({ open, onClose, onAlertClick }) => {
  const [alerts, setAlerts] = useState<ActiveAlert[]>([]);
  const [loading, setLoading] = useState(false);
  const [severityFilter, setSeverityFilter] = useState<string>('all');
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    if (open) {
      loadAlerts();
    }

    if (autoRefresh && open) {
      const interval = setInterval(() => {
        loadAlerts();
      }, 5000); // Refresh every 5 seconds

      return () => clearInterval(interval);
    }
  }, [open, severityFilter, autoRefresh]);

  const loadAlerts = async () => {
    try {
      setLoading(true);
      const data = await monitoringService.getActiveAlerts({
        severity: severityFilter === 'all' ? undefined : severityFilter as any,
        limit: 100
      });
      setAlerts(data.alerts);
      setLoading(false);
    } catch (error) {
      console.error('Failed to load alerts:', error);
      setLoading(false);
    }
  };

  const handleAcknowledge = async (alertId: string) => {
    try {
      await monitoringService.acknowledgeAlert(alertId);
      setAlerts(prev => prev.filter(a => a.id !== alertId));
    } catch (error) {
      console.error('Failed to acknowledge alert:', error);
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return <Error color="error" />;
      case 'high':
        return <Warning color="warning" />;
      case 'medium':
        return <Info color="info" />;
      case 'low':
        return <Info color="action" />;
      default:
        return <Info />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'error';
      case 'high':
        return 'warning';
      case 'medium':
        return 'info';
      case 'low':
        return 'default';
      default:
        return 'default';
    }
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMinutes = Math.floor((now.getTime() - date.getTime()) / 60000);

    if (diffMinutes < 1) return 'Just now';
    if (diffMinutes < 60) return `${diffMinutes}m ago`;
    if (diffMinutes < 1440) return `${Math.floor(diffMinutes / 60)}h ago`;
    return date.toLocaleDateString();
  };

  const criticalCount = alerts.filter(a => a.alert_severity === 'critical').length;
  const highCount = alerts.filter(a => a.alert_severity === 'high').length;

  return (
    <Drawer
      anchor="right"
      open={open}
      onClose={onClose}
      sx={{ '& .MuiDrawer-paper': { width: 400 } }}
    >
      <Box sx={{ p: 2, height: '100%', display: 'flex', flexDirection: 'column' }}>
        {/* Header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Badge badgeContent={alerts.length} color="error">
              <NotificationsActive color="primary" />
            </Badge>
            <Typography variant="h6">Active Alerts</Typography>
          </Box>
          <IconButton onClick={onClose} size="small">
            <Close />
          </IconButton>
        </Box>

        {/* Summary Stats */}
        <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
          <Chip
            label={`${criticalCount} Critical`}
            color="error"
            size="small"
            variant={criticalCount > 0 ? 'filled' : 'outlined'}
          />
          <Chip
            label={`${highCount} High`}
            color="warning"
            size="small"
            variant={highCount > 0 ? 'filled' : 'outlined'}
          />
          <Chip
            label={`${alerts.length} Total`}
            size="small"
          />
        </Box>

        {/* Controls */}
        <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
          <FormControl fullWidth size="small">
            <InputLabel>Severity Filter</InputLabel>
            <Select
              value={severityFilter}
              label="Severity Filter"
              onChange={(e) => setSeverityFilter(e.target.value)}
            >
              <MenuItem value="all">All Severities</MenuItem>
              <MenuItem value="critical">Critical</MenuItem>
              <MenuItem value="high">High</MenuItem>
              <MenuItem value="medium">Medium</MenuItem>
              <MenuItem value="low">Low</MenuItem>
            </Select>
          </FormControl>
          <IconButton
            onClick={loadAlerts}
            disabled={loading}
            color="primary"
          >
            <Refresh />
          </IconButton>
        </Box>

        <Box sx={{ mb: 2 }}>
          <Button
            size="small"
            variant={autoRefresh ? 'contained' : 'outlined'}
            onClick={() => setAutoRefresh(!autoRefresh)}
            startIcon={<Notifications />}
            fullWidth
          >
            Auto-Refresh: {autoRefresh ? 'ON' : 'OFF'}
          </Button>
        </Box>

        <Divider />

        {/* Alerts List */}
        <Box sx={{ flex: 1, overflowY: 'auto', mt: 2 }}>
          {loading && alerts.length === 0 ? (
            <Box display="flex" justifyContent="center" py={4}>
              <CircularProgress />
            </Box>
          ) : alerts.length === 0 ? (
            <Alert severity="success" sx={{ mt: 2 }}>
              <Typography variant="body2">
                No active alerts. All systems normal.
              </Typography>
            </Alert>
          ) : (
            <List sx={{ p: 0 }}>
              {alerts.map((alert, index) => (
                <React.Fragment key={alert.id}>
                  <ListItem
                    sx={{
                      bgcolor: alert.alert_severity === 'critical' ? 'error.light' : 'transparent',
                      borderRadius: 1,
                      mb: 1,
                      cursor: 'pointer',
                      '&:hover': { bgcolor: 'action.hover' }
                    }}
                    onClick={() => onAlertClick && onAlertClick(alert)}
                  >
                    <ListItemIcon>
                      {getSeverityIcon(alert.alert_severity)}
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Typography variant="subtitle2" sx={{ flex: 1 }}>
                            {alert.alert_type}
                          </Typography>
                          <Chip
                            label={alert.alert_severity}
                            size="small"
                            color={getSeverityColor(alert.alert_severity) as any}
                          />
                        </Box>
                      }
                      secondary={
                        <Box>
                          <Typography variant="body2" color="textSecondary">
                            {alert.alert_message}
                          </Typography>
                          <Typography variant="caption" color="textSecondary">
                            {formatTimestamp(alert.alert_timestamp)}
                          </Typography>
                        </Box>
                      }
                    />
                    <IconButton
                      edge="end"
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleAcknowledge(alert.id);
                      }}
                      color="success"
                    >
                      <CheckCircle />
                    </IconButton>
                  </ListItem>
                  {index < alerts.length - 1 && <Divider />}
                </React.Fragment>
              ))}
            </List>
          )}
        </Box>

        {/* Footer Actions */}
        {alerts.length > 0 && (
          <Box sx={{ mt: 2 }}>
            <Button
              variant="outlined"
              fullWidth
              onClick={() => {
                alerts.forEach(alert => handleAcknowledge(alert.id));
              }}
            >
              Acknowledge All
            </Button>
          </Box>
        )}
      </Box>
    </Drawer>
  );
};

export default AlertsSidebar;
