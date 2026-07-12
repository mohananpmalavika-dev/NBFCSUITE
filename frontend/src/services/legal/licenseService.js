/**
 * License Management Service
 * API calls for license operations, renewals, and compliance tracking
 */

import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const LICENSE_API = `${API_BASE_URL}/api/v1/legal/licenses`;

// Get authentication token
const getAuthToken = () => {
  return localStorage.getItem('token') || '';
};

// Configure axios defaults
const axiosConfig = () => ({
  headers: {
    Authorization: `Bearer ${getAuthToken()}`,
    'Content-Type': 'application/json',
  },
});

// ============================================
// LICENSE CRUD OPERATIONS
// ============================================

/**
 * Get all licenses with filtering and pagination
 */
export const getLicenses = async (params = {}) => {
  try {
    const response = await axios.get(LICENSE_API, {
      ...axiosConfig(),
      params,
    });
    return {
      success: true,
      data: response.data,
    };
  } catch (error) {
    console.error('Error fetching licenses:', error);
    return {
      success: false,
      error: error.response?.data?.message || 'Failed to fetch licenses',
    };
  }
};

/**
 * Get license by ID
 */
export const getLicenseById = async (licenseId) => {
  try {
    const response = await axios.get(`${LICENSE_API}/${licenseId}`, axiosConfig());
    return {
      success: true,
      data: response.data,
    };
  } catch (error) {
    console.error('Error fetching license:', error);
    return {
      success: false,
      error: error.response?.data?.message || 'Failed to fetch license',
    };
  }
};

/**
 * Create new license
 */
export const createLicense = async (licenseData) => {
  try {
    const response = await axios.post(LICENSE_API, licenseData, axiosConfig());
    return {
      success: true,
      data: response.data,
    };
  } catch (error) {
    console.error('Error creating license:', error);
    return {
      success: false,
      error: error.response?.data?.message || 'Failed to create license',
    };
  }
};

/**
 * Update license
 */
export const updateLicense = async (licenseId, licenseData) => {
  try {
    const response = await axios.patch(
      `${LICENSE_API}/${licenseId}`,
      licenseData,
      axiosConfig()
    );
    return {
      success: true,
      data: response.data,
    };
  } catch (error) {
    console.error('Error updating license:', error);
    return {
      success: false,
      error: error.response?.data?.message || 'Failed to update license',
    };
  }
};

/**
 * Delete license
 */
export const deleteLicense = async (licenseId) => {
  try {
    await axios.delete(`${LICENSE_API}/${licenseId}`, axiosConfig());
    return {
      success: true,
    };
  } catch (error) {
    console.error('Error deleting license:', error);
    return {
      success: false,
      error: error.response?.data?.message || 'Failed to delete license',
    };
  }
};

// ============================================
// STATISTICS & ANALYTICS
// ============================================

/**
 * Get license statistics
 */
export const getStatistics = async () => {
  try {
    const response = await axios.get(
      `${LICENSE_API}/statistics`,
      axiosConfig()
    );
    return {
      success: true,
      data: response.data,
    };
  } catch (error) {
    console.error('Error fetching statistics:', error);
    return {
      success: false,
      error: error.response?.data?.message || 'Failed to fetch statistics',
    };
  }
};

/**
 * Get expiring licenses
 */
export const getExpiringLicenses = async (days = 30) => {
  try {
    const response = await axios.get(`${LICENSE_API}/expiring`, {
      ...axiosConfig(),
      params: { days },
    });
    return {
      success: true,
      data: response.data,
    };
  } catch (error) {
    console.error('Error fetching expiring licenses:', error);
    return {
      success: false,
      error:
        error.response?.data?.message || 'Failed to fetch expiring licenses',
    };
  }
};

/**
 * Get non-compliant licenses
 */
export const getNonCompliantLicenses = async () => {
  try {
    const response = await axios.get(
      `${LICENSE_API}/non-compliant`,
      axiosConfig()
    );
    return {
      success: true,
      data: response.data,
    };
  } catch (error) {
    console.error('Error fetching non-compliant licenses:', error);
    return {
      success: false,
      error:
        error.response?.data?.message ||
        'Failed to fetch non-compliant licenses',
    };
  }
};

// ============================================
// RENEWAL OPERATIONS
// ============================================

/**
 * Create renewal record
 */
export const createRenewal = async (licenseId, renewalData) => {
  try {
    const response = await axios.post(
      `${LICENSE_API}/${licenseId}/renewals`,
      renewalData,
      axiosConfig()
    );
    return {
      success: true,
      data: response.data,
    };
  } catch (error) {
    console.error('Error creating renewal:', error);
    return {
      success: false,
      error: error.response?.data?.message || 'Failed to create renewal',
    };
  }
};

/**
 * Update renewal record
 */
export const updateRenewal = async (renewalId, renewalData) => {
  try {
    const response = await axios.patch(
      `${LICENSE_API}/renewals/${renewalId}`,
      renewalData,
      axiosConfig()
    );
    return {
      success: true,
      data: response.data,
    };
  } catch (error) {
    console.error('Error updating renewal:', error);
    return {
      success: false,
      error: error.response?.data?.message || 'Failed to update renewal',
    };
  }
};

/**
 * Get renewal history for a license
 */
export const getRenewals = async (licenseId) => {
  try {
    const response = await axios.get(
      `${LICENSE_API}/${licenseId}/renewals`,
      axiosConfig()
    );
    return {
      success: true,
      data: response.data,
    };
  } catch (error) {
    console.error('Error fetching renewals:', error);
    return {
      success: false,
      error: error.response?.data?.message || 'Failed to fetch renewals',
    };
  }
};

// ============================================
// COMPLIANCE OPERATIONS
// ============================================

/**
 * Create compliance check
 */
export const createComplianceCheck = async (licenseId, checkData) => {
  try {
    const response = await axios.post(
      `${LICENSE_API}/${licenseId}/compliance-checks`,
      checkData,
      axiosConfig()
    );
    return {
      success: true,
      data: response.data,
    };
  } catch (error) {
    console.error('Error creating compliance check:', error);
    return {
      success: false,
      error:
        error.response?.data?.message || 'Failed to create compliance check',
    };
  }
};

/**
 * Update compliance check
 */
export const updateComplianceCheck = async (checkId, checkData) => {
  try {
    const response = await axios.patch(
      `${LICENSE_API}/compliance-checks/${checkId}`,
      checkData,
      axiosConfig()
    );
    return {
      success: true,
      data: response.data,
    };
  } catch (error) {
    console.error('Error updating compliance check:', error);
    return {
      success: false,
      error:
        error.response?.data?.message || 'Failed to update compliance check',
    };
  }
};

/**
 * Get compliance check history for a license
 */
export const getComplianceChecks = async (licenseId) => {
  try {
    const response = await axios.get(
      `${LICENSE_API}/${licenseId}/compliance-checks`,
      axiosConfig()
    );
    return {
      success: true,
      data: response.data,
    };
  } catch (error) {
    console.error('Error fetching compliance checks:', error);
    return {
      success: false,
      error:
        error.response?.data?.message || 'Failed to fetch compliance checks',
    };
  }
};

// ============================================
// DOCUMENT OPERATIONS
// ============================================

/**
 * Add document to license
 */
export const addDocument = async (licenseId, documentData) => {
  try {
    const response = await axios.post(
      `${LICENSE_API}/${licenseId}/documents`,
      documentData,
      axiosConfig()
    );
    return {
      success: true,
      data: response.data,
    };
  } catch (error) {
    console.error('Error adding document:', error);
    return {
      success: false,
      error: error.response?.data?.message || 'Failed to add document',
    };
  }
};

/**
 * Get documents for a license
 */
export const getDocuments = async (licenseId) => {
  try {
    const response = await axios.get(
      `${LICENSE_API}/${licenseId}/documents`,
      axiosConfig()
    );
    return {
      success: true,
      data: response.data,
    };
  } catch (error) {
    console.error('Error fetching documents:', error);
    return {
      success: false,
      error: error.response?.data?.message || 'Failed to fetch documents',
    };
  }
};

// ============================================
// REMINDER OPERATIONS
// ============================================

/**
 * Create reminder
 */
export const createReminder = async (licenseId, reminderData) => {
  try {
    const response = await axios.post(
      `${LICENSE_API}/${licenseId}/reminders`,
      reminderData,
      axiosConfig()
    );
    return {
      success: true,
      data: response.data,
    };
  } catch (error) {
    console.error('Error creating reminder:', error);
    return {
      success: false,
      error: error.response?.data?.message || 'Failed to create reminder',
    };
  }
};

/**
 * Get reminders for a license
 */
export const getReminders = async (licenseId) => {
  try {
    const response = await axios.get(
      `${LICENSE_API}/${licenseId}/reminders`,
      axiosConfig()
    );
    return {
      success: true,
      data: response.data,
    };
  } catch (error) {
    console.error('Error fetching reminders:', error);
    return {
      success: false,
      error: error.response?.data?.message || 'Failed to fetch reminders',
    };
  }
};

// ============================================
// UTILITY FUNCTIONS
// ============================================

/**
 * Format currency
 */
export const formatCurrency = (amount, currency = 'INR') => {
  if (amount === null || amount === undefined) return '-';
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
};

/**
 * Format date
 */
export const formatDate = (dateString) => {
  if (!dateString) return '-';
  const date = new Date(dateString);
  return date.toLocaleDateString('en-IN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
};

/**
 * Format datetime
 */
export const formatDateTime = (dateString) => {
  if (!dateString) return '-';
  const date = new Date(dateString);
  return date.toLocaleString('en-IN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

/**
 * Get license status color
 */
export const getLicenseStatusColor = (status) => {
  const colors = {
    active: 'green',
    pending_renewal: 'orange',
    expired: 'red',
    suspended: 'volcano',
    cancelled: 'default',
    revoked: 'red',
    under_review: 'blue',
    applied: 'cyan',
    rejected: 'red',
  };
  return colors[status] || 'default';
};

/**
 * Get renewal status color
 */
export const getRenewalStatusColor = (status) => {
  const colors = {
    not_required: 'default',
    pending: 'orange',
    in_progress: 'blue',
    submitted: 'cyan',
    approved: 'green',
    completed: 'green',
    rejected: 'red',
  };
  return colors[status] || 'default';
};

/**
 * Get compliance status color
 */
export const getComplianceStatusColor = (status) => {
  const colors = {
    compliant: 'green',
    non_compliant: 'red',
    partially_compliant: 'orange',
    review_required: 'blue',
    not_applicable: 'default',
  };
  return colors[status] || 'default';
};

/**
 * Export licenses to CSV
 */
export const exportLicenses = async (filters = {}) => {
  try {
    const response = await axios.get(`${LICENSE_API}/export`, {
      ...axiosConfig(),
      params: filters,
      responseType: 'blob',
    });

    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `licenses_${new Date().toISOString()}.csv`);
    document.body.appendChild(link);
    link.click();
    link.remove();

    return {
      success: true,
    };
  } catch (error) {
    console.error('Error exporting licenses:', error);
    return {
      success: false,
      error: error.response?.data?.message || 'Failed to export licenses',
    };
  }
};

export default {
  getLicenses,
  getLicenseById,
  createLicense,
  updateLicense,
  deleteLicense,
  getStatistics,
  getExpiringLicenses,
  getNonCompliantLicenses,
  createRenewal,
  updateRenewal,
  getRenewals,
  createComplianceCheck,
  updateComplianceCheck,
  getComplianceChecks,
  addDocument,
  getDocuments,
  createReminder,
  getReminders,
  formatCurrency,
  formatDate,
  formatDateTime,
  getLicenseStatusColor,
  getRenewalStatusColor,
  getComplianceStatusColor,
  exportLicenses,
};
