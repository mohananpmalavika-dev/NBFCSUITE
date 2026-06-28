'use client';

import { useAuth } from '@/lib/auth-context';
import { apiClient } from '@/lib/api';
import { useRouter } from 'next/navigation';
import { FormEvent, useEffect, useMemo, useState } from 'react';

interface OrganizationUnitNode {
  id: string;
  tenant_id: string;
  parent_id?: string | null;
  unit_code: string;
  unit_name: string;
  unit_type: string;
  display_order: number;
  status: string;
  manager_position_id?: string | null;
  cost_center_id?: string | null;
  profit_center_id?: string | null;
  created_at: string;
  updated_at: string;
  children?: OrganizationUnitNode[];
}

interface Analytics {
  total_units: number;
  active_units: number;
  inactive_units: number;
  by_type: Record<string, number>;
}

interface GradeItem {
  id: string;
  grade_code: string;
  grade_name: string;
  salary_band_min: number;
  salary_band_max: number;
  leave_entitlement_days: number;
  approval_limit: number;
  travel_class?: string;
  status: string;
}

interface DesignationItem {
  id: string;
  designation_code: string;
  designation_name: string;
  grade_id?: string | null;
  salary_band_min: number;
  salary_band_max: number;
  approval_limit: number;
  reporting_level: number;
  status: string;
}

interface PositionItem {
  id: string;
  position_code: string;
  position_title: string;
  department_id?: string | null;
  designation_id?: string | null;
  grade_id?: string | null;
  reports_to_position_id?: string | null;
  approval_limit: number;
  status: string;
}

interface DepartmentItem {
  id: string;
  department_code: string;
  department_name: string;
}

const unitTypes = [
  'COMPANY',
  'BUSINESS_UNIT',
  'DIVISION',
  'ZONE',
  'REGION',
  'AREA',
  'CLUSTER',
  'BRANCH',
  'DEPARTMENT',
  'SECTION',
  'TEAM',
];

export default function EnterpriseOrganizationPage() {
  const { user, token, isLoading } = useAuth();
  const router = useRouter();
  const [tree, setTree] = useState<OrganizationUnitNode[]>([]);
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [grades, setGrades] = useState<GradeItem[]>([]);
  const [designations, setDesignations] = useState<DesignationItem[]>([]);
  const [positions, setPositions] = useState<PositionItem[]>([]);
  const [departments, setDepartments] = useState<DepartmentItem[]>([]);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState('');
  const [form, setForm] = useState({
    parent_id: '',
    unit_code: '',
    unit_name: '',
    unit_type: 'BRANCH',
    display_order: '0',
    status: 'active',
    manager_position_id: '',
    cost_center_id: '',
    profit_center_id: '',
  });
  const [gradeForm, setGradeForm] = useState({
    grade_code: '',
    grade_name: '',
    salary_band_min: '0',
    salary_band_max: '0',
    leave_entitlement_days: '0',
    approval_limit: '0',
    travel_class: '',
  });
  const [designationForm, setDesignationForm] = useState({
    designation_code: '',
    designation_name: '',
    grade_id: '',
    salary_band_min: '0',
    salary_band_max: '0',
    approval_limit: '0',
    reporting_level: '0',
  });
  const [positionForm, setPositionForm] = useState({
    position_code: '',
    position_title: '',
    department_id: '',
    designation_id: '',
    grade_id: '',
    reports_to_position_id: '',
    approval_limit: '0',
  });

  useEffect(() => {
    if (!isLoading && !token) {
      router.push('/login');
    }
  }, [token, isLoading, router]);

  useEffect(() => {
    if (!token || !user) return;
    void loadData();
  }, [token, user]);

  const loadData = async () => {
    const tenantId = user?.tenant_id || 'default';
    setBusy(true);
    setMessage('');
    try {
      const [treeRes, analyticsRes, departmentRes, gradeRes, designationRes, positionRes] = await Promise.allSettled([
        apiClient.getOrganizationUnits({ tenant_id: tenantId }),
        apiClient.getOrganizationAnalytics({ tenant_id: tenantId }),
        apiClient.getHrmsDepartments({ tenant_id: tenantId, status: 'active' }),
        apiClient.getHrmsGrades({ tenant_id: tenantId, status: 'active' }),
        apiClient.getHrmsDesignations({ tenant_id: tenantId, status: 'active' }),
        apiClient.getHrmsPositions({ tenant_id: tenantId, status: 'active' }),
      ]);

      if (treeRes.status === 'fulfilled') {
        setTree(Array.isArray(treeRes.value?.data) ? treeRes.value.data : []);
      }
      if (analyticsRes.status === 'fulfilled') {
        setAnalytics(analyticsRes.value?.data || null);
      }
      if (departmentRes.status === 'fulfilled') {
        setDepartments(Array.isArray(departmentRes.value?.data) ? departmentRes.value.data : []);
      }
      if (gradeRes.status === 'fulfilled') {
        setGrades(Array.isArray(gradeRes.value?.data) ? gradeRes.value.data : []);
      }
      if (designationRes.status === 'fulfilled') {
        setDesignations(Array.isArray(designationRes.value?.data) ? designationRes.value.data : []);
      }
      if (positionRes.status === 'fulfilled') {
        setPositions(Array.isArray(positionRes.value?.data) ? positionRes.value.data : []);
      }
      if ([treeRes, analyticsRes, departmentRes, gradeRes, designationRes, positionRes].some((result) => result.status === 'rejected')) {
        setMessage('Some workforce or hierarchy data could not be refreshed.');
      }
    } catch {
      setMessage('Unable to load organization structure right now.');
    } finally {
      setBusy(false);
    }
  };

  const flattenedUnits = useMemo(() => {
    const items: Array<{ id: string; label: string }> = [];
    const walk = (nodes: OrganizationUnitNode[]) => {
      nodes.forEach((node) => {
        items.push({ id: node.id, label: `${node.unit_type} • ${node.unit_name} (${node.unit_code})` });
        if (node.children?.length) walk(node.children);
      });
    };
    walk(tree);
    return items;
  }, [tree]);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!token || !user) return;
    setBusy(true);
    setMessage('');
    try {
      await apiClient.createOrganizationUnit({
        tenant_id: user.tenant_id || 'default',
        parent_id: form.parent_id || undefined,
        unit_code: form.unit_code,
        unit_name: form.unit_name,
        unit_type: form.unit_type,
        display_order: Number(form.display_order || 0),
        status: form.status,
        manager_position_id: form.manager_position_id || undefined,
        cost_center_id: form.cost_center_id || undefined,
        profit_center_id: form.profit_center_id || undefined,
      });
      setForm({
        parent_id: '',
        unit_code: '',
        unit_name: '',
        unit_type: 'BRANCH',
        display_order: '0',
        status: 'active',
        manager_position_id: '',
        cost_center_id: '',
        profit_center_id: '',
      });
      await loadData();
      setMessage('Organization unit created successfully.');
    } catch {
      setMessage('The unit could not be created. Please check the values and try again.');
    } finally {
      setBusy(false);
    }
  };

  const handleGradeSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!token || !user) return;
    setBusy(true);
    setMessage('');
    try {
      await apiClient.createHrmsGrade({
        tenant_id: user.tenant_id || 'default',
        grade_code: gradeForm.grade_code,
        grade_name: gradeForm.grade_name,
        salary_band_min: Number(gradeForm.salary_band_min || 0),
        salary_band_max: Number(gradeForm.salary_band_max || 0),
        leave_entitlement_days: Number(gradeForm.leave_entitlement_days || 0),
        approval_limit: Number(gradeForm.approval_limit || 0),
        travel_class: gradeForm.travel_class || undefined,
      });
      setGradeForm({
        grade_code: '',
        grade_name: '',
        salary_band_min: '0',
        salary_band_max: '0',
        leave_entitlement_days: '0',
        approval_limit: '0',
        travel_class: '',
      });
      await loadData();
      setMessage('Grade created successfully.');
    } catch {
      setMessage('The grade could not be created.');
    } finally {
      setBusy(false);
    }
  };

  const handleDesignationSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!token || !user) return;
    setBusy(true);
    setMessage('');
    try {
      await apiClient.createHrmsDesignation({
        tenant_id: user.tenant_id || 'default',
        designation_code: designationForm.designation_code,
        designation_name: designationForm.designation_name,
        grade_id: designationForm.grade_id || undefined,
        salary_band_min: Number(designationForm.salary_band_min || 0),
        salary_band_max: Number(designationForm.salary_band_max || 0),
        approval_limit: Number(designationForm.approval_limit || 0),
        reporting_level: Number(designationForm.reporting_level || 0),
      });
      setDesignationForm({
        designation_code: '',
        designation_name: '',
        grade_id: '',
        salary_band_min: '0',
        salary_band_max: '0',
        approval_limit: '0',
        reporting_level: '0',
      });
      await loadData();
      setMessage('Designation created successfully.');
    } catch {
      setMessage('The designation could not be created.');
    } finally {
      setBusy(false);
    }
  };

  const handlePositionSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!token || !user) return;
    setBusy(true);
    setMessage('');
    try {
      await apiClient.createHrmsPosition({
        tenant_id: user.tenant_id || 'default',
        position_code: positionForm.position_code,
        position_title: positionForm.position_title,
        department_id: positionForm.department_id || undefined,
        designation_id: positionForm.designation_id || undefined,
        grade_id: positionForm.grade_id || undefined,
        reports_to_position_id: positionForm.reports_to_position_id || undefined,
        approval_limit: Number(positionForm.approval_limit || 0),
      });
      setPositionForm({
        position_code: '',
        position_title: '',
        department_id: '',
        designation_id: '',
        grade_id: '',
        reports_to_position_id: '',
        approval_limit: '0',
      });
      await loadData();
      setMessage('Position created successfully.');
    } catch {
      setMessage('The position could not be created.');
    } finally {
      setBusy(false);
    }
  };

  if (isLoading || !token) {
    return <div className="p-8 text-center text-slate-600">Loading enterprise setup...</div>;
  }

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-8">
      <div className="mx-auto max-w-7xl space-y-6">
        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <p className="text-sm font-semibold uppercase tracking-wide text-blue-700">Enterprise Setup</p>
              <h1 className="mt-2 text-3xl font-bold text-slate-950">Organization Platform</h1>
              <p className="mt-2 max-w-3xl text-sm text-slate-600">
                Create a scalable enterprise hierarchy with low manual input and instant visibility across company, branches, departments, and teams.
              </p>
            </div>
            <div className="rounded-lg border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-900">
              <p className="font-semibold">Ask AI</p>
              <p>“Create a new branch in Kerala”</p>
            </div>
          </div>
        </section>

        <section className="grid gap-4 md:grid-cols-3">
          <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
            <p className="text-sm text-slate-500">Total Units</p>
            <p className="mt-2 text-3xl font-semibold text-slate-950">{analytics?.total_units ?? 0}</p>
          </div>
          <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
            <p className="text-sm text-slate-500">Active Units</p>
            <p className="mt-2 text-3xl font-semibold text-emerald-600">{analytics?.active_units ?? 0}</p>
          </div>
          <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
            <p className="text-sm text-slate-500">Unit Types</p>
            <p className="mt-2 text-3xl font-semibold text-blue-600">{analytics ? Object.keys(analytics.by_type).length : 0}</p>
          </div>
        </section>

        <section className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-4 flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold text-slate-950">Organization Tree</h2>
                <p className="text-sm text-slate-500">Visualize the enterprise structure from company to branch and department.</p>
              </div>
            </div>
            {tree.length === 0 ? (
              <div className="rounded-lg border border-dashed border-slate-300 p-6 text-sm text-slate-500">
                No organization units yet. Create the first company or branch to begin.
              </div>
            ) : (
              <div className="space-y-2">
                {tree.map((node) => (
                  <TreeNode key={node.id} node={node} depth={0} />
                ))}
              </div>
            )}
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="text-xl font-semibold text-slate-950">Quick Create</h2>
            <p className="mt-1 text-sm text-slate-500">Capture the next unit with a compact, guided form.</p>
            <form className="mt-4 space-y-4" onSubmit={handleSubmit}>
              <div className="grid gap-4 sm:grid-cols-2">
                <label className="text-sm font-medium text-slate-700">
                  Unit Code
                  <input
                    required
                    value={form.unit_code}
                    onChange={(event) => setForm({ ...form, unit_code: event.target.value })}
                    className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
                    placeholder="HQ"
                  />
                </label>
                <label className="text-sm font-medium text-slate-700">
                  Unit Name
                  <input
                    required
                    value={form.unit_name}
                    onChange={(event) => setForm({ ...form, unit_name: event.target.value })}
                    className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
                    placeholder="Head Office"
                  />
                </label>
              </div>
              <div className="grid gap-4 sm:grid-cols-2">
                <label className="text-sm font-medium text-slate-700">
                  Unit Type
                  <select
                    value={form.unit_type}
                    onChange={(event) => setForm({ ...form, unit_type: event.target.value })}
                    className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
                  >
                    {unitTypes.map((type) => (
                      <option key={type} value={type}>
                        {type}
                      </option>
                    ))}
                  </select>
                </label>
                <label className="text-sm font-medium text-slate-700">
                  Parent Unit
                  <select
                    value={form.parent_id}
                    onChange={(event) => setForm({ ...form, parent_id: event.target.value })}
                    className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
                  >
                    <option value="">None</option>
                    {flattenedUnits.map((unit) => (
                      <option key={unit.id} value={unit.id}>
                        {unit.label}
                      </option>
                    ))}
                  </select>
                </label>
                <label className="text-sm font-medium text-slate-700">
                  Manager Position
                  <select
                    value={form.manager_position_id}
                    onChange={(event) => setForm({ ...form, manager_position_id: event.target.value })}
                    className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
                  >
                    <option value="">None</option>
                    {positions.map((position) => (
                      <option key={position.id} value={position.id}>
                        {position.position_title} ({position.position_code})
                      </option>
                    ))}
                  </select>
                </label>
              </div>
              <div className="grid gap-4 sm:grid-cols-2">
                <label className="text-sm font-medium text-slate-700">
                  Cost Center ID
                  <input
                    value={form.cost_center_id}
                    onChange={(event) => setForm({ ...form, cost_center_id: event.target.value })}
                    className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
                    placeholder="Cost center id"
                  />
                </label>
                <label className="text-sm font-medium text-slate-700">
                  Profit Center ID
                  <input
                    value={form.profit_center_id}
                    onChange={(event) => setForm({ ...form, profit_center_id: event.target.value })}
                    className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
                    placeholder="Profit center id"
                  />
                </label>
              </div>
              <div className="grid gap-4 sm:grid-cols-2">
                <label className="text-sm font-medium text-slate-700">
                  Display Order
                  <input
                    type="number"
                    value={form.display_order}
                    onChange={(event) => setForm({ ...form, display_order: event.target.value })}
                    className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
                  />
                </label>
                <label className="text-sm font-medium text-slate-700">
                  Status
                  <select
                    value={form.status}
                    onChange={(event) => setForm({ ...form, status: event.target.value })}
                    className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
                  >
                    <option value="active">Active</option>
                    <option value="inactive">Inactive</option>
                  </select>
                </label>
              </div>
              <button
                type="submit"
                disabled={busy}
                className="w-full rounded-md bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-blue-300"
              >
                {busy ? 'Creating...' : 'Create Organization Unit'}
              </button>
            </form>
            {message ? <p className="mt-3 text-sm text-slate-600">{message}</p> : null}
          </div>
        </section>

        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="flex flex-col gap-2 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <h2 className="text-xl font-semibold text-slate-950">Workforce Foundation</h2>
              <p className="text-sm text-slate-500">Capture grades, designations, and positions that connect directly to the organization tree.</p>
            </div>
            <div className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-600">
              {grades.length} grades • {designations.length} designations • {positions.length} positions
            </div>
          </div>

          <div className="mt-6 grid gap-6 xl:grid-cols-3">
            <div className="rounded-xl border border-slate-200 p-4">
              <h3 className="text-lg font-semibold text-slate-950">Create Grade</h3>
              <form className="mt-4 space-y-3" onSubmit={handleGradeSubmit}>
                <input required value={gradeForm.grade_code} onChange={(event) => setGradeForm({ ...gradeForm, grade_code: event.target.value })} placeholder="Grade code" className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm" />
                <input required value={gradeForm.grade_name} onChange={(event) => setGradeForm({ ...gradeForm, grade_name: event.target.value })} placeholder="Grade name" className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm" />
                <div className="grid gap-3 sm:grid-cols-2">
                  <input type="number" value={gradeForm.salary_band_min} onChange={(event) => setGradeForm({ ...gradeForm, salary_band_min: event.target.value })} placeholder="Min salary" className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm" />
                  <input type="number" value={gradeForm.salary_band_max} onChange={(event) => setGradeForm({ ...gradeForm, salary_band_max: event.target.value })} placeholder="Max salary" className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm" />
                </div>
                <div className="grid gap-3 sm:grid-cols-2">
                  <input type="number" value={gradeForm.leave_entitlement_days} onChange={(event) => setGradeForm({ ...gradeForm, leave_entitlement_days: event.target.value })} placeholder="Leave days" className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm" />
                  <input type="number" value={gradeForm.approval_limit} onChange={(event) => setGradeForm({ ...gradeForm, approval_limit: event.target.value })} placeholder="Approval limit" className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm" />
                </div>
                <input value={gradeForm.travel_class} onChange={(event) => setGradeForm({ ...gradeForm, travel_class: event.target.value })} placeholder="Travel class" className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm" />
                <button type="submit" disabled={busy} className="w-full rounded-md bg-slate-900 px-4 py-2 text-sm font-semibold text-white hover:bg-slate-700 disabled:cursor-not-allowed disabled:bg-slate-400">Save grade</button>
              </form>
            </div>

            <div className="rounded-xl border border-slate-200 p-4">
              <h3 className="text-lg font-semibold text-slate-950">Create Designation</h3>
              <form className="mt-4 space-y-3" onSubmit={handleDesignationSubmit}>
                <input required value={designationForm.designation_code} onChange={(event) => setDesignationForm({ ...designationForm, designation_code: event.target.value })} placeholder="Designation code" className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm" />
                <input required value={designationForm.designation_name} onChange={(event) => setDesignationForm({ ...designationForm, designation_name: event.target.value })} placeholder="Designation name" className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm" />
                <select value={designationForm.grade_id} onChange={(event) => setDesignationForm({ ...designationForm, grade_id: event.target.value })} className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm">
                  <option value="">Select grade</option>
                  {grades.map((grade) => (
                    <option key={grade.id} value={grade.id}>
                      {grade.grade_name}
                    </option>
                  ))}
                </select>
                <div className="grid gap-3 sm:grid-cols-2">
                  <input type="number" value={designationForm.salary_band_min} onChange={(event) => setDesignationForm({ ...designationForm, salary_band_min: event.target.value })} placeholder="Min salary" className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm" />
                  <input type="number" value={designationForm.salary_band_max} onChange={(event) => setDesignationForm({ ...designationForm, salary_band_max: event.target.value })} placeholder="Max salary" className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm" />
                </div>
                <div className="grid gap-3 sm:grid-cols-2">
                  <input type="number" value={designationForm.approval_limit} onChange={(event) => setDesignationForm({ ...designationForm, approval_limit: event.target.value })} placeholder="Approval limit" className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm" />
                  <input type="number" value={designationForm.reporting_level} onChange={(event) => setDesignationForm({ ...designationForm, reporting_level: event.target.value })} placeholder="Reporting level" className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm" />
                </div>
                <button type="submit" disabled={busy} className="w-full rounded-md bg-slate-900 px-4 py-2 text-sm font-semibold text-white hover:bg-slate-700 disabled:cursor-not-allowed disabled:bg-slate-400">Save designation</button>
              </form>
            </div>

            <div className="rounded-xl border border-slate-200 p-4">
              <h3 className="text-lg font-semibold text-slate-950">Create Position</h3>
              <form className="mt-4 space-y-3" onSubmit={handlePositionSubmit}>
                <input required value={positionForm.position_code} onChange={(event) => setPositionForm({ ...positionForm, position_code: event.target.value })} placeholder="Position code" className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm" />
                <input required value={positionForm.position_title} onChange={(event) => setPositionForm({ ...positionForm, position_title: event.target.value })} placeholder="Position title" className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm" />
                <select value={positionForm.department_id} onChange={(event) => setPositionForm({ ...positionForm, department_id: event.target.value })} className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm">
                  <option value="">Select department</option>
                  {departments.map((department) => (
                    <option key={department.id} value={department.id}>
                      {department.department_name}
                    </option>
                  ))}
                </select>
                <select value={positionForm.designation_id} onChange={(event) => setPositionForm({ ...positionForm, designation_id: event.target.value })} className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm">
                  <option value="">Select designation</option>
                  {designations.map((designation) => (
                    <option key={designation.id} value={designation.id}>
                      {designation.designation_name}
                    </option>
                  ))}
                </select>
                <select value={positionForm.reports_to_position_id} onChange={(event) => setPositionForm({ ...positionForm, reports_to_position_id: event.target.value })} className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm">
                  <option value="">Reports to</option>
                  {positions.map((position) => (
                    <option key={position.id} value={position.id}>
                      {position.position_title}
                    </option>
                  ))}
                </select>
                <input type="number" value={positionForm.approval_limit} onChange={(event) => setPositionForm({ ...positionForm, approval_limit: event.target.value })} placeholder="Approval limit" className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm" />
                <button type="submit" disabled={busy} className="w-full rounded-md bg-slate-900 px-4 py-2 text-sm font-semibold text-white hover:bg-slate-700 disabled:cursor-not-allowed disabled:bg-slate-400">Save position</button>
              </form>
            </div>
          </div>

          <div className="mt-6 grid gap-4 lg:grid-cols-3">
            <div className="rounded-xl border border-slate-200 p-4">
              <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">Grades</h3>
              <div className="mt-3 space-y-2">
                {grades.length === 0 ? (
                  <p className="text-sm text-slate-500">No grades captured yet.</p>
                ) : (
                  grades.slice(0, 5).map((grade) => (
                    <div key={grade.id} className="rounded-lg bg-slate-50 p-2 text-sm text-slate-700">
                      <p className="font-medium text-slate-900">{grade.grade_name}</p>
                      <p className="text-xs text-slate-500">{grade.grade_code} • {grade.salary_band_min} - {grade.salary_band_max}</p>
                    </div>
                  ))
                )}
              </div>
            </div>
            <div className="rounded-xl border border-slate-200 p-4">
              <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">Designations</h3>
              <div className="mt-3 space-y-2">
                {designations.length === 0 ? (
                  <p className="text-sm text-slate-500">No designations captured yet.</p>
                ) : (
                  designations.slice(0, 5).map((designation) => (
                    <div key={designation.id} className="rounded-lg bg-slate-50 p-2 text-sm text-slate-700">
                      <p className="font-medium text-slate-900">{designation.designation_name}</p>
                      <p className="text-xs text-slate-500">{designation.designation_code} • Level {designation.reporting_level}</p>
                    </div>
                  ))
                )}
              </div>
            </div>
            <div className="rounded-xl border border-slate-200 p-4">
              <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">Positions</h3>
              <div className="mt-3 space-y-2">
                {positions.length === 0 ? (
                  <p className="text-sm text-slate-500">No positions captured yet.</p>
                ) : (
                  positions.slice(0, 5).map((position) => (
                    <div key={position.id} className="rounded-lg bg-slate-50 p-2 text-sm text-slate-700">
                      <p className="font-medium text-slate-900">{position.position_title}</p>
                      <p className="text-xs text-slate-500">{position.position_code} • {position.status}</p>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}

function TreeNode({ node, depth }: { node: OrganizationUnitNode; depth: number }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-semibold text-slate-900">
            {Array.from({ length: depth }).map((_, index) => (
              <span key={index} className="mr-2 text-slate-400">↳</span>
            ))}
            {node.unit_name}
          </p>
          <p className="text-xs text-slate-500">
            {node.unit_type} • {node.unit_code} • {node.status}
          </p>
        </div>
        <span className="rounded-full bg-blue-100 px-2 py-1 text-xs font-medium text-blue-700">{node.unit_type}</span>
      </div>
      <div className="mt-3 space-y-2 text-xs text-slate-600">
        {node.manager_position_id ? <p>Manager position: {node.manager_position_id}</p> : null}
        {node.cost_center_id ? <p>Cost center: {node.cost_center_id}</p> : null}
        {node.profit_center_id ? <p>Profit center: {node.profit_center_id}</p> : null}
      </div>
      {node.children?.length ? (
        <div className="mt-3 space-y-2 pl-4">
          {node.children.map((child) => (
            <TreeNode key={child.id} node={child} depth={depth + 1} />
          ))}
        </div>
      ) : null}
    </div>
  );
}
