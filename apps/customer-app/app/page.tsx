"use client";

import { AppShell } from './components/AppShell';
import dynamic from 'next/dynamic';
import { useEffect, useState } from 'react';

const EOMDashboard = dynamic(() => import('./components/eds/dashboard/EOMDashboard'), { ssr: false });

export default function Home() {
  const [eomData, setEomData] = useState<any>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        const res = await fetch('/eom/dashboard');
        if (res.ok) {
          setEomData(await res.json());
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
