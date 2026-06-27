'use client';

import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api';
import { useAuth } from '@/lib/auth-context';

interface TrialBalanceRow {
  account_id: string;
  account_code: string;
  account_name: string;
  account_type: string;
  debit: number;
  credit: number;
}

export default function AccountingPage() {
  const { user, token, isLoading } = useAuth();
  const [rows, setRows] = useState<TrialBalanceRow[]>([]);
  const [totalDebit, setTotalDebit] = useState(0);
  const [totalCredit, setTotalCredit] = useState(0);
  const [isBalanced, setIsBalanced] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const tenantId = user?.tenant_id || user?.branch_id || user?.organization_id || user?.id || null;
    if (!isLoading && token) {
      if (!tenantId) {
        setError('Unable to determine tenant context for accounting data.');
        return;
      }

      apiClient
        .getTrialBalance(tenantId)
        .then((response) => {
          setRows(response.data.rows || []);
          setTotalDebit(response.data.total_debit || 0);
          setTotalCredit(response.data.total_credit || 0);
          setIsBalanced(response.data.is_balanced || false);
        })
        .catch((err) => {
          console.error('Failed to load trial balance', err);
          setError('Unable to load accounting data at this time.');
        });
    }
  }, [isLoading, token, user]);

  if (isLoading || !token) {
    return <div className="p-8 text-center">Loading accounting data...</div>;
  }

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-8">
      <div className="mx-auto max-w-6xl">
        <section className="mb-8 rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
          <p className="text-sm font-semibold uppercase tracking-wide text-blue-700">Accounting</p>
          <h1 className="mt-2 text-3xl font-bold text-slate-950">General Ledger</h1>
          <p className="mt-2 max-w-2xl text-slate-600">
            View tenant GL balances and trial balance status for ledger posting visibility.
          </p>
        </section>

        {error ? (
          <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-700">
            {error}
          </div>
        ) : (
          <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-4 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
              <div>
                <h2 className="text-xl font-semibold text-slate-900">Trial Balance</h2>
                <p className="mt-1 text-sm text-slate-600">Balances are loaded from the accounting ledger service.</p>
              </div>
              <div className="rounded-xl bg-slate-50 px-4 py-3 text-sm text-slate-700">
                {isBalanced ? 'Balanced' : 'Not balanced'}
              </div>
            </div>

            <div className="overflow-x-auto">
              {rows.length === 0 ? (
                <div className="rounded-lg border border-slate-200 bg-slate-50 p-6 text-sm text-slate-700">
                  No accounting ledger rows are available for this tenant.
                </div>
              ) : (
                <table className="min-w-full divide-y divide-slate-200">
                  <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-600">
                    <tr>
                      <th className="px-4 py-3">Code</th>
                      <th className="px-4 py-3">Name</th>
                      <th className="px-4 py-3">Type</th>
                      <th className="px-4 py-3 text-right">Debit</th>
                      <th className="px-4 py-3 text-right">Credit</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200">
                    {rows.map((row) => (
                      <tr key={row.account_id} className="hover:bg-slate-50">
                        <td className="px-4 py-3 text-sm text-slate-900">{row.account_code}</td>
                        <td className="px-4 py-3 text-sm text-slate-700">{row.account_name}</td>
                        <td className="px-4 py-3 text-sm text-slate-700">{row.account_type}</td>
                        <td className="px-4 py-3 text-right text-sm text-slate-900">{row.debit.toFixed(2)}</td>
                        <td className="px-4 py-3 text-right text-sm text-slate-900">{row.credit.toFixed(2)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>

            <div className="mt-6 flex flex-col gap-4 border-t border-slate-200 pt-4 text-sm text-slate-700 md:flex-row md:justify-between">
              <div>Total Debit: <span className="font-semibold">{totalDebit.toFixed(2)}</span></div>
              <div>Total Credit: <span className="font-semibold">{totalCredit.toFixed(2)}</span></div>
            </div>
          </section>
        )}
      </div>
    </main>
  );
}
