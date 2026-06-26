'use client';

import { useAuth } from '@/lib/auth-context';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api';

interface CustomerProfile {
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  pan: string;
  aadhar: string;
}

interface FinancialProfile {
  annual_income: string;
  employment_type: string;
  employer: string;
  occupation: string;
  assets: any;
  liabilities: any;
  credit_score: number;
}

export default function ProfilePage() {
  const { user, token, logout, isLoading: authLoading } = useAuth();
  const router = useRouter();
  const [isEditing, setIsEditing] = useState(false);
  const [customer, setCustomer] = useState<CustomerProfile | null>(null);
  const [financialProfile, setFinancialProfile] = useState<FinancialProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!authLoading && !token) {
      router.push('/login');
    }
  }, [token, authLoading, router]);

  useEffect(() => {
    if (user && token) {
      const fetchData = async () => {
        try {
          const [customerRes, financialRes] = await Promise.all([
            apiClient.getCustomer(user.id),
            apiClient.getFinancialProfile(user.id),
          ]);
          setCustomer(customerRes.data);
          setFinancialProfile(financialRes.data);
        } catch (error) {
          console.error('Failed to fetch profile data:', error);
        } finally {
          setIsLoading(false);
        }
      };
      fetchData();
    }
  }, [user, token]);

  const handleSave = async () => {
    if (!user || !customer || !financialProfile) return;

    try {
      await Promise.all([
        apiClient.updateCustomer(user.id, customer),
        apiClient.updateFinancialProfile(user.id, financialProfile),
      ]);
      alert('Profile updated successfully');
      setIsEditing(false);
    } catch (error) {
      console.error('Failed to update profile:', error);
      alert('Failed to update profile');
    }
  };

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  if (authLoading || isLoading) {
    return <div className="p-8 text-center">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900">My Profile</h1>
          <p className="text-gray-600 mt-2">Manage your account and financial information</p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-8">
          <div className="flex items-center mb-8">
            <div className="w-24 h-24 bg-blue-500 rounded-full flex items-center justify-center">
              <span className="text-4xl font-bold text-white">
                {customer?.firstName?.[0]}
                {customer?.lastName?.[0]}
              </span>
            </div>
            <div className="ml-6">
              <h2 className="text-2xl font-bold">{`${customer?.firstName} ${customer?.lastName}`}</h2>
              <p className="text-gray-600">{customer?.email}</p>
            </div>
          </div>

          {isEditing ? (
            <EditProfileForm
              customer={customer}
              setCustomer={setCustomer}
              financialProfile={financialProfile}
              setFinancialProfile={setFinancialProfile}
              handleSave={handleSave}
              setIsEditing={setIsEditing}
            />
          ) : (
            <ViewProfile
              customer={customer}
              financialProfile={financialProfile}
              setIsEditing={setIsEditing}
              handleLogout={handleLogout}
            />
          )}
        </div>
      </div>
    </div>
  );
}

// ... (imports and main component)

function ViewProfile({ customer, financialProfile, setIsEditing, handleLogout }) {
  return (
    <div className="space-y-8">
      {/* Personal Information */}
      <div>
        <h3 className="text-xl font-semibold text-gray-900 mb-4">Personal Information</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <InfoItem label="First Name" value={customer?.firstName} />
          <InfoItem label="Last Name" value={customer?.lastName} />
          <InfoItem label="Email" value={customer?.email} />
          <InfoItem label="Phone" value={customer?.phone} />
          <InfoItem label="PAN" value={customer?.pan} />
          <InfoItem label="Aadhar" value={customer?.aadhar} />
        </div>
      </div>

      {/* Financial Profile */}
      <div>
        <h3 className="text-xl font-semibold text-gray-900 mb-4">Financial Profile</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <InfoItem label="Annual Income" value={financialProfile?.annual_income} />
          <InfoItem label="Employment Type" value={financialProfile?.employment_type} />
          <InfoItem label="Employer" value={financialProfile?.employer} />
          <InfoItem label="Occupation" value={financialProfile?.occupation} />
          <InfoItem label="Credit Score" value={financialProfile?.credit_score} />
        </div>
      </div>

      {/* Assets and Liabilities */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Assets</h3>
          <pre className="bg-gray-100 p-4 rounded-lg">{JSON.stringify(financialProfile?.assets, null, 2)}</pre>
        </div>
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Liabilities</h3>
          <pre className="bg-gray-100 p-4 rounded-lg">{JSON.stringify(financialProfile?.liabilities, null, 2)}</pre>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex space-x-4 pt-6 border-t">
        <button
          onClick={() => setIsEditing(true)}
          className="flex-1 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 font-medium"
        >
          Edit Profile
        </button>
        <button
          onClick={handleLogout}
          className="flex-1 bg-red-600 text-white py-2 rounded-lg hover:bg-red-700 font-medium"
        >
          Logout
        </button>
      </div>
    </div>
  );
}

function EditProfileForm({ customer, setCustomer, financialProfile, setFinancialProfile, handleSave, setIsEditing }) {
  const handleCustomerChange = (e) => {
    setCustomer({ ...customer, [e.target.name]: e.target.value });
  };

  const handleFinancialChange = (e) => {
    setFinancialProfile({ ...financialProfile, [e.target.name]: e.target.value });
  };

  const handleJsonChange = (e, field) => {
    try {
      const parsedJson = JSON.parse(e.target.value);
      setFinancialProfile({ ...financialProfile, [field]: parsedJson });
    } catch (error) {
      // Handle JSON parsing error if needed
      console.error(`Invalid JSON in ${field}:`, e.target.value);
    }
  };

  return (
    <div className="space-y-8">
      {/* Personal Information Form */}
      <div>
        <h3 className="text-xl font-semibold text-gray-900 mb-4">Edit Personal Information</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <FormInput label="First Name" name="firstName" value={customer?.firstName} onChange={handleCustomerChange} />
          <FormInput label="Last Name" name="lastName" value={customer?.lastName} onChange={handleCustomerChange} />
          <FormInput label="Email" name="email" value={customer?.email} onChange={handleCustomerChange} type="email" />
          <FormInput label="Phone" name="phone" value={customer?.phone} onChange={handleCustomerChange} />
          <FormInput label="PAN" name="pan" value={customer?.pan} onChange={handleCustomerChange} />
          <FormInput label="Aadhar" name="aadhar" value={customer?.aadhar} onChange={handleCustomerChange} />
        </div>
      </div>

      {/* Financial Profile Form */}
      <div>
        <h3 className="text-xl font-semibold text-gray-900 mb-4">Edit Financial Profile</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <FormInput label="Annual Income" name="annual_income" value={financialProfile?.annual_income} onChange={handleFinancialChange} />
          <FormInput label="Employment Type" name="employment_type" value={financialProfile?.employment_type} onChange={handleFinancialChange} />
          <FormInput label="Employer" name="employer" value={financialProfile?.employer} onChange={handleFinancialChange} />
          <FormInput label="Occupation" name="occupation" value={financialProfile?.occupation} onChange={handleFinancialChange} />
          <FormInput label="Credit Score" name="credit_score" value={financialProfile?.credit_score} onChange={handleFinancialChange} type="number" />
        </div>
      </div>

      {/* Assets and Liabilities Form */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Assets (JSON)</h3>
          <textarea
            name="assets"
            rows={6}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            defaultValue={JSON.stringify(financialProfile?.assets, null, 2)}
            onBlur={(e) => handleJsonChange(e, 'assets')}
          />
        </div>
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Liabilities (JSON)</h3>
          <textarea
            name="liabilities"
            rows={6}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            defaultValue={JSON.stringify(financialProfile?.liabilities, null, 2)}
            onBlur={(e) => handleJsonChange(e, 'liabilities')}
          />
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex space-x-4 pt-6 border-t">
        <button
          onClick={handleSave}
          className="flex-1 bg-green-600 text-white py-2 rounded-lg hover:bg-green-700 font-medium"
        >
          Save Changes
        </button>
        <button
          onClick={() => setIsEditing(false)}
          className="flex-1 bg-gray-400 text-white py-2 rounded-lg hover:bg-gray-500 font-medium"
        >
          Cancel
        </button>
      </div>
    </div>
  );
}

function FormInput({ label, name, value, onChange, type = 'text' }) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-2">{label}</label>
      <input
        type={type}
        name={name}
        value={value || ''}
        onChange={onChange}
        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
    </div>
  );
}


function InfoItem({ label, value }) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700">{label}</label>
      <p className="mt-1 text-lg text-gray-900">{value || 'Not provided'}</p>
    </div>
  );
}