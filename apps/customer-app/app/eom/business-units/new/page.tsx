"use client";

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { AppShell } from '../../../components/AppShell';
import { eomApiUrl } from '../../eomApi';

export default function NewBusinessUnitPage() {
  const router = useRouter();
  const [form, setForm] = useState<any>({
    legal_entity_id: '',
    business_unit_code: '',
    business_unit_name: '',
    head: '',
  });
  const [legalEntities, setLegalEntities] = useState<any[]>([]);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const res = await fetch(eomApiUrl('/eom/legal-entities'));
        if (!res.ok) return;
        const body = await res.json();
        const list = Array.isArray(body) ? body : (body.items || []);
        if (mounted) setLegalEntities(list);
      } catch (e) {
      }
    })();
    return () => { mounted = false; };
  }, []);

  function update(field: string, value: any) {
    setForm((s: any) => ({ ...s, [field]: value }));
  }

  async function submit() {
    setSaving(true);
    try {
      const res = await fetch(eomApiUrl('/eom/business-units'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-User-Roles': 'enterprise.admin' },
        body: JSON.stringify(form),
      });
      if (res.ok) {
        const body = await res.json();
        router.push(`/eom/business-units/${body.id}`);
      } else {
        const body = await res.json().catch(() => null);
        alert('Failed to create: ' + (body?.detail || JSON.stringify(body)));
      }
    } finally {
      setSaving(false);
    }
  }

  return (
    <AppShell>
      <div className="space-y-4 max-w-2xl">
        <h2 className="text-xl font-semibold">New Business Unit</h2>
        <div className="rounded-md border p-4 space-y-3">
          <label className="block">
            <div className="text-sm font-medium">Legal Entity</div>
            <select className="input w-full" value={form.legal_entity_id} onChange={(e) => update('legal_entity_id', e.target.value)}>
              <option value="">Select legal entity</option>
              {legalEntities.map((entity) => (
                <option key={entity.id} value={entity.id}>{entity.name} ({entity.code})</option>
              ))}
            </select>
          </label>
          <label className="block">
            <div className="text-sm font-medium">Business Unit Code</div>
            <input className="input w-full" value={form.business_unit_code} onChange={(e) => update('business_unit_code', e.target.value)} />
          </label>
          <label className="block">
            <div className="text-sm font-medium">Business Unit Name</div>
            <input className="input w-full" value={form.business_unit_name} onChange={(e) => update('business_unit_name', e.target.value)} />
          </label>
          <label className="block">
            <div className="text-sm font-medium">Head</div>
            <input className="input w-full" value={form.head} onChange={(e) => update('head', e.target.value)} />
          </label>
          <div className="flex gap-2">
            <button className="btn btn-primary" onClick={submit} disabled={saving}>{saving ? 'Creating…' : 'Create'}</button>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
