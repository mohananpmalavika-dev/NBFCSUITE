import type { JournalStatus } from '@/lib/api';

export interface JournalLine {
  id?: string;
  sequence?: number;
  gl_account_id?: string;
  account_code?: string;
  account_name?: string;
  debit: number;
  credit: number;
  currency?: string;
  branch_id?: string;
  department_id?: string;
  cost_center?: string;
  profit_center?: string;
  project_id?: string;
  employee_id?: string;
  product_id?: string;
  business_unit_id?: string;
  description?: string;
  remarks?: string;
}

export interface ValidationCheck {
  key: string;
  label: string;
  status: 'passed' | 'failed';
  detail?: string | null;
}

export interface JournalValidation {
  valid: boolean;
  errors: string[];
  warnings: string[];
  checks: ValidationCheck[];
  total_debit: number;
  total_credit: number;
  impact: {
    gl_accounts: Array<{
      account_id: string;
      account_code: string;
      account_name: string;
      debit: number;
      credit: number;
      current_balance: number;
      projected_balance: number;
    }>;
    trial_balance: {
      debit_change: number;
      credit_change: number;
      remains_balanced: boolean;
    };
  };
}

export interface JournalDocument {
  id: string;
  batch_id?: string | null;
  journal_no: string;
  posting_date: string;
  entry_date: string;
  voucher_type: string;
  source_module?: string | null;
  source_event?: string | null;
  source_reference?: string | null;
  description: string;
  reference?: string | null;
  status: JournalStatus;
  posting_status: JournalStatus;
  currency: string;
  exchange_rate: number;
  branch_id?: string | null;
  financial_year?: string | null;
  period?: string | null;
  voucher_id?: string | null;
  reversal_of?: string | null;
  created_by?: string | null;
  approved_by?: string | null;
  approved_at?: string | null;
  total_debit: number;
  total_credit: number;
  total_amount: number;
  validation_result?: JournalValidation | null;
  lines: JournalLine[];
  attachments: Array<{
    id: string;
    document_id?: string | null;
    file_name: string;
    uploaded_by?: string | null;
    created_at: string;
  }>;
  approvals: Array<{
    id: string;
    level: string;
    approver: string;
    decision: string;
    remarks?: string | null;
    approved_time: string;
  }>;
}

export interface JournalListResponse {
  items: JournalDocument[];
  total: number;
  status_counts: Partial<Record<JournalStatus, number>>;
}

export interface JournalTemplate {
  id: string;
  template_name: string;
  description?: string | null;
  voucher_type: string;
  currency: string;
  lines: Array<{
    account_code: string;
    direction: 'debit' | 'credit';
    description?: string;
  }>;
}

export interface JournalBatch {
  id: string;
  batch_no: string;
  posting_date: string;
  financial_year: string;
  period: string;
  status: string;
  total_amount: number;
  journal_count: number;
  created_by?: string | null;
}

export interface JournalAuditItem {
  id: string;
  entity_id: string;
  action: string;
  payload?: Record<string, unknown> | null;
  performed_by?: string | null;
  created_at: string;
}

export interface GlAccountOption {
  id: string;
  account_code: string;
  account_name: string;
  account_type: string;
  status?: string;
  posting_allowed?: string;
}
