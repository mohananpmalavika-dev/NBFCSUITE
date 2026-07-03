/**
 * Open Recurring Deposit - Multi-step Form
 * RD opening with installment schedule preview
 */

'use client';

import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import { Clock, Calendar, CheckCircle, ArrowRight, ArrowLeft, TrendingUp, Users } from 'lucide-react';

interface RDFormData {
  customer_id: string;
  cif_number: string;
  product_id: string;
  installment_amount: number;
  num_installments: number;
  is_senior_citizen: boolean;
  branch_code: string;
  auto_debit: boolean;
  debit_account: string;
  nominees: Array<{
    name: string;
    relationship: string;
    date_of_birth: string;
    phone: string;
    allocation_percentage: number;
  }>;
}

export default function OpenRDPage() {
  const searchParams = useSearchParams();
  const productId = searchParams?.get('product');
  
  const [step, setStep] = useState(1);
  const [products, setProducts] = useState<any[]>([]);
  const [selectedProduct, setSelectedProduct] = useState<any>(null);
  const [maturityCalc, setMaturityCalc] = useState<any>(null);
  const [schedule, setSchedule] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  
  const [formData, setFormData] = useState<RDFormData>({
    customer_id: '',
    cif_number: '',
    product_id: productId || '',
    installment_amount: 5000,
    num_installments: 12,
    is_senior_citizen: false,
    branch_code: 'BR001',
    auto_debit: false,
    debit_account: '',
    nominees: [{
      name: '',
      relationship: 'SPOUSE',
      date_of_birth: '',
      phone: '',
      allocation_percentage: 100
    }]
  });

  useEffect(() => {
    fetchProducts();
  }, []);

  useEffect(() => {
    if (formData.product_id) {
      const product = products.find(p => p.id === formData.product_id);
      setSelectedProduct(product);
    }
  }, [formData.product_id, products]);

  useEffect(() => {
    if (selectedProduct && formData.installment_amount && formData.num_installments) {
      calculateMaturity();
    }
  }, [formData.installment_amount, formData.num_installments, formData.is_senior_citizen, selectedProduct]);

  const fetchProducts = async () => {
    try {
      const response = await fetch('http://localhost:8007/api/v1/products?deposit_type=RECURRING_DEPOSIT');
      const data = await response.json();
      setProducts(data);
      
      if (productId && data.length > 0) {
        const product = data.find((p: any) => p.id === productId);
        if (product) setSelectedProduct(product);
      }
    } catch (error) {
      console.error('Error fetching products:', error);
    }
  };

  const calculateMaturity = async () => {
    if (!selectedProduct) return;
    
    try {
      const response = await fetch('http://localhost:8007/api/v1/rd/calculate-maturity', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          installment_amount: formData.installment_amount,
          num_months: formData.num_installments,
          interest_rate: selectedProduct.default_interest_rate
        })
      });
      
      const data = await response.json();
      setMaturityCalc(data);
    } catch (error) {
      console.error('Error calculating:', error);
    }
  };

  const handleSubmit = async () => {
    setLoading(true);
    
    try {
      const response = await fetch('http://localhost:8007/api/v1/accounts/rd', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      
      if (response.ok) {
        alert(`Recurring Deposit opened successfully!\nAccount Number: ${data.account_number}`);
        window.location.href = `/deposits/accounts/${data.account_id}`;
      } else {
        alert(`Error: ${data.detail || 'Failed to open account'}`);
      }
    } catch (error) {
      console.error('Error submitting:', error);
      alert('Error opening account. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const renderStep = () => {
    switch(step) {
      case 1:
        return <StepProductSelection products={products} formData={formData} setFormData={setFormData} />;
      case 2:
        return <StepRDDetails formData={formData} setFormData={setFormData} selectedProduct={selectedProduct} maturityCalc={maturityCalc} />;
      case 3:
        return <StepCustomerInfo formData={formData} setFormData={setFormData} />;
      case 4:
        return <StepNominees formData={formData} setFormData={setFormData} />;
      case 5:
        return <StepReview formData={formData} selectedProduct={selectedProduct} maturityCalc={maturityCalc} />;
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-orange-50/30 p-8">
      <div className="max-w-4xl mx-auto">
        
        {/* Progress */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            {['Product', 'Details', 'Customer', 'Nominees', 'Review'].map((label, index) => (
              <div key={label} className="flex items-center">
                <div className={`flex items-center justify-center w-10 h-10 rounded-full font-bold ${
                  step > index + 1 ? 'bg-green-600 text-white' :
                  step === index + 1 ? 'bg-orange-600 text-white' :
                  'bg-slate-200 text-slate-600'
                }`}>
                  {step > index + 1 ? <CheckCircle className="w-5 h-5" /> : index + 1}
                </div>
                <p className={`ml-2 text-sm font-medium ${step >= index + 1 ? 'text-slate-900' : 'text-slate-500'}`}>
                  {label}
                </p>
                {index < 4 && (
                  <div className={`w-20 h-1 mx-4 ${step > index + 1 ? 'bg-green-600' : 'bg-slate-200'}`} />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Form */}
        <div className="bg-white rounded-xl shadow-lg border border-slate-200 p-8">
          {renderStep()}
          
          {/* Navigation */}
          <div className="flex justify-between mt-8 pt-6 border-t border-slate-200">
            {step > 1 ? (
              <button
                onClick={() => setStep(step - 1)}
                className="px-6 py-3 border border-slate-300 rounded-lg font-medium hover:bg-slate-50 transition-colors flex items-center gap-2"
              >
                <ArrowLeft className="w-4 h-4" />
                Previous
              </button>
            ) : <div />}
            
            {step < 5 ? (
              <button
                onClick={() => setStep(step + 1)}
                className="px-6 py-3 bg-orange-600 text-white rounded-lg font-medium hover:bg-orange-700 transition-colors flex items-center gap-2"
              >
                Next
                <ArrowRight className="w-4 h-4" />
              </button>
            ) : (
              <button
                onClick={handleSubmit}
                disabled={loading}
                className="px-6 py-3 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 transition-colors flex items-center gap-2 disabled:opacity-50"
              >
                {loading ? 'Processing...' : 'Open Recurring Deposit'}
                <CheckCircle className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function StepProductSelection({ products, formData, setFormData }: any) {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 mb-2">Select RD Product</h2>
        <p className="text-slate-600">Choose recurring deposit plan</p>
      </div>
      
      <div className="grid grid-cols-1 gap-4">
        {products.map((product: any) => (
          <label key={product.id} className="cursor-pointer">
            <input
              type="radio"
              name="product"
              value={product.id}
              checked={formData.product_id === product.id}
              onChange={(e) => setFormData({ ...formData, product_id: e.target.value })}
              className="sr-only"
            />
            <div className={`p-6 border-2 rounded-xl transition-all ${
              formData.product_id === product.id
                ? 'border-orange-600 bg-orange-50'
                : 'border-slate-200 hover:border-orange-300'
            }`}>
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-bold text-slate-900 text-lg">{product.name}</h3>
                  <p className="text-slate-600 text-sm mt-1">{product.code}</p>
                </div>
                <div className="text-right">
                  <p className="text-3xl font-bold text-orange-600">{product.default_interest_rate}%</p>
                  <p className="text-slate-600 text-sm">p.a.</p>
                </div>
              </div>
            </div>
          </label>
        ))}
      </div>
    </div>
  );
}

function StepRDDetails({ formData, setFormData, selectedProduct, maturityCalc }: any) {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 mb-2">RD Details</h2>
        <p className="text-slate-600">Enter monthly installment and duration</p>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            Monthly Installment (₹)
          </label>
          <input
            type="number"
            value={formData.installment_amount}
            onChange={(e) => setFormData({ ...formData, installment_amount: Number(e.target.value) })}
            min={500}
            step={500}
            className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-orange-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            Number of Months
          </label>
          <select
            value={formData.num_installments}
            onChange={(e) => setFormData({ ...formData, num_installments: Number(e.target.value) })}
            className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-orange-500"
          >
            <option value={6}>6 Months</option>
            <option value={12}>12 Months (1 Year)</option>
            <option value={24}>24 Months (2 Years)</option>
            <option value={36}>36 Months (3 Years)</option>
            <option value={60}>60 Months (5 Years)</option>
          </select>
        </div>
      </div>

      <div className="flex items-center gap-3 p-4 bg-slate-50 rounded-lg">
        <input
          type="checkbox"
          id="senior_citizen"
          checked={formData.is_senior_citizen}
          onChange={(e) => setFormData({ ...formData, is_senior_citizen: e.target.checked })}
          className="w-4 h-4 text-orange-600"
        />
        <label htmlFor="senior_citizen" className="text-sm font-medium text-slate-700">
          Senior Citizen (Additional 0.5% rate)
        </label>
      </div>

      {maturityCalc && (
        <div className="bg-gradient-to-r from-orange-50 to-red-50 rounded-xl p-6 border border-orange-200">
          <h3 className="font-bold text-slate-900 mb-4">Maturity Projection</h3>
          <div className="grid grid-cols-3 gap-6">
            <div>
              <p className="text-sm text-slate-600">Total Deposits</p>
              <p className="text-2xl font-bold text-slate-900">
                ₹{maturityCalc.total_principal?.toLocaleString('en-IN')}
              </p>
            </div>
            <div>
              <p className="text-sm text-slate-600">Interest Rate</p>
              <p className="text-2xl font-bold text-orange-600">{maturityCalc.annual_rate}%</p>
            </div>
            <div>
              <p className="text-sm text-slate-600">Interest Earned</p>
              <p className="text-2xl font-bold text-green-600">
                ₹{maturityCalc.total_interest?.toLocaleString('en-IN')}
              </p>
            </div>
          </div>
          <div className="mt-6 pt-6 border-t border-orange-200">
            <p className="text-sm text-slate-600">Maturity Amount</p>
            <p className="text-4xl font-bold text-purple-600">
              ₹{maturityCalc.maturity_amount?.toLocaleString('en-IN')}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

function StepCustomerInfo({ formData, setFormData }: any) {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 mb-2">Customer Information</h2>
        <p className="text-slate-600">Enter customer details and payment setup</p>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">CIF Number</label>
          <input
            type="text"
            value={formData.cif_number}
            onChange={(e) => setFormData({ ...formData, cif_number: e.target.value })}
            placeholder="CIF12345"
            className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-orange-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">Branch Code</label>
          <select
            value={formData.branch_code}
            onChange={(e) => setFormData({ ...formData, branch_code: e.target.value })}
            className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-orange-500"
          >
            <option value="BR001">Branch 001</option>
            <option value="BR002">Branch 002</option>
            <option value="BR003">Branch 003</option>
          </select>
        </div>
      </div>

      <div className="p-6 bg-orange-50 rounded-xl border border-orange-200 space-y-4">
        <div className="flex items-center gap-3">
          <input
            type="checkbox"
            id="auto_debit"
            checked={formData.auto_debit}
            onChange={(e) => setFormData({ ...formData, auto_debit: e.target.checked })}
            className="w-4 h-4 text-orange-600"
          />
          <label htmlFor="auto_debit" className="font-medium text-slate-900">
            Setup Auto-Debit for Monthly Installments
          </label>
        </div>
        
        {formData.auto_debit && (
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">Debit Account Number</label>
            <input
              type="text"
              value={formData.debit_account}
              onChange={(e) => setFormData({ ...formData, debit_account: e.target.value })}
              placeholder="Enter savings account number"
              className="w-full px-4 py-3 border border-slate-300 rounded-lg"
            />
          </div>
        )}
      </div>
    </div>
  );
}

function StepNominees({ formData, setFormData }: any) {
  const updateNominee = (index: number, field: string, value: any) => {
    const newNominees = [...formData.nominees];
    newNominees[index] = { ...newNominees[index], [field]: value };
    setFormData({ ...formData, nominees: newNominees });
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 mb-2">Nominee Details</h2>
        <p className="text-slate-600">Add nominee information</p>
      </div>

      <div className="p-6 bg-slate-50 rounded-xl space-y-4">
        <h3 className="font-bold text-slate-900">Nominee</h3>
        
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">Full Name</label>
            <input
              type="text"
              value={formData.nominees[0].name}
              onChange={(e) => updateNominee(0, 'name', e.target.value)}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">Relationship</label>
            <select
              value={formData.nominees[0].relationship}
              onChange={(e) => updateNominee(0, 'relationship', e.target.value)}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg"
            >
              <option value="SPOUSE">Spouse</option>
              <option value="SON">Son</option>
              <option value="DAUGHTER">Daughter</option>
              <option value="FATHER">Father</option>
              <option value="MOTHER">Mother</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">Date of Birth</label>
            <input
              type="date"
              value={formData.nominees[0].date_of_birth}
              onChange={(e) => updateNominee(0, 'date_of_birth', e.target.value)}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">Phone</label>
            <input
              type="tel"
              value={formData.nominees[0].phone}
              onChange={(e) => updateNominee(0, 'phone', e.target.value)}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg"
            />
          </div>
        </div>
      </div>
    </div>
  );
}

function StepReview({ formData, selectedProduct, maturityCalc }: any) {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 mb-2">Review & Confirm</h2>
        <p className="text-slate-600">Review all details before submitting</p>
      </div>

      <div className="space-y-4">
        <div className="p-6 bg-slate-50 rounded-xl">
          <h3 className="font-bold text-slate-900 mb-4">RD Details</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-slate-600">Product</span>
              <span className="font-semibold text-slate-900">{selectedProduct?.name}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-600">Monthly Installment</span>
              <span className="font-semibold text-slate-900">₹{formData.installment_amount.toLocaleString('en-IN')}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-600">Number of Months</span>
              <span className="font-semibold text-slate-900">{formData.num_installments}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-600">Total Deposits</span>
              <span className="font-semibold text-slate-900">₹{maturityCalc?.total_principal?.toLocaleString('en-IN')}</span>
            </div>
          </div>
        </div>

        <div className="p-6 bg-green-50 rounded-xl border border-green-200">
          <h3 className="font-bold text-slate-900 mb-4">Maturity Projection</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-slate-600">Interest Earned</span>
              <span className="font-semibold text-green-600">₹{maturityCalc?.total_interest?.toLocaleString('en-IN')}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-600">Maturity Amount</span>
              <span className="font-bold text-2xl text-green-600">₹{maturityCalc?.maturity_amount?.toLocaleString('en-IN')}</span>
            </div>
          </div>
        </div>

        <div className="p-6 bg-slate-50 rounded-xl">
          <h3 className="font-bold text-slate-900 mb-4">Customer & Payment</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-slate-600">CIF Number</span>
              <span className="font-semibold text-slate-900">{formData.cif_number}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-600">Auto-Debit</span>
              <span className="font-semibold text-slate-900">{formData.auto_debit ? 'Enabled' : 'Disabled'}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
