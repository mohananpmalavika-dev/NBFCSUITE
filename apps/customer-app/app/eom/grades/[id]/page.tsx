
"use client";

import { useEffect, useMemo, useState } from 'react';
import { AppShell } from '../../../components/AppShell';
import { eomApiUrl } from '../../eomApi';

function TabButton({ active, label, onClick }: { active: boolean; label: string; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className={
        active
          ? 'px-3 py-2 rounded bg-blue-600 text-white text-sm'
          : 'px-3 py-2 rounded hover:bg-gray-100 text-sm'
      }
    >
      {label}
    </button>
  );
}

export default function GradeProfilePage({ params }: { params: { id: string } }) {
  const gradeId = params.id;

  const [grade, setGrade] = useState<any>(null);
  const [activeTab, setActiveTab] = useState<string>('overview');
  const [health, setHealth] = useState<any>(null);


  const tabs = useMemo(
    () => [
      { key: 'overview', label: 'Overview' },
      { key: 'salary', label: 'Salary' },
      { key: 'benefits', label: 'Benefits' },
      { key: 'competencies', label: 'Competencies' },
      { key: 'career', label: 'Career Path' },
      { key: 'training', label: 'Training' },
      { key: 'approvals', label: 'Approvals' },
      { key: 'documents', label: 'Documents' },
      { key: 'timeline', label: 'Timeline' },
      { key: 'audit', label: 'Audit' },
      { key: 'ai', label: 'AI' },
      { key: 'leave', label: 'Leave' },
    ],
    []
  );

  useEffect(() => {
    async function load() {
      const [gRes, hRes] = await Promise.all([
        fetch(eomApiUrl(`/eom/grades/${gradeId}`)),
        fetch(eomApiUrl(`/eom/grades/${gradeId}/health`)),
      ]);
      if (gRes.ok) setGrade(await gRes.json());
      if (hRes.ok) setHealth(await hRes.json());
    }
    load();
  }, [gradeId]);

  const content = (() => {
    if (!grade) return <div className="p-4 text-gray-500">Loading...</div>;

    if (activeTab === 'overview') {
      return (
        <div className="p-4">
          <div className="grid md:grid-cols-3 gap-4">
            <div className="border rounded p-4">
              <div className="text-sm text-gray-600">Grade</div>
              <div className="text-lg font-semibold">{grade.code}</div>
              <div className="text-sm text-gray-700">{grade.name}</div>
            </div>
            <div className="border rounded p-4">
              <div className="text-sm text-gray-600">Level</div>
              <div className="text-lg font-semibold">{grade.level ?? '-'}</div>
              <div className="text-sm text-gray-700">Category: {grade.category ?? '-'}</div>
            </div>
            <div className="border rounded p-4">
              <div className="text-sm text-gray-600">Grade Health</div>
              <div className="text-lg font-semibold">{health?.score ?? 0}%</div>
              <div className="text-sm text-gray-700">{health?.rating ?? ''}</div>
            </div>
          </div>

          <div className="mt-4 border rounded p-4">
            <div className="text-sm text-gray-600">Description</div>
            <div className="text-sm text-gray-800 mt-1">{grade.description ?? '-'}</div>
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

    return (
      <div className="p-4">
        <div className="text-sm text-gray-600">{tabs.find((t) => t.key === activeTab)?.label}</div>
        <div className="text-sm text-gray-500 mt-1">Tab page scaffold. Full data rendering is wired per endpoints in subsequent iterations.</div>
      </div>
    );
  })();

  return (
    <AppShell>
      <div className="p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-semibold">Grade Profile</h1>
            <p className="text-sm text-gray-600">360 view for grade {grade?.code ?? gradeId}</p>
          </div>
        </div>

        <div className="flex flex-wrap gap-2 mb-4">
          {tabs.map((t) => (
            <TabButton key={t.key} active={t.key === activeTab} label={t.label} onClick={() => setActiveTab(t.key)} />
          ))}
        </div>

        <div className="border rounded bg-white">{content}</div>
      </div>
    </AppShell>
  );
}

