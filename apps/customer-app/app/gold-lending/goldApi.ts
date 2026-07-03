export const GOLD_API_BASE = process.env.NEXT_PUBLIC_GOLD_API_URL ?? 'http://localhost:8013';

export function goldApiUrl(path: string) {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  return `${GOLD_API_BASE}${normalizedPath}`;
}

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(goldApiUrl(path));
  if (!response.ok) throw new Error(`Gold API request failed: ${response.status}`);
  return response.json() as Promise<T>;
}

async function postJson<T>(path: string, payload: unknown): Promise<T> {
  const response = await fetch(goldApiUrl(path), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new Error(`Gold API request failed: ${response.status}`);
  return response.json() as Promise<T>;
}

async function patchJson<T>(path: string, payload: unknown): Promise<T> {
  const response = await fetch(goldApiUrl(path), {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new Error(`Gold API request failed: ${response.status}`);
  return response.json() as Promise<T>;
}

async function deleteJson(path: string): Promise<void> {
  const response = await fetch(goldApiUrl(path), {
    method: 'DELETE',
  });
  if (!response.ok) throw new Error(`Gold API request failed: ${response.status}`);
}

export const goldApi = {
  // Product Management
  listProducts: (isActive?: boolean | null) => {
    const params = new URLSearchParams();
    if (isActive !== null && isActive !== undefined) {
      params.append('is_active', String(isActive));
    }
    const query = params.toString() ? `?${params.toString()}` : '';
    return getJson<any[]>(`/api/v1/gold/products${query}`);
  },
  getProduct: (productId: string) => getJson<any>(`/api/v1/gold/products/${productId}`),
  getProductByCode: (productCode: string) => getJson<any>(`/api/v1/gold/products/code/${productCode}`),
  createProduct: (payload: unknown) => postJson('/api/v1/gold/products', payload),
  updateProduct: (productId: string, payload: unknown) => patchJson(`/api/v1/gold/products/${productId}`, payload),
  deleteProduct: (productId: string) => deleteJson(`/api/v1/gold/products/${productId}`),
  
  // Interest Configuration
  setInterestConfig: (productId: string, payload: unknown) => 
    postJson(`/api/v1/gold/products/${productId}/interest`, payload),
  
  // Tenure Configuration
  setTenureConfig: (productId: string, payload: unknown) => 
    postJson(`/api/v1/gold/products/${productId}/tenure`, payload),
  
  // Limits Configuration
  setLimitsConfig: (productId: string, payload: unknown) => 
    postJson(`/api/v1/gold/products/${productId}/limits`, payload),
  
  // Charges
  addCharge: (productId: string, payload: unknown) => 
    postJson(`/api/v1/gold/products/${productId}/charges`, payload),
  listCharges: (productId: string) => 
    getJson<any[]>(`/api/v1/gold/products/${productId}/charges`),
  deleteCharge: (productId: string, chargeId: string) => 
    deleteJson(`/api/v1/gold/products/${productId}/charges/${chargeId}`),
  
  // Documents
  addDocument: (productId: string, payload: unknown) => 
    postJson(`/api/v1/gold/products/${productId}/documents`, payload),
  listDocuments: (productId: string) => 
    getJson<any[]>(`/api/v1/gold/products/${productId}/documents`),
  
  // Eligibility Rules
  addEligibilityRule: (productId: string, payload: unknown) => 
    postJson(`/api/v1/gold/products/${productId}/eligibility`, payload),
  listEligibilityRules: (productId: string) => 
    getJson<any[]>(`/api/v1/gold/products/${productId}/eligibility`),
  
  // Workflow
  addWorkflowStage: (productId: string, payload: unknown) => 
    postJson(`/api/v1/gold/products/${productId}/workflow`, payload),
  listWorkflowStages: (productId: string) => 
    getJson<any[]>(`/api/v1/gold/products/${productId}/workflow`),
  
  // Journey Management
  createJourneySession: (payload: unknown) => 
    postJson('/api/v1/gold/journey/sessions', payload),
  getJourneySession: (sessionId: string) => 
    getJson<any>(`/api/v1/gold/journey/sessions/${sessionId}`),
  updateJourneySession: (sessionId: string, payload: unknown) => 
    patchJson(`/api/v1/gold/journey/sessions/${sessionId}`, payload),
  listJourneySessions: (params?: Record<string, any>) => {
    const query = new URLSearchParams(params).toString();
    return getJson<any[]>(`/api/v1/gold/journey/sessions${query ? `?${query}` : ''}`);
  },
  
  // Customer Search
  searchCustomer: (payload: unknown) => 
    postJson('/api/v1/gold/journey/search-customer', payload),
  selectCustomer: (sessionId: string, customerId: string) => 
    postJson(`/api/v1/gold/journey/select-customer/${sessionId}/${customerId}`, {}),
  
  // Product Recommendations
  getProductRecommendations: (sessionId: string, requestedAmount?: number) => {
    const params = requestedAmount ? `?requested_amount=${requestedAmount}` : '';
    return getJson<any[]>(`/api/v1/gold/journey/recommend-products/${sessionId}${params}`);
  },
  selectProduct: (payload: unknown) => 
    postJson('/api/v1/gold/journey/select-product', payload),
  
  // Eligibility
  checkEligibility: (sessionId: string, productId: string) => 
    postJson(`/api/v1/gold/journey/check-eligibility/${sessionId}/${productId}`, {}),
  
  // Journey Steps
  createJourneyStep: (payload: unknown) => 
    postJson('/api/v1/gold/journey/steps', payload),
  updateJourneyStep: (stepId: string, payload: unknown) => 
    patchJson(`/api/v1/gold/journey/steps/${stepId}`, payload),
  
  // Customer Interactions
  createInteraction: (payload: unknown) => 
    postJson('/api/v1/gold/journey/interactions', payload),
  listInteractions: (sessionId: string) => 
    getJson<any[]>(`/api/v1/gold/journey/interactions/${sessionId}`),
  
  // Appraisal Engine
  listOrnamentTypes: (category?: string) => {
    const params = category ? `?category=${category}` : '';
    return getJson<any[]>(`/api/v1/gold/appraisal/ornament-types${params}`);
  },
  
  // Market Rates
  createMarketRate: (payload: unknown) => 
    postJson('/api/v1/gold/appraisal/market-rates', payload),
  getCurrentMarketRates: (params?: Record<string, any>) => {
    const query = new URLSearchParams(params).toString();
    return getJson<any[]>(`/api/v1/gold/appraisal/market-rates/current${query ? `?${query}` : ''}`);
  },
  getMarketRate: (rateId: string) => 
    getJson<any>(`/api/v1/gold/appraisal/market-rates/${rateId}`),
  
  // Appraisal Sessions
  createAppraisalSession: (payload: unknown) => 
    postJson('/api/v1/gold/appraisal/sessions', payload),
  getAppraisalSession: (sessionId: string) => 
    getJson<any>(`/api/v1/gold/appraisal/sessions/${sessionId}`),
  updateAppraisalSession: (sessionId: string, payload: unknown) => 
    patchJson(`/api/v1/gold/appraisal/sessions/${sessionId}`, payload),
  completeAppraisalSession: (sessionId: string) => 
    postJson(`/api/v1/gold/appraisal/sessions/${sessionId}/complete`, {}),
  
  // Purity Tests
  createPurityTest: (payload: unknown) => 
    postJson('/api/v1/gold/appraisal/purity-tests', payload),
  verifyPurityTest: (testId: string, payload: unknown) => 
    patchJson(`/api/v1/gold/appraisal/purity-tests/${testId}/verify`, payload),
  listPurityTests: (ornamentId: string) => 
    getJson<any[]>(`/api/v1/gold/appraisal/purity-tests/ornament/${ornamentId}`),
  
  // Weight Verification
  recordWeightMeasurement: (payload: unknown) => 
    postJson('/api/v1/gold/appraisal/weight-measurements', payload),
  verifyWeightMeasurement: (verificationId: string, verifiedBy: string, payload: unknown) => 
    postJson(`/api/v1/gold/appraisal/weight-measurements/${verificationId}/verify?verified_by_user_id=${verifiedBy}`, payload),
  
  // Anomalies
  createAnomaly: (payload: unknown) => 
    postJson('/api/v1/gold/appraisal/anomalies', payload),
  resolveAnomaly: (anomalyId: string, payload: unknown) => 
    patchJson(`/api/v1/gold/appraisal/anomalies/${anomalyId}/resolve`, payload),
  listAnomalies: (params?: Record<string, any>) => {
    const query = new URLSearchParams(params).toString();
    return getJson<any[]>(`/api/v1/gold/appraisal/anomalies${query ? `?${query}` : ''}`);
  },
  
  // Quick Appraisal
  performQuickAppraisal: (payload: unknown) => 
    postJson('/api/v1/gold/appraisal/quick-appraisal', payload),
  
  // ====================================
  // CATALOG - Phase 4: Enhanced Ornament Lifecycle
  // ====================================
  
  // Photo Management
  addOrnamentPhoto: (payload: unknown) => 
    postJson('/api/v1/gold/catalog/photos', payload),
  listOrnamentPhotos: (ornamentId: string, photoType?: string) => {
    const params = photoType ? `?photo_type=${photoType}` : '';
    return getJson<any[]>(`/api/v1/gold/catalog/photos/ornament/${ornamentId}${params}`);
  },
  deleteOrnamentPhoto: (photoId: string) => 
    deleteJson(`/api/v1/gold/catalog/photos/${photoId}`),
  
  // Stone Catalog
  addStone: (payload: unknown) => 
    postJson('/api/v1/gold/catalog/stones', payload),
  listOrnamentStones: (ornamentId: string) => 
    getJson<any[]>(`/api/v1/gold/catalog/stones/ornament/${ornamentId}`),
  getStone: (stoneId: string) => 
    getJson<any>(`/api/v1/gold/catalog/stones/${stoneId}`),
  updateStone: (stoneId: string, payload: unknown) => 
    patchJson(`/api/v1/gold/catalog/stones/${stoneId}`, payload),
  
  // Status Tracking
  changeOrnamentStatus: (payload: unknown) => 
    postJson('/api/v1/gold/catalog/status-change', payload),
  getStatusHistory: (ornamentId: string) => 
    getJson<any[]>(`/api/v1/gold/catalog/status-history/ornament/${ornamentId}`),
  
  // Movement Tracking
  recordMovement: (payload: unknown) => 
    postJson('/api/v1/gold/catalog/movements', payload),
  verifyMovement: (movementId: string, verifiedByUserId: string) => 
    postJson(`/api/v1/gold/catalog/movements/${movementId}/verify`, { verified_by_user_id: verifiedByUserId }),
  listOrnamentMovements: (ornamentId: string) => 
    getJson<any[]>(`/api/v1/gold/catalog/movements/ornament/${ornamentId}`),
  getMovementsByLocation: (location: string, fromDate?: string, toDate?: string) => {
    const params = new URLSearchParams({ location });
    if (fromDate) params.append('from_date', fromDate);
    if (toDate) params.append('to_date', toDate);
    return getJson<any[]>(`/api/v1/gold/catalog/movements/location/${location}?${params.toString()}`);
  },
  
  // Condition Inspection
  createConditionInspection: (payload: unknown) => 
    postJson('/api/v1/gold/catalog/conditions', payload),
  listConditionHistory: (ornamentId: string) => 
    getJson<any[]>(`/api/v1/gold/catalog/conditions/ornament/${ornamentId}`),
  getDueInspections: (daysAhead: number = 30) => 
    getJson<any[]>(`/api/v1/gold/catalog/conditions/due-inspection?days_ahead=${daysAhead}`),
  
  // Tags
  addTag: (payload: unknown) => 
    postJson('/api/v1/gold/catalog/tags', payload),
  listOrnamentTags: (ornamentId: string) => 
    getJson<any[]>(`/api/v1/gold/catalog/tags/ornament/${ornamentId}`),
  deleteTag: (tagId: string) => 
    deleteJson(`/api/v1/gold/catalog/tags/${tagId}`),
  
  // Comparisons (Fraud Detection)
  createComparison: (payload: unknown) => 
    postJson('/api/v1/gold/catalog/comparisons', payload),
  listComparisons: (ornamentId?: string, isFlagged?: boolean) => {
    const params = new URLSearchParams();
    if (ornamentId) params.append('ornament_id', ornamentId);
    if (isFlagged !== undefined) params.append('is_flagged', String(isFlagged));
    const query = params.toString() ? `?${params.toString()}` : '';
    return getJson<any[]>(`/api/v1/gold/catalog/comparisons${query}`);
  },
  
  // Certificates
  addCertificate: (payload: unknown) => 
    postJson('/api/v1/gold/catalog/certificates', payload),
  verifyCertificate: (certId: string, payload: unknown) => 
    postJson(`/api/v1/gold/catalog/certificates/${certId}/verify`, payload),
  listOrnamentCertificates: (ornamentId: string) => 
    getJson<any[]>(`/api/v1/gold/catalog/certificates/ornament/${ornamentId}`),
  
  // Insurance
  addInsurance: (payload: unknown) => 
    postJson('/api/v1/gold/catalog/insurance', payload),
  updateInsurance: (insuranceId: string, payload: unknown) => 
    patchJson(`/api/v1/gold/catalog/insurance/${insuranceId}`, payload),
  getOrnamentInsurance: (ornamentId: string) => 
    getJson<any>(`/api/v1/gold/catalog/insurance/ornament/${ornamentId}`),
  
  // Ornament Groups
  createOrnamentGroup: (payload: unknown) => 
    postJson('/api/v1/gold/catalog/groups', payload),
  addOrnamentToGroup: (groupId: string, payload: unknown) => 
    postJson(`/api/v1/gold/catalog/groups/${groupId}/ornaments`, payload),
  getOrnamentGroup: (groupId: string) => 
    getJson<any>(`/api/v1/gold/catalog/groups/${groupId}`),
  listOrnamentGroups: (customerId?: string) => {
    const params = customerId ? `?customer_id=${customerId}` : '';
    return getJson<any[]>(`/api/v1/gold/catalog/groups${params}`);
  },
  
  // Complete Profile
  getOrnamentCompleteProfile: (ornamentId: string) => 
    getJson<any>(`/api/v1/gold/catalog/profile/${ornamentId}`),
  
  // ====================================
  // VAULT & PACKET MANAGEMENT - Phase 5
  // ====================================
  
  // Vault Management
  createVault: (payload: unknown) => 
    postJson('/api/v1/gold/vault/vaults', payload),
  listVaults: (params?: Record<string, any>) => {
    const query = new URLSearchParams(params).toString();
    return getJson<any[]>(`/api/v1/gold/vault/vaults${query ? `?${query}` : ''}`);
  },
  getVault: (vaultId: string) => 
    getJson<any>(`/api/v1/gold/vault/vaults/${vaultId}`),
  updateVault: (vaultId: string, payload: unknown) => 
    patchJson(`/api/v1/gold/vault/vaults/${vaultId}`, payload),
  getVaultHierarchy: (vaultId: string) => 
    getJson<any>(`/api/v1/gold/vault/vaults/${vaultId}/hierarchy`),
  
  // Rack Management
  createRack: (payload: unknown) => 
    postJson('/api/v1/gold/vault/racks', payload),
  listVaultRacks: (vaultId: string) => 
    getJson<any[]>(`/api/v1/gold/vault/vaults/${vaultId}/racks`),
  
  // Locker Management
  createLocker: (payload: unknown) => 
    postJson('/api/v1/gold/vault/lockers', payload),
  listRackLockers: (rackId: string) => 
    getJson<any[]>(`/api/v1/gold/vault/racks/${rackId}/lockers`),
  
  // Tray Management
  createTray: (payload: unknown) => 
    postJson('/api/v1/gold/vault/trays', payload),
  listLockerTrays: (lockerId: string) => 
    getJson<any[]>(`/api/v1/gold/vault/lockers/${lockerId}/trays`),
  
  // Packet Management
  createPacket: (payload: unknown) => 
    postJson('/api/v1/gold/vault/packets', payload),
  sealPacket: (packetId: string, payload: unknown) => 
    postJson(`/api/v1/gold/vault/packets/${packetId}/seal`, payload),
  verifyPacketSeal: (packetId: string, payload: unknown) => 
    postJson(`/api/v1/gold/vault/packets/${packetId}/verify-seal`, payload),
  assignPacketLocation: (packetId: string, payload: unknown) => 
    postJson(`/api/v1/gold/vault/packets/${packetId}/assign-location`, payload),
  listPackets: (params?: Record<string, any>) => {
    const query = new URLSearchParams(params).toString();
    return getJson<any[]>(`/api/v1/gold/vault/packets${query ? `?${query}` : ''}`);
  },
  getPacket: (packetId: string) => 
    getJson<any>(`/api/v1/gold/vault/packets/${packetId}`),
  getPacketQRCode: (packetId: string) => 
    getJson<any>(`/api/v1/gold/vault/packets/${packetId}/qr-code`),
  
  // Packet Movements
  recordPacketMovement: (payload: unknown) => 
    postJson('/api/v1/gold/vault/packet-movements', payload),
  verifyPacketMovement: (movementId: string, verifiedByUserId: string) => 
    postJson(`/api/v1/gold/vault/packet-movements/${movementId}/verify`, { verified_by_user_id: verifiedByUserId }),
  listPacketMovements: (packetId: string) => 
    getJson<any[]>(`/api/v1/gold/vault/packets/${packetId}/movements`),
  getPacketAuditTrail: (packetId: string) => 
    getJson<any>(`/api/v1/gold/vault/packets/${packetId}/audit-trail`),
  
  // Vault Audits
  createVaultAudit: (payload: unknown) => 
    postJson('/api/v1/gold/vault/audits', payload),
  startVaultAudit: (auditId: string, payload: unknown) => 
    postJson(`/api/v1/gold/vault/audits/${auditId}/start`, payload),
  completeVaultAudit: (auditId: string, payload: unknown) => 
    postJson(`/api/v1/gold/vault/audits/${auditId}/complete`, payload),
  reviewVaultAudit: (auditId: string, payload: unknown) => 
    postJson(`/api/v1/gold/vault/audits/${auditId}/review`, payload),
  approveVaultAudit: (auditId: string, payload: unknown) => 
    postJson(`/api/v1/gold/vault/audits/${auditId}/approve`, payload),
  listAudits: (params?: Record<string, any>) => {
    const query = new URLSearchParams(params).toString();
    return getJson<any[]>(`/api/v1/gold/vault/audits${query ? `?${query}` : ''}`);
  },
  
  // Audit Findings
  createAuditFinding: (payload: unknown) => 
    postJson('/api/v1/gold/vault/audit-findings', payload),
  resolveAuditFinding: (findingId: string, payload: unknown) => 
    postJson(`/api/v1/gold/vault/audit-findings/${findingId}/resolve`, payload),
  listAuditFindings: (auditId: string) => 
    getJson<any[]>(`/api/v1/gold/vault/audits/${auditId}/findings`),
  
  // Vault Access Log
  recordVaultAccess: (payload: unknown) => 
    postJson('/api/v1/gold/vault/access-log', payload),
  recordVaultExit: (accessId: string, payload: unknown) => 
    postJson(`/api/v1/gold/vault/access-log/${accessId}/exit`, payload),
  listVaultAccess: (vaultId: string, params?: Record<string, any>) => {
    const query = new URLSearchParams(params).toString();
    return getJson<any[]>(`/api/v1/gold/vault/vaults/${vaultId}/access-log${query ? `?${query}` : ''}`);
  },
  
  // Seal Management
  createSeal: (payload: unknown) => 
    postJson('/api/v1/gold/vault/seals', payload),
  issueSeal: (sealId: string, payload: unknown) => 
    postJson(`/api/v1/gold/vault/seals/${sealId}/issue`, payload),
  disposeSeal: (sealId: string, payload: unknown) => 
    postJson(`/api/v1/gold/vault/seals/${sealId}/dispose`, payload),
  listSeals: (params?: Record<string, any>) => {
    const query = new URLSearchParams(params).toString();
    return getJson<any[]>(`/api/v1/gold/vault/seals${query ? `?${query}` : ''}`);
  },
  getAvailableSealsCount: (branchId?: string) => {
    const params = branchId ? `?branch_id=${branchId}` : '';
    return getJson<any>(`/api/v1/gold/vault/seals/available-count${params}`);
  },
};

  // ========================================================================
  // LOAN ORIGINATION & DISBURSEMENT (Phase 6)
  // ========================================================================

  // Loan Applications
  createLoanApplication: (data: any) =>
    postJson<any>('/api/v1/gold/applications', data),
  
  getLoanApplications: (filters?: {
    status?: string;
    stage?: string;
    branch_id?: string;
    customer_id?: string;
    from_date?: string;
    to_date?: string;
    skip?: number;
    limit?: number;
  }) => {
    const params = new URLSearchParams();
    if (filters?.status) params.append('status', filters.status);
    if (filters?.stage) params.append('stage', filters.stage);
    if (filters?.branch_id) params.append('branch_id', filters.branch_id);
    if (filters?.customer_id) params.append('customer_id', filters.customer_id);
    if (filters?.from_date) params.append('from_date', filters.from_date);
    if (filters?.to_date) params.append('to_date', filters.to_date);
    if (filters?.skip) params.append('skip', filters.skip.toString());
    if (filters?.limit) params.append('limit', filters.limit.toString());
    const query = params.toString() ? `?${params.toString()}` : '';
    return getJson<any[]>(`/api/v1/gold/applications${query}`);
  },

  getLoanApplication: (applicationId: string) =>
    getJson<any>(`/api/v1/gold/applications/${applicationId}`),

  updateLoanApplication: (applicationId: string, data: any) =>
    patchJson<any>(`/api/v1/gold/applications/${applicationId}`, data),

  submitLoanApplication: (applicationId: string, submittedBy: string) =>
    postJson<any>(`/api/v1/gold/applications/${applicationId}/submit`, {
      submitted_by: submittedBy,
    }),

  getApplicationOrnaments: (applicationId: string) =>
    getJson<any[]>(`/api/v1/gold/applications/${applicationId}/ornaments`),

  deleteLoanApplication: (applicationId: string) =>
    deleteJson(`/api/v1/gold/applications/${applicationId}`),

  // Credit Evaluation
  createCreditEvaluation: (data: any) =>
    postJson<any>('/api/v1/gold/credit-evaluations', data),

  getCreditEvaluation: (evaluationId: string) =>
    getJson<any>(`/api/v1/gold/credit-evaluations/${evaluationId}`),

  getApplicationCreditEvaluation: (applicationId: string) =>
    getJson<any>(`/api/v1/gold/applications/${applicationId}/credit-evaluation`),

  // Approval Workflow
  createLoanApproval: (data: any) =>
    postJson<any>('/api/v1/gold/approvals', data),

  submitApprovalDecision: (approvalId: string, decision: any) =>
    postJson<any>(`/api/v1/gold/approvals/${approvalId}/decision`, decision),

  getApplicationApprovals: (applicationId: string) =>
    getJson<any[]>(`/api/v1/gold/applications/${applicationId}/approvals`),

  // Loan Accounts
  createLoanAccount: (data: any) =>
    postJson<any>('/api/v1/gold/loan-accounts', data),

  getLoanAccounts: (filters?: {
    status?: string;
    customer_id?: string;
    branch_id?: string;
    is_npa?: boolean;
    skip?: number;
    limit?: number;
  }) => {
    const params = new URLSearchParams();
    if (filters?.status) params.append('status', filters.status);
    if (filters?.customer_id) params.append('customer_id', filters.customer_id);
    if (filters?.branch_id) params.append('branch_id', filters.branch_id);
    if (filters?.is_npa !== undefined) params.append('is_npa', filters.is_npa.toString());
    if (filters?.skip) params.append('skip', filters.skip.toString());
    if (filters?.limit) params.append('limit', filters.limit.toString());
    const query = params.toString() ? `?${params.toString()}` : '';
    return getJson<any[]>(`/api/v1/gold/loan-accounts${query}`);
  },

  getLoanAccount: (loanId: string) =>
    getJson<any>(`/api/v1/gold/loan-accounts/${loanId}`),

  // Disbursements
  createDisbursement: (data: any) =>
    postJson<any>('/api/v1/gold/disbursements', data),

  verifyDisbursement: (disbursementId: string, data: any) =>
    postJson<any>(`/api/v1/gold/disbursements/${disbursementId}/verify`, data),

  getDisbursement: (disbursementId: string) =>
    getJson<any>(`/api/v1/gold/disbursements/${disbursementId}`),

  getApplicationDisbursements: (applicationId: string) =>
    getJson<any[]>(`/api/v1/gold/applications/${applicationId}/disbursements`),

  // Summary & Stats
  getApplicationsSummary: (filters?: {
    branch_id?: string;
    from_date?: string;
    to_date?: string;
  }) => {
    const params = new URLSearchParams();
    if (filters?.branch_id) params.append('branch_id', filters.branch_id);
    if (filters?.from_date) params.append('from_date', filters.from_date);
    if (filters?.to_date) params.append('to_date', filters.to_date);
    const query = params.toString() ? `?${params.toString()}` : '';
    return getJson<any>(`/api/v1/gold/applications/summary${query}`);
  },

  getLoanPortfolio: (filters?: { branch_id?: string }) => {
    const params = new URLSearchParams();
    if (filters?.branch_id) params.append('branch_id', filters.branch_id);
    const query = params.toString() ? `?${params.toString()}` : '';
    return getJson<any>(`/api/v1/gold/loan-accounts/portfolio${query}`);
  },
};

  // ========================================================================
  // LOAN SERVICING & REPAYMENT (Phase 7)
  // ========================================================================

  // EMI Schedule
  generateEMISchedule: (loanAccountId: string) =>
    postJson<any[]>(`/api/v1/gold/emi-schedule?loan_account_id=${loanAccountId}`, {}),

  getEMISchedule: (loanAccountId: string, paymentStatus?: string) => {
    const params = paymentStatus ? `?payment_status=${paymentStatus}` : '';
    return getJson<any[]>(`/api/v1/gold/emi-schedule/${loanAccountId}${params}`);
  },

  getOverdueEMIs: (loanAccountId: string) =>
    getJson<any[]>(`/api/v1/gold/emi-schedule/${loanAccountId}/overdue`),

  updateEMISchedule: (scheduleId: string, data: any) =>
    patchJson<any>(`/api/v1/gold/emi-schedule/${scheduleId}`, data),

  getEMISummary: (loanAccountId: string) =>
    getJson<any>(`/api/v1/gold/emi-schedule/${loanAccountId}/summary`),

  // Repayment Transactions
  createRepayment: (data: any) =>
    postJson<any>('/api/v1/gold/repayments', data),

  getRepayments: (filters?: {
    loan_account_id?: string;
    payment_mode?: string;
    transaction_status?: string;
    from_date?: string;
    to_date?: string;
    skip?: number;
    limit?: number;
  }) => {
    const params = new URLSearchParams();
    if (filters?.loan_account_id) params.append('loan_account_id', filters.loan_account_id);
    if (filters?.payment_mode) params.append('payment_mode', filters.payment_mode);
    if (filters?.transaction_status) params.append('transaction_status', filters.transaction_status);
    if (filters?.from_date) params.append('from_date', filters.from_date);
    if (filters?.to_date) params.append('to_date', filters.to_date);
    if (filters?.skip) params.append('skip', filters.skip.toString());
    if (filters?.limit) params.append('limit', filters.limit.toString());
    const query = params.toString() ? `?${params.toString()}` : '';
    return getJson<any[]>(`/api/v1/gold/repayments${query}`);
  },

  getRepayment: (transactionId: string) =>
    getJson<any>(`/api/v1/gold/repayments/${transactionId}`),

  verifyRepayment: (transactionId: string, verifiedByUserId: string) =>
    postJson<any>(`/api/v1/gold/repayments/${transactionId}/verify`, { verified_by_user_id: verifiedByUserId }),

  reverseRepayment: (transactionId: string, reversedByUserId: string, reason: string) =>
    postJson<any>(`/api/v1/gold/repayments/${transactionId}/reverse`, {
      reversed_by_user_id: reversedByUserId,
      reversal_reason: reason
    }),

  getRepaymentSummary: (loanAccountId: string) =>
    getJson<any>(`/api/v1/gold/repayments/${loanAccountId}/summary`),

  // Interest Accrual
  createInterestAccrual: (data: any) =>
    postJson<any>('/api/v1/gold/interest-accrual', data),

  getInterestAccruals: (loanAccountId: string, fromDate?: string, toDate?: string) => {
    const params = new URLSearchParams();
    if (fromDate) params.append('from_date', fromDate);
    if (toDate) params.append('to_date', toDate);
    const query = params.toString() ? `?${params.toString()}` : '';
    return getJson<any[]>(`/api/v1/gold/interest-accrual/${loanAccountId}${query}`);
  },

  bulkInterestAccrual: (loanAccountIds: string[], accrualDate: string) =>
    postJson<any>('/api/v1/gold/interest-accrual/bulk', {
      loan_account_ids: loanAccountIds,
      accrual_date: accrualDate
    }),

  // Loan Adjustments
  createAdjustment: (data: any) =>
    postJson<any>('/api/v1/gold/adjustments', data),

  getAdjustments: (filters?: {
    loan_account_id?: string;
    adjustment_type?: string;
    approval_status?: string;
    skip?: number;
    limit?: number;
  }) => {
    const params = new URLSearchParams();
    if (filters?.loan_account_id) params.append('loan_account_id', filters.loan_account_id);
    if (filters?.adjustment_type) params.append('adjustment_type', filters.adjustment_type);
    if (filters?.approval_status) params.append('approval_status', filters.approval_status);
    if (filters?.skip) params.append('skip', filters.skip.toString());
    if (filters?.limit) params.append('limit', filters.limit.toString());
    const query = params.toString() ? `?${params.toString()}` : '';
    return getJson<any[]>(`/api/v1/gold/adjustments${query}`);
  },

  approveAdjustment: (adjustmentId: string, approvedByUserId: string, approvalStatus: string) =>
    postJson<any>(`/api/v1/gold/adjustments/${adjustmentId}/approve`, {
      approved_by_user_id: approvedByUserId,
      approval_status: approvalStatus
    }),

  // Prepayments
  createPrepayment: (data: any) =>
    postJson<any>('/api/v1/gold/prepayments', data),

  getPrepayments: (filters?: {
    loan_account_id?: string;
    prepayment_type?: string;
    prepayment_status?: string;
    skip?: number;
    limit?: number;
  }) => {
    const params = new URLSearchParams();
    if (filters?.loan_account_id) params.append('loan_account_id', filters.loan_account_id);
    if (filters?.prepayment_type) params.append('prepayment_type', filters.prepayment_type);
    if (filters?.prepayment_status) params.append('prepayment_status', filters.prepayment_status);
    if (filters?.skip) params.append('skip', filters.skip.toString());
    if (filters?.limit) params.append('limit', filters.limit.toString());
    const query = params.toString() ? `?${params.toString()}` : '';
    return getJson<any[]>(`/api/v1/gold/prepayments${query}`);
  },

  approvePrepayment: (prepaymentId: string, approvedByUserId: string) =>
    postJson<any>(`/api/v1/gold/prepayments/${prepaymentId}/approve`, { approved_by_user_id: approvedByUserId }),

  // Statements
  createStatement: (data: any) =>
    postJson<any>('/api/v1/gold/statements', data),

  getStatements: (loanAccountId: string, statementType?: string) => {
    const params = statementType ? `?statement_type=${statementType}` : '';
    return getJson<any[]>(`/api/v1/gold/statements/${loanAccountId}${params}`);
  },

  bulkGenerateStatements: (loanAccountIds: string[], periodStart: string, periodEnd: string, statementType: string) =>
    postJson<any>('/api/v1/gold/statements/bulk', {
      loan_account_ids: loanAccountIds,
      period_start: periodStart,
      period_end: periodEnd,
      statement_type: statementType
    }),

  // Auto Debit Mandates
  createMandate: (data: any) =>
    postJson<any>('/api/v1/gold/mandates', data),

  getMandates: (filters?: {
    loan_account_id?: string;
    mandate_status?: string;
    skip?: number;
    limit?: number;
  }) => {
    const params = new URLSearchParams();
    if (filters?.loan_account_id) params.append('loan_account_id', filters.loan_account_id);
    if (filters?.mandate_status) params.append('mandate_status', filters.mandate_status);
    if (filters?.skip) params.append('skip', filters.skip.toString());
    if (filters?.limit) params.append('limit', filters.limit.toString());
    const query = params.toString() ? `?${params.toString()}` : '';
    return getJson<any[]>(`/api/v1/gold/mandates${query}`);
  },

  updateMandate: (mandateId: string, data: any) =>
    patchJson<any>(`/api/v1/gold/mandates/${mandateId}`, data),

  // Penalties
  createPenalty: (data: any) =>
    postJson<any>('/api/v1/gold/penalties', data),

  getPenalties: (filters?: {
    loan_account_id?: string;
    penalty_type?: string;
    penalty_status?: string;
    skip?: number;
    limit?: number;
  }) => {
    const params = new URLSearchParams();
    if (filters?.loan_account_id) params.append('loan_account_id', filters.loan_account_id);
    if (filters?.penalty_type) params.append('penalty_type', filters.penalty_type);
    if (filters?.penalty_status) params.append('penalty_status', filters.penalty_status);
    if (filters?.skip) params.append('skip', filters.skip.toString());
    if (filters?.limit) params.append('limit', filters.limit.toString());
    const query = params.toString() ? `?${params.toString()}` : '';
    return getJson<any[]>(`/api/v1/gold/penalties${query}`);
  },

  waivePenalty: (penaltyId: string, data: any) =>
    postJson<any>(`/api/v1/gold/penalties/${penaltyId}/waive`, data),

  // Renewals
  createRenewal: (data: any) =>
    postJson<any>('/api/v1/gold/renewals', data),

  getRenewals: (filters?: {
    original_loan_account_id?: string;
    renewal_type?: string;
    renewal_status?: string;
    skip?: number;
    limit?: number;
  }) => {
    const params = new URLSearchParams();
    if (filters?.original_loan_account_id) params.append('original_loan_account_id', filters.original_loan_account_id);
    if (filters?.renewal_type) params.append('renewal_type', filters.renewal_type);
    if (filters?.renewal_status) params.append('renewal_status', filters.renewal_status);
    if (filters?.skip) params.append('skip', filters.skip.toString());
    if (filters?.limit) params.append('limit', filters.limit.toString());
    const query = params.toString() ? `?${params.toString()}` : '';
    return getJson<any[]>(`/api/v1/gold/renewals${query}`);
  },

  approveRenewal: (renewalId: string, approvedByUserId: string) =>
    postJson<any>(`/api/v1/gold/renewals/${renewalId}/approve`, { approved_by_user_id: approvedByUserId }),

  // Allocation Rules
  createAllocationRule: (data: any) =>
    postJson<any>('/api/v1/gold/allocation-rules', data),

  getAllocationRules: (isActive?: boolean, isDefault?: boolean) => {
    const params = new URLSearchParams();
    if (isActive !== undefined) params.append('is_active', isActive.toString());
    if (isDefault !== undefined) params.append('is_default', isDefault.toString());
    const query = params.toString() ? `?${params.toString()}` : '';
    return getJson<any[]>(`/api/v1/gold/allocation-rules${query}`);
  },

  // Summary & Analytics
  getLoanAccountSummary: (loanAccountId: string) =>
    getJson<any>(`/api/v1/gold/loan-accounts/${loanAccountId}/summary`),

  getOverdueSummary: (branchId?: string, minDaysOverdue?: number) => {
    const params = new URLSearchParams();
    if (branchId) params.append('branch_id', branchId);
    if (minDaysOverdue) params.append('min_days_overdue', minDaysOverdue.toString());
    const query = params.toString() ? `?${params.toString()}` : '';
    return getJson<any[]>(`/api/v1/gold/overdue-summary${query}`);
  },

  getPortfolioHealth: (branchId?: string, productId?: string) => {
    const params = new URLSearchParams();
    if (branchId) params.append('branch_id', branchId);
    if (productId) params.append('product_id', productId);
    const query = params.toString() ? `?${params.toString()}` : '';
    return getJson<any[]>(`/api/v1/gold/portfolio-health${query}`);
  },

  // ========================================================================
  // COLLECTIONS & RECOVERY (Phase 8)
  // ========================================================================

  // Collection Cases
  createCollectionCase: (data: any) =>
    postJson<any>('/api/v1/gold/collections/cases', data),

  getCollectionCases: (filters?: {
    case_status?: string;
    bucket_type?: string;
    priority?: string;
    assigned_to_user_id?: string;
    skip?: number;
    limit?: number;
  }) => {
    const params = new URLSearchParams();
    if (filters?.case_status) params.append('case_status', filters.case_status);
    if (filters?.bucket_type) params.append('bucket_type', filters.bucket_type);
    if (filters?.priority) params.append('priority', filters.priority);
    if (filters?.assigned_to_user_id) params.append('assigned_to_user_id', filters.assigned_to_user_id);
    if (filters?.skip) params.append('skip', filters.skip.toString());
    if (filters?.limit) params.append('limit', filters.limit.toString());
    const query = params.toString() ? `?${params.toString()}` : '';
    return getJson<any>(`/api/v1/gold/collections/cases${query}`);
  },

  getCollectionCase: (caseId: string) =>
    getJson<any>(`/api/v1/gold/collections/cases/${caseId}`),

  updateCollectionCase: (caseId: string, data: any) =>
    patchJson<any>(`/api/v1/gold/collections/cases/${caseId}`, data),

  deleteCollectionCase: (caseId: string) =>
    deleteJson(`/api/v1/gold/collections/cases/${caseId}`),

  getCaseStatistics: (caseId: string) =>
    getJson<any>(`/api/v1/gold/collections/cases/${caseId}/statistics`),

  getCaseTimeline: (caseId: string) =>
    getJson<any[]>(`/api/v1/gold/collections/cases/${caseId}/timeline`),

  // Collection Activities
  createCollectionActivity: (data: any) =>
    postJson<any>('/api/v1/gold/collections/activities', data),

  getCollectionActivities: (filters?: {
    collection_case_id?: string;
    activity_type?: string;
    disposition?: string;
    from_date?: string;
    to_date?: string;
    skip?: number;
    limit?: number;
  }) => {
    const params = new URLSearchParams();
    if (filters?.collection_case_id) params.append('collection_case_id', filters.collection_case_id);
    if (filters?.activity_type) params.append('activity_type', filters.activity_type);
    if (filters?.disposition) params.append('disposition', filters.disposition);
    if (filters?.from_date) params.append('from_date', filters.from_date);
    if (filters?.to_date) params.append('to_date', filters.to_date);
    if (filters?.skip) params.append('skip', filters.skip.toString());
    if (filters?.limit) params.append('limit', filters.limit.toString());
    const query = params.toString() ? `?${params.toString()}` : '';
    return getJson<any[]>(`/api/v1/gold/collections/activities${query}`);
  },

  getCollectionActivity: (activityId: string) =>
    getJson<any>(`/api/v1/gold/collections/activities/${activityId}`),

  deleteCollectionActivity: (activityId: string) =>
    deleteJson(`/api/v1/gold/collections/activities/${activityId}`),

  // Field Visits
  createFieldVisit: (data: any) =>
    postJson<any>('/api/v1/gold/collections/field-visits', data),

  getFieldVisits: (filters?: {
    collection_case_id?: string;
    visit_status?: string;
    field_officer_id?: string;
    from_date?: string;
    to_date?: string;
    skip?: number;
    limit?: number;
  }) => {
    const params = new URLSearchParams();
    if (filters?.collection_case_id) params.append('collection_case_id', filters.collection_case_id);
    if (filters?.visit_status) params.append('visit_status', filters.visit_status);
    if (filters?.field_officer_id) params.append('field_officer_id', filters.field_officer_id);
    if (filters?.from_date) params.append('from_date', filters.from_date);
    if (filters?.to_date) params.append('to_date', filters.to_date);
    if (filters?.skip) params.append('skip', filters.skip.toString());
    if (filters?.limit) params.append('limit', filters.limit.toString());
    const query = params.toString() ? `?${params.toString()}` : '';
    return getJson<any>(`/api/v1/gold/collections/field-visits${query}`);
  },

  getFieldVisit: (visitId: string) =>
    getJson<any>(`/api/v1/gold/collections/field-visits/${visitId}`),

  updateFieldVisit: (visitId: string, data: any) =>
    patchJson<any>(`/api/v1/gold/collections/field-visits/${visitId}`, data),

  deleteFieldVisit: (visitId: string) =>
    deleteJson(`/api/v1/gold/collections/field-visits/${visitId}`),

  // Payment Promises
  createPaymentPromise: (data: any) =>
    postJson<any>('/api/v1/gold/collections/payment-promises', data),

  getPaymentPromises: (filters?: {
    collection_case_id?: string;
    promise_status?: string;
    from_date?: string;
    to_date?: string;
    skip?: number;
    limit?: number;
  }) => {
    const params = new URLSearchParams();
    if (filters?.collection_case_id) params.append('collection_case_id', filters.collection_case_id);
    if (filters?.promise_status) params.append('promise_status', filters.promise_status);
    if (filters?.from_date) params.append('from_date', filters.from_date);
    if (filters?.to_date) params.append('to_date', filters.to_date);
    if (filters?.skip) params.append('skip', filters.skip.toString());
    if (filters?.limit) params.append('limit', filters.limit.toString());
    const query = params.toString() ? `?${params.toString()}` : '';
    return getJson<any[]>(`/api/v1/gold/collections/payment-promises${query}`);
  },

  getPaymentPromise: (promiseId: string) =>
    getJson<any>(`/api/v1/gold/collections/payment-promises/${promiseId}`),

  updatePaymentPromise: (promiseId: string, data: any) =>
    patchJson<any>(`/api/v1/gold/collections/payment-promises/${promiseId}`, data),

  deletePaymentPromise: (promiseId: string) =>
    deleteJson(`/api/v1/gold/collections/payment-promises/${promiseId}`),

  // Recovery Actions
  createRecoveryAction: (data: any) =>
    postJson<any>('/api/v1/gold/collections/recovery-actions', data),

  getRecoveryActions: (filters?: {
    collection_case_id?: string;
    action_type?: string;
    action_status?: string;
    from_date?: string;
    to_date?: string;
    skip?: number;
    limit?: number;
  }) => {
    const params = new URLSearchParams();
    if (filters?.collection_case_id) params.append('collection_case_id', filters.collection_case_id);
    if (filters?.action_type) params.append('action_type', filters.action_type);
    if (filters?.action_status) params.append('action_status', filters.action_status);
    if (filters?.from_date) params.append('from_date', filters.from_date);
    if (filters?.to_date) params.append('to_date', filters.to_date);
    if (filters?.skip) params.append('skip', filters.skip.toString());
    if (filters?.limit) params.append('limit', filters.limit.toString());
    const query = params.toString() ? `?${params.toString()}` : '';
    return getJson<any[]>(`/api/v1/gold/collections/recovery-actions${query}`);
  },

  getRecoveryAction: (actionId: string) =>
    getJson<any>(`/api/v1/gold/collections/recovery-actions/${actionId}`),

  updateRecoveryAction: (actionId: string, data: any) =>
    patchJson<any>(`/api/v1/gold/collections/recovery-actions/${actionId}`, data),

  deleteRecoveryAction: (actionId: string) =>
    deleteJson(`/api/v1/gold/collections/recovery-actions/${actionId}`),

  // Legal Notices
  createLegalNotice: (data: any) =>
    postJson<any>('/api/v1/gold/collections/legal-notices', data),

  getLegalNotices: (filters?: {
    collection_case_id?: string;
    notice_type?: string;
    notice_status?: string;
    from_date?: string;
    to_date?: string;
    skip?: number;
    limit?: number;
  }) => {
    const params = new URLSearchParams();
    if (filters?.collection_case_id) params.append('collection_case_id', filters.collection_case_id);
    if (filters?.notice_type) params.append('notice_type', filters.notice_type);
    if (filters?.notice_status) params.append('notice_status', filters.notice_status);
    if (filters?.from_date) params.append('from_date', filters.from_date);
    if (filters?.to_date) params.append('to_date', filters.to_date);
    if (filters?.skip) params.append('skip', filters.skip.toString());
    if (filters?.limit) params.append('limit', filters.limit.toString());
    const query = params.toString() ? `?${params.toString()}` : '';
    return getJson<any[]>(`/api/v1/gold/collections/legal-notices${query}`);
  },

  getLegalNotice: (noticeId: string) =>
    getJson<any>(`/api/v1/gold/collections/legal-notices/${noticeId}`),

  updateLegalNotice: (noticeId: string, data: any) =>
    patchJson<any>(`/api/v1/gold/collections/legal-notices/${noticeId}`, data),

  deleteLegalNotice: (noticeId: string) =>
    deleteJson(`/api/v1/gold/collections/legal-notices/${noticeId}`),

  // Auction Lots
  createAuctionLot: (data: any) =>
    postJson<any>('/api/v1/gold/collections/auction-lots', data),

  getAuctionLots: (filters?: {
    lot_status?: string;
    auction_type?: string;
    from_date?: string;
    to_date?: string;
    skip?: number;
    limit?: number;
  }) => {
    const params = new URLSearchParams();
    if (filters?.lot_status) params.append('lot_status', filters.lot_status);
    if (filters?.auction_type) params.append('auction_type', filters.auction_type);
    if (filters?.from_date) params.append('from_date', filters.from_date);
    if (filters?.to_date) params.append('to_date', filters.to_date);
    if (filters?.skip) params.append('skip', filters.skip.toString());
    if (filters?.limit) params.append('limit', filters.limit.toString());
    const query = params.toString() ? `?${params.toString()}` : '';
    return getJson<any>(`/api/v1/gold/collections/auction-lots${query}`);
  },

  getAuctionLot: (lotId: string) =>
    getJson<any>(`/api/v1/gold/collections/auction-lots/${lotId}`),

  updateAuctionLot: (lotId: string, data: any) =>
    patchJson<any>(`/api/v1/gold/collections/auction-lots/${lotId}`, data),

  deleteAuctionLot: (lotId: string) =>
    deleteJson(`/api/v1/gold/collections/auction-lots/${lotId}`),

  // Auction Lot Items
  createAuctionLotItem: (data: any) =>
    postJson<any>('/api/v1/gold/collections/auction-lot-items', data),

  getAuctionLotItems: (filters?: {
    auction_lot_id?: string;
    collection_case_id?: string;
    skip?: number;
    limit?: number;
  }) => {
    const params = new URLSearchParams();
    if (filters?.auction_lot_id) params.append('auction_lot_id', filters.auction_lot_id);
    if (filters?.collection_case_id) params.append('collection_case_id', filters.collection_case_id);
    if (filters?.skip) params.append('skip', filters.skip.toString());
    if (filters?.limit) params.append('limit', filters.limit.toString());
    const query = params.toString() ? `?${params.toString()}` : '';
    return getJson<any[]>(`/api/v1/gold/collections/auction-lot-items${query}`);
  },

  getAuctionLotItem: (itemId: string) =>
    getJson<any>(`/api/v1/gold/collections/auction-lot-items/${itemId}`),

  updateAuctionLotItem: (itemId: string, data: any) =>
    patchJson<any>(`/api/v1/gold/collections/auction-lot-items/${itemId}`, data),

  deleteAuctionLotItem: (itemId: string) =>
    deleteJson(`/api/v1/gold/collections/auction-lot-items/${itemId}`),

  // Auction Bids
  createAuctionBid: (data: any) =>
    postJson<any>('/api/v1/gold/collections/auction-bids', data),

  getAuctionBids: (filters?: {
    auction_lot_id?: string;
    bidder_id?: string;
    bid_status?: string;
    skip?: number;
    limit?: number;
  }) => {
    const params = new URLSearchParams();
    if (filters?.auction_lot_id) params.append('auction_lot_id', filters.auction_lot_id);
    if (filters?.bidder_id) params.append('bidder_id', filters.bidder_id);
    if (filters?.bid_status) params.append('bid_status', filters.bid_status);
    if (filters?.skip) params.append('skip', filters.skip.toString());
    if (filters?.limit) params.append('limit', filters.limit.toString());
    const query = params.toString() ? `?${params.toString()}` : '';
    return getJson<any[]>(`/api/v1/gold/collections/auction-bids${query}`);
  },

  getAuctionBid: (bidId: string) =>
    getJson<any>(`/api/v1/gold/collections/auction-bids/${bidId}`),

  updateAuctionBid: (bidId: string, data: any) =>
    patchJson<any>(`/api/v1/gold/collections/auction-bids/${bidId}`, data),

  deleteAuctionBid: (bidId: string) =>
    deleteJson(`/api/v1/gold/collections/auction-bids/${bidId}`),

  // Communication Logs
  createCommunicationLog: (data: any) =>
    postJson<any>('/api/v1/gold/collections/communication-logs', data),

  getCommunicationLogs: (filters?: {
    collection_case_id?: string;
    communication_type?: string;
    direction?: string;
    from_date?: string;
    to_date?: string;
    skip?: number;
    limit?: number;
  }) => {
    const params = new URLSearchParams();
    if (filters?.collection_case_id) params.append('collection_case_id', filters.collection_case_id);
    if (filters?.communication_type) params.append('communication_type', filters.communication_type);
    if (filters?.direction) params.append('direction', filters.direction);
    if (filters?.from_date) params.append('from_date', filters.from_date);
    if (filters?.to_date) params.append('to_date', filters.to_date);
    if (filters?.skip) params.append('skip', filters.skip.toString());
    if (filters?.limit) params.append('limit', filters.limit.toString());
    const query = params.toString() ? `?${params.toString()}` : '';
    return getJson<any[]>(`/api/v1/gold/collections/communication-logs${query}`);
  },

  getCommunicationLog: (logId: string) =>
    getJson<any>(`/api/v1/gold/collections/communication-logs/${logId}`),

  updateCommunicationLog: (logId: string, data: any) =>
    patchJson<any>(`/api/v1/gold/collections/communication-logs/${logId}`, data),

  deleteCommunicationLog: (logId: string) =>
    deleteJson(`/api/v1/gold/collections/communication-logs/${logId}`),

  // Settlement Offers
  createSettlementOffer: (data: any) =>
    postJson<any>('/api/v1/gold/collections/settlement-offers', data),

  getSettlementOffers: (filters?: {
    collection_case_id?: string;
    offer_status?: string;
    offered_by?: string;
    from_date?: string;
    to_date?: string;
    skip?: number;
    limit?: number;
  }) => {
    const params = new URLSearchParams();
    if (filters?.collection_case_id) params.append('collection_case_id', filters.collection_case_id);
    if (filters?.offer_status) params.append('offer_status', filters.offer_status);
    if (filters?.offered_by) params.append('offered_by', filters.offered_by);
    if (filters?.from_date) params.append('from_date', filters.from_date);
    if (filters?.to_date) params.append('to_date', filters.to_date);
    if (filters?.skip) params.append('skip', filters.skip.toString());
    if (filters?.limit) params.append('limit', filters.limit.toString());
    const query = params.toString() ? `?${params.toString()}` : '';
    return getJson<any[]>(`/api/v1/gold/collections/settlement-offers${query}`);
  },

  getSettlementOffer: (offerId: string) =>
    getJson<any>(`/api/v1/gold/collections/settlement-offers/${offerId}`),

  updateSettlementOffer: (offerId: string, data: any) =>
    patchJson<any>(`/api/v1/gold/collections/settlement-offers/${offerId}`, data),

  deleteSettlementOffer: (offerId: string) =>
    deleteJson(`/api/v1/gold/collections/settlement-offers/${offerId}`),

  // Collection Performance
  createPerformanceRecord: (data: any) =>
    postJson<any>('/api/v1/gold/collections/performance', data),

  getPerformanceRecords: (filters?: {
    user_id?: string;
    team_name?: string;
    region?: string;
    from_date?: string;
    to_date?: string;
    skip?: number;
    limit?: number;
  }) => {
    const params = new URLSearchParams();
    if (filters?.user_id) params.append('user_id', filters.user_id);
    if (filters?.team_name) params.append('team_name', filters.team_name);
    if (filters?.region) params.append('region', filters.region);
    if (filters?.from_date) params.append('from_date', filters.from_date);
    if (filters?.to_date) params.append('to_date', filters.to_date);
    if (filters?.skip) params.append('skip', filters.skip.toString());
    if (filters?.limit) params.append('limit', filters.limit.toString());
    const query = params.toString() ? `?${params.toString()}` : '';
    return getJson<any[]>(`/api/v1/gold/collections/performance${query}`);
  },

  getPerformanceRecord: (performanceId: string) =>
    getJson<any>(`/api/v1/gold/collections/performance/${performanceId}`),

  updatePerformanceRecord: (performanceId: string, data: any) =>
    patchJson<any>(`/api/v1/gold/collections/performance/${performanceId}`, data),

  deletePerformanceRecord: (performanceId: string) =>
    deleteJson(`/api/v1/gold/collections/performance/${performanceId}`),

  // Dashboard & Analytics
  getCollectionDashboard: (filters?: {
    from_date?: string;
    to_date?: string;
  }) => {
    const params = new URLSearchParams();
    if (filters?.from_date) params.append('from_date', filters.from_date);
    if (filters?.to_date) params.append('to_date', filters.to_date);
    const query = params.toString() ? `?${params.toString()}` : '';
    return getJson<any>(`/api/v1/gold/collections/dashboard${query}`);
  },

  // ========================================================================
  // REPORTING & ANALYTICS (Phase 9)
  // ========================================================================

  // Report Definitions
  createReportDefinition: (data: any) =>
    postJson<any>('/api/v1/gold/reporting/definitions', data),

  getReportDefinitions: (filters?: {
    category?: string;
    report_type?: string;
    is_active?: boolean;
    is_system?: boolean;
    skip?: number;
    limit?: number;
  }) => {
    const params = new URLSearchParams();
    if (filters?.category) params.append('category', filters.category);
    if (filters?.report_type) params.append('report_type', filters.report_type);
    if (filters?.is_active !== undefined) params.append('is_active', filters.is_active.toString());
    if (filters?.is_system !== undefined) params.append('is_system', filters.is_system.toString());
    if (filters?.skip) params.append('skip', filters.skip.toString());
    if (filters?.limit) params.append('limit', filters.limit.toString());
    const query = params.toString() ? `?${params.toString()}` : '';
    return getJson<any[]>(`/api/v1/gold/reporting/definitions${query}`);
  },

  getReportDefinition: (definitionId: string) =>
    getJson<any>(`/api/v1/gold/reporting/definitions/${definitionId}`),

  getReportDefinitionByCode: (code: string) =>
    getJson<any>(`/api/v1/gold/reporting/definitions/by-code/${code}`),

  updateReportDefinition: (definitionId: string, data: any) =>
    patchJson<any>(`/api/v1/gold/reporting/definitions/${definitionId}`, data),

  deleteReportDefinition: (definitionId: string) =>
    deleteJson(`/api/v1/gold/reporting/definitions/${definitionId}`),

  // Report Templates
  createReportTemplate: (data: any) =>
    postJson<any>('/api/v1/gold/reporting/templates', data),

  getReportTemplates: (filters?: {
    report_definition_id?: string;
    template_type?: string;
    is_active?: boolean;
    skip?: number;
    limit?: number;
  }) => {
    const params = new URLSearchParams();
    if (filters?.report_definition_id) params.append('report_definition_id', filters.report_definition_id);
    if (filters?.template_type) params.append('template_type', filters.template_type);
    if (filters?.is_active !== undefined) params.append('is_active', filters.is_active.toString());
    if (filters?.skip) params.append('skip', filters.skip.toString());
    if (filters?.limit) params.append('limit', filters.limit.toString());
    const query = params.toString() ? `?${params.toString()}` : '';
    return getJson<any[]>(`/api/v1/gold/reporting/templates${query}`);
  },

  getReportTemplate: (templateId: string) =>
    getJson<any>(`/api/v1/gold/reporting/templates/${templateId}`),

  updateReportTemplate: (templateId: string, data: any) =>
    patchJson<any>(`/api/v1/gold/reporting/templates/${templateId}`, data),

  deleteReportTemplate: (templateId: string) =>
    deleteJson(`/api/v1/gold/reporting/templates/${templateId}`),

  // Report Schedules
  createReportSchedule: (data: any) =>
    postJson<any>('/api/v1/gold/reporting/schedules', data),

  getReportSchedules: (filters?: {
    report_definition_id?: string;
    status?: string;
    is_active?: boolean;
    skip?: number;
    limit?: number;
  }) => {
    const params = new URLSearchParams();
    if (filters?.report_definition_id) params.append('report_definition_id', filters.report_definition_id);
    if (filters?.status) params.append('status', filters.status);
    if (filters?.is_active !== undefined) params.append('is_active', filters.is_active.toString());
    if (filters?.skip) params.append('skip', filters.skip.toString());
    if (filters?.limit) params.append('limit', filters.limit.toString());
    const query = params.toString() ? `?${params.toString()}` : '';
    return getJson<any[]>(`/api/v1/gold/reporting/schedules${query}`);
  },

  getReportSchedule: (scheduleId: string) =>
    getJson<any>(`/api/v1/gold/reporting/schedules/${scheduleId}`),

  updateReportSchedule: (scheduleId: string, data: any) =>
    patchJson<any>(`/api/v1/gold/reporting/schedules/${scheduleId}`, data),

  pauseReportSchedule: (scheduleId: string, reason?: string) =>
    postJson<any>(`/api/v1/gold/reporting/schedules/${scheduleId}/pause`, { reason }),

  resumeReportSchedule: (scheduleId: string, nextExecutionAt?: string) =>
    postJson<any>(`/api/v1/gold/reporting/schedules/${scheduleId}/resume`, { next_execution_at: nextExecutionAt }),

  executeScheduleNow: (scheduleId: string, overrideParameters?: any) =>
    postJson<any>(`/api/v1/gold/reporting/schedules/${scheduleId}/execute`, { override_parameters: overrideParameters }),

  deleteReportSchedule: (scheduleId: string) =>
    deleteJson(`/api/v1/gold/reporting/schedules/${scheduleId}`),

  // Report Executions
  createReportExecution: (data: any) =>
    postJson<any>('/api/v1/gold/reporting/executions', data),

  getReportExecutions: (filters?: {
    report_definition_id?: string;
    schedule_id?: string;
    status?: string;
    execution_type?: string;
    date_from?: string;
    date_to?: string;
    skip?: number;
    limit?: number;
  }) => {
    const params = new URLSearchParams();
    if (filters?.report_definition_id) params.append('report_definition_id', filters.report_definition_id);
    if (filters?.schedule_id) params.append('schedule_id', filters.schedule_id);
    if (filters?.status) params.append('status', filters.status);
    if (filters?.execution_type) params.append('execution_type', filters.execution_type);
    if (filters?.date_from) params.append('date_from', filters.date_from);
    if (filters?.date_to) params.append('date_to', filters.date_to);
    if (filters?.skip) params.append('skip', filters.skip.toString());
    if (filters?.limit) params.append('limit', filters.limit.toString());
    const query = params.toString() ? `?${params.toString()}` : '';
    return getJson<any[]>(`/api/v1/gold/reporting/executions${query}`);
  },

  getReportExecution: (executionId: string) =>
    getJson<any>(`/api/v1/gold/reporting/executions/${executionId}`),

  updateReportExecution: (executionId: string, data: any) =>
    patchJson<any>(`/api/v1/gold/reporting/executions/${executionId}`, data),

  cancelReportExecution: (executionId: string) =>
    postJson<any>(`/api/v1/gold/reporting/executions/${executionId}/cancel`, {}),

  // Report Parameters
  createReportParameter: (data: any) =>
    postJson<any>('/api/v1/gold/reporting/parameters', data),

  getReportParameters: (reportDefinitionId: string, isActive?: boolean) => {
    const params = new URLSearchParams({ report_definition_id: reportDefinitionId });
    if (isActive !== undefined) params.append('is_active', isActive.toString());
    const query = params.toString() ? `?${params.toString()}` : '';
    return getJson<any[]>(`/api/v1/gold/reporting/parameters${query}`);
  },

  getReportParameter: (parameterId: string) =>
    getJson<any>(`/api/v1/gold/reporting/parameters/${parameterId}`),

  updateReportParameter: (parameterId: string, data: any) =>
    patchJson<any>(`/api/v1/gold/reporting/parameters/${parameterId}`, data),

  deleteReportParameter: (parameterId: string) =>
    deleteJson(`/api/v1/gold/reporting/parameters/${parameterId}`),

  // Report Exports
  createReportExport: (data: any) =>
    postJson<any>('/api/v1/gold/reporting/exports', data),

  getReportExports: (filters?: {
    execution_id?: string;
    export_format?: string;
    status?: string;
    skip?: number;
    limit?: number;
  }) => {
    const params = new URLSearchParams();
    if (filters?.execution_id) params.append('execution_id', filters.execution_id);
    if (filters?.export_format) params.append('export_format', filters.export_format);
    if (filters?.status) params.append('status', filters.status);
    if (filters?.skip) params.append('skip', filters.skip.toString());
    if (filters?.limit) params.append('limit', filters.limit.toString());
    const query = params.toString() ? `?${params.toString()}` : '';
    return getJson<any[]>(`/api/v1/gold/reporting/exports${query}`);
  },

  getReportExport: (exportId: string) =>
    getJson<any>(`/api/v1/gold/reporting/exports/${exportId}`),

  downloadReportExport: (exportId: string) =>
    getJson<any>(`/api/v1/gold/reporting/exports/${exportId}/download`),

  shareReportExport: (exportId: string, data: any) =>
    postJson<any>(`/api/v1/gold/reporting/exports/${exportId}/share`, data),

  deleteReportExport: (exportId: string) =>
    deleteJson(`/api/v1/gold/reporting/exports/${exportId}`),

  // Dashboard Definitions
  createDashboard: (data: any) =>
    postJson<any>('/api/v1/gold/reporting/dashboards', data),

  getDashboards: (filters?: {
    dashboard_type?: string;
    category?: string;
    is_active?: boolean;
    skip?: number;
    limit?: number;
  }) => {
    const params = new URLSearchParams();
    if (filters?.dashboard_type) params.append('dashboard_type', filters.dashboard_type);
    if (filters?.category) params.append('category', filters.category);
    if (filters?.is_active !== undefined) params.append('is_active', filters.is_active.toString());
    if (filters?.skip) params.append('skip', filters.skip.toString());
    if (filters?.limit) params.append('limit', filters.limit.toString());
    const query = params.toString() ? `?${params.toString()}` : '';
    return getJson<any[]>(`/api/v1/gold/reporting/dashboards${query}`);
  },

  getDashboard: (dashboardId: string) =>
    getJson<any>(`/api/v1/gold/reporting/dashboards/${dashboardId}`),

  getDashboardByCode: (code: string) =>
    getJson<any>(`/api/v1/gold/reporting/dashboards/by-code/${code}`),

  updateDashboard: (dashboardId: string, data: any) =>
    patchJson<any>(`/api/v1/gold/reporting/dashboards/${dashboardId}`, data),

  deleteDashboard: (dashboardId: string) =>
    deleteJson(`/api/v1/gold/reporting/dashboards/${dashboardId}`),

  // Dashboard Widgets
  createDashboardWidget: (dashboardId: string, data: any) =>
    postJson<any>(`/api/v1/gold/reporting/dashboards/${dashboardId}/widgets`, data),

  getDashboardWidgets: (dashboardId: string, isVisible?: boolean) => {
    const params = isVisible !== undefined ? `?is_visible=${isVisible}` : '';
    return getJson<any[]>(`/api/v1/gold/reporting/dashboards/${dashboardId}/widgets${params}`);
  },

  getDashboardWidget: (widgetId: string) =>
    getJson<any>(`/api/v1/gold/reporting/widgets/${widgetId}`),

  updateDashboardWidget: (widgetId: string, data: any) =>
    patchJson<any>(`/api/v1/gold/reporting/widgets/${widgetId}`, data),

  deleteDashboardWidget: (widgetId: string) =>
    deleteJson(`/api/v1/gold/reporting/widgets/${widgetId}`),

  getWidgetData: (widgetId: string, filters?: {
    date_from?: string;
    date_to?: string;
    filters?: string;
  }) => {
    const params = new URLSearchParams();
    if (filters?.date_from) params.append('date_from', filters.date_from);
    if (filters?.date_to) params.append('date_to', filters.date_to);
    if (filters?.filters) params.append('filters', filters.filters);
    const query = params.toString() ? `?${params.toString()}` : '';
    return getJson<any>(`/api/v1/gold/reporting/widgets/${widgetId}/data${query}`);
  },

  // Data Snapshots
  createDataSnapshot: (data: any) =>
    postJson<any>('/api/v1/gold/reporting/snapshots', data),

  getDataSnapshots: (filters?: {
    snapshot_type?: string;
    entity_type?: string;
    date_from?: string;
    date_to?: string;
    status?: string;
    skip?: number;
    limit?: number;
  }) => {
    const params = new URLSearchParams();
    if (filters?.snapshot_type) params.append('snapshot_type', filters.snapshot_type);
    if (filters?.entity_type) params.append('entity_type', filters.entity_type);
    if (filters?.date_from) params.append('date_from', filters.date_from);
    if (filters?.date_to) params.append('date_to', filters.date_to);
    if (filters?.status) params.append('status', filters.status);
    if (filters?.skip) params.append('skip', filters.skip.toString());
    if (filters?.limit) params.append('limit', filters.limit.toString());
    const query = params.toString() ? `?${params.toString()}` : '';
    return getJson<any[]>(`/api/v1/gold/reporting/snapshots${query}`);
  },

  getDataSnapshot: (snapshotId: string) =>
    getJson<any>(`/api/v1/gold/reporting/snapshots/${snapshotId}`),

  updateDataSnapshot: (snapshotId: string, data: any) =>
    patchJson<any>(`/api/v1/gold/reporting/snapshots/${snapshotId}`, data),

  deleteDataSnapshot: (snapshotId: string) =>
    deleteJson(`/api/v1/gold/reporting/snapshots/${snapshotId}`),

  // Analytics Metrics
  createAnalyticsMetric: (data: any) =>
    postJson<any>('/api/v1/gold/reporting/metrics', data),

  getAnalyticsMetrics: (filters?: {
    metric_category?: string;
    metric_type?: string;
    is_kpi?: boolean;
    is_active?: boolean;
    skip?: number;
    limit?: number;
  }) => {
    const params = new URLSearchParams();
    if (filters?.metric_category) params.append('metric_category', filters.metric_category);
    if (filters?.metric_type) params.append('metric_type', filters.metric_type);
    if (filters?.is_kpi !== undefined) params.append('is_kpi', filters.is_kpi.toString());
    if (filters?.is_active !== undefined) params.append('is_active', filters.is_active.toString());
    if (filters?.skip) params.append('skip', filters.skip.toString());
    if (filters?.limit) params.append('limit', filters.limit.toString());
    const query = params.toString() ? `?${params.toString()}` : '';
    return getJson<any[]>(`/api/v1/gold/reporting/metrics${query}`);
  },

  getAnalyticsMetric: (metricId: string) =>
    getJson<any>(`/api/v1/gold/reporting/metrics/${metricId}`),

  getAnalyticsMetricByCode: (code: string) =>
    getJson<any>(`/api/v1/gold/reporting/metrics/by-code/${code}`),

  updateAnalyticsMetric: (metricId: string, data: any) =>
    patchJson<any>(`/api/v1/gold/reporting/metrics/${metricId}`, data),

  deleteAnalyticsMetric: (metricId: string) =>
    deleteJson(`/api/v1/gold/reporting/metrics/${metricId}`),

  // Report Generation
  generateReport: (data: any) =>
    postJson<any>('/api/v1/gold/reporting/generate', data),

  getReportCatalog: (category?: string) => {
    const params = category ? `?category=${category}` : '';
    return getJson<any>(`/api/v1/gold/reporting/catalog${params}`);
  },

  queryAnalytics: (data: any) =>
    postJson<any>('/api/v1/gold/reporting/analytics/query', data),

  getDashboardAnalytics: (dashboardCode: string, data: any) =>
    postJson<any>(`/api/v1/gold/reporting/dashboards/${dashboardCode}/analytics`, data),
};

  // ============================================================================
  // DOCUMENT MANAGEMENT API
  // ============================================================================
  
  // Document Categories
  createDocumentCategory: (payload: unknown) => 
    postJson('/api/v1/gold/documents/categories', payload),
  listDocumentCategories: (params?: { is_active?: boolean; parent_category_id?: string; skip?: number; limit?: number }) => {
    const query = new URLSearchParams();
    if (params?.is_active !== undefined) query.append('is_active', String(params.is_active));
    if (params?.parent_category_id) query.append('parent_category_id', params.parent_category_id);
    if (params?.skip !== undefined) query.append('skip', String(params.skip));
    if (params?.limit !== undefined) query.append('limit', String(params.limit));
    return getJson<any[]>(`/api/v1/gold/documents/categories?${query.toString()}`);
  },
  getDocumentCategory: (categoryId: string) => 
    getJson<any>(`/api/v1/gold/documents/categories/${categoryId}`),
  updateDocumentCategory: (categoryId: string, payload: unknown) => 
    patchJson(`/api/v1/gold/documents/categories/${categoryId}`, payload),
  deleteDocumentCategory: (categoryId: string) => 
    deleteJson(`/api/v1/gold/documents/categories/${categoryId}`),
  
  // Documents
  createDocument: (payload: unknown) => 
    postJson('/api/v1/gold/documents', payload),
  listDocuments: (params?: { 
    category_id?: string; 
    document_type?: string; 
    entity_type?: string; 
    entity_id?: string; 
    storage_status?: string; 
    is_deleted?: boolean; 
    search?: string;
    from_date?: string;
    to_date?: string;
    skip?: number; 
    limit?: number;
  }) => {
    const query = new URLSearchParams();
    if (params?.category_id) query.append('category_id', params.category_id);
    if (params?.document_type) query.append('document_type', params.document_type);
    if (params?.entity_type) query.append('entity_type', params.entity_type);
    if (params?.entity_id) query.append('entity_id', params.entity_id);
    if (params?.storage_status) query.append('storage_status', params.storage_status);
    if (params?.is_deleted !== undefined) query.append('is_deleted', String(params.is_deleted));
    if (params?.search) query.append('search', params.search);
    if (params?.from_date) query.append('from_date', params.from_date);
    if (params?.to_date) query.append('to_date', params.to_date);
    if (params?.skip !== undefined) query.append('skip', String(params.skip));
    if (params?.limit !== undefined) query.append('limit', String(params.limit));
    return getJson<any[]>(`/api/v1/gold/documents?${query.toString()}`);
  },
  getDocument: (documentId: string) => 
    getJson<any>(`/api/v1/gold/documents/${documentId}`),
  updateDocument: (documentId: string, payload: unknown) => 
    patchJson(`/api/v1/gold/documents/${documentId}`, payload),
  deleteDocument: (documentId: string, deletedBy: string) => 
    deleteJson(`/api/v1/gold/documents/${documentId}?deleted_by=${deletedBy}`),
  restoreDocument: (documentId: string) => 
    postJson(`/api/v1/gold/documents/${documentId}/restore`, {}),
  
  // Document Versions
  listDocumentVersions: (documentId: string) => 
    getJson<any[]>(`/api/v1/gold/documents/${documentId}/versions`),
  getDocumentVersion: (documentId: string, versionNumber: number) => 
    getJson<any>(`/api/v1/gold/documents/${documentId}/versions/${versionNumber}`),
  restoreDocumentVersion: (documentId: string, versionNumber: number, restoredBy: string) => 
    postJson(`/api/v1/gold/documents/${documentId}/versions/${versionNumber}/restore?restored_by=${restoredBy}`, {}),
  
  // Document Metadata
  addDocumentMetadata: (documentId: string, payload: unknown) => 
    postJson(`/api/v1/gold/documents/${documentId}/metadata`, payload),
  listDocumentMetadata: (documentId: string) => 
    getJson<any[]>(`/api/v1/gold/documents/${documentId}/metadata`),
  updateDocumentMetadata: (documentId: string, metadataId: string, payload: unknown) => 
    patchJson(`/api/v1/gold/documents/${documentId}/metadata/${metadataId}`, payload),
  deleteDocumentMetadata: (documentId: string, metadataId: string) => 
    deleteJson(`/api/v1/gold/documents/${documentId}/metadata/${metadataId}`),
  
  // Document Templates
  createDocumentTemplate: (payload: unknown) => 
    postJson('/api/v1/gold/documents/templates', payload),
  listDocumentTemplates: (params?: { category_id?: string; template_type?: string; is_active?: boolean; skip?: number; limit?: number }) => {
    const query = new URLSearchParams();
    if (params?.category_id) query.append('category_id', params.category_id);
    if (params?.template_type) query.append('template_type', params.template_type);
    if (params?.is_active !== undefined) query.append('is_active', String(params.is_active));
    if (params?.skip !== undefined) query.append('skip', String(params.skip));
    if (params?.limit !== undefined) query.append('limit', String(params.limit));
    return getJson<any[]>(`/api/v1/gold/documents/templates?${query.toString()}`);
  },
  getDocumentTemplate: (templateId: string) => 
    getJson<any>(`/api/v1/gold/documents/templates/${templateId}`),
  updateDocumentTemplate: (templateId: string, payload: unknown) => 
    patchJson(`/api/v1/gold/documents/templates/${templateId}`, payload),
  deleteDocumentTemplate: (templateId: string) => 
    deleteJson(`/api/v1/gold/documents/templates/${templateId}`),
  
  // Document Workflows
  createDocumentWorkflow: (payload: unknown) => 
    postJson('/api/v1/gold/documents/workflows', payload),
  listDocumentWorkflows: (params?: { category_id?: string; workflow_type?: string; is_active?: boolean; skip?: number; limit?: number }) => {
    const query = new URLSearchParams();
    if (params?.category_id) query.append('category_id', params.category_id);
    if (params?.workflow_type) query.append('workflow_type', params.workflow_type);
    if (params?.is_active !== undefined) query.append('is_active', String(params.is_active));
    if (params?.skip !== undefined) query.append('skip', String(params.skip));
    if (params?.limit !== undefined) query.append('limit', String(params.limit));
    return getJson<any[]>(`/api/v1/gold/documents/workflows?${query.toString()}`);
  },
  getDocumentWorkflow: (workflowId: string) => 
    getJson<any>(`/api/v1/gold/documents/workflows/${workflowId}`),
  updateDocumentWorkflow: (workflowId: string, payload: unknown) => 
    patchJson(`/api/v1/gold/documents/workflows/${workflowId}`, payload),
  deleteDocumentWorkflow: (workflowId: string) => 
    deleteJson(`/api/v1/gold/documents/workflows/${workflowId}`),
  
  // Document Approvals
  createDocumentApproval: (payload: unknown) => 
    postJson('/api/v1/gold/documents/approvals', payload),
  listDocumentApprovals: (params?: { 
    workflow_id?: string; 
    approval_status?: string; 
    assigned_to?: string; 
    initiated_by?: string; 
    priority?: string; 
    is_escalated?: boolean;
    from_date?: string;
    to_date?: string;
    skip?: number; 
    limit?: number;
  }) => {
    const query = new URLSearchParams();
    if (params?.workflow_id) query.append('workflow_id', params.workflow_id);
    if (params?.approval_status) query.append('approval_status', params.approval_status);
    if (params?.assigned_to) query.append('assigned_to', params.assigned_to);
    if (params?.initiated_by) query.append('initiated_by', params.initiated_by);
    if (params?.priority) query.append('priority', params.priority);
    if (params?.is_escalated !== undefined) query.append('is_escalated', String(params.is_escalated));
    if (params?.from_date) query.append('from_date', params.from_date);
    if (params?.to_date) query.append('to_date', params.to_date);
    if (params?.skip !== undefined) query.append('skip', String(params.skip));
    if (params?.limit !== undefined) query.append('limit', String(params.limit));
    return getJson<any[]>(`/api/v1/gold/documents/approvals?${query.toString()}`);
  },
  getDocumentApproval: (approvalId: string) => 
    getJson<any>(`/api/v1/gold/documents/approvals/${approvalId}`),
  takeApprovalAction: (approvalId: string, payload: unknown) => 
    postJson(`/api/v1/gold/documents/approvals/${approvalId}/action`, payload),
  updateDocumentApproval: (approvalId: string, payload: unknown) => 
    patchJson(`/api/v1/gold/documents/approvals/${approvalId}`, payload),
  
  // Document Tags
  createDocumentTag: (payload: unknown) => 
    postJson('/api/v1/gold/documents/tags', payload),
  listDocumentTags: (params?: { tag_category?: string; is_active?: boolean; search?: string; skip?: number; limit?: number }) => {
    const query = new URLSearchParams();
    if (params?.tag_category) query.append('tag_category', params.tag_category);
    if (params?.is_active !== undefined) query.append('is_active', String(params.is_active));
    if (params?.search) query.append('search', params.search);
    if (params?.skip !== undefined) query.append('skip', String(params.skip));
    if (params?.limit !== undefined) query.append('limit', String(params.limit));
    return getJson<any[]>(`/api/v1/gold/documents/tags?${query.toString()}`);
  },
  getDocumentTag: (tagId: string) => 
    getJson<any>(`/api/v1/gold/documents/tags/${tagId}`),
  updateDocumentTag: (tagId: string, payload: unknown) => 
    patchJson(`/api/v1/gold/documents/tags/${tagId}`, payload),
  deleteDocumentTag: (tagId: string) => 
    deleteJson(`/api/v1/gold/documents/tags/${tagId}`),
  
  // Document-Tag Mappings
  addTagToDocument: (documentId: string, payload: unknown) => 
    postJson(`/api/v1/gold/documents/${documentId}/tags`, payload),
  listDocumentTagsForDocument: (documentId: string) => 
    getJson<any[]>(`/api/v1/gold/documents/${documentId}/tags`),
  removeTagFromDocument: (documentId: string, tagId: string) => 
    deleteJson(`/api/v1/gold/documents/${documentId}/tags/${tagId}`),
  
  // Document Access Logs
  createDocumentAccessLog: (payload: unknown) => 
    postJson('/api/v1/gold/documents/access-logs', payload),
  listDocumentAccessLogs: (params?: { 
    document_id?: string; 
    user_id?: string; 
    action_type?: string; 
    access_result?: string;
    from_date?: string;
    to_date?: string;
    skip?: number; 
    limit?: number;
  }) => {
    const query = new URLSearchParams();
    if (params?.document_id) query.append('document_id', params.document_id);
    if (params?.user_id) query.append('user_id', params.user_id);
    if (params?.action_type) query.append('action_type', params.action_type);
    if (params?.access_result) query.append('access_result', params.access_result);
    if (params?.from_date) query.append('from_date', params.from_date);
    if (params?.to_date) query.append('to_date', params.to_date);
    if (params?.skip !== undefined) query.append('skip', String(params.skip));
    if (params?.limit !== undefined) query.append('limit', String(params.limit));
    return getJson<any[]>(`/api/v1/gold/documents/access-logs?${query.toString()}`);
  },
  getDocumentAccessLogs: (documentId: string, skip?: number, limit?: number) => {
    const query = new URLSearchParams();
    if (skip !== undefined) query.append('skip', String(skip));
    if (limit !== undefined) query.append('limit', String(limit));
    return getJson<any[]>(`/api/v1/gold/documents/${documentId}/access-logs?${query.toString()}`);
  },
  
  // Document Retention Policies
  createRetentionPolicy: (payload: unknown) => 
    postJson('/api/v1/gold/documents/retention-policies', payload),
  listRetentionPolicies: (params?: { category_id?: string; document_type?: string; is_active?: boolean; skip?: number; limit?: number }) => {
    const query = new URLSearchParams();
    if (params?.category_id) query.append('category_id', params.category_id);
    if (params?.document_type) query.append('document_type', params.document_type);
    if (params?.is_active !== undefined) query.append('is_active', String(params.is_active));
    if (params?.skip !== undefined) query.append('skip', String(params.skip));
    if (params?.limit !== undefined) query.append('limit', String(params.limit));
    return getJson<any[]>(`/api/v1/gold/documents/retention-policies?${query.toString()}`);
  },
  getRetentionPolicy: (policyId: string) => 
    getJson<any>(`/api/v1/gold/documents/retention-policies/${policyId}`),
  updateRetentionPolicy: (policyId: string, payload: unknown) => 
    patchJson(`/api/v1/gold/documents/retention-policies/${policyId}`, payload),
  deleteRetentionPolicy: (policyId: string) => 
    deleteJson(`/api/v1/gold/documents/retention-policies/${policyId}`),
  
  // Document Shares
  createDocumentShare: (payload: unknown) => 
    postJson('/api/v1/gold/documents/shares', payload),
  listDocumentShares: (params?: { document_id?: string; shared_by?: string; is_revoked?: boolean; skip?: number; limit?: number }) => {
    const query = new URLSearchParams();
    if (params?.document_id) query.append('document_id', params.document_id);
    if (params?.shared_by) query.append('shared_by', params.shared_by);
    if (params?.is_revoked !== undefined) query.append('is_revoked', String(params.is_revoked));
    if (params?.skip !== undefined) query.append('skip', String(params.skip));
    if (params?.limit !== undefined) query.append('limit', String(params.limit));
    return getJson<any[]>(`/api/v1/gold/documents/shares?${query.toString()}`);
  },
  getDocumentShare: (shareId: string) => 
    getJson<any>(`/api/v1/gold/documents/shares/${shareId}`),
  getDocumentShareByToken: (shareToken: string) => 
    getJson<any>(`/api/v1/gold/documents/shares/token/${shareToken}`),
  updateDocumentShare: (shareId: string, payload: unknown) => 
    patchJson(`/api/v1/gold/documents/shares/${shareId}`, payload),
  revokeDocumentShare: (shareId: string, payload: unknown) => 
    postJson(`/api/v1/gold/documents/shares/${shareId}/revoke`, payload),
  listSharesForDocument: (documentId: string) => 
    getJson<any[]>(`/api/v1/gold/documents/${documentId}/shares`),
  
  // Bulk Operations
  bulkTagDocuments: (payload: unknown) => 
    postJson('/api/v1/gold/documents/bulk/tag', payload),
  bulkDeleteDocuments: (payload: unknown) => 
    postJson('/api/v1/gold/documents/bulk/delete', payload),
  bulkMoveDocuments: (payload: unknown) => 
    postJson('/api/v1/gold/documents/bulk/move', payload),
  
  // OCR Operations
  extractDocumentTextOCR: (payload: unknown) => 
    postJson('/api/v1/gold/documents/ocr/extract', payload),
  reprocessDocumentOCR: (documentId: string, ocrLanguage?: string) => {
    const query = new URLSearchParams();
    if (ocrLanguage) query.append('ocr_language', ocrLanguage);
    return postJson(`/api/v1/gold/documents/${documentId}/ocr/reprocess?${query.toString()}`, {});
  },
  
  // Statistics
  getDocumentStatistics: () => 
    getJson<any>('/api/v1/gold/documents/statistics/overview'),
  getWorkflowStatistics: () => 
    getJson<any>('/api/v1/gold/documents/statistics/workflows'),
  getCategoryStatistics: (categoryId: string) => 
    getJson<any>(`/api/v1/gold/documents/statistics/category/${categoryId}`),
  getUserDocumentStatistics: (userId: string) => 
    getJson<any>(`/api/v1/gold/documents/statistics/user/${userId}`),

  // ============================================================================
  // RISK MANAGEMENT - Phase 11
  // ============================================================================
  
  // Risk Parameters
  createRiskParameter: (payload: unknown) => 
    postJson('/api/v1/gold/risk/parameters', payload),
  listRiskParameters: (params?: { risk_category?: string; parameter_type?: string; is_active?: boolean; skip?: number; limit?: number }) => {
    const query = new URLSearchParams();
    if (params?.risk_category) query.append('risk_category', params.risk_category);
    if (params?.parameter_type) query.append('parameter_type', params.parameter_type);
    if (params?.is_active !== undefined) query.append('is_active', String(params.is_active));
    if (params?.skip !== undefined) query.append('skip', String(params.skip));
    if (params?.limit !== undefined) query.append('limit', String(params.limit));
    return getJson<any[]>(`/api/v1/gold/risk/parameters?${query.toString()}`);
  },
  getRiskParameter: (parameterId: string) => 
    getJson<any>(`/api/v1/gold/risk/parameters/${parameterId}`),
  updateRiskParameter: (parameterId: string, payload: unknown) => 
    patchJson(`/api/v1/gold/risk/parameters/${parameterId}`, payload),
  deleteRiskParameter: (parameterId: string) => 
    deleteJson(`/api/v1/gold/risk/parameters/${parameterId}`),
  
  // Credit Risk Assessments
  createCreditRiskAssessment: (payload: unknown) => 
    postJson('/api/v1/gold/risk/credit-assessments', payload),
  listCreditRiskAssessments: (params?: { 
    loan_id?: string; 
    customer_id?: string; 
    assessment_type?: string; 
    risk_category?: string; 
    approval_status?: string;
    date_from?: string;
    date_to?: string;
    skip?: number; 
    limit?: number;
  }) => {
    const query = new URLSearchParams();
    if (params?.loan_id) query.append('loan_id', params.loan_id);
    if (params?.customer_id) query.append('customer_id', params.customer_id);
    if (params?.assessment_type) query.append('assessment_type', params.assessment_type);
    if (params?.risk_category) query.append('risk_category', params.risk_category);
    if (params?.approval_status) query.append('approval_status', params.approval_status);
    if (params?.date_from) query.append('date_from', params.date_from);
    if (params?.date_to) query.append('date_to', params.date_to);
    if (params?.skip !== undefined) query.append('skip', String(params.skip));
    if (params?.limit !== undefined) query.append('limit', String(params.limit));
    return getJson<any[]>(`/api/v1/gold/risk/credit-assessments?${query.toString()}`);
  },
  getCreditRiskAssessment: (assessmentId: string) => 
    getJson<any>(`/api/v1/gold/risk/credit-assessments/${assessmentId}`),
  updateCreditRiskAssessment: (assessmentId: string, payload: unknown) => 
    patchJson(`/api/v1/gold/risk/credit-assessments/${assessmentId}`, payload),
  approveCreditRiskAssessment: (assessmentId: string, payload: unknown) => 
    postJson(`/api/v1/gold/risk/credit-assessments/${assessmentId}/approve`, payload),
  deleteCreditRiskAssessment: (assessmentId: string) => 
    deleteJson(`/api/v1/gold/risk/credit-assessments/${assessmentId}`),

  // Operational Risk Events
  createOperationalRiskEvent: (payload: unknown) => 
    postJson('/api/v1/gold/risk/operational-events', payload),
  listOperationalRiskEvents: (params?: { 
    event_category?: string; 
    severity_level?: string; 
    event_status?: string;
    date_from?: string;
    date_to?: string;
    skip?: number; 
    limit?: number;
  }) => {
    const query = new URLSearchParams();
    if (params?.event_category) query.append('event_category', params.event_category);
    if (params?.severity_level) query.append('severity_level', params.severity_level);
    if (params?.event_status) query.append('event_status', params.event_status);
    if (params?.date_from) query.append('date_from', params.date_from);
    if (params?.date_to) query.append('date_to', params.date_to);
    if (params?.skip !== undefined) query.append('skip', String(params.skip));
    if (params?.limit !== undefined) query.append('limit', String(params.limit));
    return getJson<any[]>(`/api/v1/gold/risk/operational-events?${query.toString()}`);
  },
  getOperationalRiskEvent: (eventId: string) => 
    getJson<any>(`/api/v1/gold/risk/operational-events/${eventId}`),
  updateOperationalRiskEvent: (eventId: string, payload: unknown) => 
    patchJson(`/api/v1/gold/risk/operational-events/${eventId}`, payload),
  deleteOperationalRiskEvent: (eventId: string) => 
    deleteJson(`/api/v1/gold/risk/operational-events/${eventId}`),
  
  // Market Risk Exposures
  createMarketRiskExposure: (payload: unknown) => 
    postJson('/api/v1/gold/risk/market-exposures', payload),
  listMarketRiskExposures: (params?: { 
    exposure_type?: string; 
    currency?: string;
    date_from?: string;
    date_to?: string;
    skip?: number; 
    limit?: number;
  }) => {
    const query = new URLSearchParams();
    if (params?.exposure_type) query.append('exposure_type', params.exposure_type);
    if (params?.currency) query.append('currency', params.currency);
    if (params?.date_from) query.append('date_from', params.date_from);
    if (params?.date_to) query.append('date_to', params.date_to);
    if (params?.skip !== undefined) query.append('skip', String(params.skip));
    if (params?.limit !== undefined) query.append('limit', String(params.limit));
    return getJson<any[]>(`/api/v1/gold/risk/market-exposures?${query.toString()}`);
  },
  getMarketRiskExposure: (exposureId: string) => 
    getJson<any>(`/api/v1/gold/risk/market-exposures/${exposureId}`),
  deleteMarketRiskExposure: (exposureId: string) => 
    deleteJson(`/api/v1/gold/risk/market-exposures/${exposureId}`),

  // Concentration Risk Limits
  createConcentrationRiskLimit: (payload: unknown) => 
    postJson('/api/v1/gold/risk/concentration-limits', payload),
  listConcentrationRiskLimits: (params?: { concentration_type?: string; is_active?: boolean; skip?: number; limit?: number }) => {
    const query = new URLSearchParams();
    if (params?.concentration_type) query.append('concentration_type', params.concentration_type);
    if (params?.is_active !== undefined) query.append('is_active', String(params.is_active));
    if (params?.skip !== undefined) query.append('skip', String(params.skip));
    if (params?.limit !== undefined) query.append('limit', String(params.limit));
    return getJson<any[]>(`/api/v1/gold/risk/concentration-limits?${query.toString()}`);
  },
  getConcentrationRiskLimit: (limitId: string) => 
    getJson<any>(`/api/v1/gold/risk/concentration-limits/${limitId}`),
  updateConcentrationRiskLimit: (limitId: string, payload: unknown) => 
    patchJson(`/api/v1/gold/risk/concentration-limits/${limitId}`, payload),
  monitorConcentrationRisks: () => 
    getJson<any[]>('/api/v1/gold/risk/concentration-limits/monitor'),
  deleteConcentrationRiskLimit: (limitId: string) => 
    deleteJson(`/api/v1/gold/risk/concentration-limits/${limitId}`),
  
  // Risk Alerts
  createRiskAlert: (payload: unknown) => 
    postJson('/api/v1/gold/risk/alerts', payload),
  listRiskAlerts: (params?: { 
    alert_type?: string; 
    risk_category?: string; 
    severity_level?: string; 
    alert_status?: string;
    date_from?: string;
    date_to?: string;
    skip?: number; 
    limit?: number;
  }) => {
    const query = new URLSearchParams();
    if (params?.alert_type) query.append('alert_type', params.alert_type);
    if (params?.risk_category) query.append('risk_category', params.risk_category);
    if (params?.severity_level) query.append('severity_level', params.severity_level);
    if (params?.alert_status) query.append('alert_status', params.alert_status);
    if (params?.date_from) query.append('date_from', params.date_from);
    if (params?.date_to) query.append('date_to', params.date_to);
    if (params?.skip !== undefined) query.append('skip', String(params.skip));
    if (params?.limit !== undefined) query.append('limit', String(params.limit));
    return getJson<any[]>(`/api/v1/gold/risk/alerts?${query.toString()}`);
  },
  getRiskAlert: (alertId: string) => 
    getJson<any>(`/api/v1/gold/risk/alerts/${alertId}`),
  updateRiskAlert: (alertId: string, payload: unknown) => 
    patchJson(`/api/v1/gold/risk/alerts/${alertId}`, payload),
  resolveRiskAlert: (alertId: string, payload: unknown) => 
    postJson(`/api/v1/gold/risk/alerts/${alertId}/resolve`, payload),
  deleteRiskAlert: (alertId: string) => 
    deleteJson(`/api/v1/gold/risk/alerts/${alertId}`),

  // Risk Mitigations
  createRiskMitigation: (payload: unknown) => 
    postJson('/api/v1/gold/risk/mitigations', payload),
  listRiskMitigations: (params?: { 
    risk_category?: string; 
    mitigation_type?: string; 
    mitigation_status?: string; 
    approval_status?: string;
    skip?: number; 
    limit?: number;
  }) => {
    const query = new URLSearchParams();
    if (params?.risk_category) query.append('risk_category', params.risk_category);
    if (params?.mitigation_type) query.append('mitigation_type', params.mitigation_type);
    if (params?.mitigation_status) query.append('mitigation_status', params.mitigation_status);
    if (params?.approval_status) query.append('approval_status', params.approval_status);
    if (params?.skip !== undefined) query.append('skip', String(params.skip));
    if (params?.limit !== undefined) query.append('limit', String(params.limit));
    return getJson<any[]>(`/api/v1/gold/risk/mitigations?${query.toString()}`);
  },
  getRiskMitigation: (mitigationId: string) => 
    getJson<any>(`/api/v1/gold/risk/mitigations/${mitigationId}`),
  updateRiskMitigation: (mitigationId: string, payload: unknown) => 
    patchJson(`/api/v1/gold/risk/mitigations/${mitigationId}`, payload),
  approveRiskMitigation: (mitigationId: string, payload: unknown) => 
    postJson(`/api/v1/gold/risk/mitigations/${mitigationId}/approve`, payload),
  deleteRiskMitigation: (mitigationId: string) => 
    deleteJson(`/api/v1/gold/risk/mitigations/${mitigationId}`),
  
  // Risk Reports
  createRiskReport: (payload: unknown) => 
    postJson('/api/v1/gold/risk/reports', payload),
  listRiskReports: (params?: { 
    report_type?: string; 
    report_category?: string; 
    report_status?: string; 
    approval_status?: string;
    date_from?: string;
    date_to?: string;
    skip?: number; 
    limit?: number;
  }) => {
    const query = new URLSearchParams();
    if (params?.report_type) query.append('report_type', params.report_type);
    if (params?.report_category) query.append('report_category', params.report_category);
    if (params?.report_status) query.append('report_status', params.report_status);
    if (params?.approval_status) query.append('approval_status', params.approval_status);
    if (params?.date_from) query.append('date_from', params.date_from);
    if (params?.date_to) query.append('date_to', params.date_to);
    if (params?.skip !== undefined) query.append('skip', String(params.skip));
    if (params?.limit !== undefined) query.append('limit', String(params.limit));
    return getJson<any[]>(`/api/v1/gold/risk/reports?${query.toString()}`);
  },
  getRiskReport: (reportId: string) => 
    getJson<any>(`/api/v1/gold/risk/reports/${reportId}`),
  updateRiskReport: (reportId: string, payload: unknown) => 
    patchJson(`/api/v1/gold/risk/reports/${reportId}`, payload),
  approveRiskReport: (reportId: string, payload: unknown) => 
    postJson(`/api/v1/gold/risk/reports/${reportId}/approve`, payload),
  publishRiskReport: (reportId: string, payload: unknown) => 
    postJson(`/api/v1/gold/risk/reports/${reportId}/publish`, payload),
  deleteRiskReport: (reportId: string) => 
    deleteJson(`/api/v1/gold/risk/reports/${reportId}`),

  // Risk Dashboards
  createRiskDashboard: (payload: unknown) => 
    postJson('/api/v1/gold/risk/dashboards', payload),
  listRiskDashboards: (params?: { dashboard_type?: string; is_active?: boolean; skip?: number; limit?: number }) => {
    const query = new URLSearchParams();
    if (params?.dashboard_type) query.append('dashboard_type', params.dashboard_type);
    if (params?.is_active !== undefined) query.append('is_active', String(params.is_active));
    if (params?.skip !== undefined) query.append('skip', String(params.skip));
    if (params?.limit !== undefined) query.append('limit', String(params.limit));
    return getJson<any[]>(`/api/v1/gold/risk/dashboards?${query.toString()}`);
  },
  getRiskDashboard: (dashboardId: string) => 
    getJson<any>(`/api/v1/gold/risk/dashboards/${dashboardId}`),
  updateRiskDashboard: (dashboardId: string, payload: unknown) => 
    patchJson(`/api/v1/gold/risk/dashboards/${dashboardId}`, payload),
  deleteRiskDashboard: (dashboardId: string) => 
    deleteJson(`/api/v1/gold/risk/dashboards/${dashboardId}`),
  
  // Compliance Checks
  createComplianceCheck: (payload: unknown) => 
    postJson('/api/v1/gold/risk/compliance-checks', payload),
  listComplianceChecks: (params?: { 
    check_type?: string; 
    compliance_area?: string; 
    check_status?: string; 
    compliance_status?: string; 
    review_status?: string;
    date_from?: string;
    date_to?: string;
    skip?: number; 
    limit?: number;
  }) => {
    const query = new URLSearchParams();
    if (params?.check_type) query.append('check_type', params.check_type);
    if (params?.compliance_area) query.append('compliance_area', params.compliance_area);
    if (params?.check_status) query.append('check_status', params.check_status);
    if (params?.compliance_status) query.append('compliance_status', params.compliance_status);
    if (params?.review_status) query.append('review_status', params.review_status);
    if (params?.date_from) query.append('date_from', params.date_from);
    if (params?.date_to) query.append('date_to', params.date_to);
    if (params?.skip !== undefined) query.append('skip', String(params.skip));
    if (params?.limit !== undefined) query.append('limit', String(params.limit));
    return getJson<any[]>(`/api/v1/gold/risk/compliance-checks?${query.toString()}`);
  },
  getComplianceCheck: (checkId: string) => 
    getJson<any>(`/api/v1/gold/risk/compliance-checks/${checkId}`),
  updateComplianceCheck: (checkId: string, payload: unknown) => 
    patchJson(`/api/v1/gold/risk/compliance-checks/${checkId}`, payload),
  reviewComplianceCheck: (checkId: string, payload: unknown) => 
    postJson(`/api/v1/gold/risk/compliance-checks/${checkId}/review`, payload),
  approveComplianceCheck: (checkId: string, payload: unknown) => 
    postJson(`/api/v1/gold/risk/compliance-checks/${checkId}/approve`, payload),
  deleteComplianceCheck: (checkId: string) => 
    deleteJson(`/api/v1/gold/risk/compliance-checks/${checkId}`),
  
  // Risk Statistics
  getCreditRiskStatistics: (params?: { date_from?: string; date_to?: string }) => {
    const query = new URLSearchParams();
    if (params?.date_from) query.append('date_from', params.date_from);
    if (params?.date_to) query.append('date_to', params.date_to);
    return getJson<any>(`/api/v1/gold/risk/statistics/credit-risk?${query.toString()}`);
  },
  getOperationalRiskStatistics: (params?: { date_from?: string; date_to?: string }) => {
    const query = new URLSearchParams();
    if (params?.date_from) query.append('date_from', params.date_from);
    if (params?.date_to) query.append('date_to', params.date_to);
    return getJson<any>(`/api/v1/gold/risk/statistics/operational-risk?${query.toString()}`);
  },
  getMarketRiskStatistics: (params?: { date_from?: string; date_to?: string }) => {
    const query = new URLSearchParams();
    if (params?.date_from) query.append('date_from', params.date_from);
    if (params?.date_to) query.append('date_to', params.date_to);
    return getJson<any>(`/api/v1/gold/risk/statistics/market-risk?${query.toString()}`);
  },
  getConcentrationRiskStatistics: () => 
    getJson<any>('/api/v1/gold/risk/statistics/concentration-risk'),
  getComplianceStatistics: (params?: { date_from?: string; date_to?: string }) => {
    const query = new URLSearchParams();
    if (params?.date_from) query.append('date_from', params.date_from);
    if (params?.date_to) query.append('date_to', params.date_to);
    return getJson<any>(`/api/v1/gold/risk/statistics/compliance?${query.toString()}`);
  },

};
