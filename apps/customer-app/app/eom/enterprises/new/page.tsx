"use client";

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { AppShell } from '../../../components/AppShell';

export default function NewEnterprisePage() {
  const [code, setCode] = useState('');
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await fetch('/eom/enterprises', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code, name }),
      });
      if (res.ok) {
        router.push('/eom/enterprises');
      } else {
        const body = await res.json();
        alert('Failed: ' + (body.detail || JSON.stringify(body)));
      }
    } catch (err) {
      alert('Error: ' + String(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <AppShell>
      <div className="max-w-xl">
        <h2 className="text-xl font-semibold mb-4">New Enterprise</h2>
        <form onSubmit={submit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium">Code</label>
            <input value={code} onChange={(e) => setCode(e.target.value)} className="mt-1 input" />
          </div>
          <div>
            <label className="block text-sm font-medium">Name</label>
            <input value={name} onChange={(e) => setName(e.target.value)} className="mt-1 input" />
          </div>
          <div>
            <button className="btn btn-primary" type="submit" disabled={loading}>{loading ? 'Creating…' : 'Create'}</button>
        </div>
        </form>
      </div>
    </AppShell>
  );
}
