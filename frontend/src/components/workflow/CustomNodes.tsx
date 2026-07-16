/**
 * Custom BPMN Node Components
 * Visual representations of different BPMN node types
 */

import React, { memo } from 'react';
import { Handle, Position, NodeProps } from 'reactflow';
import { Box, Typography, Paper } from '@mui/material';
import {
  PlayCircleOutline,
  StopCircleOutlined,
  Person,
  Api,
  Code,
  Send,
  CallSplit,
  AccountTree,
} from '@mui/icons-material';

// Base Node Component
const BaseNode: React.FC<NodeProps & { icon: React.ReactNode; color: string; shape?: 'circle' | 'rect' | 'diamond' }> = ({
  data,
  icon,
  color,
  shape = 'rect',
  selected,
}) => {
  const getShapeStyles = () => {
    switch (shape) {
      case 'circle':
        return {
          borderRadius: '50%',
          width: 60,
          height: 60,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        };
      case 'diamond':
        return {
          width: 80,
          height: 80,
          transform: 'rotate(45deg)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        };
      default:
        return {
          borderRadius: 1,
          minWidth: 120,
          p: 2,
        };
    }
  };

  return (
    <Box>
      <Paper
        elevation={selected ? 8 : 2}
        sx={{
          ...getShapeStyles(),
          borderLeft: `4px solid ${color}`,
          bgcolor: 'background.paper',
          border: selected ? `2px solid ${color}` : '1px solid #ddd',
        }}
      >
        {shape === 'diamond' ? (
          <Box sx={{ transform: 'rotate(-45deg)' }}>
            <Box sx={{ color }}>{icon}</Box>
          </Box>
        ) : (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Box sx={{ color }}>{icon}</Box>
            {shape !== 'circle' && (
              <Box sx={{ flexGrow: 1 }}>
                <Typography variant="body2" fontWeight="bold">
                  {data.label}
                </Typography>
                {data.description && (
                  <Typography variant="caption" color="textSecondary" noWrap>
                    {data.description}
                  </Typography>
                )}
              </Box>
            )}
          </Box>
        )}
      </Paper>
      
      {/* Handles */}
      {!shape.includes('start') && (
        <Handle
          type="target"
          position={Position.Top}
          style={{ background: color }}
        />
      )}
      {!shape.includes('end') && (
        <Handle
          type="source"
          position={Position.Bottom}
          style={{ background: color }}
        />
      )}
    </Box>
  );
};

// Start Event Node
export const StartNoneNode = memo((props: NodeProps) => (
  <BaseNode {...props} icon={<PlayCircleOutline />} color="#4caf50" shape="circle" />
));

// End Event Node
export const EndNoneNode = memo((props: NodeProps) => (
  <BaseNode {...props} icon={<StopCircleOutlined />} color="#f44336" shape="circle" />
));

// User Task Node
export const UserTaskNode = memo((props: NodeProps) => (
  <BaseNode {...props} icon={<Person />} color="#2196f3" />
));

// Service Task Node
export const ServiceTaskNode = memo((props: NodeProps) => (
  <BaseNode {...props} icon={<Api />} color="#9c27b0" />
));

// Script Task Node
export const ScriptTaskNode = memo((props: NodeProps) => (
  <BaseNode {...props} icon={<Code />} color="#ff9800" />
));

// Send Task Node
export const SendTaskNode = memo((props: NodeProps) => (
  <BaseNode {...props} icon={<Send />} color="#00bcd4" />
));

// Exclusive Gateway Node
export const ExclusiveGatewayNode = memo((props: NodeProps) => (
  <BaseNode {...props} icon={<CallSplit />} color="#ffc107" shape="diamond" />
));

// Parallel Gateway Node
export const ParallelGatewayNode = memo((props: NodeProps) => (
  <BaseNode {...props} icon={<AccountTree />} color="#ffc107" shape="diamond" />
));

// Inclusive Gateway Node
export const InclusiveGatewayNode = memo((props: NodeProps) => (
  <BaseNode {...props} icon={<CallSplit style={{ transform: 'rotate(90deg)' }} />} color="#ffc107" shape="diamond" />
));

// Export all custom nodes
const CustomNodes = {
  start_none: StartNoneNode,
  end_none: EndNoneNode,
  user_task: UserTaskNode,
  service_task: ServiceTaskNode,
  script_task: ScriptTaskNode,
  send_task: SendTaskNode,
  exclusive_gateway: ExclusiveGatewayNode,
  parallel_gateway: ParallelGatewayNode,
  inclusive_gateway: InclusiveGatewayNode,
};

export default CustomNodes;
