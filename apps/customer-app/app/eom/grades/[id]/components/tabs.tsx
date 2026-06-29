"use client";

import { useEffect, useState } from 'react';
import { getJson, putJson } from './gradeApi';
import React from 'react';

import { SectionHeader } from './GradeTabShell';

export function OverviewTab({ gradeId: _gradeId, grade, health }: { gradeId: string; grade: any; health: any }) {
  return (
    <div className="p-4">
      <div className="grid md:grid-cols-3 gap-4">
        <div className="border rounded p-4">
          <div className="text-sm text-gray-600">Grade</div>
          <div className="text-lg font-semibold">{grade?.code}</div>
          <div className="text-sm text-gray-700">{grade?.name}</div>
        </div>
        <div className="border rounded p-4">
          <div className="text-sm text-gray-600">Level</div>
          <div className="text-lg font-semibold">{grade?.level ?? '-'}</div>
          <div className="text-sm text-gray-700">Category: {grade?.category ?? '-'}</div>
        </div>
        <div className="border rounded p-4">
          <div className="text-sm text-gray-600">Grade Health</div>
          <div className="text-lg font-semibold">{health?.score ?? 0}%</div>
          <div className="text-sm text-gray-700">{health?.rating ?? ''}</div>
        </div>
      </div>

      <div className="mt-4 border rounded p-4">
        <div className="text-sm text-gray-600">Description</div>
        <div className="text-sm text-gray-800 mt-1">{grade?.description ?? '-'}</div>
        {health?.issues?.length ? (
          <div className="mt-3">
            <div className="text-sm font-semibold">Issues</div>
            <ul className="text-sm list-disc ml-5 text-gray-700">
              {health.issues.map((it: string) => (
                <li key={it}>{it}</li>
              ))}
            </ul>
          </div>
        ) : null}
      </div>
    </div>
  );
}

export function SalaryTab({ gradeId }: { gradeId: string }) {
  const [salary, setSalary] = useState<any | null>(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      const s = await getJson<any>(`/eom/grades/${gradeId}/salary`);
      setSalary(s ?? null);
    })().catch((e) => setError(e?.message ?? 'Failed to load salary'));
  }, [gradeId]);

  async function onSave() {
    setSaving(true);
    setError(null);
    try {
      await putJson(`/eom/grades/${gradeId}/salary`, {
        minimum_salary: salary?.minimum_salary ? Number(salary.minimum_salary) : null,
        mid_salary: salary?.mid_salary ? Number(salary.mid_salary) : null,
        maximum_salary: salary?.maximum_salary ? Number(salary.maximum_salary) : null,
        currency: salary?.currency ?? null,
        increment_policy: salary?.increment_policy ?? null,
        bonus_eligibility: salary?.bonus_eligibility ?? null,
      });
    } catch (e: any) {
      setError(e?.message ?? 'Failed to save salary');
    } finally {
      setSaving(false);
    }
  }

  if (error) {
    return (
      <div className="p-4 text-red-700 text-sm">{error}</div>
    );
  }
  if (!salary) return <div className="p-4 text-gray-500">Loading...</div>;

  return (
    <div className="p-4">
      <SectionHeader title="Salary Band" subtitle="Minimum / Mid / Maximum" />

      <div className="grid md:grid-cols-2 gap-3">
        <label className="block">
          <span className="text-sm">Minimum Salary</span>
          <input className="border rounded w-full p-2" value={salary.minimum_salary ?? ''} onChange={(e) => setSalary({ ...salary, minimum_salary: e.target.value })} />
        </label>
        <label className="block">
          <span className="text-sm">Mid Salary</span>
          <input className="border rounded w-full p-2" value={salary.mid_salary ?? ''} onChange={(e) => setSalary({ ...salary, mid_salary: e.target.value })} />
        </label>
        <label className="block">
          <span className="text-sm">Maximum Salary</span>
          <input className="border rounded w-full p-2" value={salary.maximum_salary ?? ''} onChange={(e) => setSalary({ ...salary, maximum_salary: e.target.value })} />
        </label>
        <label className="block">
          <span className="text-sm">Currency</span>
          <input className="border rounded w-full p-2" value={salary.currency ?? ''} onChange={(e) => setSalary({ ...salary, currency: e.target.value })} />
        </label>
        <label className="block">
          <span className="text-sm">Increment Policy</span>
          <input className="border rounded w-full p-2" value={salary.increment_policy ?? ''} onChange={(e) => setSalary({ ...salary, increment_policy: e.target.value })} />
        </label>
        <label className="block">
          <span className="text-sm">Bonus Eligibility</span>
          <input className="border rounded w-full p-2" value={salary.bonus_eligibility ?? ''} onChange={(e) => setSalary({ ...salary, bonus_eligibility: e.target.value })} />
        </label>
      </div>

      <div className="mt-4 flex justify-end">
        <button onClick={onSave} disabled={saving} className="px-4 py-2 rounded bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50">
          {saving ? 'Saving...' : 'Save'}
        </button>
      </div>
    </div>
  );
}

export function ReadOnlyListTab({
  gradeId,
  title,
  fetchPath,
  renderRow,
}: {
  gradeId: string;
  title: string;
  fetchPath: string;
  renderRow: (item: any, idx: number) => React.ReactNode;
}) {
  const [items, setItems] = useState<any[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      const res = await getJson<any>(fetchPath);
      setItems(Array.isArray(res) ? res : res?.items ?? []);
    })().catch((e) => setError(e?.message ?? 'Failed to load'));
  }, [gradeId, fetchPath]);

  if (error) return <div className="p-4 text-red-700 text-sm">{error}</div>;
  if (!items) return <div className="p-4 text-gray-500">Loading...</div>;

  return (
    <div className="p-4">
      <SectionHeader title={title} />
      <div className="border rounded overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-left">
            <tr>
              <th className="p-3">#</th>
              <th className="p-3">Item</th>
            </tr>
          </thead>
          <tbody>
            {items.map((it, idx) => (
              <tr key={idx} className="border-t">
                <td className="p-3 text-gray-500">{idx + 1}</td>
                <td className="p-3">{renderRow(it, idx)}</td>
              </tr>
            ))}
            {!items.length ? (
              <tr>
                <td colSpan={2} className="p-6 text-gray-500">No data</td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export function TrainingTab({ gradeId }: { gradeId: string }) {
  return (
    <ReadOnlyListTab
      gradeId={gradeId}
      title="Training Requirements"
      fetchPath={`/eom/grades/${gradeId}/training`}
      renderRow={(it) => (
        <div>
          <div className="font-medium">{it.training_name}</div>
          <div className="text-xs text-gray-600">Mandatory: {it.mandatory ?? '-'}</div>
          <div className="text-xs text-gray-600">Required Level: {it.required_level ?? '-'}</div>
        </div>
      )}
    />
  );
}

export function CompetenciesTab({ gradeId }: { gradeId: string }) {
  return (
    <ReadOnlyListTab
      gradeId={gradeId}
      title="Competency Framework"
      fetchPath={`/eom/grades/${gradeId}/competencies`}
      renderRow={(it) => (
        <div>
          <div className="font-medium">{it.competency_type}</div>
          <div className="text-xs text-gray-600">Required Level: {it.required_level ?? '-'}</div>
        </div>
      )}
    />
  );
}

export function BenefitsTab({ gradeId: _gradeId }: { gradeId: string }) {
  return <div className="p-4 text-gray-500">Benefits tab rendering pending (GET/PUT wiring next).</div>;
}

export function LeaveTab({ gradeId: _gradeId }: { gradeId: string }) {
  return <div className="p-4 text-gray-500">Leave tab rendering pending (GET/PUT wiring next).</div>;
}

export function ApprovalsTab({ gradeId: _gradeId }: { gradeId: string }) {
  return <div className="p-4 text-gray-500">Approvals tab rendering pending (GET/PUT wiring next).</div>;
}

export function CareerTab({ gradeId: _gradeId }: { gradeId: string }) {
  return <div className="p-4 text-gray-500">Career Path tab rendering pending (GET/PUT wiring next).</div>;
}

export function DocumentsTab({ gradeId: _gradeId }: { gradeId: string }) {
  return <div className="p-4 text-gray-500">Documents tab rendering pending (GET/PUT wiring next).</div>;
}

export function TimelineTab({ gradeId: _gradeId }: { gradeId: string }) {
  return <div className="p-4 text-gray-500">Timeline tab rendering pending (GET /timeline).</div>;
}

export function AuditTab({ gradeId: _gradeId }: { gradeId: string }) {
  return <div className="p-4 text-gray-500">Audit tab rendering pending (GET /audit).</div>;
}

export function AiTab({ gradeId: _gradeId }: { gradeId: string }) {
  return <div className="p-4 text-gray-500">AI tab rendering pending (GET /ai).</div>;
}

export function PlaceholderTab({ label }: { label: string }) {
  return <div className="p-4 text-gray-500">{label}</div>;
}

