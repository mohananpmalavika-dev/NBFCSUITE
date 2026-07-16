/**
 * Rule Library Component
 * 
 * Browse and use pre-built rule templates from the library
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Divider,
  Grid,
  Card,
  CardContent,
  CardActions,
  Chip,
  Alert,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Tabs,
  Tab,
  InputAdornment,
  IconButton,
  Tooltip,
  List,
  ListItem,
  ListItemText,
  Badge,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  Search as SearchIcon,
  LibraryBooks as LibraryIcon,
  ContentCopy as CopyIcon,
  Add as AddIcon,
  Visibility as ViewIcon,
  CheckCircle as CheckIcon,
  ExpandMore as ExpandMoreIcon,
  FilterList as FilterIcon,
  Category as CategoryIcon,
  VerifiedUser as ComplianceIcon,
  TrendingUp as TrendingIcon,
} from '@mui/icons-material';

export interface RuleTemplate {
  template_id: string;
  template_name: string;
  description: string;
  category: string;
  rule_template: any;
  tags: string[];
  compliance_tags: string[];
  usage_count: number;
  created_at: string;
  updated_at: string;
}

interface RuleLibraryProps {
  onTemplateSelect?: (template: RuleTemplate) => void;
  onCreateFromTemplate?: (rulesetId: string) => void;
}

const RuleLibrary: React.FC<RuleLibraryProps> = ({
  onTemplateSelect,
  onCreateFromTemplate,
}) => {
  const [templates, setTemplates] = useState<RuleTemplate[]>([]);
  const [filteredTemplates, setFilteredTemplates] = useState<RuleTemplate[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [complianceTags, setComplianceTags] = useState<string[]>([]);
  const [libraryStats, setLibraryStats] = useState<any>(null);
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  const [activeTab, setActiveTab] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [selectedCompliance, setSelectedCompliance] = useState<string>('');
  
  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  const [cloneDialogOpen, setCloneDialogOpen] = useState(false);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<RuleTemplate | null>(null);
  
  const [cloneName, setCloneName] = useState('');
  const [cloneModifications, setCloneModifications] = useState('{}');
  const [rulesetName, setRulesetName] = useState('');
  const [entityType, setEntityType] = useState('');

  useEffect(() => {
    loadTemplates();
    loadCategories();
    loadComplianceTags();
    loadLibraryStats();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [templates, searchQuery, selectedCategory, selectedCompliance, activeTab]);

  const loadTemplates = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/rules/library/templates');
      const data = await response.json();
      if (data.success) {
        setTemplates(data.data);
      }
    } catch (err) {
      setError('Error loading templates');
    } finally {
      setLoading(false);
    }
  };

  const loadCategories = async () => {
    try {
      const response = await fetch('/api/rules/library/categories');
      const data = await response.json();
      if (data.success) {
        setCategories(data.data);
      }
    } catch (err) {
      console.error('Error loading categories:', err);
    }
  };

  const loadComplianceTags = async () => {
    try {
      const response = await fetch('/api/rules/library/compliance-tags');
      const data = await response.json();
      if (data.success) {
        setComplianceTags(data.data);
      }
    } catch (err) {
      console.error('Error loading compliance tags:', err);
    }
  };

  const loadLibraryStats = async () => {
    try {
      const response = await fetch('/api/rules/library/stats');
      const data = await response.json();
      if (data.success) {
        setLibraryStats(data.data);
      }
    } catch (err) {
      console.error('Error loading stats:', err);
    }
  };

  const applyFilters = () => {
    let filtered = [...templates];

    // Filter by category
    if (selectedCategory) {
      filtered = filtered.filter(t => t.category === selectedCategory);
    }

    // Filter by compliance tag
    if (selectedCompliance) {
      filtered = filtered.filter(t => t.compliance_tags.includes(selectedCompliance));
    }

    // Filter by search query
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(t =>
        t.template_name.toLowerCase().includes(query) ||
        t.description.toLowerCase().includes(query) ||
        t.tags.some(tag => tag.toLowerCase().includes(query))
      );
    }

    // Filter by tab
    if (activeTab === 1) {
      // Most Used
      filtered.sort((a, b) => b.usage_count - a.usage_count);
    } else if (activeTab === 2) {
      // Compliance Only
      filtered = filtered.filter(t => t.compliance_tags.length > 0);
    }

    setFilteredTemplates(filtered);
  };


  const handleCloneTemplate = async () => {
    if (!selectedTemplate) return;
    
    setLoading(true);
    setError(null);
    try {
      const parsedMods = cloneModifications ? JSON.parse(cloneModifications) : null;
      
      const response = await fetch(`/api/rules/library/templates/${selectedTemplate.template_id}/clone`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          new_name: cloneName,
          modifications: parsedMods,
        }),
      });
      const data = await response.json();
      if (data.success) {
        setSuccess('Template cloned successfully');
        setCloneDialogOpen(false);
        setCloneName('');
        setCloneModifications('{}');
      } else {
        setError(data.detail || 'Failed to clone template');
      }
    } catch (err: any) {
      setError(err.message || 'Error cloning template');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateFromTemplate = async () => {
    if (!selectedTemplate) return;
    
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`/api/rules/library/templates/${selectedTemplate.template_id}/create-ruleset`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ruleset_name: rulesetName,
          entity_type: entityType,
          modifications: {},
        }),
      });
      const data = await response.json();
      if (data.success) {
        setSuccess('Ruleset created successfully from template');
        setCreateDialogOpen(false);
        setRulesetName('');
        setEntityType('');
        if (onCreateFromTemplate) {
          onCreateFromTemplate(data.data.ruleset_id);
        }
      } else {
        setError(data.detail || 'Failed to create ruleset');
      }
    } catch (err) {
      setError('Error creating ruleset from template');
    } finally {
      setLoading(false);
    }
  };

  const handleViewTemplate = (template: RuleTemplate) => {
    setSelectedTemplate(template);
    setViewDialogOpen(true);
    if (onTemplateSelect) {
      onTemplateSelect(template);
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'rbi_compliance': return <ComplianceIcon />;
      case 'loan_eligibility': return <CheckIcon />;
      default: return <CategoryIcon />;
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'rbi_compliance': return 'error';
      case 'loan_eligibility': return 'primary';
      case 'credit_assessment': return 'success';
      case 'compliance': return 'warning';
      case 'pricing': return 'info';
      case 'risk_assessment': return 'secondary';
      default: return 'default';
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Paper sx={{ p: 3 }}>
        {/* Header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <LibraryIcon fontSize="large" color="primary" />
            <Box>
              <Typography variant="h5">Rule Library</Typography>
              <Typography variant="body2" color="text.secondary">
                {templates.length} pre-built templates available
              </Typography>
            </Box>
          </Box>
        </Box>

        <Divider sx={{ mb: 3 }} />

        {/* Alerts */}
        {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>{error}</Alert>}
        {success && <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(null)}>{success}</Alert>}

        {/* Stats Cards */}
        {libraryStats && (
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Typography variant="h4">{libraryStats.total_templates}</Typography>
                  <Typography variant="caption" color="text.secondary">Total Templates</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Typography variant="h4">{Object.keys(libraryStats.categories || {}).length}</Typography>
                  <Typography variant="caption" color="text.secondary">Categories</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Typography variant="h4">{libraryStats.total_usage}</Typography>
                  <Typography variant="caption" color="text.secondary">Total Usage</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={3}>
              <Card sx={{ bgcolor: 'primary.light' }}>
                <CardContent>
                  <TrendingIcon />
                  <Typography variant="caption" color="text.secondary">Most Popular</Typography>
                  <Typography variant="body2" noWrap>
                    {libraryStats.most_used?.[0]?.template_name || 'N/A'}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}

        {/* Search and Filters */}
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} md={5}>
            <TextField
              fullWidth
              placeholder="Search templates..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>Category</InputLabel>
              <Select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                label="Category"
              >
                <MenuItem value="">All Categories</MenuItem>
                {categories.map((cat) => (
                  <MenuItem key={cat} value={cat}>
                    {cat.replace(/_/g, ' ').toUpperCase()}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <InputLabel>Compliance</InputLabel>
              <Select
                value={selectedCompliance}
                onChange={(e) => setSelectedCompliance(e.target.value)}
                label="Compliance"
              >
                <MenuItem value="">All</MenuItem>
                {complianceTags.map((tag) => (
                  <MenuItem key={tag} value={tag}>
                    {tag}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
        </Grid>

        {/* Tabs */}
        <Tabs value={activeTab} onChange={(e, v) => setActiveTab(v)} sx={{ mb: 3 }}>
          <Tab label="All Templates" />
          <Tab label="Most Used" />
          <Tab label="Compliance" />
        </Tabs>

        {/* Template Grid */}
        <Grid container spacing={2}>
          {filteredTemplates.map((template) => (
            <Grid item xs={12} md={6} lg={4} key={template.template_id}>
              <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <CardContent sx={{ flexGrow: 1 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 1 }}>
                    <Chip
                      icon={getCategoryIcon(template.category)}
                      label={template.category.replace(/_/g, ' ')}
                      color={getCategoryColor(template.category)}
                      size="small"
                    />
                    {template.usage_count > 0 && (
                      <Badge badgeContent={template.usage_count} color="primary">
                        <TrendingIcon fontSize="small" />
                      </Badge>
                    )}
                  </Box>
                  
                  <Typography variant="h6" gutterBottom>
                    {template.template_name}
                  </Typography>
                  
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2, minHeight: 60 }}>
                    {template.description}
                  </Typography>

                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 1 }}>
                    {template.tags.slice(0, 3).map((tag) => (
                      <Chip key={tag} label={tag} size="small" variant="outlined" />
                    ))}
                    {template.tags.length > 3 && (
                      <Chip label={`+${template.tags.length - 3}`} size="small" variant="outlined" />
                    )}
                  </Box>

                  {template.compliance_tags.length > 0 && (
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mt: 1 }}>
                      <ComplianceIcon fontSize="small" color="error" />
                      <Typography variant="caption" color="error">
                        {template.compliance_tags.join(', ')}
                      </Typography>
                    </Box>
                  )}
                </CardContent>
                
                <CardActions>
                  <Button
                    size="small"
                    startIcon={<ViewIcon />}
                    onClick={() => handleViewTemplate(template)}
                  >
                    View
                  </Button>
                  <Button
                    size="small"
                    startIcon={<CopyIcon />}
                    onClick={() => {
                      setSelectedTemplate(template);
                      setCloneDialogOpen(true);
                    }}
                  >
                    Clone
                  </Button>
                  <Button
                    size="small"
                    startIcon={<AddIcon />}
                    onClick={() => {
                      setSelectedTemplate(template);
                      setCreateDialogOpen(true);
                    }}
                  >
                    Use
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>

        {filteredTemplates.length === 0 && (
          <Box sx={{ textAlign: 'center', py: 8 }}>
            <LibraryIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" color="text.secondary">
              No templates found
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Try adjusting your search or filters
            </Typography>
          </Box>
        )}


      {/* View Template Dialog */}
      <Dialog open={viewDialogOpen} onClose={() => setViewDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Template Details</DialogTitle>
        <DialogContent>
          {selectedTemplate && (
            <Box sx={{ pt: 2 }}>
              <Typography variant="h6" gutterBottom>
                {selectedTemplate.template_name}
              </Typography>
              
              <Typography variant="body2" color="text.secondary" paragraph>
                {selectedTemplate.description}
              </Typography>

              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={6}>
                  <Typography variant="caption" color="text.secondary">Category</Typography>
                  <Typography variant="body2">{selectedTemplate.category.replace(/_/g, ' ')}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="caption" color="text.secondary">Usage Count</Typography>
                  <Typography variant="body2">{selectedTemplate.usage_count} times</Typography>
                </Grid>
              </Grid>

              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2" gutterBottom>Tags</Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {selectedTemplate.tags.map((tag) => (
                    <Chip key={tag} label={tag} size="small" />
                  ))}
                </Box>
              </Box>

              {selectedTemplate.compliance_tags.length > 0 && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>Compliance Tags</Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {selectedTemplate.compliance_tags.map((tag) => (
                      <Chip key={tag} label={tag} size="small" color="error" />
                    ))}
                  </Box>
                </Box>
              )}

              <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography variant="subtitle2">Template Structure</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <pre style={{ overflow: 'auto', maxHeight: 400, fontSize: '0.75rem' }}>
                    {JSON.stringify(selectedTemplate.rule_template, null, 2)}
                  </pre>
                </AccordionDetails>
              </Accordion>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setViewDialogOpen(false)}>Close</Button>
          <Button
            variant="outlined"
            startIcon={<CopyIcon />}
            onClick={() => {
              setViewDialogOpen(false);
              setCloneDialogOpen(true);
            }}
          >
            Clone
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => {
              setViewDialogOpen(false);
              setCreateDialogOpen(true);
            }}
          >
            Use Template
          </Button>
        </DialogActions>
      </Dialog>

      {/* Clone Template Dialog */}
      <Dialog open={cloneDialogOpen} onClose={() => setCloneDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Clone Template</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            {selectedTemplate && (
              <Alert severity="info" sx={{ mb: 2 }}>
                Cloning: <strong>{selectedTemplate.template_name}</strong>
              </Alert>
            )}
            
            <TextField
              fullWidth
              label="New Template Name"
              value={cloneName}
              onChange={(e) => setCloneName(e.target.value)}
              sx={{ mb: 2 }}
              required
            />

            <TextField
              fullWidth
              label="Modifications (JSON, Optional)"
              multiline
              rows={4}
              value={cloneModifications}
              onChange={(e) => setCloneModifications(e.target.value)}
              helperText="JSON object with fields to modify"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCloneDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleCloneTemplate}
            disabled={!cloneName || loading}
          >
            Clone Template
          </Button>
        </DialogActions>
      </Dialog>

      {/* Create Ruleset Dialog */}
      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create Ruleset from Template</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            {selectedTemplate && (
              <Alert severity="info" sx={{ mb: 2 }}>
                Using template: <strong>{selectedTemplate.template_name}</strong>
              </Alert>
            )}
            
            <TextField
              fullWidth
              label="Ruleset Name"
              value={rulesetName}
              onChange={(e) => setRulesetName(e.target.value)}
              sx={{ mb: 2 }}
              required
            />

            <TextField
              fullWidth
              label="Entity Type"
              value={entityType}
              onChange={(e) => setEntityType(e.target.value)}
              helperText="e.g., loan_application, customer, account"
              required
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleCreateFromTemplate}
            disabled={!rulesetName || !entityType || loading}
          >
            Create Ruleset
          </Button>
        </DialogActions>
      </Dialog>
      </Paper>
    </Box>
  );
};

export default RuleLibrary;
