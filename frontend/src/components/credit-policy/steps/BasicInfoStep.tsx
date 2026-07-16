/**
 * Basic Information Step
 * Policy name, code, description, product selection
 */
import React from 'react';
import {
  Box,
  Grid,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Typography
} from '@mui/material';
import { CreditPolicy, PolicyStatus } from '@/services/creditPolicyService';

interface BasicInfoStepProps {
  data: Partial<CreditPolicy>;
  onChange: (data: Partial<CreditPolicy>) => void;
}

const BasicInfoStep: React.FC<BasicInfoStepProps> = ({ data, onChange }) => {
  const handleChange = (field: keyof CreditPolicy) => (
    event: React.ChangeEvent<HTMLInputElement | { value: unknown }>
  ) => {
    onChange({
      ...data,
      [field]: event.target.value
    });
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Basic Policy Information
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Configure the basic details of your credit policy
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <TextField
            required
            fullWidth
            label="Policy Name"
            value={data.name || ''}
            onChange={handleChange('name')}
            placeholder="e.g., Personal Loan - Standard Policy"
            helperText="A descriptive name for the policy"
          />
        </Grid>

        <Grid item xs={12} md={6}>
          <TextField
            required
            fullWidth
            label="Policy Code"
            value={data.code || ''}
            onChange={handleChange('code')}
            placeholder="e.g., PL-STD-001"
            helperText="Unique identifier for the policy"
          />
        </Grid>

        <Grid item xs={12}>
          <TextField
            fullWidth
            multiline
            rows={4}
            label="Description"
            value={data.description || ''}
            onChange={handleChange('description')}
            placeholder="Describe the purpose and scope of this policy"
          />
        </Grid>

        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Version"
            value={data.version || '1.0'}
            onChange={handleChange('version')}
            helperText="Policy version number"
          />
        </Grid>

        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel>Status</InputLabel>
            <Select
              value={data.status || PolicyStatus.DRAFT}
              onChange={handleChange('status')}
              label="Status"
            >
              <MenuItem value={PolicyStatus.DRAFT}>Draft</MenuItem>
              <MenuItem value={PolicyStatus.ACTIVE}>Active</MenuItem>
              <MenuItem value={PolicyStatus.INACTIVE}>Inactive</MenuItem>
              <MenuItem value={PolicyStatus.ARCHIVED}>Archived</MenuItem>
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            type="datetime-local"
            label="Effective From"
            value={data.effective_from || ''}
            onChange={handleChange('effective_from')}
            InputLabelProps={{ shrink: true }}
            helperText="When this policy becomes active"
          />
        </Grid>

        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            type="datetime-local"
            label="Effective To"
            value={data.effective_to || ''}
            onChange={handleChange('effective_to')}
            InputLabelProps={{ shrink: true }}
            helperText="When this policy expires (optional)"
          />
        </Grid>
      </Grid>
    </Box>
  );
};

export default BasicInfoStep;
