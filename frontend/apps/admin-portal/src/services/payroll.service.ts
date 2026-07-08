/**
 * Payroll API Service
 * Frontend service for payroll management API calls
 */

import {
  SalaryComponent,
  SalaryComponentCreate,
  SalaryComponentUpdate,
  SalaryComponentListResponse,
  SalaryStructure,
  SalaryStructureCreate,
  SalaryStructureListResponse,
  EmployeeSalary,
  EmployeeSalaryCreate,
  EmployeeSalaryListResponse,
  PayrollRun,
  PayrollRunCreate,
  PayrollRunListResponse,
  PayrollRunProcessRequest,
  PayrollRunApproveRequest,
  Payslip,
  PayslipListResponse,
  StatutoryCompliance,
  StatutoryComplianceListResponse,
  Form16,
  Form16ListResponse,
  PaymentFile,
  PaymentFileListResponse,
  PayrollDashboardStats,
  PayrollSummary,
  PayrollFilterParams,
} from '@/types/payroll.types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// ============ Utility Functions ============

const handleResponse = async <T>(response: Response): Promise<T> => {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'An error occurred' }));
    throw new Error(error.detail || `HTTP error! status: ${response.status}`);
  }
  return response.json();
};

const buildQueryString = (params: Record<string, any>): string => {
  const filtered = Object.entries(params)
    .filter(([_, value]) => value !== undefined && value !== null && value !== '')
    .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
    .join('&');
  return filtered ? `?${filtered}` : '';
};

// ============ Salary Component Service ============

export const salaryComponentService = {
  async create(data: SalaryComponentCreate): Promise<SalaryComponent> {
    const response = await fetch(`${API_BASE_URL}/api/payroll/components`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return handleResponse<SalaryComponent>(response);
  },

  async list(params: PayrollFilterParams = {}): Promise<SalaryComponentListResponse> {
    const queryString = buildQueryString(params);
    const response = await fetch(`${API_BASE_URL}/api/payroll/components${queryString}`);
    return handleResponse<SalaryComponentListResponse>(response);
  },

  async get(id: number): Promise<SalaryComponent> {
    const response = await fetch(`${API_BASE_URL}/api/payroll/components/${id}`);
    return handleResponse<SalaryComponent>(response);
  },

  async update(id: number, data: SalaryComponentUpdate): Promise<SalaryComponent> {
    const response = await fetch(`${API_BASE_URL}/api/payroll/components/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return handleResponse<SalaryComponent>(response);
  },

  async delete(id: number): Promise<{ message: string }> {
    const response = await fetch(`${API_BASE_URL}/api/payroll/components/${id}`, {
      method: 'DELETE',
    });
    return handleResponse<{ message: string }>(response);
  },
};

// ============ Salary Structure Service ============

export const salaryStructureService = {
  async create(data: SalaryStructureCreate): Promise<SalaryStructure> {
    const response = await fetch(`${API_BASE_URL}/api/payroll/structures`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return handleResponse<SalaryStructure>(response);
  },

  async list(params: PayrollFilterParams = {}): Promise<SalaryStructureListResponse> {
    const queryString = buildQueryString(params);
    const response = await fetch(`${API_BASE_URL}/api/payroll/structures${queryString}`);
    return handleResponse<SalaryStructureListResponse>(response);
  },

  async get(id: number): Promise<SalaryStructure> {
    const response = await fetch(`${API_BASE_URL}/api/payroll/structures/${id}`);
    return handleResponse<SalaryStructure>(response);
  },

  async update(id: number, data: any): Promise<SalaryStructure> {
    const response = await fetch(`${API_BASE_URL}/api/payroll/structures/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return handleResponse<SalaryStructure>(response);
  },

  async delete(id: number): Promise<{ message: string }> {
    const response = await fetch(`${API_BASE_URL}/api/payroll/structures/${id}`, {
      method: 'DELETE',
    });
    return handleResponse<{ message: string }>(response);
  },
};

// ============ Employee Salary Service ============

export const employeeSalaryService = {
  async create(data: EmployeeSalaryCreate): Promise<EmployeeSalary> {
    const response = await fetch(`${API_BASE_URL}/api/payroll/employee-salaries`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return handleResponse<EmployeeSalary>(response);
  },

  async list(params: PayrollFilterParams = {}): Promise<EmployeeSalaryListResponse> {
    const queryString = buildQueryString(params);
    const response = await fetch(`${API_BASE_URL}/api/payroll/employee-salaries${queryString}`);
    return handleResponse<EmployeeSalaryListResponse>(response);
  },

  async get(id: number): Promise<EmployeeSalary> {
    const response = await fetch(`${API_BASE_URL}/api/payroll/employee-salaries/${id}`);
    return handleResponse<EmployeeSalary>(response);
  },

  async getByEmployee(employeeId: number): Promise<EmployeeSalary> {
    const response = await fetch(`${API_BASE_URL}/api/payroll/employee-salaries/employee/${employeeId}`);
    return handleResponse<EmployeeSalary>(response);
  },

  async update(id: number, data: any): Promise<EmployeeSalary> {
    const response = await fetch(`${API_BASE_URL}/api/payroll/employee-salaries/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return handleResponse<EmployeeSalary>(response);
  },
};

// ============ Payroll Run Service ============

export const payrollRunService = {
  async create(data: PayrollRunCreate): Promise<PayrollRun> {
    const response = await fetch(`${API_BASE_URL}/api/payroll/runs`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return handleResponse<PayrollRun>(response);
  },

  async list(params: PayrollFilterParams = {}): Promise<PayrollRunListResponse> {
    const queryString = buildQueryString(params);
    const response = await fetch(`${API_BASE_URL}/api/payroll/runs${queryString}`);
    return handleResponse<PayrollRunListResponse>(response);
  },

  async get(id: number): Promise<PayrollRun> {
    const response = await fetch(`${API_BASE_URL}/api/payroll/runs/${id}`);
    return handleResponse<PayrollRun>(response);
  },

  async process(id: number, data: PayrollRunProcessRequest): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/api/payroll/runs/${id}/process`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return handleResponse<any>(response);
  },

  async approve(id: number, data: PayrollRunApproveRequest): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/api/payroll/runs/${id}/approve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return handleResponse<any>(response);
  },
};

// ============ Payslip Service ============

export const payslipService = {
  async list(params: PayrollFilterParams = {}): Promise<PayslipListResponse> {
    const queryString = buildQueryString(params);
    const response = await fetch(`${API_BASE_URL}/api/payroll/payslips${queryString}`);
    return handleResponse<PayslipListResponse>(response);
  },

  async get(id: number): Promise<Payslip> {
    const response = await fetch(`${API_BASE_URL}/api/payroll/payslips/${id}`);
    return handleResponse<Payslip>(response);
  },

  async download(id: number): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/api/payroll/payslips/${id}/download`);
    return handleResponse<any>(response);
  },
};

// ============ Statutory Compliance Service ============

export const statutoryComplianceService = {
  async list(params: PayrollFilterParams = {}): Promise<StatutoryComplianceListResponse> {
    const queryString = buildQueryString(params);
    const response = await fetch(`${API_BASE_URL}/api/payroll/statutory-compliance${queryString}`);
    return handleResponse<StatutoryComplianceListResponse>(response);
  },

  async get(id: number): Promise<StatutoryCompliance> {
    const response = await fetch(`${API_BASE_URL}/api/payroll/statutory-compliance/${id}`);
    return handleResponse<StatutoryCompliance>(response);
  },

  async update(id: number, data: any): Promise<StatutoryCompliance> {
    const response = await fetch(`${API_BASE_URL}/api/payroll/statutory-compliance/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return handleResponse<StatutoryCompliance>(response);
  },
};

// ============ Form 16 Service ============

export const form16Service = {
  async list(params: PayrollFilterParams = {}): Promise<Form16ListResponse> {
    const queryString = buildQueryString(params);
    const response = await fetch(`${API_BASE_URL}/api/payroll/form16${queryString}`);
    return handleResponse<Form16ListResponse>(response);
  },

  async get(id: number): Promise<Form16> {
    const response = await fetch(`${API_BASE_URL}/api/payroll/form16/${id}`);
    return handleResponse<Form16>(response);
  },

  async generate(financialYear: string, employeeIds?: number[]): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/api/payroll/form16/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ financial_year: financialYear, employee_ids: employeeIds }),
    });
    return handleResponse<any>(response);
  },

  async download(id: number): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/api/payroll/form16/${id}/download`);
    return handleResponse<any>(response);
  },
};

// ============ Payment File Service ============

export const paymentFileService = {
  async list(params: PayrollFilterParams = {}): Promise<PaymentFileListResponse> {
    const queryString = buildQueryString(params);
    const response = await fetch(`${API_BASE_URL}/api/payroll/payment-files${queryString}`);
    return handleResponse<PaymentFileListResponse>(response);
  },

  async get(id: number): Promise<PaymentFile> {
    const response = await fetch(`${API_BASE_URL}/api/payroll/payment-files/${id}`);
    return handleResponse<PaymentFile>(response);
  },

  async generate(runId: number, fileFormat: string): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/api/payroll/payment-files/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ payroll_run_id: runId, file_format: fileFormat }),
    });
    return handleResponse<any>(response);
  },

  async download(id: number): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/api/payroll/payment-files/${id}/download`);
    return handleResponse<any>(response);
  },
};

// ============ Dashboard Service ============

export const payrollDashboardService = {
  async getStats(): Promise<PayrollDashboardStats> {
    const response = await fetch(`${API_BASE_URL}/api/payroll/dashboard/stats`);
    return handleResponse<PayrollDashboardStats>(response);
  },

  async getSummary(year: number, month: number): Promise<PayrollSummary> {
    const response = await fetch(`${API_BASE_URL}/api/payroll/summary/${year}/${month}`);
    return handleResponse<PayrollSummary>(response);
  },
};

// ============ Export All Services ============

// Export individual services with PascalCase names for compatibility
export const SalaryComponentService = salaryComponentService;
export const SalaryStructureService = salaryStructureService;
export const EmployeeSalaryService = employeeSalaryService;
export const PayrollRunService = payrollRunService;
export const PayslipService = payslipService;
export const StatutoryComplianceService = statutoryComplianceService;
export const Form16Service = form16Service;
export const PaymentFileService = paymentFileService;
export const PayrollDashboardService = payrollDashboardService;

export const payrollService = {
  salaryComponent: salaryComponentService,
  salaryStructure: salaryStructureService,
  employeeSalary: employeeSalaryService,
  payrollRun: payrollRunService,
  payslip: payslipService,
  statutoryCompliance: statutoryComplianceService,
  form16: form16Service,
  paymentFile: paymentFileService,
  dashboard: payrollDashboardService,
};

export default payrollService;
