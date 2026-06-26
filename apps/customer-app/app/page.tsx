'use client';

import { useAuth } from '@/lib/auth-context';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

const dashboardCards = [
  { title: 'Loans', value: 'Applications and accounts', href: '/loans' },
  { title: 'Payments', value: 'EMI history and collection', href: '/payments' },
  { title: 'Documents', value: 'KYC and expiry tracking', href: '/documents' },
  { title: 'Profile', value: 'Customer 360 and risk', href: '/profile' },
  { title: 'Apply Loan', value: 'New loan request', href: '/apply-loan' },
  { title: 'Settings', value: 'Preferences and security', href: '/settings' },
];

export default function Home() {
  const { user, token, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !token) {
      router.push('/login');
    }
  }, [token, isLoading, router]);

  if (isLoading || !token) {
    return <div className="p-8 text-center">Loading...</div>;
  }

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-8">
      <div className="mx-auto max-w-6xl">
        <section className="mb-8 rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
          <p className="text-sm font-semibold uppercase tracking-wide text-blue-700">Customer Portal</p>
          <h1 className="mt-2 text-3xl font-bold text-slate-950">NBFCSUITE</h1>
          <p className="mt-2 max-w-2xl text-slate-600">
            Welcome, {user?.username}. Manage loans, payments, customer profile, and documents from one workspace.
          </p>
        </section>

        <section className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
          {dashboardCards.map((card) => (
            <Link
              key={card.href}
              href={card.href}
              className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm transition hover:border-blue-300 hover:shadow-md"
            >
              <h2 className="text-lg font-semibold text-slate-950">{card.title}</h2>
              <p className="mt-2 text-sm text-slate-600">{card.value}</p>
              <p className="mt-4 text-sm font-medium text-blue-700">Open</p>
            </Link>
          ))}
        </section>
      </div>
    </main>
  );
}
