'use client';

import { useCIFStore } from '@/lib/cif-store';
import { cifApi } from '@/lib/cif-api';
import { useState } from 'react';

interface StageContactProps {
  onNext: () => void;
}

export default function StageContact({ onNext }: StageContactProps) {
  const { customerId, contact, updateContact, setLoading, setError, markStageComplete } =
    useCIFStore();
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!customerId) {
      setError('No customer selected');
      return;
    }

    setLoading(true);
    try {
      await cifApi.addContact(customerId, {
        phone: contact.phone || '',
        email: contact.email || '',
        whatsapp: contact.whatsapp,
        preferred_language: contact.preferredLanguage || 'English',
      });

      markStageComplete(6);
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
        <h2 className="text-2xl font-bold text-slate-900">Contact Saved!</h2>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 mb-2">Stage 6: Contact Information</h2>
        <p className="text-slate-600">Enter communication preferences and contact details.</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Primary Phone
          </label>
          <input
            type="tel"
            value={contact.phone || ''}
            onChange={(e) => updateContact({ phone: e.target.value })}
            className="w-full px-4 py-2 border border-slate-300 rounded-lg"
            placeholder="9876543210"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Email Address
          </label>
          <input
            type="email"
            value={contact.email || ''}
            onChange={(e) => updateContact({ email: e.target.value })}
            className="w-full px-4 py-2 border border-slate-300 rounded-lg"
            placeholder="customer@example.com"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            WhatsApp Number
          </label>
          <input
            type="tel"
            value={contact.whatsapp || ''}
            onChange={(e) => updateContact({ whatsapp: e.target.value })}
            className="w-full px-4 py-2 border border-slate-300 rounded-lg"
            placeholder="9876543210"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Preferred Language
          </label>
          <select
            value={contact.preferredLanguage || 'English'}
            onChange={(e) => updateContact({ preferredLanguage: e.target.value })}
            className="w-full px-4 py-2 border border-slate-300 rounded-lg"
          >
            <option value="English">English</option>
            <option value="Hindi">Hindi</option>
            <option value="Marathi">Marathi</option>
            <option value="Tamil">Tamil</option>
            <option value="Telugu">Telugu</option>
          </select>
        </div>

        <button
          type="submit"
          className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold"
        >
          📞 Save Contact Info
        </button>
      </form>
    </div>
  );
}
