"use client";

import React from 'react';
import { OverviewTab, CompetenciesTab, CareerPathTab, PlaceholderTab } from './tabs';

export type DesignationTabKey =
  | 'overview'
  | 'responsibilities'
  | 'competencies'
  | 'grade-mapping'
  | 'career-path'
  | 'kpis'
  | 'approvals'
  | 'recruitment'
  | 'training'
  | 'documents'
  | 'timeline'
  | 'audit'
  | 'ai';

export function DesignationTabs({
  activeTab,
  designation,
  health,
  competencies,
  career,
}: {
  activeTab: DesignationTabKey;
  designation: any;
  health: any;
  competencies: any[];
  career: any;
}) {
  switch (activeTab) {
    case 'overview':
      return <OverviewTab designation={designation} health={health} />;
    case 'competencies':
      return <CompetenciesTab competencies={competencies} />;
    case 'career-path':
      return <CareerPathTab career={career} />;

    default:
      return <PlaceholderTab title={`Tab: ${activeTab}`} />;
  }
}

