"use client";

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { AppShell } from '../../../components/AppShell';
import { eomApiUrl } from '../../eomApi';

export default function DepartmentDetailPage() {
  const params = useParams<{ id: string }>();
  const [department, setDepartment] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!params?.id) return;
    let mounted = true;
    (async () => {
      try {
        const res = await fetch(eomApiUrl(`/eom/departments/${params.id}`));
        if (!res.ok) return;
        const body = await res.json();
        if (mounted) setDepartment(body);
      } finally {
        if (mounted) setLoading(false);
      }
    })();
    return () => { mounted = false; };
  }, [params?.id]);

  if (loading) return <AppShell><div>Loading…</div></AppShell>;
  if (!department) return <AppShell><div>Department not found.</div></AppShell>;

  return (
    <AppShell>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-primary-600">Department 360</p>
            <h2 className="text-xl font-semibold">{department.name}</h2>
            <p className="text-sm text-text-secondary">{department.code} · {department.department_head || 'Department'}</p>
          </div>
          <Link href="/eom/departments" className="btn">Back to departments</Link>
        </div>

        <div className="grid gap-4 lg:grid-cols-2">
          <section className="rounded-md border p-4 space-y-3">
            <h3 className="font-semibold">Operational profile</h3>
            <div className="grid gap-2 text-sm">
              <div><span className="font-medium">Status:</span> {department.status}</div>
              <div><span className="font-medium">Head:</span> {department.department_head || '—'}</div>
              <div><span className="font-medium">Branch:</span> {department.branch_id || '—'}</div>
              <div><span className="font-medium">Business unit:</span> {department.business_unit_id || '—'}</div>
              <div><span className="font-medium">Legal entity:</span> {department.legal_entity_id || '—'}</div>
            </div>
          </section>
          <section className="rounded-md border p-4 space-y-3">
            <h3 className="font-semibold">Contact & location</h3>
            <div className="grid gap-2 text-sm">
              <div><span className="font-medium">City:</span> {department.city || '—'}</div>
              <div><span className="font-medium">Region:</span> {department.region || '—'}</div>
              <div><span className="font-medium">Phone:</span> {department.phone || '—'}</div>
              <div><span className="font-medium">Email:</span> {department.email || '—'}</div>
              <div><span className="font-medium">Address:</span> {department.address || '—'}</div>
            </div>
          </section>
        </div>

        <section className="rounded-md border p-4 space-y-2">
          <h3 className="font-semibold">Department insights</h3>
          <p className="text-sm text-text-secondary">Use department dashboard, health, and analytics for operational review.</p>
          <div className="flex flex-wrap gap-2">
            <Link href={`/eom/departments/${department.id}/dashboard`} className="btn">Dashboard</Link>
            <Link href={`/eom/departments/${department.id}/health`} className="btn">Health</Link>
            <Link href={`/eom/departments/${department.id}/analytics`} className="btn">Analytics</Link>
          </div>
        </section>
      </div>
    </AppShell>
  );
}
