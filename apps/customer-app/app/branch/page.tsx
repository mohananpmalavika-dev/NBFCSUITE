'use client';

import { apiClient } from '@/lib/api';
import { useAuth } from '@/lib/auth-context';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { ChangeEvent, FormEvent, ReactNode, useCallback, useEffect, useMemo, useState } from 'react';

interface Customer {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  kyc_status: string;
  branch_id?: string | null;
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
  outstanding_interest: number;
  emi_amount: number;
  status: string;
}

interface LoanProduct {
  product_code: string;
  product_name: string;
  min_amount: number;
  min_tenor: number;
  base_rate: number;
}

const branchRoles = new Set(['admin', 'branch_manager', 'regional_manager', 'lender', 'collector']);

function formatCurrency(value: number) {
  return `INR ${Number(value || 0).toLocaleString()}`;
}

function roleName(role: string | { name: string }) {
  return typeof role === 'string' ? role : role.name;
}

export default function BranchPortalPage() {
  const { user, token, isLoading } = useAuth();
  const router = useRouter();
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [applications, setApplications] = useState<LoanApplication[]>([]);
  const [loans, setLoans] = useState<LoanAccount[]>([]);
  const [products, setProducts] = useState<LoanProduct[]>([]);
  const [selectedCustomerId, setSelectedCustomerId] = useState('');
  const [productCode, setProductCode] = useState('');
  const [amount, setAmount] = useState('');
  const [tenure, setTenure] = useState('');
  const [paymentByLoan, setPaymentByLoan] = useState<Record<string, string>>({});
  const [busyAction, setBusyAction] = useState('');
  const [message, setMessage] = useState('');

  const roles = useMemo(() => new Set((user?.roles || []).map(roleName)), [user]);
  const canOpenBranchPortal = useMemo(
    () => roles.size === 0 || Array.from(roles).some((role) => branchRoles.has(role)),
    [roles],
  );
  const scopeParams = useMemo(
    () => (user?.branch_id ? { branch_id: user.branch_id } : undefined),
    [user?.branch_id],
  );

  useEffect(() => {
    if (!isLoading && !token) {
      router.push('/login');
    }
  }, [token, isLoading, router]);

  const loadBranchWork = useCallback(async () => {
    if (!token || !user) {
      return;
    }
    setMessage('');
    try {
      const [customersRes, appsRes, loansRes, productsRes] = await Promise.all([
        apiClient.getCustomers(scopeParams),
        apiClient.getLoanApplications(scopeParams),
        apiClient.getLoans(scopeParams),
        apiClient.getLoanProducts(),
      ]);
      const customerItems = customersRes.data.items || [];
      const productItems = productsRes.data || [];
      setCustomers(customerItems);
      setApplications(appsRes.data.items || []);
      setLoans(loansRes.data.items || []);
      setProducts(productItems);
      setSelectedCustomerId((current) => current || customerItems[0]?.id || '');
      if (!productCode && productItems[0]) {
        setProductCode(productItems[0].product_code);
        setAmount(String(productItems[0].min_amount));
        setTenure(String(productItems[0].min_tenor));
      }
    } catch {
      setMessage('Branch workspace data could not be loaded.');
    }
  }, [productCode, scopeParams, token, user]);

  useEffect(() => {
    loadBranchWork();
  }, [loadBranchWork]);

  const customerById = useMemo(() => {
    return new Map(customers.map((customer) => [customer.id, customer]));
  }, [customers]);

  const selectedProduct = products.find((product) => product.product_code === productCode);

  const handleProductChange = (event: ChangeEvent<HTMLSelectElement>) => {
    const nextProduct = products.find((product) => product.product_code === event.target.value);
    setProductCode(event.target.value);
    if (nextProduct) {
      setAmount(String(nextProduct.min_amount));
      setTenure(String(nextProduct.min_tenor));
    }
  };

  const runAction = async (key: string, action: () => Promise<void>, successMessage: string) => {
    setBusyAction(key);
    setMessage('');
    try {
      await action();
      setMessage(successMessage);
      await loadBranchWork();
    } catch {
      setMessage('Action failed. Review the record state and try again.');
    } finally {
      setBusyAction('');
    }
  };

  const createApplication = async (event: FormEvent) => {
    event.preventDefault();
    if (!selectedCustomerId || !selectedProduct) {
      setMessage('Select a customer and loan product.');
      return;
    }
    await runAction(
      'create-application',
      () =>
        apiClient.applyForLoan({
          customer_id: selectedCustomerId,
          branch_id: user?.branch_id || customerById.get(selectedCustomerId)?.branch_id || undefined,
          product_code: selectedProduct.product_code,
          applied_amount: Number(amount),
          tenure_months: Number(tenure),
        }).then(() => undefined),
      'Loan application created.',
    );
  };

  const approveApplication = (application: LoanApplication) =>
    runAction(
      `approve-${application.id}`,
      () =>
        apiClient
          .decideLoanApplication(application.id, {
            decision: 'approved',
            approved_amount: application.applied_amount,
            approved_tenure_months: application.tenure_months,
            approved_interest_rate: selectedProduct?.base_rate || 14.5,
          })
          .then(() => undefined),
      'Application approved and queued for booking.',
    );

  if (isLoading || !token) {
    return <div className="p-8 text-center">Loading...</div>;
  }

  if (!canOpenBranchPortal) {
    return (
      <main className="min-h-screen bg-slate-50 px-4 py-8">
        <div className="mx-auto max-w-3xl rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
          <h1 className="text-2xl font-bold text-slate-950">Branch Portal</h1>
          <p className="mt-2 text-sm text-slate-600">Your role is not enabled for branch operations.</p>
          <Link href="/" className="mt-5 inline-flex rounded-md border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700">
            Dashboard
          </Link>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-8">
      <div className="mx-auto max-w-7xl">
        <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase text-blue-700">Branch Portal</p>
            <h1 className="mt-1 text-3xl font-bold text-slate-950">
              {user?.branch_id ? `Branch ${user.branch_id}` : 'All Branches'}
            </h1>
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

        <section className="mb-6 grid grid-cols-1 gap-4 md:grid-cols-3">
          <Metric label="Customers" value={String(customers.length)} />
          <Metric label="Applications" value={String(applications.length)} />
          <Metric label="Loans" value={String(loans.length)} />
        </section>

        <section className="mb-6 rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-xl font-semibold text-slate-950">New Application</h2>
          <form onSubmit={createApplication} className="grid grid-cols-1 gap-4 lg:grid-cols-[1fr_220px_160px_160px_auto]">
            <label className="block">
              <span className="mb-1 block text-sm font-medium text-slate-700">Customer</span>
              <select
                value={selectedCustomerId}
                onChange={(event) => setSelectedCustomerId(event.target.value)}
                className="w-full rounded-md border border-slate-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
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
                value={productCode}
                onChange={handleProductChange}
                className="w-full rounded-md border border-slate-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
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
                type="number"
                value={amount}
                onChange={(event) => setAmount(event.target.value)}
                className="w-full rounded-md border border-slate-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
              />
            </label>
            <label className="block">
              <span className="mb-1 block text-sm font-medium text-slate-700">Tenure</span>
              <input
                type="number"
                value={tenure}
                onChange={(event) => setTenure(event.target.value)}
                className="w-full rounded-md border border-slate-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
              />
            </label>
            <button
              type="submit"
              disabled={busyAction === 'create-application' || customers.length === 0 || products.length === 0}
              className="self-end rounded-md bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              Create
            </button>
          </form>
        </section>

        <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
          <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-xl font-semibold text-slate-950">CIF Queue</h2>
            <div className="overflow-x-auto">
              <table className="w-full min-w-[640px] text-sm">
                <thead>
                  <tr className="border-b border-slate-200 text-left text-slate-500">
                    <th className="px-3 py-3">Customer</th>
                    <th className="px-3 py-3">Contact</th>
                    <th className="px-3 py-3">KYC</th>
                    <th className="px-3 py-3">Branch</th>
                  </tr>
                </thead>
                <tbody>
                  {customers.map((customer) => (
                    <tr key={customer.id} className="border-b border-slate-100">
                      <td className="px-3 py-3 font-medium text-slate-950">
                        {customer.first_name} {customer.last_name}
                      </td>
                      <td className="px-3 py-3 text-slate-600">{customer.phone}</td>
                      <td className="px-3 py-3 capitalize text-slate-600">{customer.kyc_status}</td>
                      <td className="px-3 py-3 text-slate-600">{customer.branch_id || '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-xl font-semibold text-slate-950">Application Queue</h2>
            <div className="space-y-3">
              {applications.length === 0 ? (
                <p className="rounded-md bg-slate-50 p-4 text-sm text-slate-600">No applications found.</p>
              ) : (
                applications.map((application) => (
                  <article key={application.id} className="rounded-lg border border-slate-200 p-4">
                    <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                      <div>
                        <p className="font-semibold text-slate-950">{application.id}</p>
                        <p className="mt-1 text-sm text-slate-500">
                          {customerById.get(application.customer_id)?.first_name || application.customer_id} -{' '}
                          {formatCurrency(application.applied_amount)}
                        </p>
                      </div>
                      <span className="w-fit rounded bg-slate-100 px-2 py-1 text-xs font-semibold capitalize text-slate-700">
                        {application.application_status}
                      </span>
                    </div>
                    <div className="mt-4 flex flex-wrap gap-2">
                      {application.application_status === 'draft' && (
                        <ActionButton
                          busy={busyAction === `submit-${application.id}`}
                          onClick={() =>
                            runAction(
                              `submit-${application.id}`,
                              () => apiClient.submitLoanApplication(application.id).then(() => undefined),
                              'Application submitted.',
                            )
                          }
                        >
                          Submit
                        </ActionButton>
                      )}
                      {application.application_status === 'submitted' && (
                        <ActionButton
                          busy={busyAction === `underwrite-${application.id}`}
                          onClick={() =>
                            runAction(
                              `underwrite-${application.id}`,
                              () => apiClient.underwriteLoanApplication(application.id).then(() => undefined),
                              'Underwriting completed.',
                            )
                          }
                        >
                          Underwrite
                        </ActionButton>
                      )}
                      {application.application_status === 'under_review' && (
                        <ActionButton busy={busyAction === `approve-${application.id}`} onClick={() => approveApplication(application)}>
                          Approve
                        </ActionButton>
                      )}
                    </div>
                  </article>
                ))
              )}
            </div>
          </section>
        </div>

        <section className="mt-6 rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-xl font-semibold text-slate-950">Loan Operations</h2>
          {loans.length === 0 ? (
            <p className="rounded-md bg-slate-50 p-4 text-sm text-slate-600">No loan accounts found.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[1080px] text-sm">
                <thead>
                  <tr className="border-b border-slate-200 text-left text-slate-500">
                    <th className="px-3 py-3">Account</th>
                    <th className="px-3 py-3 text-right">Sanctioned</th>
                    <th className="px-3 py-3 text-right">Disbursed</th>
                    <th className="px-3 py-3 text-right">Outstanding</th>
                    <th className="px-3 py-3">Status</th>
                    <th className="px-3 py-3">Payment</th>
                    <th className="px-3 py-3">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {loans.map((loan) => (
                    <tr key={loan.id} className="border-b border-slate-100">
                      <td className="px-3 py-3 font-medium text-slate-950">{loan.account_number}</td>
                      <td className="px-3 py-3 text-right">{formatCurrency(loan.sanction_amount)}</td>
                      <td className="px-3 py-3 text-right">{formatCurrency(loan.disbursed_amount)}</td>
                      <td className="px-3 py-3 text-right">
                        {formatCurrency(loan.outstanding_principal + loan.outstanding_interest)}
                      </td>
                      <td className="px-3 py-3 capitalize text-slate-600">{loan.status}</td>
                      <td className="px-3 py-3">
                        <input
                          type="number"
                          value={paymentByLoan[loan.id] || ''}
                          onChange={(event) =>
                            setPaymentByLoan((current) => ({ ...current, [loan.id]: event.target.value }))
                          }
                          placeholder={String(Math.round(loan.emi_amount))}
                          className="w-32 rounded-md border border-slate-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
                        />
                      </td>
                      <td className="px-3 py-3">
                        <div className="flex flex-wrap gap-2">
                          {loan.status === 'sanctioned' && (
                            <ActionButton
                              busy={busyAction === `disburse-${loan.id}`}
                              onClick={() =>
                                runAction(
                                  `disburse-${loan.id}`,
                                  () =>
                                    apiClient
                                      .disburseLoan(loan.id, {
                                        amount: loan.sanction_amount - loan.disbursed_amount,
                                        reference: `BR-${Date.now()}`,
                                      })
                                      .then(() => undefined),
                                  'Loan disbursed.',
                                )
                              }
                            >
                              Disburse
                            </ActionButton>
                          )}
                          <ActionButton
                            busy={busyAction === `overdue-${loan.id}`}
                            onClick={() =>
                              runAction(
                                `overdue-${loan.id}`,
                                () => apiClient.computeLoanOverdue(loan.id).then(() => undefined),
                                'Overdue status computed.',
                              )
                            }
                          >
                            DPD
                          </ActionButton>
                          <ActionButton
                            busy={busyAction === `payment-${loan.id}`}
                            onClick={() =>
                              runAction(
                                `payment-${loan.id}`,
                                () =>
                                  apiClient
                                    .makePayment(loan.id, {
                                      amount: Number(paymentByLoan[loan.id] || loan.emi_amount),
                                      payment_mode: 'BRANCH',
                                      reference: `BRPAY-${Date.now()}`,
                                    })
                                    .then(() => undefined),
                                'Payment recorded.',
                              )
                            }
                          >
                            Pay
                          </ActionButton>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </div>
    </main>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <p className="text-sm font-medium text-slate-500">{label}</p>
      <p className="mt-2 text-2xl font-bold text-slate-950">{value}</p>
    </div>
  );
}

function ActionButton({
  busy,
  onClick,
  children,
}: {
  busy: boolean;
  onClick: () => void;
  children: ReactNode;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={busy}
      className="rounded-md border border-slate-300 px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
    >
      {busy ? 'Working' : children}
    </button>
  );
}
