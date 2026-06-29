"use client";

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { AppShell } from '../../components/AppShell';
import { eomApiUrl } from '../eomApi';

export default function BranchesPage() {
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const res = await fetch(eomApiUrl('/eom/branches'));
        if (!res.ok) return;
        const body = await res.json();
        const list = Array.isArray(body) ? body : (body.items || []);
        if (mounted) setItems(list);
      } catch (e) {
      } finally {
        if (mounted) setLoading(false);
      }
    })();
    return () => { mounted = false; };
  }, []);

  return (
    <AppShell>
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold">Branches</h2>
            <p className="text-sm text-text-secondary">Operate branch profiles, health, and financial summaries from a single workspace.</p>
          </div>
          <Link href="/eom/branches/new" className="btn btn-primary">New Branch</Link>
        </div>
        {loading ? (
          <div>Loading…</div>
        ) : (
          <div className="space-y-2">
            {items.map((branch) => (
              <Link key={branch.id} href={`/eom/branches/${branch.id}`} className="block rounded-md border p-3 hover:bg-gray-50">
                <div className="flex items-center justify-between gap-4">
                  <div>
                    <div className="font-semibold">{branch.name}</div>
                    <div className="text-sm text-text-secondary">{branch.code} · {branch.branch_type || 'branch'}</div>
                  </div>
                  <div className="text-sm text-text-secondary">{branch.status}</div>
                </div>
              </Link>
            ))}
            {items.length === 0 && <div className="text-sm text-text-secondary">No branches yet.</div>}
          </div>
        )}
      </div>
    </AppShell>
  );
}
