"use client";

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { AppShell } from '../../components/AppShell';
import { eomApiUrl } from '../eomApi';

type EnterpriseRow = {
  id: string;
  code: string;
  name: string;
  display_name?: string | null;
  short_name?: string | null;
  status: string;
  currency_code?: string | null;
  timezone?: string | null;
  language?: string | null;
};

export default function EnterprisesPage() {
  const [items, setItems] = useState<EnterpriseRow[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;

    async function loadEnterprises() {
      try {
        const res = await fetch(eomApiUrl('/eom/enterprises'));
        if (!res.ok) {
          return;
        }
        const body = await res.json();
        const nextItems = Array.isArray(body) ? body : body.items || [];
        if (mounted) {
          setItems(nextItems);
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    }

    loadEnterprises();
    return () => {
      mounted = false;
    };
  }, []);

  return (
    <AppShell>
      <div className="space-y-5">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-sm font-medium text-text-secondary">EOM-001</p>
            <h2 className="text-2xl font-semibold">Enterprise Master</h2>
            <p className="mt-1 max-w-3xl text-sm text-text-secondary">
              Root enterprise records with branding, legal, finance, compliance, workflow, documents, settings, and AI health controls.
            </p>
          </div>
          <Link href="/eom/enterprises/new/wizard" className="btn btn-primary">
            New Enterprise
          </Link>
        </div>

        {loading ? (
          <div className="rounded-md border border-border-default bg-background-surface p-4 text-sm text-text-secondary">
            Loading...
          </div>
        ) : (
          <div className="grid gap-3">
            {items.map((enterprise) => (
              <Link
                key={enterprise.id}
                href={`/eom/enterprises/${enterprise.id}`}
                className="rounded-md border border-border-default bg-background-surface p-4 transition hover:border-primary-300 hover:shadow-sm"
              >
                <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                  <div>
                    <div className="text-lg font-semibold">{enterprise.display_name || enterprise.name}</div>
                    <div className="text-sm text-text-secondary">
                      {enterprise.code} · {enterprise.short_name || enterprise.name}
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-sm md:grid-cols-4 md:text-right">
                    <div>
                      <div className="text-text-secondary">Status</div>
                      <div className="font-medium capitalize">{enterprise.status}</div>
                    </div>
                    <div>
                      <div className="text-text-secondary">Currency</div>
                      <div className="font-medium">{enterprise.currency_code || 'Not set'}</div>
                    </div>
                    <div>
                      <div className="text-text-secondary">Timezone</div>
                      <div className="font-medium">{enterprise.timezone || 'Not set'}</div>
                    </div>
                    <div>
                      <div className="text-text-secondary">Language</div>
                      <div className="font-medium">{enterprise.language || 'Not set'}</div>
                    </div>
                  </div>
                </div>
              </Link>
            ))}
            {items.length === 0 ? (
              <div className="rounded-md border border-dashed border-border-default bg-background-surface p-6 text-sm text-text-secondary">
                No enterprises yet. Create the first Enterprise Master to establish the organizational root.
              </div>
            ) : null}
          </div>
        )}
      </div>
    </AppShell>
  );
}
