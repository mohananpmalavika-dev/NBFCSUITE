'use client';

import { apiClient } from '@/lib/api';
import { useAuth } from '@/lib/auth-context';
import { useRouter } from 'next/navigation';
import { ChangeEvent, useEffect, useState } from 'react';

interface CustomerProfile {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  kyc_status: string;
  pan?: string | null;
  aadhar?: string | null;
}

interface FinancialProfile {
  annual_income?: string | null;
  employment_type?: string | null;
  employer?: string | null;
  occupation?: string | null;
  assets?: Record<string, unknown> | null;
  liabilities?: Record<string, unknown> | null;
  credit_score?: number | null;
  behavior_score?: string | null;
  risk_level?: string | null;
}

const emptyFinancialProfile: FinancialProfile = {
  annual_income: '',
  employment_type: '',
  employer: '',
  occupation: '',
  assets: {},
  liabilities: {},
  credit_score: null,
  behavior_score: '',
  risk_level: 'medium',
};

export default function ProfilePage() {
  const { user, token, logout, isLoading: authLoading } = useAuth();
  const router = useRouter();
  const [isEditing, setIsEditing] = useState(false);
  const [customer, setCustomer] = useState<CustomerProfile | null>(null);
  const [financialProfile, setFinancialProfile] = useState<FinancialProfile>(emptyFinancialProfile);
  const [assetsText, setAssetsText] = useState('{}');
  const [liabilitiesText, setLiabilitiesText] = useState('{}');
  const [isLoading, setIsLoading] = useState(true);
  const [message, setMessage] = useState('');

  useEffect(() => {
    if (!authLoading && !token) {
      router.push('/login');
    }
  }, [token, authLoading, router]);

  useEffect(() => {
    if (!user || !token) {
      return;
    }

    const fetchData = async () => {
      setIsLoading(true);
      setMessage('');
      try {
        const customerRes = await apiClient.getCustomer(user.id);
        setCustomer(customerRes.data);

        try {
          const financialRes = await apiClient.getFinancialProfile(user.id);
          setFinancialProfile(financialRes.data);
          setAssetsText(JSON.stringify(financialRes.data.assets || {}, null, 2));
          setLiabilitiesText(JSON.stringify(financialRes.data.liabilities || {}, null, 2));
        } catch {
          setFinancialProfile(emptyFinancialProfile);
          setAssetsText('{}');
          setLiabilitiesText('{}');
        }
      } catch {
        setMessage('Profile data is not available for this login yet.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [user, token]);

  const updateCustomerField = (event: ChangeEvent<HTMLInputElement>) => {
    if (!customer) {
      return;
    }
    setCustomer({ ...customer, [event.target.name]: event.target.value });
  };

  const updateFinancialField = (event: ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = event.target;
    setFinancialProfile({
      ...financialProfile,
      [name]: name === 'credit_score' ? Number(value) || null : value,
    });
  };

  const handleSave = async () => {
    if (!user || !customer) {
      return;
    }

    setMessage('');
    try {
      const assets = JSON.parse(assetsText || '{}') as Record<string, unknown>;
      const liabilities = JSON.parse(liabilitiesText || '{}') as Record<string, unknown>;

      await Promise.all([
        apiClient.updateCustomer(user.id, {
          first_name: customer.first_name,
          last_name: customer.last_name,
          email: customer.email,
          phone: customer.phone,
          pan: customer.pan || null,
          aadhar: customer.aadhar || null,
        }),
        apiClient.updateFinancialProfile(user.id, {
          ...financialProfile,
          assets,
          liabilities,
        }),
      ]);
      setFinancialProfile({ ...financialProfile, assets, liabilities });
      setMessage('Profile updated successfully.');
      setIsEditing(false);
    } catch {
      setMessage('Could not save profile. Check JSON fields and try again.');
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
    <main className="min-h-screen bg-slate-50 px-4 py-8">
      <div className="mx-auto max-w-5xl">
        <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <h1 className="text-3xl font-bold text-slate-950">My Profile</h1>
            <p className="mt-1 text-slate-600">Customer identity, KYC status, and risk profile.</p>
          </div>
          <button
            onClick={() => router.push('/')}
            className="rounded-md border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-white"
          >
            Dashboard
          </button>
        </div>

        {message && (
          <div className="mb-4 rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
            {message}
          </div>
        )}

        {!customer ? (
          <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
            No customer record was found for user id {user?.id}.
          </div>
        ) : (
          <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-8 flex items-center gap-4">
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-blue-600 text-xl font-bold text-white">
                {customer.first_name[0]}
                {customer.last_name[0]}
              </div>
              <div>
                <h2 className="text-xl font-semibold text-slate-950">
                  {customer.first_name} {customer.last_name}
                </h2>
                <p className="text-sm text-slate-600">{customer.email}</p>
                <p className="mt-1 text-xs font-semibold uppercase tracking-wide text-blue-700">
                  KYC {customer.kyc_status}
                </p>
              </div>
            </div>

            {isEditing ? (
              <EditProfileForm
                customer={customer}
                financialProfile={financialProfile}
                assetsText={assetsText}
                liabilitiesText={liabilitiesText}
                onCustomerChange={updateCustomerField}
                onFinancialChange={updateFinancialField}
                onAssetsChange={setAssetsText}
                onLiabilitiesChange={setLiabilitiesText}
                onSave={handleSave}
                onCancel={() => setIsEditing(false)}
              />
            ) : (
              <ViewProfile
                customer={customer}
                financialProfile={financialProfile}
                onEdit={() => setIsEditing(true)}
                onLogout={handleLogout}
              />
            )}
          </section>
        )}
      </div>
    </main>
  );
}

function ViewProfile({
  customer,
  financialProfile,
  onEdit,
  onLogout,
}: {
  customer: CustomerProfile;
  financialProfile: FinancialProfile;
  onEdit: () => void;
  onLogout: () => void;
}) {
  return (
    <div className="space-y-8">
      <InfoGrid
        title="Personal Information"
        items={[
          ['First name', customer.first_name],
          ['Last name', customer.last_name],
          ['Email', customer.email],
          ['Phone', customer.phone],
          ['PAN', customer.pan],
          ['Aadhar', customer.aadhar],
        ]}
      />
      <InfoGrid
        title="Financial Profile"
        items={[
          ['Annual income', financialProfile.annual_income],
          ['Employment type', financialProfile.employment_type],
          ['Employer', financialProfile.employer],
          ['Occupation', financialProfile.occupation],
          ['Credit score', financialProfile.credit_score],
          ['Risk level', financialProfile.risk_level],
        ]}
      />
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <JsonPanel title="Assets" value={financialProfile.assets} />
        <JsonPanel title="Liabilities" value={financialProfile.liabilities} />
      </div>
      <div className="flex flex-col gap-3 border-t border-slate-200 pt-6 sm:flex-row">
        <button onClick={onEdit} className="rounded-md bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700">
          Edit Profile
        </button>
        <button onClick={onLogout} className="rounded-md border border-red-200 px-4 py-2 font-medium text-red-700 hover:bg-red-50">
          Logout
        </button>
      </div>
    </div>
  );
}

function EditProfileForm({
  customer,
  financialProfile,
  assetsText,
  liabilitiesText,
  onCustomerChange,
  onFinancialChange,
  onAssetsChange,
  onLiabilitiesChange,
  onSave,
  onCancel,
}: {
  customer: CustomerProfile;
  financialProfile: FinancialProfile;
  assetsText: string;
  liabilitiesText: string;
  onCustomerChange: (event: ChangeEvent<HTMLInputElement>) => void;
  onFinancialChange: (event: ChangeEvent<HTMLInputElement | HTMLSelectElement>) => void;
  onAssetsChange: (value: string) => void;
  onLiabilitiesChange: (value: string) => void;
  onSave: () => void;
  onCancel: () => void;
}) {
  return (
    <div className="space-y-8">
      <div>
        <h3 className="mb-4 text-lg font-semibold text-slate-950">Personal Information</h3>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <FormInput label="First name" name="first_name" value={customer.first_name} onChange={onCustomerChange} />
          <FormInput label="Last name" name="last_name" value={customer.last_name} onChange={onCustomerChange} />
          <FormInput label="Email" name="email" type="email" value={customer.email} onChange={onCustomerChange} />
          <FormInput label="Phone" name="phone" value={customer.phone} onChange={onCustomerChange} />
          <FormInput label="PAN" name="pan" value={customer.pan || ''} onChange={onCustomerChange} />
          <FormInput label="Aadhar" name="aadhar" value={customer.aadhar || ''} onChange={onCustomerChange} />
        </div>
      </div>

      <div>
        <h3 className="mb-4 text-lg font-semibold text-slate-950">Financial Profile</h3>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <FormInput label="Annual income" name="annual_income" value={financialProfile.annual_income || ''} onChange={onFinancialChange} />
          <FormInput label="Employment type" name="employment_type" value={financialProfile.employment_type || ''} onChange={onFinancialChange} />
          <FormInput label="Employer" name="employer" value={financialProfile.employer || ''} onChange={onFinancialChange} />
          <FormInput label="Occupation" name="occupation" value={financialProfile.occupation || ''} onChange={onFinancialChange} />
          <FormInput label="Credit score" name="credit_score" type="number" value={financialProfile.credit_score?.toString() || ''} onChange={onFinancialChange} />
          <label className="block">
            <span className="mb-1 block text-sm font-medium text-slate-700">Risk level</span>
            <select
              name="risk_level"
              value={financialProfile.risk_level || 'medium'}
              onChange={onFinancialChange}
              className="w-full rounded-md border border-slate-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="critical">Critical</option>
            </select>
          </label>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <JsonEditor title="Assets JSON" value={assetsText} onChange={onAssetsChange} />
        <JsonEditor title="Liabilities JSON" value={liabilitiesText} onChange={onLiabilitiesChange} />
      </div>

      <div className="flex flex-col gap-3 border-t border-slate-200 pt-6 sm:flex-row">
        <button onClick={onSave} className="rounded-md bg-emerald-600 px-4 py-2 font-medium text-white hover:bg-emerald-700">
          Save Changes
        </button>
        <button onClick={onCancel} className="rounded-md border border-slate-300 px-4 py-2 font-medium text-slate-700 hover:bg-slate-50">
          Cancel
        </button>
      </div>
    </div>
  );
}

function InfoGrid({ title, items }: { title: string; items: Array<[string, unknown]> }) {
  return (
    <div>
      <h3 className="mb-4 text-lg font-semibold text-slate-950">{title}</h3>
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        {items.map(([label, value]) => (
          <div key={label}>
            <p className="text-sm font-medium text-slate-500">{label}</p>
            <p className="mt-1 text-base text-slate-950">{value?.toString() || 'Not provided'}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

function JsonPanel({ title, value }: { title: string; value?: Record<string, unknown> | null }) {
  return (
    <div>
      <h3 className="mb-2 text-base font-semibold text-slate-950">{title}</h3>
      <pre className="max-h-56 overflow-auto rounded-md bg-slate-100 p-3 text-sm text-slate-700">
        {JSON.stringify(value || {}, null, 2)}
      </pre>
    </div>
  );
}

function JsonEditor({ title, value, onChange }: { title: string; value: string; onChange: (value: string) => void }) {
  return (
    <label className="block">
      <span className="mb-1 block text-sm font-medium text-slate-700">{title}</span>
      <textarea
        rows={7}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="w-full rounded-md border border-slate-300 px-3 py-2 font-mono text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
      />
    </label>
  );
}

function FormInput({
  label,
  name,
  value,
  onChange,
  type = 'text',
}: {
  label: string;
  name: string;
  value: string;
  onChange: (event: ChangeEvent<HTMLInputElement>) => void;
  type?: string;
}) {
  return (
    <label className="block">
      <span className="mb-1 block text-sm font-medium text-slate-700">{label}</span>
      <input
        type={type}
        name={name}
        value={value}
        onChange={onChange}
        className="w-full rounded-md border border-slate-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
      />
    </label>
  );
}
