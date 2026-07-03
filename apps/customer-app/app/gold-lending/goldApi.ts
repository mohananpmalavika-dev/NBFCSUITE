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
};
