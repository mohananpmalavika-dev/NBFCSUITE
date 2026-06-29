"use client";

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { AppShell } from '../../../../components/AppShell';
import { eomApiUrl } from '../../../eomApi';

export default function NewDepartmentPage() {
  const router = useRouter();
  const [form, setForm] = useState<any>({
    code: '',
    name: '',
    department_head: '',
    branch_id: '',
    business_unit_id: '',
    legal_entity_id: '',
    city: '',
    region: '',
    address: '',
    phone: '',
    email: '',
    description: '',
    status: 'active',
  });
  const [businessUnits, setBusinessUnits] = useState<any[]>([]);
  const [legalEntities, setLegalEntities] = useState<any[]>([]);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const [unitsRes, legalRes] = await Promise.all([
          fetch(eomApiUrl('/eom/business-units')),
          fetch(eomApiUrl('/eom/legal-entities')),
        ]);
        const unitsBody = unitsRes.ok ? await unitsRes.json() : { items: [] };
        const legalBody = legalRes.ok ? await legalRes.json() : { items: [] };
        if (mounted) {
          setBusinessUnits(Array.isArray(unitsBody) ? unitsBody : (unitsBody.items || []));
          setLegalEntities(Array.isArray(legalBody) ? legalBody : (legalBody.items || []));
        }
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
      const payload = {
        ...form,
        branch_id: form.branch_id || undefined,
        business_unit_id: form.business_unit_id || undefined,
        legal_entity_id: form.legal_entity_id || undefined,
      };
      const res = await fetch(eomApiUrl('/eom/departments'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-User-Roles': 'enterprise.admin' },
        body: JSON.stringify(payload),
      });
      if (res.ok) {
        const body = await res.json();
        router.push(`/eom/departments/${body.id}`);
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
      <div className="space-y-4 max-w-3xl">
        <h2 className="text-xl font-semibold">New Department</h2>
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
              <span className="text-sm font-medium">Department Head</span>
              <input className="input" value={form.department_head} onChange={(e) => update('department_head', e.target.value)} />
            </label>
            <label className="block space-y-2">
              <span className="text-sm font-medium">Branch</span>
              <input className="input" value={form.branch_id} onChange={(e) => update('branch_id', e.target.value)} placeholder="Branch id" />
            </label>
            <label className="block space-y-2">
              <span className="text-sm font-medium">Business Unit</span>
              <select className="input" value={form.business_unit_id} onChange={(e) => update('business_unit_id', e.target.value)}>
                <option value="">Select business unit</option>
                {businessUnits.map((bu) => (
                  <option key={bu.id} value={bu.id}>{bu.business_unit_name} ({bu.business_unit_code})</option>
                ))}
              </select>
            </label>
            <label className="block space-y-2">
              <span className="text-sm font-medium">Legal Entity</span>
              <select className="input" value={form.legal_entity_id} onChange={(e) => update('legal_entity_id', e.target.value)}>
                <option value="">Select legal entity</option>
                {legalEntities.map((entity) => (
                  <option key={entity.id} value={entity.id}>{entity.name} ({entity.code})</option>
                ))}
              </select>
            </label>
            <label className="block space-y-2">
              <span className="text-sm font-medium">City</span>
              <input className="input" value={form.city} onChange={(e) => update('city', e.target.value)} />
            </label>
            <label className="block space-y-2">
              <span className="text-sm font-medium">Region</span>
              <input className="input" value={form.region} onChange={(e) => update('region', e.target.value)} />
            </label>
            <label className="block space-y-2 md:col-span-2">
              <span className="text-sm font-medium">Address</span>
              <input className="input" value={form.address} onChange={(e) => update('address', e.target.value)} />
            </label>
            <label className="block space-y-2">
              <span className="text-sm font-medium">Phone</span>
              <input className="input" value={form.phone} onChange={(e) => update('phone', e.target.value)} />
            </label>
            <label className="block space-y-2">
              <span className="text-sm font-medium">Email</span>
              <input className="input" value={form.email} onChange={(e) => update('email', e.target.value)} />
            </label>
          </div>
          <label className="block space-y-2">
            <span className="text-sm font-medium">Description</span>
            <textarea className="input min-h-[120px]" value={form.description} onChange={(e) => update('description', e.target.value)} />
          </label>
          <div className="flex gap-2">
            <button className="btn" type="button" onClick={() => router.back()}>Cancel</button>
            <button className="btn btn-primary" onClick={submit} disabled={saving}>{saving ? 'Saving…' : 'Create'}</button>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
