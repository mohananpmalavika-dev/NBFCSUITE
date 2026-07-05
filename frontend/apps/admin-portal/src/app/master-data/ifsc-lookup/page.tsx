"use client";

import { useState } from "react";
import { Search, MapPin, Building2, Phone, Mail } from "lucide-react";

interface BranchDetails {
  id: number;
  bank_name: string;
  branch_name: string;
  ifsc_code: string;
  micr_code?: string;
  address?: string;
  city_name?: string;
  state_name?: string;
  pincode?: string;
  phone?: string;
  email?: string;
  is_active: boolean;
}

export default function IFSCLookupPage() {
  const [ifscCode, setIfscCode] = useState("");
  const [loading, setLoading] = useState(false);
  const [branchDetails, setBranchDetails] = useState<BranchDetails | null>(null);
  const [error, setError] = useState<string>("");

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!ifscCode || ifscCode.length !== 11) {
      setError("Please enter a valid 11-character IFSC code");
      return;
    }

    setLoading(true);
    setError("");
    setBranchDetails(null);

    try {
      const response = await fetch(
        `/api/v1/masterdata/bank-branches/ifsc/${ifscCode.toUpperCase()}`,
        {
          headers: { "Content-Type": "application/json" }
        }
      );

      if (!response.ok) {
        throw new Error("IFSC code not found");
      }

      const result = await response.json();
      setBranchDetails(result);
    } catch (err) {
      setError("IFSC code not found in our database. Please verify and try again.");
      setBranchDetails(null);
    } finally {
      setLoading(false);
    }
  };

  const formatIFSC = (value: string) => {
    return value.toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 11);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-teal-600 to-teal-700 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-white/20 rounded-full mb-4">
              <Search className="w-8 h-8" />
            </div>
            <h1 className="text-3xl font-bold mb-2">IFSC Code Lookup</h1>
            <p className="text-teal-100">
              Search for bank branch details using IFSC code
            </p>
          </div>
        </div>
      </div>

      {/* Search Section */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <form onSubmit={handleSearch} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Enter IFSC Code
              </label>
              <div className="flex gap-3">
                <input
                  type="text"
                  value={ifscCode}
                  onChange={(e) => setIfscCode(formatIFSC(e.target.value))}
                  placeholder="e.g., SBIN0000123"
                  className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent font-mono text-lg uppercase"
                  maxLength={11}
                />
                <button
                  type="submit"
                  disabled={loading || ifscCode.length !== 11}
                  className="px-8 py-3 bg-teal-600 text-white rounded-lg hover:bg-teal-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 font-medium"
                >
                  {loading ? (
                    <>
                      <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      Searching...
                    </>
                  ) : (
                    <>
                      <Search className="w-5 h-5" />
                      Search
                    </>
                  )}
                </button>
              </div>
              <p className="text-xs text-gray-500 mt-2">
                IFSC code is 11 characters (e.g., first 4 letters for bank code, 5th character is 0, last 6 characters for branch code)
              </p>
            </div>

            {error && (
              <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-sm text-red-700">{error}</p>
              </div>
            )}
          </form>
        </div>

        {/* Results Section */}
        {branchDetails && (
          <div className="mt-6 bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
            {/* Header */}
            <div className="bg-gradient-to-r from-teal-50 to-teal-100 px-6 py-4 border-b">
              <h2 className="text-xl font-bold text-teal-900">Branch Details</h2>
              <p className="text-sm text-teal-700 mt-1">
                Complete information for IFSC: <span className="font-mono font-bold">{branchDetails.ifsc_code}</span>
              </p>
            </div>

            {/* Content */}
            <div className="p-6 space-y-6">
              {/* Bank & Branch Info */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <div className="flex items-start gap-3">
                    <div className="w-10 h-10 bg-teal-100 rounded-lg flex items-center justify-center flex-shrink-0">
                      <Building2 className="w-5 h-5 text-teal-600" />
                    </div>
                    <div>
                      <p className="text-xs text-gray-500 uppercase tracking-wide">Bank Name</p>
                      <p className="text-lg font-semibold text-gray-900 mt-1">{branchDetails.bank_name}</p>
                    </div>
                  </div>
                </div>

                <div>
                  <div className="flex items-start gap-3">
                    <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                      <Building2 className="w-5 h-5 text-blue-600" />
                    </div>
                    <div>
                      <p className="text-xs text-gray-500 uppercase tracking-wide">Branch Name</p>
                      <p className="text-lg font-semibold text-gray-900 mt-1">{branchDetails.branch_name}</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Codes */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="p-4 bg-gray-50 rounded-lg">
                  <p className="text-xs text-gray-500 uppercase tracking-wide mb-2">IFSC Code</p>
                  <p className="text-2xl font-mono font-bold text-green-600">{branchDetails.ifsc_code}</p>
                </div>

                {branchDetails.micr_code && (
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <p className="text-xs text-gray-500 uppercase tracking-wide mb-2">MICR Code</p>
                    <p className="text-2xl font-mono font-bold text-purple-600">{branchDetails.micr_code}</p>
                  </div>
                )}
              </div>

              {/* Address */}
              {branchDetails.address && (
                <div>
                  <div className="flex items-start gap-3">
                    <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center flex-shrink-0">
                      <MapPin className="w-5 h-5 text-orange-600" />
                    </div>
                    <div className="flex-1">
                      <p className="text-xs text-gray-500 uppercase tracking-wide">Address</p>
                      <p className="text-sm text-gray-900 mt-1 leading-relaxed">{branchDetails.address}</p>
                      <div className="flex gap-4 mt-2 text-sm text-gray-600">
                        {branchDetails.city_name && <span>{branchDetails.city_name}</span>}
                        {branchDetails.state_name && <span>{branchDetails.state_name}</span>}
                        {branchDetails.pincode && <span className="font-mono">PIN: {branchDetails.pincode}</span>}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Contact */}
              {(branchDetails.phone || branchDetails.email) && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {branchDetails.phone && (
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                        <Phone className="w-5 h-5 text-blue-600" />
                      </div>
                      <div>
                        <p className="text-xs text-gray-500 uppercase tracking-wide">Phone</p>
                        <p className="text-sm font-medium text-gray-900 mt-1">{branchDetails.phone}</p>
                      </div>
                    </div>
                  )}

                  {branchDetails.email && (
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center flex-shrink-0">
                        <Mail className="w-5 h-5 text-purple-600" />
                      </div>
                      <div>
                        <p className="text-xs text-gray-500 uppercase tracking-wide">Email</p>
                        <p className="text-sm font-medium text-gray-900 mt-1">{branchDetails.email}</p>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Status */}
              <div className="pt-4 border-t">
                <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                  branchDetails.is_active 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-red-100 text-red-800'
                }`}>
                  {branchDetails.is_active ? '✓ Active Branch' : '✗ Inactive Branch'}
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Info Box */}
        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex gap-3">
            <div className="flex-shrink-0">
              <svg className="w-5 h-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <h3 className="text-sm font-medium text-blue-900">About IFSC Codes</h3>
              <p className="mt-1 text-sm text-blue-700">
                IFSC (Indian Financial System Code) is an 11-character alphanumeric code used for electronic fund transfers in India. 
                It uniquely identifies each bank branch participating in NEFT, RTGS, and IMPS payment systems.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
