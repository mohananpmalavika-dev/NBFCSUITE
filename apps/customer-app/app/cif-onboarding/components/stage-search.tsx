'use client';

import { useState } from 'react';
import { useCIFStore } from '@/lib/cif-store';
import { cifApi } from '@/lib/cif-api';

export default function StageSearch() {
  const { searchData, updateSearchData, setLoading, setError, setCustomerId, setCurrentStep } =
    useCIFStore();
  const [searchResults, setSearchResults] = useState<any | null>(null);
  const [searching, setSearching] = useState(false);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchData.mobileNumber && !searchData.panNumber && !searchData.aadharNumber && !searchData.email) {
      setError('Please enter at least one search criteria');
      return;
    }

    setSearching(true);
    setLoading(true);
    try {
      const results = await cifApi.searchCustomer({
        mobile_number: searchData.mobileNumber,
        pan_number: searchData.panNumber,
        aadhar_number: searchData.aadharNumber,
        email: searchData.email,
      });

      setSearchResults(results);
      if (results.found && results.customer_id) {
        setCustomerId(results.customer_id);
        setError(null);
      } else {
        setCustomerId('');
      }
    } catch (err: any) {
      setError(err.message || 'Search failed');
    } finally {
      setSearching(false);
      setLoading(false);
    }
  };

  const handleNewCustomer = () => {
    setSearchResults(null);
    setCustomerId('');
    setCurrentStep(2); // Go to prospect stage
  };

  const handleExistingCustomer = () => {
    if (searchResults?.found && searchResults?.customer_id) {
      // Jump to customer 360 view
      setCurrentStep(18);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 mb-2">Stage 1: Customer Search</h2>
        <p className="text-slate-600">
          Search for existing customers to prevent duplicates. Try searching by any identifier.
        </p>
      </div>

      <form onSubmit={handleSearch} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Mobile Number
            </label>
            <input
              type="tel"
              placeholder="9876543210"
              value={searchData.mobileNumber || ''}
              onChange={(e) => updateSearchData({ mobileNumber: e.target.value })}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              PAN Number
            </label>
            <input
              type="text"
              placeholder="AAAPB1234C"
              value={searchData.panNumber || ''}
              onChange={(e) => updateSearchData({ panNumber: e.target.value.toUpperCase() })}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Aadhaar Number
            </label>
            <input
              type="text"
              placeholder="1234 5678 9012"
              value={searchData.aadharNumber || ''}
              onChange={(e) => updateSearchData({ aadharNumber: e.target.value })}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Email Address
            </label>
            <input
              type="email"
              placeholder="customer@example.com"
              value={searchData.email || ''}
              onChange={(e) => updateSearchData({ email: e.target.value })}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={searching}
          className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 font-semibold transition-colors"
        >
          {searching ? 'Searching...' : '🔍 Search Customer'}
        </button>
      </form>

      {/* Search Results */}
      {searchResults && (
        <div
          className={`border rounded-lg p-6 ${
            searchResults.found
              ? 'bg-green-50 border-green-200'
              : 'bg-blue-50 border-blue-200'
          }`}
        >
          {searchResults.found ? (
            <div className="space-y-4">
              <div>
                <h3 className="text-lg font-bold text-green-900 mb-2">
                  ✅ Customer Found!
                </h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-slate-600">Customer ID</p>
                    <p className="font-semibold text-slate-900">{searchResults.customer_id}</p>
                  </div>
                  <div>
                    <p className="text-slate-600">Name</p>
                    <p className="font-semibold text-slate-900">{searchResults.customer_name}</p>
                  </div>
                  <div>
                    <p className="text-slate-600">Mobile</p>
                    <p className="font-semibold text-slate-900">{searchResults.mobile}</p>
                  </div>
                  <div>
                    <p className="text-slate-600">Status</p>
                    <p className="font-semibold text-slate-900">{searchResults.status}</p>
                  </div>
                </div>
              </div>

              <button
                onClick={handleExistingCustomer}
                className="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 font-semibold"
              >
                View Customer 360 →
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              <div>
                <h3 className="text-lg font-bold text-blue-900 mb-2">
                  ℹ️ No Existing Customer Found
                </h3>
                <p className="text-blue-800 mb-4">
                  This appears to be a new customer. Let's create their profile.
                </p>
              </div>

              <button
                onClick={handleNewCustomer}
                className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold"
              >
                Create New Prospect →
              </button>
            </div>
          )}
        </div>
      )}

      {/* Info Box */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="font-semibold text-blue-900 mb-2">🔍 Search Tips</h4>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• Enter any one or combination of identifiers</li>
          <li>• Mobile number has highest match probability</li>
          <li>• PAN search is exact match only</li>
          <li>• Fuzzy matching available for close matches</li>
        </ul>
      </div>
    </div>
  );
}
