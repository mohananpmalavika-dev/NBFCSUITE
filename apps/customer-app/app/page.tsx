'use client';

import { useAuth } from '@/lib/auth-context';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export default function Home() {
  const { user, token } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!token) {
      router.push('/login');
    }
  }, [token, router]);

  if (!token) {
    return null;
  }

  return (
    <div style={{ padding: '2rem' }}>
      <h1>NBFCSUITE Customer Portal</h1>
      <p>Welcome, {user?.username}!</p>

      <div style={{ marginTop: '2rem' }}>
        <h2>Your Dashboard</h2>
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(3, 1fr)',
            gap: '1rem',
          }}
        >
          <Card title="Loans" count="2" href="/loans" />
          <Card title="EMI Payments" count="24" href="/payments" />
          <Card title="Documents" count="5" href="/documents" />
          <Card title="KYC Status" count="Approved" href="/kyc" />
          <Card title="Credit Score" count="750" href="/score" />
          <Card title="Settings" count="—" href="/settings" />
        </div>
      </div>

      <div style={{ marginTop: '3rem' }}>
        <h3>Quick Actions</h3>
        <button
          onClick={() => router.push('/apply-loan')}
          style={{
            padding: '0.5rem 1rem',
            marginRight: '0.5rem',
            cursor: 'pointer',
          }}
        >
          Apply for Loan
        </button>
        <button
          onClick={() => router.push('/payment')}
          style={{
            padding: '0.5rem 1rem',
            marginRight: '0.5rem',
            cursor: 'pointer',
          }}
        >
          Make Payment
        </button>
      </div>
    </div>
  );
}

function Card({
  title,
  count,
  href,
}: {
  title: string;
  count: string;
  href: string;
}) {
  return (
    <div
      style={{
        border: '1px solid #ccc',
        padding: '1rem',
        borderRadius: '0.5rem',
        cursor: 'pointer',
      }}
    >
      <h3>{title}</h3>
      <p style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{count}</p>
      <a href={href} style={{ color: '#0070f3', textDecoration: 'none' }}>
        View →
      </a>
    </div>
  );
}
