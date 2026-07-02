export const PLATFORM_API_BASE = process.env.NEXT_PUBLIC_PLATFORM_API_URL ?? 'http://localhost:8018';
export const DEFAULT_PLATFORM_TENANT = process.env.NEXT_PUBLIC_PLATFORM_TENANT_ID ?? 'tenant-local-accounting';

export function platformApiUrl(path: string) {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  return `${PLATFORM_API_BASE}${normalizedPath}`;
}

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(platformApiUrl(path));
  if (!response.ok) {
    throw new Error(`Platform API request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export interface EdpDashboardResponse {
  tenant_id: string;
  data_assets: number;
  data_domains: number;
  lineage_edges: number;
  quality_checks: number;
  glossary_terms: number;
  health_score: number;
  status: string;
}

export interface EdpReportItem {
  report_type: string;
  status: string;
  last_generated: string;
}

export interface EdpReportsResponse {
  tenant_id: string;
  reports: EdpReportItem[];
}

export interface DataAssetItem {
  id: string;
  tenant_id: string;
  asset_code: string;
  asset_name: string;
  asset_type?: string;
  domain_code?: string;
  owner?: string;
  status: string;
  description?: string;
  metadata?: Record<string, unknown>;
  created_at: string;
}

export interface DataDomainItem {
  id: string;
  tenant_id: string;
  domain_code: string;
  domain_name: string;
  description?: string;
  status: string;
  metadata?: Record<string, unknown>;
  created_at: string;
}

export interface DataQualityItem {
  id: string;
  tenant_id: string;
  check_name: string;
  data_asset_id: string;
  status: string;
  score: number;
  last_run_at: string;
  metadata?: Record<string, unknown>;
  created_at: string;
}

export interface LineageItem {
  id: string;
  tenant_id: string;
  source_asset_id: string;
  target_asset_id: string;
  relationship?: string;
  metadata?: Record<string, unknown>;
  created_at: string;
}

export interface GlossaryTermItem {
  id: string;
  tenant_id: string;
  term: string;
  definition?: string;
  domain?: string;
  synonyms?: string[];
  metadata?: Record<string, unknown>;
  created_at: string;
}

export const platformApi = {
  getDashboard: (tenantId = DEFAULT_PLATFORM_TENANT) =>
    getJson<EdpDashboardResponse>(`/api/v1/edp/dashboard?tenant_id=${encodeURIComponent(tenantId)}`),
  getReports: (tenantId = DEFAULT_PLATFORM_TENANT) =>
    getJson<EdpReportsResponse>(`/api/v1/edp/reports?tenant_id=${encodeURIComponent(tenantId)}`),
  listDataAssets: (tenantId = DEFAULT_PLATFORM_TENANT) =>
    getJson<DataAssetItem[]>(`/api/v1/edp/data-assets?tenant_id=${encodeURIComponent(tenantId)}`),
  listDataDomains: (tenantId = DEFAULT_PLATFORM_TENANT) =>
    getJson<DataDomainItem[]>(`/api/v1/edp/data-domains?tenant_id=${encodeURIComponent(tenantId)}`),
  listLineage: (tenantId = DEFAULT_PLATFORM_TENANT) =>
    getJson<LineageItem[]>(`/api/v1/edp/lineage?tenant_id=${encodeURIComponent(tenantId)}`),
  listQualityChecks: (tenantId = DEFAULT_PLATFORM_TENANT) =>
    getJson<DataQualityItem[]>(`/api/v1/edp/quality-checks?tenant_id=${encodeURIComponent(tenantId)}`),
  listGlossary: (tenantId = DEFAULT_PLATFORM_TENANT) =>
    getJson<GlossaryTermItem[]>(`/api/v1/edp/glossary?tenant_id=${encodeURIComponent(tenantId)}`),
};
