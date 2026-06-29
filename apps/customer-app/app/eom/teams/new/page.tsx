"use client";

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { AppShell } from '../../../components/AppShell';
import { eomApiUrl } from '../../eomApi';

type FormData = {
  code: string; name: string; team_type: string; section_id: string; status: string;
  team_lead: string; deputy_lead: string; reporting_manager: string;
  shift: string; capacity: string; working_days: string; business_calendar: string; location: string;
  primary_skills: string; secondary_skills: string; certifications: string; required_competencies: string;
};

const TEAM_TYPES = [
  'Permanent Team', 'Project Team', 'Task Force', 'Virtual Team',
  'Cross Functional Team', 'Shift Team', 'Regional Team', 'Support Team',
];

const TOTAL_STEPS = 6;

export default function NewTeamPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [form, setForm] = useState<FormData>({
    code: '', name: '', team_type: '', section_id: '', status: 'active',
    team_lead: '', deputy_lead: '', reporting_manager: '',
    shift: '', capacity: '', working_days: '', business_calendar: '', location: '',
    primary_skills: '', secondary_skills: '', certifications: '', required_competencies: '',
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const update = (f: keyof FormData, v: string) => setForm((s) => ({ ...s, [f]: v }));

  const canNext = () => step !== 1 || (form.code.trim() !== '' && form.name.trim() !== '');

  const stepIndicator = () => (
    <div className="flex items-center gap-2 text-sm">
      {Array.from({ length: TOTAL_STEPS }, (_, i) => i + 1).map((s) => (
        <React.Fragment key={s}>
          {s > 1 && <span className="text-gray-300">—</span>}
          <button type="button"
            className={`rounded-full w-7 h-7 text-xs font-bold flex items-center justify-center border ${
              s === step ? 'bg-primary-600 text-white border-primary-600' :
              s < step ? 'bg-green-100 text-green-800 border-green-300' :
              'bg-gray-50 text-gray-400 border-gray-200'
            }`}
            onClick={() => s < step && setStep(s)}
          >{s < step ? '✓' : s}</button>
        </React.Fragment>
      ))}
      <span className="ml-2 text-text-secondary">Step {step} of {TOTAL_STEPS}</span>
    </div>
  );

  const handleSubmit = async () => {
    setSubmitting(true); setError('');
    try {
      const res = await fetch(eomApiUrl('/eom/teams'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-User-Roles': 'enterprise.admin' },
        body: JSON.stringify(form),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const created = await res.json();
      router.push(`/eom/teams/${created.id}`);
    } catch (e: any) {
      setError(e.message || 'Failed to create team');
    } finally { setSubmitting(false); }
  };

  return (
    <AppShell>
      <div className="max-w-2xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold">New Team</h2>
          <button type="button" className="btn" onClick={() => router.push('/eom/teams')}>Cancel</button>
        </div>

        {stepIndicator()}

        <div className="rounded-md border p-4">
          {step === 1 && (
            <div className="space-y-4">
              <h3 className="font-semibold">General</h3>
              <div className="grid gap-4 sm:grid-cols-2">
                <div><label className="block text-sm font-medium mb-1">Team Code *</label><input className="input" value={form.code} onChange={(e) => update('code', e.target.value)} /></div>
                <div><label className="block text-sm font-medium mb-1">Team Name *</label><input className="input" value={form.name} onChange={(e) => update('name', e.target.value)} /></div>
                <div><label className="block text-sm font-medium mb-1">Team Type</label>
                  <select className="input" value={form.team_type} onChange={(e) => update('team_type', e.target.value)}>
                    <option value="">— Select —</option>
                    {TEAM_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
                  </select>
                </div>
                <div><label className="block text-sm font-medium mb-1">Section</label><input className="input" value={form.section_id} onChange={(e) => update('section_id', e.target.value)} /></div>
                <div><label className="block text-sm font-medium mb-1">Status</label>
                  <select className="input" value={form.status} onChange={(e) => update('status', e.target.value)}>
                    <option value="active">Active</option>
                    <option value="inactive">Inactive</option>
                    <option value="draft">Draft</option>
                  </select>
                </div>
              </div>
            </div>
          )}

          {step === 2 && (
            <div className="space-y-4">
              <h3 className="font-semibold">Leadership</h3>
              <div className="grid gap-4 sm:grid-cols-2">
                <div><label className="block text-sm font-medium mb-1">Team Lead</label><input className="input" value={form.team_lead} onChange={(e) => update('team_lead', e.target.value)} /></div>
                <div><label className="block text-sm font-medium mb-1">Deputy Lead</label><input className="input" value={form.deputy_lead} onChange={(e) => update('deputy_lead', e.target.value)} /></div>
                <div className="sm:col-span-2"><label className="block text-sm font-medium mb-1">Reporting Manager</label><input className="input" value={form.reporting_manager} onChange={(e) => update('reporting_manager', e.target.value)} /></div>
              </div>
            </div>
          )}

          {step === 3 && (
            <div className="space-y-4">
              <h3 className="font-semibold">Operations</h3>
              <div className="grid gap-4 sm:grid-cols-2">
                <div><label className="block text-sm font-medium mb-1">Shift</label><input className="input" value={form.shift} onChange={(e) => update('shift', e.target.value)} /></div>
                <div><label className="block text-sm font-medium mb-1">Capacity</label><input className="input" value={form.capacity} onChange={(e) => update('capacity', e.target.value)} /></div>
                <div><label className="block text-sm font-medium mb-1">Working Days</label><input className="input" value={form.working_days} onChange={(e) => update('working_days', e.target.value)} /></div>
                <div><label className="block text-sm font-medium mb-1">Business Calendar</label><input className="input" value={form.business_calendar} onChange={(e) => update('business_calendar', e.target.value)} /></div>
                <div className="sm:col-span-2"><label className="block text-sm font-medium mb-1">Location</label><input className="input" value={form.location} onChange={(e) => update('location', e.target.value)} /></div>
              </div>
            </div>
          )}

          {step === 4 && (
            <div className="space-y-4">
              <h3 className="font-semibold">Skills</h3>
              <div className="grid gap-4">
                <div><label className="block text-sm font-medium mb-1">Primary Skills</label><textarea className="input min-h-[60px]" value={form.primary_skills} onChange={(e) => update('primary_skills', e.target.value)} /></div>
                <div><label className="block text-sm font-medium mb-1">Secondary Skills</label><textarea className="input min-h-[60px]" value={form.secondary_skills} onChange={(e) => update('secondary_skills', e.target.value)} /></div>
                <div><label className="block text-sm font-medium mb-1">Certifications</label><textarea className="input min-h-[60px]" value={form.certifications} onChange={(e) => update('certifications', e.target.value)} /></div>
                <div><label className="block text-sm font-medium mb-1">Required Competencies</label><textarea className="input min-h-[60px]" value={form.required_competencies} onChange={(e) => update('required_competencies', e.target.value)} /></div>
              </div>
            </div>
          )}

          {step === 5 && (
            <div className="space-y-4">
              <h3 className="font-semibold">Projects</h3>
              <p className="text-sm text-text-secondary">Project assignments can be configured after team creation from the team profile.</p>
              <div className="grid gap-4 sm:grid-cols-2">
                <div><label className="block text-sm font-medium mb-1">Default Project ID</label><input className="input" /></div>
                <div><label className="block text-sm font-medium mb-1">Default Project Name</label><input className="input" /></div>
                <div><label className="block text-sm font-medium mb-1">Product</label><input className="input" /></div>
                <div><label className="block text-sm font-medium mb-1">Customer</label><input className="input" /></div>
              </div>
            </div>
          )}

          {step === 6 && (
            <div className="space-y-4">
              <h3 className="font-semibold">Review & Create</h3>
              <p className="text-sm text-text-secondary">Please verify the data below before submitting.</p>
              <div className="grid gap-3 sm:grid-cols-2 text-sm">
                {Object.entries(form).map(([key, val]) => val ? (
                  <div key={key}><span className="font-medium">{key.replace(/_/g, ' ')}:</span> <span className="text-text-secondary">{val}</span></div>
                ) : null)}
              </div>
              {error && <div className="text-red-600 text-sm">{error}</div>}
            </div>
          )}
        </div>

        <div className="flex items-center justify-between">
          <button type="button" className="btn" disabled={step === 1} onClick={() => setStep((s) => s - 1)}>Previous</button>
          {step < TOTAL_STEPS ? (
            <button type="button" className="btn btn-primary" disabled={!canNext()} onClick={() => setStep((s) => s + 1)}>Next</button>
          ) : (
            <button type="button" className="btn btn-primary" disabled={submitting} onClick={handleSubmit}>
              {submitting ? 'Creating…' : 'Create Team'}
            </button>
          )}
        </div>
      </div>
    </AppShell>
  );
}
