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
        const [entRes, brandRes] = await Promise.all([fetch('/eom/enterprises'), fetch('/eom/brands')]);
        if (!entRes.ok) return;
        const entBody = await entRes.json();
        const entList = Array.isArray(entBody) ? entBody : (entBody.items || []);
        let brandList: any[] = [];
        if (brandRes && brandRes.ok) {
          const b = await brandRes.json();
          brandList = Array.isArray(b) ? b : (b.items || []);
        }
        // Build a lightweight dashboard shape expected by EOMDashboard
        const data = {
          summary: {
            enterprises: Array.isArray(entList) ? entList.length : 0,
            branches: 0,
            departments: 0,
            employees: 0,
            brands: Array.isArray(brandList) ? brandList.length : 0,
          },
          recent_enterprises: (entList || []).map((e: any) => ({
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
