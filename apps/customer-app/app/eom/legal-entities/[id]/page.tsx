"use client";

import React, { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { AppShell } from '../../../components/AppShell';

export default function LegalEntityDetailsPage() {
  const params: any = useParams();
  const id = params.id;
  const [item, setItem] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const res = await fetch(`/eom/legal-entities/${id}`);
        if (!res.ok) return;
        const body = await res.json();
        if (mounted) setItem(body);
      } catch (e) {
      } finally {
        if (mounted) setLoading(false);
      }
    })();
    return () => { mounted = false };
  }, [id]);

  return (
    <AppShell>
      <div className="space-y-4">
        {loading ? (
          <div>Loading…</div>
        ) : item ? (
          <div className="space-y-2">
            <h2 className="text-xl font-semibold">{item.name}</h2>
            <div className="text-sm text-text-secondary">{item.code} • {item.status}</div>
            <div className="rounded-md border p-3">
              <div><strong>Display Name:</strong> {item.display_name}</div>
              <div><strong>Legal Type:</strong> {item.legal_type}</div>
              <div><strong>Country:</strong> {item.country}</div>
              <div><strong>PAN:</strong> {item.pan}</div>
              <div><strong>GST:</strong> {item.gst}</div>
            </div>
          </div>
        ) : (
          <div>Not found.</div>
        )}
      </div>
    </AppShell>
  );
}
