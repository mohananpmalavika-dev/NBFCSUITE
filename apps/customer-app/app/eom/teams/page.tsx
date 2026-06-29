"use client";

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { AppShell } from '../../components/AppShell';
import { eomApiUrl } from '../eomApi';

export default function TeamsPage() {
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('');

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const res = await fetch(eomApiUrl('/eom/teams'));
        if (!res.ok) return;
        const body = await res.json();
        const list = Array.isArray(body) ? body : (body.items || []);
        if (mounted) setItems(list);
      } catch {
      } finally {
        if (mounted) setLoading(false);
      }
    })();
    return () => { mounted = false; };
  }, []);

  const filtered = items.filter((t) => {
    const q = search.toLowerCase();
    if (q && !t.name?.toLowerCase().includes(q) && !t.code?.toLowerCase().includes(q)) return false;
    if (statusFilter && t.status !== statusFilter) return false;
    if (typeFilter && t.team_type !== typeFilter) return false;
    return true;
  });

  const statuses = [...new Set(items.map((t) => t.status).filter(Boolean))];
  const types = [...new Set(items.map((t) => t.team_type).filter(Boolean))];

  return (
    <AppShell>
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold">Teams</h2>
            <p className="text-sm text-text-secondary">Manage operational teams, capacity, skills, and performance.</p>
          </div>
          <Link href="/eom/teams/new" className="btn btn-primary">New Team</Link>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <input className="input max-w-xs" placeholder="Search by name or code…" value={search} onChange={(e) => setSearch(e.target.value)} />
          <select className="input max-w-[160px]" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            <option value="">All Status</option>
            {statuses.map((s) => (<option key={s} value={s}>{s}</option>))}
          </select>
          <select className="input max-w-[200px]" value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)}>
            <option value="">All Types</option>
            {types.map((t) => (<option key={t} value={t}>{t}</option>))}
          </select>
        </div>

        {loading ? (
          <div className="py-8 text-center text-sm text-text-secondary">Loading…</div>
        ) : (
          <div className="overflow-x-auto rounded-md border">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-50 text-left">
                  <th className="p-3 font-semibold">Team Code</th>
                  <th className="p-3 font-semibold">Team Name</th>
                  <th className="p-3 font-semibold">Section</th>
                  <th className="p-3 font-semibold">Team Lead</th>
                  <th className="p-3 font-semibold">Type</th>
                  <th className="p-3 font-semibold">Capacity</th>
                  <th className="p-3 font-semibold">Status</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((team) => (
                  <tr key={team.id} className="border-t hover:bg-gray-50">
                    <td className="p-3">
                      <Link href={`/eom/teams/${team.id}`} className="font-medium text-primary-600 underline">{team.code}</Link>
                    </td>
                    <td className="p-3">
                      <Link href={`/eom/teams/${team.id}`} className="font-medium">{team.name}</Link>
                    </td>
                    <td className="p-3 text-text-secondary">{team.section_id || '—'}</td>
                    <td className="p-3 text-text-secondary">{team.team_lead || '—'}</td>
                    <td className="p-3 text-text-secondary">{team.team_type || '—'}</td>
                    <td className="p-3 text-center">{team.capacity || '—'}</td>
                    <td className="p-3">
                      <span className={`inline-block rounded px-2 py-0.5 text-xs font-medium ${
                        team.status === 'active' ? 'bg-green-100 text-green-800' :
                        team.status === 'inactive' ? 'bg-gray-100 text-gray-600' :
                        'bg-yellow-100 text-yellow-800'
                      }`}>{team.status}</span>
                    </td>
                  </tr>
                ))}
                {filtered.length === 0 && (
                  <tr><td colSpan={7} className="p-6 text-center text-sm text-text-secondary">No teams found.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </AppShell>
  );
}
