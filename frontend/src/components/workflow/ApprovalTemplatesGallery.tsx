/**
 * Approval Templates Gallery
 * Browse and use pre-built approval chain templates
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  CardActions,
  Typography,
  Button,
  Chip,
  Stack,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Paper,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import {
  ArrowForward,
  AccountTree,
  CallSplit,
  Group,
  Check,
  Visibility,
  ContentCopy,
} from '@mui/icons-material';
import approvalService from '../../services/approvalService';

interface ApprovalTemplate {
  id: string;
  name: string;
  description: string;
  type: string;
  levels: number;
}

const ApprovalTemplatesGallery: React.FC = () => {
  const [templates, setTemplates] = useState<ApprovalTemplate[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<any>(null);
  const [previewDialog, setPreviewDialog] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    setLoading(true);
    try {
      const response = await approvalService.getApprovalTemplates();
      setTemplates(response.templates || []);
    } catch (error) {
      console.error('Failed to load templates:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePreview = async (template: ApprovalTemplate) => {
    try {
      const response = await approvalService.getApprovalChain(template.id);
      setSelectedTemplate(response.chain);
      setPreviewDialog(true);
    } catch (error) {
      console.error('Failed to load template details:', error);
    }
  };

  const handleUseTemplate = async (template: ApprovalTemplate) => {
    // Navigate to configurator with template
    console.log('Using template:', template.id);
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'sequential':
        return <ArrowForward color="primary" />;
      case 'parallel':
        return <AccountTree color="success" />;
      case 'any_one':
        return <CallSplit color="warning" />;
      case 'majority':
        return <Group color="info" />;
      default:
        return <Check />;
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'sequential':
        return 'primary';
      case 'parallel':
        return 'success';
      case 'any_one':
        return 'warning';
      case 'majority':
        return 'info';
      case 'maker_checker':
        return 'secondary';
      default:
        return 'default';
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" fontWeight="bold" gutterBottom>
        Approval Chain Templates
      </Typography>
      <Typography variant="body1" color="textSecondary" mb={3}>
        Choose from pre-built approval workflows and customize them for your needs
      </Typography>

      <Grid container spacing={3}>
        {templates.map((template) => (
          <Grid item xs={12} md={6} lg={4} key={template.id}>
            <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
              <CardContent sx={{ flexGrow: 1 }}>
                <Stack direction="row" alignItems="center" spacing={2} mb={2}>
                  {getTypeIcon(template.type)}
                  <Box>
                    <Typography variant="h6" fontWeight="bold">
                      {template.name}
                    </Typography>
                    <Chip
                      label={template.type.replace('_', ' ')}
                      size="small"
                      color={getTypeColor(template.type) as any}
                      sx={{ mt: 0.5 }}
                    />
                  </Box>
                </Stack>

                <Typography variant="body2" color="textSecondary" mb={2}>
                  {template.description}
                </Typography>

                <Stack direction="row" spacing={1}>
                  <Chip
                    label={`${template.levels} Level${template.levels > 1 ? 's' : ''}`}
                    size="small"
                    variant="outlined"
                  />
                </Stack>
              </CardContent>

              <CardActions sx={{ justifyContent: 'space-between', p: 2 }}>
                <Button
                  size="small"
                  startIcon={<Visibility />}
                  onClick={() => handlePreview(template)}
                >
                  Preview
                </Button>
                <Button
                  size="small"
                  variant="contained"
                  startIcon={<ContentCopy />}
                  onClick={() => handleUseTemplate(template)}
                >
                  Use Template
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Template Details */}
      <Paper sx={{ mt: 4, p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Approval Types Explained
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <Card variant="outlined">
              <CardContent>
                <Stack direction="row" spacing={2} mb={1}>
                  <ArrowForward color="primary" />
                  <Typography variant="subtitle1" fontWeight="bold">
                    Sequential Approval
                  </Typography>
                </Stack>
                <Typography variant="body2" color="textSecondary">
                  One approver after another. Each level must approve before moving to next.
                </Typography>
                <Typography variant="caption" color="textSecondary" sx={{ mt: 1, display: 'block' }}>
                  Example: Loan Officer → Branch Manager → Regional Manager
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card variant="outlined">
              <CardContent>
                <Stack direction="row" spacing={2} mb={1}>
                  <AccountTree color="success" />
                  <Typography variant="subtitle1" fontWeight="bold">
                    Parallel Approval
                  </Typography>
                </Stack>
                <Typography variant="body2" color="textSecondary">
                  All approvers must approve simultaneously. Faster processing.
                </Typography>
                <Typography variant="caption" color="textSecondary" sx={{ mt: 1, display: 'block' }}>
                  Example: Risk Team + Legal Team + Finance Team (all at once)
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card variant="outlined">
              <CardContent>
                <Stack direction="row" spacing={2} mb={1}>
                  <CallSplit color="warning" />
                  <Typography variant="subtitle1" fontWeight="bold">
                    Any One Approval
                  </Typography>
                </Stack>
                <Typography variant="body2" color="textSecondary">
                  First to approve wins. Useful for distributed teams.
                </Typography>
                <Typography variant="caption" color="textSecondary" sx={{ mt: 1, display: 'block' }}>
                  Example: Any Regional Manager (North/South/East/West)
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card variant="outlined">
              <CardContent>
                <Stack direction="row" spacing={2} mb={1}>
                  <Group color="info" />
                  <Typography variant="subtitle1" fontWeight="bold">
                    Majority Approval
                  </Typography>
                </Stack>
                <Typography variant="body2" color="textSecondary">
                  Threshold-based approval. Requires specific number or percentage.
                </Typography>
                <Typography variant="caption" color="textSecondary" sx={{ mt: 1, display: 'block' }}>
                  Example: 3 out of 5 committee members must approve
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Paper>

      {/* Preview Dialog */}
      <Dialog
        open={previewDialog}
        onClose={() => setPreviewDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {selectedTemplate?.name}
        </DialogTitle>
        <DialogContent>
          {selectedTemplate && (
            <Box>
              <Typography variant="body1" paragraph>
                {selectedTemplate.description}
              </Typography>

              <Typography variant="subtitle2" gutterBottom sx={{ mt: 2 }}>
                Approval Levels:
              </Typography>
              <List>
                {selectedTemplate.levels?.map((level: any, index: number) => (
                  <ListItem key={index}>
                    <ListItemIcon>
                      <Chip label={level.level} color="primary" size="small" />
                    </ListItemIcon>
                    <ListItemText
                      primary={level.name}
                      secondary={`Type: ${level.approval_type} • SLA: ${level.sla_hours || 24}h`}
                    />
                  </ListItem>
                ))}
              </List>

              {selectedTemplate.maker_checker_enabled && (
                <Paper sx={{ p: 2, bgcolor: 'warning.light', mt: 2 }}>
                  <Typography variant="body2" fontWeight="bold">
                    ⚠️ Maker-Checker Enabled
                  </Typography>
                  <Typography variant="caption">
                    Maker cannot approve their own submission. A different user must approve.
                  </Typography>
                </Paper>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPreviewDialog(false)}>Close</Button>
          <Button
            variant="contained"
            onClick={() => {
              if (selectedTemplate) {
                handleUseTemplate({ ...selectedTemplate });
              }
            }}
          >
            Use This Template
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ApprovalTemplatesGallery;
