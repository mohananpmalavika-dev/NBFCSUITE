"use client";

import { AppShell } from './components/AppShell';
import { useEffect, useState } from 'react';
import { eomApiUrl } from './eom/eomApi';
import EOMDashboard from './components/eds/dashboard/EOMDashboard';

export default function Home() {
  const [eomData, setEomData] = useState<any>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        const [dashboardRes, hierarchyRes] = await Promise.all([
          fetch(eomApiUrl('/eom/dashboard')),
          fetch(eomApiUrl('/eom/hierarchy')),
        ]);
        if (dashboardRes.ok) {
          const dashboard = await dashboardRes.json();
          const hierarchy = hierarchyRes.ok ? await hierarchyRes.json() : { items: [] };
          setEomData({ ...dashboard, hierarchy });
        }
      } catch (e) {
        // ignore fetch errors in demo shell
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
