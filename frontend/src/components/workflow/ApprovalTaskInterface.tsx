/**
 * Approval Task Interface
 * Interface for users to approve/reject/delegate tasks
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Stack,
  Card,
  CardContent,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Chip,
  Divider,
  Alert,
  Grid,
  List,
  ListItem,
  ListItemText,
  Avatar,
  LinearProgress,
} from '@mui/material';
import {
  ThumbUp as ApproveIcon,
  ThumbDown as RejectIcon,
  Forward as DelegateIcon,
  Undo as ReturnIcon,
  CheckCircle,
  Cancel,
  HourglassEmpty,
} from '@mui/icons-material';
import approvalService from '../../services/approvalService';

interface ApprovalTaskInterfaceProps {
  taskId: number;
  instanceId: number;
  onComplete?: () => void;
}

const ApprovalTaskInterface: React.FC<ApprovalTaskInterfaceProps> = ({
  taskId,
  instanceId,
  onComplete,
}) => {
  const [task, setTask] = useState<any>(null);
  const [instance, setInstance] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [actionDialog, setActionDialog] = useState(false);
  const [actionType, setActionType] = useState<'approve' | 'reject' | 'delegate' | 'return'>('approve');
  const [comments, setComments] = useState('');
  const [delegateTo, setDelegateTo] = useState<number | ''>('');

  useEffect(() => {
    loadData();
  }, [taskId, instanceId]);

  const loadData = async () => {
    setLoading(true);
    try {
      // Load approval status
      const response = await approvalService.getApprovalStatus(instanceId);
      setInstance(response.instance);
    } catch (error) {
      console.error('Failed to load approval data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAction = (action: 'approve' | 'reject' | 'delegate' | 'return') => {
    setActionType(action);
    setActionDialog(true);
  };

  const handleConfirmAction = async () => {
    setLoading(true);
    try {
      await approvalService.processApproval(instanceId, taskId, {
        action: actionType,
        comments: comments || undefined,
        delegate_to: actionType === 'delegate' ? Number(delegateTo) : undefined,
      });

      setActionDialog(false);
      setComments('');
      setDelegateTo('');

      if (onComplete) {
        onComplete();
      }
    } catch (error) {
      console.error('Failed to process approval:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'approved':
        return 'success';
      case 'rejected':
        return 'error';
      case 'in_progress':
        return 'primary';
      case 'pending':
        return 'warning';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'approved':
      case 'completed':
        return <CheckCircle color="success" />;
      case 'rejected':
        return <Cancel color="error" />;
      case 'pending':
      case 'in_progress':
        return <HourglassEmpty color="warning" />;
      default:
        return null;
    }
  };

  if (loading && !instance) {
    return (
      <Box sx={{ p: 3 }}>
        <LinearProgress />
      </Box>
    );
  }

  if (!instance) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">Approval instance not found</Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Stack direction="row" justifyContent="space-between" alignItems="center">
          <Box>
            <Typography variant="h5" fontWeight="bold" gutterBottom>
              Approval Request
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Instance: {instance.instance_number}
            </Typography>
          </Box>
          <Chip
            icon={getStatusIcon(instance.status)}
            label={instance.status.toUpperCase()}
            color={getStatusColor(instance.status)}
          />
        </Stack>
      </Paper>

      {/* Entity Details */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Entity Details
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6}>
            <Typography variant="body2" color="textSecondary">
              Entity Type
            </Typography>
            <Typography variant="body1">{instance.entity_type}</Typography>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Typography variant="body2" color="textSecondary">
              Entity ID
            </Typography>
            <Typography variant="body1">{instance.entity_id}</Typography>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Typography variant="body2" color="textSecondary">
              Started At
            </Typography>
            <Typography variant="body1">
              {instance.started_at
                ? new Date(instance.started_at).toLocaleString()
                : '-'}
            </Typography>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Typography variant="body2" color="textSecondary">
              Completed At
            </Typography>
            <Typography variant="body1">
              {instance.completed_at
                ? new Date(instance.completed_at).toLocaleString()
                : '-'}
            </Typography>
          </Grid>
        </Grid>
      </Paper>

      {/* Approval Levels Progress */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Approval Progress
        </Typography>
        {instance.approval_levels && instance.approval_levels.length > 0 ? (
          <Stack spacing={2}>
            {instance.approval_levels.map((level: any, index: number) => (
              <Card key={index} variant="outlined">
                <CardContent>
                  <Stack direction="row" justifyContent="space-between" alignItems="center" mb={1}>
                    <Typography variant="subtitle1" fontWeight="bold">
                      Level {level.level}
                    </Typography>
                    <Chip
                      label={`${level.approved_count}/${level.required_count} Approved`}
                      size="small"
                      color={
                        level.approved_count >= level.required_count
                          ? 'success'
                          : 'default'
                      }
                    />
                  </Stack>
                  
                  {level.approvers && level.approvers.length > 0 && (
                    <List dense>
                      {level.approvers.map((approver: any, idx: number) => (
                        <ListItem key={idx}>
                          <Avatar sx={{ width: 24, height: 24, mr: 1 }}>
                            {approver.user_id}
                          </Avatar>
                          <ListItemText
                            primary={`User ${approver.user_id}`}
                            secondary={`${approver.action} - ${new Date(
                              approver.timestamp
                            ).toLocaleString()}`}
                          />
                        </ListItem>
                      ))}
                    </List>
                  )}
                </CardContent>
              </Card>
            ))}
          </Stack>
        ) : (
          <Typography variant="body2" color="textSecondary">
            No approval levels recorded yet
          </Typography>
        )}
      </Paper>

      {/* Action Buttons */}
      {instance.status === 'in_progress' && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Your Action
          </Typography>
          <Stack direction="row" spacing={2}>
            <Button
              variant="contained"
              color="success"
              startIcon={<ApproveIcon />}
              onClick={() => handleAction('approve')}
              size="large"
            >
              Approve
            </Button>
            <Button
              variant="contained"
              color="error"
              startIcon={<RejectIcon />}
              onClick={() => handleAction('reject')}
              size="large"
            >
              Reject
            </Button>
            <Button
              variant="outlined"
              startIcon={<DelegateIcon />}
              onClick={() => handleAction('delegate')}
              size="large"
            >
              Delegate
            </Button>
            <Button
              variant="outlined"
              startIcon={<ReturnIcon />}
              onClick={() => handleAction('return')}
              size="large"
            >
              Return to Maker
            </Button>
          </Stack>
        </Paper>
      )}

      {/* Action Dialog */}
      <Dialog open={actionDialog} onClose={() => setActionDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          {actionType === 'approve' && 'Approve Request'}
          {actionType === 'reject' && 'Reject Request'}
          {actionType === 'delegate' && 'Delegate Request'}
          {actionType === 'return' && 'Return to Maker'}
        </DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 2 }}>
            {actionType === 'delegate' && (
              <TextField
                fullWidth
                type="number"
                label="Delegate To (User ID)"
                value={delegateTo}
                onChange={(e) => setDelegateTo(e.target.value ? Number(e.target.value) : '')}
                required
              />
            )}
            
            <TextField
              fullWidth
              multiline
              rows={4}
              label="Comments"
              value={comments}
              onChange={(e) => setComments(e.target.value)}
              required={actionType === 'reject' || actionType === 'return'}
              placeholder={
                actionType === 'reject'
                  ? 'Please provide reason for rejection (required)'
                  : actionType === 'return'
                  ? 'Please provide reason for return (required)'
                  : 'Add your comments (optional)'
              }
            />

            {actionType === 'reject' && (
              <Alert severity="warning">
                Rejecting this request will terminate the approval workflow.
              </Alert>
            )}
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setActionDialog(false)}>Cancel</Button>
          <Button
            onClick={handleConfirmAction}
            variant="contained"
            color={actionType === 'approve' ? 'success' : actionType === 'reject' ? 'error' : 'primary'}
            disabled={
              loading ||
              (actionType === 'delegate' && !delegateTo) ||
              ((actionType === 'reject' || actionType === 'return') && !comments)
            }
          >
            Confirm {actionType}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ApprovalTaskInterface;
