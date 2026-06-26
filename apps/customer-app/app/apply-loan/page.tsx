'use client';

import { apiClient } from '@/lib/api';
import { useAuth } from '@/lib/auth-context';
import { useRouter } from 'next/navigation';
import { ChangeEvent, FormEvent, useEffect, useMemo, useState } from 'react';

interface LoanProduct {
  product_code: string;
  product_name: string;
  min_amount: number;
  max_amount: number;
  min_tenor: number;
  max_tenor: number;
  base_rate: number;
}

export default function ApplyLoanPage() {
  const { user, token, isLoading } = useAuth();
  const router = useRouter();
  const [products, setProducts] = useState<LoanProduct[]>([]);
  const [formData, setFormData] = useState({
    productCode: '',
    appliedAmount: '',
    tenureMonths: '',
  });
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    if (!isLoading && !token) {
      router.push('/login');
    }
  }, [token, isLoading, router]);

  useEffect(() => {
    const loadProducts = async () => {
      if (!token) {
        return;
      }
      try {
        const response = await apiClient.getLoanProducts();
        const productList = response.data as LoanProduct[];
        setProducts(productList);
        if (productList.length > 0) {
          setFormData({
            productCode: productList[0].product_code,
            appliedAmount: String(productList[0].min_amount),
            tenureMonths: String(productList[0].min_tenor),
          });
        }
      } catch {
        setMessage('Could not load loan products.');
      }
    };

    loadProducts();
  }, [token]);

  const selectedProduct = useMemo(
    () => products.find((product) => product.product_code === formData.productCode),
    [products, formData.productCode],
  );

  const loanAmount = Number(formData.appliedAmount) || 0;
  const tenure = Number(formData.tenureMonths) || selectedProduct?.min_tenor || 0;
  const rate = selectedProduct?.base_rate || 0;
  const monthlyRate = rate / 100 / 12;
  const emi =
    loanAmount > 0 && tenure > 0
      ? (loanAmount * monthlyRate * Math.pow(1 + monthlyRate, tenure)) /
        (Math.pow(1 + monthlyRate, tenure) - 1)
      : 0;
  const totalAmount = emi * tenure;
  const totalInterest = totalAmount - loanAmount;

  const handleChange = (event: ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = event.target;
    if (name === 'productCode') {
      const product = products.find((item) => item.product_code === value);
      setFormData({
        productCode: value,
        appliedAmount: product ? String(product.min_amount) : '',
        tenureMonths: product ? String(product.min_tenor) : '',
      });
      return;
    }
    setFormData((previous) => ({ ...previous, [name]: value }));
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!user || !selectedProduct) {
      return;
    }

    setSubmitting(true);
    setMessage('');
    try {
      if (loanAmount < selectedProduct.min_amount || loanAmount > selectedProduct.max_amount) {
        setMessage('Amount is outside the selected product limits.');
        return;
      }
      if (tenure < selectedProduct.min_tenor || tenure > selectedProduct.max_tenor) {
        setMessage('Tenure is outside the selected product limits.');
        return;
      }

      await apiClient.applyForLoan({
        customer_id: user.id,
        product_code: selectedProduct.product_code,
        applied_amount: loanAmount,
        tenure_months: tenure,
      });
      router.push('/loans');
    } catch {
      setMessage('Failed to submit application.');
    } finally {
      setSubmitting(false);
    }
  };

  if (isLoading) {
    return <div className="p-8 text-center">Loading...</div>;
  }

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-8">
      <div className="mx-auto max-w-3xl">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-slate-950">Apply for a Loan</h1>
          <p className="mt-1 text-slate-600">Choose a product and submit a draft LOS application.</p>
        </div>

        {message && (
          <div className="mb-4 rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
            {message}
          </div>
        )}

        <form onSubmit={handleSubmit} className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
          <div className="space-y-5">
            <label className="block">
              <span className="mb-1 block text-sm font-medium text-slate-700">Loan type</span>
              <select
                name="productCode"
                value={formData.productCode}
                onChange={handleChange}
                className="w-full rounded-md border border-slate-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
              >
                {products.map((product) => (
                  <option key={product.product_code} value={product.product_code}>
                    {product.product_name} @ {product.base_rate}% p.a.
                  </option>
                ))}
              </select>
            </label>

            <label className="block">
              <span className="mb-1 block text-sm font-medium text-slate-700">Loan amount (INR)</span>
              <input
                type="number"
                name="appliedAmount"
                value={formData.appliedAmount}
                onChange={handleChange}
                min={selectedProduct?.min_amount}
                max={selectedProduct?.max_amount}
                className="w-full rounded-md border border-slate-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
              />
              {selectedProduct && (
                <p className="mt-1 text-xs text-slate-500">
                  Range: INR {selectedProduct.min_amount.toLocaleString()} - INR {selectedProduct.max_amount.toLocaleString()}
                </p>
              )}
            </label>

            <label className="block">
              <span className="mb-1 block text-sm font-medium text-slate-700">Tenure (months)</span>
              <input
                type="number"
                name="tenureMonths"
                value={formData.tenureMonths}
                onChange={handleChange}
                min={selectedProduct?.min_tenor}
                max={selectedProduct?.max_tenor}
                className="w-full rounded-md border border-slate-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
              />
              {selectedProduct && (
                <p className="mt-1 text-xs text-slate-500">
                  Range: {selectedProduct.min_tenor} - {selectedProduct.max_tenor} months
                </p>
              )}
            </label>

            {loanAmount > 0 && tenure > 0 && (
              <section className="rounded-lg border border-blue-200 bg-blue-50 p-4">
                <h2 className="mb-3 font-semibold text-slate-950">Estimated repayment</h2>
                <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
                  <Metric label="Monthly EMI" value={`INR ${Math.round(emi).toLocaleString()}`} />
                  <Metric label="Total interest" value={`INR ${Math.round(totalInterest).toLocaleString()}`} />
                  <Metric label="Total payable" value={`INR ${Math.round(totalAmount).toLocaleString()}`} />
                </div>
              </section>
            )}

            <div className="flex flex-col gap-3 border-t border-slate-200 pt-5 sm:flex-row">
              <button
                type="submit"
                disabled={submitting || products.length === 0}
                className="rounded-md bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {submitting ? 'Submitting...' : 'Submit Application'}
              </button>
              <button
                type="button"
                onClick={() => router.back()}
                className="rounded-md border border-slate-300 px-4 py-2 font-medium text-slate-700 hover:bg-slate-50"
              >
                Cancel
              </button>
            </div>
          </div>
        </form>
      </div>
    </main>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs font-medium text-slate-500">{label}</p>
      <p className="mt-1 text-lg font-semibold text-slate-950">{value}</p>
    </div>
  );
}
