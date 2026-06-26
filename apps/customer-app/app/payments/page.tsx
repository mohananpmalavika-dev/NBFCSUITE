'use client';

import { apiClient } from '@/lib/api';
import { useAuth } from '@/lib/auth-context';
import { useRouter } from 'next/navigation';
import { FormEvent, useCallback, useEffect, useState } from 'react';

interface LoanAccount {
  id: string;
  account_number: string;
  emi_amount: number;
  outstanding_principal: number;
  status: string;
}

interface Payment {
  id?: string;
  transaction_id?: string;
  transaction_date: string;
  payment_mode: string;
  amount: number;
  principal_paid?: number;
  interest_paid?: number;
  reference?: string;
  status: string;
}

export default function PaymentsPage() {
  const { user, token, isLoading } = useAuth();
  const router = useRouter();
  const [loans, setLoans] = useState<LoanAccount[]>([]);
  const [payments, setPayments] = useState<Payment[]>([]);
  const [loanId, setLoanId] = useState('');
  const [paymentAmount, setPaymentAmount] = useState('');
  const [paymentMode, setPaymentMode] = useState('UPI');
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    if (!isLoading && !token) {
      router.push('/login');
    }
  }, [token, isLoading, router]);

  const loadLoans = useCallback(async () => {
    if (!user || !token) {
      return;
    }
    setMessage('');
    try {
      const response = await apiClient.getCustomerLoans(user.id);
      const loanItems = response.data.items || [];
      setLoans(loanItems);
      if (!loanId && loanItems.length > 0) {
        setLoanId(loanItems[0].id);
      }
    } catch {
      setMessage('Could not load loan accounts.');
    }
  }, [user, token, loanId]);

  const loadPayments = useCallback(async () => {
    if (!loanId) {
      setPayments([]);
      return;
    }
    try {
      const response = await apiClient.getLoanPayments(loanId);
      setPayments(response.data.payments || []);
    } catch {
      setMessage('Could not load payment history.');
    }
  }, [loanId]);

  useEffect(() => {
    loadLoans();
  }, [loadLoans]);

  useEffect(() => {
    loadPayments();
  }, [loadPayments]);

  const handleMakePayment = async (event: FormEvent) => {
    event.preventDefault();
    setSubmitting(true);
    setMessage('');

    try {
      const amount = Number(paymentAmount);
      if (!loanId || !amount || amount <= 0) {
        setMessage('Select a loan and enter a valid amount.');
        return;
      }

      await apiClient.makePayment(loanId, {
        amount,
        payment_mode: paymentMode,
        reference: `WEB-${Date.now()}`,
      });

      setPaymentAmount('');
      setMessage('Payment recorded successfully.');
      await Promise.all([loadLoans(), loadPayments()]);
    } catch {
      setMessage('Payment failed. Please try again.');
    } finally {
      setSubmitting(false);
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
            <h1 className="text-3xl font-bold text-slate-950">Payments</h1>
            <p className="mt-1 text-slate-600">Record EMI payments and view LMS history.</p>
          </div>
          <button
            onClick={() => router.push('/loans')}
            className="rounded-md border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-white"
          >
            Loans
          </button>
        </div>

        {message && (
          <div className="mb-4 rounded-md border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-900">
            {message}
          </div>
        )}

        <section className="mb-6 rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-xl font-semibold text-slate-950">Make a Payment</h2>
          <form onSubmit={handleMakePayment} className="grid grid-cols-1 gap-4 lg:grid-cols-[1fr_180px_180px_auto]">
            <label className="block">
              <span className="mb-1 block text-sm font-medium text-slate-700">Loan account</span>
              <select
                value={loanId}
                onChange={(event) => setLoanId(event.target.value)}
                className="w-full rounded-md border border-slate-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
              >
                <option value="">Choose a loan</option>
                {loans.map((loan) => (
                  <option key={loan.id} value={loan.id}>
                    {loan.account_number} - EMI INR {Math.round(loan.emi_amount).toLocaleString()}
                  </option>
                ))}
              </select>
            </label>
            <label className="block">
              <span className="mb-1 block text-sm font-medium text-slate-700">Amount</span>
              <input
                type="number"
                value={paymentAmount}
                onChange={(event) => setPaymentAmount(event.target.value)}
                className="w-full rounded-md border border-slate-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
              />
            </label>
            <label className="block">
              <span className="mb-1 block text-sm font-medium text-slate-700">Mode</span>
              <select
                value={paymentMode}
                onChange={(event) => setPaymentMode(event.target.value)}
                className="w-full rounded-md border border-slate-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
              >
                <option value="UPI">UPI</option>
                <option value="NEFT">NEFT</option>
                <option value="CASH">Cash</option>
                <option value="CARD">Card</option>
              </select>
            </label>
            <button
              type="submit"
              disabled={submitting || loans.length === 0}
              className="self-end rounded-md bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {submitting ? 'Recording...' : 'Pay'}
            </button>
          </form>
        </section>

        <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-xl font-semibold text-slate-950">Payment History</h2>
          {payments.length === 0 ? (
            <p className="rounded-md bg-slate-50 p-4 text-sm text-slate-600">No payments found for the selected loan.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[760px] text-sm">
                <thead>
                  <tr className="border-b border-slate-200 text-left text-slate-500">
                    <th className="px-3 py-3">Date</th>
                    <th className="px-3 py-3">Mode</th>
                    <th className="px-3 py-3 text-right">Amount</th>
                    <th className="px-3 py-3 text-right">Principal</th>
                    <th className="px-3 py-3 text-right">Interest</th>
                    <th className="px-3 py-3">Reference</th>
                    <th className="px-3 py-3">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {payments.map((payment) => (
                    <tr key={payment.id || payment.transaction_id} className="border-b border-slate-100">
                      <td className="px-3 py-3">{new Date(payment.transaction_date).toLocaleDateString()}</td>
                      <td className="px-3 py-3">{payment.payment_mode}</td>
                      <td className="px-3 py-3 text-right">INR {payment.amount.toLocaleString()}</td>
                      <td className="px-3 py-3 text-right">INR {(payment.principal_paid || 0).toLocaleString()}</td>
                      <td className="px-3 py-3 text-right">INR {(payment.interest_paid || 0).toLocaleString()}</td>
                      <td className="px-3 py-3">{payment.reference || payment.transaction_id}</td>
                      <td className="px-3 py-3">{payment.status}</td>
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
