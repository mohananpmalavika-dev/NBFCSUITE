"use client";

import { useState, useEffect } from "react";
import { 
  TrendingDown,
  Calendar,
  DollarSign,
  Package,
  Play,
  Download,
  CheckCircle,
  AlertCircle,
  Info
} from "lucide-react";

interface DepreciationCalculation {
  financial_year: number;
  financial_month: number | null;
  calculation_date: string;
  asset_ids: number[] | null;
  auto_post: boolean;
}

interface DepreciationResult {
  total_assets: number;
  assets_depreciated: number;
  total_depreciation: number;
  posted_entries: number;
  errors: Array<{
    asset_id: number;
    asset_code: string;
    error: string;
  }>;
}

export default function DepreciationPage() {
  const [calculation, setCalculation] = useState<DepreciationCalculation>({
    financial_year: new Date().getFullYear(),
    financial_month: new Date().getMonth() + 1,
    calculation_date: new Date().toISOString().split('T')[0],
    asset_ids: null,
    auto_post: true,
  });

  const [result, setResult] = useState<DepreciationResult | null>(null);
  const [processing, setProcessing] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);

  const handleCalculate = async () => {
    if (!confirm("Are you sure you want to calculate depreciation? This will process all eligible assets.")) {
      return;
    }

    try {
      setProcessing(true);
      setShowSuccess(false);

      const response = await fetch('/api/v1/fixed-assets/depreciation/calculate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(calculation),
      });

      if (response.ok) {
        const data = await response.json();
        setResult(data);
        setShowSuccess(true);
        
        // Auto-hide success message after 5 seconds
        setTimeout(() => setShowSuccess(false), 5000);
      } else {
        alert('Failed to calculate depreciation. Please try again.');
      }
    } catch (error) {
      console.error("Error calculating depreciation:", error);
      alert('An error occurred while calculating depreciation.');
    } finally {
      setProcessing(false);
    }
  };

  const formatCurrency = (value: number) => {
    return `₹${value.toLocaleString("en-IN", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })}`;
  };

  const getMonthName = (month: number) => {
    const months = [
      "January", "February", "March", "April", "May", "June",
      "July", "August", "September", "October", "November", "December"
    ];
    return months[month - 1];
  };

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900">Run Depreciation</h2>
        <p className="mt-1 text-sm text-gray-500">
          Calculate and post depreciation for fixed assets
        </p>
      </div>

      {/* Success Message */}
      {showSuccess && result && (
        <div className="mb-6 bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-start">
            <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
            <div className="ml-3 flex-1">
              <h3 className="text-sm font-medium text-green-900">
                Depreciation Calculated Successfully
              </h3>
              <div className="mt-2 text-sm text-green-700">
                <p>
                  Processed {result.assets_depreciated} of {result.total_assets} assets.
                  Total depreciation: {formatCurrency(result.total_depreciation)}
                </p>
                {result.posted_entries > 0 && (
                  <p className="mt-1">
                    {result.posted_entries} journal entries posted automatically.
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Calculation Form */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Depreciation Parameters
            </h3>

            <div className="space-y-4">
              {/* Financial Year */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Financial Year
                </label>
                <input
                  type="number"
                  value={calculation.financial_year}
                  onChange={(e) => setCalculation({
                    ...calculation,
                    financial_year: parseInt(e.target.value)
                  })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  min="2000"
                  max="2100"
                />
              </div>

              {/* Financial Month */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Financial Month (Optional)
                </label>
                <select
                  value={calculation.financial_month || ""}
                  onChange={(e) => setCalculation({
                    ...calculation,
                    financial_month: e.target.value ? parseInt(e.target.value) : null
                  })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">Annual Depreciation</option>
                  {Array.from({ length: 12 }, (_, i) => i + 1).map((month) => (
                    <option key={month} value={month}>
                      {getMonthName(month)}
                    </option>
                  ))}
                </select>
                <p className="mt-1 text-xs text-gray-500">
                  Leave empty for annual depreciation, select month for monthly calculation
                </p>
              </div>

              {/* Calculation Date */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Calculation Date
                </label>
                <input
                  type="date"
                  value={calculation.calculation_date}
                  onChange={(e) => setCalculation({
                    ...calculation,
                    calculation_date: e.target.value
                  })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              {/* Auto Post */}
              <div className="flex items-start">
                <input
                  type="checkbox"
                  id="auto_post"
                  checked={calculation.auto_post}
                  onChange={(e) => setCalculation({
                    ...calculation,
                    auto_post: e.target.checked
                  })}
                  className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label htmlFor="auto_post" className="ml-2">
                  <span className="block text-sm font-medium text-gray-700">
                    Auto-post Journal Entries
                  </span>
                  <span className="block text-xs text-gray-500">
                    Automatically create and post journal entries for depreciation
                  </span>
                </label>
              </div>
            </div>

            {/* Info Box */}
            <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-start">
                <Info className="h-5 w-5 text-blue-600 mt-0.5" />
                <div className="ml-3">
                  <h4 className="text-sm font-medium text-blue-900">
                    How Depreciation Works
                  </h4>
                  <ul className="mt-2 text-sm text-blue-700 space-y-1 list-disc list-inside">
                    <li>Only active assets are considered</li>
                    <li>Depreciation is calculated based on the method configured for each asset</li>
                    <li>SLM: (Cost - Salvage) / Useful Life</li>
                    <li>WDV: Opening WDV × Rate%</li>
                    <li>Assets won't be depreciated below salvage value</li>
                    <li>Pro-rata calculation for partial periods</li>
                  </ul>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="mt-6 flex items-center justify-between">
              <button
                onClick={handleCalculate}
                disabled={processing}
                className={`flex items-center px-6 py-2 rounded-lg text-white font-medium ${
                  processing
                    ? "bg-gray-400 cursor-not-allowed"
                    : "bg-blue-600 hover:bg-blue-700"
                }`}
              >
                {processing ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                    Processing...
                  </>
                ) : (
                  <>
                    <Play className="h-5 w-5 mr-2" />
                    Calculate Depreciation
                  </>
                )}
              </button>

              <button
                className="flex items-center px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
              >
                <Download className="h-5 w-5 mr-2" />
                Export Report
              </button>
            </div>
          </div>

          {/* Results Section */}
          {result && (
            <div className="mt-6 bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Calculation Results
              </h3>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-xs text-gray-600 mb-1">Total Assets</p>
                  <p className="text-2xl font-bold text-gray-900">{result.total_assets}</p>
                </div>
                <div className="bg-green-50 rounded-lg p-4">
                  <p className="text-xs text-gray-600 mb-1">Depreciated</p>
                  <p className="text-2xl font-bold text-green-600">{result.assets_depreciated}</p>
                </div>
                <div className="bg-blue-50 rounded-lg p-4">
                  <p className="text-xs text-gray-600 mb-1">Total Amount</p>
                  <p className="text-lg font-bold text-blue-600">
                    {formatCurrency(result.total_depreciation)}
                  </p>
                </div>
                <div className="bg-purple-50 rounded-lg p-4">
                  <p className="text-xs text-gray-600 mb-1">Posted Entries</p>
                  <p className="text-2xl font-bold text-purple-600">{result.posted_entries}</p>
                </div>
              </div>

              {/* Errors */}
              {result.errors && result.errors.length > 0 && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <div className="flex items-start">
                    <AlertCircle className="h-5 w-5 text-red-600 mt-0.5" />
                    <div className="ml-3 flex-1">
                      <h4 className="text-sm font-medium text-red-900 mb-2">
                        Errors ({result.errors.length})
                      </h4>
                      <div className="space-y-2">
                        {result.errors.map((error, index) => (
                          <div key={index} className="text-sm text-red-700">
                            <span className="font-medium">{error.asset_code}:</span> {error.error}
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Sidebar - Quick Info */}
        <div>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 sticky top-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Depreciation Methods
            </h3>

            <div className="space-y-4">
              <div>
                <div className="flex items-center mb-2">
                  <div className="w-2 h-2 bg-blue-600 rounded-full mr-2"></div>
                  <h4 className="text-sm font-medium text-gray-900">
                    Straight Line (SLM)
                  </h4>
                </div>
                <p className="text-xs text-gray-600 ml-4">
                  Equal depreciation every year. Good for assets with consistent usage.
                </p>
              </div>

              <div>
                <div className="flex items-center mb-2">
                  <div className="w-2 h-2 bg-purple-600 rounded-full mr-2"></div>
                  <h4 className="text-sm font-medium text-gray-900">
                    Written Down Value (WDV)
                  </h4>
                </div>
                <p className="text-xs text-gray-600 ml-4">
                  Higher depreciation initially, decreasing over time. Commonly used for tax purposes.
                </p>
              </div>

              <div>
                <div className="flex items-center mb-2">
                  <div className="w-2 h-2 bg-green-600 rounded-full mr-2"></div>
                  <h4 className="text-sm font-medium text-gray-900">
                    Double Declining
                  </h4>
                </div>
                <p className="text-xs text-gray-600 ml-4">
                  Accelerated depreciation at twice the straight-line rate.
                </p>
              </div>

              <div>
                <div className="flex items-center mb-2">
                  <div className="w-2 h-2 bg-orange-600 rounded-full mr-2"></div>
                  <h4 className="text-sm font-medium text-gray-900">
                    Sum of Years
                  </h4>
                </div>
                <p className="text-xs text-gray-600 ml-4">
                  Progressive depreciation based on remaining useful life.
                </p>
              </div>
            </div>

            <div className="mt-6 pt-6 border-t border-gray-200">
              <h4 className="text-sm font-medium text-gray-900 mb-3">
                Recent Depreciation Runs
              </h4>
              <div className="space-y-3">
                <div className="flex items-center justify-between text-sm">
                  <div>
                    <p className="text-gray-900">Dec 2023</p>
                    <p className="text-xs text-gray-500">Annual</p>
                  </div>
                  <p className="text-gray-600">₹2.5L</p>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <div>
                    <p className="text-gray-900">Nov 2023</p>
                    <p className="text-xs text-gray-500">Monthly</p>
                  </div>
                  <p className="text-gray-600">₹45K</p>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <div>
                    <p className="text-gray-900">Oct 2023</p>
                    <p className="text-xs text-gray-500">Monthly</p>
                  </div>
                  <p className="text-gray-600">₹48K</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
