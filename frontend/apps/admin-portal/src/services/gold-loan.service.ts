/**
 * Gold Loan Service
 * API calls for gold loan management
 */

import { apiClient } from '@/lib/api-client';

// ============================================
// Types & Interfaces
// ============================================

export interface GoldLoanProduct {
  id: string;
  product_code: string;
  product_name: string;
  description?: string;
  interest_rate_min: number;
  interest_rate_max: number;
  default_interest_rate: number;
  ltv_ratio: number;
  max_ltv_ratio: number;
  min_loan_amount: number;
  max_loan_amount: number;
  min_tenure_months: number;
  max_tenure_months: number;
  default_tenure_months: number;
  processing_fee_percentage: number;
  processing_fee_flat: number;
  valuation_charges: number;
  documentation_charges: number;
  storage_charges_monthly: number;
  penal_interest_rate: number;
  repayment_frequency: string;
  partial_release_allowed: boolean;
  top_up_allowed: boolean;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface GoldOrnament {
  id?: string;
  gold_loan_id?: string;
  item_number?: number;
  ornament_type: string;
  ornament_description?: string;
  quantity: number;
  purity_karat: number;
  purity_percentage: number;
  gross_weight_grams: number;
  stone_weight_grams: number;
  net_weight_grams: number;
  gold_rate_per_gram: number;
  market_value: number;
  appraised_value: number;
  hallmark_available: boolean;
  hallmark_number?: string;
  photo_url?: string;
  status?: string;
  released_weight_grams?: number;
  remaining_weight_grams?: number;
  remarks?: string;
  created_at?: string;
}

export interface GoldLoanAccount {
  id: string;
  loan_account_number: string;
  customer_id: string;
  product_id: string;
  application_id?: string;
  application_date: string;
  loan_amount: number;
  sanctioned_amount: number;
  disbursed_amount: number;
  total_gold_weight_grams: number;
  total_gold_value: number;
  average_gold_rate: number;
  ltv_ratio: number;
  interest_rate: number;
  penal_interest_rate: number;
  tenure_months: number;
  start_date: string;
  maturity_date: string;
  repayment_frequency: string;
  emi_amount?: number;
  processing_fee: number;
  valuation_charges: number;
  documentation_charges: number;
  insurance_charges: number;
  principal_outstanding: number;
  interest_outstanding: number;
  penal_interest_outstanding: number;
  total_outstanding: number;
  status: string;
  days_past_due: number;
  overdue_amount: number;
  is_npa: boolean;
  approval_date?: string;
  disbursement_date?: string;
  closure_date?: string;
  created_at: string;
  updated_at: string;
}

export interface GoldLoanTransaction {
  id: string;
  transaction_number: string;
  gold_loan_id: string;
  transaction_date: string;
  transaction_type: string;
  amount: number;
  principal_amount: number;
  interest_amount: number;
  penal_interest_amount: number;
  charges_amount: number;
  payment_mode?: string;
  payment_reference?: string;
  principal_balance: number;
  interest_balance: number;
  total_balance: number;
  status: string;
  created_by: string;
  remarks?: string;
  created_at: string;
}

export interface GoldReleaseRequest {
  id: string;
  request_number: string;
  gold_loan_id: string;
  customer_id: string;
  release_type: string;
  total_release_weight_grams: number;
  total_release_value: number;
  payment_amount: number;
  new_loan_amount?: number;
  new_ltv_ratio?: number;
  request_date: string;
  requested_by: string;
  approval_status: string;
  approved_by?: string;
  approval_date?: string;
  approval_remarks?: string;
  status: string;
  remarks?: string;
  created_at: string;
}

export interface GoldLoanStatistics {
  total_loans: number;
  active_loans: number;
  total_disbursed: number;
  total_outstanding: number;
  total_gold_weight_kg: number;
  average_ltv_ratio: number;
  npa_count: number;
  npa_amount: number;
  overdue_count: number;
  overdue_amount: number;
}

// ============================================
// Product Management
// ============================================

export async function getGoldLoanProducts(isActive?: boolean) {
  const params = isActive !== undefined ? { is_active: isActive } : {};
  const response = await apiClient.get<{ products: GoldLoanProduct[]; total: number }>(
    '/gold-loans/products',
    { params }
  );
  return response.data;
}

export async function getGoldLoanProduct(productId: string) {
  const response = await apiClient.get<GoldLoanProduct>(`/gold-loans/products/${productId}`);
  return response.data;
}

export async function createGoldLoanProduct(data: Partial<GoldLoanProduct>) {
  const response = await apiClient.post<GoldLoanProduct>('/gold-loans/products', data);
  return response.data;
}

export async function updateGoldLoanProduct(productId: string, data: Partial<GoldLoanProduct>) {
  const response = await apiClient.put<GoldLoanProduct>(`/gold-loans/products/${productId}`, data);
  return response.data;
}

// ============================================
// Gold Loan Account Management
// ============================================

export interface CreateGoldLoanData {
  customer_id: string;
  product_id: string;
  loan_amount: number;
  tenure_months: number;
  repayment_frequency: string;
  ornaments: GoldOrnament[];
  branch_id?: string;
  remarks?: string;
}

export async function createGoldLoan(data: CreateGoldLoanData) {
  const response = await apiClient.post<{
    loan: GoldLoanAccount;
    ornaments: GoldOrnament[];
  }>('/gold-loans/accounts', data);
  return response.data;
}

export interface GoldLoanListParams {
  page?: number;
  page_size?: number;
  status?: string;
  customer_id?: string;
  branch_id?: string;
  is_npa?: boolean;
  search?: string;
}

export async function getGoldLoans(params: GoldLoanListParams = {}) {
  const response = await apiClient.get<{
    loans: GoldLoanAccount[];
    total: number;
    page: number;
    page_size: number;
    total_pages: number;
  }>('/gold-loans/accounts', { params });
  return response.data;
}

export async function getGoldLoan(loanId: string) {
  const response = await apiClient.get<{
    loan: GoldLoanAccount;
    ornaments: GoldOrnament[];
  }>(`/gold-loans/accounts/${loanId}`);
  return response.data;
}

// ============================================
// Payment Management
// ============================================

export interface RecordPaymentData {
  transaction_type: string;
  amount: number;
  principal_amount: number;
  interest_amount: number;
  penal_interest_amount: number;
  charges_amount: number;
  payment_mode?: string;
  payment_reference?: string;
  bank_name?: string;
  cheque_number?: string;
  transaction_id?: string;
  remarks?: string;
}

export async function recordPayment(loanId: string, data: RecordPaymentData) {
  const response = await apiClient.post<GoldLoanTransaction>(
    `/gold-loans/accounts/${loanId}/payments`,
    data
  );
  return response.data;
}

// ============================================
// Gold Release Management
// ============================================

export interface CreateReleaseRequestData {
  release_type: string;
  ornament_ids: string[];
  payment_amount: number;
  payment_mode?: string;
  payment_reference?: string;
  remarks?: string;
}

export async function createReleaseRequest(loanId: string, data: CreateReleaseRequestData) {
  const response = await apiClient.post<GoldReleaseRequest>(
    `/gold-loans/accounts/${loanId}/release`,
    data
  );
  return response.data;
}

// ============================================
// Statistics & Utilities
// ============================================

export async function getGoldLoanStatistics() {
  const response = await apiClient.get<GoldLoanStatistics>('/gold-loans/statistics');
  return response.data;
}

export async function getOrnamentTypes() {
  const response = await apiClient.get<{ ornament_types: string[] }>('/gold-loans/ornament-types');
  return response.data;
}

export async function getPurityOptions() {
  const response = await apiClient.get<{
    purity_options: Array<{ karat: number; percentage: number; label: string }>;
  }>('/gold-loans/purity-options');
  return response.data;
}

export async function calculateLTV(goldValue: number, loanAmount: number) {
  const response = await apiClient.post<{
    gold_value: number;
    loan_amount: number;
    ltv_ratio: number;
    is_valid: boolean;
  }>('/gold-loans/calculate-ltv', null, {
    params: { gold_value: goldValue, loan_amount: loanAmount }
  });
  return response.data;
}
