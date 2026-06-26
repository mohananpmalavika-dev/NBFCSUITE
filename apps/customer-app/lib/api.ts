
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
});

export const apiClient = {
  setToken: (token: string) => {
    axiosInstance.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  },
  clearToken: () => {
    delete axiosInstance.defaults.headers.common['Authorization'];
  },

  // Auth Service
  login: (username, password) =>
    axiosInstance.post(`/auth/token`, { username, password }),
  getUser: (userId) =>
    axiosInstance.get(`/auth/users/${userId}`),

  // Customer Service
  getCustomer: (customerId) =>
    axiosInstance.get(`/customer/${customerId}`),
  updateCustomer: (customerId, data) =>
    axiosInstance.put(`/customer/${customerId}`, data),
  getFinancialProfile: (customerId) =>
    axiosInstance.get(`/customer/${customerId}/financial-profile`),
  updateFinancialProfile: (customerId, data) =>
    axiosInstance.post(`/customer/${customerId}/financial-profile`, data),

  // LOS Service
  getLoanProducts: () =>
    axiosInstance.get(`/los/products`),
  applyForLoan: (data) =>
    axiosInstance.post(`/los/applications`, data),

  // LMS Service
  getCustomerLoans: (customerId) =>
    axiosInstance.get(`/lms/loans/customer/${customerId}`),
  getLoanPayments: (loanId) =>
    axiosInstance.get(`/lms/payments/loan/${loanId}`),
  makePayment: (loanId, data) =>
    axiosInstance.post(`/lms/payments/loan/${loanId}`, data),
};