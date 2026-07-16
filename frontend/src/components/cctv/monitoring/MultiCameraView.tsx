/**
 * Multi-Camera View Component
 * 
 * Grid layout for viewing multiple cameras simultaneously
 * Features:
 * - Flexible grid layouts (2x2, 3x3, 4x4)
 * - Camera selection
 * - Quick actions per camera
 * - Auto-cycling through cameras
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  IconButton,
  Grid,
  Chip,
  Tooltip,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Button,
  CircularProgress
} from '@mui/material';
import {
  Videocam,
  Fullscreen,
  VolumeUp,
  VolumeOff,
  Bookmark,
  PlayArrow,
  Stop,
  AspectRatio
} from '@mui/icons-material';
import monitoringService, { LiveCamera, StreamInfo } from '../../../services/monitoringService';

interface MultiCameraViewProps {
  branchId?: string;
  locationType?: string;
  onCameraSelect?: (camera: LiveCamera) => void;
  onFullscreen?: (cameraId: string) => void;
}

const MultiCameraView: React.FC<MultiCameraViewProps> = ({
  branchId,
  locationType,
  onCameraSelect,
  onFullscreen
}) => {
  const [cameras, setCameras] = useState<LiveCamera[]>([]);
  const [loading, setLoading] = useState(true);
  const [gridLayout, setGridLayout] = useState<number>(4); // 4, 9, 16
  const [selectedCameraId, setSelectedCameraId] = useState<string | null>(null);
  const [streamInfo, setStreamInfo] = useState<Record<string, StreamInfo>>({});
  const [quality, setQuality] = useState<'low' | 'medium' | 'high' | 'ultra'>('high');
  const [autoCycle, setAutoCycle] = useState(false);
  const [cycleInterval, setCycleInterval] = useState(10); // seconds
  const [currentPage, setCurrentPage] = useState(0);

  useEffect(() => {
    loadCameras();
  }, [branchId, locationType]);

  useEffect(() => {
    if (autoCycle && cameras.length > gridLayout) {
      const interval = setInterval(() => {
        setCurrentPage((prev) => {
          const maxPages = Math.ceil(cameras.length / gridLayout);
          return (prev + 1) % maxPages;
        });
      }, cycleInterval * 1000);

      return () => clearInterval(interval);
    }
  }, [autoCycle, cameras.length, gridLayout, cycleInterval]);

  const loadCameras = async () => {
    try {
      setLoading(true);
      const data = await monitoringService.getLiveCameras({
        branch_id: branchId,
        location_type: locationType,
        page: 1,
        page_size: 100
      });
      setCameras(data.cameras);
      setLoading(false);
    } catch (error) {
      console.error('Failed to load cameras:', error);
      setLoading(false);
    }
  };

  const loadStreamInfo = async (cameraId: string) => {
    try {
      const stream = await monitoringService.getStreamUrl(cameraId, quality);
      setStreamInfo(prev => ({ ...prev, [cameraId]: stream }));
    } catch (error) {
      console.error('Failed to load stream info:', error);
    }
  };

  const handleCameraClick = (camera: LiveCamera) => {
    setSelectedCameraId(camera.id);
    if (onCameraSelect) {
      onCameraSelect(camera);
    }
    // Load stream info on demand
    if (!streamInfo[camera.id]) {
      loadStreamInfo(camera.id);
    }
  };

  const handleFullscreen = (cameraId: string) => {
    if (onFullscreen) {
      onFullscreen(cameraId);
    }
  };

  const toggleAudio = async (camera: LiveCamera) => {
    try {
      await monitoringService.toggleAudioMonitoring(
        camera.id,
        !camera.audio_recording_enabled
      );
      // Reload cameras to get updated state
      loadCameras();
    } catch (error) {
      console.error('Failed to toggle audio:', error);
    }
  };

  const getGridColumns = () => {
    switch (gridLayout) {
      case 4: return 2;
      case 9: return 3;
      case 16: return 4;
      default: return 2;
    }
  };

  const displayedCameras = cameras.slice(
    currentPage * gridLayout,
    (currentPage + 1) * gridLayout
  );

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      {/* Controls */}
      <Box sx={{ mb: 2, display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap' }}>
        <FormControl size="small" sx={{ minWidth: 150 }}>
          <InputLabel>Grid Layout</InputLabel>
          <Select
            value={gridLayout}
            label="Grid Layout"
            onChange={(e) => setGridLayout(Number(e.target.value))}
          >
            <MenuItem value={4}>2x2 (4 cameras)</MenuItem>
            <MenuItem value={9}>3x3 (9 cameras)</MenuItem>
            <MenuItem value={16}>4x4 (16 cameras)</MenuItem>
          </Select>
        </FormControl>

        <FormControl size="small" sx={{ minWidth: 150 }}>
          <InputLabel>Quality</InputLabel>
          <Select
            value={quality}
            label="Quality"
            onChange={(e) => setQuality(e.target.value as any)}
          >
            <MenuItem value="low">Low (512 kbps)</MenuItem>
            <MenuItem value="medium">Medium (1 Mbps)</MenuItem>
            <MenuItem value="high">High (2 Mbps)</MenuItem>
            <MenuItem value="ultra">Ultra (4 Mbps)</MenuItem>
          </Select>
        </FormControl>

        {cameras.length > gridLayout && (
          <>
            <Button
              variant={autoCycle ? 'contained' : 'outlined'}
              startIcon={autoCycle ? <Stop /> : <PlayArrow />}
              onClick={() => setAutoCycle(!autoCycle)}
            >
              {autoCycle ? 'Stop' : 'Start'} Auto-Cycle
            </Button>

            {autoCycle && (
              <FormControl size="small" sx={{ minWidth: 120 }}>
                <InputLabel>Interval</InputLabel>
                <Select
                  value={cycleInterval}
                  label="Interval"
                  onChange={(e) => setCycleInterval(Number(e.target.value))}
                >
                  <MenuItem value={5}>5 seconds</MenuItem>
                  <MenuItem value={10}>10 seconds</MenuItem>
                  <MenuItem value={15}>15 seconds</MenuItem>
                  <MenuItem value={30}>30 seconds</MenuItem>
                </Select>
              </FormControl>
            )}

            <Typography variant="body2" color="textSecondary">
              Page {currentPage + 1} of {Math.ceil(cameras.length / gridLayout)}
            </Typography>
          </>
        )}
      </Box>

      {/* Camera Grid */}
      <Grid container spacing={2}>
        {displayedCameras.map((camera) => (
          <Grid item xs={12} sm={6} md={12 / getGridColumns()} key={camera.id}>
            <Card
              sx={{
                cursor: 'pointer',
                border: selectedCameraId === camera.id ? '2px solid' : 'none',
                borderColor: 'primary.main',
                transition: 'all 0.3s'
              }}
              onClick={() => handleCameraClick(camera)}
            >
              <CardContent sx={{ p: 1 }}>
                {/* Header */}
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                  <Typography variant="caption" fontWeight="bold" noWrap>
                    {camera.camera_name}
                  </Typography>
                  <Chip
                    label={camera.status}
                    size="small"
                    color={camera.status === 'online' ? 'success' : 'error'}
                  />
                </Box>

                {/* Video Feed Placeholder */}
                <Box
                  sx={{
                    bgcolor: 'black',
                    aspectRatio: '16/9',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    position: 'relative',
                    mb: 1
                  }}
                >
                  <Videocam sx={{ fontSize: 40, color: 'grey.600' }} />
                  
                  {/* Status Overlays */}
                  {camera.is_critical && (
                    <Chip
                      label="CRITICAL"
                      color="error"
                      size="small"
                      sx={{ position: 'absolute', top: 4, left: 4, fontSize: '0.65rem' }}
                    />
                  )}
                  
                  {streamInfo[camera.id] && (
                    <Chip
                      label={streamInfo[camera.id].resolution}
                      size="small"
                      sx={{ position: 'absolute', top: 4, right: 4, fontSize: '0.65rem' }}
                    />
                  )}

                  {/* Action Buttons Overlay */}
                  <Box
                    sx={{
                      position: 'absolute',
                      bottom: 4,
                      right: 4,
                      display: 'flex',
                      gap: 0.5,
                      opacity: 0.8,
                      '&:hover': { opacity: 1 }
                    }}
                  >
                    <Tooltip title="Fullscreen">
                      <IconButton
                        size="small"
                        sx={{ bgcolor: 'rgba(0,0,0,0.6)', color: 'white' }}
                        onClick={(e) => {
                          e.stopPropagation();
                          handleFullscreen(camera.id);
                        }}
                      >
                        <Fullscreen fontSize="small" />
                      </IconButton>
                    </Tooltip>

                    {camera.audio_recording_enabled && (
                      <Tooltip title="Audio On/Off">
                        <IconButton
                          size="small"
                          sx={{ bgcolor: 'rgba(0,0,0,0.6)', color: 'white' }}
                          onClick={(e) => {
                            e.stopPropagation();
                            toggleAudio(camera);
                          }}
                        >
                          {camera.audio_recording_enabled ? (
                            <VolumeUp fontSize="small" />
                          ) : (
                            <VolumeOff fontSize="small" />
                          )}
                        </IconButton>
                      </Tooltip>
                    )}

                    {camera.camera_type === 'ptz' && (
                      <Tooltip title="PTZ Control">
                        <IconButton
                          size="small"
                          sx={{ bgcolor: 'rgba(0,0,0,0.6)', color: 'white' }}
                        >
                          <AspectRatio fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    )}
                  </Box>
                </Box>

                {/* Footer */}
                <Typography variant="caption" color="textSecondary" display="block" noWrap>
                  {camera.location_type} - {camera.location_description}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* No Cameras Message */}
      {cameras.length === 0 && (
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <Typography color="textSecondary">
            No cameras available for monitoring
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default MultiCameraView;
