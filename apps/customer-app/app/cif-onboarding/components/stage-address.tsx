'use client';

import { useCIFStore } from '@/lib/cif-store';
import { cifApi } from '@/lib/cif-api';
import { useState } from 'react';

interface StageAddressProps {
  onNext: () => void;
}

export default function StageAddress({ onNext }: StageAddressProps) {
  const { customerId, address, updateAddress, setLoading, setError, markStageComplete } =
    useCIFStore();
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!customerId || !address.street || !address.city) {
      setError('Please fill required fields');
      return;
    }

    setLoading(true);
    try {
      await cifApi.addAddress(customerId, {
        address_type: address.type || 'permanent',
        street_address: address.street || '',
        city: address.city || '',
        state: address.state || '',
        postal_code: address.postalCode || '',
        country: address.country || 'India',
      });

      markStageComplete(5);
      setSubmitted(true);
      setTimeout(onNext, 1000);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (submitted) {
    return (
      <div className="text-center py-12">
        <div className="text-5xl mb-4">✅</div>
        <h2 className="text-2xl font-bold text-slate-900">Address Saved!</h2>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 mb-2">Stage 5: Address</h2>
        <p className="text-slate-600">Enter residential address information.</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Address Type
          </label>
          <select
            value={address.type || 'permanent'}
            onChange={(e) => updateAddress({ type: e.target.value })}
            className="w-full px-4 py-2 border border-slate-300 rounded-lg"
          >
            <option value="permanent">Permanent</option>
            <option value="communication">Communication</option>
            <option value="office">Office</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Street Address *
          </label>
          <input
            type="text"
            required
            value={address.street || ''}
            onChange={(e) => updateAddress({ street: e.target.value })}
            className="w-full px-4 py-2 border border-slate-300 rounded-lg"
            placeholder="123 Main Street"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              City *
            </label>
            <input
              type="text"
              required
              value={address.city || ''}
              onChange={(e) => updateAddress({ city: e.target.value })}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg"
              placeholder="Mumbai"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              State
            </label>
            <input
              type="text"
              value={address.state || ''}
              onChange={(e) => updateAddress({ state: e.target.value })}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg"
              placeholder="Maharashtra"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Postal Code
            </label>
            <input
              type="text"
              value={address.postalCode || ''}
              onChange={(e) => updateAddress({ postalCode: e.target.value })}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg"
              placeholder="400001"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Country
            </label>
            <input
              type="text"
              value={address.country || 'India'}
              onChange={(e) => updateAddress({ country: e.target.value })}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg"
              placeholder="India"
            />
          </div>
        </div>

        <button
          type="submit"
          className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold"
        >
          📍 Save Address
        </button>
      </form>
    </div>
  );
}
