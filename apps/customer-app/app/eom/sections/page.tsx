"use client";

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { AppShell } from '../../components/AppShell';
import { eomApiUrl } from '../eomApi';

interface Section {
  id: string;
  code: string;
  name: string;
  department: string;
  section_head: string;
  employee_count: number;
  team_count: number;
  project_count: number;
  status: string;
}

export default function SectionsPage() {
  const [items, setItems] = useState<Section[]>([]);
  const [filtered, setFiltered] = useState<Section[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [deptFilter, setDeptFilter] = useState('');

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const res = await fetch(eomApiUrl('/eom/sections'));
        if (!res.ok) return;
        const body = await res.json();
        const list: Section[] = Array.isArray(body) ? body : (body.items || []);
        if (mounted) {
          setItems(list);
          setFiltered(list);
        }
      } catch {
      } finally {
        if (mounted) setLoading(false);
      }
    })();
    return () => { mounted = false; };
  }, []);

  useEffect(() => {
    let result = items;
    if (search) {
      const q = search.toLowerCase();
      result = result.filter((s) =>
        s.name?.toLowerCase().includes(q) ||
        s.code?.toLowerCase().includes(q) ||
        s.department?.toLowerCase().includes(q)
      );
    }
    if (statusFilter) {
      result = result.filter((s) => s.status === statusFilter);
    }
    if (deptFilter) {
      result = result.filter((s) => s.department === deptFilter);
    }
    setFiltered(result);
  }, [search, statusFilter, deptFilter, items]);

  const departments = [...new Set(items.map((s) => s.department).filter(Boolean))];
  const statuses = [...new Set(items.map((s) => s.status).filter(Boolean))];

  return (
    <AppShell>
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold">Sections</h2>
            <p className="text-sm text-text-secondary">Manage section profiles, organisation, operations, and services.</p>
          </div>
          <Link href="/eom/sections/new" className="btn btn-primary">New Section</Link>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <input
            className="input max-w-xs"
            placeholder="Search by name, code, department…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <select className="input max-w-[160px]" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            <option value="">All Status</option>
            {statuses.map((st) => (
              <option key={st} value={st}>{st}</option>
            ))}
          </select>
          <select className="input max-w-[200px]" value={deptFilter} onChange={(e) => setDeptFilter(e.target.value)}>
            <option value="">All Departments</option>
            {departments.map((d) => (
              <option key={d} value={d}>{d}</option>
            ))}
          </select>
        </div>

        {loading ? (
          <div className="py-8 text-center text-sm text-text-secondary">Loading…</div>
        ) : (
          <div className="overflow-x-auto rounded-md border">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-50 text-left">
                  <th className="p-3 font-semibold">Code</th>
                  <th className="p-3 font-semibold">Section</th>
                  <th className="p-3 font-semibold">Department</th>
                  <th className="p-3 font-semibold">Section Head</th>
                  <th className="p-3 font-semibold text-center">Employees</th>
                  <th className="p-3 font-semibold text-center">Teams</th>
                  <th className="p-3 font-semibold text-center">Projects</th>
                  <th className="p-3 font-semibold">Status</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((section) => (
                  <tr key={section.id} className="border-t hover:bg-gray-50">
                    <td className="p-3">
                      <Link href={`/eom/sections/${section.id}`} className="font-medium text-primary-600 underline">
                        {section.code}
                      </Link>
                    </td>
                    <td className="p-3">
                      <Link href={`/eom/sections/${section.id}`} className="font-medium">
                        {section.name}
                      </Link>
                    </td>
                    <td className="p-3 text-text-secondary">{section.department || '—'}</td>
                    <td className="p-3 text-text-secondary">{section.section_head || '—'}</td>
                    <td className="p-3 text-center">{section.employee_count ?? '—'}</td>
                    <td className="p-3 text-center">{section.team_count ?? '—'}</td>
                    <td className="p-3 text-center">{section.project_count ?? '—'}</td>
                    <td className="p-3">
                      <span className={`inline-block rounded px-2 py-0.5 text-xs font-medium ${
                        section.status === 'active' ? 'bg-green-100 text-green-800' :
                        section.status === 'inactive' ? 'bg-gray-100 text-gray-600' :
                        'bg-yellow-100 text-yellow-800'
                      }`}>
                        {section.status}
                      </span>
                    </td>
                  </tr>
                ))}
                {filtered.length === 0 && (
                  <tr>
                    <td colSpan={8} className="p-6 text-center text-sm text-text-secondary">No sections found.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </AppShell>
  );
}