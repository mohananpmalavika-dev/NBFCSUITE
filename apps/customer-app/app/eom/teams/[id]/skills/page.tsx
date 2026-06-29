"use client";

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { AppShell } from '../../../../components/AppShell';
import { eomApiUrl } from '../../../eomApi';

export default function TeamSkillsPage() {
  const params = useParams<{ id: string }>();
  const [skills, setSkills] = useState<any[]>([]);
  const [team, setTeam] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!params?.id) return;
    let mounted = true;
    (async () => {
      try {
        const [skRes, teamRes] = await Promise.all([
          fetch(eomApiUrl(`/eom/teams/${params.id}/skills`)),
          fetch(eomApiUrl(`/eom/teams/${params.id}`)),
        ]);
        if (skRes.ok) { const body = await skRes.json(); if (mounted) setSkills(body.items || []); }
        if (teamRes.ok) { const body = await teamRes.json(); if (mounted) setTeam(body); }
      } finally { if (mounted) setLoading(false); }
    })();
    return () => { mounted = false; };
  }, [params?.id]);

  const levelColor = (level: string) => {
    const l = (level || '').toLowerCase();
    if (['expert', 'advanced'].includes(l)) return 'bg-green-100 text-green-800';
    if (['intermediate', 'competent'].includes(l)) return 'bg-yellow-100 text-yellow-800';
    return 'bg-gray-100 text-gray-800';
  };

  if (loading) return <AppShell><div className="p-4 text-sm text-text-secondary">Loading…</div></AppShell>;
  if (!team) return <AppShell><div className="p-4 text-sm text-text-secondary">Team not found.</div></AppShell>;

  return (
    <AppShell>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-primary-600">Team Skills Matrix</p>
            <h2 className="text-xl font-semibold">{team.name}</h2>
            <p className="text-sm text-text-secondary">{team.code} · {skills.length} skill records</p>
          </div>
          <Link href={`/eom/teams/${params.id}`} className="btn">Back to Team</Link>
        </div>

        <div className="overflow-x-auto rounded-md border">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 text-left">
                <th className="p-3 font-medium">Employee ID</th>
                <th className="p-3 font-medium">Skill Name</th>
                <th className="p-3 font-medium">Level</th>
                <th className="p-3 font-medium">Certification</th>
                <th className="p-3 font-medium">Expiry Date</th>
              </tr>
            </thead>
            <tbody>
              {skills.length === 0 && (
                <tr><td colSpan={5} className="p-3 text-center text-text-secondary">No skills found.</td></tr>
              )}
              {skills.map((s: any) => (
                <tr key={s.id} className="border-t hover:bg-gray-50">
                  <td className="p-3">{s.employee_id}</td>
                  <td className="p-3 font-medium">{s.skill_name}</td>
                  <td className="p-3">
                    <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${levelColor(s.level)}`}>
                      {s.level || '—'}
                    </span>
                  </td>
                  <td className="p-3">{s.certification || '—'}</td>
                  <td className="p-3">{s.expiry_date || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </AppShell>
  );
}