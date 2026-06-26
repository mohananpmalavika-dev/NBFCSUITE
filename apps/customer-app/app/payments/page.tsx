'use client';

import { useAuth } from '@/lib/auth-context';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api';

interface Payment {
  id: string;
  transactionDate: string;
  paymentMode: string;
  amount: number;
  principalPaid: number;
  interestPaid: number;
  reference: string;
  status: string;
}

export default function PaymentsPage() {
  const { user, token, isLoading } = useAuth();
  const router = useRouter();
  const [payments, setPayments] = useState<Payment[]>([]);
  const [loanId, setLoanId] = useState('');
  const [paymentAmount, setPaymentAmount] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!isLoading && !token) {
      router.push('/login');
    }
  }, [token, isLoading, router]);

  useEffect(() => {
    if (loanId) {
      loadPayments();
    }
  }, [loanId]);

  const loadPayments = async () => {
    try {
      // In real implementation, fetch actual payments
      const mockPayments: Payment[] = [
        {
          id: '1',
          transactionDate: '2026-06-20',
          paymentMode: 'UPI',
          amount: 12500,
          principalPaid: 10000,
          interestPaid: 2500,
          reference: 'UPI123456',
          status: 'completed',
        },
        {
          id: '2',
          transactionDate: '2026-05-20',
          paymentMode: 'NEFT',
          amount: 12500,
          principalPaid: 10000,
          interestPaid: 2500,
          reference: 'NEFT789012',
          status: 'completed',
        },
      ];
      setPayments(mockPayments);
    } catch (err) {
      setError('Failed to load payments');
    }
  };

  const handleMakePayment = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError('');

    try {
      if (!loanId || !paymentAmount) {
        setError('Please select loan and enter amount');
        return;
      }

      // In real implementation, call payment API
      const newPayment: Payment = {
        id: Date.now().toString(),
        transactionDate: new Date().toISOString().split('T')[0],
        paymentMode: 'UPI',
        amount: parseFloat(paymentAmount),
        principalPaid: parseFloat(paymentAmount) * 0.8,
        interestPaid: parseFloat(paymentAmount) * 0.2,
        reference: `TXN${Date.now()}`,
        status: 'pending',
      };

      setPayments([newPayment, ...payments]);
      setPaymentAmount('');
      alert('Payment initiated successfully');
    } catch (err) {
      setError('Payment failed. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  if (isLoading) {
    return <div className="p-8 text-center">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900">Payments</h1>
          <p className="text-gray-600 mt-2">Manage your loan payments and view history</p>
        </div>

        {/* Make Payment Card */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Make a Payment</h2>
          <form onSubmit={handleMakePayment} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Select Loan</label>
                <select
                  value={loanId}
                  onChange={(e) => setLoanId(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Choose a loan...</option>
                  <option value="LOAN001">Personal Loan - ₹5,00,000</option>
                  <option value="LOAN002">Home Loan - ₹20,00,000</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Amount (₹)</label>
                <input
                  type="number"
                  value={paymentAmount}
                  onChange={(e) => setPaymentAmount(e.target.value)}
                  placeholder="Enter amount"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
            {error && <div className="text-red-600 text-sm">{error}</div>}
            <button
              type="submit"
              disabled={submitting}
              className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {submitting ? 'Processing...' : 'Make Payment'}
            </button>
          </form>
        </div>

        {/* Payment History */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Payment History</h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b-2 border-gray-300">
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Date</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Mode</th>
                  <th className="text-right py-3 px-4 font-semibold text-gray-700">Amount</th>
                  <th className="text-right py-3 px-4 font-semibold text-gray-700">Principal</th>
                  <th className="text-right py-3 px-4 font-semibold text-gray-700">Interest</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Reference</th>
                  <th className="text-center py-3 px-4 font-semibold text-gray-700">Status</th>
                </tr>
              </thead>
              <tbody>
                {payments.map((payment) => (
                  <tr key={payment.id} className="border-b border-gray-200 hover:bg-gray-50">
                    <td className="py-3 px-4 text-gray-900">{payment.transactionDate}</td>
                    <td className="py-3 px-4 text-gray-700">{payment.paymentMode}</td>
                    <td className="py-3 px-4 text-right font-semibold text-gray-900">₹{payment.amount.toLocaleString()}</td>
                    <td className="py-3 px-4 text-right text-gray-700">₹{payment.principalPaid.toLocaleString()}</td>
                    <td className="py-3 px-4 text-right text-gray-700">₹{payment.interestPaid.toLocaleString()}</td>
                    <td className="py-3 px-4 text-gray-700">{payment.reference}</td>
                    <td className="py-3 px-4 text-center">
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-semibold ${
                          payment.status === 'completed'
                            ? 'bg-green-100 text-green-800'
                            : 'bg-yellow-100 text-yellow-800'
                        }`}
                      >
                        {payment.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
