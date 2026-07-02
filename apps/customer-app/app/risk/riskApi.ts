export const RISK_API_BASE = process.env.NEXT_PUBLIC_RISK_API_URL ?? 'http://localhost:8009';
export const DEFAULT_RISK_TENANT = process.env.NEXT_PUBLIC_RISK_TENANT_ID ?? 'tenant-local-accounting';

export function riskApiUrl(path: string) {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  return `${RISK_API_BASE}${normalizedPath}`;
}

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(riskApiUrl(path));
  if (!response.ok) {
    throw new Error(`Risk API request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

async function postJson<T>(path: string, payload: unknown): Promise<T> {
  const response = await fetch(riskApiUrl(path), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error(`Risk API request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export interface RiskDashboardResponse {
  tenant_id: string;
  open_risks: number;
  high_risks: number;
  critical_risks: number;
  incidents: number;
  loss_events: number;
  controls_under_test: number;
  risk_score: number;
  compliance_issues: number;
  status: string;
}

export interface RiskCreatePayload {
  tenant_id: string;
  risk_name: string;
  category?: string;
  business_owner?: string;
  risk_owner?: string;
  likelihood?: string;
  impact?: string;
  treatment?: string;
  review_date?: string;
  metadata?: Record<string, unknown>;
}

export interface RiskResponse extends RiskCreatePayload {
  id: string;
  inherent_risk?: string;
  residual_risk?: string;
  status: string;
  created_at: string;
}

export interface RiskAssessmentPayload {
  tenant_id: string;
  risk_id: string;
  assessed_by?: string;
  likelihood?: number;
  impact?: number;
  velocity?: number;
  detectability?: number;
  findings?: string;
  metadata?: Record<string, unknown>;
}

export interface RiskAssessmentResponse extends RiskAssessmentPayload {
  id: string;
  score?: number;
  status: string;
  assessed_at: string;
}

export interface IncidentPayload {
  tenant_id: string;
  incident_type: string;
  reported_by?: string;
  branch_id?: string;
  severity?: string;
  description?: string;
  loss_amount?: number;
  metadata?: Record<string, unknown>;
}

export interface IncidentResponse extends IncidentPayload {
  id: string;
  status: string;
  occurred_at: string;
}

export interface KriPayload {
  tenant_id: string;
  name: string;
  category?: string;
  threshold?: number;
  current_value?: number;
  metadata?: Record<string, unknown>;
}

export interface KriResponse extends KriPayload {
  id: string;
  status: string;
  last_updated: string;
}

export const riskApi = {
  getRiskDashboard: (tenantId = DEFAULT_RISK_TENANT) =>
    getJson<RiskDashboardResponse>(`/api/v1/risk/dashboard?tenant_id=${encodeURIComponent(tenantId)}`),
  listRiskRegister: (tenantId = DEFAULT_RISK_TENANT) =>
    getJson<{ tenant_id: string; items: RiskResponse[] }>(`/api/v1/risk/register?tenant_id=${encodeURIComponent(tenantId)}`),
  createRiskRegisterEntry: (payload: RiskCreatePayload) => postJson<RiskResponse>('/api/v1/risk/register', payload),
  createRiskAssessment: (payload: RiskAssessmentPayload) => postJson<RiskAssessmentResponse>('/api/v1/risk/assessment', payload),
  listKri: (tenantId = DEFAULT_RISK_TENANT) => getJson<{ tenant_id: string; items: KriResponse[] }>(`/api/v1/risk/kri?tenant_id=${encodeURIComponent(tenantId)}`),
  reportIncident: (payload: IncidentPayload) => postJson<IncidentResponse>('/api/v1/risk/incident', payload),
  createRcsa: (payload: RiskAssessmentPayload) => postJson<RiskAssessmentResponse>('/api/v1/risk/rcsa', payload),
  getHeatmap: (tenantId = DEFAULT_RISK_TENANT) => getJson<{ tenant_id: string; heatmap: Array<{ category: string; likelihood: number; impact: number }> }>(`/api/v1/risk/heatmap?tenant_id=${encodeURIComponent(tenantId)}`),
  getReports: (tenantId = DEFAULT_RISK_TENANT) => getJson<{ tenant_id: string; reports: Array<{ report_type: string; status: string }> }>(`/api/v1/risk/reports?tenant_id=${encodeURIComponent(tenantId)}`),
};
