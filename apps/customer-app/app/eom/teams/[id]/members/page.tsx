"use client";

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { AppShell } from '../../../../components/AppShell';
import { eomApiUrl } from '../../../eomApi';

export default function TeamMembersPage() {
  const params = useParams<{ id: string }>();
  const [members, setMembers] = useState<any[]>([]);
  const [team, setTeam] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!params?.id) return;
    let mounted = true;
    (async () => {
      try {
        const [memRes, teamRes] = await Promise.all([
          fetch(eomApiUrl(`/eom/teams/${params.id}/members`)),
          fetch(eomApiUrl(`/eom/teams/${params.id}`)),
        ]);
        if (memRes.ok) { const body = await memRes.json(); if (mounted) setMembers(body.items || []); }
        if (teamRes.ok) { const body = await teamRes.json(); if (mounted) setTeam(body); }
      } finally { if (mounted) setLoading(false); }
    })();
    return () => { mounted = false; };
  }, [params?.id]);

  if (loading) return <AppShell><div className="p-4 text-sm text-text-secondary">Loading…</div></AppShell>;
  if (!team) return <AppShell><div className="p-4 text-sm text-text-secondary">Team not found.</div></AppShell>;

  return (
    <AppShell>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-primary-600">Team Members</p>
            <h2 className="text-xl font-semibold">{team.name}</h2>
            <p className="text-sm text-text-secondary">{team.code} · {members.length} members</p>
          </div>
          <Link href={`/eom/teams/${params.id}`} className="btn">Back to Team</Link>
        </div>

        <div className="overflow-x-auto rounded-md border">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 text-left">
                <th className="p-3 font-medium">Employee ID</th>
                <th className="p-3 font-medium">Employee Name</th>
                <th className="p-3 font-medium">Role</th>
                <th className="p-3 font-medium">Join Date</th>
              </tr>
            </thead>
            <tbody>
              {members.length === 0 && (
                <tr><td colSpan={4} className="p-3 text-center text-text-secondary">No members found.</td></tr>
              )}
              {members.map((m: any) => (
                <tr key={m.id || m.employee_id} className="border-t hover:bg-gray-50">
                  <td className="p-3">{m.employee_id}</td>
                  <td className="p-3">{m.employee_name || '—'}</td>
                  <td className="p-3">{m.role || '—'}</td>
                  <td className="p-3">{m.join_date || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </AppShell>
  );
}