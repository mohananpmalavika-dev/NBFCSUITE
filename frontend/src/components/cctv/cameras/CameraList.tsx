/**
 * Camera List Component
 * 
 * Displays all CCTV cameras with filtering, sorting, and actions
 * Features:
 * - Table/Grid view toggle
 * - Advanced filtering (type, location, status)
 * - Search by name/IP
 * - Status indicators
 * - Quick actions (edit, delete, test, health)
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  IconButton,
  TextField,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Tooltip,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  ToggleButtonGroup,
  ToggleButton
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Videocam,
  Search,
  Refresh,
  ViewList,
  ViewModule,
  CheckCircle,
  Error,
  Warning,
  Settings,
  WifiTethering
} from '@mui/icons-material';
import cameraService, { CCTVCamera } from '../../../services/cameraService';

const CameraList: React.FC = () => {
  const [cameras, setCameras] = useState<CCTVCamera[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [totalCameras, setTotalCameras] = useState(0);
  const [viewMode, setViewMode] = useState<'table' | 'grid'>('table');
  
  // Filters
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [filterLocation, setFilterLocation] = useState('all');
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterCritical, setFilterCritical] = useState('all');

  // Dialog states
  const [deleteDialog, setDeleteDialog] = useState(false);
  const [selectedCamera, setSelectedCamera] = useState<CCTVCamera | null>(null);

  useEffect(() => {
    loadCameras();
  }, [page, rowsPerPage, filterType, filterLocation, filterStatus, filterCritical]);

  const loadCameras = async () => {
    try {
      setLoading(true);
      const data = await cameraService.listCameras({
        camera_type: filterType !== 'all' ? filterType : undefined,
        location_type: filterLocation !== 'all' ? filterLocation : undefined,
        status: filterStatus !== 'all' ? filterStatus : undefined,
        is_critical: filterCritical !== 'all' ? filterCritical === 'yes' : undefined,
        page: page + 1,
        page_size: rowsPerPage
      });
      
      setCameras(data.cameras);
      setTotalCameras(data.total);
      setLoading(false);
    } catch (error) {
      console.error('Failed to load cameras:', error);
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!selectedCamera) return;
    
    try {
      await cameraService.deleteCamera(selectedCamera.id);
      setDeleteDialog(false);
      setSelectedCamera(null);
      loadCameras();
    } catch (error) {
      console.error('Failed to delete camera:', error);
      alert('Failed to delete camera');
    }
  };

  const handleTestConnectivity = async (camera: CCTVCamera) => {
    try {
      const result = await cameraService.testConnectivity(camera.id);
      alert(`Connectivity Test:\n\n${result.connectivity === 'success' ? '✅ Success' : '❌ Failed'}\n\nPing: ${result.ping_response_ms}ms\nRTSP: ${result.rtsp_stream}\nONVIF: ${result.onvif_status}`);
    } catch (error) {
      console.error('Connectivity test failed:', error);
      alert('Connectivity test failed');
    }
  };

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'online':
        return <CheckCircle color="success" />;
      case 'offline':
        return <Error color="error" />;
      case 'maintenance':
        return <Warning color="warning" />;
      case 'faulty':
        return <Error color="error" />;
      default:
        return <Videocam />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online':
        return 'success';
      case 'offline':
        return 'error';
      case 'maintenance':
        return 'warning';
      case 'faulty':
        return 'error';
      default:
        return 'default';
    }
  };

  const filteredCameras = cameras.filter(camera => 
    searchTerm === '' || 
    camera.camera_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    camera.camera_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    camera.ip_address.includes(searchTerm)
  );

  return (
    <Box>
      <Card>
        <CardContent>
          {/* Header */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h5">
              <Videocam sx={{ mr: 1, verticalAlign: 'middle' }} />
              Camera Management
            </Typography>
            <Box sx={{ display: 'flex', gap: 2 }}>
              <ToggleButtonGroup
                value={viewMode}
                exclusive
                onChange={(e, value) => value && setViewMode(value)}
                size="small"
              >
                <ToggleButton value="table">
                  <ViewList />
                </ToggleButton>
                <ToggleButton value="grid">
                  <ViewModule />
                </ToggleButton>
              </ToggleButtonGroup>
              
              <Button
                variant="outlined"
                startIcon={<Refresh />}
                onClick={loadCameras}
              >
                Refresh
              </Button>
              
              <Button
                variant="contained"
                startIcon={<Add />}
                onClick={() => window.location.href = '/cctv/cameras/new'}
              >
                Add Camera
              </Button>
            </Box>
          </Box>

          {/* Filters */}
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={12} md={3}>
              <TextField
                fullWidth
                size="small"
                placeholder="Search cameras..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                InputProps={{
                  startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />
                }}
              />
            </Grid>
            
            <Grid item xs={12} md={2}>
              <FormControl fullWidth size="small">
                <InputLabel>Camera Type</InputLabel>
                <Select
                  value={filterType}
                  label="Camera Type"
                  onChange={(e) => setFilterType(e.target.value)}
                >
                  <MenuItem value="all">All Types</MenuItem>
                  {cameraService.getCameraTypes().map(type => (
                    <MenuItem key={type.value} value={type.value}>{type.label}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} md={2}>
              <FormControl fullWidth size="small">
                <InputLabel>Location</InputLabel>
                <Select
                  value={filterLocation}
                  label="Location"
                  onChange={(e) => setFilterLocation(e.target.value)}
                >
                  <MenuItem value="all">All Locations</MenuItem>
                  {cameraService.getCameraLocations().map(loc => (
                    <MenuItem key={loc.value} value={loc.value}>{loc.label}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} md={2}>
              <FormControl fullWidth size="small">
                <InputLabel>Status</InputLabel>
                <Select
                  value={filterStatus}
                  label="Status"
                  onChange={(e) => setFilterStatus(e.target.value)}
                >
                  <MenuItem value="all">All Status</MenuItem>
                  {cameraService.getCameraStatuses().map(status => (
                    <MenuItem key={status.value} value={status.value}>{status.label}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} md={2}>
              <FormControl fullWidth size="small">
                <InputLabel>Critical</InputLabel>
                <Select
                  value={filterCritical}
                  label="Critical"
                  onChange={(e) => setFilterCritical(e.target.value)}
                >
                  <MenuItem value="all">All Cameras</MenuItem>
                  <MenuItem value="yes">Critical Only</MenuItem>
                  <MenuItem value="no">Non-Critical</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>

          {/* Loading State */}
          {loading ? (
            <Box display="flex" justifyContent="center" py={4}>
              <CircularProgress />
            </Box>
          ) : (
            <>
              {/* Table View */}
              {viewMode === 'table' && (
                <>
                  <TableContainer>
                    <Table>
                      <TableHead>
                        <TableRow>
                          <TableCell>Status</TableCell>
                          <TableCell>Camera</TableCell>
                          <TableCell>Type</TableCell>
                          <TableCell>Location</TableCell>
                          <TableCell>IP Address</TableCell>
                          <TableCell>Manufacturer</TableCell>
                          <TableCell align="center">Recording</TableCell>
                          <TableCell align="center">Uptime</TableCell>
                          <TableCell align="center">Actions</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {filteredCameras.length === 0 ? (
                          <TableRow>
                            <TableCell colSpan={9} align="center">
                              <Typography color="textSecondary">
                                No cameras found. Click "Add Camera" to get started.
                              </Typography>
                            </TableCell>
                          </TableRow>
                        ) : (
                          filteredCameras.map((camera) => (
                            <TableRow key={camera.id} hover>
                              <TableCell>
                                <Tooltip title={camera.status}>
                                  {getStatusIcon(camera.status)}
                                </Tooltip>
                              </TableCell>
                              <TableCell>
                                <Box>
                                  <Typography variant="body2" fontWeight="medium">
                                    {camera.camera_name}
                                  </Typography>
                                  <Typography variant="caption" color="textSecondary">
                                    {camera.camera_id}
                                  </Typography>
                                  {camera.is_critical && (
                                    <Chip label="CRITICAL" size="small" color="error" sx={{ ml: 1 }} />
                                  )}
                                </Box>
                              </TableCell>
                              <TableCell>
                                <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>
                                  {camera.camera_type}
                                </Typography>
                              </TableCell>
                              <TableCell>
                                <Typography variant="body2">
                                  {camera.location_description}
                                </Typography>
                              </TableCell>
                              <TableCell>
                                <Typography variant="body2" fontFamily="monospace">
                                  {camera.ip_address}:{camera.port}
                                </Typography>
                              </TableCell>
                              <TableCell>
                                <Typography variant="body2">
                                  {camera.manufacturer}
                                </Typography>
                                <Typography variant="caption" color="textSecondary">
                                  {camera.model}
                                </Typography>
                              </TableCell>
                              <TableCell align="center">
                                <Chip
                                  label={camera.recording_enabled ? 'ON' : 'OFF'}
                                  size="small"
                                  color={camera.recording_enabled ? 'success' : 'default'}
                                />
                              </TableCell>
                              <TableCell align="center">
                                <Typography 
                                  variant="body2" 
                                  color={camera.uptime_percentage >= 95 ? 'success.main' : 'warning.main'}
                                >
                                  {camera.uptime_percentage.toFixed(1)}%
                                </Typography>
                              </TableCell>
                              <TableCell align="center">
                                <Box sx={{ display: 'flex', gap: 0.5 }}>
                                  <Tooltip title="Test Connectivity">
                                    <IconButton 
                                      size="small" 
                                      color="info"
                                      onClick={() => handleTestConnectivity(camera)}
                                    >
                                      <WifiTethering />
                                    </IconButton>
                                  </Tooltip>
                                  
                                  <Tooltip title="Edit">
                                    <IconButton 
                                      size="small" 
                                      color="primary"
                                      onClick={() => window.location.href = `/cctv/cameras/${camera.id}/edit`}
                                    >
                                      <Edit />
                                    </IconButton>
                                  </Tooltip>
                                  
                                  <Tooltip title="Delete">
                                    <IconButton 
                                      size="small" 
                                      color="error"
                                      onClick={() => {
                                        setSelectedCamera(camera);
                                        setDeleteDialog(true);
                                      }}
                                    >
                                      <Delete />
                                    </IconButton>
                                  </Tooltip>
                                </Box>
                              </TableCell>
                            </TableRow>
                          ))
                        )}
                      </TableBody>
                    </Table>
                  </TableContainer>
                  
                  <TablePagination
                    component="div"
                    count={totalCameras}
                    page={page}
                    onPageChange={handleChangePage}
                    rowsPerPage={rowsPerPage}
                    onRowsPerPageChange={handleChangeRowsPerPage}
                    rowsPerPageOptions={[5, 10, 25, 50]}
                  />
                </>
              )}

              {/* Grid View */}
              {viewMode === 'grid' && (
                <Grid container spacing={2}>
                  {filteredCameras.length === 0 ? (
                    <Grid item xs={12}>
                      <Alert severity="info">
                        No cameras found. Click "Add Camera" to get started.
                      </Alert>
                    </Grid>
                  ) : (
                    filteredCameras.map((camera) => (
                      <Grid item xs={12} sm={6} md={4} lg={3} key={camera.id}>
                        <Card 
                          variant="outlined"
                          sx={{
                            '&:hover': { boxShadow: 3 },
                            border: camera.is_critical ? '2px solid' : '1px solid',
                            borderColor: camera.is_critical ? 'error.main' : 'divider'
                          }}
                        >
                          <CardContent>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                              <Box>
                                {getStatusIcon(camera.status)}
                                <Chip
                                  label={camera.status}
                                  size="small"
                                  color={getStatusColor(camera.status) as any}
                                  sx={{ ml: 1 }}
                                />
                              </Box>
                              {camera.is_critical && (
                                <Chip label="CRITICAL" size="small" color="error" />
                              )}
                            </Box>

                            <Typography variant="h6" noWrap>
                              {camera.camera_name}
                            </Typography>
                            <Typography variant="caption" color="textSecondary" display="block">
                              {camera.camera_id}
                            </Typography>

                            <Box sx={{ mt: 2 }}>
                              <Typography variant="body2" color="textSecondary">
                                Type: {camera.camera_type}
                              </Typography>
                              <Typography variant="body2" color="textSecondary">
                                Location: {camera.location_description}
                              </Typography>
                              <Typography variant="body2" color="textSecondary">
                                IP: {camera.ip_address}
                              </Typography>
                              <Typography variant="body2" color="textSecondary">
                                Uptime: {camera.uptime_percentage.toFixed(1)}%
                              </Typography>
                            </Box>

                            <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
                              <Tooltip title="Test Connectivity">
                                <IconButton 
                                  size="small" 
                                  color="info"
                                  onClick={() => handleTestConnectivity(camera)}
                                >
                                  <WifiTethering />
                                </IconButton>
                              </Tooltip>
                              
                              <Tooltip title="Edit">
                                <IconButton 
                                  size="small" 
                                  color="primary"
                                  onClick={() => window.location.href = `/cctv/cameras/${camera.id}/edit`}
                                >
                                  <Edit />
                                </IconButton>
                              </Tooltip>
                              
                              <Tooltip title="Delete">
                                <IconButton 
                                  size="small" 
                                  color="error"
                                  onClick={() => {
                                    setSelectedCamera(camera);
                                    setDeleteDialog(true);
                                  }}
                                >
                                  <Delete />
                                </IconButton>
                              </Tooltip>
                            </Box>
                          </CardContent>
                        </Card>
                      </Grid>
                    ))
                  )}
                </Grid>
              )}
            </>
          )}
        </CardContent>
      </Card>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialog} onClose={() => setDeleteDialog(false)}>
        <DialogTitle>Delete Camera</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete camera "{selectedCamera?.camera_name}"?
            This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialog(false)}>Cancel</Button>
          <Button onClick={handleDelete} color="error" variant="contained">
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default CameraList;
