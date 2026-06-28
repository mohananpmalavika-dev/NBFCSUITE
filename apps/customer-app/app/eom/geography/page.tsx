"use client";

import React, { useEffect, useState } from 'react';
import { AppShell } from '../../components/AppShell';
import Link from 'next/link';
import { eomApiUrl } from '../eomApi';

export default function GeographyPage() {
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const res = await fetch(eomApiUrl('/eom/geography'));
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
            <h2 className="text-xl font-semibold">Geography</h2>
            <p className="text-sm text-text-secondary">Manage geographic nodes, hierarchy, and territory assignments.</p>
          </div>
          <Link href="/eom/geography/new" className="btn btn-primary">New Geography Node</Link>
        </div>
        {loading ? (
          <div>Loading…</div>
        ) : (
          <div className="space-y-2">
            {items.map((node) => (
              <Link key={node.id} href={`/eom/geography/${node.id}`} className="block rounded-md border p-3 hover:bg-gray-50">
                <div className="flex items-center justify-between gap-4">
                  <div>
                    <div className="font-semibold">{node.name}</div>
                    <div className="text-sm text-text-secondary">{node.code} · {node.node_type}</div>
                  </div>
                  <div className="text-sm text-text-secondary">{node.status}</div>
                </div>
              </Link>
            ))}
            {items.length === 0 && <div className="text-sm text-text-secondary">No geography nodes yet.</div>}
          </div>
        )}
      </div>
    </AppShell>
  );
}
