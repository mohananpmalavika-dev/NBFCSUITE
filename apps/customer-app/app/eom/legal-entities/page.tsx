"use client";

import React, { useEffect, useState } from 'react';
import { AppShell } from '../../components/AppShell';
import Link from 'next/link';

export default function LegalEntitiesPage() {
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const res = await fetch('/eom/legal-entities');
        if (!res.ok) return;
        const body = await res.json();
        const list = Array.isArray(body) ? body : (body.items || []);
        if (mounted) setItems(list);
      } catch (e) {
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
          <h2 className="text-xl font-semibold">Legal Entities</h2>
          <Link href="/eom/legal-entities/new" className="btn btn-primary">New Legal Entity</Link>
        </div>
        {loading ? (
          <div>Loading…</div>
        ) : (
          <div className="space-y-2">
            {items.map((e) => (
              <Link key={e.id} href={`/eom/legal-entities/${e.id}`} className="block rounded-md border p-3 hover:bg-gray-50">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-semibold">{e.name}</div>
                    <div className="text-sm text-text-secondary">{e.code}</div>
                  </div>
                  <div className="text-sm text-text-secondary">{e.status}</div>
                </div>
              </Link>
            ))}
            {items.length === 0 && <div className="text-sm text-text-secondary">No legal entities yet.</div>}
          </div>
        )}
      </div>
    </AppShell>
  );
}
