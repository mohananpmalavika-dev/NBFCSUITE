'use client';

import { useEffect, useState } from 'react';
import { useCIFStore } from '@/lib/cif-store';
import { cifApi } from '@/lib/cif-api';
import Link from 'next/link';

export default function Customer360() {
  const { customerId, cifId, setError } = useCIFStore();
  const [customer360, setCustomer360] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    if (customerId || cifId) {
      loadCustomer360();
    }
  }, [customerId, cifId]);

  const loadCustomer360 = async () => {
    try {
      setLoading(true);
      const id = customerId || 'demo-customer-123';
      const data = await cifApi.getCustomer360(id);
      setCustomer360(data);
      setError(null);
    } catch (err: any) {
      // For demo, show mock data if API fails
      setCustomer360({
        customer_id: customerId,
        cif_id: cifId || 'CIF0000001245',
        status: 'ACTIVE',
        basic_details: {
          first_name: 'John',
          last_name: 'Doe',
          date_of_birth: '1990-01-15',
          gender: 'M',
          occupation: 'IT Professional',
        },
        addresses: [
          {
            type: 'permanent',
            street: '123 Main Street',
            city: 'Mumbai',
            state: 'Maharashtra',
            postal_code: '400001',
          },
        ],
        contacts: {
          phone: '9876543210',
          email: 'john@example.com',
          whatsapp: '9876543210',
        },
        compliance: {
          pan_verified: true,
          aadhar_verified: true,
          aml_passed: true,
        },
        behavior_profile: {
          fin_dna: 'Conservative-Stable-High-Trust',
          risk_appetite: 'Moderate',
          product_affinity: {
            'Gold Loan': 85,
            'Fixed Deposit': 75,
            'Savings Account': 95,
            'Personal Loan': 45,
          },
        },
      });
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin h-12 w-12 border-4 border-blue-500 border-t-transparent rounded-full mb-4"></div>
          <p className="text-slate-600">Loading Customer 360...</p>
        </div>
      </div>
    );
  }

  if (!customer360) {
    return (
      <div className="min-h-screen bg-slate-50 px-4 py-8">
        <div className="max-w-6xl mx-auto">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
            <p className="text-red-700 font-semibold mb-2">No Customer Data</p>
            <p className="text-red-600 mb-4">
              Please complete CIF onboarding first to view Customer 360.
            </p>
            <Link
              href="/cif-onboarding"
              className="inline-block px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold"
            >
              Start CIF Onboarding
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <main className="min-h-screen bg-gradient-to-b from-blue-50 to-slate-50 px-4 py-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-4xl font-bold text-slate-900">Customer 360</h1>
              <p className="text-slate-600 mt-2">Complete customer view across all products</p>
            </div>
            <Link
              href="/"
              className="px-4 py-2 bg-slate-600 text-white rounded-lg hover:bg-slate-700 font-semibold"
            >
              ← Back to Home
            </Link>
          </div>

          {/* CIF Card */}
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg p-6 shadow-lg">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <p className="text-sm opacity-90">CIF ID</p>
                <p className="text-2xl font-bold">{customer360.cif_id}</p>
              </div>
              <div>
                <p className="text-sm opacity-90">Customer Status</p>
                <p className="text-2xl font-bold">{customer360.status}</p>
              </div>
              <div>
                <p className="text-sm opacity-90">FinDNA Score</p>
                <p className="text-2xl font-bold">{customer360.behavior_profile?.fin_dna}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="mb-6 border-b border-slate-200 bg-white rounded-t-lg">
          <div className="flex gap-0">
            {[
              { id: 'overview', label: '📊 Overview' },
              { id: 'personal', label: '👤 Personal Details' },
              { id: 'compliance', label: '✅ Compliance' },
              { id: 'behavior', label: '🧠 Behavior & Products' },
              { id: 'documents', label: '📦 Documents' },
              { id: 'products', label: '💼 Products' },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-6 py-3 border-b-2 font-semibold transition-all ${
                  activeTab === tab.id
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-slate-600 hover:text-slate-900'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Content */}
        <div className="bg-white rounded-b-lg shadow-sm border border-slate-200 p-8">
          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Personal Summary */}
                <div className="bg-slate-50 rounded-lg p-6">
                  <h3 className="font-bold text-slate-900 mb-4">👤 Personal Information</h3>
                  <div className="space-y-2 text-sm">
                    <p>
                      <span className="text-slate-600">Name:</span>{' '}
                      <span className="font-semibold">
                        {customer360.basic_details?.first_name} {customer360.basic_details?.last_name}
                      </span>
                    </p>
                    <p>
                      <span className="text-slate-600">Occupation:</span>{' '}
                      <span className="font-semibold">{customer360.basic_details?.occupation}</span>
                    </p>
                    <p>
                      <span className="text-slate-600">Gender:</span>{' '}
                      <span className="font-semibold">{customer360.basic_details?.gender}</span>
                    </p>
                    <p>
                      <span className="text-slate-600">DOB:</span>{' '}
                      <span className="font-semibold">{customer360.basic_details?.date_of_birth}</span>
                    </p>
                  </div>
                </div>

                {/* Contact Summary */}
                <div className="bg-slate-50 rounded-lg p-6">
                  <h3 className="font-bold text-slate-900 mb-4">📞 Contact Information</h3>
                  <div className="space-y-2 text-sm">
                    <p>
                      <span className="text-slate-600">Phone:</span>{' '}
                      <span className="font-semibold">{customer360.contacts?.phone}</span>
                    </p>
                    <p>
                      <span className="text-slate-600">Email:</span>{' '}
                      <span className="font-semibold">{customer360.contacts?.email}</span>
                    </p>
                    <p>
                      <span className="text-slate-600">WhatsApp:</span>{' '}
                      <span className="font-semibold">{customer360.contacts?.whatsapp}</span>
                    </p>
                  </div>
                </div>

                {/* Address Summary */}
                <div className="bg-slate-50 rounded-lg p-6">
                  <h3 className="font-bold text-slate-900 mb-4">📍 Address</h3>
                  {customer360.addresses?.[0] && (
                    <div className="text-sm">
                      <p className="font-semibold">
                        {customer360.addresses[0].street}
                      </p>
                      <p className="text-slate-600">
                        {customer360.addresses[0].city}, {customer360.addresses[0].state}
                      </p>
                      <p className="text-slate-600">
                        {customer360.addresses[0].postal_code}
                      </p>
                    </div>
                  )}
                </div>

                {/* Compliance Summary */}
                <div className="bg-green-50 rounded-lg p-6 border border-green-200">
                  <h3 className="font-bold text-green-900 mb-4">✅ Compliance Status</h3>
                  <div className="space-y-2 text-sm">
                    <p>
                      PAN Verified:{' '}
                      <span className="font-semibold text-green-700">
                        {customer360.compliance?.pan_verified ? '✓ Yes' : '✗ No'}
                      </span>
                    </p>
                    <p>
                      Aadhar Verified:{' '}
                      <span className="font-semibold text-green-700">
                        {customer360.compliance?.aadhar_verified ? '✓ Yes' : '✗ No'}
                      </span>
                    </p>
                    <p>
                      AML Check:{' '}
                      <span className="font-semibold text-green-700">
                        {customer360.compliance?.aml_passed ? '✓ Passed' : '✗ Failed'}
                      </span>
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Personal Tab */}
          {activeTab === 'personal' && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-slate-50 p-4 rounded-lg">
                  <p className="text-slate-600 text-sm">Full Name</p>
                  <p className="font-bold text-slate-900">
                    {customer360.basic_details?.first_name} {customer360.basic_details?.last_name}
                  </p>
                </div>
                <div className="bg-slate-50 p-4 rounded-lg">
                  <p className="text-slate-600 text-sm">Date of Birth</p>
                  <p className="font-bold text-slate-900">{customer360.basic_details?.date_of_birth}</p>
                </div>
                <div className="bg-slate-50 p-4 rounded-lg">
                  <p className="text-slate-600 text-sm">Gender</p>
                  <p className="font-bold text-slate-900">{customer360.basic_details?.gender}</p>
                </div>
                <div className="bg-slate-50 p-4 rounded-lg">
                  <p className="text-slate-600 text-sm">Occupation</p>
                  <p className="font-bold text-slate-900">{customer360.basic_details?.occupation}</p>
                </div>
              </div>
            </div>
          )}

          {/* Compliance Tab */}
          {activeTab === 'compliance' && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {[
                  {
                    name: 'PAN Verification',
                    status: customer360.compliance?.pan_verified,
                  },
                  {
                    name: 'Aadhar Verification',
                    status: customer360.compliance?.aadhar_verified,
                  },
                  {
                    name: 'AML Check',
                    status: customer360.compliance?.aml_passed,
                  },
                ].map((check) => (
                  <div
                    key={check.name}
                    className={`p-4 rounded-lg border-2 ${
                      check.status
                        ? 'bg-green-50 border-green-200'
                        : 'bg-red-50 border-red-200'
                    }`}
                  >
                    <p className={`font-semibold ${check.status ? 'text-green-900' : 'text-red-900'}`}>
                      {check.status ? '✓' : '✗'} {check.name}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Behavior & Products Tab */}
          {activeTab === 'behavior' && (
            <div className="space-y-6">
              <div className="bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-lg p-6">
                <h3 className="font-bold text-purple-900 mb-2">🧠 FinDNA Profile</h3>
                <p className="text-2xl font-bold text-purple-600 mb-4">
                  {customer360.behavior_profile?.fin_dna}
                </p>
                <p className="text-purple-800">
                  Risk Appetite: <span className="font-semibold">{customer360.behavior_profile?.risk_appetite}</span>
                </p>
              </div>

              <div>
                <h3 className="font-bold text-slate-900 mb-4">📊 Recommended Products</h3>
                <div className="space-y-3">
                  {Object.entries(customer360.behavior_profile?.product_affinity || {})
                    .sort(([, a]: any, [, b]: any) => b - a)
                    .map(([product, affinity]: any) => (
                      <div key={product} className="flex items-center justify-between">
                        <span className="font-semibold text-slate-900">{product}</span>
                        <div className="flex items-center gap-3">
                          <div className="w-40 h-3 bg-slate-200 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-blue-600 rounded-full"
                              style={{ width: `${affinity}%` }}
                            ></div>
                          </div>
                          <span className="font-bold text-slate-900 w-12 text-right">{affinity}%</span>
                        </div>
                      </div>
                    ))}
                </div>
              </div>
            </div>
          )}

          {/* Documents Tab */}
          {activeTab === 'documents' && (
            <div className="text-center py-12">
              <p className="text-slate-600">No documents available yet</p>
              <Link href="/documents" className="text-blue-600 hover:underline font-semibold">
                View all documents →
              </Link>
            </div>
          )}

          {/* Products Tab */}
          {activeTab === 'products' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {[
                { name: 'Gold Loan', icon: '💰', href: '/loans' },
                { name: 'Fixed Deposit', icon: '📈', href: '/deposits' },
                { name: 'Personal Loan', icon: '💳', href: '/loans' },
                { name: 'Forex Account', icon: '💵', href: '/' },
              ].map((product) => (
                <Link
                  key={product.name}
                  href={product.href}
                  className="bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 rounded-lg p-6 hover:shadow-lg transition"
                >
                  <span className="text-3xl">{product.icon}</span>
                  <p className="font-bold text-slate-900 mt-2">{product.name}</p>
                  <p className="text-sm text-slate-600 mt-1">Apply now →</p>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
