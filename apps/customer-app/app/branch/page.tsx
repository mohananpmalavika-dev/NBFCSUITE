'use client';

import { apiClient } from '@/lib/api';
import { useAuth } from '@/lib/auth-context';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { ChangeEvent, FormEvent, useCallback, useEffect, useMemo, useState } from 'react';

interface Customer {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  kyc_status: string;
  branch_id?: string | null;
}

interface LoanProduct {
  product_code: string;
  product_name: string;
  min_amount: number;
  min_tenor: number;
  base_rate: number;
}

interface LoanApplication {
  id: string;
  customer_id: string;
  branch_id?: string | null;
  application_status: string;
  applied_amount: number;
  tenure_months: number;
  application_date: string;
}

interface LoanAccount {
  id: string;
  account_number: string;
  customer_id: string;
  branch_id?: string | null;
  sanction_amount: number;
  disbursed_amount: number;
  outstanding_principal: number;
  emi_amount: number;
  status: string;
}

const statusFilters = ['submitted', 'under_review', 'approved', 'disbursed', 'draft'];

function formatCurrency(value: number) {
  return `INR ${Number(value || 0).toLocaleString()}`;
}

export default function BranchPortalPage() {
  const { user, token, isLoading } = useAuth();
  const router = useRouter();
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [applications, setApplications] = useState<LoanApplication[]>([]);
  const [loans, setLoans] = useState<LoanAccount[]>([]);
  const [products, setProducts] = useState<LoanProduct[]>([]);
  const [selectedStatus, setSelectedStatus] = useState('submitted');
  const [message, setMessage] = useState('');
  const [busyId, setBusyId] = useState('');
  const [formData, setFormData] = useState({
    customerId: '',
    productCode: '',
    appliedAmount: '',
    tenureMonths: '',
  });

  const selectedProduct = useMemo(
    () => products.find((product) => product.product_code === formData.productCode),
    [products, formData.productCode],
  );

  const branchId = user?.branch_id || undefined;

  useEffect(() => {
    if (!isLoading && !token) {
      router.push('/login');
    }
  }, [token, isLoading, router]);

  const loadBranchWorkspace = useCallback(async () => {
    if (!token) {
      return;
    }

    setMessage('');
    try {
      const [customersRes, appsRes, loansRes, productsRes] = await Promise.all([
        apiClient.getCustomers(branchId ? { branch_id: branchId, limit: 50 } : { limit: 50 }),
        apiClient.getLoanApplications({ branch_id: branchId, status: selectedStatus, limit: 50 }),
        apiClient.getLoans(branchId ? { branch_id: branchId, limit: 50 } : { limit: 50 }),
        apiClient.getLoanProducts(),
      ]);
      const customerItems = customersRes.data.items || [];
      const productItems = productsRes.data || [];
      setCustomers(customerItems);
      setApplications(appsRes.data.items || []);
      setLoans(loansRes.data.items || []);
      setProducts(productItems);
      setFormData((previous) => ({
        customerId: previous.customerId || customerItems[0]?.id || '',
        productCode: previous.productCode || productItems[0]?.product_code || '',
        appliedAmount: previous.appliedAmount || String(productItems[0]?.min_amount || ''),
        tenureMonths: previous.tenureMonths || String(productItems[0]?.min_tenor || ''),
      }));
    } catch {
      setMessage('Could not load the branch workspace. Check service availability and scope headers.');
    }
  }, [branchId, selectedStatus, token]);

  useEffect(() => {
    loadBranchWorkspace();
  }, [loadBranchWorkspace]);

  const handleFormChange = (event: ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = event.target;
    if (name === 'productCode') {
      const product = products.find((item) => item.product_code === value);
      setFormData((previous) => ({
        ...previous,
        productCode: value,
        appliedAmount: product ? String(product.min_amount) : previous.appliedAmount,
        tenureMonths: product ? String(product.min_tenor) : previous.tenureMonths,
      }));
      return;
    }
    setFormData((previous) => ({ ...previous, [name]: value }));
  };

  const createApplication = async (event: FormEvent) => {
    event.preventDefault();
    if (!formData.customerId || !selectedProduct) {
      setMessage('Select a customer and loan product.');
      return;
    }

    setBusyId('create-application');
    setMessage('');
    try {
      await apiClient.applyForLoan({
        customer_id: formData.customerId,
        branch_id: branchId,
        product_code: selectedProduct.product_code,
        applied_amount: Number(formData.appliedAmount),
        tenure_months: Number(formData.tenureMonths),
      });
      setSelectedStatus('draft');
      setMessage('Draft application created for the selected branch customer.');
      await loadBranchWorkspace();
    } catch {
      setMessage('Could not create the branch application.');
    } finally {
      setBusyId('');
    }
  };

  const runApplicationAction = async (application: LoanApplication, action: 'submit' | 'underwrite' | 'approve') => {
    setBusyId(`${action}-${application.id}`);
    setMessage('');
    try {
      if (action === 'submit') {
        await apiClient.submitLoanApplication(application.id);
      } else if (action === 'underwrite') {
        await apiClient.underwriteLoanApplication(application.id);
      } else {
        await apiClient.decideLoanApplication(application.id, {
          decision: 'approved',
          approved_amount: application.applied_amount,
          approved_tenure_months: application.tenure_months,
          approved_interest_rate: selectedProduct?.base_rate || 14.5,
        });
      }
      setMessage(`Application ${action} completed.`);
      await loadBranchWorkspace();
    } catch {
      setMessage(`Could not ${action} application.`);
    } finally {
      setBusyId('');
    }
  };

  const runLoanAction = async (loan: LoanAccount, action: 'disburse' | 'overdue') => {
    setBusyId(`${action}-${loan.id}`);
    setMessage('');
    try {
      if (action === 'disburse') {
        await apiClient.disburseLoan(loan.id, {
          amount: loan.sanction_amount - loan.disbursed_amount,
          reference: `BRANCH-${Date.now()}`,
        });
        setMessage('Loan disbursement posted.');
      } else {
        const response = await apiClient.computeLoanOverdue(loan.id);
        setMessage(
          `DPD ${response.data.days_past_due}, penalty ${formatCurrency(response.data.penalty_amount)} computed.`,
        );
      }
      await loadBranchWorkspace();
    } catch {
      setMessage(`Could not ${action} loan.`);
    } finally {
      setBusyId('');
    }
  };

  if (isLoading) {
    return <div className="p-8 text-center">Loading...</div>;
  }

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-8">
      <div className="mx-auto max-w-7xl">
        <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-wide text-blue-700">Branch Portal</p>
            <h1 className="mt-1 text-3xl font-bold text-slate-950">Core Lending Operations</h1>
            <p className="mt-1 text-slate-600">
              {branchId ? `Scoped to branch ${branchId}` : 'Using organization scope from the signed-in user.'}
            </p>
          </div>
          <Link href="/" className="rounded-md border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-white">
            Dashboard
          </Link>
        </div>

        {message && (
          <div className="mb-4 rounded-md border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-900">
            {message}
          </div>
        )}

        <section className="mb-6 rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-xl font-semibold text-slate-950">Create Branch Application</h2>
          <form onSubmit={createApplication} className="grid grid-cols-1 gap-4 lg:grid-cols-[1.4fr_1fr_160px_160px_auto]">
            <label className="block">
              <span className="mb-1 block text-sm font-medium text-slate-700">Customer CIF</span>
              <select
                name="customerId"
                value={formData.customerId}
                onChange={handleFormChange}
                className="w-full rounded-md border border-slate-300 px-3 py-2"
              >
                <option value="">Select customer</option>
                {customers.map((customer) => (
                  <option key={customer.id} value={customer.id}>
                    {customer.first_name} {customer.last_name} - {customer.phone}
                  </option>
                ))}
              </select>
            </label>
            <label className="block">
              <span className="mb-1 block text-sm font-medium text-slate-700">Product</span>
              <select
                name="productCode"
                value={formData.productCode}
                onChange={handleFormChange}
                className="w-full rounded-md border border-slate-300 px-3 py-2"
              >
                {products.map((product) => (
                  <option key={product.product_code} value={product.product_code}>
                    {product.product_name}
                  </option>
                ))}
              </select>
            </label>
            <label className="block">
              <span className="mb-1 block text-sm font-medium text-slate-700">Amount</span>
              <input
                name="appliedAmount"
                type="number"
                value={formData.appliedAmount}
                onChange={handleFormChange}
                className="w-full rounded-md border border-slate-300 px-3 py-2"
              />
            </label>
            <label className="block">
              <span className="mb-1 block text-sm font-medium text-slate-700">Tenure</span>
              <input
                name="tenureMonths"
                type="number"
                value={formData.tenureMonths}
                onChange={handleFormChange}
                className="w-full rounded-md border border-slate-300 px-3 py-2"
              />
            </label>
            <button
              type="submit"
              disabled={busyId === 'create-application' || customers.length === 0}
              className="self-end rounded-md bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              Create
            </button>
          </form>
        </section>

        <div className="grid grid-cols-1 gap-6 xl:grid-cols-[1fr_1fr]">
          <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <h2 className="text-xl font-semibold text-slate-950">Application Queue</h2>
              <select
                value={selectedStatus}
                onChange={(event) => setSelectedStatus(event.target.value)}
                className="rounded-md border border-slate-300 px-3 py-2 text-sm"
              >
                {statusFilters.map((status) => (
                  <option key={status} value={status}>
                    {status}
                  </option>
                ))}
              </select>
            </div>
            {applications.length === 0 ? (
              <p className="rounded-md bg-slate-50 p-4 text-sm text-slate-600">No applications in this queue.</p>
            ) : (
              <div className="space-y-3">
                {applications.map((application) => (
                  <article key={application.id} className="rounded-lg border border-slate-200 p-4">
                    <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                      <div>
                        <p className="font-semibold text-slate-950">{application.id}</p>
                        <p className="mt-1 text-sm text-slate-500">
                          {application.customer_id} - {formatCurrency(application.applied_amount)} - {application.tenure_months} months
                        </p>
                      </div>
                      <span className="w-fit rounded bg-slate-100 px-2 py-1 text-xs font-semibold text-slate-700">
                        {application.application_status}
                      </span>
                    </div>
                    <div className="mt-4 flex flex-wrap gap-2">
                      <button
                        type="button"
                        onClick={() => runApplicationAction(application, 'submit')}
                        disabled={busyId === `submit-${application.id}` || application.application_status !== 'draft'}
                        className="rounded-md border border-slate-300 px-3 py-2 text-sm font-medium text-slate-700 disabled:opacity-50"
                      >
                        Submit
                      </button>
                      <button
                        type="button"
                        onClick={() => runApplicationAction(application, 'underwrite')}
                        disabled={busyId === `underwrite-${application.id}` || !['submitted', 'under_review'].includes(application.application_status)}
                        className="rounded-md border border-slate-300 px-3 py-2 text-sm font-medium text-slate-700 disabled:opacity-50"
                      >
                        Underwrite
                      </button>
                      <button
                        type="button"
                        onClick={() => runApplicationAction(application, 'approve')}
                        disabled={busyId === `approve-${application.id}` || !['submitted', 'under_review'].includes(application.application_status)}
                        className="rounded-md bg-emerald-600 px-3 py-2 text-sm font-medium text-white disabled:opacity-50"
                      >
                        Approve + Book
                      </button>
                    </div>
                  </article>
                ))}
              </div>
            )}
          </section>

          <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-xl font-semibold text-slate-950">Loan Accounts</h2>
            {loans.length === 0 ? (
              <p className="rounded-md bg-slate-50 p-4 text-sm text-slate-600">No loan accounts found.</p>
            ) : (
              <div className="space-y-3">
                {loans.map((loan) => (
                  <article key={loan.id} className="rounded-lg border border-slate-200 p-4">
                    <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                      <div>
                        <p className="font-semibold text-slate-950">{loan.account_number}</p>
                        <p className="mt-1 text-sm text-slate-500">
                          EMI {formatCurrency(loan.emi_amount)} - Outstanding {formatCurrency(loan.outstanding_principal)}
                        </p>
                      </div>
                      <span className="w-fit rounded bg-slate-100 px-2 py-1 text-xs font-semibold text-slate-700">
                        {loan.status}
                      </span>
                    </div>
                    <div className="mt-4 flex flex-wrap gap-2">
                      <button
                        type="button"
                        onClick={() => runLoanAction(loan, 'disburse')}
                        disabled={busyId === `disburse-${loan.id}` || loan.disbursed_amount >= loan.sanction_amount}
                        className="rounded-md bg-blue-600 px-3 py-2 text-sm font-medium text-white disabled:opacity-50"
                      >
                        Disburse
                      </button>
                      <button
                        type="button"
                        onClick={() => runLoanAction(loan, 'overdue')}
                        disabled={busyId === `overdue-${loan.id}`}
                        className="rounded-md border border-slate-300 px-3 py-2 text-sm font-medium text-slate-700 disabled:opacity-50"
                      >
                        Compute DPD
                      </button>
                      <Link
                        href="/payments"
                        className="rounded-md border border-slate-300 px-3 py-2 text-sm font-medium text-slate-700"
                      >
                        Record Payment
                      </Link>
                    </div>
                  </article>
                ))}
              </div>
            )}
          </section>
        </div>
      </div>
    </main>
  );
}
