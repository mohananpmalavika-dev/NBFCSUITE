"use client";

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { AppShell } from '../../../components/AppShell';
import { eomApiUrl } from '../../eomApi';

export default function BranchDetailPage() {
  const params = useParams<{ id: string }>();
  const [branch, setBranch] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!params?.id) return;
    let mounted = true;
    (async () => {
      try {
        const res = await fetch(eomApiUrl(`/eom/branches/${params.id}`));
        if (!res.ok) return;
        const body = await res.json();
        if (mounted) setBranch(body);
      } finally {
        if (mounted) setLoading(false);
      }
    })();
    return () => { mounted = false; };
  }, [params?.id]);

  if (loading) return <AppShell><div>Loading…</div></AppShell>;
  if (!branch) return <AppShell><div>Branch not found.</div></AppShell>;

  return (
    <AppShell>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-primary-600">Branch 360</p>
            <h2 className="text-xl font-semibold">{branch.name}</h2>
            <p className="text-sm text-text-secondary">{branch.code} · {branch.branch_type || 'Branch'}</p>
          </div>
          <Link href="/eom/branches" className="btn">Back to branches</Link>
        </div>
        <div className="grid gap-4 lg:grid-cols-2">
          <section className="rounded-md border p-4 space-y-3">
            <h3 className="font-semibold">Operational profile</h3>
            <div className="grid gap-2 text-sm">
              <div><span className="font-medium">Status:</span> {branch.status}</div>
              <div><span className="font-medium">Manager:</span> {branch.manager || '—'}</div>
              <div><span className="font-medium">City:</span> {branch.city || '—'}</div>
              <div><span className="font-medium">Region:</span> {branch.region || '—'}</div>
              <div><span className="font-medium">Address:</span> {branch.address || '—'}</div>
            </div>
          </section>
          <section className="rounded-md border p-4 space-y-3">
            <h3 className="font-semibold">Financial controls</h3>
            <div className="grid gap-2 text-sm">
              <div><span className="font-medium">Cash limit:</span> {branch.cash_limit ?? '—'}</div>
              <div><span className="font-medium">Vault limit:</span> {branch.vault_limit ?? '—'}</div>
              <div><span className="font-medium">Gold loan enabled:</span> {branch.gold_loan_enabled ? 'Yes' : 'No'}</div>
              <div><span className="font-medium">Deposit enabled:</span> {branch.deposit_enabled ? 'Yes' : 'No'}</div>
              <div><span className="font-medium">Forex enabled:</span> {branch.forex_enabled ? 'Yes' : 'No'}</div>
            </div>
          </section>
        </div>
        <section className="rounded-md border p-4 space-y-2">
          <h3 className="font-semibold">Branch insights</h3>
          <p className="text-sm text-text-secondary">Dashboard, health, and analytics endpoints are available for the branch twin and can be extended with real transaction data.</p>
          <div className="flex flex-wrap gap-2">
            <Link href={`/eom/branches/${branch.id}/dashboard`} className="btn">Dashboard</Link>
            <Link href={`/eom/branches/${branch.id}/health`} className="btn">Health</Link>
            <Link href={`/eom/branches/${branch.id}/analytics`} className="btn">Analytics</Link>
          </div>
        </section>
      </div>
    </AppShell>
  );
}
