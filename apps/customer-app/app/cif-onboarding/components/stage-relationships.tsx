'use client';

import { useCIFStore } from '@/lib/cif-store';
import { cifApi } from '@/lib/cif-api';
import { useEffect, useState } from 'react';

interface StageRelationshipsProps {
  onNext: () => void;
}

export default function StageRelationships({ onNext }: StageRelationshipsProps) {
  const { customerId, markStageComplete } = useCIFStore();
  const [selectedView, setSelectedView] = useState<'network' | 'accounts' | 'transactions'>(
    'network'
  );
  const [networkData, setNetworkData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadNetwork = async () => {
      if (!customerId) return;
      setLoading(true);
      try {
        const response = await cifApi.getRelationshipNetwork(customerId);
        setNetworkData(response.network || {});
      } catch (err: any) {
        setError(err.message || 'Unable to load relationship network');
      } finally {
        setLoading(false);
      }
    };

    loadNetwork();
  }, [customerId]);

  const handleContinue = () => {
    markStageComplete(14);
    onNext();
  };

  // Mock relationship data
  const relationshipNetwork = {
    name: 'John Doe',
    accounts: ['Current A/C', 'Savings A/C', 'Gold Loan'],
    contacts: [
      { name: 'Priya Doe', relationship: 'Spouse', accounts: 2 },
      { name: 'Raj Kumar', relationship: 'Employer', accounts: 1 },
      { name: 'Bank of India', relationship: 'External', accounts: 1 },
    ],
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 mb-2">
          Stage 14: Relationship Mapping
        </h2>
        <p className="text-slate-600">
          Map relationships across accounts and entities for integrated customer view.
        </p>
      </div>

      {/* View Tabs */}
      <div className="flex gap-2 border-b border-slate-200">
        {[
          { id: 'network', label: '🔗 Relationship Network' },
          { id: 'accounts', label: '💳 Linked Accounts' },
          { id: 'transactions', label: '💰 Transaction Network' },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setSelectedView(tab.id as any)}
            className={`px-4 py-2 border-b-2 font-medium transition ${
              selectedView === tab.id
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-slate-600 hover:text-slate-900'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Network View */}
      {selectedView === 'network' && (
        <div className="bg-gradient-to-br from-blue-50 to-purple-50 border border-blue-200 rounded-lg p-8">
          <h3 className="font-bold text-slate-900 mb-6">Network Visualization</h3>

          {loading ? (
            <div className="text-center py-8">
              <div className="inline-block animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full mb-4"></div>
              <p className="text-slate-600">Loading network...</p>
            </div>
          ) : error ? (
            <div className="text-center text-red-600 py-8">{error}</div>
          ) : (
            <>
              <div className="flex justify-center mb-8">
                <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-full p-6 shadow-lg w-32 h-32 flex items-center justify-center text-center">
                  <div>
                    <p className="text-sm opacity-80">Customer</p>
                    <p className="font-bold">Relationship Map</p>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {(networkData?.primary || []).map((contact: any, idx: number) => (
                  <div
                    key={idx}
                    className="bg-white border-2 border-blue-300 rounded-lg p-4 text-center hover:shadow-lg transition"
                  >
                    <div className="text-3xl mb-2">👤</div>
                    <p className="font-semibold text-slate-900">{contact.name}</p>
                    <p className="text-xs text-slate-600 mb-2">{contact.relationship}</p>
                    <p className="text-sm font-medium text-blue-600">{contact.cif || 'No CIF'}</p>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      )}

      {/* Accounts View */}
      {selectedView === 'accounts' && (
        <div className="space-y-4">
          <div className="bg-white border border-slate-200 rounded-lg p-6">
            <h3 className="font-bold text-slate-900 mb-4">Customer Accounts</h3>
            <div className="space-y-3">
              {relationshipNetwork.accounts.map((account, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-4 bg-slate-50 rounded-lg"
                >
                  <div>
                    <p className="font-semibold text-slate-900">{account}</p>
                    <p className="text-xs text-slate-600">Active</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-blue-600 font-medium">View →</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Transactions View */}
      {selectedView === 'transactions' && (
        <div className="bg-white border border-slate-200 rounded-lg p-6">
          <h3 className="font-bold text-slate-900 mb-4">Transaction Network</h3>
          <p className="text-slate-600 text-sm mb-4">
            Shows flow of funds between linked accounts and relationships
          </p>

          <div className="space-y-4">
            {[
              {
                from: 'Current A/C',
                to: 'Employer (Salary)',
                amount: '₹50,000',
                frequency: 'Monthly',
              },
              { from: 'Savings A/C', to: 'Online Shopping', amount: '₹12,500', frequency: 'Variable' },
              {
                from: 'Gold Loan A/C',
                to: 'Household',
                amount: '₹8,000',
                frequency: 'Monthly EMI',
              },
            ].map((tx, idx) => (
              <div key={idx} className="flex items-center justify-between p-4 bg-slate-50 rounded-lg">
                <div className="flex-1">
                  <p className="font-semibold text-slate-900">{tx.from}</p>
                  <p className="text-xs text-slate-600">→ {tx.to}</p>
                </div>
                <div className="text-right">
                  <p className="font-bold text-slate-900">{tx.amount}</p>
                  <p className="text-xs text-slate-600">{tx.frequency}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Summary Info */}
      <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
        <h4 className="font-semibold text-purple-900 mb-2">📊 Relationship Summary</h4>
        <ul className="text-sm text-purple-800 space-y-1">
          <li>✓ {relationshipNetwork.contacts.length} Primary relationships mapped</li>
          <li>✓ {relationshipNetwork.accounts.length} Accounts linked</li>
          <li>✓ Cross-account transaction patterns identified</li>
          <li>✓ Risk profile updated based on network analysis</li>
        </ul>
      </div>

      <button
        onClick={handleContinue}
        className="w-full px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 font-semibold"
      >
        ✅ Continue to Compliance Check
      </button>
    </div>
  );
}
