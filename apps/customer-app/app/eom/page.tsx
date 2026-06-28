"use client";

import dynamic from 'next/dynamic';
import { useEffect, useState } from 'react';
import { AppShell } from '../components/AppShell';

const EOMDashboard = dynamic(() => import('../components/eds/dashboard/EOMDashboard'), { ssr: false });

export default function EOMPage() {
  const [eomData, setEomData] = useState<any>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        const res = await fetch('/eom/enterprises');
        if (!res.ok) return;
        const list = await res.json();
        // Build a lightweight dashboard shape expected by EOMDashboard
        const data = {
          summary: {
            enterprises: list.length,
            branches: 0,
            departments: 0,
            employees: 0,
          },
          recent_enterprises: list.map((e: any) => ({
            id: e.id,
            enterprise_name: e.name,
            enterprise_code: e.code,
            status: e.status,
          })),
        };
        setEomData(data);
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
