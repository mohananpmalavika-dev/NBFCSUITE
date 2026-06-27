'use client';

import { useAuth } from '@/lib/auth-context';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

const dashboardCards = [
  { title: '🆔 CIF Onboarding', value: '18-stage customer onboarding process', href: '/cif-onboarding', featured: true },
  { title: 'Loans', value: 'Applications and accounts', href: '/loans' },
  { title: 'Deposits', value: 'Savings, FD/RD and statements', href: '/deposits' },
  { title: 'Payments', value: 'EMI history and collection', href: '/payments' },
  { title: 'Accounting', value: 'Ledger and trial balance reporting', href: '/accounting' },
  { title: 'Branch Portal', value: 'CIF, underwriting and disbursement queue', href: '/branch' },
  { title: 'EOM Master Data', value: 'Enterprise organization and branch mapping', href: '/eom' },
  { title: 'HRMS', value: 'Employee master, branch assignments and payroll', href: '/hrms' },
  { title: 'Documents', value: 'KYC and expiry tracking', href: '/documents' },
  { title: 'Profile', value: 'Customer 360 and risk', href: '/profile' },
  { title: 'Customer 360', value: 'Complete customer view with all products', href: '/customer-360', featured: true },
  { title: 'Executive', value: 'Portfolio and AI risk summary', href: '/executive' },
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
          {dashboardCards.map((card: any) => (
            <Link
              key={card.href}
              href={card.href}
              className={`rounded-lg border p-5 shadow-sm transition ${
                card.featured
                  ? 'border-blue-400 bg-gradient-to-br from-blue-50 to-blue-100 hover:border-blue-500 hover:shadow-md'
                  : 'border-slate-200 bg-white hover:border-blue-300 hover:shadow-md'
              }`}
            >
              <h2 className={`text-lg font-semibold ${card.featured ? 'text-blue-900' : 'text-slate-950'}`}>
                {card.title}
              </h2>
              <p className={`mt-2 text-sm ${card.featured ? 'text-blue-800' : 'text-slate-600'}`}>
                {card.value}
              </p>
              <p className="mt-4 text-sm font-medium text-blue-700">Open →</p>
            </Link>
          ))}
        </section>
      </div>
    </main>
  );
}
