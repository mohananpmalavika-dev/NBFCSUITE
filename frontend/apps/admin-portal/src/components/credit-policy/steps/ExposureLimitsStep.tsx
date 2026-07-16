/**
 * Exposure Limits Step
 * Configure portfolio exposure and concentration limits
 */
import React from 'react';
import {
  Box,
  Grid,
  TextField,
  Typography,
  Card,
  CardContent,
  Button,
  IconButton,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  InputAdornment,
  Tabs,
  Tab
} from '@mui/material';
import { Add as AddIcon, Delete as DeleteIcon } from '@mui/icons-material';
import { ExposureType } from '@/services/creditPolicy.service';

interface ExposureLimitsStepProps {
  data: any[];
  onChange: (data: any[]) => void;
}

const defaultExposure = {
  exposure_type: ExposureType.CUSTOMER,
  exposure_name: '',
  max_exposure_amount: 0,
  warning_threshold_percentage: 80
};

const ExposureLimitsStep: React.FC<ExposureLimitsStepProps> = ({ data, onChange }) => {
  const [tabValue, setTabValue] = React.useState(0);

  const handleAdd = () => {
    onChange([...data, { ...defaultExposure }]);
  };

  const handleRemove = (index: number) => {
    onChange(data.filter((_, i) => i !== index));
  };

  const handleChange = (index: number, field: string) => (
    event: React.ChangeEvent<HTMLInputElement | { value: unknown }>
  ) => {
    const newData = [...data];
    const value = event.target.type === 'number' 
      ? parseFloat(event.target.value as string)
      : event.target.value;
    
    newData[index] = {
      ...newData[index],
      [field]: value
    };
    onChange(newData);
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h6">Exposure & Concentration Limits</Typography>
          <Typography variant="body2" color="text.secondary">
            Set portfolio risk limits and concentration controls
          </Typography>
        </Box>
        <Button variant="contained" startIcon={<AddIcon />} onClick={handleAdd}>
          Add Limit
        </Button>
      </Box>

      <Tabs value={tabValue} onChange={(_, v) => setTabValue(v)} sx={{ mb: 3 }}>
        <Tab label="Exposure Limits" />
        <Tab label="Sectoral Caps" />
        <Tab label="Concentration Limits" />
      </Tabs>

      {tabValue === 0 && (
        <>
          {data.length === 0 ? (
            <Card>
              <CardContent>
                <Typography variant="body1" color="text.secondary" align="center" py={4}>
                  No exposure limits configured. Click "Add Limit" to create one.
                </Typography>
              </CardContent>
            </Card>
          ) : (
            <Grid container spacing={2}>
              {data.map((limit, index) => (
                <Grid item xs={12} key={index}>
                  <Card>
                    <CardContent>
                      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                        <Typography variant="subtitle1" fontWeight="bold">
                          Exposure Limit {index + 1}
                        </Typography>
                        <IconButton color="error" onClick={() => handleRemove(index)} size="small">
                          <DeleteIcon />
                        </IconButton>
                      </Box>

                      <Grid container spacing={2}>
                        <Grid item xs={12} md={4}>
                          <FormControl fullWidth required>
                            <InputLabel>Exposure Type</InputLabel>
                            <Select
                              value={limit.exposure_type}
                              onChange={handleChange(index, 'exposure_type')}
                              label="Exposure Type"
                            >
                              {Object.values(ExposureType).map((type) => (
                                <MenuItem key={type} value={type}>
                                  {type}
                                </MenuItem>
                              ))}
                            </Select>
                          </FormControl>
                        </Grid>

                        <Grid item xs={12} md={8}>
                          <TextField
                            fullWidth
                            required
                            label="Exposure Name"
                            value={limit.exposure_name}
                            onChange={handleChange(index, 'exposure_name')}
                            placeholder="e.g., Manufacturing Industry"
                            helperText="Name or identifier for this exposure category"
                          />
                        </Grid>

                        <Grid item xs={12} md={6}>
                          <TextField
                            fullWidth
                            required
                            type="number"
                            label="Maximum Exposure Amount"
                            value={limit.max_exposure_amount}
                            onChange={handleChange(index, 'max_exposure_amount')}
                            InputProps={{
                              startAdornment: <InputAdornment position="start">₹</InputAdornment>,
                              inputProps: { step: 1000000, min: 0 }
                            }}
                            helperText="Maximum total exposure allowed"
                          />
                        </Grid>

                        <Grid item xs={12} md={6}>
                          <TextField
                            fullWidth
                            type="number"
                            label="Maximum Exposure Percentage"
                            value={limit.max_exposure_percentage || ''}
                            onChange={handleChange(index, 'max_exposure_percentage')}
                            InputProps={{
                              endAdornment: <InputAdornment position="end">%</InputAdornment>,
                              inputProps: { step: 1, min: 0, max: 100 }
                            }}
                            helperText="% of total portfolio (optional)"
                          />
                        </Grid>

                        <Grid item xs={12} md={6}>
                          <TextField
                            fullWidth
                            type="number"
                            label="Single Obligor Limit"
                            value={limit.max_single_obligor_amount || ''}
                            onChange={handleChange(index, 'max_single_obligor_amount')}
                            InputProps={{
                              startAdornment: <InputAdornment position="start">₹</InputAdornment>,
                              inputProps: { step: 100000, min: 0 }
                            }}
                            helperText="Max to single entity (optional)"
                          />
                        </Grid>

                        <Grid item xs={12} md={6}>
                          <TextField
                            fullWidth
                            required
                            type="number"
                            label="Warning Threshold"
                            value={limit.warning_threshold_percentage}
                            onChange={handleChange(index, 'warning_threshold_percentage')}
                            InputProps={{
                              endAdornment: <InputAdornment position="end">%</InputAdornment>,
                              inputProps: { step: 5, min: 0, max: 100 }
                            }}
                            helperText="Alert when utilization reaches this %"
                          />
                        </Grid>
                      </Grid>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          )}
        </>
      )}

      {tabValue === 1 && (
        <Card>
          <CardContent>
            <Typography variant="body1" color="text.secondary" align="center" py={4}>
              Sectoral caps configuration (RBI compliance)
            </Typography>
            <Typography variant="body2" color="text.secondary" align="center">
              Configure sector-wise lending limits for regulatory compliance
            </Typography>
          </CardContent>
        </Card>
      )}

      {tabValue === 2 && (
        <Card>
          <CardContent>
            <Typography variant="body1" color="text.secondary" align="center" py={4}>
              Portfolio concentration limits
            </Typography>
            <Typography variant="body2" color="text.secondary" align="center">
              Set limits on portfolio concentration by various parameters
            </Typography>
          </CardContent>
        </Card>
      )}

      <Box mt={3}>
        <Typography variant="body2" color="text.secondary">
          💡 Tip: Set exposure limits to manage portfolio risk and ensure diversification.
          Warning thresholds help proactively manage approaching limits.
        </Typography>
      </Box>
    </Box>
  );
};

export default ExposureLimitsStep;
