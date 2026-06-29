"use client";

import React, { useEffect, useMemo, useState } from 'react';
import { AppShell } from '../../../components/AppShell';
import { getDesignation, getDesignationHealth, getDesignationCompetencies, getDesignationCareer } from './components/designationApi';
import { DesignationTabs, DesignationTabKey } from './components/DesignationTabs';

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

export default function DesignationProfilePage({ params }: { params: { id: string } }) {
  const designationId = params.id;

  const [designation, setDesignation] = useState<any>(null);
  const [health, setHealth] = useState<any>(null);
  const [competencies, setCompetencies] = useState<any[]>([]);
  const [career, setCareer] = useState<any>(null);
  const [activeTab, setActiveTab] = useState<DesignationTabKey>('overview');

  const tabs = useMemo(
    () =>
      [
        { key: 'overview' as const, label: 'Overview' },
        { key: 'responsibilities' as const, label: 'Responsibilities' },
        { key: 'competencies' as const, label: 'Competencies' },
        { key: 'grade-mapping' as const, label: 'Grade Mapping' },
        { key: 'career-path' as const, label: 'Career Path' },
        { key: 'kpis' as const, label: 'KPIs' },
        { key: 'approvals' as const, label: 'Approvals' },
        { key: 'recruitment' as const, label: 'Recruitment' },
        { key: 'training' as const, label: 'Training' },
        { key: 'documents' as const, label: 'Documents' },
        { key: 'timeline' as const, label: 'Timeline' },
        { key: 'audit' as const, label: 'Audit' },
        { key: 'ai' as const, label: 'AI' },
      ] as Array<{ key: DesignationTabKey; label: string }>,
    []
  );

  useEffect(() => {
    async function load() {
      const [dRes, hRes, cRes, crRes] = await Promise.all([
        getDesignation(designationId),
        getDesignationHealth(designationId),
        getDesignationCompetencies(designationId),
        getDesignationCareer(designationId),
      ]);
      setDesignation(dRes);
      setHealth(hRes);
      setCompetencies(cRes);
      setCareer(crRes);
    }

    load().catch(() => {
      setDesignation(null);
    });
  }, [designationId]);

  return (
    <AppShell>
      <div className="p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-semibold">Designation 360</h1>
            <p className="text-sm text-gray-600">360 view for {designation?.code ?? designationId}</p>
          </div>
        </div>

        <div className="flex flex-wrap gap-2 mb-4">
          {tabs.map((t) => (
            <TabButton key={t.key} active={t.key === activeTab} label={t.label} onClick={() => setActiveTab(t.key)} />
          ))}
        </div>

        <div className="border rounded bg-white">
          {!designation ? (
            <div className="p-4 text-gray-500">Loading...</div>
          ) : (
            <DesignationTabs
              activeTab={activeTab}
              designation={designation}
              health={health}
              competencies={competencies}
              career={career}
            />
          )}
        </div>
      </div>
    </AppShell>
  );
}

