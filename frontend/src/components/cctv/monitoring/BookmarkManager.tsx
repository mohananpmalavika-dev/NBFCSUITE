/**
 * Bookmark Manager Component
 * 
 * Manages video event bookmarks for important incidents
 * Features:
 * - Create bookmarks
 * - Search bookmarks
 * - Filter by camera/date
 * - Quick access to bookmarked events
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  IconButton,
  Chip,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Tooltip
} from '@mui/material';
import {
  Bookmark,
  Add,
  Search,
  PlayArrow,
  Delete,
  Videocam
} from '@mui/icons-material';
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import monitoringService, { VideoBookmark, LiveCamera } from '../../../services/monitoringService';

const BookmarkManager: React.FC = () => {
  const [bookmarks, setBookmarks] = useState<VideoBookmark[]>([]);
  const [cameras, setCameras] = useState<LiveCamera[]>([]);
  const [loading, setLoading] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [totalBookmarks, setTotalBookmarks] = useState(0);

  // Filters
  const [selectedCamera, setSelectedCamera] = useState<string>('all');
  const [dateFrom, setDateFrom] = useState<Date | null>(null);
  const [dateTo, setDateTo] = useState<Date | null>(null);

  // Form data
  const [formData, setFormData] = useState({
    camera_id: '',
    bookmark_name: '',
    description: '',
    timestamp: new Date()
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    loadCameras();
    loadBookmarks();
  }, [page, rowsPerPage, selectedCamera, dateFrom, dateTo]);

  const loadCameras = async () => {
    try {
      const data = await monitoringService.getLiveCameras({
        page: 1,
        page_size: 100
      });
      setCameras(data.cameras);
    } catch (error) {
      console.error('Failed to load cameras:', error);
    }
  };

  const loadBookmarks = async () => {
    try {
      setLoading(true);
      const data = await monitoringService.getBookmarks({
        camera_id: selectedCamera === 'all' ? undefined : selectedCamera,
        date_from: dateFrom?.toISOString(),
        date_to: dateTo?.toISOString(),
        page: page + 1,
        page_size: rowsPerPage
      });
      setBookmarks(data.bookmarks);
      setTotalBookmarks(data.total);
      setLoading(false);
    } catch (error) {
      console.error('Failed to load bookmarks:', error);
      setLoading(false);
    }
  };

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.camera_id) {
      newErrors.camera_id = 'Please select a camera';
    }
    if (!formData.bookmark_name.trim()) {
      newErrors.bookmark_name = 'Bookmark name is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleCreateBookmark = async () => {
    if (!validateForm()) {
      return;
    }

    try {
      setLoading(true);
      await monitoringService.createBookmark({
        camera_id: formData.camera_id,
        bookmark_name: formData.bookmark_name,
        description: formData.description || undefined,
        timestamp: formData.timestamp.toISOString()
      });

      setDialogOpen(false);
      resetForm();
      loadBookmarks();
      setLoading(false);
    } catch (error) {
      console.error('Failed to create bookmark:', error);
      setLoading(false);
      alert('Failed to create bookmark');
    }
  };

  const resetForm = () => {
    setFormData({
      camera_id: '',
      bookmark_name: '',
      description: '',
      timestamp: new Date()
    });
    setErrors({});
  };

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const getCameraName = (cameraId: string) => {
    const camera = cameras.find(c => c.id === cameraId);
    return camera?.camera_name || 'Unknown Camera';
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Box>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h6">
                <Bookmark sx={{ mr: 1, verticalAlign: 'middle' }} />
                Video Event Bookmarks
              </Typography>
              <Button
                variant="contained"
                startIcon={<Add />}
                onClick={() => setDialogOpen(true)}
              >
                Create Bookmark
              </Button>
            </Box>

            <Alert severity="info" sx={{ mb: 3 }}>
              <Typography variant="body2">
                Bookmark important events for quick access and review. Timestamps are saved for easy video retrieval.
              </Typography>
            </Alert>

            {/* Filters */}
            <Grid container spacing={2} sx={{ mb: 3 }}>
              <Grid item xs={12} md={4}>
                <FormControl fullWidth size="small">
                  <InputLabel>Camera Filter</InputLabel>
                  <Select
                    value={selectedCamera}
                    label="Camera Filter"
                    onChange={(e) => {
                      setSelectedCamera(e.target.value);
                      setPage(0);
                    }}
                  >
                    <MenuItem value="all">All Cameras</MenuItem>
                    {cameras.map(camera => (
                      <MenuItem key={camera.id} value={camera.id}>
                        {camera.camera_name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={4}>
                <DateTimePicker
                  label="From Date"
                  value={dateFrom}
                  onChange={(newValue) => {
                    setDateFrom(newValue);
                    setPage(0);
                  }}
                  slotProps={{
                    textField: { fullWidth: true, size: 'small' }
                  }}
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <DateTimePicker
                  label="To Date"
                  value={dateTo}
                  onChange={(newValue) => {
                    setDateTo(newValue);
                    setPage(0);
                  }}
                  slotProps={{
                    textField: { fullWidth: true, size: 'small' }
                  }}
                />
              </Grid>
            </Grid>

            {/* Bookmarks Table */}
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Bookmark Name</TableCell>
                    <TableCell>Camera</TableCell>
                    <TableCell>Event Time</TableCell>
                    <TableCell>Description</TableCell>
                    <TableCell>Created By</TableCell>
                    <TableCell align="center">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {bookmarks.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={6} align="center">
                        <Typography color="textSecondary">
                          No bookmarks found. Create your first bookmark to get started.
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ) : (
                    bookmarks.map((bookmark) => (
                      <TableRow key={bookmark.id} hover>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Bookmark color="primary" fontSize="small" />
                            <Typography variant="body2" fontWeight="medium">
                              {bookmark.bookmark_name}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Chip
                            icon={<Videocam />}
                            label={getCameraName(bookmark.camera_id)}
                            size="small"
                            variant="outlined"
                          />
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {new Date(bookmark.bookmark_timestamp).toLocaleString()}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" color="textSecondary">
                            {bookmark.description || '-'}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="caption" color="textSecondary">
                            {new Date(bookmark.created_at).toLocaleDateString()}
                          </Typography>
                        </TableCell>
                        <TableCell align="center">
                          <Tooltip title="Play Video">
                            <IconButton size="small" color="primary">
                              <PlayArrow />
                            </IconButton>
                          </Tooltip>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </TableContainer>

            <TablePagination
              component="div"
              count={totalBookmarks}
              page={page}
              onPageChange={handleChangePage}
              rowsPerPage={rowsPerPage}
              onRowsPerPageChange={handleChangeRowsPerPage}
              rowsPerPageOptions={[5, 10, 25, 50]}
            />
          </CardContent>
        </Card>

        {/* Create Bookmark Dialog */}
        <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
          <DialogTitle>
            <Bookmark sx={{ mr: 1, verticalAlign: 'middle' }} />
            Create Event Bookmark
          </DialogTitle>
          <DialogContent>
            <Box sx={{ pt: 2 }}>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <FormControl fullWidth error={!!errors.camera_id}>
                    <InputLabel>Camera *</InputLabel>
                    <Select
                      value={formData.camera_id}
                      label="Camera *"
                      onChange={(e) => setFormData({ ...formData, camera_id: e.target.value })}
                    >
                      {cameras.map(camera => (
                        <MenuItem key={camera.id} value={camera.id}>
                          {camera.camera_name} - {camera.location_type}
                        </MenuItem>
                      ))}
                    </Select>
                    {errors.camera_id && (
                      <Typography variant="caption" color="error">
                        {errors.camera_id}
                      </Typography>
                    )}
                  </FormControl>
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Bookmark Name"
                    value={formData.bookmark_name}
                    onChange={(e) => setFormData({ ...formData, bookmark_name: e.target.value })}
                    error={!!errors.bookmark_name}
                    helperText={errors.bookmark_name || 'Short descriptive name for this event'}
                    required
                  />
                </Grid>
                <Grid item xs={12}>
                  <DateTimePicker
                    label="Event Timestamp"
                    value={formData.timestamp}
                    onChange={(newValue) => setFormData({ ...formData, timestamp: newValue || new Date() })}
                    slotProps={{
                      textField: {
                        fullWidth: true,
                        helperText: 'Time when the event occurred'
                      }
                    }}
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Description"
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    multiline
                    rows={4}
                    helperText="Detailed description of the event"
                  />
                </Grid>
              </Grid>
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
            <Button
              onClick={handleCreateBookmark}
              variant="contained"
              disabled={loading}
            >
              {loading ? 'Creating...' : 'Create Bookmark'}
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </LocalizationProvider>
  );
};

export default BookmarkManager;
