/**
 * BPMN Workflow Designer
 * Visual drag-and-drop workflow designer using React Flow
 */

import React, { useState, useCallback, useEffect, useRef } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Connection,
  addEdge,
  useNodesState,
  useEdgesState,
  Controls,
  Background,
  MiniMap,
  Panel,
  ReactFlowProvider,
} from 'reactflow';
import 'reactflow/dist/style.css';
import {
  Box,
  Button,
  IconButton,
  Paper,
  Drawer,
  Typography,
  Stack,
  Divider,
  Alert,
  Snackbar,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Chip,
} from '@mui/material';
import {
  Save as SaveIcon,
  PlayArrow as PlayIcon,
  Visibility as ValidateIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';

import NodePalette from './NodePalette';
import NodeConfigPanel from './NodeConfigPanel';
import EdgeConfigPanel from './EdgeConfigPanel';
import CustomNodes from './CustomNodes';
import workflowService from '../../services/workflowService';

interface WorkflowDesignerProps {
  workflowId?: string;
  onSave?: (workflowId: string) => void;
}

const nodeTypes = CustomNodes;

const WorkflowDesigner: React.FC<WorkflowDesignerProps> = ({
  workflowId,
  onSave,
}) => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [selectedEdge, setSelectedEdge] = useState<Edge | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [workflowName, setWorkflowName] = useState('');
  const [workflowDescription, setWorkflowDescription] = useState('');
  const [category, setCategory] = useState('general');
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' as any });
  const [validationDialog, setValidationDialog] = useState(false);
  const [validationResult, setValidationResult] = useState<any>(null);
  const reactFlowWrapper = useRef<HTMLDivElement>(null);
  const [reactFlowInstance, setReactFlowInstance] = useState<any>(null);

  // Load workflow if editing
  useEffect(() => {
    if (workflowId) {
      loadWorkflow();
    }
  }, [workflowId]);

  const loadWorkflow = async () => {
    try {
      const response = await workflowService.getWorkflow(workflowId!);
      const { workflow, template } = response;
      
      setWorkflowName(workflow.workflow_name);
      setWorkflowDescription(workflow.workflow_description || '');
      setCategory(template.category || 'general');

      // Load canvas
      const canvasResponse = await workflowService.getCanvas(workflowId!);
      const { canvas } = canvasResponse;
      
      setNodes(canvas.nodes || []);
      setEdges(canvas.edges || []);
    } catch (error) {
      console.error('Failed to load workflow:', error);
      showSnackbar('Failed to load workflow', 'error');
    }
  };


  const onConnect = useCallback(
    (params: Connection) => {
      const newEdge = {
        ...params,
        id: `edge-${params.source}-${params.target}-${Date.now()}`,
        type: 'smoothstep',
        animated: false,
      };
      setEdges((eds) => addEdge(newEdge, eds));
    },
    [setEdges]
  );

  const onNodeClick = useCallback((event: React.MouseEvent, node: Node) => {
    setSelectedNode(node);
    setSelectedEdge(null);
    setDrawerOpen(true);
  }, []);

  const onEdgeClick = useCallback((event: React.MouseEvent, edge: Edge) => {
    setSelectedEdge(edge);
    setSelectedNode(null);
    setDrawerOpen(true);
  }, []);

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();

      const reactFlowBounds = reactFlowWrapper.current?.getBoundingClientRect();
      const type = event.dataTransfer.getData('application/reactflow');

      if (typeof type === 'undefined' || !type || !reactFlowInstance) {
        return;
      }

      const position = reactFlowInstance.project({
        x: event.clientX - (reactFlowBounds?.left || 0),
        y: event.clientY - (reactFlowBounds?.top || 0),
      });

      const newNode: Node = {
        id: `${type}-${Date.now()}`,
        type,
        position,
        data: {
          label: `${type.replace('_', ' ')}`,
          description: '',
          config: getDefaultConfig(type),
        },
      };

      setNodes((nds) => nds.concat(newNode));
    },
    [reactFlowInstance, setNodes]
  );

  const getDefaultConfig = (nodeType: string) => {
    switch (nodeType) {
      case 'user_task':
        return {
          assignment_type: 'role',
          assigned_role: '',
          priority: 'normal',
        };
      case 'service_task':
        return {
          implementation: 'api',
          api_method: 'POST',
          retry_enabled: false,
          max_retries: 3,
        };
      case 'script_task':
        return {
          script_format: 'python',
          script: '',
          timeout: 300,
        };
      case 'exclusive_gateway':
      case 'parallel_gateway':
      case 'inclusive_gateway':
        return {
          gateway_type: nodeType.replace('_gateway', ''),
        };
      default:
        return {};
    }
  };

  const deleteSelectedNode = () => {
    if (selectedNode) {
      setNodes((nds) => nds.filter((n) => n.id !== selectedNode.id));
      setEdges((eds) => 
        eds.filter((e) => e.source !== selectedNode.id && e.target !== selectedNode.id)
      );
      setSelectedNode(null);
      setDrawerOpen(false);
    }
  };


  const deleteSelectedEdge = () => {
    if (selectedEdge) {
      setEdges((eds) => eds.filter((e) => e.id !== selectedEdge.id));
      setSelectedEdge(null);
      setDrawerOpen(false);
    }
  };

  const updateNodeData = (nodeId: string, newData: any) => {
    setNodes((nds) =>
      nds.map((node) =>
        node.id === nodeId ? { ...node, data: { ...node.data, ...newData } } : node
      )
    );
  };

  const updateEdgeData = (edgeId: string, newData: any) => {
    setEdges((eds) =>
      eds.map((edge) =>
        edge.id === edgeId ? { ...edge, data: { ...edge.data, ...newData } } : edge
      )
    );
  };

  const saveWorkflow = async () => {
    try {
      // Convert nodes and edges to BPMN format
      const process = convertToBPMN(nodes, edges);

      // Create or update workflow
      if (workflowId) {
        await workflowService.updateWorkflow(workflowId, {
          workflow_name: workflowName,
          workflow_description: workflowDescription,
          category,
          process,
        });
      } else {
        const response = await workflowService.createWorkflow({
          workflow_name: workflowName,
          workflow_description: workflowDescription,
          category,
          process,
        });
        
        if (onSave) {
          onSave(response.workflow_id);
        }
      }

      // Save canvas layout
      const canvas = {
        nodes,
        edges,
        viewport: reactFlowInstance?.getViewport(),
      };
      
      await workflowService.saveCanvas(workflowId || workflowName, canvas);

      showSnackbar('Workflow saved successfully', 'success');
    } catch (error: any) {
      console.error('Failed to save workflow:', error);
      showSnackbar(error.response?.data?.message || 'Failed to save workflow', 'error');
    }
  };

  const validateWorkflow = async () => {
    try {
      if (!workflowId) {
        showSnackbar('Save workflow first before validating', 'warning');
        return;
      }

      const response = await workflowService.validateWorkflow(workflowId);
      setValidationResult(response.validation);
      setValidationDialog(true);
    } catch (error) {
      console.error('Validation failed:', error);
      showSnackbar('Validation failed', 'error');
    }
  };

  const convertToBPMN = (nodes: Node[], edges: Edge[]) => {
    const process: any = {
      id: workflowId || `process_${Date.now()}`,
      name: workflowName,
      version: '1.0',
      is_executable: true,
      start_events: [],
      end_events: [],
      user_tasks: [],
      service_tasks: [],
      script_tasks: [],
      send_tasks: [],
      gateways: [],
      intermediate_events: [],
      sequence_flows: [],
    };

    // Convert nodes
    nodes.forEach((node) => {
      const bpmnNode = {
        id: node.id,
        name: node.data.label,
        type: node.type,
        description: node.data.description,
        position: node.position,
        config: node.data.config,
      };

      if (node.type?.startsWith('start_')) {
        process.start_events.push(bpmnNode);
      } else if (node.type?.startsWith('end_')) {
        process.end_events.push(bpmnNode);
      } else if (node.type === 'user_task') {
        process.user_tasks.push(bpmnNode);
      } else if (node.type === 'service_task') {
        process.service_tasks.push(bpmnNode);
      } else if (node.type === 'script_task') {
        process.script_tasks.push(bpmnNode);
      } else if (node.type === 'send_task') {
        process.send_tasks.push(bpmnNode);
      } else if (node.type?.includes('gateway')) {
        process.gateways.push(bpmnNode);
      }
    });

    // Convert edges
    process.sequence_flows = edges.map((edge) => ({
      id: edge.id,
      name: edge.label,
      source_ref: edge.source,
      target_ref: edge.target,
      condition: edge.data?.condition,
    }));

    return process;
  };

  const showSnackbar = (message: string, severity: 'success' | 'error' | 'warning' = 'success') => {
    setSnackbar({ open: true, message, severity });
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };


  return (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Toolbar */}
      <Paper sx={{ p: 2, borderRadius: 0 }}>
        <Stack direction="row" spacing={2} alignItems="center">
          <TextField
            size="small"
            label="Workflow Name"
            value={workflowName}
            onChange={(e) => setWorkflowName(e.target.value)}
            sx={{ width: 300 }}
          />
          <TextField
            size="small"
            label="Category"
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            sx={{ width: 150 }}
          />
          <Box sx={{ flexGrow: 1 }} />
          <Button
            startIcon={<ValidateIcon />}
            onClick={validateWorkflow}
            variant="outlined"
          >
            Validate
          </Button>
          <Button
            startIcon={<SaveIcon />}
            onClick={saveWorkflow}
            variant="contained"
            disabled={!workflowName}
          >
            Save
          </Button>
        </Stack>
      </Paper>

      {/* Main Content */}
      <Box sx={{ display: 'flex', flexGrow: 1, overflow: 'hidden' }}>
        {/* Node Palette */}
        <NodePalette />

        {/* Canvas */}
        <Box ref={reactFlowWrapper} sx={{ flexGrow: 1, position: 'relative' }}>
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onNodeClick={onNodeClick}
            onEdgeClick={onEdgeClick}
            onInit={setReactFlowInstance}
            onDrop={onDrop}
            onDragOver={onDragOver}
            nodeTypes={nodeTypes}
            fitView
          >
            <Background />
            <Controls />
            <MiniMap />
            <Panel position="top-right">
              <Paper sx={{ p: 1 }}>
                <Typography variant="caption" color="textSecondary">
                  Nodes: {nodes.length} | Edges: {edges.length}
                </Typography>
              </Paper>
            </Panel>
          </ReactFlow>
        </Box>

        {/* Configuration Panel */}
        <Drawer
          anchor="right"
          open={drawerOpen}
          onClose={() => setDrawerOpen(false)}
          sx={{
            '& .MuiDrawer-paper': {
              width: 400,
              p: 2,
            },
          }}
        >
          {selectedNode && (
            <>
              <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6">Node Configuration</Typography>
                <IconButton onClick={deleteSelectedNode} color="error" size="small">
                  <DeleteIcon />
                </IconButton>
              </Stack>
              <Divider sx={{ mb: 2 }} />
              <NodeConfigPanel
                node={selectedNode}
                onUpdate={(data) => updateNodeData(selectedNode.id, data)}
              />
            </>
          )}

          {selectedEdge && (
            <>
              <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6">Connection Configuration</Typography>
                <IconButton onClick={deleteSelectedEdge} color="error" size="small">
                  <DeleteIcon />
                </IconButton>
              </Stack>
              <Divider sx={{ mb: 2 }} />
              <EdgeConfigPanel
                edge={selectedEdge}
                onUpdate={(data) => updateEdgeData(selectedEdge.id, data)}
              />
            </>
          )}
        </Drawer>
      </Box>

      {/* Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert onClose={handleCloseSnackbar} severity={snackbar.severity}>
          {snackbar.message}
        </Alert>
      </Snackbar>

      {/* Validation Dialog */}
      <Dialog
        open={validationDialog}
        onClose={() => setValidationDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Workflow Validation</DialogTitle>
        <DialogContent>
          {validationResult && (
            <Stack spacing={2}>
              <Alert severity={validationResult.valid ? 'success' : 'error'}>
                {validationResult.valid
                  ? 'Workflow is valid!'
                  : 'Workflow has errors'}
              </Alert>

              {validationResult.errors && validationResult.errors.length > 0 && (
                <Box>
                  <Typography variant="subtitle2" color="error" gutterBottom>
                    Errors:
                  </Typography>
                  {validationResult.errors.map((error: string, index: number) => (
                    <Chip
                      key={index}
                      label={error}
                      color="error"
                      size="small"
                      sx={{ m: 0.5 }}
                    />
                  ))}
                </Box>
              )}

              {validationResult.warnings && validationResult.warnings.length > 0 && (
                <Box>
                  <Typography variant="subtitle2" color="warning.main" gutterBottom>
                    Warnings:
                  </Typography>
                  {validationResult.warnings.map((warning: string, index: number) => (
                    <Chip
                      key={index}
                      label={warning}
                      color="warning"
                      size="small"
                      sx={{ m: 0.5 }}
                    />
                  ))}
                </Box>
              )}
            </Stack>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setValidationDialog(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default function WorkflowDesignerWrapper(props: WorkflowDesignerProps) {
  return (
    <ReactFlowProvider>
      <WorkflowDesigner {...props} />
    </ReactFlowProvider>
  );
}
