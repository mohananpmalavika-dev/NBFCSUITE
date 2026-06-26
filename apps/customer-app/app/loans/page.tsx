'use client';

import { apiClient } from '@/lib/api';
import { useAuth } from '@/lib/auth-context';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useCallback, useEffect, useState } from 'react';

interface LoanAccount {
  id: string;
  account_number: string;
  sanction_amount: number;
  outstanding_principal: number;
  emi_amount: number;
  status: string;
}

interface LoanApplication {
  id: string;
  application_status: string;
  applied_amount: number;
  tenure_months: number;
  application_date: string;
}

export default function LoansPage() {
  const { user, token, isLoading } = useAuth();
  const router = useRouter();
  const [loans, setLoans] = useState<LoanAccount[]>([]);
  const [applications, setApplications] = useState<LoanApplication[]>([]);
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
      const [loansRes, appsRes] = await Promise.all([
        apiClient.getCustomerLoans(user.id),
        apiClient.getLoanApplications(user.id),
      ]);
      setLoans(loansRes.data.items || []);
      setApplications(appsRes.data.items || []);
    } catch {
      setMessage('Could not load loans from LOS/LMS services.');
    }
  }, [user, token]);

  useEffect(() => {
    loadLoans();
  }, [loadLoans]);

  if (isLoading) {
    return <div className="p-8 text-center">Loading...</div>;
  }

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-8">
      <div className="mx-auto max-w-7xl">
        <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <h1 className="text-3xl font-bold text-slate-950">Loans</h1>
            <p className="mt-1 text-slate-600">Track active loans and loan applications.</p>
          </div>
          <Link href="/apply-loan" className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700">
            Apply Loan
          </Link>
        </div>

        {message && (
          <div className="mb-4 rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
            {message}
          </div>
        )}

        <section className="mb-6 rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-xl font-semibold text-slate-950">Active Loan Accounts</h2>
          {loans.length === 0 ? (
            <p className="rounded-md bg-slate-50 p-4 text-sm text-slate-600">No active loans found.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[720px] text-sm">
                <thead>
                  <tr className="border-b border-slate-200 text-left text-slate-500">
                    <th className="px-3 py-3">Account</th>
                    <th className="px-3 py-3 text-right">Sanctioned</th>
                    <th className="px-3 py-3 text-right">Outstanding</th>
                    <th className="px-3 py-3 text-right">EMI</th>
                    <th className="px-3 py-3">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {loans.map((loan) => (
                    <tr key={loan.id} className="border-b border-slate-100">
                      <td className="px-3 py-3 font-medium text-slate-950">{loan.account_number}</td>
                      <td className="px-3 py-3 text-right">INR {loan.sanction_amount.toLocaleString()}</td>
                      <td className="px-3 py-3 text-right">INR {loan.outstanding_principal.toLocaleString()}</td>
                      <td className="px-3 py-3 text-right">INR {loan.emi_amount.toLocaleString()}</td>
                      <td className="px-3 py-3">{loan.status}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>

        <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-xl font-semibold text-slate-950">Applications</h2>
          {applications.length === 0 ? (
            <p className="rounded-md bg-slate-50 p-4 text-sm text-slate-600">No applications found.</p>
          ) : (
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              {applications.map((application) => (
                <article key={application.id} className="rounded-lg border border-slate-200 p-4">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="font-semibold text-slate-950">{application.id}</p>
                      <p className="text-sm text-slate-500">
                        Applied {new Date(application.application_date).toLocaleDateString()}
                      </p>
                    </div>
                    <span className="rounded bg-blue-50 px-2 py-1 text-xs font-semibold text-blue-700">
                      {application.application_status}
                    </span>
                  </div>
                  <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
                    <div>
                      <p className="text-slate-500">Amount</p>
                      <p className="font-medium text-slate-950">INR {application.applied_amount.toLocaleString()}</p>
                    </div>
                    <div>
                      <p className="text-slate-500">Tenure</p>
                      <p className="font-medium text-slate-950">{application.tenure_months} months</p>
                    </div>
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>
      </div>
    </main>
  );
}
