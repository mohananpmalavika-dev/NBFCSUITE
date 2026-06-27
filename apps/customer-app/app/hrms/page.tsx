'use client';

import { apiClient } from '@/lib/api';
import { useAuth } from '@/lib/auth-context';
import { useRouter } from 'next/navigation';
import { ChangeEvent, FormEvent, useCallback, useEffect, useMemo, useState } from 'react';

interface Employee {
  id: string;
  employee_number: string;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  designation: string;
  department: string;
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

export default function HrmsPage() {
  const { user, token, isLoading } = useAuth();
  const router = useRouter();
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [payrollRuns, setPayrollRuns] = useState<PayrollRun[]>([]);
  const [payrollSlips, setPayrollSlips] = useState<PayrollSlip[]>([]);
  const [selectedRunId, setSelectedRunId] = useState<string>('');
  const [message, setMessage] = useState('');
  const [busyAction, setBusyAction] = useState('');
  const [employeeForm, setEmployeeForm] = useState({
    employee_number: '',
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    designation: '',
    department: '',
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
      const [employeesRes, runsRes] = await Promise.all([
        apiClient.getEmployees(user.branch_id ? { branch_id: user.branch_id } : undefined),
        apiClient.getPayrollRuns({ tenant_id: user.tenant_id || undefined }),
      ]);

      setEmployees(Array.isArray(employeesRes.data.items) ? employeesRes.data.items : employeesRes.data || []);
      setPayrollRuns(runsRes.data || []);
      setSelectedRunId((current) => current || runsRes.data?.[0]?.id || '');
      setSlipForm((current) => ({
        ...current,
        employee_id: current.employee_id || employeesRes.data?.[0]?.id || '',
      }));
    } catch (error) {
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

  const handleEmployeeChange = (event: ChangeEvent<HTMLInputElement>) => {
    const { name, value } = event.target;
    setEmployeeForm((current) => ({ ...current, [name]: value }));
  };

  const handleRunChange = (event: ChangeEvent<HTMLInputElement>) => {
    const { name, value } = event.target;
    setRunForm((current) => ({ ...current, [name]: value }));
  };

  const handleSlipChange = (event: ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = event.target;
    setSlipForm((current) => ({ ...current, [name]: value }));
  };

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

  const createEmployee = async (event: FormEvent) => {
    event.preventDefault();
    if (!user) {
      return;
    }
    await runAction('create-employee', async () => {
      await apiClient.createEmployee({
        tenant_id: user.tenant_id || 'default',
        employee_number: employeeForm.employee_number,
        first_name: employeeForm.first_name,
        last_name: employeeForm.last_name,
        email: employeeForm.email,
        phone: employeeForm.phone,
        designation: employeeForm.designation,
        department: employeeForm.department,
        branch_id: user.branch_id || undefined,
      });
      setEmployeeForm({
        employee_number: '',
        first_name: '',
        last_name: '',
        email: '',
        phone: '',
        designation: '',
        department: '',
      });
    }, 'Employee created successfully.');
  };

  const createPayrollRun = async (event: FormEvent) => {
    event.preventDefault();
    if (!user) {
      return;
    }

    await runAction('create-payroll-run', async () => {
      await apiClient.createPayrollRun({
        tenant_id: user.tenant_id || 'default',
        run_name: runForm.run_name || undefined,
        period_start: runForm.period_start,
        period_end: runForm.period_end,
      });
      setRunForm({ run_name: '', period_start: '', period_end: '' });
    }, 'Payroll run created.');
  };

  const addPayrollSlip = async (event: FormEvent) => {
    event.preventDefault();
    if (!user || !selectedRunId || !slipForm.employee_id) {
      return;
    }

    await runAction('add-payroll-slip', async () => {
      await apiClient.addPayrollSlip(selectedRunId, {
        tenant_id: user.tenant_id || 'default',
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
    if (!user) {
      return;
    }
    await runAction('finalize-payroll-run', async () => {
      await apiClient.finalizePayrollRun(runId, user.tenant_id || 'default');
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
            <h1 className="mt-1 text-3xl font-bold text-slate-950">Employee Master & Payroll</h1>
            <p className="mt-2 max-w-2xl text-slate-600">Manage employee records, payroll runs, and payroll slips for your scoped tenant.</p>
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

        <section className="mb-6 grid gap-4 md:grid-cols-3">
          <Metric label="Employees" value={String(employees.length)} />
          <Metric label="Payroll Runs" value={String(payrollRuns.length)} />
          <Metric label="Selected Run" value={selectedRun ? selectedRun.status : 'None'} />
        </section>

        <div className="grid gap-6 xl:grid-cols-[1.4fr_1fr]">
          <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-xl font-semibold text-slate-950">Create Employee</h2>
            <form onSubmit={createEmployee} className="grid gap-4">
              <div className="grid gap-4 sm:grid-cols-2">
                <InputField label="Employee Number" name="employee_number" value={employeeForm.employee_number} onChange={handleEmployeeChange} />
                <InputField label="First Name" name="first_name" value={employeeForm.first_name} onChange={handleEmployeeChange} />
              </div>
              <div className="grid gap-4 sm:grid-cols-2">
                <InputField label="Last Name" name="last_name" value={employeeForm.last_name} onChange={handleEmployeeChange} />
                <InputField label="Email" name="email" type="email" value={employeeForm.email} onChange={handleEmployeeChange} />
              </div>
              <div className="grid gap-4 sm:grid-cols-2">
                <InputField label="Phone" name="phone" value={employeeForm.phone} onChange={handleEmployeeChange} />
                <InputField label="Designation" name="designation" value={employeeForm.designation} onChange={handleEmployeeChange} />
              </div>
              <InputField label="Department" name="department" value={employeeForm.department} onChange={handleEmployeeChange} />
              <button
                type="submit"
                disabled={busyAction === 'create-employee'}
                className="inline-flex justify-center rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {busyAction === 'create-employee' ? 'Saving...' : 'Create Employee'}
              </button>
            </form>
          </section>

          <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-xl font-semibold text-slate-950">Create Payroll Run</h2>
            <form onSubmit={createPayrollRun} className="grid gap-4">
              <InputField label="Run Name" name="run_name" value={runForm.run_name} onChange={handleRunChange} />
              <div className="grid gap-4 sm:grid-cols-2">
                <InputField label="Start Date" name="period_start" type="date" value={runForm.period_start} onChange={handleRunChange} />
                <InputField label="End Date" name="period_end" type="date" value={runForm.period_end} onChange={handleRunChange} />
              </div>
              <button
                type="submit"
                disabled={busyAction === 'create-payroll-run'}
                className="inline-flex justify-center rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {busyAction === 'create-payroll-run' ? 'Creating...' : 'Create Payroll Run'}
              </button>
            </form>
          </section>
        </div>

        <section className="mt-6 grid gap-6 xl:grid-cols-[1.4fr_1fr]">
          <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <h2 className="text-xl font-semibold text-slate-950">Employees</h2>
              <span className="rounded-full bg-slate-100 px-3 py-1 text-sm text-slate-700">Branch: {user.branch_id || 'All'}</span>
            </div>
            {employees.length === 0 ? (
              <p className="rounded-md bg-slate-50 p-4 text-sm text-slate-600">No employee records found.</p>
            ) : (
              <div className="space-y-3">
                {employees.map((employee) => (
                  <div key={employee.id} className="rounded-lg border border-slate-200 p-4">
                    <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                      <div>
                        <p className="font-semibold text-slate-950">{employee.first_name} {employee.last_name}</p>
                        <p className="text-sm text-slate-500">{employee.designation} · {employee.department}</p>
                      </div>
                      <div className="text-sm text-slate-600">{employee.status}</div>
                    </div>
                    <div className="mt-3 grid gap-2 sm:grid-cols-2">
                      <p className="text-sm text-slate-600">Email: {employee.email}</p>
                      <p className="text-sm text-slate-600">Phone: {employee.phone}</p>
                      <p className="text-sm text-slate-600">Employee # {employee.employee_number}</p>
                      <p className="text-sm text-slate-600">Branch: {employee.branch_id || 'Unassigned'}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-xl font-semibold text-slate-950">Payroll Runs</h2>
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
                    <div className="mt-2 grid gap-2 sm:grid-cols-3 text-sm text-slate-600">
                      <span>Gross {formatCurrency(run.gross_pay)}</span>
                      <span>Deductions {formatCurrency(run.total_deductions)}</span>
                      <span>Net {formatCurrency(run.net_pay)}</span>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        </section>

        {selectedRun && (
          <section className="mt-6 rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <h2 className="text-xl font-semibold text-slate-950">Selected Payroll Run</h2>
                <p className="text-sm text-slate-500">{selectedRun.run_name || 'Unnamed run'} · {selectedRun.status}</p>
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
                  <label className="block">
                    <span className="text-sm font-medium text-slate-700">Employee</span>
                    <select
                      name="employee_id"
                      value={slipForm.employee_id}
                      onChange={handleSlipChange}
                      className="mt-1 w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
                    >
                      <option value="">Select Employee</option>
                      {employees.map((employee) => (
                        <option key={employee.id} value={employee.id}>
                          {employee.first_name} {employee.last_name}
                        </option>
                      ))}
                    </select>
                  </label>
                  <InputField label="Basic Pay" name="basic_pay" type="number" value={slipForm.basic_pay} onChange={handleSlipChange} />
                  <InputField label="Tax Amount" name="tax_amount" type="number" value={slipForm.tax_amount} onChange={handleSlipChange} />
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
    </main>
  );
}

function InputField({
  label,
  name,
  value,
  onChange,
  type = 'text',
}: {
  label: string;
  name: string;
  value: string;
  onChange: (event: ChangeEvent<HTMLInputElement | HTMLSelectElement>) => void;
  type?: string;
}) {
  return (
    <label className="block">
      <span className="text-sm font-medium text-slate-700">{label}</span>
      <input
        name={name}
        type={type}
        value={value}
        onChange={onChange}
        className="mt-1 w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
      />
    </label>
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
