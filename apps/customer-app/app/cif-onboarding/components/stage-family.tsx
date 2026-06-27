'use client';

import { useCIFStore } from '@/lib/cif-store';
import { useState } from 'react';

interface StageFamilyProps {
  onNext: () => void;
}

export default function StageFamily({ onNext }: StageFamilyProps) {
  const { familyMembers, addFamilyMember, removeFamilyMember, markStageComplete } =
    useCIFStore();
  const [newMember, setNewMember] = useState({
    name: '',
    relationship: 'spouse',
    dependents: false,
  });

  const handleAddMember = () => {
    if (newMember.name && newMember.relationship) {
      addFamilyMember(newMember);
      setNewMember({ name: '', relationship: 'spouse', dependents: false });
    }
  };

  const handleNext = () => {
    markStageComplete(7);
    onNext();
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 mb-2">Stage 7: Family Members</h2>
        <p className="text-slate-600">
          Add family members and dependents for risk assessment and beneficiary tracking.
        </p>
      </div>

      <div className="border border-slate-300 rounded-lg p-6 space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">Member Name</label>
          <input
            type="text"
            value={newMember.name}
            onChange={(e) => setNewMember({ ...newMember, name: e.target.value })}
            className="w-full px-4 py-2 border border-slate-300 rounded-lg"
            placeholder="e.g., Priya Doe"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">Relationship</label>
          <select
            value={newMember.relationship}
            onChange={(e) => setNewMember({ ...newMember, relationship: e.target.value })}
            className="w-full px-4 py-2 border border-slate-300 rounded-lg"
          >
            <option value="spouse">Spouse</option>
            <option value="child">Child</option>
            <option value="parent">Parent</option>
            <option value="sibling">Sibling</option>
            <option value="dependent">Dependent</option>
          </select>
        </div>

        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={newMember.dependents}
            onChange={(e) => setNewMember({ ...newMember, dependents: e.target.checked })}
            className="w-4 h-4"
          />
          <label className="text-sm text-slate-700">Is dependent</label>
        </div>

        <button
          onClick={handleAddMember}
          className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold"
        >
          ➕ Add Family Member
        </button>
      </div>

      {/* Family Members List */}
      {familyMembers && familyMembers.length > 0 && (
        <div>
          <h3 className="font-bold text-slate-900 mb-3">👨‍👩‍👧‍👦 Family Members</h3>
          <div className="space-y-2">
            {familyMembers.map((member: any, index: number) => (
              <div key={index} className="flex items-center justify-between bg-slate-50 p-4 rounded-lg">
                <div>
                  <p className="font-semibold text-slate-900">{member.name}</p>
                  <p className="text-xs text-slate-600">{member.relationship}</p>
                </div>
                <button
                  onClick={() => removeFamilyMember(index)}
                  className="px-3 py-1 bg-red-100 text-red-700 rounded hover:bg-red-200 text-sm"
                >
                  Remove
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {familyMembers && familyMembers.length > 0 && (
        <button
          onClick={handleNext}
          className="w-full px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 font-semibold"
        >
          ✅ Continue
        </button>
      )}

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="font-semibold text-blue-900 mb-2">ℹ️ Family Information</h4>
        <p className="text-sm text-blue-800">
          Adding family members helps us understand your support structure and potential liabilities.
        </p>
      </div>
    </div>
  );
}
