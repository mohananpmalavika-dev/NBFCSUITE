"use client";

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useParams, usePathname } from 'next/navigation';
import { AppShell } from '../../../components/AppShell';
import { eomApiUrl } from '../../eomApi';

const TABS = [
  { label: 'Overview', href: '' },
  { label: 'Members', href: '/members' },
  { label: 'Skills', href: '/skills' },
  { label: 'Projects', href: '/projects' },
  { label: 'Workload', href: '/workload' },
  { label: 'Capacity', href: '/capacity' },
  { label: 'Performance', href: '/performance' },
  { label: 'Health', href: '/health' },
  { label: 'Assets', href: '/assets' },
  { label: 'Calendar', href: '/calendar' },
  { label: 'Documents', href: '/documents' },
  { label: 'KPIs', href: '/kpis' },
  { label: 'Timeline', href: '/timeline' },
  { label: 'Audit', href: '/audit' },
  { label: 'AI', href: '/ai' },
];

export default function TeamDetailPage() {
  const params = useParams<{ id: string }>();
  const pathname = usePathname();
  const [team, setTeam] = useState<any>(null);
  const [members, setMembers] = useState<any[]>([]);
  const [skills, setSkills] = useState<any[]>([]);
  const [capacity, setCapacity] = useState<any>(null);
  const [health, setHealth] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const isActive = (href: string) => {
    if (!href) return !pathname.includes('/members') && !pathname.includes('/skills') && !pathname.includes('/projects') && !pathname.includes('/workload') && !pathname.includes('/capacity') && !pathname.includes('/performance') && !pathname.includes('/health') && !pathname.includes('/assets') && !pathname.includes('/calendar') && !pathname.includes('/documents') && !pathname.includes('/kpis') && !pathname.includes('/timeline') && !pathname.includes('/audit') && !pathname.includes('/ai');
    return pathname.includes(href);
  };

  useEffect(() => {
    if (!params?.id) return;
    let mounted = true;
    (async () => {
      try {
        const [teamRes, membersRes, skillsRes, capRes, hlRes] = await Promise.all([
          fetch(eomApiUrl(`/eom/teams/${params.id}`)),
          fetch(eomApiUrl(`/eom/teams/${params.id}/members`)),
          fetch(eomApiUrl(`/eom/teams/${params.id}/skills`)),
          fetch(eomApiUrl(`/eom/teams/${params.id}/capacity`)),
          fetch(eomApiUrl(`/eom/teams/${params.id}/health`)),
        ]);
        if (teamRes.ok) { const body = await teamRes.json(); if (mounted) setTeam(body); }
        if (membersRes.ok) { const body = await membersRes.json(); if (mounted) setMembers(body.items || []); }
        if (skillsRes.ok) { const body = await skillsRes.json(); if (mounted) setSkills(body.items || []); }
        if (capRes.ok) { const body = await capRes.json(); if (mounted) setCapacity(body); }
        if (hlRes.ok) { const body = await hlRes.json(); if (mounted) setHealth(body); }
      } finally {
        if (mounted) setLoading(false);
      }
    })();
    return () => { mounted = false; };
  }, [params?.id]);

  if (loading) return <AppShell><div className="p-4 text-sm text-text-secondary">Loading…</div></AppShell>;
  if (!team) return <AppShell><div className="p-4 text-sm text-text-secondary">Team not found.</div></AppShell>;

  const healthScore = health?.score ?? 0;
  const scoreColor = healthScore >= 80 ? 'text-green-600' : healthScore >= 60 ? 'text-yellow-600' : 'text-red-600';

  return (
    <AppShell>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-primary-600">Team 360</p>
            <h2 className="text-xl font-semibold">{team.name}</h2>
            <p className="text-sm text-text-secondary">{team.code} · {team.team_type || 'Team'} · {team.status}</p>
          </div>
          <Link href="/eom/teams" className="btn">Back to teams</Link>
        </div>

        {/* Tabs */}
        <div className="overflow-x-auto">
          <div className="flex gap-1 border-b min-w-max">
            {TABS.map((tab) => {
              const active = isActive(tab.href);
              return (
                <Link
                  key={tab.label}
                  href={`/eom/teams/${params.id}${tab.href}`}
                  className={`px-3 py-2 text-sm font-medium whitespace-nowrap border-b-2 transition-colors ${
                    active
                      ? 'border-primary-600 text-primary-600'
                      : 'border-transparent text-text-secondary hover:text-text-primary hover:border-gray-300'
                  }`}
                >
                  {tab.label}
                </Link>
              );
            })}
          </div>
        </div>

        {/* Overview Content */}
        <div className="grid gap-4 lg:grid-cols-3">
          {/* Leadership */}
          <section className="rounded-md border p-4 space-y-3">
            <h3 className="font-semibold">Leadership</h3>
            <div className="grid gap-2 text-sm">
              <div><span className="font-medium">Team Lead:</span> {team.team_lead || '—'}</div>
              <div><span className="font-medium">Deputy Lead:</span> {team.deputy_lead || '—'}</div>
              <div><span className="font-medium">Reporting Manager:</span> {team.reporting_manager || '—'}</div>
            </div>
          </section>

          {/* Operations */}
          <section className="rounded-md border p-4 space-y-3">
            <h3 className="font-semibold">Operations</h3>
            <div className="grid gap-2 text-sm">
              <div><span className="font-medium">Shift:</span> {team.shift || '—'}</div>
              <div><span className="font-medium">Capacity:</span> {team.capacity || '—'}</div>
              <div><span className="font-medium">Working Days:</span> {team.working_days || '—'}</div>
              <div><span className="font-medium">Location:</span> {team.location || '—'}</div>
            </div>
          </section>

          {/* Health Score */}
          <section className="rounded-md border p-4 space-y-3 text-center">
            <h3 className="font-semibold">Health Score</h3>
            <div className={`text-4xl font-bold ${scoreColor}`}>{Math.round(healthScore)}%</div>
            <div className="flex justify-center gap-2 mt-2">
              <Link href={`/eom/teams/${team.id}/health`} className="btn text-xs">View Details</Link>
              <Link href={`/eom/teams/${team.id}/capacity`} className="btn text-xs">Capacity</Link>
              <Link href={`/eom/teams/${team.id}/workload`} className="btn text-xs">Workload</Link>
            </div>
          </section>
        </div>

        {/* Skills */}
        <section className="rounded-md border p-4 space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold">Skills</h3>
            <Link href={`/eom/teams/${team.id}/skills`} className="text-sm text-primary-600 hover:underline">View All</Link>
          </div>
          {team.primary_skills && (
            <div className="text-sm"><span className="font-medium">Primary:</span> {team.primary_skills}</div>
          )}
          {team.secondary_skills && (
            <div className="text-sm"><span className="font-medium">Secondary:</span> {team.secondary_skills}</div>
          )}
          {team.certifications && (
            <div className="text-sm"><span className="font-medium">Certifications:</span> {team.certifications}</div>
          )}
          {skills.length > 0 && (
            <div className="overflow-x-auto mt-2">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-gray-50 text-left">
                    <th className="p-2 font-medium">Employee</th>
                    <th className="p-2 font-medium">Skill</th>
                    <th className="p-2 font-medium">Level</th>
                    <th className="p-2 font-medium">Certification</th>
                  </tr>
                </thead>
                <tbody>
                  {skills.slice(0, 5).map((s: any) => (
                    <tr key={s.id} className="border-t">
                      <td className="p-2">{s.employee_id}</td>
                      <td className="p-2">{s.skill_name}</td>
                      <td className="p-2">{s.level || '—'}</td>
                      <td className="p-2">{s.certification || '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>

        {/* Members */}
        <section className="rounded-md border p-4 space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold">Members ({members.length})</h3>
            <Link href={`/eom/teams/${team.id}/members`} className="text-sm text-primary-600 hover:underline">View All</Link>
          </div>
          {members.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-gray-50 text-left">
                    <th className="p-2 font-medium">Employee</th>
                    <th className="p-2 font-medium">Name</th>
                    <th className="p-2 font-medium">Role</th>
                    <th className="p-2 font-medium">Joined</th>
                  </tr>
                </thead>
                <tbody>
                  {members.slice(0, 5).map((m: any) => (
                    <tr key={m.id} className="border-t">
                      <td className="p-2">{m.employee_id}</td>
                      <td className="p-2">{m.employee_name || '—'}</td>
                      <td className="p-2">{m.role || '—'}</td>
                      <td className="p-2">{m.join_date || '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-sm text-text-secondary">No members assigned yet.</p>
          )}
        </section>

        {/* Capacity Summary */}
        {capacity && (
          <section className="rounded-md border p-4 space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold">Capacity</h3>
              <Link href={`/eom/teams/${team.id}/capacity`} className="text-sm text-primary-600 hover:underline">View Details</Link>
            </div>
            <div className="grid gap-4 sm:grid-cols-3">
              <div className="text-center">
                <div className="text-2xl font-bold">{capacity.total_positions ?? 0}</div>
                <div className="text-xs text-text-secondary">Total Positions</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold">{capacity.filled ?? 0}</div>
                <div className="text-xs text-text-secondary">Filled</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold">{capacity.utilization_pct ?? 0}%</div>
                <div className="text-xs text-text-secondary">Utilization</div>
              </div>
            </div>
          </section>
        )}
      </div>
    </AppShell>
  );
}