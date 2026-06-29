"use client";

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { AppShell } from '../../../components/AppShell';
import { eomApiUrl } from '../../eomApi';

export default function NewPositionPage() {
  const router = useRouter();
  const [form, setForm] = useState<any>({
    code: '',
    title: '',
    status: 'open',
    grade_id: '',
    team_id: '',
    reports_to_position_id: '',
    description: '',
  });
  const [grades, setGrades] = useState<any[]>([]);
  const [teams, setTeams] = useState<any[]>([]);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const [gradesRes, teamsRes] = await Promise.all([
          fetch(eomApiUrl('/eom/grades')),
          fetch(eomApiUrl('/eom/teams')),
        ]);
        const gradesBody = gradesRes.ok ? await gradesRes.json() : { items: [] };
        const teamsBody = teamsRes.ok ? await teamsRes.json() : { items: [] };
        if (mounted) {
          setGrades(Array.isArray(gradesBody) ? gradesBody : gradesBody.items || []);
          setTeams(Array.isArray(teamsBody) ? teamsBody : teamsBody.items || []);
        }
      } catch (e) {
      }
    })();
    return () => { mounted = false; };
  }, []);

  function update(field: string, value: any) {
    setForm((s: any) => ({ ...s, [field]: value }));
  }

  async function submit() {
    setSaving(true);
    try {
      const payload = {
        code: form.code,
        title: form.title,
        status: form.status,
        grade_id: form.grade_id || undefined,
        team_id: form.team_id || undefined,
        reports_to_position_id: form.reports_to_position_id || undefined,
        description: form.description || undefined,
      };
      const res = await fetch(eomApiUrl('/eom/positions'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-User-Roles': 'enterprise.admin' },
        body: JSON.stringify(payload),
      });
      if (res.ok) {
        const body = await res.json();
        router.push(`/eom/positions/${body.id}`);
      } else {
        const body = await res.json().catch(() => null);
        alert('Failed to create: ' + (body?.detail || JSON.stringify(body)));
      }
    } finally {
      setSaving(false);
    }
  }

  return (
    <AppShell>
      <div className="space-y-4 max-w-3xl">
        <h2 className="text-xl font-semibold">New Position</h2>

        <div className="rounded-md border p-4 space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <label className="block space-y-2">
              <span className="text-sm font-medium">Code</span>
              <input className="input" value={form.code} onChange={(e) => update('code', e.target.value)} />
            </label>
            <label className="block space-y-2">
              <span className="text-sm font-medium">Title</span>
              <input className="input" value={form.title} onChange={(e) => update('title', e.target.value)} />
            </label>
            <label className="block space-y-2">
              <span className="text-sm font-medium">Status</span>
              <select className="input" value={form.status} onChange={(e) => update('status', e.target.value)}>
                <option value="open">Open</option>
                <option value="filled">Filled</option>
                <option value="draft">Draft</option>
              </select>
            </label>
            <label className="block space-y-2">
              <span className="text-sm font-medium">Grade</span>
              <select className="input" value={form.grade_id} onChange={(e) => update('grade_id', e.target.value)}>
                <option value="">Select grade</option>
                {grades.map((grade) => (
                  <option key={grade.id} value={grade.id}>{grade.code} - {grade.name}</option>
                ))}
              </select>
            </label>
            <label className="block space-y-2">
              <span className="text-sm font-medium">Team</span>
              <select className="input" value={form.team_id} onChange={(e) => update('team_id', e.target.value)}>
                <option value="">Select team</option>
                {teams.map((team) => (
                  <option key={team.id} value={team.id}>{team.code} - {team.name}</option>
                ))}
              </select>
            </label>
            <label className="block space-y-2 md:col-span-2">
              <span className="text-sm font-medium">Reports To Position ID</span>
              <input className="input" value={form.reports_to_position_id} onChange={(e) => update('reports_to_position_id', e.target.value)} placeholder="Position id" />
            </label>
            <label className="block space-y-2 md:col-span-2">
              <span className="text-sm font-medium">Description</span>
              <textarea className="input min-h-[120px]" value={form.description} onChange={(e) => update('description', e.target.value)} />
            </label>
          </div>

          <div className="flex gap-2">
            <button type="button" className="btn" onClick={() => router.back()}>Cancel</button>
            <button type="button" className="btn btn-primary" onClick={submit} disabled={saving || !form.code.trim() || !form.title.trim()}>
              {saving ? 'Saving…' : 'Create Position'}
            </button>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
