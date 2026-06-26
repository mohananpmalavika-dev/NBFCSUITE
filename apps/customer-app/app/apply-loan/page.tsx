'use client';

import { useAuth } from '@/lib/auth-context';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

export default function ApplyLoanPage() {
  const { user, token, isLoading } = useAuth();
  const router = useRouter();
  const [formData, setFormData] = useState({
    productCode: 'PERSONAL_LOAN',
    appliedAmount: '',
    tenureMonths: '60',
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!isLoading && !token) {
      router.push('/login');
    }
  }, [token, isLoading, router]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError('');

    try {
      // Validate form
      if (!formData.appliedAmount || parseInt(formData.appliedAmount) <= 0) {
        setError('Please enter a valid amount');
        setSubmitting(false);
        return;
      }

      // In real implementation, call API
      alert('Loan application submitted successfully');
      router.push('/loans');
    } catch (err) {
      setError('Failed to submit application');
    } finally {
      setSubmitting(false);
    }
  };

  if (isLoading) {
    return <div className="p-8 text-center">Loading...</div>;
  }

  const products = [
    { code: 'PERSONAL_LOAN', name: 'Personal Loan', minAmount: 50000, maxAmount: 2000000, rate: 9.0 },
    { code: 'HOME_LOAN', name: 'Home Loan', minAmount: 1000000, maxAmount: 5000000, rate: 7.5 },
    { code: 'AUTO_LOAN', name: 'Auto Loan', minAmount: 300000, maxAmount: 1500000, rate: 8.5 },
    { code: 'GOLD_LOAN', name: 'Gold Loan', minAmount: 50000, maxAmount: 500000, rate: 12.0 },
  ];

  const selectedProduct = products.find((p) => p.code === formData.productCode);
  const loanAmount = parseInt(formData.appliedAmount) || 0;
  const tenure = parseInt(formData.tenureMonths) || 60;
  const rate = selectedProduct?.rate || 0;
  const monthlyRate = rate / 100 / 12;
  const emi =
    loanAmount > 0
      ? (loanAmount * monthlyRate * Math.pow(1 + monthlyRate, tenure)) /
        (Math.pow(1 + monthlyRate, tenure) - 1)
      : 0;
  const totalAmount = emi * tenure;
  const totalInterest = totalAmount - loanAmount;

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900">Apply for a Loan</h1>
          <p className="text-gray-600 mt-2">Fill in your details and apply instantly</p>
        </div>

        {/* Form */}
        <div className="bg-white rounded-lg shadow-md p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Product Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Loan Type</label>
              <select
                name="productCode"
                value={formData.productCode}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {products.map((product) => (
                  <option key={product.code} value={product.code}>
                    {product.name} @ {product.rate}% p.a.
                  </option>
                ))}
              </select>
            </div>

            {/* Loan Amount */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Loan Amount (₹)</label>
              <input
                type="number"
                name="appliedAmount"
                value={formData.appliedAmount}
                onChange={handleChange}
                min={selectedProduct?.minAmount || 0}
                max={selectedProduct?.maxAmount || 10000000}
                placeholder={`₹ ${selectedProduct?.minAmount?.toLocaleString()} - ₹ ${selectedProduct?.maxAmount?.toLocaleString()}`}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <p className="text-xs text-gray-500 mt-1">
                Range: ₹ {selectedProduct?.minAmount?.toLocaleString()} - ₹ {selectedProduct?.maxAmount?.toLocaleString()}
              </p>
            </div>

            {/* Tenure */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Loan Tenure (months)</label>
              <select
                name="tenureMonths"
                value={formData.tenureMonths}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {[12, 24, 36, 48, 60, 84].map((months) => (
                  <option key={months} value={months}>
                    {months} months ({Math.round(months / 12)} years)
                  </option>
                ))}
              </select>
            </div>

            {/* EMI Calculator Result */}
            {loanAmount > 0 && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 className="font-semibold text-gray-900 mb-3">Estimated EMI</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-600">Monthly EMI</p>
                    <p className="text-2xl font-bold text-blue-600">₹ {emi.toFixed(0).toLocaleString()}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Total Interest</p>
                    <p className="text-2xl font-bold text-gray-900">₹ {totalInterest.toFixed(0).toLocaleString()}</p>
                  </div>
                  <div className="col-span-2">
                    <p className="text-sm text-gray-600">Total Amount to Pay</p>
                    <p className="text-2xl font-bold text-gray-900">₹ {totalAmount.toFixed(0).toLocaleString()}</p>
                  </div>
                </div>
              </div>
            )}

            {error && <div className="text-red-600 text-sm bg-red-50 p-3 rounded-lg">{error}</div>}

            {/* Buttons */}
            <div className="flex space-x-4">
              <button
                type="submit"
                disabled={submitting}
                className="flex-1 bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 font-semibold"
              >
                {submitting ? 'Processing...' : 'Apply Now'}
              </button>
              <button
                type="button"
                onClick={() => router.back()}
                className="flex-1 bg-gray-300 text-gray-900 py-3 rounded-lg hover:bg-gray-400 font-semibold"
              >
                Cancel
              </button>
            </div>

            {/* Disclaimer */}
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <p className="text-xs text-gray-600">
                <strong>Disclaimer:</strong> This is an estimated EMI calculation. Actual EMI may vary based on your credit score,
                income verification, and other factors. Please review the loan agreement carefully before signing.
              </p>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
