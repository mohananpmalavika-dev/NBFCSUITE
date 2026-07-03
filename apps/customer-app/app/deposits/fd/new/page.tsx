/**
 * Open Fixed Deposit - Multi-step Form
 * Complete FD opening workflow with real-time calculations
 */

'use client';

import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import { 
  Building2,
  User,
  Users,
  TrendingUp,
  Calendar,
  CheckCircle,
  AlertCircle,
  ArrowRight,
  ArrowLeft,
  Sparkles,
  IndianRupee
} from 'lucide-react';

interface FDFormData {
  // Customer Info
  customer_id: string;
  cif_number: string;
  
  // Product Selection
  product_id: string;
  
  // Deposit Details
  principal_amount: number;
  tenure_days: number;
  is_senior_citizen: boolean;
  branch_code: string;
  
  // Interest Payout
  interest_payout_account: string;
  auto_renewal: boolean;
  
  // Nominees
  nominees: Array<{
    name: string;
    relationship: string;
    date_of_birth: string;
    phone: string;
    allocation_percentage: number;
  }>;
}

export default function OpenFDPage() {
  const searchParams = useSearchParams();
  const productId = searchParams?.get('product');
  
  const [step, setStep] = useState(1);
  const [products, setProducts] = useState<any[]>([]);
  const [selectedProduct, setSelectedProduct] = useState<any>(null);
  const [calculation, setCalculation] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  
  const [formData, setFormData] = useState<FDFormData>({
    customer_id: '',
    cif_number: '',
    product_id: productId || '',
    principal_amount: 100000,
    tenure_days: 365,
    is_senior_citizen: false,
    branch_code: 'BR001',
    interest_payout_account: '',
    auto_renewal: false,
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
    if (selectedProduct && formData.principal_amount && formData.tenure_days) {
      calculateMaturity();
    }
  }, [formData.principal_amount, formData.tenure_days, formData.is_senior_citizen, selectedProduct]);

  const fetchProducts = async () => {
    try {
      const response = await fetch('http://localhost:8007/api/v1/products?deposit_type=FIXED_DEPOSIT');
      const data = await response.json();
      setProducts(data);
      
      if (productId && data.length > 0) {
        const product = data.find((p: any) => p.id === productId);
        if (product) {
          setSelectedProduct(product);
        }
      }
    } catch (error) {
      console.error('Error fetching products:', error);
    }
  };

  const calculateMaturity = async () => {
    if (!selectedProduct) return;
    
    try {
      const response = await fetch('http://localhost:8007/api/v1/products/calculate-rate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          product_id: formData.product_id,
          amount: formData.principal_amount,
          tenure_days: formData.tenure_days,
          is_senior_citizen: formData.is_senior_citizen
        })
      });
      
      const rateData = await response.json();
      
      const interestResponse = await fetch('http://localhost:8007/api/v1/interest/calculate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          principal: formData.principal_amount,
          rate: rateData.applicable_rate,
          days: formData.tenure_days,
          method: selectedProduct.interest_method
        })
      });
      
      const interestData = await interestResponse.json();
      setCalculation({
        ...rateData,
        ...interestData
      });
    } catch (error) {
      console.error('Error calculating:', error);
    }
  };

  const handleSubmit = async () => {
    setLoading(true);
    
    try {
      const response = await fetch('http://localhost:8007/api/v1/accounts/fd', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      
      if (response.ok) {
        // Show success and redirect
        alert(`Fixed Deposit opened successfully!\nAccount Number: ${data.account_number}`);
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
        return <StepProductSelection 
          products={products}
          formData={formData}
          setFormData={setFormData}
          selectedProduct={selectedProduct}
        />;
      case 2:
        return <StepDepositDetails 
          formData={formData}
          setFormData={setFormData}
          selectedProduct={selectedProduct}
          calculation={calculation}
        />;
      case 3:
        return <StepCustomerInfo 
          formData={formData}
          setFormData={setFormData}
        />;
      case 4:
        return <StepNominees 
          formData={formData}
          setFormData={setFormData}
        />;
      case 5:
        return <StepReview 
          formData={formData}
          selectedProduct={selectedProduct}
          calculation={calculation}
        />;
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50/30 p-8">
      <div className="max-w-4xl mx-auto">
        
        {/* Progress Steps */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            {['Product', 'Details', 'Customer', 'Nominees', 'Review'].map((label, index) => (
              <div key={label} className="flex items-center">
                <div className={`flex items-center justify-center w-10 h-10 rounded-full font-bold ${
                  step > index + 1 ? 'bg-green-600 text-white' :
                  step === index + 1 ? 'bg-blue-600 text-white' :
                  'bg-slate-200 text-slate-600'
                }`}>
                  {step > index + 1 ? <CheckCircle className="w-5 h-5" /> : index + 1}
                </div>
                <div className="ml-2">
                  <p className={`text-sm font-medium ${step >= index + 1 ? 'text-slate-900' : 'text-slate-500'}`}>
                    {label}
                  </p>
                </div>
                {index < 4 && (
                  <div className={`w-20 h-1 mx-4 ${step > index + 1 ? 'bg-green-600' : 'bg-slate-200'}`} />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Form Content */}
        <div className="bg-white rounded-xl shadow-lg border border-slate-200 p-8">
          {renderStep()}
          
          {/* Navigation Buttons */}
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
                className="px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors flex items-center gap-2"
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
                {loading ? 'Processing...' : 'Open Fixed Deposit'}
                <CheckCircle className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// Step Components

function StepProductSelection({ products, formData, setFormData, selectedProduct }: any) {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 mb-2">Select Fixed Deposit Product</h2>
        <p className="text-slate-600">Choose the FD plan that suits your needs</p>
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
                ? 'border-blue-600 bg-blue-50'
                : 'border-slate-200 hover:border-blue-300'
            }`}>
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-bold text-slate-900 text-lg">{product.name}</h3>
                  <p className="text-slate-600 text-sm mt-1">{product.code}</p>
                </div>
                <div className="text-right">
                  <p className="text-3xl font-bold text-blue-600">{product.default_interest_rate}%</p>
                  <p className="text-slate-600 text-sm">p.a.</p>
                </div>
              </div>
              <div className="mt-4 flex gap-6 text-sm">
                <div>
                  <p className="text-slate-600">Min Amount</p>
                  <p className="font-semibold">₹{product.min_amount.toLocaleString('en-IN')}</p>
                </div>
                <div>
                  <p className="text-slate-600">Min Tenure</p>
                  <p className="font-semibold">{product.min_tenure_days} days</p>
                </div>
                <div>
                  <p className="text-slate-600">Payout</p>
                  <p className="font-semibold">{product.payout_frequency.replace(/_/g, ' ')}</p>
                </div>
              </div>
            </div>
          </label>
        ))}
      </div>
    </div>
  );
}

function StepDepositDetails({ formData, setFormData, selectedProduct, calculation }: any) {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 mb-2">Deposit Details</h2>
        <p className="text-slate-600">Enter the deposit amount and tenure</p>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            Deposit Amount (₹)
          </label>
          <input
            type="number"
            value={formData.principal_amount}
            onChange={(e) => setFormData({ ...formData, principal_amount: Number(e.target.value) })}
            min={selectedProduct?.min_amount || 10000}
            max={selectedProduct?.max_amount || 10000000}
            step={1000}
            className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          {selectedProduct && (
            <p className="text-xs text-slate-600 mt-1">
              Min: ₹{selectedProduct.min_amount.toLocaleString('en-IN')} 
              {selectedProduct.max_amount && ` | Max: ₹${selectedProduct.max_amount.toLocaleString('en-IN')}`}
            </p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            Tenure (days)
          </label>
          <input
            type="number"
            value={formData.tenure_days}
            onChange={(e) => setFormData({ ...formData, tenure_days: Number(e.target.value) })}
            min={selectedProduct?.min_tenure_days || 90}
            max={selectedProduct?.max_tenure_days || 3650}
            step={30}
            className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          {selectedProduct && (
            <p className="text-xs text-slate-600 mt-1">
              Min: {selectedProduct.min_tenure_days} days | Max: {selectedProduct.max_tenure_days} days
            </p>
          )}
        </div>
      </div>

      <div className="flex items-center gap-3 p-4 bg-slate-50 rounded-lg">
        <input
          type="checkbox"
          id="senior_citizen"
          checked={formData.is_senior_citizen}
          onChange={(e) => setFormData({ ...formData, is_senior_citizen: e.target.checked })}
          className="w-4 h-4 text-blue-600"
        />
        <label htmlFor="senior_citizen" className="text-sm font-medium text-slate-700">
          Senior Citizen (Get additional 0.5% interest rate)
        </label>
      </div>

      {calculation && (
        <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-6 border border-blue-200">
          <h3 className="font-bold text-slate-900 mb-4">Maturity Projection</h3>
          <div className="grid grid-cols-3 gap-6">
            <div>
              <p className="text-sm text-slate-600">Principal Amount</p>
              <p className="text-2xl font-bold text-slate-900">₹{formData.principal_amount.toLocaleString('en-IN')}</p>
            </div>
            <div>
              <p className="text-sm text-slate-600">Interest Rate</p>
              <p className="text-2xl font-bold text-blue-600">{calculation.applicable_rate}%</p>
            </div>
            <div>
              <p className="text-sm text-slate-600">Interest Earned</p>
              <p className="text-2xl font-bold text-green-600">₹{calculation.interest?.toLocaleString('en-IN')}</p>
            </div>
          </div>
          <div className="mt-6 pt-6 border-t border-blue-200">
            <p className="text-sm text-slate-600">Maturity Amount</p>
            <p className="text-4xl font-bold text-purple-600">₹{calculation.maturity_amount?.toLocaleString('en-IN')}</p>
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
        <p className="text-slate-600">Enter customer details</p>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            Customer ID / CIF Number
          </label>
          <input
            type="text"
            value={formData.cif_number}
            onChange={(e) => setFormData({ ...formData, cif_number: e.target.value })}
            placeholder="CIF12345"
            className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            Branch Code
          </label>
          <select
            value={formData.branch_code}
            onChange={(e) => setFormData({ ...formData, branch_code: e.target.value })}
            className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="BR001">Branch 001 - Head Office</option>
            <option value="BR002">Branch 002 - City Center</option>
            <option value="BR003">Branch 003 - Downtown</option>
          </select>
        </div>
      </div>

      <div className="flex items-center gap-3 p-4 bg-slate-50 rounded-lg">
        <input
          type="checkbox"
          id="auto_renewal"
          checked={formData.auto_renewal}
          onChange={(e) => setFormData({ ...formData, auto_renewal: e.target.checked })}
          className="w-4 h-4 text-blue-600"
        />
        <label htmlFor="auto_renewal" className="text-sm font-medium text-slate-700">
          Enable Auto-Renewal on Maturity
        </label>
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
        <p className="text-slate-600">Add nominee information (optional)</p>
      </div>

      {formData.nominees.map((nominee: any, index: number) => (
        <div key={index} className="p-6 bg-slate-50 rounded-xl space-y-4">
          <h3 className="font-bold text-slate-900">Nominee {index + 1}</h3>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Full Name</label>
              <input
                type="text"
                value={nominee.name}
                onChange={(e) => updateNominee(index, 'name', e.target.value)}
                className="w-full px-4 py-2 border border-slate-300 rounded-lg"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Relationship</label>
              <select
                value={nominee.relationship}
                onChange={(e) => updateNominee(index, 'relationship', e.target.value)}
                className="w-full px-4 py-2 border border-slate-300 rounded-lg"
              >
                <option value="SPOUSE">Spouse</option>
                <option value="SON">Son</option>
                <option value="DAUGHTER">Daughter</option>
                <option value="FATHER">Father</option>
                <option value="MOTHER">Mother</option>
                <option value="BROTHER">Brother</option>
                <option value="SISTER">Sister</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Date of Birth</label>
              <input
                type="date"
                value={nominee.date_of_birth}
                onChange={(e) => updateNominee(index, 'date_of_birth', e.target.value)}
                className="w-full px-4 py-2 border border-slate-300 rounded-lg"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Phone</label>
              <input
                type="tel"
                value={nominee.phone}
                onChange={(e) => updateNominee(index, 'phone', e.target.value)}
                className="w-full px-4 py-2 border border-slate-300 rounded-lg"
              />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

function StepReview({ formData, selectedProduct, calculation }: any) {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 mb-2">Review & Confirm</h2>
        <p className="text-slate-600">Please review all details before submitting</p>
      </div>

      <div className="space-y-4">
        <ReviewSection title="Product Details">
          <ReviewItem label="Product" value={selectedProduct?.name} />
          <ReviewItem label="Product Code" value={selectedProduct?.code} />
        </ReviewSection>

        <ReviewSection title="Deposit Details">
          <ReviewItem label="Principal Amount" value={`₹${formData.principal_amount.toLocaleString('en-IN')}`} />
          <ReviewItem label="Tenure" value={`${formData.tenure_days} days (${Math.round(formData.tenure_days / 365)} year${formData.tenure_days >= 730 ? 's' : ''})`} />
          <ReviewItem label="Interest Rate" value={`${calculation?.applicable_rate}% p.a.`} />
          <ReviewItem label="Senior Citizen" value={formData.is_senior_citizen ? 'Yes' : 'No'} />
        </ReviewSection>

        <ReviewSection title="Maturity Projection">
          <ReviewItem label="Interest Earned" value={`₹${calculation?.interest?.toLocaleString('en-IN')}`} />
          <ReviewItem label="Maturity Amount" value={`₹${calculation?.maturity_amount?.toLocaleString('en-IN')}`} className="text-green-600 font-bold" />
        </ReviewSection>

        <ReviewSection title="Customer Details">
          <ReviewItem label="CIF Number" value={formData.cif_number} />
          <ReviewItem label="Branch" value={formData.branch_code} />
          <ReviewItem label="Auto Renewal" value={formData.auto_renewal ? 'Enabled' : 'Disabled'} />
        </ReviewSection>

        {formData.nominees[0].name && (
          <ReviewSection title="Nominee">
            <ReviewItem label="Name" value={formData.nominees[0].name} />
            <ReviewItem label="Relationship" value={formData.nominees[0].relationship} />
          </ReviewSection>
        )}
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p className="text-sm text-blue-900">
          <strong>Note:</strong> By submitting this form, you agree to the terms and conditions of the Fixed Deposit scheme.
          The deposit will be subject to approval by authorized personnel.
        </p>
      </div>
    </div>
  );
}

function ReviewSection({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="p-6 bg-slate-50 rounded-xl">
      <h3 className="font-bold text-slate-900 mb-4">{title}</h3>
      <div className="space-y-3">
        {children}
      </div>
    </div>
  );
}

function ReviewItem({ label, value, className = '' }: { label: string; value: string; className?: string }) {
  return (
    <div className="flex justify-between items-center">
      <span className="text-slate-600">{label}</span>
      <span className={`font-semibold ${className || 'text-slate-900'}`}>{value}</span>
    </div>
  );
}
