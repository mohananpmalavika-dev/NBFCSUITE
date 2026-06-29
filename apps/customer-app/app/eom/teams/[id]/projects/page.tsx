"use client";

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { AppShell } from '../../../../components/AppShell';
import { eomApiUrl } from '../../../eomApi';

export default function TeamProjectsPage() {
  const params = useParams<{ id: string }>();
  const [projects, setProjects] = useState<any[]>([]);
  const [team, setTeam] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!params?.id) return;
    let mounted = true;
    (async () => {
      try {
        const [projRes, teamRes] = await Promise.all([
          fetch(eomApiUrl(`/eom/teams/${params.id}/projects`)),
          fetch(eomApiUrl(`/eom/teams/${params.id}`)),
        ]);
        if (projRes.ok) { const body = await projRes.json(); if (mounted) setProjects(body.items || []); }
        if (teamRes.ok) { const body = await teamRes.json(); if (mounted) setTeam(body); }
      } finally { if (mounted) setLoading(false); }
    })();
    return () => { mounted = false; };
  }, [params?.id]);

  const statusColor = (status: string) => {
    const s = (status || '').toLowerCase();
    if (s === 'active' || s === 'in_progress') return 'bg-green-100 text-green-800';
    if (s === 'completed' || s === 'done') return 'bg-blue-100 text-blue-800';
    if (s === 'on_hold' || s === 'paused') return 'bg-yellow-100 text-yellow-800';
    if (s === 'cancelled') return 'bg-red-100 text-red-800';
    return 'bg-gray-100 text-gray-800';
  };

  if (loading) return <AppShell><div className="p-4 text-sm text-text-secondary">Loading…</div></AppShell>;
  if (!team) return <AppShell><div className="p-4 text-sm text-text-secondary">Team not found.</div></AppShell>;

  return (
    <AppShell>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-primary-600">Team Projects</p>
            <h2 className="text-xl font-semibold">{team.name}</h2>
            <p className="text-sm text-text-secondary">{team.code} · {projects.length} projects</p>
          </div>
          <Link href={`/eom/teams/${params.id}`} className="btn">Back to Team</Link>
        </div>

        <div className="overflow-x-auto rounded-md border">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 text-left">
                <th className="p-3 font-medium">Project ID</th>
                <th className="p-3 font-medium">Project Name</th>
                <th className="p-3 font-medium">Product</th>
                <th className="p-3 font-medium">Process</th>
                <th className="p-3 font-medium">Customer</th>
                <th className="p-3 font-medium">Role</th>
                <th className="p-3 font-medium">Start Date</th>
                <th className="p-3 font-medium">End Date</th>
                <th className="p-3 font-medium">Status</th>
              </tr>
            </thead>
            <tbody>
              {projects.length === 0 && (
                <tr><td colSpan={9} className="p-3 text-center text-text-secondary">No projects found.</td></tr>
              )}
              {projects.map((p: any) => (
                <tr key={p.id || p.project_id} className="border-t hover:bg-gray-50">
                  <td className="p-3">{p.project_id}</td>
                  <td className="p-3 font-medium">{p.project_name}</td>
                  <td className="p-3">{p.product || '—'}</td>
                  <td className="p-3">{p.process || '—'}</td>
                  <td className="p-3">{p.customer || '—'}</td>
                  <td className="p-3">{p.role || '—'}</td>
                  <td className="p-3">{p.start_date || '—'}</td>
                  <td className="p-3">{p.end_date || '—'}</td>
                  <td className="p-3">
                    <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${statusColor(p.status)}`}>
                      {p.status || '—'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </AppShell>
  );
}