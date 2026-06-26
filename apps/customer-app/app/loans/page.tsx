'use client';

import { useAuth } from '@/lib/auth-context';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export default function LoansPage() {
  const { token } = useAuth();
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
      <h1>My Loans</h1>
      <p>Your active and past loans will appear here.</p>

      <div
        style={{
          marginTop: '2rem',
          border: '1px solid #ccc',
          padding: '1rem',
          borderRadius: '0.5rem',
        }}
      >
        <h3>Active Loans</h3>
        <table
          style={{
            width: '100%',
            borderCollapse: 'collapse',
            marginTop: '1rem',
          }}
        >
          <thead>
            <tr style={{ borderBottom: '2px solid #0070f3' }}>
              <th style={{ textAlign: 'left', padding: '0.5rem' }}>
                Loan ID
              </th>
              <th style={{ textAlign: 'left', padding: '0.5rem' }}>Amount</th>
              <th style={{ textAlign: 'left', padding: '0.5rem' }}>Status</th>
              <th style={{ textAlign: 'left', padding: '0.5rem' }}>EMI</th>
              <th style={{ textAlign: 'left', padding: '0.5rem' }}>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr style={{ borderBottom: '1px solid #eee' }}>
              <td style={{ padding: '0.5rem' }}>LOAN-001</td>
              <td style={{ padding: '0.5rem' }}>₹5,00,000</td>
              <td style={{ padding: '0.5rem' }}>Active</td>
              <td style={{ padding: '0.5rem' }}>₹15,800</td>
              <td style={{ padding: '0.5rem' }}>
                <a href="/loans/LOAN-001">View</a>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
