/**
 * Storage Calculator Component
 * 
 * Calculate storage requirements based on camera count, bitrate, and retention period.
 * Formula: Storage (GB) = (Bitrate × 3600 × Hours × Days × Cameras) / (8 × 1024 × 1024)
 */

import React, { useState } from 'react';
import {
  Box, Card, CardContent, Typography, TextField, Button, Grid,
  Alert, Table, TableBody, TableCell, TableContainer, TableHead,
  TableRow, Paper, Divider, Chip
} from '@mui/material';
import { Calculate, Storage, Info } from '@mui/icons-material';
import { recordingService } from '../../../services/recordingService';

interface StorageCalculation {
  num_cameras: number;
  bitrate_kbps: number;
  retention_days: number;
  recording_hours_per_day: number;
  total_storage_gb: number;
  total_storage_tb: number;
  storage_breakdown: {
    hot_storage_gb: number;
    hot_storage_days: number;
    warm_storage_gb: number;
    warm_storage_days: number;
    cold_storage_gb: number;
    cold_storage_days: number;
  };
  recommended_raid: string;
  recommended_backup_size_tb: number;
}

export const StorageCalculator: React.FC = () => {
  const [numCameras, setNumCameras] = useState<number>(20);
  const [bitrateKbps, setB

itrateKbps] = useState<number>(2048);
  const [retentionDays, setRetentionDays] = useState<number>(180);
  const [recordingHours, setRecordingHours] = useState<number>(24);
  const [calculation, setCalculation] = useState<StorageCalculation | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleCalculate = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await recordingService.calculateStorage({
        num_cameras: numCameras,
        bitrate_kbps: bitrateKbps,
        retention_days: retentionDays,
        recording_hours: recordingHours
      });
      
      setCalculation(response.data);
    } catch (err: any) {
      setError(err.message || 'Calculation failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 3 }}>
        Storage Calculator
      </Typography>

      <Grid container spacing={3}>
        {/* Input Section */}
        <Grid item xs={12} md={5}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Camera Configuration
              </Typography>
              
              <TextField
                fullWidth
                label="Number of Cameras"
                type="number"
                value={numCameras}
                onChange={(e) => setNumCameras(parseInt(e.target.value) || 0)}
                InputProps={{ inputProps: { min: 1, max: 1000 } }}
                sx={{ mb: 2 }}
              />
              
              <TextField
                fullWidth
                label="Bitrate per Camera (Kbps)"
                type="number"
                value={bitrateKbps}
                onChange={(e) => setBitrateKbps(parseInt(e.target.value) || 0)}
                InputProps={{ inputProps: { min: 512, max: 8192 } }}
                helperText="Typical: 1024-2048 Kbps for 1080p, 4096-6144 for 4K"
                sx={{ mb: 2 }}
              />
              
              <TextField
                fullWidth
                label="Retention Period (Days)"
                type="number"
                value={retentionDays}
                onChange={(e) => setRetentionDays(parseInt(e.target.value) || 0)}
                InputProps={{ inputProps: { min: 30, max: 365 } }}
                helperText="RBI minimum: 180 days"
                sx={{ mb: 2 }}
              />
              
              <TextField
                fullWidth
                label="Recording Hours per Day"
                type="number"
                value={recordingHours}
                onChange={(e) => setRecordingHours(parseInt(e.target.value) || 0)}
                InputProps={{ inputProps: { min: 1, max: 24 } }}
                helperText="24 for continuous recording"
                sx={{ mb: 3 }}
              />
              
              <Button
                fullWidth
                variant="contained"
                size="large"
                startIcon={<Calculate />}
                onClick={handleCalculate}
                disabled={loading}
              >
                Calculate Storage
              </Button>
            </CardContent>
          </Card>

          {/* Formula Info */}
          <Card sx={{ mt: 2 }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Info color="primary" sx={{ mr: 1 }} />
                <Typography variant="subtitle2">Formula</Typography>
              </Box>
              <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>
                Storage (GB) = (Bitrate × 3600 × Hours × Days × Cameras) / (8 × 1024 × 1024)
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Results Section */}
        <Grid item xs={12} md={7}>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
              {error}
            </Alert>
          )}

          {calculation && (
            <>
              {/* Total Storage Required */}
              <Card sx={{ mb: 2 }}>
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 2 }}>
                    Total Storage Required
                  </Typography>
                  <Box sx={{ textAlign: 'center', py: 2 }}>
                    <Typography variant="h2" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                      {calculation.total_storage_tb.toFixed(2)} TB
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      ({calculation.total_storage_gb.toFixed(0)} GB)
                    </Typography>
                  </Box>
                  <Divider sx={{ my: 2 }} />
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        Cameras
                      </Typography>
                      <Typography variant="h6">{calculation.num_cameras}</Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        Bitrate
                      </Typography>
                      <Typography variant="h6">{calculation.bitrate_kbps} Kbps</Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        Retention
                      </Typography>
                      <Typography variant="h6">{calculation.retention_days} days</Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        Recording
                      </Typography>
                      <Typography variant="h6">{calculation.recording_hours_per_day}h/day</Typography>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>

              {/* Storage Tier Breakdown */}
              <Card sx={{ mb: 2 }}>
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 2 }}>
                    Storage Tier Breakdown
                  </Typography>
                  <TableContainer>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Tier</TableCell>
                          <TableCell>Period</TableCell>
                          <TableCell align="right">Storage (GB)</TableCell>
                          <TableCell>Type</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        <TableRow>
                          <TableCell>
                            <Chip label="Hot" color="error" size="small" />
                          </TableCell>
                          <TableCell>
                            {calculation.storage_breakdown.hot_storage_days} days
                          </TableCell>
                          <TableCell align="right">
                            {calculation.storage_breakdown.hot_storage_gb.toFixed(2)}
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" color="text.secondary">
                              SSD/NVMe - Quick access
                            </Typography>
                          </TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell>
                            <Chip label="Warm" color="warning" size="small" />
                          </TableCell>
                          <TableCell>
                            {calculation.storage_breakdown.warm_storage_days} days
                          </TableCell>
                          <TableCell align="right">
                            {calculation.storage_breakdown.warm_storage_gb.toFixed(2)}
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" color="text.secondary">
                              HDD RAID 6 - Fast access
                            </Typography>
                          </TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell>
                            <Chip label="Cold" color="info" size="small" />
                          </TableCell>
                          <TableCell>
                            {calculation.storage_breakdown.cold_storage_days} days
                          </TableCell>
                          <TableCell align="right">
                            {calculation.storage_breakdown.cold_storage_gb.toFixed(2)}
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" color="text.secondary">
                              HDD RAID 6 - Archival
                            </Typography>
                          </TableCell>
                        </TableRow>
                      </TableBody>
                    </Table>
                  </TableContainer>
                </CardContent>
              </Card>

              {/* Recommendations */}
              <Card>
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 2 }}>
                    Recommendations
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}>
                      <Box sx={{ p: 2, bgcolor: 'action.hover', borderRadius: 1 }}>
                        <Typography variant="subtitle2" gutterBottom>
                          RAID Configuration
                        </Typography>
                        <Chip
                          label={calculation.recommended_raid}
                          color="primary"
                          sx={{ fontWeight: 'bold' }}
                        />
                        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                          {calculation.recommended_raid === 'RAID 10'
                            ? 'Best performance & redundancy'
                            : 'Good redundancy & capacity'}
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <Box sx={{ p: 2, bgcolor: 'action.hover', borderRadius: 1 }}>
                        <Typography variant="subtitle2" gutterBottom>
                          Backup Storage
                        </Typography>
                        <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                          {calculation.recommended_backup_size_tb.toFixed(2)} TB
                        </Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                          NAS or Cloud backup
                        </Typography>
                      </Box>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </>
          )}

          {!calculation && (
            <Card>
              <CardContent>
                <Box sx={{ textAlign: 'center', py: 5 }}>
                  <Storage sx={{ fontSize: 80, color: 'action.disabled', mb: 2 }} />
                  <Typography variant="h6" color="text.secondary">
                    Enter camera configuration and click Calculate
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          )}
        </Grid>
      </Grid>
    </Box>
  );
};

export default StorageCalculator;
