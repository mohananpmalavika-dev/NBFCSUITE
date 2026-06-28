"use client";

import React, { useEffect, useState } from 'react';
import { AppShell } from '../../components/AppShell';
import Link from 'next/link';
import { eomApiUrl } from '../eomApi';

export default function EnterprisesPage() {
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const res = await fetch(eomApiUrl('/eom/enterprises'));
        if (!res.ok) return;
        const body = await res.json();
        const items = Array.isArray(body) ? body : (body.items || []);
        if (mounted) setItems(items);
      } catch (e) {
        // ignore
      } finally {
        if (mounted) setLoading(false);
      }
    })();
    return () => { mounted = false };
  }, []);

  return (
    <AppShell>
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold">Enterprises</h2>
          <Link href="/eom/enterprises/new" className="btn btn-primary">New Enterprise</Link>
        </div>
        {loading ? (
          <div>Loading…</div>
        ) : (
          <div className="space-y-2">
            {items.map((e) => (
              <div key={e.id} className="rounded-md border p-3">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-semibold">{e.name}</div>
                    <div className="text-sm text-text-secondary">{e.code}</div>
                  </div>
                  <div className="text-sm text-text-secondary">{e.status}</div>
                </div>
              </div>
            ))}
            {items.length === 0 && <div className="text-sm text-text-secondary">No enterprises yet.</div>}
          </div>
        )}
      </div>
    </AppShell>
  );
}
