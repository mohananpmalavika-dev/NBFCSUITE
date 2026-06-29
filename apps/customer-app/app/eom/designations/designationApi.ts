import { eomApiUrl } from '../eomApi';

export interface Designation {
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

export async function listDesignations() {
  const res = await fetch(eomApiUrl('/eom/designations'));
  if (!res.ok) throw new Error('Failed to load designations');
  return res.json();
}

export async function createDesignation(payload: Partial<Designation>) {
  const res = await fetch(eomApiUrl('/eom/designations'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!res.ok) throw new Error('Failed to create designation');
  return res.json();
}

