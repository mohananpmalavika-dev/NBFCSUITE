// Phase 12: Audit & Compliance API Methods
// To be appended to goldApi.ts

  // ============================================================================
  // AUDIT & COMPLIANCE - Phase 12
  // ============================================================================
  
  // Audit Trail
  createAuditTrail: (payload: unknown) => 
    postJson('/api/v1/gold/audit-compliance/audit-trails', payload),
  listAuditTrails: (params?: {
    event_type?: string;
    event_category?: string;
    entity_type?: string;
    entity_id?: string;
    user_id?: string;
    action_status?: string;
    date_from?: string;
    date_to?: string;
    security_flag?: boolean;
    compliance_flag?: boolean;
    fraud_flag?: boolean;
    skip?: number;
    limit?: number;
  }) => {
    const query = new URLSearchParams();
    if (params?.event_type) query.append('event_type', params.event_type);
    if (params?.event_category) query.append('event_category', params.event_category);
    if (params?.entity_type) query.append('entity_type', params.entity_type);
    if (params?.entity_id) query.append('entity_id', params.entity_id);
    if (params?.user_id) query.append('user_id', params.user_id);
    if (params?.action_status) query.append('action_status', params.action_status);
    if (params?.date_from) query.append('date_from', params.date_from);
    if (params?.date_to) query.append('date_to', params.date_to);
    if (params?.security_flag !== undefined) query.append('security_flag', String(params.security_flag));
    if (params?.compliance_flag !== undefined) query.append('compliance_flag', String(params.compliance_flag));
    if (params?.fraud_flag !== undefined) query.append('fraud_flag', String(params.fraud_flag));
    if (params?.skip !== undefined) query.append('skip', String(params.skip));
    if (params?.limit !== undefined) query.append('limit', String(params.limit));
    return getJson<any[]>(`/api/v1/gold/audit-compliance/audit-trails?${query.toString()}`);
  },
  getAuditTrail: (auditId: string) => 
    getJson<any>(`/api/v1/gold/audit-compliance/audit-trails/${auditId}`),
  getEntityAuditTrail: (entityType: string, entityId: string, skip?: number, limit?: number) => {
    const query = new URLSearchParams();
    if (skip !== undefined) query.append('skip', String(skip));
    if (limit !== undefined) query.append('limit', String(limit));
    return getJson<any[]>(`/api/v1/gold/audit-compliance/audit-trails/entity/${entityType}/${entityId}?${query.toString()}`);
  },
  archiveAuditTrail: (auditId: string) => 
    postJson(`/api/v1/gold/audit-compliance/audit-trails/${auditId}/archive`, {}),

  // Compliance Rules
  createComplianceRule: (payload: unknown) => 
    postJson('/api/v1/gold/audit-compliance/compliance-rules', payload),
  listComplianceRules: (params?: {
    rule_category?: string;
    rule_type?: string;
    severity_level?: string;
    is_active?: boolean;
    skip?: number;
    limit?: number;
  }) => {
    const query = new URLSearchParams();
    if (params?.rule_category) query.append('rule_category', params.rule_category);
    if (params?.rule_type) query.append('rule_type', params.rule_type);
    if (params?.severity_level) query.append('severity_level', params.severity_level);
    if (params?.is_active !== undefined) query.append('is_active', String(params.is_active));
    if (params?.skip !== undefined) query.append('skip', String(params.skip));
    if (params?.limit !== undefined) query.append('limit', String(params.limit));
    return getJson<any[]>(`/api/v1/gold/audit-compliance/compliance-rules?${query.toString()}`);
  },
  getComplianceRule: (ruleId: string) => 
    getJson<any>(`/api/v1/gold/audit-compliance/compliance-rules/${ruleId}`),
  updateComplianceRule: (ruleId: string, payload: unknown) => 
    patchJson(`/api/v1/gold/audit-compliance/compliance-rules/${ruleId}`, payload),
  deleteComplianceRule: (ruleId: string) => 
    deleteJson(`/api/v1/gold/audit-compliance/compliance-rules/${ruleId}`),

  // Compliance Violations
  createComplianceViolation: (payload: unknown) => 
    postJson('/api/v1/gold/audit-compliance/compliance-violations', payload),
  listComplianceViolations: (params?: {
    rule_id?: string;
    violation_type?: string;
    severity_level?: string;
    violation_status?: string;
    entity_type?: string;
    date_from?: string;
    date_to?: string;
    assigned_to?: string;
    requires_regulatory_reporting?: boolean;
    skip?: number;
    limit?: number;
  }) => {
    const query = new URLSearchParams();
    if (params?.rule_id) query.append('rule_id', params.rule_id);
    if (params?.violation_type) query.append('violation_type', params.violation_type);
    if (params?.severity_level) query.append('severity_level', params.severity_level);
    if (params?.violation_status) query.append('violation_status', params.violation_status);
    if (params?.entity_type) query.append('entity_type', params.entity_type);
    if (params?.date_from) query.append('date_from', params.date_from);
    if (params?.date_to) query.append('date_to', params.date_to);
    if (params?.assigned_to) query.append('assigned_to', params.assigned_to);
    if (params?.requires_regulatory_reporting !== undefined) query.append('requires_regulatory_reporting', String(params.requires_regulatory_reporting));
    if (params?.skip !== undefined) query.append('skip', String(params.skip));
    if (params?.limit !== undefined) query.append('limit', String(params.limit));
    return getJson<any[]>(`/api/v1/gold/audit-compliance/compliance-violations?${query.toString()}`);
  },
  getComplianceViolation: (violationId: string) => 
    getJson<any>(`/api/v1/gold/audit-compliance/compliance-violations/${violationId}`),
  updateComplianceViolation: (violationId: string, payload: unknown) => 
    patchJson(`/api/v1/gold/audit-compliance/compliance-violations/${violationId}`, payload),
  resolveComplianceViolation: (violationId: string, payload: unknown) => 
    postJson(`/api/v1/gold/audit-compliance/compliance-violations/${violationId}/resolve`, payload),
  deleteComplianceViolation: (violationId: string) => 
    deleteJson(`/api/v1/gold/audit-compliance/compliance-violations/${violationId}`),

  // Audit Schedules
  createAuditSchedule: (payload: unknown) => 
    postJson('/api/v1/gold/audit-compliance/audit-schedules', payload),
  listAuditSchedules: (params?: {
    audit_type?: string;
    audit_category?: string;
    schedule_status?: string;
    lead_auditor?: string;
    skip?: number;
    limit?: number;
  }) => {
    const query = new URLSearchParams();
    if (params?.audit_type) query.append('audit_type', params.audit_type);
    if (params?.audit_category) query.append('audit_category', params.audit_category);
    if (params?.schedule_status) query.append('schedule_status', params.schedule_status);
    if (params?.lead_auditor) query.append('lead_auditor', params.lead_auditor);
    if (params?.skip !== undefined) query.append('skip', String(params.skip));
    if (params?.limit !== undefined) query.append('limit', String(params.limit));
    return getJson<any[]>(`/api/v1/gold/audit-compliance/audit-schedules?${query.toString()}`);
  },
  getAuditSchedule: (scheduleId: string) => 
    getJson<any>(`/api/v1/gold/audit-compliance/audit-schedules/${scheduleId}`),
  updateAuditSchedule: (scheduleId: string, payload: unknown) => 
    patchJson(`/api/v1/gold/audit-compliance/audit-schedules/${scheduleId}`, payload),
  deleteAuditSchedule: (scheduleId: string) => 
    deleteJson(`/api/v1/gold/audit-compliance/audit-schedules/${scheduleId}`),

  // Audit Executions
  createAuditExecution: (payload: unknown) => 
    postJson('/api/v1/gold/audit-compliance/audit-executions', payload),
  listAuditExecutions: (params?: {
    schedule_id?: string;
    audit_type?: string;
    execution_status?: string;
    lead_auditor?: string;
    overall_rating?: string;
    date_from?: string;
    date_to?: string;
    skip?: number;
    limit?: number;
  }) => {
    const query = new URLSearchParams();
    if (params?.schedule_id) query.append('schedule_id', params.schedule_id);
    if (params?.audit_type) query.append('audit_type', params.audit_type);
    if (params?.execution_status) query.append('execution_status', params.execution_status);
    if (params?.lead_auditor) query.append('lead_auditor', params.lead_auditor);
    if (params?.overall_rating) query.append('overall_rating', params.overall_rating);
    if (params?.date_from) query.append('date_from', params.date_from);
    if (params?.date_to) query.append('date_to', params.date_to);
    if (params?.skip !== undefined) query.append('skip', String(params.skip));
    if (params?.limit !== undefined) query.append('limit', String(params.limit));
    return getJson<any[]>(`/api/v1/gold/audit-compliance/audit-executions?${query.toString()}`);
  },
  getAuditExecution: (executionId: string) => 
    getJson<any>(`/api/v1/gold/audit-compliance/audit-executions/${executionId}`),
  updateAuditExecution: (executionId: string, payload: unknown) => 
    patchJson(`/api/v1/gold/audit-compliance/audit-executions/${executionId}`, payload),
  approveAuditExecution: (executionId: string, payload: unknown) => 
    postJson(`/api/v1/gold/audit-compliance/audit-executions/${executionId}/approve`, payload),
  deleteAuditExecution: (executionId: string) => 
    deleteJson(`/api/v1/gold/audit-compliance/audit-executions/${executionId}`),

  // Audit Findings
  createAuditFinding: (payload: unknown) => 
    postJson('/api/v1/gold/audit-compliance/audit-findings', payload),
  listAuditFindings: (params?: {
    execution_id?: string;
    finding_type?: string;
    severity_level?: string;
    risk_level?: string;
    finding_status?: string;
    responsible_person?: string;
    is_repeat_finding?: boolean;
    skip?: number;
    limit?: number;
  }) => {
    const query = new URLSearchParams();
    if (params?.execution_id) query.append('execution_id', params.execution_id);
    if (params?.finding_type) query.append('finding_type', params.finding_type);
    if (params?.severity_level) query.append('severity_level', params.severity_level);
    if (params?.risk_level) query.append('risk_level', params.risk_level);
    if (params?.finding_status) query.append('finding_status', params.finding_status);
    if (params?.responsible_person) query.append('responsible_person', params.responsible_person);
    if (params?.is_repeat_finding !== undefined) query.append('is_repeat_finding', String(params.is_repeat_finding));
    if (params?.skip !== undefined) query.append('skip', String(params.skip));
    if (params?.limit !== undefined) query.append('limit', String(params.limit));
    return getJson<any[]>(`/api/v1/gold/audit-compliance/audit-findings?${query.toString()}`);
  },
  getAuditFinding: (findingId: string) => 
    getJson<any>(`/api/v1/gold/audit-compliance/audit-findings/${findingId}`),
  updateAuditFinding: (findingId: string, payload: unknown) => 
    patchJson(`/api/v1/gold/audit-compliance/audit-findings/${findingId}`, payload),
  verifyAuditFinding: (findingId: string, payload: unknown) => 
    postJson(`/api/v1/gold/audit-compliance/audit-findings/${findingId}/verify`, payload),
  deleteAuditFinding: (findingId: string) => 
    deleteJson(`/api/v1/gold/audit-compliance/audit-findings/${findingId}`),

  // Regulatory Reports
  createRegulatoryReport: (payload: unknown) => 
    postJson('/api/v1/gold/audit-compliance/regulatory-reports', payload),
  listRegulatoryReports: (params?: {
    report_type?: string;
    regulatory_body?: string;
    report_status?: string;
    is_overdue?: boolean;
    date_from?: string;
    date_to?: string;
    skip?: number;
    limit?: number;
  }) => {
    const query = new URLSearchParams();
    if (params?.report_type) query.append('report_type', params.report_type);
    if (params?.regulatory_body) query.append('regulatory_body', params.regulatory_body);
    if (params?.report_status) query.append('report_status', params.report_status);
    if (params?.is_overdue !== undefined) query.append('is_overdue', String(params.is_overdue));
    if (params?.date_from) query.append('date_from', params.date_from);
    if (params?.date_to) query.append('date_to', params.date_to);
    if (params?.skip !== undefined) query.append('skip', String(params.skip));
    if (params?.limit !== undefined) query.append('limit', String(params.limit));
    return getJson<any[]>(`/api/v1/gold/audit-compliance/regulatory-reports?${query.toString()}`);
  },
  getRegulatoryReport: (reportId: string) => 
    getJson<any>(`/api/v1/gold/audit-compliance/regulatory-reports/${reportId}`),
  updateRegulatoryReport: (reportId: string, payload: unknown) => 
    patchJson(`/api/v1/gold/audit-compliance/regulatory-reports/${reportId}`, payload),
  approveRegulatoryReport: (reportId: string, payload: unknown) => 
    postJson(`/api/v1/gold/audit-compliance/regulatory-reports/${reportId}/approve`, payload),
  submitRegulatoryReport: (reportId: string, payload: unknown) => 
    postJson(`/api/v1/gold/audit-compliance/regulatory-reports/${reportId}/submit`, payload),
  deleteRegulatoryReport: (reportId: string) => 
    deleteJson(`/api/v1/gold/audit-compliance/regulatory-reports/${reportId}`),

  // Compliance Certifications
  createComplianceCertification: (payload: unknown) => 
    postJson('/api/v1/gold/audit-compliance/compliance-certifications', payload),
  listComplianceCertifications: (params?: {
    certification_type?: string;
    certification_status?: string;
    issuing_body?: string;
    is_expired?: boolean;
    skip?: number;
    limit?: number;
  }) => {
    const query = new URLSearchParams();
    if (params?.certification_type) query.append('certification_type', params.certification_type);
    if (params?.certification_status) query.append('certification_status', params.certification_status);
    if (params?.issuing_body) query.append('issuing_body', params.issuing_body);
    if (params?.is_expired !== undefined) query.append('is_expired', String(params.is_expired));
    if (params?.skip !== undefined) query.append('skip', String(params.skip));
    if (params?.limit !== undefined) query.append('limit', String(params.limit));
    return getJson<any[]>(`/api/v1/gold/audit-compliance/compliance-certifications?${query.toString()}`);
  },
  getComplianceCertification: (certificationId: string) => 
    getJson<any>(`/api/v1/gold/audit-compliance/compliance-certifications/${certificationId}`),
  updateComplianceCertification: (certificationId: string, payload: unknown) => 
    patchJson(`/api/v1/gold/audit-compliance/compliance-certifications/${certificationId}`, payload),
  deleteComplianceCertification: (certificationId: string) => 
    deleteJson(`/api/v1/gold/audit-compliance/compliance-certifications/${certificationId}`),

  // Policy Acknowledgements
  createPolicyAcknowledgement: (payload: unknown) => 
    postJson('/api/v1/gold/audit-compliance/policy-acknowledgements', payload),
  listPolicyAcknowledgements: (params?: {
    policy_type?: string;
    acknowledgement_status?: string;
    user_id?: string;
    is_mandatory?: boolean;
    acknowledged?: boolean;
    skip?: number;
    limit?: number;
  }) => {
    const query = new URLSearchParams();
    if (params?.policy_type) query.append('policy_type', params.policy_type);
    if (params?.acknowledgement_status) query.append('acknowledgement_status', params.acknowledgement_status);
    if (params?.user_id) query.append('user_id', params.user_id);
    if (params?.is_mandatory !== undefined) query.append('is_mandatory', String(params.is_mandatory));
    if (params?.acknowledged !== undefined) query.append('acknowledged', String(params.acknowledged));
    if (params?.skip !== undefined) query.append('skip', String(params.skip));
    if (params?.limit !== undefined) query.append('limit', String(params.limit));
    return getJson<any[]>(`/api/v1/gold/audit-compliance/policy-acknowledgements?${query.toString()}`);
  },
  getPolicyAcknowledgement: (acknowledgementId: string) => 
    getJson<any>(`/api/v1/gold/audit-compliance/policy-acknowledgements/${acknowledgementId}`),
  updatePolicyAcknowledgement: (acknowledgementId: string, payload: unknown) => 
    patchJson(`/api/v1/gold/audit-compliance/policy-acknowledgements/${acknowledgementId}`, payload),

  // Data Retention Logs
  createDataRetentionLog: (payload: unknown) => 
    postJson('/api/v1/gold/audit-compliance/data-retention-logs', payload),
  listDataRetentionLogs: (params?: {
    data_category?: string;
    retention_action?: string;
    retention_status?: string;
    policy_code?: string;
    date_from?: string;
    date_to?: string;
    skip?: number;
    limit?: number;
  }) => {
    const query = new URLSearchParams();
    if (params?.data_category) query.append('data_category', params.data_category);
    if (params?.retention_action) query.append('retention_action', params.retention_action);
    if (params?.retention_status) query.append('retention_status', params.retention_status);
    if (params?.policy_code) query.append('policy_code', params.policy_code);
    if (params?.date_from) query.append('date_from', params.date_from);
    if (params?.date_to) query.append('date_to', params.date_to);
    if (params?.skip !== undefined) query.append('skip', String(params.skip));
    if (params?.limit !== undefined) query.append('limit', String(params.limit));
    return getJson<any[]>(`/api/v1/gold/audit-compliance/data-retention-logs?${query.toString()}`);
  },
  getDataRetentionLog: (logId: string) => 
    getJson<any>(`/api/v1/gold/audit-compliance/data-retention-logs/${logId}`),
  updateDataRetentionLog: (logId: string, payload: unknown) => 
    patchJson(`/api/v1/gold/audit-compliance/data-retention-logs/${logId}`, payload),
  approveDataRetentionLog: (logId: string, payload: unknown) => 
    postJson(`/api/v1/gold/audit-compliance/data-retention-logs/${logId}/approve`, payload),
  executeDataRetentionLog: (logId: string) => 
    postJson(`/api/v1/gold/audit-compliance/data-retention-logs/${logId}/execute`, {}),

  // Statistics
  getAuditTrailStatistics: (dateFrom?: string, dateTo?: string) => {
    const query = new URLSearchParams();
    if (dateFrom) query.append('date_from', dateFrom);
    if (dateTo) query.append('date_to', dateTo);
    return getJson<any>(`/api/v1/gold/audit-compliance/statistics/audit-trails?${query.toString()}`);
  },
  getComplianceStatistics: () => 
    getJson<any>('/api/v1/gold/audit-compliance/statistics/compliance'),
  getAuditExecutionStatistics: () => 
    getJson<any>('/api/v1/gold/audit-compliance/statistics/audit-executions'),
  getRegulatoryReportStatistics: () => 
    getJson<any>('/api/v1/gold/audit-compliance/statistics/regulatory-reports'),
