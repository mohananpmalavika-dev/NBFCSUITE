/**
 * PTZ Controls Component
 * 
 * Provides pan, tilt, zoom controls for PTZ cameras
 * Features:
 * - Directional controls (up, down, left, right)
 * - Zoom in/out
 * - Preset positions
 * - Speed control
 */

import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  IconButton,
  Slider,
  Button,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Tooltip,
  Alert
} from '@mui/material';
import {
  ArrowUpward,
  ArrowDownward,
  ArrowBack,
  ArrowForward,
  ZoomIn,
  ZoomOut,
  Home,
  Stop,
  Bookmark as PresetIcon
} from '@mui/icons-material';
import monitoringService from '../../../services/monitoringService';

interface PTZControlsProps {
  cameraId: string;
  cameraName: string;
  onError?: (error: string) => void;
}

const PTZControls: React.FC<PTZControlsProps> = ({ cameraId, cameraName, onError }) => {
  const [speed, setSpeed] = useState<number>(50);
  const [selectedPreset, setSelectedPreset] = useState<number>(1);
  const [loading, setLoading] = useState<string | null>(null);
  const [lastAction, setLastAction] = useState<string>('');

  const handlePTZAction = async (
    action: 'pan_left' | 'pan_right' | 'tilt_up' | 'tilt_down' | 'zoom_in' | 'zoom_out' | 'stop' | 'home' | 'go_to_preset' | 'set_preset'
  ) => {
    try {
      setLoading(action);
      const result = await monitoringService.controlPTZ(
        cameraId,
        action,
        speed,
        action.includes('preset') ? selectedPreset : undefined
      );
      setLastAction(`${action} executed at ${new Date(result.timestamp).toLocaleTimeString()}`);
      setLoading(null);
    } catch (error: any) {
      console.error('PTZ control failed:', error);
      setLoading(null);
      if (onError) {
        onError(error.message || 'PTZ control failed');
      }
    }
  };

  const presets = [1, 2, 3, 4, 5, 6, 7, 8];

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          PTZ Control - {cameraName}
        </Typography>

        {lastAction && (
          <Alert severity="success" sx={{ mb: 2 }}>
            {lastAction}
          </Alert>
        )}

        <Grid container spacing={3}>
          {/* Directional Controls */}
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle2" gutterBottom>
              Pan & Tilt
            </Typography>
            <Box
              sx={{
                display: 'grid',
                gridTemplateColumns: 'repeat(3, 1fr)',
                gap: 1,
                maxWidth: 200,
                mx: 'auto'
              }}
            >
              <Box /> {/* Empty cell */}
              <Tooltip title="Tilt Up">
                <IconButton
                  color="primary"
                  onClick={() => handlePTZAction('tilt_up')}
                  disabled={loading !== null}
                  sx={{ 
                    bgcolor: 'primary.light',
                    '&:hover': { bgcolor: 'primary.main' }
                  }}
                >
                  <ArrowUpward />
                </IconButton>
              </Tooltip>
              <Box /> {/* Empty cell */}

              <Tooltip title="Pan Left">
                <IconButton
                  color="primary"
                  onClick={() => handlePTZAction('pan_left')}
                  disabled={loading !== null}
                  sx={{ 
                    bgcolor: 'primary.light',
                    '&:hover': { bgcolor: 'primary.main' }
                  }}
                >
                  <ArrowBack />
                </IconButton>
              </Tooltip>
              <Tooltip title="Stop">
                <IconButton
                  color="error"
                  onClick={() => handlePTZAction('stop')}
                  disabled={loading !== null}
                  sx={{ 
                    bgcolor: 'error.light',
                    '&:hover': { bgcolor: 'error.main' }
                  }}
                >
                  <Stop />
                </IconButton>
              </Tooltip>
              <Tooltip title="Pan Right">
                <IconButton
                  color="primary"
                  onClick={() => handlePTZAction('pan_right')}
                  disabled={loading !== null}
                  sx={{ 
                    bgcolor: 'primary.light',
                    '&:hover': { bgcolor: 'primary.main' }
                  }}
                >
                  <ArrowForward />
                </IconButton>
              </Tooltip>

              <Box /> {/* Empty cell */}
              <Tooltip title="Tilt Down">
                <IconButton
                  color="primary"
                  onClick={() => handlePTZAction('tilt_down')}
                  disabled={loading !== null}
                  sx={{ 
                    bgcolor: 'primary.light',
                    '&:hover': { bgcolor: 'primary.main' }
                  }}
                >
                  <ArrowDownward />
                </IconButton>
              </Tooltip>
              <Box /> {/* Empty cell */}
            </Box>

            {/* Speed Control */}
            <Box sx={{ mt: 3 }}>
              <Typography variant="body2" gutterBottom>
                Speed: {speed}%
              </Typography>
              <Slider
                value={speed}
                onChange={(_, value) => setSpeed(value as number)}
                min={1}
                max={100}
                valueLabelDisplay="auto"
                disabled={loading !== null}
              />
            </Box>
          </Grid>

          {/* Zoom Controls */}
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle2" gutterBottom>
              Zoom Control
            </Typography>
            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', mt: 2 }}>
              <Tooltip title="Zoom In">
                <Button
                  variant="contained"
                  color="primary"
                  onClick={() => handlePTZAction('zoom_in')}
                  disabled={loading !== null}
                  startIcon={<ZoomIn />}
                  size="large"
                >
                  Zoom In
                </Button>
              </Tooltip>
              <Tooltip title="Zoom Out">
                <Button
                  variant="contained"
                  color="primary"
                  onClick={() => handlePTZAction('zoom_out')}
                  disabled={loading !== null}
                  startIcon={<ZoomOut />}
                  size="large"
                >
                  Zoom Out
                </Button>
              </Tooltip>
            </Box>

            {/* Home Position */}
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
              <Tooltip title="Return to Home Position">
                <Button
                  variant="outlined"
                  color="secondary"
                  onClick={() => handlePTZAction('home')}
                  disabled={loading !== null}
                  startIcon={<Home />}
                >
                  Home Position
                </Button>
              </Tooltip>
            </Box>
          </Grid>

          {/* Preset Controls */}
          <Grid item xs={12}>
            <Typography variant="subtitle2" gutterBottom>
              Preset Positions
            </Typography>
            <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap' }}>
              <FormControl sx={{ minWidth: 150 }}>
                <InputLabel>Select Preset</InputLabel>
                <Select
                  value={selectedPreset}
                  label="Select Preset"
                  onChange={(e) => setSelectedPreset(Number(e.target.value))}
                  disabled={loading !== null}
                >
                  {presets.map((preset) => (
                    <MenuItem key={preset} value={preset}>
                      Preset {preset}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              <Tooltip title="Go to selected preset position">
                <Button
                  variant="contained"
                  onClick={() => handlePTZAction('go_to_preset')}
                  disabled={loading !== null}
                  startIcon={<PresetIcon />}
                >
                  Go To Preset
                </Button>
              </Tooltip>

              <Tooltip title="Save current position as preset">
                <Button
                  variant="outlined"
                  onClick={() => handlePTZAction('set_preset')}
                  disabled={loading !== null}
                  startIcon={<PresetIcon />}
                >
                  Set Preset
                </Button>
              </Tooltip>
            </Box>
          </Grid>
        </Grid>

        {/* Instructions */}
        <Alert severity="info" sx={{ mt: 3 }}>
          <Typography variant="body2">
            <strong>PTZ Control Tips:</strong><br />
            • Use directional arrows to pan and tilt the camera<br />
            • Adjust speed slider for finer control<br />
            • Save frequently used positions as presets<br />
            • Click Stop to halt any movement
          </Typography>
        </Alert>
      </CardContent>
    </Card>
  );
};

export default PTZControls;
