"use client";

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { AppShell } from '../../../components/AppShell';

export default function NewLegalEntityPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [form, setForm] = useState<any>({ code: '', name: '', display_name: '', country: '', legal_type: '' });
  const [saving, setSaving] = useState(false);

  function update(field: string, value: any) {
    setForm((s: any) => ({ ...s, [field]: value }));
  }

  async function submit() {
    setSaving(true);
    try {
      const res = await fetch('/eom/legal-entities', { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-User-Roles': 'enterprise.admin' }, body: JSON.stringify(form) });
      if (res.ok) {
        const body = await res.json();
        router.push(`/eom/legal-entities/${body.id}`);
      } else {
        alert('Failed to create');
      }
    } finally {
      setSaving(false);
    }
  }

  return (
    <AppShell>
      <div className="space-y-4 max-w-2xl">
        <h2 className="text-xl font-semibold">New Legal Entity</h2>
        <div className="rounded-md border p-4">
          {step === 1 && (
            <div className="space-y-3">
              <label className="block">
                <div className="text-sm font-medium">Code</div>
                <input className="input" value={form.code} onChange={(e) => update('code', e.target.value)} />
              </label>
              <label className="block">
                <div className="text-sm font-medium">Legal Name</div>
                <input className="input" value={form.name} onChange={(e) => update('name', e.target.value)} />
              </label>
              <div className="flex gap-2">
                <button className="btn" onClick={() => setStep(2)}>Next</button>
              </div>
            </div>
          )}
          {step === 2 && (
            <div className="space-y-3">
              <label className="block">
                <div className="text-sm font-medium">Display Name</div>
                <input className="input" value={form.display_name} onChange={(e) => update('display_name', e.target.value)} />
              </label>
              <label className="block">
                <div className="text-sm font-medium">Country</div>
                <input className="input" value={form.country} onChange={(e) => update('country', e.target.value)} />
              </label>
              <label className="block">
                <div className="text-sm font-medium">Legal Type</div>
                <input className="input" value={form.legal_type} onChange={(e) => update('legal_type', e.target.value)} />
              </label>
              <div className="flex gap-2">
                <button className="btn" onClick={() => setStep(1)}>Back</button>
                <button className="btn btn-primary" onClick={submit} disabled={saving}>{saving ? 'Saving…' : 'Create'}</button>
              </div>
            </div>
          )}
        </div>
      </div>
    </AppShell>
  );
}
