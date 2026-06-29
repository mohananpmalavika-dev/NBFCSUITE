"use client";

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { AppShell } from '../../../components/AppShell';
import { eomApiUrl } from '../../eomApi';

export default function NewBranchPage() {
  const router = useRouter();
  const [form, setForm] = useState<any>({
    code: '',
    name: '',
    branch_type: 'retail',
    manager: '',
    city: '',
    region: '',
    address: '',
    phone: '',
    email: '',
    website: '',
    description: '',
    cash_limit: '',
    vault_limit: '',
    gold_loan_enabled: false,
    deposit_enabled: true,
    forex_enabled: false,
    atm: false,
    locker: false,
    kiosk: false,
    status: 'active',
  });
  const [saving, setSaving] = useState(false);

  function update(field: string, value: any) {
    setForm((s: any) => ({ ...s, [field]: value }));
  }

  async function submit() {
    setSaving(true);
    try {
      const payload = {
        ...form,
        cash_limit: form.cash_limit ? Number(form.cash_limit) : undefined,
        vault_limit: form.vault_limit ? Number(form.vault_limit) : undefined,
      };
      const res = await fetch(eomApiUrl('/eom/branches'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-User-Roles': 'enterprise.admin' },
        body: JSON.stringify(payload),
      });
      if (res.ok) {
        const body = await res.json();
        router.push(`/eom/branches/${body.id}`);
      } else {
        alert('Failed to create branch');
      }
    } finally {
      setSaving(false);
    }
  }

  return (
    <AppShell>
      <div className="space-y-4 max-w-3xl">
        <h2 className="text-xl font-semibold">New Branch</h2>
        <div className="rounded-md border p-4 space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <label className="block space-y-2">
              <span className="text-sm font-medium">Code</span>
              <input className="input" value={form.code} onChange={(e) => update('code', e.target.value)} />
            </label>
            <label className="block space-y-2">
              <span className="text-sm font-medium">Name</span>
              <input className="input" value={form.name} onChange={(e) => update('name', e.target.value)} />
            </label>
            <label className="block space-y-2">
              <span className="text-sm font-medium">Branch Type</span>
              <input className="input" value={form.branch_type} onChange={(e) => update('branch_type', e.target.value)} />
            </label>
            <label className="block space-y-2">
              <span className="text-sm font-medium">Manager</span>
              <input className="input" value={form.manager} onChange={(e) => update('manager', e.target.value)} />
            </label>
            <label className="block space-y-2">
              <span className="text-sm font-medium">City</span>
              <input className="input" value={form.city} onChange={(e) => update('city', e.target.value)} />
            </label>
            <label className="block space-y-2">
              <span className="text-sm font-medium">Region</span>
              <input className="input" value={form.region} onChange={(e) => update('region', e.target.value)} />
            </label>
            <label className="block space-y-2">
              <span className="text-sm font-medium">Phone</span>
              <input className="input" value={form.phone} onChange={(e) => update('phone', e.target.value)} />
            </label>
            <label className="block space-y-2">
              <span className="text-sm font-medium">Email</span>
              <input className="input" value={form.email} onChange={(e) => update('email', e.target.value)} />
            </label>
            <label className="block space-y-2 md:col-span-2">
              <span className="text-sm font-medium">Address</span>
              <input className="input" value={form.address} onChange={(e) => update('address', e.target.value)} />
            </label>
            <label className="block space-y-2">
              <span className="text-sm font-medium">Cash Limit</span>
              <input className="input" type="number" value={form.cash_limit} onChange={(e) => update('cash_limit', e.target.value)} />
            </label>
            <label className="block space-y-2">
              <span className="text-sm font-medium">Vault Limit</span>
              <input className="input" type="number" value={form.vault_limit} onChange={(e) => update('vault_limit', e.target.value)} />
            </label>
          </div>
          <label className="block space-y-2">
            <span className="text-sm font-medium">Description</span>
            <textarea className="input min-h-[120px]" value={form.description} onChange={(e) => update('description', e.target.value)} />
          </label>
          <div className="grid gap-3 md:grid-cols-3">
            {['gold_loan_enabled', 'deposit_enabled', 'forex_enabled', 'atm', 'locker', 'kiosk'].map((field) => (
              <label key={field} className="flex items-center gap-2 rounded-md border p-2 text-sm">
                <input type="checkbox" checked={Boolean(form[field])} onChange={(e) => update(field, e.target.checked)} />
                <span>{field.replace(/_/g, ' ')}</span>
              </label>
            ))}
          </div>
          <div className="flex gap-2">
            <button className="btn" onClick={() => router.back()} type="button">Cancel</button>
            <button className="btn btn-primary" onClick={submit} disabled={saving}>{saving ? 'Saving…' : 'Create'}</button>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
