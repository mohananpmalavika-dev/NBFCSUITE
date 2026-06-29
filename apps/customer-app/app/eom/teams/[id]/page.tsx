"use client";

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { AppShell } from '../../../components/AppShell';
import { eomApiUrl } from '../../eomApi';

export default function TeamDetailPage() {
  const params = useParams<{ id: string }>();
  const [team, setTeam] = useState<any>(null);
  const [members, setMembers] = useState<any[]>([]);
  const [skills, setSkills] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!params?.id) return;
    let mounted = true;
    (async () => {
      try {
        const [teamRes, membersRes, skillsRes] = await Promise.all([
          fetch(eomApiUrl(`/eom/teams/${params.id}`)),
          fetch(eomApiUrl(`/eom/teams/${params.id}/members`)),
          fetch(eomApiUrl(`/eom/teams/${params.id}/skills`)),
        ]);
        if (teamRes.ok) {
          const body = await teamRes.json();
          if (mounted) setTeam(body);
        }
        if (membersRes.ok) {
          const body = await membersRes.json();
          if (mounted) setMembers(body.items || []);
        }
        if (skillsRes.ok) {
          const body = await skillsRes.json();
          if (mounted) setSkills(body.items || []);
        }
      } finally {
        if (mounted) setLoading(false);
      }
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
            <p className="text-sm font-medium text-primary-600">Team 360</p>
            <h2 className="text-xl font-semibold">{team.name}</h2>
            <p className="text-sm text-text-secondary">{team.code} · {team.team_type || 'Team'} · {team.status}</p>
          </div>
          <Link href="/eom/teams" className="btn">Back to teams</Link>
        </div>

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

          {/* Quick links */}
          <section className="rounded-md border p-4 space-y-3">
            <h3 className="font-semibold">Team Analytics</h3>
            <div className="flex flex-wrap gap-2">
              <Link href={`/eom/teams/${team.id}/capacity`} className="btn">Capacity</Link>
              <Link href={`/eom/teams/${team.id}/workload`} className="btn">Workload</Link>
              <Link href={`/eom/teams/${team.id}/health`} className="btn">Health</Link>
            </div>
          </section>
        </div>

        {/* Skills */}
        <section className="rounded-md border p-4 space-y-3">
          <h3 className="font-semibold">Skills</h3>
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
                  {skills.map((s: any) => (
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
          <h3 className="font-semibold">Members ({members.length})</h3>
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
                  {members.map((m: any) => (
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
      </div>
    </AppShell>
  );
}
