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

// ============================================
// Gold Rate Management
// ============================================

export interface GoldRate {
  id: string;
  rate_date: string;
  rate_type: string;
  source: string;
  gold_24k_per_gram: number;
  gold_22k_per_gram: number;
  gold_18k_per_gram: number;
  currency: string;
  is_current: boolean;
  version: number;
  effective_from: string;
  effective_to?: string;
  created_by: string;
  created_at: string;
}

export interface GoldRateStatistics {
  current_rate: GoldRate;
  previous_rate: GoldRate;
  change_amount: number;
  change_percentage: number;
  highest_rate_30_days: number;
  lowest_rate_30_days: number;
  average_rate_30_days: number;
}

export async function getCurrentGoldRates() {
  const response = await apiClient.get<GoldRate>('/gold-loans/gold-rates/current');
  return response.data;
}

export async function updateLiveGoldRates(source: string = 'IBJA') {
  const response = await apiClient.post<GoldRate>('/gold-loans/gold-rates/update-live', null, {
    params: { source }
  });
  return response.data;
}

export async function createManualGoldRate(data: {
  gold_24k_per_gram: number;
  gold_22k_per_gram: number;
  gold_18k_per_gram: number;
  source?: string;
  remarks?: string;
}) {
  const response = await apiClient.post<GoldRate>('/gold-loans/gold-rates/', data);
  return response.data;
}

export async function getGoldRateHistory(params: {
  start_date?: string;
  end_date?: string;
  source?: string;
  page?: number;
  page_size?: number;
}) {
  const response = await apiClient.get<{
    rates: GoldRate[];
    total: number;
    page: number;
    page_size: number;
  }>('/gold-loans/gold-rates/', { params });
  return response.data;
}

export async function getGoldRateStatistics() {
  const response = await apiClient.get<GoldRateStatistics>('/gold-loans/gold-rates/statistics/summary');
  return response.data;
}

export async function calculateGoldValue(data: {
  weight_grams: number;
  karat: number;
  rate_per_gram?: number;
}) {
  const response = await apiClient.get<{
    weight_grams: number;
    karat: number;
    rate_per_gram: number;
    gold_value: number;
  }>('/gold-loans/gold-rates/calculate/value', { params: data });
  return response.data;
}

// ============================================
// Vault Management
// ============================================

export interface VaultLocation {
  id: string;
  vault_code: string;
  vault_name: string;
  vault_type: string;
  location_type: string;
  branch_id?: string;
  address_line1?: string;
  city?: string;
  state?: string;
  pincode?: string;
  physical_location?: string;
  max_capacity_items: number;
  max_capacity_weight_kg: number;
  current_item_count: number;
  current_weight_kg: number;
  security_level: string;
  insurance_value?: number;
  insurance_policy_number?: string;
  access_control?: string;
  is_active: boolean;
  created_at: string;
}

export interface VaultInventory {
  id: string;
  vault_location_id: string;
  gold_loan_id: string;
  customer_id: string;
  ornament_id: string;
  check_in_date: string;
  check_in_by: string;
  check_out_date?: string;
  check_out_by?: string;
  barcode?: string;
  rfid_tag?: string;
  seal_number?: string;
  rack_number?: string;
  shelf_number?: string;
  slot_number?: string;
  weight_grams: number;
  status: string;
  remarks?: string;
  created_at: string;
}

export interface VaultTransfer {
  id: string;
  transfer_number: string;
  from_vault_id: string;
  to_vault_id: string;
  inventory_ids: string[];
  transfer_date: string;
  requested_by: string;
  approved_by?: string;
  approval_date?: string;
  status: string;
  reason?: string;
  total_items: number;
  total_weight_kg: number;
  remarks?: string;
  created_at: string;
}

export async function createVaultLocation(data: Partial<VaultLocation>) {
  const response = await apiClient.post<VaultLocation>('/gold-loans/vaults/locations', data);
  return response.data;
}

export async function getVaultLocations(params?: { is_active?: boolean; branch_id?: string }) {
  const response = await apiClient.get<{ locations: VaultLocation[]; total: number }>(
    '/gold-loans/vaults/locations',
    { params }
  );
  return response.data;
}

export async function getVaultLocation(vaultId: string) {
  const response = await apiClient.get<VaultLocation>(`/gold-loans/vaults/locations/${vaultId}`);
  return response.data;
}

export async function checkInToVault(data: {
  vault_location_id: string;
  gold_loan_id: string;
  customer_id: string;
  ornament_id: string;
  barcode?: string;
  rfid_tag?: string;
  seal_number?: string;
  rack_number?: string;
  shelf_number?: string;
  slot_number?: string;
  remarks?: string;
}) {
  const response = await apiClient.post<VaultInventory>('/gold-loans/vaults/inventory/check-in', data);
  return response.data;
}

export async function checkOutFromVault(inventoryId: string, remarks?: string) {
  const response = await apiClient.post<VaultInventory>(
    `/gold-loans/vaults/inventory/${inventoryId}/check-out`,
    { remarks }
  );
  return response.data;
}

export async function getVaultInventory(params: {
  vault_location_id?: string;
  gold_loan_id?: string;
  status?: string;
  page?: number;
  page_size?: number;
}) {
  const response = await apiClient.get<{
    inventory: VaultInventory[];
    total: number;
    page: number;
    page_size: number;
  }>('/gold-loans/vaults/inventory', { params });
  return response.data;
}

export async function createVaultTransfer(data: {
  from_vault_id: string;
  to_vault_id: string;
  inventory_ids: string[];
  reason?: string;
  remarks?: string;
}) {
  const response = await apiClient.post<VaultTransfer>('/gold-loans/vaults/transfers', data);
  return response.data;
}

export async function approveVaultTransfer(transferId: string, remarks?: string) {
  const response = await apiClient.post<VaultTransfer>(
    `/gold-loans/vaults/transfers/${transferId}/approve`,
    { remarks }
  );
  return response.data;
}

export async function getVaultCapacity(vaultId: string) {
  const response = await apiClient.get<{
    vault: VaultLocation;
    current_items: number;
    current_weight_kg: number;
    capacity_items_percentage: number;
    capacity_weight_percentage: number;
    available_items: number;
    available_weight_kg: number;
  }>(`/gold-loans/vaults/locations/${vaultId}/capacity`);
  return response.data;
}

export async function performVaultAudit(vaultId: string) {
  const response = await apiClient.post<{
    vault_id: string;
    audit_date: string;
    expected_items: number;
    found_items: number;
    missing_items: number;
    discrepancies: any[];
    status: string;
  }>(`/gold-loans/vaults/inventory/audit/${vaultId}`);
  return response.data;
}

// ============================================
// Purity Testing
// ============================================

export interface PurityTest {
  id: string;
  test_number: string;
  gold_loan_id: string;
  ornament_id: string;
  test_date: string;
  test_method: string;
  claimed_purity_karat: number;
  claimed_purity_percentage: number;
  tested_purity_karat: number;
  tested_purity_percentage: number;
  variance_percentage: number;
  test_result: string;
  equipment_id?: string;
  equipment_calibration_date?: string;
  tester_name: string;
  tester_license?: string;
  lab_name?: string;
  certificate_number?: string;
  test_report_url?: string;
  remarks?: string;
  created_at: string;
}

export interface PurityTestStatistics {
  total_tests: number;
  pass_count: number;
  fail_count: number;
  variance_acceptable_count: number;
  average_variance: number;
  tests_by_method: Record<string, number>;
}

export async function createPurityTest(data: {
  gold_loan_id: string;
  ornament_id: string;
  test_method: string;
  claimed_purity_karat: number;
  claimed_purity_percentage: number;
  tested_purity_karat: number;
  tested_purity_percentage: number;
  equipment_id?: string;
  equipment_calibration_date?: string;
  tester_name: string;
  tester_license?: string;
  lab_name?: string;
  remarks?: string;
}) {
  const response = await apiClient.post<PurityTest>('/gold-loans/purity-tests/', data);
  return response.data;
}

export async function bulkTestLoan(loanId: string, data: {
  test_method: string;
  tester_name: string;
  equipment_id?: string;
  tester_license?: string;
}) {
  const response = await apiClient.post<{ tests: PurityTest[]; total_tests: number }>(
    `/gold-loans/purity-tests/bulk-test/${loanId}`,
    data
  );
  return response.data;
}

export async function getPurityTests(params: {
  gold_loan_id?: string;
  ornament_id?: string;
  test_result?: string;
  page?: number;
  page_size?: number;
}) {
  const response = await apiClient.get<{
    tests: PurityTest[];
    total: number;
    page: number;
    page_size: number;
  }>('/gold-loans/purity-tests/', { params });
  return response.data;
}

export async function generatePurityCertificate(testId: string) {
  const response = await apiClient.post<{
    test: PurityTest;
    certificate_url: string;
  }>(`/gold-loans/purity-tests/${testId}/certificate`);
  return response.data;
}

export async function flagPurityDiscrepancy(testId: string, data: {
  action: string;
  remarks?: string;
}) {
  const response = await apiClient.post<PurityTest>(
    `/gold-loans/purity-tests/${testId}/discrepancy`,
    data
  );
  return response.data;
}

export async function getPurityTestStatistics() {
  const response = await apiClient.get<PurityTestStatistics>('/gold-loans/purity-tests/statistics/summary');
  return response.data;
}

// ============================================
// Appraisal Workflow
// ============================================

export interface AppraisalReport {
  id: string;
  appraisal_number: string;
  customer_id: string;
  gold_loan_id?: string;
  ornament_id?: string;
  appraisal_type: string;
  appraisal_date: string;
  ornament_type: string;
  ornament_description?: string;
  photo_urls?: string[];
  video_url?: string;
  verified_karat: number;
  purity_percentage: number;
  gross_weight_grams: number;
  net_weight_grams: number;
  gold_rate_used: number;
  market_value: number;
  appraised_value: number;
  forced_sale_value: number;
  condition: string;
  condition_notes?: string;
  market_comparison?: string;
  appraiser_name: string;
  appraiser_license?: string;
  appraiser_experience_years?: number;
  status: string;
  submitted_date?: string;
  verified_by?: string;
  verification_date?: string;
  verification_remarks?: string;
  certificate_url?: string;
  valid_until?: string;
  remarks?: string;
  created_at: string;
}

export async function createAppraisal(data: {
  customer_id: string;
  gold_loan_id?: string;
  ornament_id?: string;
  appraisal_type: string;
  ornament_type: string;
  ornament_description?: string;
  verified_karat: number;
  purity_percentage: number;
  gross_weight_grams: number;
  net_weight_grams: number;
  condition: string;
  condition_notes?: string;
  appraiser_name: string;
  appraiser_license?: string;
  appraiser_experience_years?: number;
  remarks?: string;
}) {
  const response = await apiClient.post<AppraisalReport>('/gold-loans/appraisals/', data);
  return response.data;
}

export async function submitAppraisal(appraisalId: string) {
  const response = await apiClient.post<AppraisalReport>(
    `/gold-loans/appraisals/${appraisalId}/submit`
  );
  return response.data;
}

export async function verifyAppraisal(appraisalId: string, data: {
  approved: boolean;
  remarks?: string;
}) {
  const response = await apiClient.post<AppraisalReport>(
    `/gold-loans/appraisals/${appraisalId}/verify`,
    data
  );
  return response.data;
}

export async function generateAppraisalCertificate(appraisalId: string) {
  const response = await apiClient.post<{
    appraisal: AppraisalReport;
    certificate_url: string;
  }>(`/gold-loans/appraisals/${appraisalId}/certificate`);
  return response.data;
}

export async function reappraise(appraisalId: string, data: {
  reason: string;
  appraiser_name: string;
  remarks?: string;
}) {
  const response = await apiClient.post<AppraisalReport>(
    `/gold-loans/appraisals/${appraisalId}/reappraise`,
    data
  );
  return response.data;
}

export async function getAppraisals(params: {
  customer_id?: string;
  gold_loan_id?: string;
  status?: string;
  appraisal_type?: string;
  page?: number;
  page_size?: number;
}) {
  const response = await apiClient.get<{
    appraisals: AppraisalReport[];
    total: number;
    page: number;
    page_size: number;
  }>('/gold-loans/appraisals/', { params });
  return response.data;
}

export async function getAppraisalHistory(ornamentId: string) {
  const response = await apiClient.get<{
    ornament_id: string;
    appraisals: AppraisalReport[];
    value_trend: Array<{ date: string; value: number }>;
  }>(`/gold-loans/appraisals/ornament/${ornamentId}/history`);
  return response.data;
}

export async function compareAppraisals(appraisalId1: string, appraisalId2: string) {
  const response = await apiClient.get<{
    appraisal1: AppraisalReport;
    appraisal2: AppraisalReport;
    differences: Record<string, any>;
    value_change: number;
    value_change_percentage: number;
  }>(`/gold-loans/appraisals/compare/${appraisalId1}/${appraisalId2}`);
  return response.data;
}

// ============================================
// Auction Management
// ============================================

export interface Auction {
  id: string;
  auction_number: string;
  gold_loan_id: string;
  customer_id: string;
  auction_type: string;
  auction_date: string;
  auction_venue?: string;
  auction_mode: string;
  reserve_price: number;
  starting_bid: number;
  bid_increment: number;
  registration_deadline: string;
  emd_percentage: number;
  emd_amount: number;
  status: string;
  notice_sent_date?: string;
  notice_period_days: number;
  winning_bid_id?: string;
  winning_amount?: number;
  winner_name?: string;
  sale_completion_date?: string;
  total_proceeds: number;
  loan_settlement_amount: number;
  refund_to_customer: number;
  remarks?: string;
  created_at: string;
}

export interface AuctionBid {
  id: string;
  auction_id: string;
  bidder_name: string;
  bidder_contact: string;
  bidder_email?: string;
  bid_amount: number;
  bid_time: string;
  emd_paid: boolean;
  emd_amount?: number;
  emd_payment_reference?: string;
  bid_rank?: number;
  is_winning_bid: boolean;
  status: string;
  remarks?: string;
  created_at: string;
}

export interface AuctionNotice {
  id: string;
  auction_id: string;
  gold_loan_id: string;
  notice_number: string;
  notice_date: string;
  notice_type: string;
  customer_name: string;
  customer_address?: string;
  loan_account_number: string;
  outstanding_amount: number;
  ornament_details: string;
  auction_date: string;
  delivery_method: string;
  delivery_date?: string;
  delivery_status: string;
  tracking_number?: string;
  received_by?: string;
  received_date?: string;
  response_received: boolean;
  response_date?: string;
  response_details?: string;
  created_at: string;
}

export async function createAuction(data: {
  gold_loan_id: string;
  auction_type?: string;
  auction_date: string;
  auction_venue?: string;
  auction_mode?: string;
  notice_period_days?: number;
  remarks?: string;
}) {
  const response = await apiClient.post<{
    auction: Auction;
    notice: AuctionNotice;
  }>('/gold-loans/auctions/', data);
  return response.data;
}

export async function getAuctions(params: {
  status?: string;
  gold_loan_id?: string;
  page?: number;
  page_size?: number;
}) {
  const response = await apiClient.get<{
    auctions: Auction[];
    total: number;
    page: number;
    page_size: number;
  }>('/gold-loans/auctions/', { params });
  return response.data;
}

export async function getAuction(auctionId: string) {
  const response = await apiClient.get<{
    auction: Auction;
    gold_loan: GoldLoanAccount;
    ornaments: GoldOrnament[];
    bids: AuctionBid[];
    notices: AuctionNotice[];
  }>(`/gold-loans/auctions/${auctionId}`);
  return response.data;
}

export async function startAuction(auctionId: string) {
  const response = await apiClient.post<Auction>(`/gold-loans/auctions/${auctionId}/start`);
  return response.data;
}

export async function registerBidder(auctionId: string, data: {
  bidder_name: string;
  bidder_contact: string;
  bidder_email?: string;
  emd_amount: number;
  emd_payment_reference: string;
}) {
  const response = await apiClient.post<AuctionBid>(
    `/gold-loans/auctions/${auctionId}/register-bidder`,
    data
  );
  return response.data;
}

export async function submitBid(data: {
  auction_id: string;
  bidder_name: string;
  bidder_contact: string;
  bid_amount: number;
  remarks?: string;
}) {
  const response = await apiClient.post<AuctionBid>('/gold-loans/auctions/bids', data);
  return response.data;
}

export async function completeAuction(auctionId: string, data: {
  winning_bid_id: string;
  sale_completion_date: string;
  remarks?: string;
}) {
  const response = await apiClient.post<{
    auction: Auction;
    gold_loan: GoldLoanAccount;
    refund_amount: number;
  }>(`/gold-loans/auctions/${auctionId}/complete`, data);
  return response.data;
}

export async function createAuctionNotice(data: {
  auction_id: string;
  gold_loan_id: string;
  notice_type: string;
  delivery_method: string;
}) {
  const response = await apiClient.post<AuctionNotice>('/gold-loans/auctions/notices', data);
  return response.data;
}

export async function sendAuctionNotice(noticeId: string, data: {
  delivery_method?: string;
  tracking_number?: string;
}) {
  const response = await apiClient.post<AuctionNotice>(
    `/gold-loans/auctions/notices/${noticeId}/send`,
    data
  );
  return response.data;
}

export async function getUpcomingAuctions() {
  const response = await apiClient.get<{
    auctions: Auction[];
    total: number;
  }>('/gold-loans/auctions/upcoming/scheduled');
  return response.data;
}
