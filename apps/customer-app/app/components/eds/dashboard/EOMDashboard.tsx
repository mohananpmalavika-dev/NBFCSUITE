"use client";

import React from 'react';
import { DashboardLayout } from './DashboardLayout';
import { KPIWidget } from './KPIWidget';

export default function EOMDashboard({ data }: { data?: any }) {
  const kpis = [
    { label: 'Enterprises', value: data?.summary?.enterprises ?? 0 },
    { label: 'Branches', value: data?.summary?.branches ?? 0 },
    { label: 'Departments', value: data?.summary?.departments ?? 0 },
    { label: 'Employees', value: data?.summary?.employees ?? 0 },
  ];

  return (
    <DashboardLayout title="EOM Dashboard" persona="executive">
      <div className="space-y-4">
        <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
          {kpis.map((k) => (
            <KPIWidget key={k.label} title={k.label} value={String(k.value)} trend="up" change="" />
          ))}
        </div>
        <div>
          <h3 className="text-lg font-semibold">Recent Enterprises</h3>
          <div className="mt-3 space-y-2">
            {(data?.recent_enterprises || []).map((ent: any) => (
              <div key={ent.id} className="rounded-md border p-3">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-semibold">{ent.enterprise_name}</div>
                    <div className="text-sm text-text-secondary">{ent.enterprise_code}</div>
                  </div>
                  <div className="text-sm text-text-secondary">{ent.status}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
