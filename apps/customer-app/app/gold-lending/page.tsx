"use client";

import { useEffect, useState } from 'react';
import { AppShell } from '../components/AppShell';
import { goldApi } from './goldApi';

export default function GoldLanding() {
  const [products, setProducts] = useState<any[]>([]);

  useEffect(() => {
    goldApi.products().then((res) => setProducts(res as any[])).catch(() => setProducts([]));
  }, []);

  return (
    <AppShell>
      <div className="space-y-6 p-6">
        <div className="rounded-md border border-border-default bg-background-surface p-6">
          <div className="text-sm font-semibold uppercase tracking-wide text-accent-primary">Gold Lending</div>
          <h1 className="mt-2 text-2xl font-semibold text-text-primary">Gold Lending Platform</h1>
        </div>
        <div className="rounded-md border border-border-default bg-background-default p-6">
          <h2 className="text-lg font-semibold">Products</h2>
          <ul className="mt-2 space-y-2">
            {products.map((p) => (
              <li key={p.id} className="rounded-md border bg-background-surface p-3">{p.name} — LTV {p.max_ltv ?? 'n/a'}</li>
            ))}
          </ul>
        </div>
      </div>
    </AppShell>
  );
}
