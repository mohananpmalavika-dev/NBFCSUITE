/**
 * Node Palette
 * Drag-and-drop palette of available BPMN nodes
 */

import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Stack,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Tooltip,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  PlayCircleOutline,
  StopCircleOutlined,
  Person,
  Api,
  Code,
  Send,
  CallSplit,
  AccountTree,
  Timer,
} from '@mui/icons-material';

interface NodeTypeItem {
  type: string;
  label: string;
  icon: React.ReactNode;
  description: string;
  color: string;
}

const nodeCategories = {
  events: [
    {
      type: 'start_none',
      label: 'Start',
      icon: <PlayCircleOutline />,
      description: 'Workflow start point',
      color: '#4caf50',
    },
    {
      type: 'end_none',
      label: 'End',
      icon: <StopCircleOutlined />,
      description: 'Workflow end point',
      color: '#f44336',
    },
  ],
  tasks: [
    {
      type: 'user_task',
      label: 'User Task',
      icon: <Person />,
      description: 'Manual task requiring user action',
      color: '#2196f3',
    },
    {
      type: 'service_task',
      label: 'Service Task',
      icon: <Api />,
      description: 'Automated API call or service',
      color: '#9c27b0',
    },
    {
      type: 'script_task',
      label: 'Script Task',
      icon: <Code />,
      description: 'Execute custom script',
      color: '#ff9800',
    },
    {
      type: 'send_task',
      label: 'Send Task',
      icon: <Send />,
      description: 'Send email, SMS, or notification',
      color: '#00bcd4',
    },
  ],
  gateways: [
    {
      type: 'exclusive_gateway',
      label: 'Exclusive (XOR)',
      icon: <CallSplit />,
      description: 'Take ONE path based on condition',
      color: '#ffc107',
    },
    {
      type: 'parallel_gateway',
      label: 'Parallel (AND)',
      icon: <AccountTree />,
      description: 'Execute ALL paths simultaneously',
      color: '#ffc107',
    },
    {
      type: 'inclusive_gateway',
      label: 'Inclusive (OR)',
      icon: <CallSplit style={{ transform: 'rotate(90deg)' }} />,
      description: 'Execute MULTIPLE matching paths',
      color: '#ffc107',
    },
  ],
};

const NodePalette: React.FC = () => {
  const onDragStart = (event: React.DragEvent, nodeType: string) => {
    event.dataTransfer.setData('application/reactflow', nodeType);
    event.dataTransfer.effectAllowed = 'move';
  };

  const renderNodeItem = (item: NodeTypeItem) => (
    <Tooltip key={item.type} title={item.description} placement="right">
      <Paper
        sx={{
          p: 1.5,
          cursor: 'grab',
          display: 'flex',
          alignItems: 'center',
          gap: 1,
          '&:hover': {
            bgcolor: 'action.hover',
          },
          borderLeft: `4px solid ${item.color}`,
        }}
        draggable
        onDragStart={(e) => onDragStart(e, item.type)}
      >
        <Box sx={{ color: item.color }}>{item.icon}</Box>
        <Typography variant="body2">{item.label}</Typography>
      </Paper>
    </Tooltip>
  );

  return (
    <Paper
      sx={{
        width: 250,
        height: '100%',
        overflowY: 'auto',
        borderRadius: 0,
      }}
    >
      <Box sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>
          BPMN Nodes
        </Typography>
        <Typography variant="caption" color="textSecondary">
          Drag to canvas
        </Typography>
      </Box>

      <Accordion defaultExpanded>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="subtitle2">Events</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Stack spacing={1}>
            {nodeCategories.events.map(renderNodeItem)}
          </Stack>
        </AccordionDetails>
      </Accordion>

      <Accordion defaultExpanded>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="subtitle2">Tasks</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Stack spacing={1}>
            {nodeCategories.tasks.map(renderNodeItem)}
          </Stack>
        </AccordionDetails>
      </Accordion>

      <Accordion defaultExpanded>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="subtitle2">Gateways</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Stack spacing={1}>
            {nodeCategories.gateways.map(renderNodeItem)}
          </Stack>
        </AccordionDetails>
      </Accordion>
    </Paper>
  );
};

export default NodePalette;
