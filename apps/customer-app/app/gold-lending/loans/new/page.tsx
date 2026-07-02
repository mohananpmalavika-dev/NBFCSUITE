'use client';

import { useState, useEffect } from 'react';
import { goldApi } from '../../goldApi';
import { useRouter } from 'next/navigation';

interface Product {
  id: string;
  product_code: string;
  product_name: string;
  min_amount: number;
  max_amount: number;
  min_tenure_months: number;
  max_tenure_months: number;
  base_interest_rate: number;
}

interface Ornament {
  id: string;
  ornament_code: string;
  ornament_type: string;
  gross_weight: number;
  net_weight: number;
  purity_karat: number;
  appraised_value: number;
  status: string;
}

export default function NewLoanApplicationPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Form data
  const [customerId, setCustomerId] = useState('');
  const [productId, setProductId] = useState('');
  const [branchId, setBranchId] = useState('');
  const [requestedAmount, setRequestedAmount] = useState('');
  const [requestedTenure, setRequestedTenure] = useState('');
  const [purpose, setPurpose] = useState('');
  const [remarks, setRemarks] = useState('');

  // Data
  const [products, setProducts] = useState<Product[]>([]);
  const [availableOrnaments, setAvailableOrnaments] = useState<Ornament[]>([]);
  const [selectedOrnaments, setSelectedOrnaments] = useState<string[]>([]);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);

  useEffect(() => {
    loadProducts();
  }, []);

  useEffect(() => {
    if (customerId) {
      loadCustomerOrnaments();
    }
  }, [customerId]);

  useEffect(() => {
    if (productId) {
      const product = products.find(p => p.id === productId);
      setSelectedProduct(product || null);
    }
  }, [productId, products]);

  const loadProducts = async () => {
    try {
      const data = await goldApi.listProducts(true);
      setProducts(data);
    } catch (err: any) {
      setError('Failed to load products: ' + err.message);
    }
  };

  const loadCustomerOrnaments = async () => {
    try {
      // This would need a proper endpoint - using placeholder
      // In real implementation, filter ornaments by customer_id and status='available'
      setAvailableOrnaments([]);
    } catch (err) {
      console.error('Failed to load ornaments:', err);
    }
  };

  const toggleOrnament = (ornamentId: string) => {
    if (selectedOrnaments.includes(ornamentId)) {
      setSelectedOrnaments(selectedOrnaments.filter(id => id !== ornamentId));
    } else {
      setSelectedOrnaments([...selectedOrnaments, ornamentId]);
    }
  };

  const calculateTotalValue = () => {
    return availableOrnaments
      .filter(o => selectedOrnaments.includes(o.id))
      .reduce((sum, o) => sum + o.appraised_value, 0);
  };

  const validateStep1 = () => {
    if (!customerId.trim()) {
      setError('Customer ID is required');
      return false;
    }
    if (!productId) {
      setError('Please select a product');
      return false;
    }
    if (!branchId.trim()) {
      setError('Branch ID is required');
      return false;
    }
    if (!requestedAmount || parseFloat(requestedAmount) <= 0) {
      setError('Valid requested amount is required');
      return false;
    }
    if (!requestedTenure || parseInt(requestedTenure) <= 0) {
      setError('Valid tenure is required');
      return false;
    }

    // Validate against product limits
    if (selectedProduct) {
      const amount = parseFloat(requestedAmount);
      const tenure = parseInt(requestedTenure);

      if (amount < selectedProduct.min_amount || amount > selectedProduct.max_amount) {
        setError(`Amount must be between ₹${selectedProduct.min_amount} and ₹${selectedProduct.max_amount}`);
        return false;
      }

      if (tenure < selectedProduct.min_tenure_months || tenure > selectedProduct.max_tenure_months) {
        setError(`Tenure must be between ${selectedProduct.min_tenure_months} and ${selectedProduct.max_tenure_months} months`);
        return false;
      }
    }

    setError('');
    return true;
  };

  const validateStep2 = () => {
    if (selectedOrnaments.length === 0) {
      setError('Please select at least one ornament');
      return false;
    }

    const totalValue = calculateTotalValue();
    const requestedAmt = parseFloat(requestedAmount);

    if (totalValue < requestedAmt * 1.2) {
      setError(`Total ornament value (₹${totalValue.toFixed(2)}) should be at least 120% of requested amount`);
      return false;
    }

    setError('');
    return true;
  };

  const handleNext = () => {
    if (step === 1 && validateStep1()) {
      setStep(2);
    } else if (step === 2 && validateStep2()) {
      setStep(3);
    }
  };

  const handleBack = () => {
    setStep(step - 1);
    setError('');
  };

  const handleSubmit = async () => {
    try {
      setLoading(true);
      setError('');

      const payload = {
        customer_id: customerId,
        product_id: productId,
        branch_id: branchId,
        requested_amount: parseFloat(requestedAmount),
        requested_tenure_months: parseInt(requestedTenure),
        purpose: purpose || undefined,
        remarks: remarks || undefined,
        ornament_ids: selectedOrnaments,
      };

      const application = await goldApi.createLoanApplication(payload);
      
      setSuccess('Loan application created successfully!');
      
      // Redirect to application detail page after 2 seconds
      setTimeout(() => {
        router.push(`/gold-lending/loans/${application.id}`);
      }, 2000);
    } catch (err: any) {
      setError(err.message || 'Failed to create application');
    } finally {
      setLoading(false);
    }
  };

  const formatAmount = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(amount);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">New Loan Application</h1>
          <p className="text-gray-600 mt-1">Create a new gold loan application</p>
        </div>

        {/* Progress Steps */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${
                step >= 1 ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-600'
              }`}>
                1
              </div>
              <div className="ml-3">
                <div className="text-sm font-medium text-gray-900">Application Details</div>
              </div>
            </div>
            <div className={`flex-1 h-1 mx-4 ${step >= 2 ? 'bg-blue-600' : 'bg-gray-200'}`}></div>
            <div className="flex items-center">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${
                step >= 2 ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-600'
              }`}>
                2
              </div>
              <div className="ml-3">
                <div className="text-sm font-medium text-gray-900">Select Ornaments</div>
              </div>
            </div>
            <div className={`flex-1 h-1 mx-4 ${step >= 3 ? 'bg-blue-600' : 'bg-gray-200'}`}></div>
            <div className="flex items-center">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${
                step >= 3 ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-600'
              }`}>
                3
              </div>
              <div className="ml-3">
                <div className="text-sm font-medium text-gray-900">Review & Submit</div>
              </div>
            </div>
          </div>
        </div>

        {/* Messages */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        {success && (
          <div className="mb-6 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">
            {success}
          </div>
        )}

        {/* Step 1: Application Details */}
        {step === 1 && (
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Application Details</h2>
            
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Customer ID <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={customerId}
                    onChange={(e) => setCustomerId(e.target.value)}
                    placeholder="Enter customer ID"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Branch ID <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={branchId}
                    onChange={(e) => setBranchId(e.target.value)}
                    placeholder="Enter branch ID"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Product <span className="text-red-500">*</span>
                </label>
                <select
                  value={productId}
                  onChange={(e) => setProductId(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">Select a product</option>
                  {products.map(product => (
                    <option key={product.id} value={product.id}>
                      {product.product_name} ({product.product_code}) - {product.base_interest_rate}% p.a.
                    </option>
                  ))}
                </select>
              </div>

              {selectedProduct && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h3 className="font-medium text-blue-900 mb-2">Product Details</h3>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-blue-700">Amount Range:</span>
                      <span className="ml-2 font-medium text-blue-900">
                        {formatAmount(selectedProduct.min_amount)} - {formatAmount(selectedProduct.max_amount)}
                      </span>
                    </div>
                    <div>
                      <span className="text-blue-700">Tenure Range:</span>
                      <span className="ml-2 font-medium text-blue-900">
                        {selectedProduct.min_tenure_months} - {selectedProduct.max_tenure_months} months
                      </span>
                    </div>
                  </div>
                </div>
              )}

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Requested Amount (₹) <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="number"
                    value={requestedAmount}
                    onChange={(e) => setRequestedAmount(e.target.value)}
                    placeholder="Enter amount"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Tenure (months) <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="number"
                    value={requestedTenure}
                    onChange={(e) => setRequestedTenure(e.target.value)}
                    placeholder="Enter tenure"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Purpose
                </label>
                <input
                  type="text"
                  value={purpose}
                  onChange={(e) => setPurpose(e.target.value)}
                  placeholder="Purpose of loan (optional)"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Remarks
                </label>
                <textarea
                  value={remarks}
                  onChange={(e) => setRemarks(e.target.value)}
                  placeholder="Additional remarks (optional)"
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            <div className="mt-8 flex justify-end gap-4">
              <button
                onClick={() => router.push('/gold-lending/loans')}
                className="px-6 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleNext}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Next: Select Ornaments →
              </button>
            </div>
          </div>
        )}

        {/* Step 2: Select Ornaments */}
        {step === 2 && (
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Select Ornaments</h2>
            
            {availableOrnaments.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-gray-400 text-5xl mb-4">📿</div>
                <p className="text-gray-600 text-lg">No available ornaments found</p>
                <p className="text-gray-500 text-sm mt-2">
                  Make sure the customer has ornaments in 'available' status
                </p>
              </div>
            ) : (
              <>
                <div className="mb-6 bg-gray-50 rounded-lg p-4">
                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div>
                      <span className="text-gray-600">Selected Ornaments:</span>
                      <span className="ml-2 font-bold text-gray-900">{selectedOrnaments.length}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Total Value:</span>
                      <span className="ml-2 font-bold text-gray-900">{formatAmount(calculateTotalValue())}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Requested:</span>
                      <span className="ml-2 font-bold text-gray-900">{formatAmount(parseFloat(requestedAmount) || 0)}</span>
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  {availableOrnaments.map(ornament => (
                    <div
                      key={ornament.id}
                      className={`border-2 rounded-lg p-4 cursor-pointer transition-all ${
                        selectedOrnaments.includes(ornament.id)
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                      onClick={() => toggleOrnament(ornament.id)}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-3">
                            <input
                              type="checkbox"
                              checked={selectedOrnaments.includes(ornament.id)}
                              onChange={() => {}}
                              className="w-5 h-5"
                            />
                            <div>
                              <div className="font-medium text-gray-900">{ornament.ornament_code}</div>
                              <div className="text-sm text-gray-600">{ornament.ornament_type}</div>
                            </div>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="font-bold text-gray-900">{formatAmount(ornament.appraised_value)}</div>
                          <div className="text-sm text-gray-600">
                            {ornament.net_weight}g @ {ornament.purity_karat}K
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </>
            )}

            <div className="mt-8 flex justify-between">
              <button
                onClick={handleBack}
                className="px-6 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
              >
                ← Back
              </button>
              <button
                onClick={handleNext}
                disabled={selectedOrnaments.length === 0}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
              >
                Next: Review →
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Review & Submit */}
        {step === 3 && (
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Review & Submit</h2>
            
            <div className="space-y-6">
              {/* Application Summary */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">Application Summary</h3>
                <div className="bg-gray-50 rounded-lg p-4 space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Customer ID:</span>
                    <span className="font-medium text-gray-900">{customerId}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Branch ID:</span>
                    <span className="font-medium text-gray-900">{branchId}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Product:</span>
                    <span className="font-medium text-gray-900">
                      {selectedProduct?.product_name}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Requested Amount:</span>
                    <span className="font-bold text-blue-600">{formatAmount(parseFloat(requestedAmount))}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Tenure:</span>
                    <span className="font-medium text-gray-900">{requestedTenure} months</span>
                  </div>
                  {purpose && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Purpose:</span>
                      <span className="font-medium text-gray-900">{purpose}</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Ornaments Summary */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">Pledged Ornaments ({selectedOrnaments.length})</h3>
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="space-y-2">
                    {availableOrnaments
                      .filter(o => selectedOrnaments.includes(o.id))
                      .map(ornament => (
                        <div key={ornament.id} className="flex justify-between text-sm">
                          <span className="text-gray-900">{ornament.ornament_code} - {ornament.ornament_type}</span>
                          <span className="font-medium text-gray-900">{formatAmount(ornament.appraised_value)}</span>
                        </div>
                      ))}
                  </div>
                  <div className="mt-4 pt-4 border-t border-gray-200 flex justify-between font-bold">
                    <span className="text-gray-900">Total Collateral Value:</span>
                    <span className="text-green-600">{formatAmount(calculateTotalValue())}</span>
                  </div>
                </div>
              </div>

              {/* LTV Ratio */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex justify-between items-center">
                  <span className="text-blue-900 font-medium">Loan-to-Value (LTV) Ratio:</span>
                  <span className="text-2xl font-bold text-blue-600">
                    {((parseFloat(requestedAmount) / calculateTotalValue()) * 100).toFixed(2)}%
                  </span>
                </div>
              </div>
            </div>

            <div className="mt-8 flex justify-between">
              <button
                onClick={handleBack}
                disabled={loading}
                className="px-6 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors disabled:bg-gray-200 disabled:cursor-not-allowed"
              >
                ← Back
              </button>
              <button
                onClick={handleSubmit}
                disabled={loading}
                className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {loading && (
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                )}
                {loading ? 'Creating...' : 'Submit Application'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
