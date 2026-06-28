'use client';

import { apiClient, type ContraTransferType, type CreditNoteType, type DebitNoteType, type PaymentVoucherCategory, type ReceiptVoucherCategory } from '@/lib/api';
import { useAuth } from '@/lib/auth-context';
import { useCallback, useEffect, useMemo, useState } from 'react';

type TabKey = 'coa' | 'posting' | 'receiptVoucher' | 'paymentVoucher' | 'contraVoucher' | 'creditNote' | 'debitNote' | 'vouchers' | 'statements' | 'dayend';

interface GlAccount {
  id: string;
  account_code: string;
  account_name: string;
  account_type: string;
  parent_account_id?: string | null;
  category?: string | null;
  currency?: string | null;
  branch_id?: string | null;
  branch_specific?: string | null;
  posting_allowed?: string | null;
  status?: string | null;
  financial_year?: string | null;
  balance: number;
}

interface CoaCategorySummary {
  category: string;
  count: number;
  posting_allowed: number;
  control_accounts: number;
  balance: number;
}

interface CoaSummary {
  total_accounts: number;
  posting_accounts: number;
  control_accounts: number;
  categories: CoaCategorySummary[];
}

interface CoaTreeNode {
  id: string;
  account_code: string;
  account_name: string;
  account_type: string;
  category?: string | null;
  posting_allowed?: string | null;
  status?: string | null;
  balance: number;
  children: CoaTreeNode[];
}

interface TrialBalanceRow {
  account_id: string;
  account_code: string;
  account_name: string;
  account_type: string;
  debit: number;
  credit: number;
}

interface VoucherLine {
  gl_account_id: string;
  debit: number;
  credit: number;
  description?: string | null;
  cost_center?: string | null;
  profit_center?: string | null;
}

type PaymentMode = 'cash' | 'cheque' | 'upi' | 'rtgs' | 'neft' | 'imps';

interface Voucher {
  id: string;
  voucher_number: string;
  voucher_type: string;
  description: string;
  reference?: string | null;
  status: string;
  posted_journal_entry_id?: string | null;
  voucher_date?: string;
  payment_mode?: PaymentMode | null;
  payment_reference?: string | null;
  payment_details?: Record<string, unknown> | null;
  payment_category?: PaymentVoucherCategory | null;
  receipt_category?: ReceiptVoucherCategory | null;
  contra_transfer_type?: ContraTransferType | null;
  credit_note_type?: CreditNoteType | null;
  debit_note_type?: DebitNoteType | null;
  payee_name?: string | null;
  payer_name?: string | null;
  customer_name?: string | null;
  customer_id?: string | null;
  source_location?: string | null;
  destination_location?: string | null;
  transfer_reference?: string | null;
  credit_note_reference?: string | null;
  debit_note_reference?: string | null;
  amount?: number | null;
  metadata?: Record<string, unknown> | null;
  lines?: VoucherLine[];
}

interface ReceiptVoucherCategoryOption {
  key: ReceiptVoucherCategory;
  label: string;
  credit_account_code: string;
  description: string;
}

interface ReceiptVoucherOptions {
  categories: ReceiptVoucherCategoryOption[];
  payment_modes: PaymentMode[];
}

interface PaymentVoucherCategoryOption {
  key: PaymentVoucherCategory;
  label: string;
  debit_account_code: string;
  description: string;
}

interface ContraTransferOption {
  key: ContraTransferType;
  label: string;
  debit_account_code: string;
  credit_account_code: string;
  source_label: string;
  destination_label: string;
  description: string;
}

interface ContraVoucherOptions {
  transfer_types: ContraTransferOption[];
}

interface CreditNoteTypeOption {
  key: CreditNoteType;
  label: string;
  debit_account_code: string;
  credit_account_code: string;
  description: string;
}

interface CreditNoteOptions {
  credit_note_types: CreditNoteTypeOption[];
}

interface DebitNoteTypeOption {
  key: DebitNoteType;
  label: string;
  debit_account_code: string;
  credit_account_code: string;
  description: string;
}

interface DebitNoteOptions {
  debit_note_types: DebitNoteTypeOption[];
}

interface LedgerRow {
  gl_account_id: string;
  gl_number?: string | null;
  account_code?: string | null;
  account_name?: string | null;
  branch?: string | null;
  branch_id?: string | null;
  currency: string;
  financial_year: string;
  opening_balance: number;
  debit: number;
  credit: number;
  balance: number;
  closing_balance: number;
}

interface SubLedgerSummaryRow {
  source_module: string;
  ledger_name: string;
  transaction_count: number;
  total_amount: number;
  last_entry_at?: string | null;
  rollup_to: string;
}

interface PostingRuleLineForm {
  account_code: string;
  direction: 'debit' | 'credit';
  description: string;
}

interface PostingRuleForm {
  source_module: string;
  source_event: string;
  description: string;
  lines: PostingRuleLineForm[];
}

interface Dashboard {
  chart_of_accounts: number;
  posting_rules: number;
  journal_entries: number;
  subledger_entries: number;
  pending_vouchers: number;
  trial_balance: {
    total_debit: number;
    total_credit: number;
    is_balanced: boolean;
  };
}

const tabs: Array<{ key: TabKey; label: string }> = [
  { key: 'coa', label: 'COA' },
  { key: 'posting', label: 'Posting Engine' },
  { key: 'receiptVoucher', label: 'Module 7 Receipt' },
  { key: 'paymentVoucher', label: 'Module 8 Payment' },
  { key: 'contraVoucher', label: 'Module 9 Contra' },
  { key: 'creditNote', label: 'Module 10 Credit' },
  { key: 'debitNote', label: 'Module 11 Debit' },
  { key: 'vouchers', label: 'Vouchers' },
  { key: 'statements', label: 'Statements' },
  { key: 'dayend', label: 'Day End' },
];

const defaultReceiptVoucherOptions: ReceiptVoucherOptions = {
  categories: [
    { key: 'customer_payments', label: 'Customer payments', credit_account_code: '1200_LOAN_RECEIVABLE', description: 'Customer payment receipt' },
  ],
  payment_modes: ['cash', 'cheque', 'upi', 'rtgs', 'neft', 'imps'],
};

const defaultPaymentVoucherCategories: PaymentVoucherCategoryOption[] = [
  { key: 'vendor_payments', label: 'Vendor payments', debit_account_code: '2400_VENDOR_PAYABLE', description: 'Vendor payment' },
  { key: 'salary', label: 'Salary', debit_account_code: '5210_SALARY_EXPENSE', description: 'Salary payment' },
  { key: 'rent', label: 'Rent', debit_account_code: '5110_RENT_EXPENSE', description: 'Rent payment' },
  { key: 'electricity', label: 'Electricity', debit_account_code: '5120_ELECTRICITY_EXPENSE', description: 'Electricity payment' },
  { key: 'tax', label: 'Tax', debit_account_code: '2300_GST_PAYABLE', description: 'Tax payment' },
  { key: 'insurance', label: 'Insurance', debit_account_code: '5130_INSURANCE_EXPENSE', description: 'Insurance payment' },
];

const defaultContraVoucherOptions: ContraVoucherOptions = {
  transfer_types: [
    { key: 'cash_to_bank', label: 'Cash to Bank', debit_account_code: '1120_BANK', credit_account_code: '1000_CASH', source_label: 'Cash', destination_label: 'Bank', description: 'Cash deposited to bank' },
    { key: 'bank_to_cash', label: 'Bank to Cash', debit_account_code: '1000_CASH', credit_account_code: '1120_BANK', source_label: 'Bank', destination_label: 'Cash', description: 'Cash withdrawn from bank' },
    { key: 'vault_to_branch', label: 'Vault to Branch', debit_account_code: '1110_BRANCH_CASH', credit_account_code: '1130_VAULT_CASH', source_label: 'Vault', destination_label: 'Branch', description: 'Cash moved from vault to branch' },
    { key: 'branch_to_treasury', label: 'Branch to Treasury', debit_account_code: '1500_TREASURY', credit_account_code: '1110_BRANCH_CASH', source_label: 'Branch', destination_label: 'Treasury', description: 'Cash moved from branch to treasury' },
  ],
};

const defaultCreditNoteOptions: CreditNoteOptions = {
  credit_note_types: [
    { key: 'interest_reversal', label: 'Interest Reversal', debit_account_code: '4110_INTEREST_REVERSAL', credit_account_code: '1200_LOAN_RECEIVABLE', description: 'Interest reversal credit note' },
    { key: 'refund', label: 'Refund', debit_account_code: '5300_REFUND_EXPENSE', credit_account_code: '2500_CUSTOMER_CREDIT_PAYABLE', description: 'Customer refund credit note' },
    { key: 'adjustment', label: 'Adjustment', debit_account_code: '5400_ADJUSTMENT_EXPENSE', credit_account_code: '1200_LOAN_RECEIVABLE', description: 'Customer account adjustment credit note' },
    { key: 'discount', label: 'Discount', debit_account_code: '5500_DISCOUNT_ALLOWED', credit_account_code: '1200_LOAN_RECEIVABLE', description: 'Discount allowed credit note' },
  ],
};

const defaultDebitNoteOptions: DebitNoteOptions = {
  debit_note_types: [
    { key: 'penalty', label: 'Penalty', debit_account_code: '1200_LOAN_RECEIVABLE', credit_account_code: '4120_PENALTY_INCOME', description: 'Penalty debit note' },
    { key: 'charges', label: 'Charges', debit_account_code: '1200_LOAN_RECEIVABLE', credit_account_code: '4130_CHARGES_INCOME', description: 'Charges debit note' },
    { key: 'recovery', label: 'Recovery', debit_account_code: '1200_LOAN_RECEIVABLE', credit_account_code: '4140_RECOVERY_INCOME', description: 'Recovery debit note' },
    { key: 'tax_adjustment', label: 'Tax Adjustment', debit_account_code: '1200_LOAN_RECEIVABLE', credit_account_code: '2300_GST_PAYABLE', description: 'Tax adjustment debit note' },
  ],
};

function money(value: number | undefined) {
  return Number(value || 0).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function errorText(error: unknown, fallback: string) {
  const candidate = error as { response?: { data?: { detail?: string } } };
  return candidate?.response?.data?.detail || fallback;
}

function accountLabel(account: GlAccount) {
  return `${account.account_code} - ${account.account_name}`;
}

function CoaTreeRows({ nodes, depth = 0 }: { nodes: CoaTreeNode[]; depth?: number }) {
  return (
    <>
      {nodes.map((node) => (
        <div key={node.id}>
          <div
            className="grid grid-cols-[1fr_auto_auto] gap-3 border-b border-slate-100 py-2 text-sm"
            style={{ paddingLeft: `${depth * 16}px` }}
          >
            <div>
              <p className="font-medium text-slate-900">{node.account_code} - {node.account_name}</p>
              <p className="text-xs text-slate-500">{node.category || node.account_type}</p>
            </div>
            <span className="text-xs text-slate-500">{node.posting_allowed === 'false' ? 'Control' : 'Posting'}</span>
            <span className="text-right text-slate-700">{money(node.balance)}</span>
          </div>
          {node.children.length > 0 && <CoaTreeRows nodes={node.children} depth={depth + 1} />}
        </div>
      ))}
    </>
  );
}

export default function AccountingPage() {
  const { user, token, isLoading } = useAuth();
  const [activeTab, setActiveTab] = useState<TabKey>('coa');
  const [message, setMessage] = useState('');
  const [busyAction, setBusyAction] = useState('');
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [accounts, setAccounts] = useState<GlAccount[]>([]);
  const [coaSummary, setCoaSummary] = useState<CoaSummary | null>(null);
  const [coaTree, setCoaTree] = useState<CoaTreeNode[]>([]);
  const [trialRows, setTrialRows] = useState<TrialBalanceRow[]>([]);
  const [ledgerRows, setLedgerRows] = useState<LedgerRow[]>([]);
  const [subLedgerSummaryRows, setSubLedgerSummaryRows] = useState<SubLedgerSummaryRow[]>([]);
  const [vouchers, setVouchers] = useState<Voucher[]>([]);
  const [receiptVoucherOptions, setReceiptVoucherOptions] = useState<ReceiptVoucherOptions>(defaultReceiptVoucherOptions);
  const [paymentVoucherCategories, setPaymentVoucherCategories] = useState<PaymentVoucherCategoryOption[]>(defaultPaymentVoucherCategories);
  const [contraVoucherOptions, setContraVoucherOptions] = useState<ContraVoucherOptions>(defaultContraVoucherOptions);
  const [creditNoteOptions, setCreditNoteOptions] = useState<CreditNoteOptions>(defaultCreditNoteOptions);
  const [debitNoteOptions, setDebitNoteOptions] = useState<DebitNoteOptions>(defaultDebitNoteOptions);
  const [dayEndRows, setDayEndRows] = useState<Array<{ id: string; business_date: string; status: string; is_balanced: string }>>([]);
  const [postingPipeline, setPostingPipeline] = useState<Record<string, any> | null>(null);

  const tenantId = user?.tenant_id || user?.branch_id || user?.organization_id || user?.id || 'default';

  const [accountForm, setAccountForm] = useState({
    account_code: '',
    account_name: '',
    account_type: 'asset',
    parent_account_id: '',
    category: 'Assets',
    currency: 'INR',
    branch_id: '',
    branch_specific: 'false',
    posting_allowed: 'true',
    status: 'active',
    financial_year: '2026-27',
  });
  const [ruleForm, setRuleForm] = useState<PostingRuleForm>({
    source_module: 'loans',
    source_event: 'disbursement',
    description: '',
    lines: [
      { account_code: '', direction: 'debit', description: '' },
      { account_code: '', direction: 'credit', description: '' },
    ],
  });
  const [postingForm, setPostingForm] = useState({
    source_module: 'manual',
    source_event: 'adjustment',
    source_reference: '',
    description: '',
    debit_account_id: '',
    credit_account_id: '',
    amount: '0',
    branch_id: '',
  });
  const [postingRules, setPostingRules] = useState<any[]>([]);

  const canCreateRule = ruleForm.lines.some((line) => line.account_code) &&
    ruleForm.lines.some((line) => line.direction === 'debit' && line.account_code) &&
    ruleForm.lines.some((line) => line.direction === 'credit' && line.account_code);
  const [voucherForm, setVoucherForm] = useState({
    voucher_type: 'journal',
    description: '',
    reference: '',
    voucher_date: new Date().toISOString().slice(0, 10),
    branch_id: '',
    payment_mode: 'cash' as PaymentMode,
    payment_reference: '',
    payment_details: { note: '' },
    lines: [
      { gl_account_id: '', debit: 0, credit: 0, description: '' },
      { gl_account_id: '', debit: 0, credit: 0, description: '' },
    ],
  });
  const [receiptVoucherForm, setReceiptVoucherForm] = useState({
    receipt_category: 'customer_payments' as ReceiptVoucherCategory,
    amount: '',
    payer_name: '',
    customer_id: '',
    description: '',
    reference: '',
    voucher_date: new Date().toISOString().slice(0, 10),
    branch_id: '',
    payment_mode: 'upi' as PaymentMode,
    payment_reference: '',
    payment_note: '',
    debit_account_id: '',
    credit_account_id: '',
    cost_center: '',
    profit_center: '',
  });
  const [paymentVoucherForm, setPaymentVoucherForm] = useState({
    payment_category: 'vendor_payments' as PaymentVoucherCategory,
    amount: '',
    payee_name: '',
    description: '',
    reference: '',
    voucher_date: new Date().toISOString().slice(0, 10),
    branch_id: '',
    payment_mode: 'neft' as PaymentMode,
    payment_reference: '',
    payment_note: '',
    debit_account_id: '',
    credit_account_id: '',
    cost_center: '',
    profit_center: '',
  });
  const [contraVoucherForm, setContraVoucherForm] = useState({
    transfer_type: 'cash_to_bank' as ContraTransferType,
    amount: '',
    description: '',
    reference: '',
    transfer_reference: '',
    voucher_date: new Date().toISOString().slice(0, 10),
    branch_id: '',
    source_location: '',
    destination_location: '',
    transfer_note: '',
    debit_account_id: '',
    credit_account_id: '',
    cost_center: '',
    profit_center: '',
  });
  const [creditNoteForm, setCreditNoteForm] = useState({
    credit_note_type: 'interest_reversal' as CreditNoteType,
    amount: '',
    customer_name: '',
    customer_id: '',
    description: '',
    reference: '',
    credit_note_reference: '',
    voucher_date: new Date().toISOString().slice(0, 10),
    branch_id: '',
    credit_note_note: '',
    debit_account_id: '',
    credit_account_id: '',
    cost_center: '',
    profit_center: '',
  });
  const [debitNoteForm, setDebitNoteForm] = useState({
    debit_note_type: 'penalty' as DebitNoteType,
    amount: '',
    customer_name: '',
    customer_id: '',
    description: '',
    reference: '',
    debit_note_reference: '',
    voucher_date: new Date().toISOString().slice(0, 10),
    branch_id: '',
    debit_note_note: '',
    debit_account_id: '',
    credit_account_id: '',
    cost_center: '',
    profit_center: '',
  });
  const [dayEndForm, setDayEndForm] = useState({
    business_date: new Date().toISOString().slice(0, 10),
    branch_id: '',
  });

  const selectableAccounts = useMemo(
    () => accounts.filter((account) => String(account.posting_allowed || 'true').toLowerCase() !== 'false'),
    [accounts],
  );
  const receiptVouchers = useMemo(
    () => vouchers.filter((voucher) => voucher.voucher_type === 'receipt' && voucher.receipt_category),
    [vouchers],
  );
  const paymentVouchers = useMemo(
    () => vouchers.filter((voucher) => voucher.voucher_type === 'payment' && voucher.payment_category),
    [vouchers],
  );
  const contraVouchers = useMemo(
    () => vouchers.filter((voucher) => voucher.voucher_type === 'contra' && voucher.contra_transfer_type),
    [vouchers],
  );
  const creditNotes = useMemo(
    () => vouchers.filter((voucher) => voucher.voucher_type === 'credit_note' && voucher.credit_note_type),
    [vouchers],
  );
  const debitNotes = useMemo(
    () => vouchers.filter((voucher) => voucher.voucher_type === 'debit_note' && voucher.debit_note_type),
    [vouchers],
  );

  const refresh = useCallback(async () => {
    if (!token || !tenantId) return;
    try {
      const [dashboardRes, accountsRes, trialRes, ledgerRes, subLedgerRes, vouchersRes, dayEndRes, postingRulesRes, paymentCategoriesRes, receiptOptionsRes, contraOptionsRes, creditNoteOptionsRes, debitNoteOptionsRes] = await Promise.all([
        apiClient.getAccountingDashboard(tenantId),
        apiClient.getGlAccounts(tenantId),
        apiClient.getTrialBalance(tenantId),
        apiClient.getGlLedger(tenantId),
        apiClient.getSubLedgerSummary(tenantId),
        apiClient.getVouchers(tenantId),
        apiClient.getDayEndCloses(tenantId),
        apiClient.getPostingRules(tenantId),
        apiClient.getPaymentVoucherCategories(),
        apiClient.getReceiptVoucherOptions(),
        apiClient.getContraVoucherOptions(),
        apiClient.getCreditNoteOptions(),
        apiClient.getDebitNoteOptions(),
      ]);
      setDashboard(dashboardRes.data);
      setAccounts(accountsRes.data || []);
      const [summaryRes, hierarchyRes] = await Promise.all([
        apiClient.getGlAccountSummary(tenantId),
        apiClient.getGlAccountHierarchy(tenantId),
      ]);
      setCoaSummary(summaryRes.data || null);
      setCoaTree(hierarchyRes.data.items || []);
      setTrialRows(trialRes.data.rows || []);
      setLedgerRows(ledgerRes.data.items || []);
      setSubLedgerSummaryRows(subLedgerRes.data.items || []);
      setVouchers(vouchersRes.data.items || []);
      setDayEndRows(dayEndRes.data || []);
      setPostingRules(postingRulesRes.data || []);
      setPaymentVoucherCategories(paymentCategoriesRes.data.items || defaultPaymentVoucherCategories);
      setReceiptVoucherOptions(receiptOptionsRes.data || defaultReceiptVoucherOptions);
      setContraVoucherOptions(contraOptionsRes.data || defaultContraVoucherOptions);
      setCreditNoteOptions(creditNoteOptionsRes.data || defaultCreditNoteOptions);
      setDebitNoteOptions(debitNoteOptionsRes.data || defaultDebitNoteOptions);
    } catch (error) {
      setMessage(errorText(error, 'Unable to load accounting workspace.'));
    }
  }, [tenantId, token]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  async function runAction(name: string, action: () => Promise<unknown>, success: string) {
    setBusyAction(name);
    setMessage('');
    try {
      await action();
      setMessage(success);
      await refresh();
    } catch (error) {
      setMessage(errorText(error, `${success} failed.`));
    } finally {
      setBusyAction('');
    }
  }

  const amount = Number(postingForm.amount || 0);
  const voucherTotalDebit = voucherForm.lines.reduce((sum, line) => sum + Number(line.debit || 0), 0);
  const voucherTotalCredit = voucherForm.lines.reduce((sum, line) => sum + Number(line.credit || 0), 0);
  const voucherLinesComplete = voucherForm.lines.every((line) => line.gl_account_id && (line.debit > 0 || line.credit > 0));
  const voucherBalanced = voucherTotalDebit === voucherTotalCredit && voucherTotalDebit > 0;
  const isReceipt = voucherForm.voucher_type === 'receipt';
  const isPaymentLikeVoucher = isReceipt || voucherForm.voucher_type === 'payment';
  const paymentModeValid = !isPaymentLikeVoucher || !!voucherForm.payment_mode;
  const paymentReferenceValid = !isPaymentLikeVoucher || voucherForm.payment_mode === 'cash' || !!voucherForm.payment_reference;
  const receiptVoucherAmount = Number(receiptVoucherForm.amount || 0);
  const receiptVoucherCategory = receiptVoucherOptions.categories.find((category) => category.key === receiptVoucherForm.receipt_category) || receiptVoucherOptions.categories[0];
  const receiptVoucherNeedsReference = receiptVoucherForm.payment_mode !== 'cash';
  const canCreateReceiptVoucher = receiptVoucherAmount > 0 &&
    receiptVoucherForm.payer_name.trim() &&
    receiptVoucherForm.receipt_category &&
    (!receiptVoucherNeedsReference || receiptVoucherForm.payment_reference.trim());
  const paymentVoucherAmount = Number(paymentVoucherForm.amount || 0);
  const paymentVoucherCategory = paymentVoucherCategories.find((category) => category.key === paymentVoucherForm.payment_category) || paymentVoucherCategories[0];
  const paymentVoucherNeedsReference = paymentVoucherForm.payment_mode !== 'cash';
  const canCreatePaymentVoucher = paymentVoucherAmount > 0 &&
    paymentVoucherForm.payee_name.trim() &&
    paymentVoucherForm.payment_category &&
    (!paymentVoucherNeedsReference || paymentVoucherForm.payment_reference.trim());
  const contraVoucherAmount = Number(contraVoucherForm.amount || 0);
  const contraTransfer = contraVoucherOptions.transfer_types.find((transfer) => transfer.key === contraVoucherForm.transfer_type) || contraVoucherOptions.transfer_types[0];
  const canCreateContraVoucher = contraVoucherAmount > 0 && contraVoucherForm.transfer_type;
  const creditNoteAmount = Number(creditNoteForm.amount || 0);
  const creditNoteType = creditNoteOptions.credit_note_types.find((noteType) => noteType.key === creditNoteForm.credit_note_type) || creditNoteOptions.credit_note_types[0];
  const canCreateCreditNote = creditNoteAmount > 0 && creditNoteForm.credit_note_type && creditNoteForm.customer_name.trim();
  const debitNoteAmount = Number(debitNoteForm.amount || 0);
  const debitNoteType = debitNoteOptions.debit_note_types.find((noteType) => noteType.key === debitNoteForm.debit_note_type) || debitNoteOptions.debit_note_types[0];
  const canCreateDebitNote = debitNoteAmount > 0 && debitNoteForm.debit_note_type && debitNoteForm.customer_name.trim();
  const canPost = postingForm.debit_account_id && postingForm.credit_account_id && amount > 0;
  const canCreateVoucher = voucherForm.description && voucherBalanced && voucherLinesComplete && paymentModeValid && paymentReferenceValid;

  if (isLoading || !token) {
    return <div className="p-8 text-center">Loading accounting data...</div>;
  }

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-6">
      <div className="mx-auto max-w-7xl space-y-6">
        <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-end">
            <div>
              <p className="text-xs font-semibold uppercase text-blue-700">Enterprise Accounting Suite</p>
              <h1 className="mt-1 text-3xl font-bold text-slate-950">Accounting & General Ledger</h1>
              <p className="mt-2 max-w-3xl text-sm text-slate-600">
                Central posting engine, chart of accounts, vouchers, sub-ledger visibility, financial statements,
                and day-end controls for the tenant ledger.
              </p>
            </div>
            <button
              type="button"
              onClick={refresh}
              className="h-10 rounded-md border border-slate-300 bg-white px-4 text-sm font-semibold text-slate-800 hover:border-blue-400"
            >
              Refresh
            </button>
          </div>
        </section>

        {message && (
          <div className="rounded-md border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-900">{message}</div>
        )}

        <section className="grid gap-3 sm:grid-cols-2 lg:grid-cols-6">
          {[
            ['COA', dashboard?.chart_of_accounts],
            ['Posting Rules', dashboard?.posting_rules],
            ['Journals', dashboard?.journal_entries],
            ['Sub Ledger', dashboard?.subledger_entries],
            ['Pending Vouchers', dashboard?.pending_vouchers],
            ['Balanced', dashboard?.trial_balance?.is_balanced ? 'Yes' : 'No'],
          ].map(([label, value]) => (
            <div key={String(label)} className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
              <dt className="text-xs font-semibold uppercase text-slate-500">{label}</dt>
              <dd className="mt-2 text-2xl font-bold text-slate-950">{value ?? 0}</dd>
            </div>
          ))}
        </section>

        <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <div className="flex flex-wrap gap-2 border-b border-slate-200 pb-3">
            {tabs.map((tab) => (
              <button
                key={tab.key}
                type="button"
                onClick={() => setActiveTab(tab.key)}
                className={`h-9 rounded-md px-3 text-sm font-semibold ${
                  activeTab === tab.key ? 'bg-blue-600 text-white' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {activeTab === 'coa' && (
            <div className="mt-5 grid gap-6 xl:grid-cols-[0.8fr_1.2fr]">
              <form
                className="grid gap-3"
                onSubmit={(event) => {
                  event.preventDefault();
                  runAction(
                    'account',
                    async () => {
                      await apiClient.createGlAccount({
                        tenant_id: tenantId,
                        ...accountForm,
                        parent_account_id: accountForm.parent_account_id || undefined,
                        branch_id: accountForm.branch_id || undefined,
                      });
                      setAccountForm({ ...accountForm, account_code: '', account_name: '', parent_account_id: '', branch_id: '' });
                    },
                    'GL account created.',
                  );
                }}
              >
                <h2 className="text-lg font-semibold text-slate-950">Chart of Accounts</h2>
                <button
                  type="button"
                  disabled={!!busyAction}
                  onClick={() =>
                    runAction(
                      'seed-coa',
                      () => apiClient.seedDefaultGlAccounts({ tenant_id: tenantId, currency: accountForm.currency, financial_year: accountForm.financial_year }),
                      'Default NBFC COA seeded.',
                    )
                  }
                  className="h-10 rounded-md border border-blue-300 bg-blue-50 px-4 text-sm font-semibold text-blue-800 disabled:opacity-50"
                >
                  {busyAction === 'seed-coa' ? 'Seeding...' : 'Seed NBFC COA'}
                </button>
                <input className="h-10 rounded-md border border-slate-300 px-3 text-sm" placeholder="GL Code" value={accountForm.account_code} onChange={(e) => setAccountForm({ ...accountForm, account_code: e.target.value })} />
                <input className="h-10 rounded-md border border-slate-300 px-3 text-sm" placeholder="GL Name" value={accountForm.account_name} onChange={(e) => setAccountForm({ ...accountForm, account_name: e.target.value })} />
                <select className="h-10 rounded-md border border-slate-300 px-3 text-sm" value={accountForm.parent_account_id} onChange={(e) => setAccountForm({ ...accountForm, parent_account_id: e.target.value })}>
                  <option value="">No parent GL</option>
                  {accounts.map((account) => (
                    <option key={account.id} value={account.id}>{accountLabel(account)}</option>
                  ))}
                </select>
                <div className="grid gap-3 sm:grid-cols-2">
                  <select className="h-10 rounded-md border border-slate-300 px-3 text-sm" value={accountForm.account_type} onChange={(e) => setAccountForm({ ...accountForm, account_type: e.target.value, category: e.target.options[e.target.selectedIndex].text })}>
                    <option value="asset">Assets</option>
                    <option value="liability">Liabilities</option>
                    <option value="revenue">Income</option>
                    <option value="expense">Expenses</option>
                    <option value="equity">Capital</option>
                    <option value="off_balance">Off Balance Sheet</option>
                    <option value="memo">Memo Accounts</option>
                  </select>
                  <select className="h-10 rounded-md border border-slate-300 px-3 text-sm" value={accountForm.posting_allowed} onChange={(e) => setAccountForm({ ...accountForm, posting_allowed: e.target.value })}>
                    <option value="true">Posting Allowed</option>
                    <option value="false">Control Only</option>
                  </select>
                </div>
                <div className="grid gap-3 sm:grid-cols-2">
                  <input className="h-10 rounded-md border border-slate-300 px-3 text-sm" placeholder="Currency" value={accountForm.currency} onChange={(e) => setAccountForm({ ...accountForm, currency: e.target.value })} />
                  <input className="h-10 rounded-md border border-slate-300 px-3 text-sm" placeholder="Optional Branch ID" value={accountForm.branch_id} onChange={(e) => setAccountForm({ ...accountForm, branch_id: e.target.value })} />
                </div>
                <button disabled={!!busyAction || !accountForm.account_code || !accountForm.account_name} className="h-10 rounded-md bg-blue-600 px-4 text-sm font-semibold text-white disabled:opacity-50">
                  {busyAction === 'account' ? 'Saving...' : 'Create GL Account'}
                </button>
              </form>

              <div className="space-y-5">
                <div className="grid gap-3 sm:grid-cols-3">
                  <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                    <dt className="text-xs font-semibold uppercase text-slate-500">Total GLs</dt>
                    <dd className="mt-1 text-2xl font-bold text-slate-950">{coaSummary?.total_accounts || 0}</dd>
                  </div>
                  <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                    <dt className="text-xs font-semibold uppercase text-slate-500">Posting</dt>
                    <dd className="mt-1 text-2xl font-bold text-slate-950">{coaSummary?.posting_accounts || 0}</dd>
                  </div>
                  <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                    <dt className="text-xs font-semibold uppercase text-slate-500">Control</dt>
                    <dd className="mt-1 text-2xl font-bold text-slate-950">{coaSummary?.control_accounts || 0}</dd>
                  </div>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full min-w-[620px] text-sm">
                    <thead>
                      <tr className="border-b border-slate-200 text-left text-slate-500">
                        <th className="px-3 py-2">Category</th>
                        <th className="px-3 py-2 text-right">Accounts</th>
                        <th className="px-3 py-2 text-right">Posting</th>
                        <th className="px-3 py-2 text-right">Balance</th>
                      </tr>
                    </thead>
                    <tbody>
                      {(coaSummary?.categories || []).map((row) => (
                        <tr key={row.category} className="border-b border-slate-100">
                          <td className="px-3 py-2 font-medium text-slate-900">{row.category}</td>
                          <td className="px-3 py-2 text-right text-slate-700">{row.count}</td>
                          <td className="px-3 py-2 text-right text-slate-700">{row.posting_allowed}</td>
                          <td className="px-3 py-2 text-right text-slate-900">{money(row.balance)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                <div>
                  <h3 className="text-base font-semibold text-slate-950">COA Hierarchy</h3>
                  <div className="mt-3 max-h-[420px] overflow-auto rounded-lg border border-slate-200 px-3">
                    {coaTree.length === 0 ? (
                      <p className="py-4 text-sm text-slate-600">No chart of accounts hierarchy available.</p>
                    ) : (
                      <CoaTreeRows nodes={coaTree} />
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'posting' && (
            <div className="mt-5 grid gap-6 lg:grid-cols-2">
              <form
                className="grid gap-3"
                onSubmit={(event) => {
                  event.preventDefault();
                  runAction(
                    'rule',
                    async () => {
                      await apiClient.createPostingRule({ tenant_id: tenantId, ...ruleForm });
                      setRuleForm({
                        source_module: ruleForm.source_module,
                        source_event: ruleForm.source_event,
                        description: '',
                        lines: [
                          { account_code: '', direction: 'debit', description: '' },
                          { account_code: '', direction: 'credit', description: '' },
                        ],
                      });
                    },
                    'Posting rule created.',
                  );
                }}
              >
                <h2 className="text-lg font-semibold text-slate-950">Posting Rule</h2>
                <div className="grid gap-3 sm:grid-cols-2">
                  <input className="h-10 rounded-md border border-slate-300 px-3 text-sm" value={ruleForm.source_module} onChange={(e) => setRuleForm({ ...ruleForm, source_module: e.target.value })} />
                  <input className="h-10 rounded-md border border-slate-300 px-3 text-sm" value={ruleForm.source_event} onChange={(e) => setRuleForm({ ...ruleForm, source_event: e.target.value })} />
                </div>
                <input className="h-10 rounded-md border border-slate-300 px-3 text-sm" placeholder="Description" value={ruleForm.description} onChange={(e) => setRuleForm({ ...ruleForm, description: e.target.value })} />
                <div className="space-y-3">
                  {ruleForm.lines.map((line, index) => (
                    <div key={index} className="grid gap-3 sm:grid-cols-4 items-end">
                      <select
                        className="h-10 rounded-md border border-slate-300 px-3 text-sm"
                        value={line.direction}
                        onChange={(e) => {
                          const direction = e.target.value as 'debit' | 'credit';
                          setRuleForm({
                            ...ruleForm,
                            lines: ruleForm.lines.map((item, idx) =>
                              idx === index ? { ...item, direction } : item,
                            ),
                          });
                        }}
                      >
                        <option value="debit">Debit</option>
                        <option value="credit">Credit</option>
                      </select>
                      <select
                        className="h-10 rounded-md border border-slate-300 px-3 text-sm"
                        value={line.account_code}
                        onChange={(e) => {
                          const account_code = e.target.value;
                          setRuleForm({
                            ...ruleForm,
                            lines: ruleForm.lines.map((item, idx) =>
                              idx === index ? { ...item, account_code } : item,
                            ),
                          });
                        }}
                      >
                        <option value="">Select GL account</option>
                        {selectableAccounts.map((account) => (
                          <option key={account.id} value={account.account_code}>
                            {accountLabel(account)}
                          </option>
                        ))}
                      </select>
                      <input
                        className="h-10 rounded-md border border-slate-300 px-3 text-sm"
                        placeholder="Line description"
                        value={line.description}
                        onChange={(e) => {
                          const description = e.target.value;
                          setRuleForm({
                            ...ruleForm,
                            lines: ruleForm.lines.map((item, idx) =>
                              idx === index ? { ...item, description } : item,
                            ),
                          });
                        }}
                      />
                      <button
                        type="button"
                        className="h-10 rounded-md border border-slate-300 bg-slate-100 px-3 text-sm text-slate-700 hover:bg-slate-200"
                        onClick={() => setRuleForm({
                          ...ruleForm,
                          lines: ruleForm.lines.filter((_, idx) => idx !== index),
                        })}
                        disabled={ruleForm.lines.length <= 1}
                      >
                        Remove
                      </button>
                    </div>
                  ))}
                </div>
                <button
                  type="button"
                  onClick={() => setRuleForm({
                    ...ruleForm,
                    lines: [...ruleForm.lines, { account_code: '', direction: 'debit', description: '' }],
                  })}
                  className="h-10 rounded-md border border-slate-300 bg-white px-3 text-sm font-semibold text-slate-700 hover:bg-slate-50"
                >
                  Add posting line
                </button>
                <button
                  disabled={!!busyAction || !canCreateRule}
                  className="h-10 rounded-md bg-blue-600 px-4 text-sm font-semibold text-white disabled:opacity-50"
                >
                  {busyAction === 'rule' ? 'Saving...' : 'Create Posting Rule'}
                </button>
              </form>

              <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
                <h3 className="text-base font-semibold text-slate-950">Existing Posting Rules</h3>
                <div className="mt-3 space-y-3">
                  {postingRules.length === 0 ? (
                    <p className="text-sm text-slate-600">No posting rules defined yet.</p>
                  ) : (
                    postingRules.map((rule) => (
                      <div key={rule.id} className="rounded-md border border-slate-200 bg-white p-3 text-sm">
                        <p className="font-semibold text-slate-900">{rule.source_module} / {rule.source_event}</p>
                        <p className="text-slate-500">{rule.description || 'No description'}</p>
                        <div className="mt-2 grid gap-2 sm:grid-cols-3">
                          {rule.lines?.map((line: any, index: number) => (
                            <div key={index} className="rounded border border-slate-100 bg-slate-50 p-2 text-slate-700">
                              <p className="text-xs uppercase text-slate-500">{line.direction}</p>
                              <p>{line.account_code}</p>
                              {line.description && <p className="text-xs text-slate-500">{line.description}</p>}
                            </div>
                          ))}
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>

              <form
                className="grid gap-3"
                onSubmit={(event) => {
                  event.preventDefault();
                  runAction(
                    'posting',
                    async () => {
                      const sourceReference = postingForm.source_reference || `MAN-${Date.now()}`;
                      const lines = [
                        { gl_account_id: postingForm.debit_account_id, debit: amount, credit: 0, branch_id: postingForm.branch_id || undefined },
                        { gl_account_id: postingForm.credit_account_id, debit: 0, credit: amount, branch_id: postingForm.branch_id || undefined },
                      ];
                      const validationResponse = await apiClient.validateAccountingPosting(tenantId, lines, {
                        source_module: postingForm.source_module,
                        source_event: postingForm.source_event,
                        source_reference: sourceReference,
                      });
                      if (!validationResponse.data?.is_balanced) {
                        throw new Error('Posting must balance before it can be posted.');
                      }
                      const postingResponse = await apiClient.postAccountingEngine({
                        tenant_id: tenantId,
                        source_module: postingForm.source_module,
                        source_event: postingForm.source_event,
                        source_reference: sourceReference,
                        description: postingForm.description,
                        branch_id: postingForm.branch_id || undefined,
                        lines,
                      });
                      setPostingPipeline(postingResponse.data?.pipeline || null);
                      setPostingForm({ ...postingForm, source_reference: '', description: '', amount: '0' });
                    },
                    'Transaction posted through the validation, entry, GL, sub-ledger, and audit pipeline.',
                  );
                }}
              >
                <h2 className="text-lg font-semibold text-slate-950">Transaction Engine</h2>
                <div className="grid gap-3 sm:grid-cols-2">
                  <input className="h-10 rounded-md border border-slate-300 px-3 text-sm" value={postingForm.source_module} onChange={(e) => setPostingForm({ ...postingForm, source_module: e.target.value })} />
                  <input className="h-10 rounded-md border border-slate-300 px-3 text-sm" value={postingForm.source_event} onChange={(e) => setPostingForm({ ...postingForm, source_event: e.target.value })} />
                </div>
                <input className="h-10 rounded-md border border-slate-300 px-3 text-sm" placeholder="Reference" value={postingForm.source_reference} onChange={(e) => setPostingForm({ ...postingForm, source_reference: e.target.value })} />
                <div className="grid gap-3 sm:grid-cols-2">
                  <select className="h-10 rounded-md border border-slate-300 px-3 text-sm" value={postingForm.debit_account_id} onChange={(e) => setPostingForm({ ...postingForm, debit_account_id: e.target.value })}>
                    <option value="">Debit account</option>
                    {selectableAccounts.map((account) => <option key={account.id} value={account.id}>{accountLabel(account)}</option>)}
                  </select>
                  <select className="h-10 rounded-md border border-slate-300 px-3 text-sm" value={postingForm.credit_account_id} onChange={(e) => setPostingForm({ ...postingForm, credit_account_id: e.target.value })}>
                    <option value="">Credit account</option>
                    {selectableAccounts.map((account) => <option key={account.id} value={account.id}>{accountLabel(account)}</option>)}
                  </select>
                </div>
                <input className="h-10 rounded-md border border-slate-300 px-3 text-sm" type="number" value={postingForm.amount} onChange={(e) => setPostingForm({ ...postingForm, amount: e.target.value })} />
                <button disabled={!!busyAction || !canPost} className="h-10 rounded-md bg-blue-600 px-4 text-sm font-semibold text-white disabled:opacity-50">
                  {busyAction === 'posting' ? 'Posting...' : 'Validate & Post'}
                </button>
              </form>
              <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
                <h3 className="text-sm font-semibold text-slate-950">Posting pipeline</h3>
                <p className="mt-1 text-sm text-slate-600">Every transaction passes through validation, posting-rule resolution, debit/credit entries, GL updates, sub-ledger capture, and audit logging.</p>
                <div className="mt-3 grid gap-3 md:grid-cols-2">
                  {postingPipeline ? (
                    Object.entries(postingPipeline).map(([stage, details]) => {
                      const pipelineDetails = details as { status?: string; is_balanced?: boolean; rule?: unknown; entry_id?: string };
                      const ruleApplied = Boolean(pipelineDetails.rule);
                      return (
                        <div key={stage} className="rounded-md border border-slate-200 bg-white p-3">
                          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{stage.replace(/_/g, ' ')}</p>
                          <p className="mt-1 text-sm font-medium text-slate-900">{String(pipelineDetails.status || 'pending')}</p>
                          {pipelineDetails.is_balanced !== undefined && (
                            <p className="mt-1 text-xs text-slate-500">Balanced: {pipelineDetails.is_balanced ? 'Yes' : 'No'}</p>
                          )}
                          {ruleApplied && (
                            <p className="mt-1 text-xs text-slate-500">Rule applied</p>
                          )}
                          {pipelineDetails.entry_id && (
                            <p className="mt-1 break-all text-xs text-slate-500">Entry ID: {pipelineDetails.entry_id}</p>
                          )}
                        </div>
                      );
                    })
                  ) : (
                    <p className="text-sm text-slate-600">Submit a posting to see the pipeline stages here.</p>
                  )}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'receiptVoucher' && (
            <div className="mt-5 grid gap-6 xl:grid-cols-[0.85fr_1.15fr]">
              <form
                className="grid gap-4"
                onSubmit={(event) => {
                  event.preventDefault();
                  runAction(
                    'receipt-voucher',
                    async () => {
                      await apiClient.createReceiptVoucher({
                        tenant_id: tenantId,
                        receipt_category: receiptVoucherForm.receipt_category,
                        amount: receiptVoucherAmount,
                        payer_name: receiptVoucherForm.payer_name,
                        customer_id: receiptVoucherForm.customer_id || undefined,
                        description: receiptVoucherForm.description || undefined,
                        reference: receiptVoucherForm.reference || undefined,
                        voucher_date: receiptVoucherForm.voucher_date,
                        branch_id: receiptVoucherForm.branch_id || undefined,
                        payment_mode: receiptVoucherForm.payment_mode,
                        payment_reference: receiptVoucherForm.payment_reference || undefined,
                        payment_details: receiptVoucherForm.payment_note ? { note: receiptVoucherForm.payment_note } : undefined,
                        created_by: user?.username || 'system',
                        debit_account_id: receiptVoucherForm.debit_account_id || undefined,
                        credit_account_id: receiptVoucherForm.credit_account_id || undefined,
                        cost_center: receiptVoucherForm.cost_center || undefined,
                        profit_center: receiptVoucherForm.profit_center || undefined,
                      });
                      setReceiptVoucherForm({
                        receipt_category: receiptVoucherForm.receipt_category,
                        amount: '',
                        payer_name: '',
                        customer_id: '',
                        description: '',
                        reference: '',
                        voucher_date: new Date().toISOString().slice(0, 10),
                        branch_id: '',
                        payment_mode: receiptVoucherForm.payment_mode,
                        payment_reference: '',
                        payment_note: '',
                        debit_account_id: '',
                        credit_account_id: '',
                        cost_center: '',
                        profit_center: '',
                      });
                    },
                    'Receipt voucher created.',
                  );
                }}
              >
                <div>
                  <p className="text-xs font-semibold uppercase text-blue-700">Module 7</p>
                  <h2 className="mt-1 text-lg font-semibold text-slate-950">Receipt Voucher</h2>
                </div>

                <div className="grid gap-2 sm:grid-cols-2 xl:grid-cols-3">
                  {receiptVoucherOptions.categories.map((category) => (
                    <button
                      key={category.key}
                      type="button"
                      onClick={() => setReceiptVoucherForm({ ...receiptVoucherForm, receipt_category: category.key })}
                      className={`rounded-md border px-3 py-2 text-left text-sm font-semibold ${
                        receiptVoucherForm.receipt_category === category.key
                          ? 'border-blue-600 bg-blue-50 text-blue-800'
                          : 'border-slate-200 bg-white text-slate-700 hover:border-blue-300'
                      }`}
                    >
                      {category.label}
                    </button>
                  ))}
                </div>

                <div className="grid gap-3 sm:grid-cols-2">
                  <input
                    className="h-10 rounded-md border border-slate-300 px-3 text-sm"
                    type="number"
                    min="0"
                    step="0.01"
                    placeholder="Amount"
                    value={receiptVoucherForm.amount}
                    onChange={(e) => setReceiptVoucherForm({ ...receiptVoucherForm, amount: e.target.value })}
                  />
                  <input
                    className="h-10 rounded-md border border-slate-300 px-3 text-sm"
                    placeholder="Customer / payer name"
                    value={receiptVoucherForm.payer_name}
                    onChange={(e) => setReceiptVoucherForm({ ...receiptVoucherForm, payer_name: e.target.value })}
                  />
                </div>

                <div className="grid gap-3 sm:grid-cols-2">
                  <input
                    className="h-10 rounded-md border border-slate-300 px-3 text-sm"
                    placeholder="Customer ID"
                    value={receiptVoucherForm.customer_id}
                    onChange={(e) => setReceiptVoucherForm({ ...receiptVoucherForm, customer_id: e.target.value })}
                  />
                  <input
                    className="h-10 rounded-md border border-slate-300 px-3 text-sm"
                    type="date"
                    value={receiptVoucherForm.voucher_date}
                    onChange={(e) => setReceiptVoucherForm({ ...receiptVoucherForm, voucher_date: e.target.value })}
                  />
                </div>

                <div className="grid gap-3 sm:grid-cols-2">
                  <input
                    className="h-10 rounded-md border border-slate-300 px-3 text-sm"
                    placeholder="Branch ID"
                    value={receiptVoucherForm.branch_id}
                    onChange={(e) => setReceiptVoucherForm({ ...receiptVoucherForm, branch_id: e.target.value })}
                  />
                  <input
                    className="h-10 rounded-md border border-slate-300 px-3 text-sm"
                    placeholder="Reference"
                    value={receiptVoucherForm.reference}
                    onChange={(e) => setReceiptVoucherForm({ ...receiptVoucherForm, reference: e.target.value })}
                  />
                </div>

                <input
                  className="h-10 rounded-md border border-slate-300 px-3 text-sm"
                  placeholder="Description"
                  value={receiptVoucherForm.description}
                  onChange={(e) => setReceiptVoucherForm({ ...receiptVoucherForm, description: e.target.value })}
                />

                <div className="grid gap-3 sm:grid-cols-2">
                  <select
                    className="h-10 rounded-md border border-slate-300 px-3 text-sm"
                    value={receiptVoucherForm.payment_mode}
                    onChange={(e) => setReceiptVoucherForm({ ...receiptVoucherForm, payment_mode: e.target.value as PaymentMode })}
                  >
                    {receiptVoucherOptions.payment_modes.map((mode) => (
                      <option key={mode} value={mode}>{mode.toUpperCase()}</option>
                    ))}
                  </select>
                  <input
                    className="h-10 rounded-md border border-slate-300 px-3 text-sm"
                    placeholder={receiptVoucherForm.payment_mode === 'cash' ? 'Cash receipt note' : 'Transaction reference'}
                    value={receiptVoucherForm.payment_reference}
                    onChange={(e) => setReceiptVoucherForm({ ...receiptVoucherForm, payment_reference: e.target.value })}
                  />
                </div>

                <input
                  className="h-10 rounded-md border border-slate-300 px-3 text-sm"
                  placeholder="Receipt note"
                  value={receiptVoucherForm.payment_note}
                  onChange={(e) => setReceiptVoucherForm({ ...receiptVoucherForm, payment_note: e.target.value })}
                />

                <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                  <p className="text-sm font-semibold text-slate-900">GL Posting</p>
                  <div className="mt-3 grid gap-3 sm:grid-cols-2">
                    <select
                      className="h-10 rounded-md border border-slate-300 bg-white px-3 text-sm"
                      value={receiptVoucherForm.debit_account_id}
                      onChange={(e) => setReceiptVoucherForm({ ...receiptVoucherForm, debit_account_id: e.target.value })}
                    >
                      <option value="">Debit: {receiptVoucherForm.payment_mode === 'cash' ? '1000_CASH' : '1120_BANK'}</option>
                      {selectableAccounts.map((account) => (
                        <option key={account.id} value={account.id}>{accountLabel(account)}</option>
                      ))}
                    </select>
                    <select
                      className="h-10 rounded-md border border-slate-300 bg-white px-3 text-sm"
                      value={receiptVoucherForm.credit_account_id}
                      onChange={(e) => setReceiptVoucherForm({ ...receiptVoucherForm, credit_account_id: e.target.value })}
                    >
                      <option value="">Credit: {receiptVoucherCategory?.credit_account_code || 'category default'}</option>
                      {selectableAccounts.map((account) => (
                        <option key={account.id} value={account.id}>{accountLabel(account)}</option>
                      ))}
                    </select>
                  </div>
                  <div className="mt-3 grid gap-3 sm:grid-cols-2">
                    <input
                      className="h-10 rounded-md border border-slate-300 bg-white px-3 text-sm"
                      placeholder="Cost center"
                      value={receiptVoucherForm.cost_center}
                      onChange={(e) => setReceiptVoucherForm({ ...receiptVoucherForm, cost_center: e.target.value })}
                    />
                    <input
                      className="h-10 rounded-md border border-slate-300 bg-white px-3 text-sm"
                      placeholder="Profit center"
                      value={receiptVoucherForm.profit_center}
                      onChange={(e) => setReceiptVoucherForm({ ...receiptVoucherForm, profit_center: e.target.value })}
                    />
                  </div>
                </div>

                <button
                  disabled={!!busyAction || !canCreateReceiptVoucher}
                  className="h-10 rounded-md bg-blue-600 px-4 text-sm font-semibold text-white disabled:opacity-50"
                >
                  {busyAction === 'receipt-voucher' ? 'Saving...' : 'Create Receipt Voucher'}
                </button>
              </form>

              <div className="space-y-4">
                <div className="grid gap-3 sm:grid-cols-3">
                  <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                    <dt className="text-xs font-semibold uppercase text-slate-500">Draft/Review</dt>
                    <dd className="mt-1 text-2xl font-bold text-slate-950">{receiptVouchers.filter((item) => ['draft', 'verified', 'approved'].includes(item.status)).length}</dd>
                  </div>
                  <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                    <dt className="text-xs font-semibold uppercase text-slate-500">Posted</dt>
                    <dd className="mt-1 text-2xl font-bold text-slate-950">{receiptVouchers.filter((item) => item.status === 'posted').length}</dd>
                  </div>
                  <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                    <dt className="text-xs font-semibold uppercase text-slate-500">Total</dt>
                    <dd className="mt-1 text-2xl font-bold text-slate-950">{money(receiptVouchers.reduce((sum, item) => sum + Number(item.amount || 0), 0))}</dd>
                  </div>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full min-w-[840px] text-sm">
                    <thead>
                      <tr className="border-b border-slate-200 text-left text-slate-500">
                        <th className="px-3 py-2">Voucher</th>
                        <th className="px-3 py-2">Category</th>
                        <th className="px-3 py-2">Customer</th>
                        <th className="px-3 py-2">Mode</th>
                        <th className="px-3 py-2 text-right">Amount</th>
                        <th className="px-3 py-2">Status</th>
                        <th className="px-3 py-2">Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {receiptVouchers.map((voucher) => (
                        <tr key={voucher.id} className="border-b border-slate-100">
                          <td className="px-3 py-2">
                            <p className="font-medium text-slate-900">{voucher.voucher_number}</p>
                            <p className="text-xs text-slate-500">{voucher.reference || voucher.payment_reference || 'No reference'}</p>
                          </td>
                          <td className="px-3 py-2 text-slate-700">
                            {receiptVoucherOptions.categories.find((category) => category.key === voucher.receipt_category)?.label || voucher.receipt_category}
                          </td>
                          <td className="px-3 py-2 text-slate-700">
                            <p>{voucher.payer_name || '-'}</p>
                            {voucher.customer_id && <p className="text-xs text-slate-500">{voucher.customer_id}</p>}
                          </td>
                          <td className="px-3 py-2 text-slate-700">{voucher.payment_mode?.toUpperCase() || '-'}</td>
                          <td className="px-3 py-2 text-right text-slate-900">{money(Number(voucher.amount || 0))}</td>
                          <td className="px-3 py-2 text-slate-700">{voucher.status}</td>
                          <td className="px-3 py-2">
                            <div className="flex flex-wrap gap-2">
                              {voucher.status === 'draft' && <button className="rounded-md bg-slate-100 px-3 py-1 font-semibold text-slate-700" onClick={() => runAction('verify-receipt', () => apiClient.verifyVoucher(voucher.id, tenantId, user?.username), 'Receipt voucher verified.')}>Verify</button>}
                              {voucher.status === 'verified' && <button className="rounded-md bg-slate-100 px-3 py-1 font-semibold text-slate-700" onClick={() => runAction('approve-receipt', () => apiClient.approveVoucher(voucher.id, tenantId, user?.username), 'Receipt voucher approved.')}>Approve</button>}
                              {voucher.status === 'approved' && <button className="rounded-md bg-blue-600 px-3 py-1 font-semibold text-white" onClick={() => runAction('post-receipt', () => apiClient.postVoucher(voucher.id, tenantId, user?.username), 'Receipt voucher posted.')}>Post</button>}
                              {voucher.status === 'posted' && <button className="rounded-md bg-rose-600 px-3 py-1 font-semibold text-white" onClick={() => runAction('reverse-receipt', () => apiClient.reverseVoucher(voucher.id, tenantId, user?.username), 'Receipt voucher reversed.')}>Reverse</button>}
                            </div>
                          </td>
                        </tr>
                      ))}
                      {receiptVouchers.length === 0 && (
                        <tr>
                          <td colSpan={7} className="px-3 py-8 text-center text-sm text-slate-500">No receipt vouchers yet.</td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'paymentVoucher' && (
            <div className="mt-5 grid gap-6 xl:grid-cols-[0.85fr_1.15fr]">
              <form
                className="grid gap-4"
                onSubmit={(event) => {
                  event.preventDefault();
                  runAction(
                    'payment-voucher',
                    async () => {
                      await apiClient.createPaymentVoucher({
                        tenant_id: tenantId,
                        payment_category: paymentVoucherForm.payment_category,
                        amount: paymentVoucherAmount,
                        payee_name: paymentVoucherForm.payee_name,
                        description: paymentVoucherForm.description || undefined,
                        reference: paymentVoucherForm.reference || undefined,
                        voucher_date: paymentVoucherForm.voucher_date,
                        branch_id: paymentVoucherForm.branch_id || undefined,
                        payment_mode: paymentVoucherForm.payment_mode,
                        payment_reference: paymentVoucherForm.payment_reference || undefined,
                        payment_details: paymentVoucherForm.payment_note ? { note: paymentVoucherForm.payment_note } : undefined,
                        created_by: user?.username || 'system',
                        debit_account_id: paymentVoucherForm.debit_account_id || undefined,
                        credit_account_id: paymentVoucherForm.credit_account_id || undefined,
                        cost_center: paymentVoucherForm.cost_center || undefined,
                        profit_center: paymentVoucherForm.profit_center || undefined,
                      });
                      setPaymentVoucherForm({
                        payment_category: paymentVoucherForm.payment_category,
                        amount: '',
                        payee_name: '',
                        description: '',
                        reference: '',
                        voucher_date: new Date().toISOString().slice(0, 10),
                        branch_id: '',
                        payment_mode: paymentVoucherForm.payment_mode,
                        payment_reference: '',
                        payment_note: '',
                        debit_account_id: '',
                        credit_account_id: '',
                        cost_center: '',
                        profit_center: '',
                      });
                    },
                    'Payment voucher created.',
                  );
                }}
              >
                <div>
                  <p className="text-xs font-semibold uppercase text-blue-700">Module 8</p>
                  <h2 className="mt-1 text-lg font-semibold text-slate-950">Payment Voucher</h2>
                </div>

                <div className="grid gap-2 sm:grid-cols-2 xl:grid-cols-3">
                  {paymentVoucherCategories.map((category) => (
                    <button
                      key={category.key}
                      type="button"
                      onClick={() => setPaymentVoucherForm({ ...paymentVoucherForm, payment_category: category.key })}
                      className={`rounded-md border px-3 py-2 text-left text-sm font-semibold ${
                        paymentVoucherForm.payment_category === category.key
                          ? 'border-blue-600 bg-blue-50 text-blue-800'
                          : 'border-slate-200 bg-white text-slate-700 hover:border-blue-300'
                      }`}
                    >
                      {category.label}
                    </button>
                  ))}
                </div>

                <div className="grid gap-3 sm:grid-cols-2">
                  <input
                    className="h-10 rounded-md border border-slate-300 px-3 text-sm"
                    type="number"
                    min="0"
                    step="0.01"
                    placeholder="Amount"
                    value={paymentVoucherForm.amount}
                    onChange={(e) => setPaymentVoucherForm({ ...paymentVoucherForm, amount: e.target.value })}
                  />
                  <input
                    className="h-10 rounded-md border border-slate-300 px-3 text-sm"
                    placeholder="Payee name"
                    value={paymentVoucherForm.payee_name}
                    onChange={(e) => setPaymentVoucherForm({ ...paymentVoucherForm, payee_name: e.target.value })}
                  />
                </div>

                <div className="grid gap-3 sm:grid-cols-2">
                  <input
                    className="h-10 rounded-md border border-slate-300 px-3 text-sm"
                    type="date"
                    value={paymentVoucherForm.voucher_date}
                    onChange={(e) => setPaymentVoucherForm({ ...paymentVoucherForm, voucher_date: e.target.value })}
                  />
                  <input
                    className="h-10 rounded-md border border-slate-300 px-3 text-sm"
                    placeholder="Branch ID"
                    value={paymentVoucherForm.branch_id}
                    onChange={(e) => setPaymentVoucherForm({ ...paymentVoucherForm, branch_id: e.target.value })}
                  />
                </div>

                <input
                  className="h-10 rounded-md border border-slate-300 px-3 text-sm"
                  placeholder="Description"
                  value={paymentVoucherForm.description}
                  onChange={(e) => setPaymentVoucherForm({ ...paymentVoucherForm, description: e.target.value })}
                />
                <input
                  className="h-10 rounded-md border border-slate-300 px-3 text-sm"
                  placeholder="Reference"
                  value={paymentVoucherForm.reference}
                  onChange={(e) => setPaymentVoucherForm({ ...paymentVoucherForm, reference: e.target.value })}
                />

                <div className="grid gap-3 sm:grid-cols-2">
                  <select
                    className="h-10 rounded-md border border-slate-300 px-3 text-sm"
                    value={paymentVoucherForm.payment_mode}
                    onChange={(e) => setPaymentVoucherForm({ ...paymentVoucherForm, payment_mode: e.target.value as PaymentMode })}
                  >
                    <option value="cash">Cash</option>
                    <option value="cheque">Cheque</option>
                    <option value="upi">UPI</option>
                    <option value="rtgs">RTGS</option>
                    <option value="neft">NEFT</option>
                    <option value="imps">IMPS</option>
                  </select>
                  <input
                    className="h-10 rounded-md border border-slate-300 px-3 text-sm"
                    placeholder={paymentVoucherForm.payment_mode === 'cash' ? 'Cash note' : 'Transaction reference'}
                    value={paymentVoucherForm.payment_reference}
                    onChange={(e) => setPaymentVoucherForm({ ...paymentVoucherForm, payment_reference: e.target.value })}
                  />
                </div>

                <input
                  className="h-10 rounded-md border border-slate-300 px-3 text-sm"
                  placeholder="Payment note"
                  value={paymentVoucherForm.payment_note}
                  onChange={(e) => setPaymentVoucherForm({ ...paymentVoucherForm, payment_note: e.target.value })}
                />

                <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                  <p className="text-sm font-semibold text-slate-900">GL Posting</p>
                  <div className="mt-3 grid gap-3 sm:grid-cols-2">
                    <select
                      className="h-10 rounded-md border border-slate-300 bg-white px-3 text-sm"
                      value={paymentVoucherForm.debit_account_id}
                      onChange={(e) => setPaymentVoucherForm({ ...paymentVoucherForm, debit_account_id: e.target.value })}
                    >
                      <option value="">Debit: {paymentVoucherCategory?.debit_account_code || 'category default'}</option>
                      {selectableAccounts.map((account) => (
                        <option key={account.id} value={account.id}>{accountLabel(account)}</option>
                      ))}
                    </select>
                    <select
                      className="h-10 rounded-md border border-slate-300 bg-white px-3 text-sm"
                      value={paymentVoucherForm.credit_account_id}
                      onChange={(e) => setPaymentVoucherForm({ ...paymentVoucherForm, credit_account_id: e.target.value })}
                    >
                      <option value="">Credit: {paymentVoucherForm.payment_mode === 'cash' ? '1000_CASH' : '1120_BANK'}</option>
                      {selectableAccounts.map((account) => (
                        <option key={account.id} value={account.id}>{accountLabel(account)}</option>
                      ))}
                    </select>
                  </div>
                  <div className="mt-3 grid gap-3 sm:grid-cols-2">
                    <input
                      className="h-10 rounded-md border border-slate-300 bg-white px-3 text-sm"
                      placeholder="Cost center"
                      value={paymentVoucherForm.cost_center}
                      onChange={(e) => setPaymentVoucherForm({ ...paymentVoucherForm, cost_center: e.target.value })}
                    />
                    <input
                      className="h-10 rounded-md border border-slate-300 bg-white px-3 text-sm"
                      placeholder="Profit center"
                      value={paymentVoucherForm.profit_center}
                      onChange={(e) => setPaymentVoucherForm({ ...paymentVoucherForm, profit_center: e.target.value })}
                    />
                  </div>
                </div>

                <button
                  disabled={!!busyAction || !canCreatePaymentVoucher}
                  className="h-10 rounded-md bg-blue-600 px-4 text-sm font-semibold text-white disabled:opacity-50"
                >
                  {busyAction === 'payment-voucher' ? 'Saving...' : 'Create Payment Voucher'}
                </button>
              </form>

              <div className="space-y-4">
                <div className="grid gap-3 sm:grid-cols-3">
                  <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                    <dt className="text-xs font-semibold uppercase text-slate-500">Draft/Review</dt>
                    <dd className="mt-1 text-2xl font-bold text-slate-950">{paymentVouchers.filter((item) => ['draft', 'verified', 'approved'].includes(item.status)).length}</dd>
                  </div>
                  <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                    <dt className="text-xs font-semibold uppercase text-slate-500">Posted</dt>
                    <dd className="mt-1 text-2xl font-bold text-slate-950">{paymentVouchers.filter((item) => item.status === 'posted').length}</dd>
                  </div>
                  <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                    <dt className="text-xs font-semibold uppercase text-slate-500">Total</dt>
                    <dd className="mt-1 text-2xl font-bold text-slate-950">{money(paymentVouchers.reduce((sum, item) => sum + Number(item.amount || 0), 0))}</dd>
                  </div>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full min-w-[820px] text-sm">
                    <thead>
                      <tr className="border-b border-slate-200 text-left text-slate-500">
                        <th className="px-3 py-2">Voucher</th>
                        <th className="px-3 py-2">Category</th>
                        <th className="px-3 py-2">Payee</th>
                        <th className="px-3 py-2 text-right">Amount</th>
                        <th className="px-3 py-2">Status</th>
                        <th className="px-3 py-2">Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {paymentVouchers.map((voucher) => (
                        <tr key={voucher.id} className="border-b border-slate-100">
                          <td className="px-3 py-2">
                            <p className="font-medium text-slate-900">{voucher.voucher_number}</p>
                            <p className="text-xs text-slate-500">{voucher.reference || voucher.payment_reference || 'No reference'}</p>
                          </td>
                          <td className="px-3 py-2 text-slate-700">
                            {paymentVoucherCategories.find((category) => category.key === voucher.payment_category)?.label || voucher.payment_category}
                          </td>
                          <td className="px-3 py-2 text-slate-700">{voucher.payee_name || '-'}</td>
                          <td className="px-3 py-2 text-right text-slate-900">{money(Number(voucher.amount || 0))}</td>
                          <td className="px-3 py-2 text-slate-700">{voucher.status}</td>
                          <td className="px-3 py-2">
                            <div className="flex flex-wrap gap-2">
                              {voucher.status === 'draft' && <button className="rounded-md bg-slate-100 px-3 py-1 font-semibold text-slate-700" onClick={() => runAction('verify-payment', () => apiClient.verifyVoucher(voucher.id, tenantId, user?.username), 'Payment voucher verified.')}>Verify</button>}
                              {voucher.status === 'verified' && <button className="rounded-md bg-slate-100 px-3 py-1 font-semibold text-slate-700" onClick={() => runAction('approve-payment', () => apiClient.approveVoucher(voucher.id, tenantId, user?.username), 'Payment voucher approved.')}>Approve</button>}
                              {voucher.status === 'approved' && <button className="rounded-md bg-blue-600 px-3 py-1 font-semibold text-white" onClick={() => runAction('post-payment', () => apiClient.postVoucher(voucher.id, tenantId, user?.username), 'Payment voucher posted.')}>Post</button>}
                              {voucher.status === 'posted' && <button className="rounded-md bg-rose-600 px-3 py-1 font-semibold text-white" onClick={() => runAction('reverse-payment', () => apiClient.reverseVoucher(voucher.id, tenantId, user?.username), 'Payment voucher reversed.')}>Reverse</button>}
                            </div>
                          </td>
                        </tr>
                      ))}
                      {paymentVouchers.length === 0 && (
                        <tr>
                          <td colSpan={6} className="px-3 py-8 text-center text-sm text-slate-500">No payment vouchers yet.</td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'contraVoucher' && (
            <div className="mt-5 grid gap-6 xl:grid-cols-[0.85fr_1.15fr]">
              <form
                className="grid gap-4"
                onSubmit={(event) => {
                  event.preventDefault();
                  runAction(
                    'contra-voucher',
                    async () => {
                      await apiClient.createContraVoucher({
                        tenant_id: tenantId,
                        transfer_type: contraVoucherForm.transfer_type,
                        amount: contraVoucherAmount,
                        description: contraVoucherForm.description || undefined,
                        reference: contraVoucherForm.reference || undefined,
                        transfer_reference: contraVoucherForm.transfer_reference || undefined,
                        voucher_date: contraVoucherForm.voucher_date,
                        branch_id: contraVoucherForm.branch_id || undefined,
                        source_location: contraVoucherForm.source_location || undefined,
                        destination_location: contraVoucherForm.destination_location || undefined,
                        transfer_details: contraVoucherForm.transfer_note ? { note: contraVoucherForm.transfer_note } : undefined,
                        created_by: user?.username || 'system',
                        debit_account_id: contraVoucherForm.debit_account_id || undefined,
                        credit_account_id: contraVoucherForm.credit_account_id || undefined,
                        cost_center: contraVoucherForm.cost_center || undefined,
                        profit_center: contraVoucherForm.profit_center || undefined,
                      });
                      setContraVoucherForm({
                        transfer_type: contraVoucherForm.transfer_type,
                        amount: '',
                        description: '',
                        reference: '',
                        transfer_reference: '',
                        voucher_date: new Date().toISOString().slice(0, 10),
                        branch_id: '',
                        source_location: '',
                        destination_location: '',
                        transfer_note: '',
                        debit_account_id: '',
                        credit_account_id: '',
                        cost_center: '',
                        profit_center: '',
                      });
                    },
                    'Contra voucher created.',
                  );
                }}
              >
                <div>
                  <p className="text-xs font-semibold uppercase text-blue-700">Module 9</p>
                  <h2 className="mt-1 text-lg font-semibold text-slate-950">Contra Voucher</h2>
                </div>

                <div className="grid gap-2 sm:grid-cols-2">
                  {contraVoucherOptions.transfer_types.map((transfer) => (
                    <button
                      key={transfer.key}
                      type="button"
                      onClick={() => setContraVoucherForm({ ...contraVoucherForm, transfer_type: transfer.key })}
                      className={`rounded-md border px-3 py-2 text-left text-sm font-semibold ${
                        contraVoucherForm.transfer_type === transfer.key
                          ? 'border-blue-600 bg-blue-50 text-blue-800'
                          : 'border-slate-200 bg-white text-slate-700 hover:border-blue-300'
                      }`}
                    >
                      <span>{transfer.label}</span>
                      <span className="mt-1 block text-xs font-normal text-slate-500">
                        Dr {transfer.debit_account_code} / Cr {transfer.credit_account_code}
                      </span>
                    </button>
                  ))}
                </div>

                <div className="grid gap-3 sm:grid-cols-2">
                  <input
                    className="h-10 rounded-md border border-slate-300 px-3 text-sm"
                    type="number"
                    min="0"
                    step="0.01"
                    placeholder="Amount"
                    value={contraVoucherForm.amount}
                    onChange={(e) => setContraVoucherForm({ ...contraVoucherForm, amount: e.target.value })}
                  />
                  <input
                    className="h-10 rounded-md border border-slate-300 px-3 text-sm"
                    type="date"
                    value={contraVoucherForm.voucher_date}
                    onChange={(e) => setContraVoucherForm({ ...contraVoucherForm, voucher_date: e.target.value })}
                  />
                </div>

                <div className="grid gap-3 sm:grid-cols-2">
                  <input
                    className="h-10 rounded-md border border-slate-300 px-3 text-sm"
                    placeholder="Reference"
                    value={contraVoucherForm.reference}
                    onChange={(e) => setContraVoucherForm({ ...contraVoucherForm, reference: e.target.value })}
                  />
                  <input
                    className="h-10 rounded-md border border-slate-300 px-3 text-sm"
                    placeholder="Transfer reference"
                    value={contraVoucherForm.transfer_reference}
                    onChange={(e) => setContraVoucherForm({ ...contraVoucherForm, transfer_reference: e.target.value })}
                  />
                </div>

                <div className="grid gap-3 sm:grid-cols-2">
                  <input
                    className="h-10 rounded-md border border-slate-300 px-3 text-sm"
                    placeholder={`Source (${contraTransfer?.source_label || 'source'})`}
                    value={contraVoucherForm.source_location}
                    onChange={(e) => setContraVoucherForm({ ...contraVoucherForm, source_location: e.target.value })}
                  />
                  <input
                    className="h-10 rounded-md border border-slate-300 px-3 text-sm"
                    placeholder={`Destination (${contraTransfer?.destination_label || 'destination'})`}
                    value={contraVoucherForm.destination_location}
                    onChange={(e) => setContraVoucherForm({ ...contraVoucherForm, destination_location: e.target.value })}
                  />
                </div>

                <div className="grid gap-3 sm:grid-cols-2">
                  <input
                    className="h-10 rounded-md border border-slate-300 px-3 text-sm"
                    placeholder="Branch ID"
                    value={contraVoucherForm.branch_id}
                    onChange={(e) => setContraVoucherForm({ ...contraVoucherForm, branch_id: e.target.value })}
                  />
                  <input
                    className="h-10 rounded-md border border-slate-300 px-3 text-sm"
                    placeholder="Description"
                    value={contraVoucherForm.description}
                    onChange={(e) => setContraVoucherForm({ ...contraVoucherForm, description: e.target.value })}
                  />
                </div>

                <input
                  className="h-10 rounded-md border border-slate-300 px-3 text-sm"
                  placeholder="Transfer note"
                  value={contraVoucherForm.transfer_note}
                  onChange={(e) => setContraVoucherForm({ ...contraVoucherForm, transfer_note: e.target.value })}
                />

                <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                  <p className="text-sm font-semibold text-slate-900">GL Posting</p>
                  <div className="mt-3 grid gap-3 sm:grid-cols-2">
                    <select
                      className="h-10 rounded-md border border-slate-300 bg-white px-3 text-sm"
                      value={contraVoucherForm.debit_account_id}
                      onChange={(e) => setContraVoucherForm({ ...contraVoucherForm, debit_account_id: e.target.value })}
                    >
                      <option value="">Debit: {contraTransfer?.debit_account_code || 'transfer default'}</option>
                      {selectableAccounts.map((account) => (
                        <option key={account.id} value={account.id}>{accountLabel(account)}</option>
                      ))}
                    </select>
                    <select
                      className="h-10 rounded-md border border-slate-300 bg-white px-3 text-sm"
                      value={contraVoucherForm.credit_account_id}
                      onChange={(e) => setContraVoucherForm({ ...contraVoucherForm, credit_account_id: e.target.value })}
                    >
                      <option value="">Credit: {contraTransfer?.credit_account_code || 'transfer default'}</option>
                      {selectableAccounts.map((account) => (
                        <option key={account.id} value={account.id}>{accountLabel(account)}</option>
                      ))}
                    </select>
                  </div>
                  <div className="mt-3 grid gap-3 sm:grid-cols-2">
                    <input
                      className="h-10 rounded-md border border-slate-300 bg-white px-3 text-sm"
                      placeholder="Cost center"
                      value={contraVoucherForm.cost_center}
                      onChange={(e) => setContraVoucherForm({ ...contraVoucherForm, cost_center: e.target.value })}
                    />
                    <input
                      className="h-10 rounded-md border border-slate-300 bg-white px-3 text-sm"
                      placeholder="Profit center"
                      value={contraVoucherForm.profit_center}
                      onChange={(e) => setContraVoucherForm({ ...contraVoucherForm, profit_center: e.target.value })}
                    />
                  </div>
                </div>

                <button
                  disabled={!!busyAction || !canCreateContraVoucher}
                  className="h-10 rounded-md bg-blue-600 px-4 text-sm font-semibold text-white disabled:opacity-50"
                >
                  {busyAction === 'contra-voucher' ? 'Saving...' : 'Create Contra Voucher'}
                </button>
              </form>

              <div className="space-y-4">
                <div className="grid gap-3 sm:grid-cols-3">
                  <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                    <dt className="text-xs font-semibold uppercase text-slate-500">Draft/Review</dt>
                    <dd className="mt-1 text-2xl font-bold text-slate-950">{contraVouchers.filter((item) => ['draft', 'verified', 'approved'].includes(item.status)).length}</dd>
                  </div>
                  <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                    <dt className="text-xs font-semibold uppercase text-slate-500">Posted</dt>
                    <dd className="mt-1 text-2xl font-bold text-slate-950">{contraVouchers.filter((item) => item.status === 'posted').length}</dd>
                  </div>
                  <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                    <dt className="text-xs font-semibold uppercase text-slate-500">Total</dt>
                    <dd className="mt-1 text-2xl font-bold text-slate-950">{money(contraVouchers.reduce((sum, item) => sum + Number(item.amount || 0), 0))}</dd>
                  </div>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full min-w-[860px] text-sm">
                    <thead>
                      <tr className="border-b border-slate-200 text-left text-slate-500">
                        <th className="px-3 py-2">Voucher</th>
                        <th className="px-3 py-2">Transfer</th>
                        <th className="px-3 py-2">Route</th>
                        <th className="px-3 py-2 text-right">Amount</th>
                        <th className="px-3 py-2">Status</th>
                        <th className="px-3 py-2">Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {contraVouchers.map((voucher) => (
                        <tr key={voucher.id} className="border-b border-slate-100">
                          <td className="px-3 py-2">
                            <p className="font-medium text-slate-900">{voucher.voucher_number}</p>
                            <p className="text-xs text-slate-500">{voucher.reference || voucher.transfer_reference || 'No reference'}</p>
                          </td>
                          <td className="px-3 py-2 text-slate-700">
                            {contraVoucherOptions.transfer_types.find((transfer) => transfer.key === voucher.contra_transfer_type)?.label || voucher.contra_transfer_type}
                          </td>
                          <td className="px-3 py-2 text-slate-700">
                            {(voucher.source_location || 'Source')} to {(voucher.destination_location || 'Destination')}
                          </td>
                          <td className="px-3 py-2 text-right text-slate-900">{money(Number(voucher.amount || 0))}</td>
                          <td className="px-3 py-2 text-slate-700">{voucher.status}</td>
                          <td className="px-3 py-2">
                            <div className="flex flex-wrap gap-2">
                              {voucher.status === 'draft' && <button className="rounded-md bg-slate-100 px-3 py-1 font-semibold text-slate-700" onClick={() => runAction('verify-contra', () => apiClient.verifyVoucher(voucher.id, tenantId, user?.username), 'Contra voucher verified.')}>Verify</button>}
                              {voucher.status === 'verified' && <button className="rounded-md bg-slate-100 px-3 py-1 font-semibold text-slate-700" onClick={() => runAction('approve-contra', () => apiClient.approveVoucher(voucher.id, tenantId, user?.username), 'Contra voucher approved.')}>Approve</button>}
                              {voucher.status === 'approved' && <button className="rounded-md bg-blue-600 px-3 py-1 font-semibold text-white" onClick={() => runAction('post-contra', () => apiClient.postVoucher(voucher.id, tenantId, user?.username), 'Contra voucher posted.')}>Post</button>}
                              {voucher.status === 'posted' && <button className="rounded-md bg-rose-600 px-3 py-1 font-semibold text-white" onClick={() => runAction('reverse-contra', () => apiClient.reverseVoucher(voucher.id, tenantId, user?.username), 'Contra voucher reversed.')}>Reverse</button>}
                            </div>
                          </td>
                        </tr>
                      ))}
                      {contraVouchers.length === 0 && (
                        <tr>
                          <td colSpan={6} className="px-3 py-8 text-center text-sm text-slate-500">No contra vouchers yet.</td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'creditNote' && (
            <div className="mt-5 grid gap-6 xl:grid-cols-[0.85fr_1.15fr]">
              <form
                className="grid gap-4"
                onSubmit={(event) => {
                  event.preventDefault();
                  runAction(
                    'credit-note',
                    async () => {
                      await apiClient.createCreditNote({
                        tenant_id: tenantId,
                        credit_note_type: creditNoteForm.credit_note_type,
                        amount: creditNoteAmount,
                        customer_name: creditNoteForm.customer_name,
                        customer_id: creditNoteForm.customer_id || undefined,
                        description: creditNoteForm.description || undefined,
                        reference: creditNoteForm.reference || undefined,
                        credit_note_reference: creditNoteForm.credit_note_reference || undefined,
                        voucher_date: creditNoteForm.voucher_date,
                        branch_id: creditNoteForm.branch_id || undefined,
                        credit_note_details: creditNoteForm.credit_note_note ? { note: creditNoteForm.credit_note_note } : undefined,
                        created_by: user?.username || 'system',
                        debit_account_id: creditNoteForm.debit_account_id || undefined,
                        credit_account_id: creditNoteForm.credit_account_id || undefined,
                        cost_center: creditNoteForm.cost_center || undefined,
                        profit_center: creditNoteForm.profit_center || undefined,
                      });
                      setCreditNoteForm({
                        credit_note_type: creditNoteForm.credit_note_type,
                        amount: '',
                        customer_name: '',
                        customer_id: '',
                        description: '',
                        reference: '',
                        credit_note_reference: '',
                        voucher_date: new Date().toISOString().slice(0, 10),
                        branch_id: '',
                        credit_note_note: '',
                        debit_account_id: '',
                        credit_account_id: '',
                        cost_center: '',
                        profit_center: '',
                      });
                    },
                    'Credit note created.',
                  );
                }}
              >
                <div>
                  <p className="text-xs font-semibold uppercase text-blue-700">Module 10</p>
                  <h2 className="mt-1 text-lg font-semibold text-slate-950">Credit Note</h2>
                </div>

                <div className="grid gap-2 sm:grid-cols-2">
                  {creditNoteOptions.credit_note_types.map((noteType) => (
                    <button
                      key={noteType.key}
                      type="button"
                      onClick={() => setCreditNoteForm({ ...creditNoteForm, credit_note_type: noteType.key })}
                      className={`rounded-md border px-3 py-2 text-left text-sm font-semibold ${
                        creditNoteForm.credit_note_type === noteType.key
                          ? 'border-blue-600 bg-blue-50 text-blue-800'
                          : 'border-slate-200 bg-white text-slate-700 hover:border-blue-300'
                      }`}
                    >
                      <span>{noteType.label}</span>
                      <span className="mt-1 block text-xs font-normal text-slate-500">
                        Dr {noteType.debit_account_code} / Cr {noteType.credit_account_code}
                      </span>
                    </button>
                  ))}
                </div>

                <div className="grid gap-3 sm:grid-cols-2">
                  <input
                    className="h-10 rounded-md border border-slate-300 px-3 text-sm"
                    type="number"
                    min="0"
                    step="0.01"
                    placeholder="Amount"
                    value={creditNoteForm.amount}
                    onChange={(e) => setCreditNoteForm({ ...creditNoteForm, amount: e.target.value })}
                  />
                  <input
                    className="h-10 rounded-md border border-slate-300 px-3 text-sm"
                    type="date"
                    value={creditNoteForm.voucher_date}
                    onChange={(e) => setCreditNoteForm({ ...creditNoteForm, voucher_date: e.target.value })}
                  />
                </div>

                <div className="grid gap-3 sm:grid-cols-2">
                  <input
                    className="h-10 rounded-md border border-slate-300 px-3 text-sm"
                    placeholder="Customer name"
                    value={creditNoteForm.customer_name}
                    onChange={(e) => setCreditNoteForm({ ...creditNoteForm, customer_name: e.target.value })}
                  />
                  <input
                    className="h-10 rounded-md border border-slate-300 px-3 text-sm"
                    placeholder="Customer ID"
                    value={creditNoteForm.customer_id}
                    onChange={(e) => setCreditNoteForm({ ...creditNoteForm, customer_id: e.target.value })}
                  />
                </div>

                <div className="grid gap-3 sm:grid-cols-2">
                  <input
                    className="h-10 rounded-md border border-slate-300 px-3 text-sm"
                    placeholder="Reference"
                    value={creditNoteForm.reference}
                    onChange={(e) => setCreditNoteForm({ ...creditNoteForm, reference: e.target.value })}
                  />
                  <input
                    className="h-10 rounded-md border border-slate-300 px-3 text-sm"
                    placeholder="Credit note reference"
                    value={creditNoteForm.credit_note_reference}
                    onChange={(e) => setCreditNoteForm({ ...creditNoteForm, credit_note_reference: e.target.value })}
                  />
                </div>

                <div className="grid gap-3 sm:grid-cols-2">
                  <input
                    className="h-10 rounded-md border border-slate-300 px-3 text-sm"
                    placeholder="Branch ID"
                    value={creditNoteForm.branch_id}
                    onChange={(e) => setCreditNoteForm({ ...creditNoteForm, branch_id: e.target.value })}
                  />
                  <input
                    className="h-10 rounded-md border border-slate-300 px-3 text-sm"
                    placeholder="Description"
                    value={creditNoteForm.description}
                    onChange={(e) => setCreditNoteForm({ ...creditNoteForm, description: e.target.value })}
                  />
                </div>

                <input
                  className="h-10 rounded-md border border-slate-300 px-3 text-sm"
                  placeholder="Credit note note"
                  value={creditNoteForm.credit_note_note}
                  onChange={(e) => setCreditNoteForm({ ...creditNoteForm, credit_note_note: e.target.value })}
                />

                <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                  <p className="text-sm font-semibold text-slate-900">GL Posting</p>
                  <div className="mt-3 grid gap-3 sm:grid-cols-2">
                    <select
                      className="h-10 rounded-md border border-slate-300 bg-white px-3 text-sm"
                      value={creditNoteForm.debit_account_id}
                      onChange={(e) => setCreditNoteForm({ ...creditNoteForm, debit_account_id: e.target.value })}
                    >
                      <option value="">Debit: {creditNoteType?.debit_account_code || 'credit note default'}</option>
                      {selectableAccounts.map((account) => (
                        <option key={account.id} value={account.id}>{accountLabel(account)}</option>
                      ))}
                    </select>
                    <select
                      className="h-10 rounded-md border border-slate-300 bg-white px-3 text-sm"
                      value={creditNoteForm.credit_account_id}
                      onChange={(e) => setCreditNoteForm({ ...creditNoteForm, credit_account_id: e.target.value })}
                    >
                      <option value="">Credit: {creditNoteType?.credit_account_code || 'credit note default'}</option>
                      {selectableAccounts.map((account) => (
                        <option key={account.id} value={account.id}>{accountLabel(account)}</option>
                      ))}
                    </select>
                  </div>
                  <div className="mt-3 grid gap-3 sm:grid-cols-2">
                    <input
                      className="h-10 rounded-md border border-slate-300 bg-white px-3 text-sm"
                      placeholder="Cost center"
                      value={creditNoteForm.cost_center}
                      onChange={(e) => setCreditNoteForm({ ...creditNoteForm, cost_center: e.target.value })}
                    />
                    <input
                      className="h-10 rounded-md border border-slate-300 bg-white px-3 text-sm"
                      placeholder="Profit center"
                      value={creditNoteForm.profit_center}
                      onChange={(e) => setCreditNoteForm({ ...creditNoteForm, profit_center: e.target.value })}
                    />
                  </div>
                </div>

                <button
                  disabled={!!busyAction || !canCreateCreditNote}
                  className="h-10 rounded-md bg-blue-600 px-4 text-sm font-semibold text-white disabled:opacity-50"
                >
                  {busyAction === 'credit-note' ? 'Saving...' : 'Create Credit Note'}
                </button>
              </form>

              <div className="space-y-4">
                <div className="grid gap-3 sm:grid-cols-3">
                  <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                    <dt className="text-xs font-semibold uppercase text-slate-500">Draft/Review</dt>
                    <dd className="mt-1 text-2xl font-bold text-slate-950">{creditNotes.filter((item) => ['draft', 'verified', 'approved'].includes(item.status)).length}</dd>
                  </div>
                  <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                    <dt className="text-xs font-semibold uppercase text-slate-500">Posted</dt>
                    <dd className="mt-1 text-2xl font-bold text-slate-950">{creditNotes.filter((item) => item.status === 'posted').length}</dd>
                  </div>
                  <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                    <dt className="text-xs font-semibold uppercase text-slate-500">Total</dt>
                    <dd className="mt-1 text-2xl font-bold text-slate-950">{money(creditNotes.reduce((sum, item) => sum + Number(item.amount || 0), 0))}</dd>
                  </div>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full min-w-[860px] text-sm">
                    <thead>
                      <tr className="border-b border-slate-200 text-left text-slate-500">
                        <th className="px-3 py-2">Voucher</th>
                        <th className="px-3 py-2">Type</th>
                        <th className="px-3 py-2">Customer</th>
                        <th className="px-3 py-2 text-right">Amount</th>
                        <th className="px-3 py-2">Status</th>
                        <th className="px-3 py-2">Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {creditNotes.map((voucher) => (
                        <tr key={voucher.id} className="border-b border-slate-100">
                          <td className="px-3 py-2">
                            <p className="font-medium text-slate-900">{voucher.voucher_number}</p>
                            <p className="text-xs text-slate-500">{voucher.reference || voucher.credit_note_reference || 'No reference'}</p>
                          </td>
                          <td className="px-3 py-2 text-slate-700">
                            {creditNoteOptions.credit_note_types.find((noteType) => noteType.key === voucher.credit_note_type)?.label || voucher.credit_note_type}
                          </td>
                          <td className="px-3 py-2 text-slate-700">
                            <p>{voucher.customer_name || 'Customer'}</p>
                            <p className="text-xs text-slate-500">{voucher.customer_id || 'No customer ID'}</p>
                          </td>
                          <td className="px-3 py-2 text-right text-slate-900">{money(Number(voucher.amount || 0))}</td>
                          <td className="px-3 py-2 text-slate-700">{voucher.status}</td>
                          <td className="px-3 py-2">
                            <div className="flex flex-wrap gap-2">
                              {voucher.status === 'draft' && <button className="rounded-md bg-slate-100 px-3 py-1 font-semibold text-slate-700" onClick={() => runAction('verify-credit-note', () => apiClient.verifyVoucher(voucher.id, tenantId, user?.username), 'Credit note verified.')}>Verify</button>}
                              {voucher.status === 'verified' && <button className="rounded-md bg-slate-100 px-3 py-1 font-semibold text-slate-700" onClick={() => runAction('approve-credit-note', () => apiClient.approveVoucher(voucher.id, tenantId, user?.username), 'Credit note approved.')}>Approve</button>}
                              {voucher.status === 'approved' && <button className="rounded-md bg-blue-600 px-3 py-1 font-semibold text-white" onClick={() => runAction('post-credit-note', () => apiClient.postVoucher(voucher.id, tenantId, user?.username), 'Credit note posted.')}>Post</button>}
                              {voucher.status === 'posted' && <button className="rounded-md bg-rose-600 px-3 py-1 font-semibold text-white" onClick={() => runAction('reverse-credit-note', () => apiClient.reverseVoucher(voucher.id, tenantId, user?.username), 'Credit note reversed.')}>Reverse</button>}
                            </div>
                          </td>
                        </tr>
                      ))}
                      {creditNotes.length === 0 && (
                        <tr>
                          <td colSpan={6} className="px-3 py-8 text-center text-sm text-slate-500">No credit notes yet.</td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'debitNote' && (
            <div className="mt-5 grid gap-6 xl:grid-cols-[0.85fr_1.15fr]">
              <form
                className="grid gap-4"
                onSubmit={(event) => {
                  event.preventDefault();
                  runAction(
                    'debit-note',
                    async () => {
                      await apiClient.createDebitNote({
                        tenant_id: tenantId,
                        debit_note_type: debitNoteForm.debit_note_type,
                        amount: debitNoteAmount,
                        customer_name: debitNoteForm.customer_name,
                        customer_id: debitNoteForm.customer_id || undefined,
                        description: debitNoteForm.description || undefined,
                        reference: debitNoteForm.reference || undefined,
                        debit_note_reference: debitNoteForm.debit_note_reference || undefined,
                        voucher_date: debitNoteForm.voucher_date,
                        branch_id: debitNoteForm.branch_id || undefined,
                        debit_note_details: debitNoteForm.debit_note_note ? { note: debitNoteForm.debit_note_note } : undefined,
                        created_by: user?.username || 'system',
                        debit_account_id: debitNoteForm.debit_account_id || undefined,
                        credit_account_id: debitNoteForm.credit_account_id || undefined,
                        cost_center: debitNoteForm.cost_center || undefined,
                        profit_center: debitNoteForm.profit_center || undefined,
                      });
                      setDebitNoteForm({
                        debit_note_type: debitNoteForm.debit_note_type,
                        amount: '',
                        customer_name: '',
                        customer_id: '',
                        description: '',
                        reference: '',
                        debit_note_reference: '',
                        voucher_date: new Date().toISOString().slice(0, 10),
                        branch_id: '',
                        debit_note_note: '',
                        debit_account_id: '',
                        credit_account_id: '',
                        cost_center: '',
                        profit_center: '',
                      });
                    },
                    'Debit note created.',
                  );
                }}
              >
                <div>
                  <p className="text-xs font-semibold uppercase text-blue-700">Module 11</p>
                  <h2 className="mt-1 text-lg font-semibold text-slate-950">Debit Note</h2>
                </div>

                <div className="grid gap-2 sm:grid-cols-2">
                  {debitNoteOptions.debit_note_types.map((noteType) => (
                    <button
                      key={noteType.key}
                      type="button"
                      onClick={() => setDebitNoteForm({ ...debitNoteForm, debit_note_type: noteType.key })}
                      className={`rounded-md border px-3 py-2 text-left text-sm font-semibold ${
                        debitNoteForm.debit_note_type === noteType.key
                          ? 'border-blue-600 bg-blue-50 text-blue-800'
                          : 'border-slate-200 bg-white text-slate-700 hover:border-blue-300'
                      }`}
                    >
                      <span>{noteType.label}</span>
                      <span className="mt-1 block text-xs font-normal text-slate-500">
                        Dr {noteType.debit_account_code} / Cr {noteType.credit_account_code}
                      </span>
                    </button>
                  ))}
                </div>

                <div className="grid gap-3 sm:grid-cols-2">
                  <input
                    className="h-10 rounded-md border border-slate-300 px-3 text-sm"
                    type="number"
                    min="0"
                    step="0.01"
                    placeholder="Amount"
                    value={debitNoteForm.amount}
                    onChange={(e) => setDebitNoteForm({ ...debitNoteForm, amount: e.target.value })}
                  />
                  <input
                    className="h-10 rounded-md border border-slate-300 px-3 text-sm"
                    type="date"
                    value={debitNoteForm.voucher_date}
                    onChange={(e) => setDebitNoteForm({ ...debitNoteForm, voucher_date: e.target.value })}
                  />
                </div>

                <div className="grid gap-3 sm:grid-cols-2">
                  <input
                    className="h-10 rounded-md border border-slate-300 px-3 text-sm"
                    placeholder="Customer name"
                    value={debitNoteForm.customer_name}
                    onChange={(e) => setDebitNoteForm({ ...debitNoteForm, customer_name: e.target.value })}
                  />
                  <input
                    className="h-10 rounded-md border border-slate-300 px-3 text-sm"
                    placeholder="Customer ID"
                    value={debitNoteForm.customer_id}
                    onChange={(e) => setDebitNoteForm({ ...debitNoteForm, customer_id: e.target.value })}
                  />
                </div>

                <div className="grid gap-3 sm:grid-cols-2">
                  <input
                    className="h-10 rounded-md border border-slate-300 px-3 text-sm"
                    placeholder="Reference"
                    value={debitNoteForm.reference}
                    onChange={(e) => setDebitNoteForm({ ...debitNoteForm, reference: e.target.value })}
                  />
                  <input
                    className="h-10 rounded-md border border-slate-300 px-3 text-sm"
                    placeholder="Debit note reference"
                    value={debitNoteForm.debit_note_reference}
                    onChange={(e) => setDebitNoteForm({ ...debitNoteForm, debit_note_reference: e.target.value })}
                  />
                </div>

                <div className="grid gap-3 sm:grid-cols-2">
                  <input
                    className="h-10 rounded-md border border-slate-300 px-3 text-sm"
                    placeholder="Branch ID"
                    value={debitNoteForm.branch_id}
                    onChange={(e) => setDebitNoteForm({ ...debitNoteForm, branch_id: e.target.value })}
                  />
                  <input
                    className="h-10 rounded-md border border-slate-300 px-3 text-sm"
                    placeholder="Description"
                    value={debitNoteForm.description}
                    onChange={(e) => setDebitNoteForm({ ...debitNoteForm, description: e.target.value })}
                  />
                </div>

                <input
                  className="h-10 rounded-md border border-slate-300 px-3 text-sm"
                  placeholder="Debit note note"
                  value={debitNoteForm.debit_note_note}
                  onChange={(e) => setDebitNoteForm({ ...debitNoteForm, debit_note_note: e.target.value })}
                />

                <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                  <p className="text-sm font-semibold text-slate-900">GL Posting</p>
                  <div className="mt-3 grid gap-3 sm:grid-cols-2">
                    <select
                      className="h-10 rounded-md border border-slate-300 bg-white px-3 text-sm"
                      value={debitNoteForm.debit_account_id}
                      onChange={(e) => setDebitNoteForm({ ...debitNoteForm, debit_account_id: e.target.value })}
                    >
                      <option value="">Debit: {debitNoteType?.debit_account_code || 'debit note default'}</option>
                      {selectableAccounts.map((account) => (
                        <option key={account.id} value={account.id}>{accountLabel(account)}</option>
                      ))}
                    </select>
                    <select
                      className="h-10 rounded-md border border-slate-300 bg-white px-3 text-sm"
                      value={debitNoteForm.credit_account_id}
                      onChange={(e) => setDebitNoteForm({ ...debitNoteForm, credit_account_id: e.target.value })}
                    >
                      <option value="">Credit: {debitNoteType?.credit_account_code || 'debit note default'}</option>
                      {selectableAccounts.map((account) => (
                        <option key={account.id} value={account.id}>{accountLabel(account)}</option>
                      ))}
                    </select>
                  </div>
                  <div className="mt-3 grid gap-3 sm:grid-cols-2">
                    <input
                      className="h-10 rounded-md border border-slate-300 bg-white px-3 text-sm"
                      placeholder="Cost center"
                      value={debitNoteForm.cost_center}
                      onChange={(e) => setDebitNoteForm({ ...debitNoteForm, cost_center: e.target.value })}
                    />
                    <input
                      className="h-10 rounded-md border border-slate-300 bg-white px-3 text-sm"
                      placeholder="Profit center"
                      value={debitNoteForm.profit_center}
                      onChange={(e) => setDebitNoteForm({ ...debitNoteForm, profit_center: e.target.value })}
                    />
                  </div>
                </div>

                <button
                  disabled={!!busyAction || !canCreateDebitNote}
                  className="h-10 rounded-md bg-blue-600 px-4 text-sm font-semibold text-white disabled:opacity-50"
                >
                  {busyAction === 'debit-note' ? 'Saving...' : 'Create Debit Note'}
                </button>
              </form>

              <div className="space-y-4">
                <div className="grid gap-3 sm:grid-cols-3">
                  <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                    <dt className="text-xs font-semibold uppercase text-slate-500">Draft/Review</dt>
                    <dd className="mt-1 text-2xl font-bold text-slate-950">{debitNotes.filter((item) => ['draft', 'verified', 'approved'].includes(item.status)).length}</dd>
                  </div>
                  <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                    <dt className="text-xs font-semibold uppercase text-slate-500">Posted</dt>
                    <dd className="mt-1 text-2xl font-bold text-slate-950">{debitNotes.filter((item) => item.status === 'posted').length}</dd>
                  </div>
                  <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                    <dt className="text-xs font-semibold uppercase text-slate-500">Total</dt>
                    <dd className="mt-1 text-2xl font-bold text-slate-950">{money(debitNotes.reduce((sum, item) => sum + Number(item.amount || 0), 0))}</dd>
                  </div>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full min-w-[860px] text-sm">
                    <thead>
                      <tr className="border-b border-slate-200 text-left text-slate-500">
                        <th className="px-3 py-2">Voucher</th>
                        <th className="px-3 py-2">Type</th>
                        <th className="px-3 py-2">Customer</th>
                        <th className="px-3 py-2 text-right">Amount</th>
                        <th className="px-3 py-2">Status</th>
                        <th className="px-3 py-2">Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {debitNotes.map((voucher) => (
                        <tr key={voucher.id} className="border-b border-slate-100">
                          <td className="px-3 py-2">
                            <p className="font-medium text-slate-900">{voucher.voucher_number}</p>
                            <p className="text-xs text-slate-500">{voucher.reference || voucher.debit_note_reference || 'No reference'}</p>
                          </td>
                          <td className="px-3 py-2 text-slate-700">
                            {debitNoteOptions.debit_note_types.find((noteType) => noteType.key === voucher.debit_note_type)?.label || voucher.debit_note_type}
                          </td>
                          <td className="px-3 py-2 text-slate-700">
                            <p>{voucher.customer_name || 'Customer'}</p>
                            <p className="text-xs text-slate-500">{voucher.customer_id || 'No customer ID'}</p>
                          </td>
                          <td className="px-3 py-2 text-right text-slate-900">{money(Number(voucher.amount || 0))}</td>
                          <td className="px-3 py-2 text-slate-700">{voucher.status}</td>
                          <td className="px-3 py-2">
                            <div className="flex flex-wrap gap-2">
                              {voucher.status === 'draft' && <button className="rounded-md bg-slate-100 px-3 py-1 font-semibold text-slate-700" onClick={() => runAction('verify-debit-note', () => apiClient.verifyVoucher(voucher.id, tenantId, user?.username), 'Debit note verified.')}>Verify</button>}
                              {voucher.status === 'verified' && <button className="rounded-md bg-slate-100 px-3 py-1 font-semibold text-slate-700" onClick={() => runAction('approve-debit-note', () => apiClient.approveVoucher(voucher.id, tenantId, user?.username), 'Debit note approved.')}>Approve</button>}
                              {voucher.status === 'approved' && <button className="rounded-md bg-blue-600 px-3 py-1 font-semibold text-white" onClick={() => runAction('post-debit-note', () => apiClient.postVoucher(voucher.id, tenantId, user?.username), 'Debit note posted.')}>Post</button>}
                              {voucher.status === 'posted' && <button className="rounded-md bg-rose-600 px-3 py-1 font-semibold text-white" onClick={() => runAction('reverse-debit-note', () => apiClient.reverseVoucher(voucher.id, tenantId, user?.username), 'Debit note reversed.')}>Reverse</button>}
                            </div>
                          </td>
                        </tr>
                      ))}
                      {debitNotes.length === 0 && (
                        <tr>
                          <td colSpan={6} className="px-3 py-8 text-center text-sm text-slate-500">No debit notes yet.</td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'vouchers' && (
            <div className="mt-5 grid gap-6 xl:grid-cols-[0.8fr_1.2fr]">
              <form
                className="grid gap-3"
                onSubmit={(event) => {
                  event.preventDefault();
                  runAction(
                    'voucher',
                    async () => {
                      await apiClient.createVoucher({
                        tenant_id: tenantId,
                        voucher_type: voucherForm.voucher_type,
                        description: voucherForm.description,
                        reference: voucherForm.reference,
                        voucher_date: voucherForm.voucher_date,
                        branch_id: voucherForm.branch_id || undefined,
                        payment_mode: isPaymentLikeVoucher ? voucherForm.payment_mode : undefined,
                        payment_reference: isPaymentLikeVoucher ? voucherForm.payment_reference : undefined,
                        payment_details: isPaymentLikeVoucher ? voucherForm.payment_details : undefined,
                        created_by: user?.username || 'system',
                        lines: voucherForm.lines.map((line) => ({
                          gl_account_id: line.gl_account_id,
                          debit: Number(line.debit || 0),
                          credit: Number(line.credit || 0),
                          description: line.description || undefined,
                        })),
                      });
                      setVoucherForm({
                        ...voucherForm,
                        description: '',
                        reference: '',
                        branch_id: '',
                        payment_mode: 'cash',
                        payment_reference: '',
                        payment_details: { note: '' },
                        lines: [
                          { gl_account_id: '', debit: 0, credit: 0, description: '' },
                          { gl_account_id: '', debit: 0, credit: 0, description: '' },
                        ],
                      });
                    },
                    'Voucher created.',
                  );
                }}
              >
                <h2 className="text-lg font-semibold text-slate-950">Voucher Workflow</h2>
                <select className="h-10 rounded-md border border-slate-300 px-3 text-sm" value={voucherForm.voucher_type} onChange={(e) => setVoucherForm({ ...voucherForm, voucher_type: e.target.value })}>
                  <option value="journal">Journal Voucher</option>
                  <option value="receipt">Receipt Voucher</option>
                  <option value="payment">Payment Voucher</option>
                  <option value="contra">Contra Voucher</option>
                  <option value="credit_note">Credit Note</option>
                  <option value="debit_note">Debit Note</option>
                </select>
                <div className="grid gap-3 sm:grid-cols-2">
                  <input className="h-10 rounded-md border border-slate-300 px-3 text-sm" type="date" value={voucherForm.voucher_date} onChange={(e) => setVoucherForm({ ...voucherForm, voucher_date: e.target.value })} />
                  <input className="h-10 rounded-md border border-slate-300 px-3 text-sm" placeholder="Branch ID" value={voucherForm.branch_id} onChange={(e) => setVoucherForm({ ...voucherForm, branch_id: e.target.value })} />
                </div>
                <input className="h-10 rounded-md border border-slate-300 px-3 text-sm" placeholder="Description" value={voucherForm.description} onChange={(e) => setVoucherForm({ ...voucherForm, description: e.target.value })} />
                <input className="h-10 rounded-md border border-slate-300 px-3 text-sm" placeholder="Reference" value={voucherForm.reference} onChange={(e) => setVoucherForm({ ...voucherForm, reference: e.target.value })} />
                {isPaymentLikeVoucher && (
                  <div className="grid gap-3">
                    <div className="grid gap-3 sm:grid-cols-2">
                      <select
                        className="h-10 rounded-md border border-slate-300 px-3 text-sm"
                        value={voucherForm.payment_mode}
                        onChange={(e) => setVoucherForm({ ...voucherForm, payment_mode: e.target.value as PaymentMode })}
                      >
                        <option value="cash">Cash</option>
                        <option value="cheque">Cheque</option>
                        <option value="upi">UPI</option>
                        <option value="rtgs">RTGS</option>
                        <option value="neft">NEFT</option>
                        <option value="imps">IMPS</option>
                      </select>
                      <input
                        className="h-10 rounded-md border border-slate-300 px-3 text-sm"
                        placeholder={voucherForm.payment_mode === 'cash' ? 'Cash note' : 'Transaction reference'}
                        value={voucherForm.payment_reference}
                        onChange={(e) => setVoucherForm({ ...voucherForm, payment_reference: e.target.value })}
                      />
                    </div>
                    <input
                      className="h-10 rounded-md border border-slate-300 px-3 text-sm"
                      placeholder="Payment details (bank name, UPI ID, cheque number, notes)"
                      value={voucherForm.payment_details.note}
                      onChange={(e) => setVoucherForm({ ...voucherForm, payment_details: { ...voucherForm.payment_details, note: e.target.value } })}
                    />
                  </div>
                )}
                <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                  <div className="flex items-center justify-between gap-3">
                    <p className="text-sm font-semibold text-slate-900">Journal Lines</p>
                    <button
                      type="button"
                      className="rounded-md border border-slate-300 bg-white px-3 py-1 text-sm font-semibold text-slate-700 hover:bg-slate-50"
                      onClick={() => setVoucherForm({
                        ...voucherForm,
                        lines: [...voucherForm.lines, { gl_account_id: '', debit: 0, credit: 0, description: '' }],
                      })}
                    >
                      Add line
                    </button>
                  </div>
                  <div className="mt-3 space-y-3">
                    {voucherForm.lines.map((line, index) => (
                      <div key={index} className="grid gap-3 sm:grid-cols-[1.3fr_1fr_1fr_1fr_auto] items-end">
                        <select
                          className="h-10 rounded-md border border-slate-300 px-3 text-sm"
                          value={line.gl_account_id}
                          onChange={(e) => {
                            const gl_account_id = e.target.value;
                            setVoucherForm({
                              ...voucherForm,
                              lines: voucherForm.lines.map((item, idx) => idx === index ? { ...item, gl_account_id } : item),
                            });
                          }}
                        >
                          <option value="">Select GL account</option>
                          {selectableAccounts.map((account) => (
                            <option key={account.id} value={account.id}>{accountLabel(account)}</option>
                          ))}
                        </select>
                        <input
                          className="h-10 rounded-md border border-slate-300 px-3 text-sm"
                          type="number"
                          placeholder="Debit"
                          value={line.debit}
                          onChange={(e) => {
                            const debit = Number(e.target.value);
                            setVoucherForm({
                              ...voucherForm,
                              lines: voucherForm.lines.map((item, idx) => idx === index ? { ...item, debit, credit: debit > 0 ? 0 : item.credit } : item),
                            });
                          }}
                        />
                        <input
                          className="h-10 rounded-md border border-slate-300 px-3 text-sm"
                          type="number"
                          placeholder="Credit"
                          value={line.credit}
                          onChange={(e) => {
                            const credit = Number(e.target.value);
                            setVoucherForm({
                              ...voucherForm,
                              lines: voucherForm.lines.map((item, idx) => idx === index ? { ...item, credit, debit: credit > 0 ? 0 : item.debit } : item),
                            });
                          }}
                        />
                        <input
                          className="h-10 rounded-md border border-slate-300 px-3 text-sm"
                          placeholder="Line description"
                          value={line.description}
                          onChange={(e) => {
                            const description = e.target.value;
                            setVoucherForm({
                              ...voucherForm,
                              lines: voucherForm.lines.map((item, idx) => idx === index ? { ...item, description } : item),
                            });
                          }}
                        />
                        <button
                          type="button"
                          disabled={voucherForm.lines.length <= 2}
                          className="h-10 rounded-md border border-slate-300 bg-slate-100 px-3 text-sm text-slate-700 hover:bg-slate-200 disabled:opacity-50"
                          onClick={() => setVoucherForm({
                            ...voucherForm,
                            lines: voucherForm.lines.filter((_, idx) => idx !== index),
                          })}
                        >
                          Remove
                        </button>
                      </div>
                    ))}
                  </div>
                  <div className="mt-3 flex items-center justify-between text-sm text-slate-700">
                    <span>Total Debit: {money(voucherTotalDebit)}</span>
                    <span>Total Credit: {money(voucherTotalCredit)}</span>
                    <span className={voucherBalanced ? 'text-emerald-700' : 'text-rose-700'}>
                      {voucherBalanced ? 'Balanced' : 'Not balanced'}
                    </span>
                  </div>
                </div>
                <button disabled={!!busyAction || !canCreateVoucher} className="h-10 rounded-md bg-blue-600 px-4 text-sm font-semibold text-white disabled:opacity-50">
                  {busyAction === 'voucher' ? 'Saving...' : 'Create Voucher'}
                </button>
              </form>

              <div className="overflow-x-auto">
                <table className="w-full min-w-[720px] text-sm">
                  <thead>
                    <tr className="border-b border-slate-200 text-left text-slate-500">
                      <th className="px-3 py-2">Voucher</th>
                      <th className="px-3 py-2">Type</th>
                      <th className="px-3 py-2">Status</th>
                      <th className="px-3 py-2">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {vouchers.map((voucher) => (
                      <tr key={voucher.id} className="border-b border-slate-100">
                        <td className="px-3 py-2">
                          <p className="font-medium text-slate-900">{voucher.voucher_number}</p>
                          <p className="text-slate-500">{voucher.description}</p>
                        </td>
                        <td className="px-3 py-2 text-slate-700">{voucher.voucher_type}</td>
                        <td className="px-3 py-2 text-slate-700">{voucher.status}{voucher.payment_mode ? ` - ${voucher.payment_mode.toUpperCase()}` : ''}</td>
                        <td className="px-3 py-2">
                          <div className="flex flex-wrap gap-2">
                            {voucher.status === 'draft' && <button className="rounded-md bg-slate-100 px-3 py-1 font-semibold text-slate-700" onClick={() => runAction('verify', () => apiClient.verifyVoucher(voucher.id, tenantId, user?.username), 'Voucher verified.')}>Verify</button>}
                            {voucher.status === 'verified' && <button className="rounded-md bg-slate-100 px-3 py-1 font-semibold text-slate-700" onClick={() => runAction('approve', () => apiClient.approveVoucher(voucher.id, tenantId, user?.username), 'Voucher approved.')}>Approve</button>}
                            {voucher.status === 'approved' && <button className="rounded-md bg-blue-600 px-3 py-1 font-semibold text-white" onClick={() => runAction('post-voucher', () => apiClient.postVoucher(voucher.id, tenantId, user?.username), 'Voucher posted.')}>Post</button>}
                            {voucher.status === 'posted' && <button className="rounded-md bg-rose-600 px-3 py-1 font-semibold text-white" onClick={() => runAction('reverse-voucher', () => apiClient.reverseVoucher(voucher.id, tenantId, user?.username), 'Voucher reversed.')}>Reverse</button>}
                          </div>
                          {voucher.posted_journal_entry_id && (
                            <p className="mt-2 text-xs text-slate-500">Journal: {voucher.posted_journal_entry_id}</p>
                          )}
                          {voucher.payment_reference && (
                            <p className="mt-1 text-xs text-slate-500">Payment Ref: {voucher.payment_reference}</p>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {activeTab === 'statements' && (
            <div className="mt-5 grid gap-6 xl:grid-cols-2">
              <div>
                <h2 className="text-lg font-semibold text-slate-950">Trial Balance</h2>
                <div className="mt-3 overflow-x-auto">
                  <table className="w-full min-w-[620px] text-sm">
                    <thead>
                      <tr className="border-b border-slate-200 text-left text-slate-500">
                        <th className="px-3 py-2">Code</th>
                        <th className="px-3 py-2">Name</th>
                        <th className="px-3 py-2 text-right">Debit</th>
                        <th className="px-3 py-2 text-right">Credit</th>
                      </tr>
                    </thead>
                    <tbody>
                      {trialRows.map((row) => (
                        <tr key={row.account_id} className="border-b border-slate-100">
                          <td className="px-3 py-2 font-medium text-slate-900">{row.account_code}</td>
                          <td className="px-3 py-2 text-slate-700">{row.account_name}</td>
                          <td className="px-3 py-2 text-right text-slate-900">{money(row.debit)}</td>
                          <td className="px-3 py-2 text-right text-slate-900">{money(row.credit)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
              <div className="space-y-6">
                <div>
                  <h2 className="text-lg font-semibold text-slate-950">Product Ledgers</h2>
                  <p className="mt-1 text-sm text-slate-600">Each product ledger posts into the same journal stream and rolls up into the general ledger.</p>
                  <div className="mt-3 overflow-x-auto">
                    <table className="w-full min-w-[720px] text-sm">
                      <thead>
                        <tr className="border-b border-slate-200 text-left text-slate-500">
                          <th className="px-3 py-2">Ledger</th>
                          <th className="px-3 py-2">Module</th>
                          <th className="px-3 py-2 text-right">Transactions</th>
                          <th className="px-3 py-2 text-right">Total</th>
                          <th className="px-3 py-2">Roll-up</th>
                        </tr>
                      </thead>
                      <tbody>
                        {subLedgerSummaryRows.map((row) => (
                          <tr key={`${row.source_module}-${row.ledger_name}`} className="border-b border-slate-100">
                            <td className="px-3 py-2 text-slate-900">
                              <p className="font-medium">{row.ledger_name}</p>
                              <p className="text-xs text-slate-500">{row.last_entry_at ? new Date(row.last_entry_at).toLocaleString() : 'No entries yet'}</p>
                            </td>
                            <td className="px-3 py-2 text-slate-700">{row.source_module}</td>
                            <td className="px-3 py-2 text-right text-slate-900">{row.transaction_count}</td>
                            <td className="px-3 py-2 text-right text-slate-900">{money(row.total_amount)}</td>
                            <td className="px-3 py-2 text-slate-700">{row.rollup_to}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>

                <div>
                  <h2 className="text-lg font-semibold text-slate-950">General Ledger Book</h2>
                  <div className="mt-3 overflow-x-auto">
                    <table className="w-full min-w-[900px] text-sm">
                      <thead>
                        <tr className="border-b border-slate-200 text-left text-slate-500">
                          <th className="px-3 py-2">GL Number</th>
                          <th className="px-3 py-2">Branch</th>
                          <th className="px-3 py-2">Currency</th>
                          <th className="px-3 py-2 text-right">Opening</th>
                          <th className="px-3 py-2 text-right">Debit</th>
                          <th className="px-3 py-2 text-right">Credit</th>
                          <th className="px-3 py-2 text-right">Balance</th>
                          <th className="px-3 py-2 text-right">Closing</th>
                          <th className="px-3 py-2">FY</th>
                        </tr>
                      </thead>
                      <tbody>
                        {ledgerRows.map((row) => (
                          <tr key={`${row.gl_account_id}-${row.financial_year}-${row.branch_id || 'all'}`} className="border-b border-slate-100">
                            <td className="px-3 py-2 text-slate-900">
                              <p className="font-medium">{row.gl_number || row.account_code}</p>
                              <p className="text-xs text-slate-500">{row.account_name}</p>
                            </td>
                            <td className="px-3 py-2 text-slate-700">{row.branch || row.branch_id || 'All'}</td>
                            <td className="px-3 py-2 text-slate-700">{row.currency}</td>
                            <td className="px-3 py-2 text-right text-slate-900">{money(row.opening_balance)}</td>
                            <td className="px-3 py-2 text-right text-slate-900">{money(row.debit)}</td>
                            <td className="px-3 py-2 text-right text-slate-900">{money(row.credit)}</td>
                            <td className="px-3 py-2 text-right text-slate-900">{money(row.balance)}</td>
                            <td className="px-3 py-2 text-right text-slate-900">{money(row.closing_balance)}</td>
                            <td className="px-3 py-2 text-slate-700">{row.financial_year}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'dayend' && (
            <div className="mt-5 grid gap-6 lg:grid-cols-[0.7fr_1.3fr]">
              <form
                className="grid gap-3"
                onSubmit={(event) => {
                  event.preventDefault();
                  runAction(
                    'dayend',
                    async () => {
                      await apiClient.closeDayEnd({
                        tenant_id: tenantId,
                        business_date: `${dayEndForm.business_date}T23:59:59`,
                        branch_id: dayEndForm.branch_id || undefined,
                        closed_by: user?.username || 'system',
                      });
                    },
                    'Day end closed.',
                  );
                }}
              >
                <h2 className="text-lg font-semibold text-slate-950">Close Business Date</h2>
                <input className="h-10 rounded-md border border-slate-300 px-3 text-sm" type="date" value={dayEndForm.business_date} onChange={(e) => setDayEndForm({ ...dayEndForm, business_date: e.target.value })} />
                <input className="h-10 rounded-md border border-slate-300 px-3 text-sm" placeholder="Optional branch id" value={dayEndForm.branch_id} onChange={(e) => setDayEndForm({ ...dayEndForm, branch_id: e.target.value })} />
                <button disabled={!!busyAction || !dayEndForm.business_date} className="h-10 rounded-md bg-blue-600 px-4 text-sm font-semibold text-white disabled:opacity-50">
                  {busyAction === 'dayend' ? 'Closing...' : 'Run EOD Close'}
                </button>
              </form>
              <div className="overflow-x-auto">
                <table className="w-full min-w-[520px] text-sm">
                  <thead>
                    <tr className="border-b border-slate-200 text-left text-slate-500">
                      <th className="px-3 py-2">Business Date</th>
                      <th className="px-3 py-2">Status</th>
                      <th className="px-3 py-2">Balanced</th>
                    </tr>
                  </thead>
                  <tbody>
                    {dayEndRows.map((row) => (
                      <tr key={row.id} className="border-b border-slate-100">
                        <td className="px-3 py-2 text-slate-900">{new Date(row.business_date).toLocaleDateString()}</td>
                        <td className="px-3 py-2 text-slate-700">{row.status}</td>
                        <td className="px-3 py-2 text-slate-700">{row.is_balanced}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </section>
      </div>
    </main>
  );
}
