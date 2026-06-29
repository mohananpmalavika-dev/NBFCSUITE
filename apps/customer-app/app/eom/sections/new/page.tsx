"use client";

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { AppShell } from '../../../components/AppShell';
import { eomApiUrl } from '../../eomApi';

type FormData = {
  // Step 1 — General
  code: string;
  name: string;
  department: string;
  type: string;
  status: string;
  // Step 2 — Organization
  section_head: string;
  deputy_head: string;
  business_unit: string;
  branch: string;
  reporting_department: string;
  // Step 3 — Operations
  working_calendar: string;
  shift: string;
  capacity: string;
  business_hours: string;
  sla_profile: string;
  // Step 4 — Services
  service_catalog: string;
  business_capabilities: string;
  workflows: string;
};

const initialData: FormData = {
  code: '',
  name: '',
  department: '',
  type: '',
  status: 'active',
  section_head: '',
  deputy_head: '',
  business_unit: '',
  branch: '',
  reporting_department: '',
  working_calendar: '',
  shift: '',
  capacity: '',
  business_hours: '',
  sla_profile: '',
  service_catalog: '',
  business_capabilities: '',
  workflows: '',
};

const SECTION_TYPES = [
  'Operations',
  'Sales',
  'Support',
  'Compliance',
  'Audit',
  'Technology',
  'Finance',
  'Administration',
  'Quality',
  'Training',
];

const TOTAL_STEPS = 5;

export default function NewSectionPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [form, setForm] = useState<FormData>(initialData);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const update = (field: keyof FormData, value: string) =>
    setForm((prev) => ({ ...prev, [field]: value }));

  const canNext = (): boolean => {
    if (step === 1) return form.code.trim() !== '' && form.name.trim() !== '' && form.department.trim() !== '';
    if (step === 2) return true;
    if (step === 3) return true;
    if (step === 4) return true;
    return true;
  };

  const handleNext = () => {
    if (step < TOTAL_STEPS && canNext()) setStep((s) => s + 1);
  };

  const handlePrev = () => {
    if (step > 1) setStep((s) => s - 1);
  };

  const handleSubmit = async () => {
    if (submitting) return;
    setSubmitting(true);
    setError('');
    try {
      const res = await fetch(eomApiUrl('/eom/sections'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-Roles': 'enterprise.admin',
        },
        body: JSON.stringify(form),
      });
      if (!res.ok) {
        const msg = await res.text().catch(() => '');
        throw new Error(msg || `HTTP ${res.status}`);
      }
      const created = await res.json();
      router.push(`/eom/sections/${created.id}`);
    } catch (err: any) {
      setError(err.message || 'Something went wrong');
    } finally {
      setSubmitting(false);
    }
  };

  const renderStepIndicator = () => (
    <div className="flex items-center gap-2 text-sm">
      {Array.from({ length: TOTAL_STEPS }, (_, i) => i + 1).map((s) => (
        <React.Fragment key={s}>
          {s > 1 && <span className="text-gray-300">—</span>}
          <button
            type="button"
            className={`rounded-full w-7 h-7 text-xs font-bold flex items-center justify-center border ${
              s === step
                ? 'bg-primary-600 text-white border-primary-600'
                : s < step
                ? 'bg-green-100 text-green-800 border-green-300'
                : 'bg-gray-50 text-gray-400 border-gray-200'
            }`}
            onClick={() => s < step && setStep(s)}
            title={`Step ${s}`}
          >
            {s < step ? '✓' : s}
          </button>
        </React.Fragment>
      ))}
      <span className="ml-2 text-text-secondary">Step {step} of {TOTAL_STEPS}</span>
    </div>
  );

  /* ---------- Step 1 — General ---------- */
  const StepGeneral = () => (
    <div className="space-y-4">
      <h3 className="font-semibold">General Information</h3>
      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <label className="block text-sm font-medium mb-1">Code *</label>
          <input className="input" placeholder="e.g. SEC-001" value={form.code} onChange={(e) => update('code', e.target.value)} />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Name *</label>
          <input className="input" placeholder="e.g. Retail Lending" value={form.name} onChange={(e) => update('name', e.target.value)} />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Department *</label>
          <input className="input" placeholder="e.g. Operations" value={form.department} onChange={(e) => update('department', e.target.value)} />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Type</label>
          <select className="input" value={form.type} onChange={(e) => update('type', e.target.value)}>
            <option value="">— Select —</option>
            {SECTION_TYPES.map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Status</label>
          <select className="input" value={form.status} onChange={(e) => update('status', e.target.value)}>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
          </select>
        </div>
      </div>
    </div>
  );

  /* ---------- Step 2 — Organization ---------- */
  const StepOrganization = () => (
    <div className="space-y-4">
      <h3 className="font-semibold">Organization</h3>
      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <label className="block text-sm font-medium mb-1">Section Head</label>
          <input className="input" placeholder="Name" value={form.section_head} onChange={(e) => update('section_head', e.target.value)} />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Deputy Head</label>
          <input className="input" placeholder="Name" value={form.deputy_head} onChange={(e) => update('deputy_head', e.target.value)} />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Business Unit</label>
          <input className="input" placeholder="e.g. Retail Banking" value={form.business_unit} onChange={(e) => update('business_unit', e.target.value)} />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Branch</label>
          <input className="input" placeholder="e.g. HO-001" value={form.branch} onChange={(e) => update('branch', e.target.value)} />
        </div>
        <div className="sm:col-span-2">
          <label className="block text-sm font-medium mb-1">Reporting Department</label>
          <input className="input" placeholder="e.g. Operations" value={form.reporting_department} onChange={(e) => update('reporting_department', e.target.value)} />
        </div>
      </div>
    </div>
  );

  /* ---------- Step 3 — Operations ---------- */
  const StepOperations = () => (
    <div className="space-y-4">
      <h3 className="font-semibold">Operations</h3>
      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <label className="block text-sm font-medium mb-1">Working Calendar</label>
          <input className="input" placeholder="e.g. Standard 5-day" value={form.working_calendar} onChange={(e) => update('working_calendar', e.target.value)} />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Shift</label>
          <input className="input" placeholder="e.g. General" value={form.shift} onChange={(e) => update('shift', e.target.value)} />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Capacity</label>
          <input className="input" placeholder="e.g. 50" value={form.capacity} onChange={(e) => update('capacity', e.target.value)} />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Business Hours</label>
          <input className="input" placeholder="e.g. 09:00–18:00" value={form.business_hours} onChange={(e) => update('business_hours', e.target.value)} />
        </div>
        <div className="sm:col-span-2">
          <label className="block text-sm font-medium mb-1">SLA Profile</label>
          <input className="input" placeholder="e.g. Gold SLA" value={form.sla_profile} onChange={(e) => update('sla_profile', e.target.value)} />
        </div>
      </div>
    </div>
  );

  /* ---------- Step 4 — Services ---------- */
  const StepServices = () => (
    <div className="space-y-4">
      <h3 className="font-semibold">Services</h3>
      <div className="grid gap-4">
        <div>
          <label className="block text-sm font-medium mb-1">Service Catalog</label>
          <textarea className="input min-h-[80px]" placeholder="Describe services offered by this section" value={form.service_catalog} onChange={(e) => update('service_catalog', e.target.value)} />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Business Capabilities</label>
          <textarea className="input min-h-[80px]" placeholder="List business capabilities" value={form.business_capabilities} onChange={(e) => update('business_capabilities', e.target.value)} />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Workflows</label>
          <textarea className="input min-h-[80px]" placeholder="Describe workflows" value={form.workflows} onChange={(e) => update('workflows', e.target.value)} />
        </div>
      </div>
    </div>
  );

  /* ---------- Step 5 — Review ---------- */
  const StepReview = () => {
    const rows: { label: string; key: keyof FormData }[] = [
      { label: 'Code', key: 'code' },
      { label: 'Name', key: 'name' },
      { label: 'Department', key: 'department' },
      { label: 'Type', key: 'type' },
      { label: 'Status', key: 'status' },
      { label: 'Section Head', key: 'section_head' },
      { label: 'Deputy Head', key: 'deputy_head' },
      { label: 'Business Unit', key: 'business_unit' },
      { label: 'Branch', key: 'branch' },
      { label: 'Reporting Department', key: 'reporting_department' },
      { label: 'Working Calendar', key: 'working_calendar' },
      { label: 'Shift', key: 'shift' },
      { label: 'Capacity', key: 'capacity' },
      { label: 'Business Hours', key: 'business_hours' },
      { label: 'SLA Profile', key: 'sla_profile' },
      { label: 'Service Catalog', key: 'service_catalog' },
      { label: 'Business Capabilities', key: 'business_capabilities' },
      { label: 'Workflows', key: 'workflows' },
    ];

    return (
      <div className="space-y-4">
        <h3 className="font-semibold">Review & Submit</h3>
        <p className="text-sm text-text-secondary">Please verify the data below before submitting.</p>
        <div className="grid gap-3 sm:grid-cols-2 text-sm">
          {rows.map(({ label, key }) => {
            const val = form[key];
            if (!val) return null;
            return (
              <div key={key}>
                <span className="font-medium">{label}:</span>{' '}
                <span className="text-text-secondary whitespace-pre-wrap">{val}</span>
              </div>
            );
          })}
        </div>
        {error && <div className="text-red-600 text-sm">{error}</div>}
      </div>
    );
  };

  return (
    <AppShell>
      <div className="max-w-2xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold">New Section</h2>
          <button type="button" className="btn" onClick={() => router.push('/eom/sections')}>Cancel</button>
        </div>

        {renderStepIndicator()}

        <div className="rounded-md border p-4">
          {step === 1 && <StepGeneral />}
          {step === 2 && <StepOrganization />}
          {step === 3 && <StepOperations />}
          {step === 4 && <StepServices />}
          {step === 5 && <StepReview />}
        </div>

        <div className="flex items-center justify-between">
          <button
            type="button"
            className="btn"
            disabled={step === 1}
            onClick={handlePrev}
          >
            Previous
          </button>
          {step < TOTAL_STEPS ? (
            <button
              type="button"
              className="btn btn-primary"
              disabled={!canNext()}
              onClick={handleNext}
            >
              Next
            </button>
          ) : (
            <button
              type="button"
              className="btn btn-primary"
              disabled={submitting}
              onClick={handleSubmit}
            >
              {submitting ? 'Submitting…' : 'Submit'}
            </button>
          )}
        </div>
      </div>
    </AppShell>
  );
}