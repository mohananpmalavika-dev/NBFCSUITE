"use client";

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { AppShell } from '../../components/AppShell';
import { eomApiUrl } from '../eomApi';

export default function PositionsPage() {
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const res = await fetch(eomApiUrl('/eom/positions'));
        if (!res.ok) return;
        const body = await res.json();
        const list = Array.isArray(body) ? body : body.items || [];
        if (mounted) setItems(list);
      } catch (e) {
      } finally {
        if (mounted) setLoading(false);
      }
    })();
    return () => { mounted = false; };
  }, []);

  return (
    <AppShell>
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold">Positions</h2>
            <p className="text-sm text-text-secondary">Manage role positions and vacancies across the organization.</p>
          </div>
          <Link href="/eom/positions/new" className="btn btn-primary">New Position</Link>
        </div>

        {loading ? (
          <div className="py-8 text-center text-sm text-text-secondary">Loading…</div>
        ) : (
          <div className="overflow-x-auto rounded-md border">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-50 text-left">
                  <th className="p-3 font-semibold">Code</th>
                  <th className="p-3 font-semibold">Title</th>
                  <th className="p-3 font-semibold">Grade</th>
                  <th className="p-3 font-semibold">Team</th>
                  <th className="p-3 font-semibold">Status</th>
                </tr>
              </thead>
              <tbody>
                {items.map((position) => (
                  <tr key={position.id} className="border-t hover:bg-gray-50">
                    <td className="p-3">
                      <Link href={`/eom/positions/${position.id}`} className="font-medium text-primary-600 underline">
                        {position.code}
                      </Link>
                    </td>
                    <td className="p-3">{position.title}</td>
                    <td className="p-3 text-text-secondary">{position.grade_id || '—'}</td>
                    <td className="p-3 text-text-secondary">{position.team_id || '—'}</td>
                    <td className="p-3">
                      <span className={`inline-block rounded px-2 py-0.5 text-xs font-medium ${
                        position.status === 'open' ? 'bg-green-100 text-green-800' :
                        position.status === 'filled' ? 'bg-blue-100 text-blue-800' :
                        'bg-gray-100 text-gray-700'
                      }`}>
                        {position.status}
                      </span>
                    </td>
                  </tr>
                ))}
                {items.length === 0 && (
                  <tr>
                    <td colSpan={5} className="p-6 text-center text-sm text-text-secondary">No positions found.</td>
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
