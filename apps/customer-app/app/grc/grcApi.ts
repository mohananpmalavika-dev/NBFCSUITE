export const GRC_API_BASE = process.env.NEXT_PUBLIC_GRC_API_URL ?? 'http://localhost:8020';
export const DEFAULT_GRC_TENANT = process.env.NEXT_PUBLIC_GRC_TENANT_ID ?? 'tenant-local-accounting';

export function grcApiUrl(path: string) {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  return `${GRC_API_BASE}${normalizedPath}`;
}

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(grcApiUrl(path));
  if (!response.ok) {
    throw new Error(`GRC API request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

async function postJson<T>(path: string, payload: unknown): Promise<T> {
  const response = await fetch(grcApiUrl(path), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error(`GRC API request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export interface GrcDashboardResponse {
  tenant_id: string;
  active_policies: number;
  obligations_due: number;
  open_audits: number;
  open_issues: number;
  corrective_actions: number;
  compliance_score: number;
  status: string;
}

export interface PolicyCreatePayload {
  tenant_id: string;
  policy_number: string;
  title: string;
  owner?: string;
  version?: string;
  effective_date?: string;
  review_date?: string;
  status?: string;
  metadata?: Record<string, unknown>;
}

export interface PolicyResponse extends PolicyCreatePayload {
  id: string;
  created_at: string;
}

export interface IssueCreatePayload {
  tenant_id: string;
  title: string;
  owner?: string;
  severity?: string;
  description?: string;
  metadata?: Record<string, unknown>;
}

export interface IssueResponse extends IssueCreatePayload {
  id: string;
  status: string;
  created_at: string;
}

export const grcApi = {
  getDashboard: (tenantId = DEFAULT_GRC_TENANT) =>
    getJson<GrcDashboardResponse>(`/api/v1/grc/dashboard?tenant_id=${encodeURIComponent(tenantId)}`),
  listPolicies: (tenantId = DEFAULT_GRC_TENANT) =>
    getJson<PolicyResponse[]>(`/api/v1/grc/policies?tenant_id=${encodeURIComponent(tenantId)}`),
  createPolicy: (payload: PolicyCreatePayload) => postJson<PolicyResponse>('/api/v1/grc/policies', payload),
  listObligations: (tenantId = DEFAULT_GRC_TENANT) =>
    getJson<any[]>(`/api/v1/grc/obligations?tenant_id=${encodeURIComponent(tenantId)}`),
  createAssessment: (payload: { tenant_id: string; assessment_type: string; title?: string; owner?: string; findings?: string; metadata?: Record<string, unknown> }) =>
    postJson('/api/v1/grc/assessments', payload),
  createAudit: (payload: { tenant_id: string; audit_type: string; title?: string; owner?: string; findings?: string; metadata?: Record<string, unknown> }) =>
    postJson('/api/v1/grc/audits', payload),
  createIssue: (payload: IssueCreatePayload) => postJson<IssueResponse>('/api/v1/grc/issues', payload),
  createCorrectiveAction: (payload: { tenant_id: string; issue_id?: string; owner?: string; action_plan?: string; status?: string; metadata?: Record<string, unknown> }) =>
    postJson('/api/v1/grc/corrective-actions', payload),
  listRegulations: (tenantId = DEFAULT_GRC_TENANT) =>
    getJson<any[]>(`/api/v1/grc/regulations?tenant_id=${encodeURIComponent(tenantId)}`),
  getReports: (tenantId = DEFAULT_GRC_TENANT) =>
    getJson<{ tenant_id: string; reports: Array<{ report_type: string; status: string }> }>(`/api/v1/grc/reports?tenant_id=${encodeURIComponent(tenantId)}`),
};
