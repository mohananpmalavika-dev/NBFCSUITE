"use client";

import React, { useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import { AppShell } from '../../../../components/AppShell';
import { enterpriseApi, Enterprise, EnterpriseProfile } from '../../../eomApi';

const tabs = [
  'overview',
  'branding',
  'legal',
  'finance',
  'localization',
  'contact',
  'compliance',
  'integrations',
  'documents',
  'settings',
];

type ProfileForm = EnterpriseProfile & { enterprise: Enterprise };

const initialForm: ProfileForm = {
  enterprise: {
    id: '',
    code: '',
    name: '',
    display_name: '',
    short_name: '',
    status: 'active',
    currency_code: '',
    timezone: '',
    language: '',
    fiscal_year_start: '',
    description: '',
  },
  branding: {
    logo_url: '',
    primary_color: '',
    secondary_color: '',
    theme: '',
    website: '',
    email_domain: '',
    mobile_app_name: '',
    portal_name: '',
  },
  legal: {
    country: '',
    registration_number: '',
    incorporation_date: '',
    tax_number: '',
    gst_vat_number: '',
    pan: '',
    corporate_identity_number: '',
    regulatory_license: '',
  },
  finance: {
    base_currency: '',
    financial_year: '',
    accounting_standard: '',
    tax_system: '',
    default_gl: '',
    default_cost_center: '',
    default_profit_center: '',
  },
  localization: {
    language: '',
    time_zone: '',
    date_format: '',
    number_format: '',
    fiscal_calendar: '',
    holiday_calendar: '',
  },
  contact: {
    corporate_address: '',
    head_office: '',
    email: '',
    phone: '',
    website: '',
    support_contact: '',
  },
  compliance: {
    aml_enabled: false,
    kyc_policy: '',
    data_retention: '',
    audit_retention: '',
    password_policy: '',
    session_policy: '',
  },
  integrations: [],
  documents: [],
  settings: [],
};

function normalizeText(value: unknown) {
  if (typeof value === 'string') {
    return value;
  }
  if (typeof value === 'boolean') {
    return value ? 'true' : 'false';
  }
  return '';
}

function TextField({
  label,
  value,
  onChange,
  type = 'text',
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  type?: string;
}) {
  return (
    <label className="block text-sm">
      <span className="font-medium text-text-primary">{label}</span>
      <input
        className="input mt-1 w-full"
        type={type}
        value={value}
        onChange={(event) => onChange(event.target.value)}
      />
    </label>
  );
}

function TextAreaField({
  label,
  value,
  onChange,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <label className="block text-sm md:col-span-2">
      <span className="font-medium text-text-primary">{label}</span>
      <textarea
        className="input mt-1 min-h-24 w-full"
        value={value}
        onChange={(event) => onChange(event.target.value)}
      />
    </label>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="space-y-4 rounded-md border border-border-default bg-background-surface p-4">
      <h3 className="text-lg font-semibold">{title}</h3>
      <div className="grid gap-4 md:grid-cols-2">{children}</div>
    </section>
  );
}

export default function EnterpriseProfileEditPage({ params }: { params: { id: string } }) {
  const id = params.id;
  const [form, setForm] = useState<ProfileForm>(initialForm);
  const [selectedTab, setSelectedTab] = useState(tabs[0]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;

    async function loadProfile() {
      try {
        const [enterprise, profile] = await Promise.all([
          enterpriseApi.getEnterprise(id),
          enterpriseApi.getEnterpriseProfile(id),
        ]);
        if (!mounted) {
          return;
        }

        setForm({ ...profile, enterprise });
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unable to load enterprise profile.');
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    }

    loadProfile();
    return () => {
      mounted = false;
    };
  }, [id]);

  const canSave = useMemo(() => Boolean(form.enterprise.code.trim() && form.enterprise.name.trim()), [form.enterprise.code, form.enterprise.name]);

  function updateSection(section: keyof ProfileForm, key: string, value: string | boolean) {
    setForm((current) => ({
      ...current,
      [section]: {
        ...(current[section] as Record<string, unknown>),
        [key]: value,
      },
    }));
  }

  function updateArrayItem(
    section: 'integrations' | 'documents' | 'settings',
    index: number,
    key: string,
    value: string | boolean,
  ) {
    setForm((current) => {
      const items = [...(current[section] as Array<Record<string, unknown>>)] as Array<Record<string, unknown>>;
      items[index] = { ...items[index], [key]: value };
      return { ...current, [section]: items } as ProfileForm;
    });
  }

  async function saveProfile() {
    if (!canSave || saving) {
      return;
    }
    setSaving(true);
    setError(null);
    setSuccess(null);

    try {
      await enterpriseApi.patchEnterprise(id, {
        code: form.enterprise.code,
        name: form.enterprise.name,
        display_name: form.enterprise.display_name,
        short_name: form.enterprise.short_name,
        currency_code: form.enterprise.currency_code,
        timezone: form.enterprise.timezone,
        language: form.enterprise.language,
        fiscal_year_start: form.enterprise.fiscal_year_start,
        description: form.enterprise.description,
      });

      await enterpriseApi.updateEnterpriseProfile(id, {
        ...form,
        enterprise: undefined as any,
      });

      setSuccess('Enterprise profile updated successfully.');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred while saving profile.');
    } finally {
      setSaving(false);
    }
  }

  function renderSection() {
    if (selectedTab === 'overview') {
      return (
        <Section title="Overview">
          <TextField
            label="Enterprise code"
            value={normalizeText(form.enterprise.code)}
            onChange={(value) => updateSection('enterprise', 'code', value)}
          />
          <TextField
            label="Enterprise name"
            value={normalizeText(form.enterprise.name)}
            onChange={(value) => updateSection('enterprise', 'name', value)}
          />
          <TextField
            label="Display name"
            value={normalizeText(form.enterprise.display_name)}
            onChange={(value) => updateSection('enterprise', 'display_name', value)}
          />
          <TextField
            label="Short name"
            value={normalizeText(form.enterprise.short_name)}
            onChange={(value) => updateSection('enterprise', 'short_name', value)}
          />
          <TextField
            label="Description"
            value={normalizeText(form.enterprise.description)}
            onChange={(value) => updateSection('enterprise', 'description', value)}
          />
          <TextField
            label="Currency code"
            value={normalizeText(form.enterprise.currency_code)}
            onChange={(value) => updateSection('enterprise', 'currency_code', value)}
          />
          <TextField
            label="Time zone"
            value={normalizeText(form.enterprise.timezone)}
            onChange={(value) => updateSection('enterprise', 'timezone', value)}
          />
          <TextField
            label="Language"
            value={normalizeText(form.enterprise.language)}
            onChange={(value) => updateSection('enterprise', 'language', value)}
          />
          <TextField
            label="Financial year start"
            value={normalizeText(form.enterprise.fiscal_year_start)}
            onChange={(value) => updateSection('enterprise', 'fiscal_year_start', value)}
          />
        </Section>
      );
    }

    if (selectedTab === 'branding') {
      return (
        <Section title="Branding">
          <TextField
            label="Logo URL"
            value={normalizeText(form.branding.logo_url)}
            onChange={(value) => updateSection('branding', 'logo_url', value)}
          />
          <TextField
            label="Primary color"
            value={normalizeText(form.branding.primary_color)}
            onChange={(value) => updateSection('branding', 'primary_color', value)}
          />
          <TextField
            label="Secondary color"
            value={normalizeText(form.branding.secondary_color)}
            onChange={(value) => updateSection('branding', 'secondary_color', value)}
          />
          <TextField
            label="Theme"
            value={normalizeText(form.branding.theme)}
            onChange={(value) => updateSection('branding', 'theme', value)}
          />
          <TextField
            label="Website"
            value={normalizeText(form.branding.website)}
            onChange={(value) => updateSection('branding', 'website', value)}
          />
          <TextField
            label="Email domain"
            value={normalizeText(form.branding.email_domain)}
            onChange={(value) => updateSection('branding', 'email_domain', value)}
          />
          <TextField
            label="Mobile app name"
            value={normalizeText(form.branding.mobile_app_name)}
            onChange={(value) => updateSection('branding', 'mobile_app_name', value)}
          />
          <TextField
            label="Portal name"
            value={normalizeText(form.branding.portal_name)}
            onChange={(value) => updateSection('branding', 'portal_name', value)}
          />
        </Section>
      );
    }

    if (selectedTab === 'legal') {
      return (
        <Section title="Legal">
          <TextField
            label="Country"
            value={normalizeText(form.legal.country)}
            onChange={(value) => updateSection('legal', 'country', value)}
          />
          <TextField
            label="Registration number"
            value={normalizeText(form.legal.registration_number)}
            onChange={(value) => updateSection('legal', 'registration_number', value)}
          />
          <TextField
            label="Incorporation date"
            type="date"
            value={normalizeText(form.legal.incorporation_date)}
            onChange={(value) => updateSection('legal', 'incorporation_date', value)}
          />
          <TextField
            label="Tax number"
            value={normalizeText(form.legal.tax_number)}
            onChange={(value) => updateSection('legal', 'tax_number', value)}
          />
          <TextField
            label="GST / VAT number"
            value={normalizeText(form.legal.gst_vat_number)}
            onChange={(value) => updateSection('legal', 'gst_vat_number', value)}
          />
          <TextField
            label="PAN"
            value={normalizeText(form.legal.pan)}
            onChange={(value) => updateSection('legal', 'pan', value)}
          />
          <TextField
            label="Corporate identity number"
            value={normalizeText(form.legal.corporate_identity_number)}
            onChange={(value) => updateSection('legal', 'corporate_identity_number', value)}
          />
          <TextField
            label="Regulatory license"
            value={normalizeText(form.legal.regulatory_license)}
            onChange={(value) => updateSection('legal', 'regulatory_license', value)}
          />
        </Section>
      );
    }

    if (selectedTab === 'finance') {
      return (
        <Section title="Finance">
          <TextField
            label="Base currency"
            value={normalizeText(form.finance.base_currency)}
            onChange={(value) => updateSection('finance', 'base_currency', value)}
          />
          <TextField
            label="Financial year"
            value={normalizeText(form.finance.financial_year)}
            onChange={(value) => updateSection('finance', 'financial_year', value)}
          />
          <TextField
            label="Accounting standard"
            value={normalizeText(form.finance.accounting_standard)}
            onChange={(value) => updateSection('finance', 'accounting_standard', value)}
          />
          <TextField
            label="Tax system"
            value={normalizeText(form.finance.tax_system)}
            onChange={(value) => updateSection('finance', 'tax_system', value)}
          />
          <TextField
            label="Default GL"
            value={normalizeText(form.finance.default_gl)}
            onChange={(value) => updateSection('finance', 'default_gl', value)}
          />
          <TextField
            label="Default cost center"
            value={normalizeText(form.finance.default_cost_center)}
            onChange={(value) => updateSection('finance', 'default_cost_center', value)}
          />
          <TextField
            label="Default profit center"
            value={normalizeText(form.finance.default_profit_center)}
            onChange={(value) => updateSection('finance', 'default_profit_center', value)}
          />
        </Section>
      );
    }

    if (selectedTab === 'localization') {
      return (
        <Section title="Localization">
          <TextField
            label="Language"
            value={normalizeText(form.localization.language)}
            onChange={(value) => updateSection('localization', 'language', value)}
          />
          <TextField
            label="Time zone"
            value={normalizeText(form.localization.time_zone)}
            onChange={(value) => updateSection('localization', 'time_zone', value)}
          />
          <TextField
            label="Date format"
            value={normalizeText(form.localization.date_format)}
            onChange={(value) => updateSection('localization', 'date_format', value)}
          />
          <TextField
            label="Number format"
            value={normalizeText(form.localization.number_format)}
            onChange={(value) => updateSection('localization', 'number_format', value)}
          />
          <TextField
            label="Fiscal calendar"
            value={normalizeText(form.localization.fiscal_calendar)}
            onChange={(value) => updateSection('localization', 'fiscal_calendar', value)}
          />
          <TextField
            label="Holiday calendar"
            value={normalizeText(form.localization.holiday_calendar)}
            onChange={(value) => updateSection('localization', 'holiday_calendar', value)}
          />
        </Section>
      );
    }

    if (selectedTab === 'contact') {
      return (
        <Section title="Contact">
          <TextAreaField
            label="Corporate address"
            value={normalizeText(form.contact.corporate_address)}
            onChange={(value) => updateSection('contact', 'corporate_address', value)}
          />
          <TextField
            label="Head office"
            value={normalizeText(form.contact.head_office)}
            onChange={(value) => updateSection('contact', 'head_office', value)}
          />
          <TextField
            label="Email"
            value={normalizeText(form.contact.email)}
            onChange={(value) => updateSection('contact', 'email', value)}
          />
          <TextField
            label="Phone"
            value={normalizeText(form.contact.phone)}
            onChange={(value) => updateSection('contact', 'phone', value)}
          />
          <TextField
            label="Website"
            value={normalizeText(form.contact.website)}
            onChange={(value) => updateSection('contact', 'website', value)}
          />
          <TextField
            label="Support contact"
            value={normalizeText(form.contact.support_contact)}
            onChange={(value) => updateSection('contact', 'support_contact', value)}
          />
        </Section>
      );
    }

    if (selectedTab === 'compliance') {
      return (
        <Section title="Compliance">
          <label className="flex items-center gap-3 rounded-md border border-border-default p-3 text-sm">
            <input
              type="checkbox"
              checked={Boolean(form.compliance.aml_enabled)}
              onChange={() => updateSection('compliance', 'aml_enabled', !Boolean(form.compliance.aml_enabled))}
            />
            <span className="font-medium">AML enabled</span>
          </label>
          <TextField
            label="KYC policy"
            value={normalizeText(form.compliance.kyc_policy)}
            onChange={(value) => updateSection('compliance', 'kyc_policy', value)}
          />
          <TextField
            label="Data retention"
            value={normalizeText(form.compliance.data_retention)}
            onChange={(value) => updateSection('compliance', 'data_retention', value)}
          />
          <TextField
            label="Audit retention"
            value={normalizeText(form.compliance.audit_retention)}
            onChange={(value) => updateSection('compliance', 'audit_retention', value)}
          />
          <TextField
            label="Password policy"
            value={normalizeText(form.compliance.password_policy)}
            onChange={(value) => updateSection('compliance', 'password_policy', value)}
          />
          <TextField
            label="Session policy"
            value={normalizeText(form.compliance.session_policy)}
            onChange={(value) => updateSection('compliance', 'session_policy', value)}
          />
        </Section>
      );
    }

    if (selectedTab === 'integrations') {
      return (
        <Section title="Integrations">
          {form.integrations.map((integration, index) => (
            <div key={`${integration.integration_type}-${index}`} className="space-y-3 rounded-md border border-border-default p-3">
              <div className="text-sm font-semibold capitalize">{integration.integration_type.replace(/_/g, ' ')}</div>
              <TextField
                label="Provider"
                value={normalizeText(integration.provider)}
                onChange={(value) => updateArrayItem('integrations', index, 'provider', value)}
              />
              <TextField
                label="Status"
                value={normalizeText(integration.status)}
                onChange={(value) => updateArrayItem('integrations', index, 'status', value)}
              />
            </div>
          ))}
        </Section>
      );
    }

    if (selectedTab === 'documents') {
      return (
        <Section title="Documents">
          {form.documents.map((document, index) => (
            <div key={`${document.document_type}-${index}`} className="space-y-3 rounded-md border border-border-default p-3">
              <div className="text-sm font-semibold capitalize">{document.name || document.document_type.replace(/_/g, ' ')}</div>
              <TextField
                label="Status"
                value={normalizeText(document.status)}
                onChange={(value) => updateArrayItem('documents', index, 'status', value)}
              />
              <TextField
                label="OCR metadata"
                value={normalizeText(document.ocr_metadata)}
                onChange={(value) => updateArrayItem('documents', index, 'ocr_metadata', value)}
              />
            </div>
          ))}
        </Section>
      );
    }

    if (selectedTab === 'settings') {
      return (
        <Section title="Settings">
          {form.settings.map((setting, index) => (
            <div key={`${setting.setting_group}-${setting.setting_key}-${index}`} className="space-y-3 rounded-md border border-border-default p-3">
              <div className="text-sm font-semibold">{setting.setting_group}</div>
              <TextField
                label="Key"
                value={normalizeText(setting.setting_key)}
                onChange={(value) => updateArrayItem('settings', index, 'setting_key', value)}
              />
              <TextField
                label="Value"
                value={normalizeText(setting.setting_value)}
                onChange={(value) => updateArrayItem('settings', index, 'setting_value', value)}
              />
              <label className="flex items-center gap-3 text-sm">
                <input
                  type="checkbox"
                  checked={Boolean(setting.inherited)}
                  onChange={() => updateArrayItem('settings', index, 'inherited', !Boolean(setting.inherited))}
                />
                Inherited
              </label>
            </div>
          ))}
        </Section>
      );
    }

    return null;
  }

  return (
    <AppShell>
      <div className="space-y-5">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <p className="text-sm font-medium text-text-secondary">EOM-001 Enterprise Master</p>
            <h2 className="text-2xl font-semibold">Edit Enterprise Profile</h2>
            <p className="mt-1 max-w-3xl text-sm text-text-secondary">
              Update enterprise settings, branding, finance defaults, compliance, localization, and governance data.
            </p>
          </div>
          <div className="flex gap-2">
            <Link href={`/eom/enterprises/${id}`} className="btn btn-secondary">
              Back to Enterprise
            </Link>
            <button
              type="button"
              className="btn btn-primary"
              onClick={saveProfile}
              disabled={!canSave || saving || loading}
            >
              {saving ? 'Saving…' : 'Save Profile'}
            </button>
          </div>
        </div>

        {loading ? (
          <div className="rounded-md border border-border-default bg-background-surface p-4 text-sm text-text-secondary">
            Loading enterprise profile...
          </div>
        ) : (
          <>
            <div className="grid gap-2 md:grid-cols-3 lg:grid-cols-5">
              {tabs.map((tab) => (
                <button
                  key={tab}
                  type="button"
                  className={`rounded-md border px-3 py-2 text-left text-sm font-medium ${selectedTab === tab ? 'border-primary-500 bg-primary-50 text-primary-700' : 'border-border-default bg-background-surface text-text-secondary'}`}
                  onClick={() => setSelectedTab(tab)}
                >
                  {tab.replace(/_/g, ' ')}
                </button>
              ))}
            </div>

            <div className="space-y-4">
              {error ? (
                <div className="rounded-md border border-red-200 bg-red-50 p-4 text-sm text-red-700">{error}</div>
              ) : null}
              {success ? (
                <div className="rounded-md border border-green-200 bg-green-50 p-4 text-sm text-green-700">{success}</div>
              ) : null}

              {renderSection()}
            </div>
          </>
        )}
      </div>
    </AppShell>
  );
}
