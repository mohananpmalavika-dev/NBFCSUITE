"use client";

import React, { useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { AppShell } from '../../../../components/AppShell';
import { eomApiUrl } from '../../../eomApi';

const steps = [
  'General',
  'Branding',
  'Legal',
  'Finance',
  'Localization',
  'Contact',
  'Compliance',
  'Integrations',
  'Documents',
  'Review',
  'Submit',
];

const integrationTypes = [
  'core_banking',
  'sms',
  'email',
  'whatsapp',
  'payment_gateway',
  'ocr',
  'aml',
  'credit_bureau',
  'identity_verification',
  'erp',
  'crm',
];

const documentTypes = ['Certificate', 'GST', 'PAN', 'Trade license', 'Incorporation documents', 'Board resolution', 'Logo files', 'Policy documents'];

type FormState = {
  general: {
    code: string;
    name: string;
    shortName: string;
    displayName: string;
    enterpriseType: string;
    industry: string;
    businessCategory: string;
    businessModel: string;
    status: string;
  };
  branding: {
    logoUrl: string;
    primaryColor: string;
    secondaryColor: string;
    theme: string;
    website: string;
    emailDomain: string;
    mobileAppName: string;
    portalName: string;
  };
  legal: {
    country: string;
    registrationNumber: string;
    incorporationDate: string;
    taxNumber: string;
    gstVatNumber: string;
    pan: string;
    cin: string;
    regulatoryLicense: string;
  };
  finance: {
    baseCurrency: string;
    financialYear: string;
    accountingStandard: string;
    taxSystem: string;
    defaultGl: string;
    defaultCostCenter: string;
    defaultProfitCenter: string;
  };
  localization: {
    language: string;
    timeZone: string;
    dateFormat: string;
    numberFormat: string;
    fiscalCalendar: string;
    holidayCalendar: string;
  };
  contact: {
    corporateAddress: string;
    headOffice: string;
    email: string;
    phone: string;
    website: string;
    supportContact: string;
  };
  compliance: {
    amlEnabled: boolean;
    kycPolicy: string;
    dataRetention: string;
    auditRetention: string;
    passwordPolicy: string;
    sessionPolicy: string;
  };
  integrations: Record<string, boolean>;
  documents: Record<string, boolean>;
};

const initialForm: FormState = {
  general: {
    code: '',
    name: '',
    shortName: '',
    displayName: '',
    enterpriseType: 'NBFC',
    industry: 'Financial services',
    businessCategory: 'Lending',
    businessModel: 'Branch and digital',
    status: 'active',
  },
  branding: {
    logoUrl: '',
    primaryColor: '#0f766e',
    secondaryColor: '#1d4ed8',
    theme: 'Enterprise',
    website: '',
    emailDomain: '',
    mobileAppName: '',
    portalName: '',
  },
  legal: {
    country: 'India',
    registrationNumber: '',
    incorporationDate: '',
    taxNumber: '',
    gstVatNumber: '',
    pan: '',
    cin: '',
    regulatoryLicense: '',
  },
  finance: {
    baseCurrency: 'INR',
    financialYear: 'April-March',
    accountingStandard: 'Ind AS',
    taxSystem: 'GST',
    defaultGl: '',
    defaultCostCenter: '',
    defaultProfitCenter: '',
  },
  localization: {
    language: 'en-IN',
    timeZone: 'Asia/Kolkata',
    dateFormat: 'DD/MM/YYYY',
    numberFormat: 'en-IN',
    fiscalCalendar: 'India FY',
    holidayCalendar: 'India',
  },
  contact: {
    corporateAddress: '',
    headOffice: '',
    email: '',
    phone: '',
    website: '',
    supportContact: '',
  },
  compliance: {
    amlEnabled: true,
    kycPolicy: 'Standard KYC',
    dataRetention: '8 years',
    auditRetention: '10 years',
    passwordPolicy: 'Strong password policy',
    sessionPolicy: '30 minutes',
  },
  integrations: integrationTypes.reduce<Record<string, boolean>>((acc, item) => ({ ...acc, [item]: false }), {}),
  documents: documentTypes.reduce<Record<string, boolean>>((acc, item) => ({ ...acc, [item]: false }), {}),
};

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
      <input className="input mt-1 w-full" type={type} value={value} onChange={(event) => onChange(event.target.value)} />
    </label>
  );
}

function TextAreaField({ label, value, onChange }: { label: string; value: string; onChange: (value: string) => void }) {
  return (
    <label className="block text-sm md:col-span-2">
      <span className="font-medium text-text-primary">{label}</span>
      <textarea className="input mt-1 min-h-24 w-full" value={value} onChange={(event) => onChange(event.target.value)} />
    </label>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="space-y-4">
      <h3 className="text-lg font-semibold">{title}</h3>
      <div className="grid gap-4 md:grid-cols-2">{children}</div>
    </section>
  );
}

export default function EnterpriseMasterWizardPage() {
  const [stepIndex, setStepIndex] = useState(0);
  const [form, setForm] = useState<FormState>(initialForm);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const progress = useMemo(() => Math.round(((stepIndex + 1) / steps.length) * 100), [stepIndex]);
  const canSubmit = Boolean(form.general.code.trim() && form.general.name.trim());

  function updateSection(section: keyof FormState, key: string, value: string | boolean) {
    setForm((current) => ({
      ...current,
      [section]: {
        ...(current[section] as Record<string, string | boolean>),
        [key]: value,
      },
    }));
  }

  function toggleMap(section: 'integrations' | 'documents', key: string) {
    setForm((current) => ({
      ...current,
      [section]: {
        ...current[section],
        [key]: !current[section][key],
      },
    }));
  }

  async function submitEnterprise() {
    if (!canSubmit || submitting) {
      return;
    }
    setSubmitting(true);
    setError(null);

    try {
      const enterpriseRes = await fetch(eomApiUrl('/eom/enterprises'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-User-Roles': 'enterprise.admin' },
        body: JSON.stringify({
          code: form.general.code,
          name: form.general.name,
          display_name: form.general.displayName,
          short_name: form.general.shortName,
          currency_code: form.finance.baseCurrency,
          timezone: form.localization.timeZone,
          language: form.localization.language,
          fiscal_year_start: form.finance.financialYear,
          description: `${form.general.enterpriseType} · ${form.general.industry} · ${form.general.businessModel}`,
        }),
      });

      if (!enterpriseRes.ok) {
        const body = await enterpriseRes.json();
        throw new Error(body.detail || 'Failed to create enterprise');
      }

      const enterprise = await enterpriseRes.json();
      const profileRes = await fetch(eomApiUrl(`/eom/enterprises/${enterprise.id}/profile`), {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', 'X-User-Roles': 'enterprise.admin' },
        body: JSON.stringify({
          branding: {
            logo_url: form.branding.logoUrl,
            primary_color: form.branding.primaryColor,
            secondary_color: form.branding.secondaryColor,
            theme: form.branding.theme,
            website: form.branding.website,
            email_domain: form.branding.emailDomain,
            mobile_app_name: form.branding.mobileAppName,
            portal_name: form.branding.portalName,
          },
          legal: {
            country: form.legal.country,
            registration_number: form.legal.registrationNumber,
            incorporation_date: form.legal.incorporationDate,
            tax_number: form.legal.taxNumber,
            gst_vat_number: form.legal.gstVatNumber,
            pan: form.legal.pan,
            corporate_identity_number: form.legal.cin,
            regulatory_license: form.legal.regulatoryLicense,
          },
          finance: {
            base_currency: form.finance.baseCurrency,
            financial_year: form.finance.financialYear,
            accounting_standard: form.finance.accountingStandard,
            tax_system: form.finance.taxSystem,
            default_gl: form.finance.defaultGl,
            default_cost_center: form.finance.defaultCostCenter,
            default_profit_center: form.finance.defaultProfitCenter,
          },
          localization: {
            language: form.localization.language,
            time_zone: form.localization.timeZone,
            date_format: form.localization.dateFormat,
            number_format: form.localization.numberFormat,
            fiscal_calendar: form.localization.fiscalCalendar,
            holiday_calendar: form.localization.holidayCalendar,
          },
          contact: {
            corporate_address: form.contact.corporateAddress,
            head_office: form.contact.headOffice,
            email: form.contact.email,
            phone: form.contact.phone,
            website: form.contact.website,
            support_contact: form.contact.supportContact,
          },
          compliance: {
            aml_enabled: form.compliance.amlEnabled,
            kyc_policy: form.compliance.kycPolicy,
            data_retention: form.compliance.dataRetention,
            audit_retention: form.compliance.auditRetention,
            password_policy: form.compliance.passwordPolicy,
            session_policy: form.compliance.sessionPolicy,
          },
          integrations: integrationTypes.map((type) => ({
            integration_type: type,
            provider: form.integrations[type] ? 'Configured' : '',
            status: form.integrations[type] ? 'active' : 'planned',
          })),
          documents: documentTypes.map((type) => ({
            document_type: type.toLowerCase().replace(/ /g, '_'),
            name: type,
            status: form.documents[type] ? 'verified' : 'pending',
          })),
          settings: ['General', 'Branding', 'Finance', 'Security', 'Notifications', 'Workflow', 'AI', 'Reports'].map((group) => ({
            setting_group: group,
            setting_key: 'enabled',
            setting_value: 'true',
            inherited: true,
          })),
        }),
      });

      if (!profileRes.ok) {
        const body = await profileRes.json();
        throw new Error(body.detail || 'Failed to save enterprise profile');
      }

      router.push(`/eom/enterprises/${enterprise.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setSubmitting(false);
    }
  }

  function renderStep() {
    if (stepIndex === 0) {
      return (
        <Section title="General information">
          <TextField label="Enterprise code" value={form.general.code} onChange={(value) => updateSection('general', 'code', value)} />
          <TextField label="Enterprise name" value={form.general.name} onChange={(value) => updateSection('general', 'name', value)} />
          <TextField label="Short name" value={form.general.shortName} onChange={(value) => updateSection('general', 'shortName', value)} />
          <TextField label="Display name" value={form.general.displayName} onChange={(value) => updateSection('general', 'displayName', value)} />
          <TextField label="Enterprise type" value={form.general.enterpriseType} onChange={(value) => updateSection('general', 'enterpriseType', value)} />
          <TextField label="Industry" value={form.general.industry} onChange={(value) => updateSection('general', 'industry', value)} />
          <TextField label="Business category" value={form.general.businessCategory} onChange={(value) => updateSection('general', 'businessCategory', value)} />
          <TextField label="Business model" value={form.general.businessModel} onChange={(value) => updateSection('general', 'businessModel', value)} />
        </Section>
      );
    }

    if (stepIndex === 1) {
      return (
        <Section title="Branding">
          <TextField label="Logo URL" value={form.branding.logoUrl} onChange={(value) => updateSection('branding', 'logoUrl', value)} />
          <TextField label="Theme" value={form.branding.theme} onChange={(value) => updateSection('branding', 'theme', value)} />
          <TextField label="Primary color" value={form.branding.primaryColor} onChange={(value) => updateSection('branding', 'primaryColor', value)} />
          <TextField label="Secondary color" value={form.branding.secondaryColor} onChange={(value) => updateSection('branding', 'secondaryColor', value)} />
          <TextField label="Website" value={form.branding.website} onChange={(value) => updateSection('branding', 'website', value)} />
          <TextField label="Email domain" value={form.branding.emailDomain} onChange={(value) => updateSection('branding', 'emailDomain', value)} />
          <TextField label="Mobile app name" value={form.branding.mobileAppName} onChange={(value) => updateSection('branding', 'mobileAppName', value)} />
          <TextField label="Portal name" value={form.branding.portalName} onChange={(value) => updateSection('branding', 'portalName', value)} />
          <div className="rounded-md border border-border-default p-4 md:col-span-2" style={{ borderColor: form.branding.primaryColor }}>
            <div className="text-sm text-text-secondary">Live preview</div>
            <div className="mt-2 text-lg font-semibold" style={{ color: form.branding.primaryColor }}>
              {form.branding.portalName || form.general.displayName || 'Enterprise Portal'}
            </div>
          </div>
        </Section>
      );
    }

    if (stepIndex === 2) {
      return (
        <Section title="Legal">
          <TextField label="Country" value={form.legal.country} onChange={(value) => updateSection('legal', 'country', value)} />
          <TextField label="Registration number" value={form.legal.registrationNumber} onChange={(value) => updateSection('legal', 'registrationNumber', value)} />
          <TextField label="Incorporation date" type="date" value={form.legal.incorporationDate} onChange={(value) => updateSection('legal', 'incorporationDate', value)} />
          <TextField label="Tax number" value={form.legal.taxNumber} onChange={(value) => updateSection('legal', 'taxNumber', value)} />
          <TextField label="GST or VAT number" value={form.legal.gstVatNumber} onChange={(value) => updateSection('legal', 'gstVatNumber', value)} />
          <TextField label="PAN" value={form.legal.pan} onChange={(value) => updateSection('legal', 'pan', value)} />
          <TextField label="Corporate identity number" value={form.legal.cin} onChange={(value) => updateSection('legal', 'cin', value)} />
          <TextField label="Regulatory license" value={form.legal.regulatoryLicense} onChange={(value) => updateSection('legal', 'regulatoryLicense', value)} />
        </Section>
      );
    }

    if (stepIndex === 3) {
      return (
        <Section title="Finance">
          <TextField label="Base currency" value={form.finance.baseCurrency} onChange={(value) => updateSection('finance', 'baseCurrency', value)} />
          <TextField label="Financial year" value={form.finance.financialYear} onChange={(value) => updateSection('finance', 'financialYear', value)} />
          <TextField label="Accounting standard" value={form.finance.accountingStandard} onChange={(value) => updateSection('finance', 'accountingStandard', value)} />
          <TextField label="Tax system" value={form.finance.taxSystem} onChange={(value) => updateSection('finance', 'taxSystem', value)} />
          <TextField label="Default GL" value={form.finance.defaultGl} onChange={(value) => updateSection('finance', 'defaultGl', value)} />
          <TextField label="Default cost center" value={form.finance.defaultCostCenter} onChange={(value) => updateSection('finance', 'defaultCostCenter', value)} />
          <TextField label="Default profit center" value={form.finance.defaultProfitCenter} onChange={(value) => updateSection('finance', 'defaultProfitCenter', value)} />
        </Section>
      );
    }

    if (stepIndex === 4) {
      return (
        <Section title="Localization">
          <TextField label="Language" value={form.localization.language} onChange={(value) => updateSection('localization', 'language', value)} />
          <TextField label="Time zone" value={form.localization.timeZone} onChange={(value) => updateSection('localization', 'timeZone', value)} />
          <TextField label="Date format" value={form.localization.dateFormat} onChange={(value) => updateSection('localization', 'dateFormat', value)} />
          <TextField label="Number format" value={form.localization.numberFormat} onChange={(value) => updateSection('localization', 'numberFormat', value)} />
          <TextField label="Fiscal calendar" value={form.localization.fiscalCalendar} onChange={(value) => updateSection('localization', 'fiscalCalendar', value)} />
          <TextField label="Holiday calendar" value={form.localization.holidayCalendar} onChange={(value) => updateSection('localization', 'holidayCalendar', value)} />
        </Section>
      );
    }

    if (stepIndex === 5) {
      return (
        <Section title="Contact">
          <TextAreaField label="Corporate address" value={form.contact.corporateAddress} onChange={(value) => updateSection('contact', 'corporateAddress', value)} />
          <TextField label="Head office" value={form.contact.headOffice} onChange={(value) => updateSection('contact', 'headOffice', value)} />
          <TextField label="Email" value={form.contact.email} onChange={(value) => updateSection('contact', 'email', value)} />
          <TextField label="Phone" value={form.contact.phone} onChange={(value) => updateSection('contact', 'phone', value)} />
          <TextField label="Website" value={form.contact.website} onChange={(value) => updateSection('contact', 'website', value)} />
          <TextField label="Support contact" value={form.contact.supportContact} onChange={(value) => updateSection('contact', 'supportContact', value)} />
        </Section>
      );
    }

    if (stepIndex === 6) {
      return (
        <Section title="Compliance">
          <label className="flex items-center gap-3 rounded-md border border-border-default p-3 text-sm">
            <input type="checkbox" checked={form.compliance.amlEnabled} onChange={() => updateSection('compliance', 'amlEnabled', !form.compliance.amlEnabled)} />
            <span className="font-medium">AML enabled</span>
          </label>
          <TextField label="KYC policy" value={form.compliance.kycPolicy} onChange={(value) => updateSection('compliance', 'kycPolicy', value)} />
          <TextField label="Data retention" value={form.compliance.dataRetention} onChange={(value) => updateSection('compliance', 'dataRetention', value)} />
          <TextField label="Audit retention" value={form.compliance.auditRetention} onChange={(value) => updateSection('compliance', 'auditRetention', value)} />
          <TextField label="Password policy" value={form.compliance.passwordPolicy} onChange={(value) => updateSection('compliance', 'passwordPolicy', value)} />
          <TextField label="Session policy" value={form.compliance.sessionPolicy} onChange={(value) => updateSection('compliance', 'sessionPolicy', value)} />
        </Section>
      );
    }

    if (stepIndex === 7) {
      return (
        <section className="space-y-4">
          <h3 className="text-lg font-semibold">Integrations</h3>
          <div className="grid gap-3 md:grid-cols-3">
            {integrationTypes.map((type) => (
              <label key={type} className="flex items-center justify-between rounded-md border border-border-default p-3 text-sm">
                <span className="font-medium capitalize">{type.replace(/_/g, ' ')}</span>
                <input type="checkbox" checked={form.integrations[type]} onChange={() => toggleMap('integrations', type)} />
              </label>
            ))}
          </div>
        </section>
      );
    }

    if (stepIndex === 8) {
      return (
        <section className="space-y-4">
          <h3 className="text-lg font-semibold">Documents</h3>
          <div className="grid gap-3 md:grid-cols-2">
            {documentTypes.map((type) => (
              <label key={type} className="flex items-center justify-between rounded-md border border-border-default p-3 text-sm">
                <span className="font-medium">{type}</span>
                <input type="checkbox" checked={form.documents[type]} onChange={() => toggleMap('documents', type)} />
              </label>
            ))}
          </div>
        </section>
      );
    }

    if (stepIndex === 9) {
      const reviewRows = [
        ['General', form.general.name || 'Not set'],
        ['Branding', form.branding.portalName || form.branding.theme],
        ['Legal', form.legal.regulatoryLicense || 'License pending'],
        ['Finance', `${form.finance.baseCurrency} · ${form.finance.financialYear}`],
        ['Localization', `${form.localization.language} · ${form.localization.timeZone}`],
        ['Compliance', form.compliance.amlEnabled ? 'AML enabled' : 'AML disabled'],
        ['Integrations', `${Object.values(form.integrations).filter(Boolean).length} active`],
        ['Documents', `${Object.values(form.documents).filter(Boolean).length} verified`],
      ];

      return (
        <section className="space-y-4">
          <h3 className="text-lg font-semibold">Review</h3>
          <div className="grid gap-3 md:grid-cols-2">
            {reviewRows.map(([label, value]) => (
              <div key={label} className="rounded-md border border-border-default p-3">
                <div className="text-sm text-text-secondary">{label}</div>
                <div className="mt-1 font-medium">{value}</div>
              </div>
            ))}
          </div>
        </section>
      );
    }

    return (
      <section className="space-y-4">
        <h3 className="text-lg font-semibold">Submit for workflow</h3>
        <div className="rounded-md border border-border-default bg-background-surface p-4">
          <div className="text-sm text-text-secondary">Workflow lifecycle</div>
          <div className="mt-2 font-medium">Draft to Review to Admin approval to Enterprise created</div>
        </div>
        <div className="rounded-md border border-border-default p-4">
          <div className="text-sm text-text-secondary">Enterprise health inputs</div>
          <div className="mt-2 grid gap-2 text-sm md:grid-cols-3">
            <span>Configuration defaults</span>
            <span>Compliance policies</span>
            <span>Documents and OCR metadata</span>
            <span>Integrations</span>
            <span>Localization</span>
            <span>Audit trail</span>
          </div>
        </div>
        {error ? <div className="rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div> : null}
      </section>
    );
  }

  return (
    <AppShell>
      <div className="space-y-5">
        <div>
          <p className="text-sm font-medium text-text-secondary">EOM-001 Enterprise Master</p>
          <h2 className="text-2xl font-semibold">Create Enterprise</h2>
          <p className="mt-1 max-w-3xl text-sm text-text-secondary">
            Configure the root enterprise object used by EOM, IAM, workflow, audit, reports, and downstream business modules.
          </p>
        </div>

        <div className="rounded-md border border-border-default bg-background-surface">
          <div className="border-b border-border-default p-4">
            <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <div className="text-sm text-text-secondary">Step {stepIndex + 1} of {steps.length}</div>
                <div className="text-lg font-semibold">{steps[stepIndex]}</div>
              </div>
              <div className="h-2 w-full max-w-md overflow-hidden rounded-full bg-background-muted">
                <div className="h-full bg-primary-500" style={{ width: `${progress}%` }} />
              </div>
            </div>
            <div className="mt-4 grid gap-2 md:grid-cols-4 xl:grid-cols-11">
              {steps.map((step, index) => (
                <button
                  key={step}
                  type="button"
                  className={`rounded-md border px-2 py-2 text-xs font-medium ${index === stepIndex ? 'border-primary-500 bg-primary-50 text-primary-700' : 'border-border-default bg-background-surface text-text-secondary'}`}
                  onClick={() => setStepIndex(index)}
                >
                  {step}
                </button>
              ))}
            </div>
          </div>

          <div className="p-4 sm:p-5">{renderStep()}</div>

          <div className="flex flex-col gap-3 border-t border-border-default p-4 sm:flex-row sm:items-center sm:justify-between">
            <button className="btn" type="button" disabled={stepIndex === 0} onClick={() => setStepIndex((current) => Math.max(0, current - 1))}>
              Back
            </button>
            <div className="flex gap-2">
              {stepIndex < steps.length - 1 ? (
                <button className="btn btn-primary" type="button" onClick={() => setStepIndex((current) => Math.min(steps.length - 1, current + 1))}>
                  Next
                </button>
              ) : (
                <button className="btn btn-primary" type="button" disabled={!canSubmit || submitting} onClick={submitEnterprise}>
                  {submitting ? 'Creating...' : 'Create enterprise'}
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
