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
