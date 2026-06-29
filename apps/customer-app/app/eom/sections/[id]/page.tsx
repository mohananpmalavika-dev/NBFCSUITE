"use client";

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { AppShell } from '../../../components/AppShell';
import { eomApiUrl } from '../../eomApi';

type Tab = 'overview' | 'organization' | 'operations' | 'services';

export default function SectionDetailPage() {
  const params = useParams<{ id: string }>();
  const [section, setSection] = useState<any>(null);
  const [dashboard, setDashboard] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<Tab>('overview');

  useEffect(() => {
    if (!params?.id) return;
    let mounted = true;
    (async () => {
      try {
        const [sectionRes, dashRes] = await Promise.all([
          fetch(eomApiUrl(`/eom/sections/${params.id}`)),
          fetch(eomApiUrl(`/eom/sections/${params.id}/dashboard`)),
        ]);
        if (sectionRes.ok) {
          const body = await sectionRes.json();
          if (mounted) setSection(body);
        }
        if (dashRes.ok) {
          const body = await dashRes.json();
          if (mounted) setDashboard(body);
        }
      } finally {
        if (mounted) setLoading(false);
      }
    })();
    return () => { mounted = false; };
  }, [params?.id]);

  const tabs: { key: Tab; label: string }[] = [
    { key: 'overview', label: 'Overview' },
    { key: 'organization', label: 'Organization' },
    { key: 'operations', label: 'Operations' },
    { key: 'services', label: 'Services' },
  ];

  if (loading) return <AppShell><div className="p-4 text-sm text-text-secondary">Loading…</div></AppShell>;
  if (!section) return <AppShell><div className="p-4 text-sm text-text-secondary">Section not found.</div></AppShell>;

  return (
    <AppShell>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-primary-600">Section 360</p>
            <h2 className="text-xl font-semibold">{section.name}</h2>
            <p className="text-sm text-text-secondary">{section.code} · {section.type || 'Section'} · {section.status}</p>
          </div>
          <Link href="/eom/sections" className="btn">Back to sections</Link>
        </div>

        {/* Health Score */}
        {(dashboard?.health_score != null || dashboard?.health) && (
          <div className="flex flex-wrap items-center gap-4 rounded-md border p-4">
            <div>
              <span className="text-sm font-medium">Health Score</span>
              <div className="text-2xl font-bold">
                {dashboard.health_score ?? dashboard.health ?? '—'}
              </div>
            </div>
            <Link href={`/eom/sections/${section.id}/dashboard`} className="btn">Dashboard</Link>
          </div>
        )}

        {/* Tabs */}
        <div className="flex border-b gap-1">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab.key
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-text-secondary hover:text-text'
              }`}
              onClick={() => setActiveTab(tab.key)}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div className="rounded-md border p-4">
          {activeTab === 'overview' && (
            <div className="space-y-4">
              <h3 className="font-semibold">Overview</h3>
              <div className="grid gap-3 sm:grid-cols-2 text-sm">
                <div><span className="font-medium">Name:</span> {section.name || '—'}</div>
                <div><span className="font-medium">Code:</span> {section.code || '—'}</div>
                <div><span className="font-medium">Type:</span> {section.type || '—'}</div>
                <div><span className="font-medium">Status:</span> {section.status || '—'}</div>
                <div><span className="font-medium">Section Head:</span> {section.section_head || '—'}</div>
                <div><span className="font-medium">Department:</span> {section.department || '—'}</div>
              </div>
            </div>
          )}

          {activeTab === 'organization' && (
            <div className="space-y-4">
              <h3 className="font-semibold">Organization</h3>
              <div className="grid gap-3 sm:grid-cols-2 text-sm">
                <div><span className="font-medium">Business Unit:</span> {section.business_unit || '—'}</div>
                <div><span className="font-medium">Branch:</span> {section.branch || '—'}</div>
                <div><span className="font-medium">Deputy Head:</span> {section.deputy_head || '—'}</div>
                <div><span className="font-medium">Reporting Department:</span> {section.reporting_department || '—'}</div>
                <div><span className="font-medium">Division:</span> {section.division || '—'}</div>
                <div><span className="font-medium">Cost Center:</span> {section.cost_center || '—'}</div>
              </div>
            </div>
          )}

          {activeTab === 'operations' && (
            <div className="space-y-4">
              <h3 className="font-semibold">Operations</h3>
              <div className="grid gap-3 sm:grid-cols-2 text-sm">
                <div><span className="font-medium">Working Calendar:</span> {section.working_calendar || '—'}</div>
                <div><span className="font-medium">Shift:</span> {section.shift || '—'}</div>
                <div><span className="font-medium">Capacity:</span> {section.capacity ?? '—'}</div>
                <div><span className="font-medium">Business Hours:</span> {section.business_hours || '—'}</div>
                <div><span className="font-medium">SLA Profile:</span> {section.sla_profile || '—'}</div>
                <div><span className="font-medium">Timezone:</span> {section.timezone || '—'}</div>
              </div>
            </div>
          )}

          {activeTab === 'services' && (
            <div className="space-y-4">
              <h3 className="font-semibold">Services</h3>
              <div className="grid gap-3 text-sm">
                <div>
                  <span className="font-medium">Service Catalog:</span>
                  <p className="mt-1 text-text-secondary whitespace-pre-wrap">{section.service_catalog || '—'}</p>
                </div>
                <div>
                  <span className="font-medium">Business Capabilities:</span>
                  <p className="mt-1 text-text-secondary whitespace-pre-wrap">{section.business_capabilities || '—'}</p>
                </div>
                <div>
                  <span className="font-medium">Workflows:</span>
                  <p className="mt-1 text-text-secondary whitespace-pre-wrap">{section.workflows || '—'}</p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Insights */}
        <section className="rounded-md border p-4 space-y-2">
          <h3 className="font-semibold">Section insights</h3>
          <p className="text-sm text-text-secondary">
            Dashboard, health, and analytics endpoints are available for extended monitoring and reporting.
          </p>
          <div className="flex flex-wrap gap-2">
            <Link href={`/eom/sections/${section.id}/dashboard`} className="btn">Dashboard</Link>
            <Link href={`/eom/sections/${section.id}/health`} className="btn">Health</Link>
            <Link href={`/eom/sections/${section.id}/analytics`} className="btn">Analytics</Link>
          </div>
        </section>
      </div>
    </AppShell>
  );
}