'use client';

import { apiClient } from '@/lib/api';
import { useAuth } from '@/lib/auth-context';
import { useRouter } from 'next/navigation';
import { ChangeEvent, FormEvent, useCallback, useEffect, useMemo, useState } from 'react';

interface Department {
  id: string;
  department_code: string;
  department_name: string;
  parent_department_id?: string | null;
  cost_center_code?: string | null;
  profit_center_code?: string | null;
  annual_budget: number;
  status: string;
}

interface Grade {
  id: string;
  grade_code: string;
  grade_name: string;
  salary_band_min: number;
  salary_band_max: number;
  leave_entitlement_days: number;
  approval_limit: number;
  travel_class?: string | null;
  status: string;
}

interface Designation {
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

interface Position {
  id: string;
  position_code: string;
  position_title: string;
  department_id?: string | null;
  designation_id?: string | null;
  grade_id?: string | null;
  branch_id?: string | null;
  reports_to_position_id?: string | null;
  occupied_by_employee_id?: string | null;
  approval_limit: number;
  status: string;
}

interface Employee {
  id: string;
  employee_number: string;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  designation: string;
  department: string;
  department_id?: string | null;
  designation_id?: string | null;
  grade_id?: string | null;
  position_id?: string | null;
  manager_employee_id?: string | null;
  official_email?: string | null;
  branch_id?: string | null;
  status: string;
}

interface PayrollRun {
  id: string;
  run_name?: string | null;
  period_start: string;
  period_end: string;
  status: string;
  gross_pay: number;
  total_deductions: number;
  net_pay: number;
}

interface PayrollSlip {
  id: string;
  employee_name: string;
  basic_pay: number;
  allowances?: Record<string, number> | null;
  deductions?: Record<string, number> | null;
  tax_amount: number;
  gross_pay: number;
  total_deductions: number;
  net_pay: number;
  status: string;
}

type TabKey = 'organization' | 'employees' | 'payroll';

const tabs: Array<{ key: TabKey; label: string }> = [
  { key: 'organization', label: 'Organization' },
  { key: 'employees', label: 'Employees' },
  { key: 'payroll', label: 'Payroll' },
];

export default function HrmsPage() {
  const { user, token, isLoading } = useAuth();
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<TabKey>('organization');
  const [departments, setDepartments] = useState<Department[]>([]);
  const [grades, setGrades] = useState<Grade[]>([]);
  const [designations, setDesignations] = useState<Designation[]>([]);
  const [positions, setPositions] = useState<Position[]>([]);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [payrollRuns, setPayrollRuns] = useState<PayrollRun[]>([]);
  const [payrollSlips, setPayrollSlips] = useState<PayrollSlip[]>([]);
  const [selectedRunId, setSelectedRunId] = useState<string>('');
  const [message, setMessage] = useState('');
  const [busyAction, setBusyAction] = useState('');

  const [departmentForm, setDepartmentForm] = useState({
    department_code: '',
    department_name: '',
    parent_department_id: '',
    cost_center_code: '',
    profit_center_code: '',
    annual_budget: '0',
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
  const [employeeForm, setEmployeeForm] = useState({
    employee_number: '',
    first_name: '',
    last_name: '',
    email: '',
    official_email: '',
    phone: '',
    department_id: '',
    designation_id: '',
    grade_id: '',
    position_id: '',
    manager_employee_id: '',
  });
  const [runForm, setRunForm] = useState({
    run_name: '',
    period_start: '',
    period_end: '',
  });
  const [slipForm, setSlipForm] = useState({
    employee_id: '',
    basic_pay: '0',
    tax_amount: '0',
  });

  const selectedRun = useMemo(
    () => payrollRuns.find((run) => run.id === selectedRunId) || null,
    [payrollRuns, selectedRunId],
  );

  const openPositions = useMemo(
    () => positions.filter((position) => position.status === 'open'),
    [positions],
  );

  const activeEmployees = useMemo(
    () => employees.filter((employee) => employee.status === 'active'),
    [employees],
  );

  useEffect(() => {
    if (!isLoading && !token) {
      router.push('/login');
    }
  }, [token, isLoading, router]);

  const loadHrmsData = useCallback(async () => {
    if (!token || !user) {
      return;
    }

    setMessage('');
    try {
      const tenantParams = { tenant_id: user.tenant_id || undefined };
      const [departmentsRes, gradesRes, designationsRes, positionsRes, employeesRes, runsRes] = await Promise.all([
        apiClient.getHrmsDepartments(tenantParams),
        apiClient.getHrmsGrades(tenantParams),
        apiClient.getHrmsDesignations(tenantParams),
        apiClient.getHrmsPositions(user.branch_id ? { ...tenantParams, branch_id: user.branch_id } : tenantParams),
        apiClient.getEmployees(user.branch_id ? { branch_id: user.branch_id } : tenantParams),
        apiClient.getPayrollRuns(tenantParams),
      ]);

      const loadedEmployees = Array.isArray(employeesRes.data.items) ? employeesRes.data.items : employeesRes.data || [];
      const loadedRuns = runsRes.data || [];
      setDepartments(departmentsRes.data || []);
      setGrades(gradesRes.data || []);
      setDesignations(designationsRes.data || []);
      setPositions(positionsRes.data || []);
      setEmployees(loadedEmployees);
      setPayrollRuns(loadedRuns);
      setSelectedRunId((current) => current || loadedRuns?.[0]?.id || '');
      setSlipForm((current) => ({
        ...current,
        employee_id: current.employee_id || loadedEmployees?.[0]?.id || '',
      }));
    } catch {
      setMessage('Unable to load HRMS data.');
    }
  }, [token, user]);

  const loadPayrollSlips = useCallback(async () => {
    if (!token || !user || !selectedRunId) {
      setPayrollSlips([]);
      return;
    }

    try {
      const slipsRes = await apiClient.getPayrollSlips(selectedRunId, user.tenant_id || 'default');
      setPayrollSlips(slipsRes.data || []);
    } catch {
      setPayrollSlips([]);
    }
  }, [selectedRunId, token, user]);

  useEffect(() => {
    loadHrmsData();
  }, [loadHrmsData]);

  useEffect(() => {
    loadPayrollSlips();
  }, [loadPayrollSlips]);

  const formatCurrency = (value: number) => `INR ${Number(value || 0).toLocaleString()}`;

  const tenantId = user?.tenant_id || 'default';

  const runAction = async (key: string, action: () => Promise<void>, successMessage: string) => {
    setBusyAction(key);
    setMessage('');
    try {
      await action();
      setMessage(successMessage);
      await loadHrmsData();
      if (selectedRunId) {
        await loadPayrollSlips();
      }
    } catch {
      setMessage('Action failed. Check the data and try again.');
    } finally {
      setBusyAction('');
    }
  };

  const handleFormChange =
    <T extends Record<string, string>>(setter: React.Dispatch<React.SetStateAction<T>>) =>
    (event: ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
      const { name, value } = event.target;
      setter((current) => ({ ...current, [name]: value }));
    };

  const createDepartment = async (event: FormEvent) => {
    event.preventDefault();
    await runAction('create-department', async () => {
      await apiClient.createHrmsDepartment({
        tenant_id: tenantId,
        department_code: departmentForm.department_code,
        department_name: departmentForm.department_name,
        parent_department_id: departmentForm.parent_department_id || undefined,
        cost_center_code: departmentForm.cost_center_code || undefined,
        profit_center_code: departmentForm.profit_center_code || undefined,
        annual_budget: Number(departmentForm.annual_budget),
      });
      setDepartmentForm({
        department_code: '',
        department_name: '',
        parent_department_id: '',
        cost_center_code: '',
        profit_center_code: '',
        annual_budget: '0',
      });
    }, 'Department created.');
  };

  const createGrade = async (event: FormEvent) => {
    event.preventDefault();
    await runAction('create-grade', async () => {
      await apiClient.createHrmsGrade({
        tenant_id: tenantId,
        grade_code: gradeForm.grade_code,
        grade_name: gradeForm.grade_name,
        salary_band_min: Number(gradeForm.salary_band_min),
        salary_band_max: Number(gradeForm.salary_band_max),
        leave_entitlement_days: Number(gradeForm.leave_entitlement_days),
        approval_limit: Number(gradeForm.approval_limit),
        travel_class: gradeForm.travel_class || undefined,
        benefits: {},
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
    }, 'Grade created.');
  };

  const createDesignation = async (event: FormEvent) => {
    event.preventDefault();
    await runAction('create-designation', async () => {
      await apiClient.createHrmsDesignation({
        tenant_id: tenantId,
        designation_code: designationForm.designation_code,
        designation_name: designationForm.designation_name,
        grade_id: designationForm.grade_id || undefined,
        salary_band_min: Number(designationForm.salary_band_min),
        salary_band_max: Number(designationForm.salary_band_max),
        approval_limit: Number(designationForm.approval_limit),
        reporting_level: Number(designationForm.reporting_level),
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
    }, 'Designation created.');
  };

  const createPosition = async (event: FormEvent) => {
    event.preventDefault();
    await runAction('create-position', async () => {
      await apiClient.createHrmsPosition({
        tenant_id: tenantId,
        position_code: positionForm.position_code,
        position_title: positionForm.position_title,
        department_id: positionForm.department_id || undefined,
        designation_id: positionForm.designation_id || undefined,
        grade_id: positionForm.grade_id || undefined,
        branch_id: user?.branch_id || undefined,
        reports_to_position_id: positionForm.reports_to_position_id || undefined,
        approval_limit: Number(positionForm.approval_limit),
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
    }, 'Position created.');
  };

  const createEmployee = async (event: FormEvent) => {
    event.preventDefault();
    if (!user) {
      return;
    }

    const department = departments.find((item) => item.id === employeeForm.department_id);
    const designation = designations.find((item) => item.id === employeeForm.designation_id);
    const selectedPosition = positions.find((item) => item.id === employeeForm.position_id);

    await runAction('create-employee', async () => {
      await apiClient.createEmployee({
        tenant_id: tenantId,
        employee_number: employeeForm.employee_number,
        first_name: employeeForm.first_name,
        last_name: employeeForm.last_name,
        email: employeeForm.email,
        official_email: employeeForm.official_email || undefined,
        phone: employeeForm.phone,
        designation: designation?.designation_name || selectedPosition?.position_title || '',
        department: department?.department_name || '',
        department_id: employeeForm.department_id || undefined,
        designation_id: employeeForm.designation_id || undefined,
        grade_id: employeeForm.grade_id || undefined,
        position_id: employeeForm.position_id || undefined,
        manager_employee_id: employeeForm.manager_employee_id || undefined,
        branch_id: user.branch_id || undefined,
      });
      setEmployeeForm({
        employee_number: '',
        first_name: '',
        last_name: '',
        email: '',
        official_email: '',
        phone: '',
        department_id: '',
        designation_id: '',
        grade_id: '',
        position_id: '',
        manager_employee_id: '',
      });
    }, 'Employee created and organization assignment linked.');
  };

  const createPayrollRun = async (event: FormEvent) => {
    event.preventDefault();
    await runAction('create-payroll-run', async () => {
      await apiClient.createPayrollRun({
        tenant_id: tenantId,
        run_name: runForm.run_name || undefined,
        period_start: runForm.period_start,
        period_end: runForm.period_end,
      });
      setRunForm({ run_name: '', period_start: '', period_end: '' });
    }, 'Payroll run created.');
  };

  const addPayrollSlip = async (event: FormEvent) => {
    event.preventDefault();
    if (!selectedRunId || !slipForm.employee_id) {
      return;
    }

    await runAction('add-payroll-slip', async () => {
      await apiClient.addPayrollSlip(selectedRunId, {
        tenant_id: tenantId,
        employee_id: slipForm.employee_id,
        basic_pay: Number(slipForm.basic_pay),
        allowances: {},
        deductions: {},
        tax_amount: Number(slipForm.tax_amount),
      });
      setSlipForm((current) => ({ ...current, basic_pay: '0', tax_amount: '0' }));
    }, 'Payroll slip added.');
  };

  const finalizeRun = async (runId: string) => {
    await runAction('finalize-payroll-run', async () => {
      await apiClient.finalizePayrollRun(runId, tenantId);
    }, 'Payroll run finalized.');
  };

  if (isLoading || !token) {
    return <div className="p-8 text-center">Loading...</div>;
  }

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-8">
      <div className="mx-auto max-w-7xl">
        <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase text-blue-700">HRMS</p>
            <h1 className="mt-1 text-3xl font-bold text-slate-950">Enterprise HRMS Command Center</h1>
            <p className="mt-2 max-w-3xl text-slate-600">
              Configure departments, grades, designations, positions, employee master data, and payroll for the scoped tenant.
            </p>
          </div>
          <button
            onClick={() => router.push('/')}
            className="rounded-md border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-white"
          >
            Dashboard
          </button>
        </div>

        {message && (
          <div className="mb-4 rounded-md border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-900">
            {message}
          </div>
        )}

        <section className="mb-6 grid gap-4 md:grid-cols-4">
          <Metric label="Departments" value={String(departments.length)} />
          <Metric label="Open Positions" value={String(openPositions.length)} />
          <Metric label="Active Employees" value={String(activeEmployees.length)} />
          <Metric label="Payroll Runs" value={String(payrollRuns.length)} />
        </section>

        <div className="mb-6 inline-flex rounded-md border border-slate-200 bg-white p-1 shadow-sm">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              type="button"
              onClick={() => setActiveTab(tab.key)}
              className={`rounded px-4 py-2 text-sm font-semibold transition ${
                activeTab === tab.key ? 'bg-blue-600 text-white' : 'text-slate-600 hover:bg-slate-100'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {activeTab === 'organization' && (
          <div className="grid gap-6">
            <section className="grid gap-6 xl:grid-cols-2">
              <SetupPanel title="Department Management" onSubmit={createDepartment} busy={busyAction === 'create-department'} submitLabel="Create Department">
                <div className="grid gap-4 sm:grid-cols-2">
                  <InputField label="Department Code" name="department_code" value={departmentForm.department_code} onChange={handleFormChange(setDepartmentForm)} required />
                  <InputField label="Department Name" name="department_name" value={departmentForm.department_name} onChange={handleFormChange(setDepartmentForm)} required />
                  <SelectField label="Parent Department" name="parent_department_id" value={departmentForm.parent_department_id} onChange={handleFormChange(setDepartmentForm)} options={departments.map((item) => ({ value: item.id, label: item.department_name }))} />
                  <InputField label="Cost Center" name="cost_center_code" value={departmentForm.cost_center_code} onChange={handleFormChange(setDepartmentForm)} />
                  <InputField label="Profit Center" name="profit_center_code" value={departmentForm.profit_center_code} onChange={handleFormChange(setDepartmentForm)} />
                  <InputField label="Annual Budget" name="annual_budget" type="number" value={departmentForm.annual_budget} onChange={handleFormChange(setDepartmentForm)} />
                </div>
              </SetupPanel>

              <SetupPanel title="Grade Management" onSubmit={createGrade} busy={busyAction === 'create-grade'} submitLabel="Create Grade">
                <div className="grid gap-4 sm:grid-cols-2">
                  <InputField label="Grade Code" name="grade_code" value={gradeForm.grade_code} onChange={handleFormChange(setGradeForm)} required />
                  <InputField label="Grade Name" name="grade_name" value={gradeForm.grade_name} onChange={handleFormChange(setGradeForm)} required />
                  <InputField label="Salary Band Min" name="salary_band_min" type="number" value={gradeForm.salary_band_min} onChange={handleFormChange(setGradeForm)} />
                  <InputField label="Salary Band Max" name="salary_band_max" type="number" value={gradeForm.salary_band_max} onChange={handleFormChange(setGradeForm)} />
                  <InputField label="Leave Days" name="leave_entitlement_days" type="number" value={gradeForm.leave_entitlement_days} onChange={handleFormChange(setGradeForm)} />
                  <InputField label="Approval Limit" name="approval_limit" type="number" value={gradeForm.approval_limit} onChange={handleFormChange(setGradeForm)} />
                  <InputField label="Travel Class" name="travel_class" value={gradeForm.travel_class} onChange={handleFormChange(setGradeForm)} />
                </div>
              </SetupPanel>

              <SetupPanel title="Designation Management" onSubmit={createDesignation} busy={busyAction === 'create-designation'} submitLabel="Create Designation">
                <div className="grid gap-4 sm:grid-cols-2">
                  <InputField label="Designation Code" name="designation_code" value={designationForm.designation_code} onChange={handleFormChange(setDesignationForm)} required />
                  <InputField label="Designation Name" name="designation_name" value={designationForm.designation_name} onChange={handleFormChange(setDesignationForm)} required />
                  <SelectField label="Grade" name="grade_id" value={designationForm.grade_id} onChange={handleFormChange(setDesignationForm)} options={grades.map((item) => ({ value: item.id, label: `${item.grade_code} - ${item.grade_name}` }))} />
                  <InputField label="Reporting Level" name="reporting_level" type="number" value={designationForm.reporting_level} onChange={handleFormChange(setDesignationForm)} />
                  <InputField label="Salary Band Min" name="salary_band_min" type="number" value={designationForm.salary_band_min} onChange={handleFormChange(setDesignationForm)} />
                  <InputField label="Salary Band Max" name="salary_band_max" type="number" value={designationForm.salary_band_max} onChange={handleFormChange(setDesignationForm)} />
                  <InputField label="Approval Limit" name="approval_limit" type="number" value={designationForm.approval_limit} onChange={handleFormChange(setDesignationForm)} />
                </div>
              </SetupPanel>

              <SetupPanel title="Position Management" onSubmit={createPosition} busy={busyAction === 'create-position'} submitLabel="Create Position">
                <div className="grid gap-4 sm:grid-cols-2">
                  <InputField label="Position Code" name="position_code" value={positionForm.position_code} onChange={handleFormChange(setPositionForm)} required />
                  <InputField label="Position Title" name="position_title" value={positionForm.position_title} onChange={handleFormChange(setPositionForm)} required />
                  <SelectField label="Department" name="department_id" value={positionForm.department_id} onChange={handleFormChange(setPositionForm)} options={departments.map((item) => ({ value: item.id, label: item.department_name }))} />
                  <SelectField label="Designation" name="designation_id" value={positionForm.designation_id} onChange={handleFormChange(setPositionForm)} options={designations.map((item) => ({ value: item.id, label: item.designation_name }))} />
                  <SelectField label="Grade" name="grade_id" value={positionForm.grade_id} onChange={handleFormChange(setPositionForm)} options={grades.map((item) => ({ value: item.id, label: item.grade_code }))} />
                  <SelectField label="Reports To Position" name="reports_to_position_id" value={positionForm.reports_to_position_id} onChange={handleFormChange(setPositionForm)} options={positions.map((item) => ({ value: item.id, label: item.position_title }))} />
                  <InputField label="Approval Limit" name="approval_limit" type="number" value={positionForm.approval_limit} onChange={handleFormChange(setPositionForm)} />
                </div>
              </SetupPanel>
            </section>

            <section className="grid gap-6 xl:grid-cols-2">
              <DataPanel title="Departments">
                <EntityList
                  emptyText="No departments configured."
                  items={departments.map((item) => ({
                    id: item.id,
                    title: item.department_name,
                    detail: `${item.department_code} / Cost ${item.cost_center_code || 'NA'} / Profit ${item.profit_center_code || 'NA'}`,
                    status: item.status,
                  }))}
                />
              </DataPanel>
              <DataPanel title="Positions">
                <EntityList
                  emptyText="No positions configured."
                  items={positions.map((item) => ({
                    id: item.id,
                    title: item.position_title,
                    detail: `${item.position_code} / ${departmentName(item.department_id, departments)} / ${item.occupied_by_employee_id ? 'Occupied' : 'Vacant'}`,
                    status: item.status,
                  }))}
                />
              </DataPanel>
            </section>
          </div>
        )}

        {activeTab === 'employees' && (
          <section className="grid gap-6 xl:grid-cols-[0.95fr_1.25fr]">
            <SetupPanel title="Employee Master" onSubmit={createEmployee} busy={busyAction === 'create-employee'} submitLabel="Create Employee">
              <div className="grid gap-4 sm:grid-cols-2">
                <InputField label="Employee Number" name="employee_number" value={employeeForm.employee_number} onChange={handleFormChange(setEmployeeForm)} required />
                <InputField label="First Name" name="first_name" value={employeeForm.first_name} onChange={handleFormChange(setEmployeeForm)} required />
                <InputField label="Last Name" name="last_name" value={employeeForm.last_name} onChange={handleFormChange(setEmployeeForm)} required />
                <InputField label="Personal Email" name="email" type="email" value={employeeForm.email} onChange={handleFormChange(setEmployeeForm)} required />
                <InputField label="Official Email" name="official_email" type="email" value={employeeForm.official_email} onChange={handleFormChange(setEmployeeForm)} />
                <InputField label="Phone" name="phone" value={employeeForm.phone} onChange={handleFormChange(setEmployeeForm)} required />
                <SelectField label="Department" name="department_id" value={employeeForm.department_id} onChange={handleFormChange(setEmployeeForm)} options={departments.map((item) => ({ value: item.id, label: item.department_name }))} />
                <SelectField label="Designation" name="designation_id" value={employeeForm.designation_id} onChange={handleFormChange(setEmployeeForm)} options={designations.map((item) => ({ value: item.id, label: item.designation_name }))} />
                <SelectField label="Grade" name="grade_id" value={employeeForm.grade_id} onChange={handleFormChange(setEmployeeForm)} options={grades.map((item) => ({ value: item.id, label: item.grade_code }))} />
                <SelectField label="Open Position" name="position_id" value={employeeForm.position_id} onChange={handleFormChange(setEmployeeForm)} options={openPositions.map((item) => ({ value: item.id, label: `${item.position_code} - ${item.position_title}` }))} />
                <SelectField label="Manager" name="manager_employee_id" value={employeeForm.manager_employee_id} onChange={handleFormChange(setEmployeeForm)} options={employees.map((item) => ({ value: item.id, label: `${item.first_name} ${item.last_name}` }))} />
              </div>
            </SetupPanel>

            <DataPanel title="Employees">
              {employees.length === 0 ? (
                <p className="rounded-md bg-slate-50 p-4 text-sm text-slate-600">No employee records found.</p>
              ) : (
                <div className="space-y-3">
                  {employees.map((employee) => (
                    <div key={employee.id} className="rounded-lg border border-slate-200 p-4">
                      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                        <div>
                          <p className="font-semibold text-slate-950">{employee.first_name} {employee.last_name}</p>
                          <p className="text-sm text-slate-500">{employee.designation || 'Unassigned'} / {employee.department || 'No department'}</p>
                        </div>
                        <span className="rounded-full bg-slate-100 px-2 py-1 text-xs font-semibold text-slate-700">{employee.status}</span>
                      </div>
                      <div className="mt-3 grid gap-2 sm:grid-cols-2">
                        <p className="text-sm text-slate-600">Employee # {employee.employee_number}</p>
                        <p className="text-sm text-slate-600">Branch: {employee.branch_id || 'Unassigned'}</p>
                        <p className="text-sm text-slate-600">Email: {employee.official_email || employee.email}</p>
                        <p className="text-sm text-slate-600">Position: {positionTitle(employee.position_id, positions)}</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </DataPanel>
          </section>
        )}

        {activeTab === 'payroll' && (
          <div className="grid gap-6">
            <section className="grid gap-6 xl:grid-cols-[1fr_1.4fr]">
              <SetupPanel title="Create Payroll Run" onSubmit={createPayrollRun} busy={busyAction === 'create-payroll-run'} submitLabel="Create Payroll Run">
                <InputField label="Run Name" name="run_name" value={runForm.run_name} onChange={handleFormChange(setRunForm)} />
                <div className="grid gap-4 sm:grid-cols-2">
                  <InputField label="Start Date" name="period_start" type="date" value={runForm.period_start} onChange={handleFormChange(setRunForm)} required />
                  <InputField label="End Date" name="period_end" type="date" value={runForm.period_end} onChange={handleFormChange(setRunForm)} required />
                </div>
              </SetupPanel>

              <DataPanel title="Payroll Runs">
                {payrollRuns.length === 0 ? (
                  <p className="rounded-md bg-slate-50 p-4 text-sm text-slate-600">No payroll runs exist yet.</p>
                ) : (
                  <div className="space-y-3">
                    {payrollRuns.map((run) => (
                      <button
                        key={run.id}
                        type="button"
                        onClick={() => setSelectedRunId(run.id)}
                        className={`w-full rounded-lg border px-4 py-3 text-left transition ${
                          selectedRunId === run.id ? 'border-blue-500 bg-blue-50' : 'border-slate-200 bg-white hover:border-slate-300'
                        }`}
                      >
                        <div className="flex items-center justify-between gap-3">
                          <div>
                            <p className="font-semibold text-slate-950">{run.run_name || 'Payroll run'}</p>
                            <p className="text-sm text-slate-500">{new Date(run.period_start).toLocaleDateString()} - {new Date(run.period_end).toLocaleDateString()}</p>
                          </div>
                          <span className="rounded-full bg-slate-100 px-2 py-1 text-xs font-semibold text-slate-700">{run.status}</span>
                        </div>
                        <div className="mt-2 grid gap-2 text-sm text-slate-600 sm:grid-cols-3">
                          <span>Gross {formatCurrency(run.gross_pay)}</span>
                          <span>Deductions {formatCurrency(run.total_deductions)}</span>
                          <span>Net {formatCurrency(run.net_pay)}</span>
                        </div>
                      </button>
                    ))}
                  </div>
                )}
              </DataPanel>
            </section>

            {selectedRun && (
              <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
                <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <h2 className="text-xl font-semibold text-slate-950">Selected Payroll Run</h2>
                    <p className="text-sm text-slate-500">{selectedRun.run_name || 'Unnamed run'} / {selectedRun.status}</p>
                  </div>
                  <button
                    onClick={() => finalizeRun(selectedRun.id)}
                    disabled={busyAction === 'finalize-payroll-run' || selectedRun.status === 'finalized'}
                    className="rounded-md bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    {selectedRun.status === 'finalized' ? 'Finalized' : busyAction === 'finalize-payroll-run' ? 'Finalizing...' : 'Finalize Run'}
                  </button>
                </div>

                <div className="grid gap-4 md:grid-cols-3">
                  <SummaryCard label="Gross Pay" value={formatCurrency(selectedRun.gross_pay)} />
                  <SummaryCard label="Deductions" value={formatCurrency(selectedRun.total_deductions)} />
                  <SummaryCard label="Net Pay" value={formatCurrency(selectedRun.net_pay)} />
                </div>

                <div className="mt-6 grid gap-6 lg:grid-cols-[1.4fr_1fr]">
                  <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
                    <h3 className="mb-3 text-lg font-semibold text-slate-950">Payroll Slips</h3>
                    {payrollSlips.length === 0 ? (
                      <p className="text-sm text-slate-600">No slips have been added to this run.</p>
                    ) : (
                      <ul className="space-y-3">
                        {payrollSlips.map((slip) => (
                          <li key={slip.id} className="rounded-lg border border-slate-200 bg-white p-3">
                            <div className="flex items-center justify-between gap-3">
                              <p className="font-semibold text-slate-900">{slip.employee_name}</p>
                              <span className="rounded-full bg-slate-100 px-2 py-1 text-xs font-semibold text-slate-700">{slip.status}</span>
                            </div>
                            <p className="mt-2 text-sm text-slate-600">Basic pay: {formatCurrency(slip.basic_pay)}, Tax: {formatCurrency(slip.tax_amount)}</p>
                            <p className="text-sm text-slate-600">Net pay: {formatCurrency(slip.net_pay)}</p>
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>

                  <div className="rounded-lg border border-slate-200 bg-white p-6">
                    <h3 className="mb-4 text-lg font-semibold text-slate-950">Add Payroll Slip</h3>
                    <form onSubmit={addPayrollSlip} className="grid gap-4">
                      <SelectField
                        label="Employee"
                        name="employee_id"
                        value={slipForm.employee_id}
                        onChange={handleFormChange(setSlipForm)}
                        options={employees.map((employee) => ({ value: employee.id, label: `${employee.first_name} ${employee.last_name}` }))}
                        required
                      />
                      <InputField label="Basic Pay" name="basic_pay" type="number" value={slipForm.basic_pay} onChange={handleFormChange(setSlipForm)} />
                      <InputField label="Tax Amount" name="tax_amount" type="number" value={slipForm.tax_amount} onChange={handleFormChange(setSlipForm)} />
                      <button
                        type="submit"
                        disabled={busyAction === 'add-payroll-slip' || !selectedRunId}
                        className="inline-flex justify-center rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
                      >
                        {busyAction === 'add-payroll-slip' ? 'Adding...' : 'Add Payroll Slip'}
                      </button>
                    </form>
                  </div>
                </div>
              </section>
            )}
          </div>
        )}
      </div>
    </main>
  );
}

function SetupPanel({
  title,
  children,
  onSubmit,
  busy,
  submitLabel,
}: {
  title: string;
  children: React.ReactNode;
  onSubmit: (event: FormEvent) => void;
  busy: boolean;
  submitLabel: string;
}) {
  return (
    <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
      <h2 className="mb-4 text-xl font-semibold text-slate-950">{title}</h2>
      <form onSubmit={onSubmit} className="grid gap-4">
        {children}
        <button
          type="submit"
          disabled={busy}
          className="inline-flex justify-center rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {busy ? 'Saving...' : submitLabel}
        </button>
      </form>
    </section>
  );
}

function DataPanel({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
      <h2 className="mb-4 text-xl font-semibold text-slate-950">{title}</h2>
      {children}
    </section>
  );
}

function InputField({
  label,
  name,
  value,
  onChange,
  type = 'text',
  required = false,
}: {
  label: string;
  name: string;
  value: string;
  onChange: (event: ChangeEvent<HTMLInputElement | HTMLSelectElement>) => void;
  type?: string;
  required?: boolean;
}) {
  return (
    <label className="block">
      <span className="text-sm font-medium text-slate-700">{label}</span>
      <input
        name={name}
        type={type}
        value={value}
        onChange={onChange}
        required={required}
        className="mt-1 w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
      />
    </label>
  );
}

function SelectField({
  label,
  name,
  value,
  onChange,
  options,
  required = false,
}: {
  label: string;
  name: string;
  value: string;
  onChange: (event: ChangeEvent<HTMLInputElement | HTMLSelectElement>) => void;
  options: Array<{ value: string; label: string }>;
  required?: boolean;
}) {
  return (
    <label className="block">
      <span className="text-sm font-medium text-slate-700">{label}</span>
      <select
        name={name}
        value={value}
        onChange={onChange}
        required={required}
        className="mt-1 w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
      >
        <option value="">Select</option>
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </label>
  );
}

function EntityList({
  items,
  emptyText,
}: {
  items: Array<{ id: string; title: string; detail: string; status: string }>;
  emptyText: string;
}) {
  if (items.length === 0) {
    return <p className="rounded-md bg-slate-50 p-4 text-sm text-slate-600">{emptyText}</p>;
  }

  return (
    <div className="space-y-3">
      {items.map((item) => (
        <div key={item.id} className="rounded-lg border border-slate-200 p-4">
          <div className="flex items-center justify-between gap-3">
            <div>
              <p className="font-semibold text-slate-950">{item.title}</p>
              <p className="text-sm text-slate-500">{item.detail}</p>
            </div>
            <span className="rounded-full bg-slate-100 px-2 py-1 text-xs font-semibold text-slate-700">{item.status}</span>
          </div>
        </div>
      ))}
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-5 text-center shadow-sm">
      <p className="text-sm font-medium uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-3 text-3xl font-semibold text-slate-950">{value}</p>
    </div>
  );
}

function SummaryCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700">
      <p className="font-semibold text-slate-900">{label}</p>
      <p className="mt-2 text-xl font-semibold text-slate-950">{value}</p>
    </div>
  );
}

function departmentName(departmentId: string | null | undefined, departments: Department[]) {
  return departments.find((item) => item.id === departmentId)?.department_name || 'No department';
}

function positionTitle(positionId: string | null | undefined, positions: Position[]) {
  return positions.find((item) => item.id === positionId)?.position_title || 'Unassigned';
}
