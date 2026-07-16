/**
 * Manual Review Triggers Step
 * Configure conditions that trigger manual review
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
  FormControlLabel,
  Switch
} from '@mui/material';
import { Add as AddIcon, Delete as DeleteIcon } from '@mui/icons-material';
import { ReviewTriggerType } from '@/services/creditPolicy.service';

interface ReviewTriggersStepProps {
  data: any[];
  onChange: (data: any[]) => void;
}

const defaultTrigger = {
  trigger_type: ReviewTriggerType.CREDIT_SCORE,
  trigger_name: '',
  condition_field: 'credit_score',
  condition_operator: '<',
  condition_value: '',
  review_level: 'L1',
  priority: 'NORMAL',
  is_active: true
};

const ReviewTriggersStep: React.FC<ReviewTriggersStepProps> = ({ data, onChange }) => {
  const handleAdd = () => {
    onChange([...data, { ...defaultTrigger }]);
  };

  const handleRemove = (index: number) => {
    onChange(data.filter((_, i) => i !== index));
  };

  const handleChange = (index: number, field: string) => (
    event: React.ChangeEvent<HTMLInputElement | { value: unknown }>
  ) => {
    const newData = [...data];
    const value = event.target.type === 'checkbox' 
      ? (event.target as HTMLInputElement).checked
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
          <Typography variant="h6">Manual Review Triggers</Typography>
          <Typography variant="body2" color="text.secondary">
            Define conditions that require manual review
          </Typography>
        </Box>
        <Button variant="contained" startIcon={<AddIcon />} onClick={handleAdd}>
          Add Trigger
        </Button>
      </Box>

      {data.length === 0 ? (
        <Card>
          <CardContent>
            <Typography variant="body1" color="text.secondary" align="center" py={4}>
              No review triggers configured. Click "Add Trigger" to create one.
            </Typography>
          </CardContent>
        </Card>
      ) : (
        <Grid container spacing={2}>
          {data.map((trigger, index) => (
            <Grid item xs={12} key={index}>
              <Card>
                <CardContent>
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                    <Typography variant="subtitle1" fontWeight="bold">
                      Trigger {index + 1}
                    </Typography>
                    <IconButton color="error" onClick={() => handleRemove(index)} size="small">
                      <DeleteIcon />
                    </IconButton>
                  </Box>

                  <Grid container spacing={2}>
                    <Grid item xs={12} md={6}>
                      <FormControl fullWidth required>
                        <InputLabel>Trigger Type</InputLabel>
                        <Select
                          value={trigger.trigger_type}
                          onChange={handleChange(index, 'trigger_type')}
                          label="Trigger Type"
                        >
                          {Object.values(ReviewTriggerType).map((type) => (
                            <MenuItem key={type} value={type}>
                              {type.replace(/_/g, ' ')}
                            </MenuItem>
                          ))}
                        </Select>
                      </FormControl>
                    </Grid>

                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        required
                        label="Trigger Name"
                        value={trigger.trigger_name}
                        onChange={handleChange(index, 'trigger_name')}
                        placeholder="e.g., Low Credit Score Review"
                      />
                    </Grid>

                    <Grid item xs={12} md={4}>
                      <TextField
                        fullWidth
                        label="Condition Field"
                        value={trigger.condition_field}
                        onChange={handleChange(index, 'condition_field')}
                        placeholder="e.g., credit_score"
                      />
                    </Grid>

                    <Grid item xs={12} md={2}>
                      <FormControl fullWidth>
                        <InputLabel>Operator</InputLabel>
                        <Select
                          value={trigger.condition_operator}
                          onChange={handleChange(index, 'condition_operator')}
                          label="Operator"
                        >
                          <MenuItem value="<">{'<'}</MenuItem>
                          <MenuItem value="<=">{'<='}</MenuItem>
                          <MenuItem value=">">{'>'}</MenuItem>
                          <MenuItem value=">=">{'>='}</MenuItem>
                          <MenuItem value="=">=</MenuItem>
                          <MenuItem value="!=">!=</MenuItem>
                          <MenuItem value="IN">IN</MenuItem>
                        </Select>
                      </FormControl>
                    </Grid>

                    <Grid item xs={12} md={3}>
                      <TextField
                        fullWidth
                        label="Condition Value"
                        value={trigger.condition_value}
                        onChange={handleChange(index, 'condition_value')}
                        placeholder="e.g., 650"
                      />
                    </Grid>

                    <Grid item xs={12} md={3}>
                      <FormControl fullWidth>
                        <InputLabel>Review Level</InputLabel>
                        <Select
                          value={trigger.review_level}
                          onChange={handleChange(index, 'review_level')}
                          label="Review Level"
                        >
                          <MenuItem value="L1">Level 1</MenuItem>
                          <MenuItem value="L2">Level 2</MenuItem>
                          <MenuItem value="L3">Level 3</MenuItem>
                          <MenuItem value="COMMITTEE">Committee</MenuItem>
                        </Select>
                      </FormControl>
                    </Grid>

                    <Grid item xs={12} md={6}>
                      <FormControl fullWidth>
                        <InputLabel>Priority</InputLabel>
                        <Select
                          value={trigger.priority}
                          onChange={handleChange(index, 'priority')}
                          label="Priority"
                        >
                          <MenuItem value="LOW">Low</MenuItem>
                          <MenuItem value="NORMAL">Normal</MenuItem>
                          <MenuItem value="HIGH">High</MenuItem>
                          <MenuItem value="URGENT">Urgent</MenuItem>
                        </Select>
                      </FormControl>
                    </Grid>

                    <Grid item xs={12} md={6}>
                      <FormControlLabel
                        control={
                          <Switch
                            checked={trigger.is_active}
                            onChange={handleChange(index, 'is_active')}
                          />
                        }
                        label="Active"
                      />
                    </Grid>

                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        multiline
                        rows={2}
                        label="Reviewer Instructions"
                        value={trigger.reviewer_instructions || ''}
                        onChange={handleChange(index, 'reviewer_instructions')}
                        placeholder="Instructions for the reviewer..."
                      />
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  );
};

export default ReviewTriggersStep;
