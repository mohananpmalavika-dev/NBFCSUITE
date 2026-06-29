"use client";

import React from 'react';

export function OverviewTab({ designation, health }: { designation: any; health: any }) {
  return (
    <div className="p-4">
      <div className="grid md:grid-cols-3 gap-4">
        <div className="border rounded p-4">
          <div className="text-sm text-gray-600">Designation</div>
          <div className="text-lg font-semibold">{designation?.code ?? '-'}</div>
          <div className="text-sm text-gray-700">{designation?.name ?? '-'}</div>
        </div>
        <div className="border rounded p-4">
          <div className="text-sm text-gray-600">Status</div>
          <div className="text-lg font-semibold">{designation?.status ?? '-'}</div>
        </div>
        <div className="border rounded p-4">
          <div className="text-sm text-gray-600">Designation Health</div>
          <div className="text-lg font-semibold">{health?.score ?? 0}%</div>
          <div className="text-sm text-gray-700">{health?.rating ?? ''}</div>
        </div>
      </div>

      {health?.issues?.length ? (
        <div className="mt-4 border rounded p-4">
          <div className="text-sm font-semibold">Issues</div>
          <ul className="text-sm list-disc ml-5 text-gray-700">
            {health.issues.map((it: string) => (
              <li key={it}>{it}</li>
            ))}
          </ul>
        </div>
      ) : null}
    </div>
  );
}

export function CompetenciesTab({ competencies }: { competencies: any[] }) {
  return (
    <div className="p-4">
      <div className="text-sm text-gray-600">Competencies</div>
      <pre className="text-xs mt-2 bg-gray-50 border rounded p-3 overflow-auto">
        {JSON.stringify(competencies ?? [], null, 2)}
      </pre>
    </div>
  );
}

export function CareerPathTab({ career }: { career: any }) {
  return (
    <div className="p-4">
      <div className="text-sm text-gray-600">Career Path</div>
      <pre className="text-xs mt-2 bg-gray-50 border rounded p-3 overflow-auto">
        {JSON.stringify(career ?? {}, null, 2)}
      </pre>
    </div>
  );
}

export function PlaceholderTab({ title }: { title: string }) {
  return (
    <div className="p-4">
      <div className="text-sm text-gray-500">{title} tab scaffold.</div>
    </div>
  );
}

