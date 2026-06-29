"use client";

import { useMemo, useState } from 'react';
import { AppShell } from '../../../components/AppShell';
import { eomApiUrl } from './eomApi';



const defaultProfile = {
  code: '',
  name: '',
  level: '',
  category: '',
  status: 'draft' as const,
  description: '',
};

export default function CreateGradePage() {
  const [form, setForm] = useState(defaultProfile);
  const [salary, setSalary] = useState({
    minimum_salary: '',
    mid_salary: '',
    maximum_salary: '',
    currency: 'INR',
    increment_policy: 'annual',
    bonus_eligibility: 'yes',
  });

  const [loading, setLoading] = useState(false);
  const [createdId, setCreatedId] = useState<string | null>(null);

  const disabled = useMemo(() => !form.code.trim() || !form.name.trim(), [form.code, form.name]);

  async function onCreate() {
    setLoading(true);
    try {
      const res = await fetch(eomApiUrl('/eom/grades'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          code: form.code,
          name: form.name,
          level: form.level || null,
          category: form.category || null,
          status: form.status,
          description: form.description || null,
        }),
      });
      if (!res.ok) return;
      const g = await res.json();
      setCreatedId(g.id);

      await fetch(eomApiUrl(`/eom/grades/${g.id}/salary`), {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          minimum_salary: salary.minimum_salary ? Number(salary.minimum_salary) : null,
          mid_salary: salary.mid_salary ? Number(salary.mid_salary) : null,
          maximum_salary: salary.maximum_salary ? Number(salary.maximum_salary) : null,
          currency: salary.currency || null,
          increment_policy: salary.increment_policy || null,
          bonus_eligibility: salary.bonus_eligibility || null,
        }),
      });
    } finally {
      setLoading(false);
    }
  }

  return (
    <AppShell>
      <div className="p-6 max-w-3xl">
        <h1 className="text-2xl font-semibold mb-2">Create Grade Wizard</h1>
        <p className="text-sm text-gray-600 mb-6">Steps 1–10 UI scaffold with full tab pages.</p>

        <div className="grid gap-4">
          <div className="border rounded p-4">
            <h2 className="font-semibold mb-3">Step 1 — General</h2>
            <div className="grid md:grid-cols-2 gap-3">
              <label className="block">
                <span className="text-sm">Grade Code</span>
                <input className="border rounded w-full p-2" value={form.code} onChange={(e) => setForm({ ...form, code: e.target.value })} />
              </label>
              <label className="block">
                <span className="text-sm">Grade Name</span>
                <input className="border rounded w-full p-2" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
              </label>
              <label className="block">
                <span className="text-sm">Level</span>
                <input className="border rounded w-full p-2" value={form.level} onChange={(e) => setForm({ ...form, level: e.target.value })} />
              </label>
              <label className="block">
                <span className="text-sm">Category</span>
                <input className="border rounded w-full p-2" value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} />
              </label>
              <label className="block md:col-span-2">
                <span className="text-sm">Description</span>
                <textarea className="border rounded w-full p-2" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
              </label>
            </div>
          </div>

          <div className="border rounded p-4">
            <h2 className="font-semibold mb-3">Step 2 — Salary Band</h2>
            <div className="grid md:grid-cols-2 gap-3">
              <label className="block">
                <span className="text-sm">Minimum Salary</span>
                <input className="border rounded w-full p-2" value={salary.minimum_salary} onChange={(e) => setSalary({ ...salary, minimum_salary: e.target.value })} />
              </label>
              <label className="block">
                <span className="text-sm">Mid Salary</span>
                <input className="border rounded w-full p-2" value={salary.mid_salary} onChange={(e) => setSalary({ ...salary, mid_salary: e.target.value })} />
              </label>
              <label className="block">
                <span className="text-sm">Maximum Salary</span>
                <input className="border rounded w-full p-2" value={salary.maximum_salary} onChange={(e) => setSalary({ ...salary, maximum_salary: e.target.value })} />
              </label>
              <label className="block">
                <span className="text-sm">Currency</span>
                <input className="border rounded w-full p-2" value={salary.currency} onChange={(e) => setSalary({ ...salary, currency: e.target.value })} />
              </label>
              <label className="block">
                <span className="text-sm">Increment Policy</span>
                <input className="border rounded w-full p-2" value={salary.increment_policy} onChange={(e) => setSalary({ ...salary, increment_policy: e.target.value })} />
              </label>
              <label className="block">
                <span className="text-sm">Bonus Eligibility</span>
                <input className="border rounded w-full p-2" value={salary.bonus_eligibility} onChange={(e) => setSalary({ ...salary, bonus_eligibility: e.target.value })} />
              </label>
            </div>
          </div>

          <div className="flex items-center justify-end gap-3">
            {createdId ? (
              <a className="text-blue-700 hover:underline" href={`/eom/grades/${createdId}`}>Go to Profile</a>
            ) : null}
            <button
              disabled={disabled || loading}
              className="px-4 py-2 rounded bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50"
              onClick={onCreate}
            >
              {loading ? 'Creating...' : 'Create Grade'}
            </button>
          </div>
        </div>
      </div>
    </AppShell>
  );
}

