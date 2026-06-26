'use client';

import { apiClient } from '@/lib/api';
import { useAuth } from '@/lib/auth-context';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useCallback, useEffect, useMemo, useState } from 'react';

interface DepositAccount {
  id: string;
  account_number: string;
  principal_amount: number;
  current_balance: number;
  interest_rate: number;
  start_date: string;
  maturity_date: string;
  status: string;
}

interface DepositTransaction {
  id: string;
  transaction_type: string;
  amount: number;
  running_balance: number;
  description: string;
  reference?: string | null;
  transaction_date: string;
}

interface DepositStatement {
  opening_balance: number;
  closing_balance: number;
  transactions: DepositTransaction[];
}

function formatCurrency(value: number) {
  return `INR ${Number(value || 0).toLocaleString()}`;
}

function csvEscape(value: string | number | null | undefined) {
  const normalized = String(value ?? '');
  return `"${normalized.replace(/"/g, '""')}"`;
}

export default function DepositsPage() {
  const { user, token, isLoading } = useAuth();
  const router = useRouter();
  const [accounts, setAccounts] = useState<DepositAccount[]>([]);
  const [selectedAccountId, setSelectedAccountId] = useState('');
  const [statement, setStatement] = useState<DepositStatement | null>(null);
  const [message, setMessage] = useState('');

  const selectedAccount = useMemo(
    () => accounts.find((account) => account.id === selectedAccountId) || accounts[0],
    [accounts, selectedAccountId],
  );

  useEffect(() => {
    if (!isLoading && !token) {
      router.push('/login');
    }
  }, [token, isLoading, router]);

  const loadDeposits = useCallback(async () => {
    if (!user || !token) {
      return;
    }
    setMessage('');
    try {
      const accountsRes = await apiClient.getCustomerDepositAccounts(user.id);
      const items = accountsRes.data.items || [];
      setAccounts(items);
      setSelectedAccountId(items[0]?.id || '');
    } catch {
      setMessage('Could not load deposit accounts from the deposits service.');
    }
  }, [user, token]);

  useEffect(() => {
    loadDeposits();
  }, [loadDeposits]);

  useEffect(() => {
    async function loadStatement() {
      if (!selectedAccount) {
        setStatement(null);
        return;
      }
      const fromDate = new Date(selectedAccount.start_date).toISOString();
      const toDate = new Date().toISOString();
      try {
        const statementRes = await apiClient.getDepositStatement(selectedAccount.id, fromDate, toDate);
        setStatement(statementRes.data);
      } catch {
        setStatement(null);
      }
    }

    loadStatement();
  }, [selectedAccount]);

  const downloadStatement = () => {
    if (!selectedAccount || !statement) {
      return;
    }

    const rows = [
      ['Account Number', selectedAccount.account_number],
      ['Opening Balance', statement.opening_balance],
      ['Closing Balance', statement.closing_balance],
      [],
      ['Date', 'Description', 'Type', 'Amount', 'Running Balance', 'Reference'],
      ...statement.transactions.map((transaction) => [
        new Date(transaction.transaction_date).toLocaleDateString(),
        transaction.description,
        transaction.transaction_type,
        transaction.amount,
        transaction.running_balance,
        transaction.reference || '',
      ]),
    ];
    const csv = rows.map((row) => row.map(csvEscape).join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${selectedAccount.account_number}-statement.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  if (isLoading) {
    return <div className="p-8 text-center">Loading...</div>;
  }

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-8">
      <div className="mx-auto max-w-7xl">
        <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <h1 className="text-3xl font-bold text-slate-950">Deposits</h1>
            <p className="mt-1 text-slate-600">View savings, fixed deposits, maturity values, and statements.</p>
          </div>
          <Link href="/" className="rounded-md border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-white">
            Dashboard
          </Link>
        </div>

        {message && (
          <div className="mb-4 rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
            {message}
          </div>
        )}

        {accounts.length === 0 ? (
          <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
            <p className="rounded-md bg-slate-50 p-4 text-sm text-slate-600">No deposit accounts found.</p>
          </section>
        ) : (
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-[360px_1fr]">
            <section className="space-y-3">
              {accounts.map((account) => (
                <button
                  key={account.id}
                  type="button"
                  onClick={() => setSelectedAccountId(account.id)}
                  className={`w-full rounded-lg border p-4 text-left shadow-sm transition ${
                    selectedAccount?.id === account.id
                      ? 'border-blue-300 bg-blue-50'
                      : 'border-slate-200 bg-white hover:border-blue-200'
                  }`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="font-semibold text-slate-950">{account.account_number}</p>
                      <p className="mt-1 text-sm text-slate-500">{account.status}</p>
                    </div>
                    <span className="rounded bg-white px-2 py-1 text-xs font-semibold text-blue-700">
                      {account.interest_rate}%
                    </span>
                  </div>
                  <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
                    <div>
                      <p className="text-slate-500">Balance</p>
                      <p className="font-medium text-slate-950">{formatCurrency(account.current_balance)}</p>
                    </div>
                    <div>
                      <p className="text-slate-500">Principal</p>
                      <p className="font-medium text-slate-950">{formatCurrency(account.principal_amount)}</p>
                    </div>
                  </div>
                </button>
              ))}
            </section>

            <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
              <div className="mb-5 flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                <div>
                  <h2 className="text-xl font-semibold text-slate-950">Statement</h2>
                  <p className="mt-1 text-sm text-slate-500">
                    {selectedAccount?.account_number} - Matures {selectedAccount ? new Date(selectedAccount.maturity_date).toLocaleDateString() : ''}
                  </p>
                </div>
                {statement && (
                  <div className="flex flex-col items-start gap-3 sm:items-end">
                    <div className="grid grid-cols-2 gap-3 text-left text-sm sm:text-right">
                      <div>
                        <p className="text-slate-500">Opening</p>
                        <p className="font-semibold text-slate-950">{formatCurrency(statement.opening_balance)}</p>
                      </div>
                      <div>
                        <p className="text-slate-500">Closing</p>
                        <p className="font-semibold text-slate-950">{formatCurrency(statement.closing_balance)}</p>
                      </div>
                    </div>
                    <button
                      type="button"
                      onClick={downloadStatement}
                      disabled={statement.transactions.length === 0}
                      className="rounded-md border border-slate-300 px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      Download CSV
                    </button>
                  </div>
                )}
              </div>

              {!statement || statement.transactions.length === 0 ? (
                <p className="rounded-md bg-slate-50 p-4 text-sm text-slate-600">No statement entries for this period.</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full min-w-[720px] text-sm">
                    <thead>
                      <tr className="border-b border-slate-200 text-left text-slate-500">
                        <th className="px-3 py-3">Date</th>
                        <th className="px-3 py-3">Description</th>
                        <th className="px-3 py-3">Type</th>
                        <th className="px-3 py-3 text-right">Amount</th>
                        <th className="px-3 py-3 text-right">Balance</th>
                      </tr>
                    </thead>
                    <tbody>
                      {statement.transactions.map((transaction) => (
                        <tr key={transaction.id} className="border-b border-slate-100">
                          <td className="px-3 py-3 text-slate-600">
                            {new Date(transaction.transaction_date).toLocaleDateString()}
                          </td>
                          <td className="px-3 py-3 font-medium text-slate-950">{transaction.description}</td>
                          <td className="px-3 py-3 capitalize text-slate-600">{transaction.transaction_type}</td>
                          <td className="px-3 py-3 text-right">{formatCurrency(transaction.amount)}</td>
                          <td className="px-3 py-3 text-right">{formatCurrency(transaction.running_balance)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </section>
          </div>
        )}
      </div>
    </main>
  );
}
