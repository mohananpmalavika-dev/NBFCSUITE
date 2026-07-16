/**
 * Workflow Template Library
 * Browse and instantiate pre-built workflow templates
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
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
} from '@mui/material';
import {
  AccountTree,
  ContentCopy,
  Visibility,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import workflowService from '../../services/workflowService';

interface WorkflowTemplate {
  workflow_id: string;
  workflow_name: string;
  workflow_description: string;
  category: string;
  process: any;
}

const TemplateLibrary: React.FC = () => {
  const navigate = useNavigate();
  const [templates, setTemplates] = useState<WorkflowTemplate[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<WorkflowTemplate | null>(null);
  const [previewDialog, setPreviewDialog] = useState(false);

  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    setLoading(true);
    try {
      const response = await workflowService.getTemplateLibrary();
      setTemplates(response.templates || []);
    } catch (error) {
      console.error('Failed to load templates:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePreview = (template: WorkflowTemplate) => {
    setSelectedTemplate(template);
    setPreviewDialog(true);
  };

  const handleInstantiate = async (template: WorkflowTemplate) => {
    try {
      const response = await workflowService.instantiateTemplate(template.workflow_id);
      navigate(`/workflow/designer/${response.workflow_id}`);
    } catch (error) {
      console.error('Failed to instantiate template:', error);
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'lending':
        return 'primary';
      case 'compliance':
        return 'secondary';
      case 'deposits':
        return 'success';
      case 'operations':
        return 'info';
      default:
        return 'default';
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" fontWeight="bold" gutterBottom>
        Workflow Template Library
      </Typography>
      <Typography variant="body1" color="textSecondary" mb={3}>
        Choose from pre-built workflow templates to get started quickly
      </Typography>

      {loading ? (
        <Typography>Loading templates...</Typography>
      ) : (
        <Grid container spacing={3}>
          {templates.map((template) => (
            <Grid item xs={12} md={6} lg={4} key={template.workflow_id}>
              <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <CardContent sx={{ flexGrow: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <AccountTree sx={{ fontSize: 40, color: 'primary.main', mr: 2 }} />
                    <Box>
                      <Typography variant="h6" fontWeight="bold">
                        {template.workflow_name}
                      </Typography>
                      <Chip
                        label={template.category}
                        size="small"
                        color={getCategoryColor(template.category)}
                        sx={{ mt: 0.5 }}
                      />
                    </Box>
                  </Box>
                  <Typography variant="body2" color="textSecondary">
                    {template.workflow_description}
                  </Typography>
                  
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="caption" color="textSecondary">
                      Contains:
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1, mt: 1, flexWrap: 'wrap' }}>
                      {template.process.user_tasks?.length > 0 && (
                        <Chip
                          label={`${template.process.user_tasks.length} User Tasks`}
                          size="small"
                          variant="outlined"
                        />
                      )}
                      {template.process.service_tasks?.length > 0 && (
                        <Chip
                          label={`${template.process.service_tasks.length} Service Tasks`}
                          size="small"
                          variant="outlined"
                        />
                      )}
                      {template.process.gateways?.length > 0 && (
                        <Chip
                          label={`${template.process.gateways.length} Gateways`}
                          size="small"
                          variant="outlined"
                        />
                      )}
                    </Box>
                  </Box>
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
                    onClick={() => handleInstantiate(template)}
                  >
                    Use Template
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Preview Dialog */}
      <Dialog
        open={previewDialog}
        onClose={() => setPreviewDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {selectedTemplate?.workflow_name}
        </DialogTitle>
        <DialogContent>
          {selectedTemplate && (
            <Box>
              <Alert severity="info" sx={{ mb: 2 }}>
                {selectedTemplate.workflow_description}
              </Alert>
              
              <Typography variant="subtitle2" gutterBottom>
                Workflow Steps:
              </Typography>
              
              <Box sx={{ ml: 2 }}>
                {selectedTemplate.process.user_tasks?.map((task: any, index: number) => (
                  <Typography key={index} variant="body2">
                    • {task.name} - {task.description || 'User task'}
                  </Typography>
                ))}
                {selectedTemplate.process.service_tasks?.map((task: any, index: number) => (
                  <Typography key={index} variant="body2">
                    • {task.name} - {task.description || 'Automated task'}
                  </Typography>
                ))}
              </Box>
              
              <Typography variant="subtitle2" gutterBottom sx={{ mt: 2 }}>
                Decision Points:
              </Typography>
              <Box sx={{ ml: 2 }}>
                {selectedTemplate.process.gateways?.map((gateway: any, index: number) => (
                  <Typography key={index} variant="body2">
                    • {gateway.name} ({gateway.gateway_type})
                  </Typography>
                ))}
              </Box>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPreviewDialog(false)}>
            Close
          </Button>
          <Button
            variant="contained"
            onClick={() => {
              if (selectedTemplate) {
                handleInstantiate(selectedTemplate);
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

export default TemplateLibrary;
