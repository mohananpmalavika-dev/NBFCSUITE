/**
 * Employee Profile Page
 * View and update employee profile information
 */

import React, { useEffect, useState } from 'react';
import {
  Box,
  Container,
  Card,
  CardContent,
  Typography,
  Button,
  IconButton,
  Grid,
  TextField,
  Avatar,
  Alert,
  CircularProgress,
  Divider,
  Paper
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  Save as SaveIcon,
  Person as PersonIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

interface EmployeeProfile {
  id: string;
  employee_code: string;
  full_name: string;
  official_email: string;
  personal_email: string;
  mobile: string;
  alternate_mobile: string;
  date_of_birth: string;
  gender: string;
  blood_group: string;
  marital_status: string;
  department_name: string;
  designation_name: string;
  reporting_manager_name: string;
  date_of_joining: string;
  current_address_line1: string;
  current_address_line2: string;
  current_city: string;
  current_state: string;
  current_pincode: string;
  emergency_contact_name: string;
  emergency_contact_number: string;
  salary_bank_name: string;
  salary_account_number: string;
  salary_ifsc_code: string;
  photo_url: string;
}

const Profile: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [profile, setProfile] = useState<EmployeeProfile | null>(null);
  const [editMode, setEditMode] = useState(false);
  
  const [formData, setFormData] = useState({
    personal_email: '',
    mobile: '',
    alternate_mobile: '',
    emergency_contact_name: '',
    emergency_contact_number: '',
    emergency_contact_relation: '',
    current_address_line1: '',
    current_address_line2: '',
    current_city: '',
    current_state: '',
    current_pincode: '',
    salary_bank_name: '',
    salary_account_number: '',
    salary_ifsc_code: ''
  });

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/hrms/ess/profile');
      setProfile(response.data);
      
      // Initialize form data
      setFormData({
        personal_email: response.data.personal_email || '',
        mobile: response.data.mobile || '',
        alternate_mobile: response.data.alternate_mobile || '',
        emergency_contact_name: response.data.emergency_contact_name || '',
        emergency_contact_number: response.data.emergency_contact_number || '',
        emergency_contact_relation: '',
        current_address_line1: response.data.current_address_line1 || '',
        current_address_line2: response.data.current_address_line2 || '',
        current_city: response.data.current_city || '',
        current_state: response.data.current_state || '',
        current_pincode: response.data.current_pincode || '',
        salary_bank_name: response.data.salary_bank_name || '',
        salary_account_number: response.data.salary_account_number || '',
        salary_ifsc_code: response.data.salary_ifsc_code || ''
      });
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to load profile');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setError(null);
      setSuccess(null);
      
      await axios.put('/api/hrms/ess/profile', formData);
      
      setSuccess('Profile updated successfully');
      setEditMode(false);
      fetchProfile();
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to update profile');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (!profile) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Alert severity="error">Profile not found</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box display="flex" alignItems="center" mb={3}>
        <IconButton onClick={() => navigate('/ess')} sx={{ mr: 2 }}>
          <ArrowBackIcon />
        </IconButton>
        <Box flex={1}>
          <Typography variant="h4" fontWeight={600}>
            My Profile
          </Typography>
          <Typography variant="body2" color="text.secondary">
            View and update your personal information
          </Typography>
        </Box>
        {!editMode ? (
          <Button variant="contained" onClick={() => setEditMode(true)}>
            Edit Profile
          </Button>
        ) : (
          <Box display="flex" gap={1}>
            <Button variant="outlined" onClick={() => setEditMode(false)} disabled={saving}>
              Cancel
            </Button>
            <Button
              variant="contained"
              startIcon={<SaveIcon />}
              onClick={handleSave}
              disabled={saving}
            >
              {saving ? <CircularProgress size={24} /> : 'Save Changes'}
            </Button>
          </Box>
        )}
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 3 }} onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Profile Summary */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Avatar
                sx={{ width: 120, height: 120, margin: '0 auto', mb: 2, bgcolor: 'primary.main' }}
                src={profile.photo_url}
              >
                <PersonIcon sx={{ fontSize: 60 }} />
              </Avatar>
              <Typography variant="h5" fontWeight={600} gutterBottom>
                {profile.full_name}
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                {profile.employee_code}
              </Typography>
              <Typography variant="body2" color="primary" gutterBottom>
                {profile.designation_name}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {profile.department_name}
              </Typography>
              
              <Divider sx={{ my: 2 }} />
              
              <Box textAlign="left">
                <Typography variant="caption" color="text.secondary">Official Email</Typography>
                <Typography variant="body2" gutterBottom>{profile.official_email}</Typography>
                
                <Typography variant="caption" color="text.secondary">Mobile</Typography>
                <Typography variant="body2" gutterBottom>{profile.mobile}</Typography>
                
                <Typography variant="caption" color="text.secondary">Reporting Manager</Typography>
                <Typography variant="body2" gutterBottom>{profile.reporting_manager_name}</Typography>
                
                <Typography variant="caption" color="text.secondary">Date of Joining</Typography>
                <Typography variant="body2">{new Date(profile.date_of_joining).toLocaleDateString()}</Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Editable Fields */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Contact Information
              </Typography>
              <Divider sx={{ mb: 3 }} />
              
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Personal Email"
                    value={formData.personal_email}
                    onChange={(e) => setFormData({ ...formData, personal_email: e.target.value })}
                    disabled={!editMode}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Mobile Number"
                    value={formData.mobile}
                    onChange={(e) => setFormData({ ...formData, mobile: e.target.value })}
                    disabled={!editMode}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Alternate Mobile"
                    value={formData.alternate_mobile}
                    onChange={(e) => setFormData({ ...formData, alternate_mobile: e.target.value })}
                    disabled={!editMode}
                  />
                </Grid>
              </Grid>

              <Typography variant="h6" gutterBottom sx={{ mt: 4 }}>
                Emergency Contact
              </Typography>
              <Divider sx={{ mb: 3 }} />
              
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Contact Name"
                    value={formData.emergency_contact_name}
                    onChange={(e) => setFormData({ ...formData, emergency_contact_name: e.target.value })}
                    disabled={!editMode}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Contact Number"
                    value={formData.emergency_contact_number}
                    onChange={(e) => setFormData({ ...formData, emergency_contact_number: e.target.value })}
                    disabled={!editMode}
                  />
                </Grid>
              </Grid>

              <Typography variant="h6" gutterBottom sx={{ mt: 4 }}>
                Current Address
              </Typography>
              <Divider sx={{ mb: 3 }} />
              
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Address Line 1"
                    value={formData.current_address_line1}
                    onChange={(e) => setFormData({ ...formData, current_address_line1: e.target.value })}
                    disabled={!editMode}
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Address Line 2"
                    value={formData.current_address_line2}
                    onChange={(e) => setFormData({ ...formData, current_address_line2: e.target.value })}
                    disabled={!editMode}
                  />
                </Grid>
                <Grid item xs={12} sm={4}>
                  <TextField
                    fullWidth
                    label="City"
                    value={formData.current_city}
                    onChange={(e) => setFormData({ ...formData, current_city: e.target.value })}
                    disabled={!editMode}
                  />
                </Grid>
                <Grid item xs={12} sm={4}>
                  <TextField
                    fullWidth
                    label="State"
                    value={formData.current_state}
                    onChange={(e) => setFormData({ ...formData, current_state: e.target.value })}
                    disabled={!editMode}
                  />
                </Grid>
                <Grid item xs={12} sm={4}>
                  <TextField
                    fullWidth
                    label="Pincode"
                    value={formData.current_pincode}
                    onChange={(e) => setFormData({ ...formData, current_pincode: e.target.value })}
                    disabled={!editMode}
                  />
                </Grid>
              </Grid>

              <Typography variant="h6" gutterBottom sx={{ mt: 4 }}>
                Bank Details
              </Typography>
              <Divider sx={{ mb: 3 }} />
              
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Bank Name"
                    value={formData.salary_bank_name}
                    onChange={(e) => setFormData({ ...formData, salary_bank_name: e.target.value })}
                    disabled={!editMode}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Account Number"
                    value={formData.salary_account_number}
                    onChange={(e) => setFormData({ ...formData, salary_account_number: e.target.value })}
                    disabled={!editMode}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="IFSC Code"
                    value={formData.salary_ifsc_code}
                    onChange={(e) => setFormData({ ...formData, salary_ifsc_code: e.target.value })}
                    disabled={!editMode}
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Profile;
