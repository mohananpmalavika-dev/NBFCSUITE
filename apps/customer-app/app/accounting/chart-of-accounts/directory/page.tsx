"use client";

import { useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import { AppShell } from '../../../components/AppShell';
import { accountingApi, DEFAULT_ACCOUNTING_TENANT } from '../../accountingApi';
import type { GLAccount, GLAccountPayload } from '../../accountingApi';
import { BooleanBadge, CoaPageFrame, CoaTable, EmptyState, LoadingBlock, StatusBadge, formatAmount } from '../coaComponents';

const initialForm = {
  account_code: '',
  account_name: '',
  account_type: 'asset',
  category: 'Assets',
  currency: 'INR',
  normal_balance: 'debit',
  posting_allowed: 'true',
  status: 'active',
};

export default function AccountDirectoryPage() {
  const [items, setItems] = useState<GLAccount[]>([]);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState('');
  const [type, setType] = useState('');
  const [creating, setCreating] = useState(false);
  const [form, setForm] = useState(initialForm);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const params = useMemo(() => {
    const parts = ['limit=100'];
    if (query.trim()) parts.push(`q=${encodeURIComponent(query.trim())}`);
    if (type) parts.push(`account_type=${encodeURIComponent(type)}`);
    return parts.join('&');
  }, [query, type]);

  async function load() {
    setLoading(true);
    try {
      const body = await accountingApi.listAccounts(DEFAULT_ACCOUNTING_TENANT, params);
      setItems(body.items);
    } catch {
      setItems([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, [params]);

  function update(field: keyof typeof initialForm, value: string) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function submit() {
    setSaving(true);
    setMessage(null);
    try {
      const payload: GLAccountPayload = {
        tenant_id: DEFAULT_ACCOUNTING_TENANT,
        account_code: form.account_code.trim(),
        account_name: form.account_name.trim(),
        account_type: form.account_type,
        category: form.category || form.account_type,
        currency: form.currency || 'INR',
        base_currency: form.currency || 'INR',
        normal_balance: form.normal_balance,
        posting_allowed: form.posting_allowed,
        allow_manual_posting: form.posting_allowed,
        allow_auto_posting: 'true',
        status: form.status,
        metadata: {
          short_name: form.account_name.trim().slice(0, 32),
          dimensions: ['Legal Entity', 'Branch', 'Cost Center', 'Product', 'Currency'],
          reporting: { trial_balance: true, balance_sheet: form.account_type === 'asset' || form.account_type === 'liability' || form.account_type === 'equity' },
        },
      };
      await accountingApi.createAccount(payload);
      setForm(initialForm);
      setCreating(false);
      setMessage('Account created');
      await load();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Create failed');
    } finally {
      setSaving(false);
    }
  }

  async function seedDefaults() {
    setSaving(true);
    setMessage(null);
    try {
      const result = await accountingApi.seedDefaults(DEFAULT_ACCOUNTING_TENANT);
      setMessage(`Seeded ${result.created_count} accounts`);
      await load();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Seed failed');
    } finally {
      setSaving(false);
    }
  }

  return (
    <AppShell>
      <CoaPageFrame
        title="Account Directory"
        description="Search, filter, create, and govern GL accounts used by posting rules, journals, and reporting."
      >
        <div className="space-y-4">
          <div className="flex flex-col gap-3 rounded-md border border-border-default bg-background-surface p-4 lg:flex-row lg:items-end lg:justify-between">
            <div className="grid flex-1 gap-3 md:grid-cols-[minmax(220px,1fr)_180px]">
              <label className="block space-y-1">
                <span className="text-sm font-semibold text-text-secondary">Search</span>
                <input
                  className="h-10 w-full rounded-md border border-border-default bg-background-surface px-3 text-sm outline-none focus:border-border-focus"
                  value={query}
                  onChange={(event) => setQuery(event.target.value)}
                  placeholder="GL code, account name, category"
                />
              </label>
              <label className="block space-y-1">
                <span className="text-sm font-semibold text-text-secondary">Type</span>
                <select
                  className="h-10 w-full rounded-md border border-border-default bg-background-surface px-3 text-sm outline-none focus:border-border-focus"
                  value={type}
                  onChange={(event) => setType(event.target.value)}
                >
                  <option value="">All types</option>
                  <option value="asset">Asset</option>
                  <option value="liability">Liability</option>
                  <option value="equity">Equity</option>
                  <option value="income">Income</option>
                  <option value="expense">Expense</option>
                </select>
              </label>
            </div>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={seedDefaults}
                disabled={saving}
                className="h-10 rounded-md border border-border-default bg-background-surface px-3 text-sm font-semibold text-text-secondary hover:bg-background-accent disabled:opacity-60"
              >
                Seed Defaults
              </button>
              <button
                type="button"
                onClick={() => setCreating((value) => !value)}
                className="h-10 rounded-md bg-accent-primary px-3 text-sm font-semibold text-accent-onPrimary"
              >
                {creating ? 'Close Form' : 'New Account'}
              </button>
            </div>
          </div>

          {message ? <div className="rounded-md border border-border-default bg-background-surface p-3 text-sm text-text-secondary">{message}</div> : null}

          {creating ? (
            <div className="rounded-md border border-border-default bg-background-surface p-4">
              <div className="grid gap-3 md:grid-cols-3">
                <label className="block space-y-1">
                  <span className="text-sm font-semibold text-text-secondary">GL Code</span>
                  <input className="h-10 w-full rounded-md border border-border-default px-3 text-sm" value={form.account_code} onChange={(event) => update('account_code', event.target.value)} />
                </label>
                <label className="block space-y-1 md:col-span-2">
                  <span className="text-sm font-semibold text-text-secondary">Account Name</span>
                  <input className="h-10 w-full rounded-md border border-border-default px-3 text-sm" value={form.account_name} onChange={(event) => update('account_name', event.target.value)} />
                </label>
                <label className="block space-y-1">
                  <span className="text-sm font-semibold text-text-secondary">Type</span>
                  <select className="h-10 w-full rounded-md border border-border-default px-3 text-sm" value={form.account_type} onChange={(event) => update('account_type', event.target.value)}>
                    <option value="asset">Asset</option>
                    <option value="liability">Liability</option>
                    <option value="equity">Equity</option>
                    <option value="income">Income</option>
                    <option value="expense">Expense</option>
                    <option value="memo">Memo</option>
                    <option value="control">Control</option>
                  </select>
                </label>
                <label className="block space-y-1">
                  <span className="text-sm font-semibold text-text-secondary">Category</span>
                  <input className="h-10 w-full rounded-md border border-border-default px-3 text-sm" value={form.category} onChange={(event) => update('category', event.target.value)} />
                </label>
                <label className="block space-y-1">
                  <span className="text-sm font-semibold text-text-secondary">Currency</span>
                  <input className="h-10 w-full rounded-md border border-border-default px-3 text-sm" value={form.currency} onChange={(event) => update('currency', event.target.value)} />
                </label>
                <label className="block space-y-1">
                  <span className="text-sm font-semibold text-text-secondary">Normal Balance</span>
                  <select className="h-10 w-full rounded-md border border-border-default px-3 text-sm" value={form.normal_balance} onChange={(event) => update('normal_balance', event.target.value)}>
                    <option value="debit">Debit</option>
                    <option value="credit">Credit</option>
                  </select>
                </label>
                <label className="block space-y-1">
                  <span className="text-sm font-semibold text-text-secondary">Posting</span>
                  <select className="h-10 w-full rounded-md border border-border-default px-3 text-sm" value={form.posting_allowed} onChange={(event) => update('posting_allowed', event.target.value)}>
                    <option value="true">Allowed</option>
                    <option value="false">Blocked</option>
                  </select>
                </label>
                <label className="block space-y-1">
                  <span className="text-sm font-semibold text-text-secondary">Status</span>
                  <select className="h-10 w-full rounded-md border border-border-default px-3 text-sm" value={form.status} onChange={(event) => update('status', event.target.value)}>
                    <option value="active">Active</option>
                    <option value="draft">Draft</option>
                    <option value="inactive">Inactive</option>
                  </select>
                </label>
              </div>
              <div className="mt-4 flex justify-end">
                <button
                  type="button"
                  onClick={submit}
                  disabled={saving || !form.account_code.trim() || !form.account_name.trim()}
                  className="h-10 rounded-md bg-accent-primary px-3 text-sm font-semibold text-accent-onPrimary disabled:opacity-60"
                >
                  {saving ? 'Saving...' : 'Create Account'}
                </button>
              </div>
            </div>
          ) : null}

          {loading ? (
            <LoadingBlock />
          ) : items.length === 0 ? (
            <EmptyState message="No accounts matched the current filters." />
          ) : (
            <CoaTable columns={['GL Code', 'Account Name', 'Type', 'Category', 'Posting', 'Currency', 'Balance', 'Status']}>
              {items.map((account) => (
                <tr key={account.id} className="border-t border-border-light hover:bg-gray-50">
                  <td className="p-3 font-semibold">
                    <Link href={`/accounting/chart-of-accounts/accounts/${account.id}`} className="text-accent-primary underline">
                      {account.gl_code}
                    </Link>
                  </td>
                  <td className="p-3">{account.name}</td>
                  <td className="p-3 text-text-secondary">{account.account_type}</td>
                  <td className="p-3 text-text-secondary">{account.category ?? '-'}</td>
                  <td className="p-3"><BooleanBadge value={account.posting_allowed} /></td>
                  <td className="p-3 text-text-secondary">{account.currency ?? '-'}</td>
                  <td className="p-3 text-text-secondary">{formatAmount(account.balance, account.currency ?? 'INR')}</td>
                  <td className="p-3"><StatusBadge value={account.status} /></td>
                </tr>
              ))}
            </CoaTable>
          )}
        </div>
      </CoaPageFrame>
    </AppShell>
  );
}
