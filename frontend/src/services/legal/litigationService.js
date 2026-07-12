/**
 * Legal - Litigation Management API Service
 * Handles all API calls for case tracking, hearing management, and legal expense tracking
 */

import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const LITIGATION_API = `${API_BASE_URL}/api/v1/legal/litigation`;

// Configure axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ============================================================================
// CASE MANAGEMENT API
// ============================================================================

/**
 * Create a new litigation case
 */
export const createCase = async (caseData) => {
  const response = await apiClient.post(`${LITIGATION_API}/cases`, caseData);
  return response.data;
};

/**
 * Get a case by ID
 */
export const getCase = async (caseId, includeDetails = false) => {
  const response = await apiClient.get(`${LITIGATION_API}/cases/${caseId}`, {
    params: { include_details: includeDetails },
  });
  return response.data;
};

/**
 * Get all cases with filters
 */
export const getCases = async (filters = {}) => {
  const response = await apiClient.get(`${LITIGATION_API}/cases`, {
    params: filters,
  });
  return response.data;
};

/**
 * Update a case
 */
export const updateCase = async (caseId, caseData) => {
  const response = await apiClient.put(`${LITIGATION_API}/cases/${caseId}`, caseData);
  return response.data;
};

/**
 * Delete a case
 */
export const deleteCase = async (caseId) => {
  const response = await apiClient.delete(`${LITIGATION_API}/cases/${caseId}`);
  return response.data;
};

// ============================================================================
// HEARING MANAGEMENT API
// ============================================================================

/**
 * Create a new hearing
 */
export const createHearing = async (hearingData) => {
  const response = await apiClient.post(`${LITIGATION_API}/hearings`, hearingData);
  return response.data;
};

/**
 * Get hearings for a case
 */
export const getCaseHearings = async (caseId, filters = {}) => {
  const response = await apiClient.get(`${LITIGATION_API}/cases/${caseId}/hearings`, {
    params: filters,
  });
  return response.data;
};

/**
 * Get upcoming hearings
 */
export const getUpcomingHearings = async (days = 30, filters = {}) => {
  const response = await apiClient.get(`${LITIGATION_API}/hearings/upcoming`, {
    params: { days, ...filters },
  });
  return response.data;
};

/**
 * Update a hearing
 */
export const updateHearing = async (hearingId, hearingData) => {
  const response = await apiClient.put(`${LITIGATION_API}/hearings/${hearingId}`, hearingData);
  return response.data;
};

// ============================================================================
// EXPENSE MANAGEMENT API
// ============================================================================

/**
 * Create a new legal expense
 */
export const createExpense = async (expenseData) => {
  const response = await apiClient.post(`${LITIGATION_API}/expenses`, expenseData);
  return response.data;
};

/**
 * Get expenses for a case
 */
export const getCaseExpenses = async (caseId, filters = {}) => {
  const response = await apiClient.get(`${LITIGATION_API}/cases/${caseId}/expenses`, {
    params: filters,
  });
  return response.data;
};

/**
 * Update an expense
 */
export const updateExpense = async (expenseId, expenseData) => {
  const response = await apiClient.put(`${LITIGATION_API}/expenses/${expenseId}`, expenseData);
  return response.data;
};

/**
 * Approve an expense
 */
export const approveExpense = async (expenseId, remarks = null) => {
  const response = await apiClient.post(`${LITIGATION_API}/expenses/${expenseId}/approve`, {
    remarks,
  });
  return response.data;
};

/**
 * Mark an expense as paid
 */
export const markExpensePaid = async (expenseId, paymentDate, paymentReference = null) => {
  const response = await apiClient.post(`${LITIGATION_API}/expenses/${expenseId}/mark-paid`, {
    payment_date: paymentDate,
    payment_reference: paymentReference,
  });
  return response.data;
};

// ============================================================================
// PARTY MANAGEMENT API
// ============================================================================

/**
 * Create a new case party
 */
export const createParty = async (partyData) => {
  const response = await apiClient.post(`${LITIGATION_API}/parties`, partyData);
  return response.data;
};

/**
 * Get parties for a case
 */
export const getCaseParties = async (caseId) => {
  const response = await apiClient.get(`${LITIGATION_API}/cases/${caseId}/parties`);
  return response.data;
};

// ============================================================================
// STATISTICS & ANALYTICS API
// ============================================================================

/**
 * Get litigation statistics
 */
export const getStatistics = async () => {
  const response = await apiClient.get(`${LITIGATION_API}/statistics`);
  return response.data;
};

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Format currency
 */
export const formatCurrency = (amount, currency = 'INR') => {
  if (!amount) return '₹0.00';
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 2,
  }).format(amount);
};

/**
 * Format date
 */
export const formatDate = (date) => {
  if (!date) return '-';
  return new Date(date).toLocaleDateString('en-IN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
};

/**
 * Format datetime
 */
export const formatDateTime = (datetime) => {
  if (!datetime) return '-';
  return new Date(datetime).toLocaleString('en-IN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

/**
 * Get case status badge color
 */
export const getCaseStatusColor = (status) => {
  const colors = {
    filed: 'blue',
    admitted: 'cyan',
    in_progress: 'orange',
    evidence_stage: 'purple',
    argument_stage: 'purple',
    judgment_reserved: 'yellow',
    judgment_delivered: 'blue',
    disposed: 'gray',
    won: 'green',
    lost: 'red',
    settled: 'teal',
    withdrawn: 'gray',
    dismissed: 'gray',
    appealed: 'orange',
    stayed: 'yellow',
  };
  return colors[status] || 'gray';
};

/**
 * Get priority color
 */
export const getPriorityColor = (priority) => {
  const colors = {
    low: 'green',
    medium: 'blue',
    high: 'orange',
    critical: 'red',
    urgent: 'red',
  };
  return colors[priority] || 'gray';
};

/**
 * Get hearing status color
 */
export const getHearingStatusColor = (status) => {
  const colors = {
    scheduled: 'blue',
    rescheduled: 'yellow',
    completed: 'green',
    adjourned: 'orange',
    cancelled: 'red',
    no_show: 'red',
  };
  return colors[status] || 'gray';
};

export default {
  createCase,
  getCase,
  getCases,
  updateCase,
  deleteCase,
  createHearing,
  getCaseHearings,
  getUpcomingHearings,
  updateHearing,
  createExpense,
  getCaseExpenses,
  updateExpense,
  approveExpense,
  markExpensePaid,
  createParty,
  getCaseParties,
  getStatistics,
  formatCurrency,
  formatDate,
  formatDateTime,
  getCaseStatusColor,
  getPriorityColor,
  getHearingStatusColor,
};
