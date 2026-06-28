"use client";

import { useEffect, useState } from 'react';
import { AppShell } from '../components/AppShell';
import { eomApiUrl } from './eomApi';
import EOMDashboard from '../components/eds/dashboard/EOMDashboard';

export default function EOMPage() {
  const [eomData, setEomData] = useState<any>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        const [dashboardRes, hierarchyRes] = await Promise.all([
          fetch(eomApiUrl('/eom/dashboard')),
          fetch(eomApiUrl('/eom/hierarchy')),
        ]);
        if (!dashboardRes.ok) return;
        const dashboard = await dashboardRes.json();
        const hierarchy = hierarchyRes.ok ? await hierarchyRes.json() : { items: [] };
        setEomData({ ...dashboard, hierarchy });
      } catch (e) {
        // ignore
      }
    }
    fetchData();
  }, []);

  return (
    <AppShell>
      <EOMDashboard data={eomData} />
    </AppShell>
  );
}
