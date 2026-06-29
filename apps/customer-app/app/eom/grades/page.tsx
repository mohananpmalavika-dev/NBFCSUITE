"use client";

import { useEffect, useState } from 'react';
import { AppShell } from '../../components/AppShell';
import { eomApiUrl } from '../eomApi';


export default function GradesPage() {
  const [rows, setRows] = useState<any[]>([]);
  const [total, setTotal] = useState<number>(0);

  useEffect(() => {
    async function run() {
      const res = await fetch(eomApiUrl('/eom/grades'));
      if (!res.ok) return;
      const json = await res.json();
      setRows(json.items ?? []);
      setTotal(json.total ?? 0);
    }
    run();
  }, []);

  return (
    <AppShell>
      <div className="p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-semibold">Grade Directory</h1>
            <p className="text-sm text-gray-600">{total} grades</p>
          </div>
          <a
            className="px-4 py-2 rounded bg-blue-600 text-white hover:bg-blue-700"
            href="/eom/grades/new"
          >
            Create Grade
          </a>
        </div>

        <div className="border rounded overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-left">
              <tr>
                <th className="p-3">Code</th>
                <th className="p-3">Name</th>
                <th className="p-3">Level</th>
                <th className="p-3">Category</th>
                <th className="p-3">Status</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.id} className="border-t hover:bg-gray-50">
                  <td className="p-3">
                    <a className="text-blue-700 hover:underline" href={`/eom/grades/${r.id}`}>{r.code}</a>
                  </td>
                  <td className="p-3">{r.name}</td>
                  <td className="p-3">{r.level}</td>
                  <td className="p-3">{r.category}</td>
                  <td className="p-3">{r.status}</td>
                </tr>
              ))}
              {!rows.length ? (
                <tr>
                  <td colSpan={5} className="p-6 text-gray-500">No grades found.</td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </div>
      </div>
    </AppShell>
  );
}

