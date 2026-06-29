import { eomApiUrl } from '../../../eomApi';

export interface DesignationProfile {
  id: string;
  code: string;
  name: string;
  short_name?: string | null;
  job_family_id?: string | null;
  grade_id?: string | null;
  department_id?: string | null;
  reports_to_designation_id?: string | null;
  status: string;
  description?: string | null;
}

export interface DesignationHealth {
  score: number;
  rating?: string | null;
  status?: string | null;
  vacancies: number;
  training_compliance_pct?: number | null;
  competency_gap_pct?: number | null;
  recruitment_time_days?: number | null;
  performance_score_pct?: number | null;
  succession_readiness_pct?: number | null;
  issues: string[];
}

export async function getDesignation(id: string) {
  const res = await fetch(eomApiUrl(`/eom/designations/${id}`));
  if (!res.ok) throw new Error('Failed to load designation');
  return res.json();
}

export async function getDesignationHealth(id: string) {
  const res = await fetch(eomApiUrl(`/eom/designations/${id}/health`));
  if (!res.ok) throw new Error('Failed to load designation health');
  return res.json() as Promise<DesignationHealth>;
}

export async function getDesignationCompetencies(id: string) {
  const res = await fetch(eomApiUrl(`/eom/designations/${id}/competencies`));
  if (!res.ok) throw new Error('Failed to load competencies');
  return res.json();
}

export async function getDesignationCareer(id: string) {
  const res = await fetch(eomApiUrl(`/eom/designations/${id}/career`));
  if (!res.ok) throw new Error('Failed to load career');
  return res.json();
}

