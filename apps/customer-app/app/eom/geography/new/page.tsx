"use client";

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { AppShell } from '../../../components/AppShell';
import { eomApiUrl } from '../../eomApi';

export default function NewGeographyNodePage() {
  const router = useRouter();
  const [form, setForm] = useState<any>({ code: '', name: '', node_type: '', parent_id: '', manager: '', latitude: '', longitude: '', status: 'active', description: '' });
  const [saving, setSaving] = useState(false);

  function update(field: string, value: any) {
    setForm((s: any) => ({ ...s, [field]: value }));
  }

  async function submit() {
    setSaving(true);
    try {
      const payload = {
        ...form,
        parent_id: form.parent_id || undefined,
      };
      const res = await fetch(eomApiUrl('/eom/geography'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-User-Roles': 'enterprise.admin' },
        body: JSON.stringify(payload),
      });
      if (res.ok) {
        const body = await res.json();
        router.push(`/eom/geography/${body.id}`);
      } else {
        alert('Failed to create geography node');
      }
    } finally {
      setSaving(false);
    }
  }

  return (
    <AppShell>
      <div className="space-y-4 max-w-2xl">
        <h2 className="text-xl font-semibold">New Geography Node</h2>
        <div className="rounded-md border p-4 space-y-4">
          <label className="block space-y-2">
            <span className="text-sm font-medium">Code</span>
            <input className="input" value={form.code} onChange={(e) => update('code', e.target.value)} />
          </label>
          <label className="block space-y-2">
            <span className="text-sm font-medium">Name</span>
            <input className="input" value={form.name} onChange={(e) => update('name', e.target.value)} />
          </label>
          <label className="block space-y-2">
            <span className="text-sm font-medium">Type</span>
            <input className="input" value={form.node_type} onChange={(e) => update('node_type', e.target.value)} />
          </label>
          <label className="block space-y-2">
            <span className="text-sm font-medium">Parent Node ID</span>
            <input className="input" value={form.parent_id} onChange={(e) => update('parent_id', e.target.value)} />
          </label>
          <label className="block space-y-2">
            <span className="text-sm font-medium">Manager</span>
            <input className="input" value={form.manager} onChange={(e) => update('manager', e.target.value)} />
          </label>
          <label className="block space-y-2">
            <span className="text-sm font-medium">Latitude</span>
            <input className="input" value={form.latitude} onChange={(e) => update('latitude', e.target.value)} />
          </label>
          <label className="block space-y-2">
            <span className="text-sm font-medium">Longitude</span>
            <input className="input" value={form.longitude} onChange={(e) => update('longitude', e.target.value)} />
          </label>
          <label className="block space-y-2">
            <span className="text-sm font-medium">Description</span>
            <textarea className="input min-h-[120px]" value={form.description} onChange={(e) => update('description', e.target.value)} />
          </label>
          <div className="flex gap-2">
            <button className="btn" onClick={() => router.back()} type="button">Cancel</button>
            <button className="btn btn-primary" onClick={submit} disabled={saving}>{saving ? 'Saving…' : 'Create'}</button>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
