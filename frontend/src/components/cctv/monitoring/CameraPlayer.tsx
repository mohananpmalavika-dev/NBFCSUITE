/**
 * Camera Player Component
 * 
 * Fullscreen single camera view with controls
 * Features:
 * - Fullscreen video playback
 * - Quality selection
 * - PTZ controls (if supported)
 * - Audio toggle
 * - Quick bookmarking
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  IconButton,
  Typography,
  Chip,
  Select,
  MenuItem,
  FormControl,
  Tooltip,
  Paper,
  CircularProgress,
  Alert
} from '@mui/material';
import {
  Close,
  VolumeUp,
  VolumeOff,
  Bookmark,
  AspectRatio,
  Settings,
  Fullscreen,
  FullscreenExit
} from '@mui/icons-material';
import monitoringService, { LiveCamera, StreamInfo } from '../../../services/monitoringService';
import PTZControls from './PTZControls';

interface CameraPlayerProps {
  camera: LiveCamera;
  onClose: () => void;
  onBookmark?: (camera: LiveCamera) => void;
}

const CameraPlayer: React.FC<CameraPlayerProps> = ({ camera, onClose, onBookmark }) => {
  const [streamInfo, setStreamInfo] = useState<StreamInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [quality, setQuality] = useState<'low' | 'medium' | 'high' | 'ultra'>('high');
  const [audioEnabled, setAudioEnabled] = useState(camera.audio_recording_enabled);
  const [showPTZ, setShowPTZ] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadStreamInfo();
  }, [camera.id, quality]);

  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };

    document.addEventListener('fullscreenchange', handleFullscreenChange);
    return () => document.removeEventListener('fullscreenchange', handleFullscreenChange);
  }, []);

  const loadStreamInfo = async () => {
    try {
      setLoading(true);
      setError(null);
      const stream = await monitoringService.getStreamUrl(camera.id, quality);
      setStreamInfo(stream);
      setLoading(false);
    } catch (err: any) {
      console.error('Failed to load stream:', err);
      setError(err.message || 'Failed to load camera stream');
      setLoading(false);
    }
  };

  const toggleAudio = async () => {
    try {
      await monitoringService.toggleAudioMonitoring(camera.id, !audioEnabled);
      setAudioEnabled(!audioEnabled);
    } catch (error) {
      console.error('Failed to toggle audio:', error);
    }
  };

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen();
    } else {
      document.exitFullscreen();
    }
  };

  return (
    <Box
      sx={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        bgcolor: 'black',
        zIndex: 9999,
        display: 'flex',
        flexDirection: 'column'
      }}
    >
      {/* Top Control Bar */}
      <Paper
        sx={{
          bgcolor: 'rgba(0,0,0,0.8)',
          color: 'white',
          p: 1,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}
        elevation={0}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Typography variant="h6">
            {camera.camera_name}
          </Typography>
          <Chip
            label={camera.location_type}
            size="small"
            sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}
          />
          <Chip
            label={camera.status}
            size="small"
            color={camera.status === 'online' ? 'success' : 'error'}
          />
          {camera.is_critical && (
            <Chip label="CRITICAL" size="small" color="error" />
          )}
        </Box>

        <Box sx={{ display: 'flex', gap: 1 }}>
          {streamInfo && (
            <Chip
              label={`${streamInfo.resolution} @ ${streamInfo.frame_rate}fps`}
              size="small"
              sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}
            />
          )}

          <Tooltip title="Settings">
            <IconButton
              onClick={() => setShowSettings(!showSettings)}
              sx={{ color: 'white' }}
            >
              <Settings />
            </IconButton>
          </Tooltip>

          <Tooltip title={isFullscreen ? 'Exit Fullscreen' : 'Fullscreen'}>
            <IconButton onClick={toggleFullscreen} sx={{ color: 'white' }}>
              {isFullscreen ? <FullscreenExit /> : <Fullscreen />}
            </IconButton>
          </Tooltip>

          <Tooltip title="Close">
            <IconButton onClick={onClose} sx={{ color: 'white' }}>
              <Close />
            </IconButton>
          </Tooltip>
        </Box>
      </Paper>

      {/* Settings Panel */}
      {showSettings && (
        <Paper
          sx={{
            position: 'absolute',
            top: 60,
            right: 10,
            p: 2,
            bgcolor: 'rgba(0,0,0,0.9)',
            color: 'white',
            minWidth: 250,
            zIndex: 10
          }}
        >
          <Typography variant="subtitle2" gutterBottom>
            Stream Quality
          </Typography>
          <FormControl fullWidth size="small" sx={{ mb: 2 }}>
            <Select
              value={quality}
              onChange={(e) => setQuality(e.target.value as any)}
              sx={{ color: 'white', '.MuiOutlinedInput-notchedOutline': { borderColor: 'white' } }}
            >
              <MenuItem value="low">Low (512 kbps)</MenuItem>
              <MenuItem value="medium">Medium (1 Mbps)</MenuItem>
              <MenuItem value="high">High (2 Mbps)</MenuItem>
              <MenuItem value="ultra">Ultra (4 Mbps)</MenuItem>
            </Select>
          </FormControl>

          <Typography variant="caption" display="block" color="grey.400">
            Camera ID: {camera.camera_id}<br />
            IP: {camera.specifications?.ip_address || 'N/A'}<br />
            Type: {camera.camera_type}
          </Typography>
        </Paper>
      )}

      {/* Main Video Area */}
      <Box
        sx={{
          flex: 1,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          position: 'relative'
        }}
      >
        {loading ? (
          <CircularProgress sx={{ color: 'white' }} />
        ) : error ? (
          <Alert severity="error" sx={{ maxWidth: 500 }}>
            {error}
          </Alert>
        ) : (
          <Box
            sx={{
              width: '100%',
              height: '100%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              bgcolor: 'black'
            }}
          >
            {/* Video Player Placeholder */}
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h1" sx={{ color: 'grey.700', mb: 2 }}>
                📹
              </Typography>
              <Typography variant="h6" sx={{ color: 'grey.600', mb: 1 }}>
                Live Stream
              </Typography>
              <Typography variant="body2" sx={{ color: 'grey.700' }}>
                Stream URL: {streamInfo?.stream_url}
              </Typography>
              <Typography variant="caption" sx={{ color: 'grey.700', display: 'block', mt: 1 }}>
                In production, this would display the RTSP/WebRTC video stream
              </Typography>
            </Box>
          </Box>
        )}

        {/* Overlay Controls */}
        <Box
          sx={{
            position: 'absolute',
            bottom: 20,
            left: '50%',
            transform: 'translateX(-50%)',
            display: 'flex',
            gap: 1,
            bgcolor: 'rgba(0,0,0,0.7)',
            p: 1,
            borderRadius: 2
          }}
        >
          {camera.audio_recording_enabled && (
            <Tooltip title={audioEnabled ? 'Mute Audio' : 'Unmute Audio'}>
              <IconButton onClick={toggleAudio} sx={{ color: 'white' }}>
                {audioEnabled ? <VolumeUp /> : <VolumeOff />}
              </IconButton>
            </Tooltip>
          )}

          <Tooltip title="Bookmark Event">
            <IconButton
              onClick={() => onBookmark && onBookmark(camera)}
              sx={{ color: 'white' }}
            >
              <Bookmark />
            </IconButton>
          </Tooltip>

          {camera.camera_type === 'ptz' && (
            <Tooltip title="PTZ Controls">
              <IconButton
                onClick={() => setShowPTZ(!showPTZ)}
                sx={{ color: 'white' }}
              >
                <AspectRatio />
              </IconButton>
            </Tooltip>
          )}
        </Box>

        {/* PTZ Controls Panel */}
        {showPTZ && camera.camera_type === 'ptz' && (
          <Box
            sx={{
              position: 'absolute',
              bottom: 80,
              right: 20,
              maxWidth: 400,
              bgcolor: 'rgba(0,0,0,0.95)',
              borderRadius: 2,
              overflow: 'hidden'
            }}
          >
            <PTZControls
              cameraId={camera.id}
              cameraName={camera.camera_name}
              onError={(err) => setError(err)}
            />
          </Box>
        )}
      </Box>

      {/* Camera Info Bar */}
      <Paper
        sx={{
          bgcolor: 'rgba(0,0,0,0.8)',
          color: 'white',
          p: 1,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}
        elevation={0}
      >
        <Typography variant="body2">
          {camera.location_description}
        </Typography>
        <Typography variant="caption" color="grey.400">
          {new Date().toLocaleTimeString()}
        </Typography>
      </Paper>
    </Box>
  );
};

export default CameraPlayer;
