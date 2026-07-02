"use client";

import { useEffect, useState } from 'react';
import { AppShell } from '../../components/AppShell';
import { accountingApi, DEFAULT_ACCOUNTING_TENANT } from '../accountingApi';
import type {
  EInvoiceCreate,
  EInvoiceResponse,
  EWayBillCreate,
  EWayBillResponse,
  TaxCalculationRequest,
  TaxCalculationResponse,
  TaxComplianceResponse,
  TaxDashboardResponse,
  TaxLedgerItem,
  TaxRateResponse,
  TaxReconciliationRequest,
  TaxReconciliationResponse,
  TaxReturnPayload,
  TaxReturnResponse,
} from '../accountingApi';

function formatAmount(value: number | null | undefined, currency = 'INR') {
  const amount = typeof value === 'number' ? value : 0;
  return new Intl.NumberFormat('en-IN', { style: 'currency', currency, maximumFractionDigits: 2 }).format(amount);
}

export default function TaxEnginePage() {
  const [dashboard, setDashboard] = useState<TaxDashboardResponse | null>(null);
  const [rates, setRates] = useState<TaxRateResponse[]>([]);
  const [ledger, setLedger] = useState<TaxLedgerItem[]>([]);
  const [compliance, setCompliance] = useState<TaxComplianceResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const [calculation, setCalculation] = useState<TaxCalculationResponse | null>(null);
  const [taxType, setTaxType] = useState('GST');
  const [jurisdiction, setJurisdiction] = useState('IN');
  const [baseAmount, setBaseAmount] = useState('10000');

  const [returnType, setReturnType] = useState('GSTR-1');
  const [returnPeriod, setReturnPeriod] = useState('2026-06');
  const [returnDetails, setReturnDetails] = useState<string>(
    JSON.stringify({ sales: 100000, tax_paid: 18000 }, null, 2),
  );
  const [returnResult, setReturnResult] = useState<TaxReturnResponse | null>(null);

  const [reconciliationResult, setReconciliationResult] = useState<TaxReconciliationResponse | null>(null);
  const [recReference, setRecReference] = useState('TX-REF-001');
  const [reportedAmount, setReportedAmount] = useState('18000');
  const [recordedAmount, setRecordedAmount] = useState('17500');

  const [einvoiceResult, setEinvoiceResult] = useState<EInvoiceResponse | null>(null);
  const [einvoiceId, setEinvoiceId] = useState('INV-20260601-001');
  const [einvoiceDate, setEinvoiceDate] = useState(new Date().toISOString().slice(0, 10));
  const [einvoiceAmount, setEinvoiceAmount] = useState('150000');

  const [ewayResult, setEwayResult] = useState<EWayBillResponse | null>(null);
  const [ewayVehicle, setEwayVehicle] = useState('MH12AB1234');
  const [ewayTransporter, setEwayTransporter] = useState('Rapid Logistics');
  const [ewayFrom, setEwayFrom] = useState('Mumbai');
  const [ewayTo, setEwayTo] = useState('Bengaluru');
  const [ewayDistance, setEwayDistance] = useState('980');

  async function load() {
    setLoading(true);
    setError('');

    try {
      const [dashboardBody, ratesBody, ledgerBody, complianceBody] = await Promise.all([
        accountingApi.getTaxDashboard(DEFAULT_ACCOUNTING_TENANT),
        accountingApi.listTaxRates(DEFAULT_ACCOUNTING_TENANT),
        accountingApi.getTaxLedger(DEFAULT_ACCOUNTING_TENANT),
        accountingApi.getTaxCompliance(DEFAULT_ACCOUNTING_TENANT),
      ]);
      setDashboard(dashboardBody);
      setRates(ratesBody);
      setLedger(ledgerBody.entries);
      setCompliance(complianceBody);
    } catch (err) {
      setError('Unable to load tax engine workspace. Verify the accounting backend is running and reachable.');
      setDashboard(null);
      setRates([]);
      setLedger([]);
      setCompliance(null);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function runCalculation() {
    setError('');
    try {
      const payload: TaxCalculationRequest = {
        tenant_id: DEFAULT_ACCOUNTING_TENANT,
        tax_type: taxType,
        jurisdiction,
        base_amount: Number(baseAmount) || 0,
      };
      const result = await accountingApi.calculateTax(payload);
      setCalculation(result);
    } catch {
      setError('Tax calculation failed. Confirm the input values and backend availability.');
      setCalculation(null);
    }
  }

  async function submitReturn() {
    setError('');
    try {
      const payload: TaxReturnPayload = {
        tenant_id: DEFAULT_ACCOUNTING_TENANT,
        return_type: returnType,
        period: returnPeriod,
        details: JSON.parse(returnDetails || '{}'),
      };
      const result = returnType.toUpperCase().startsWith('GSTR')
        ? await accountingApi.createGSTReturn(payload)
        : await accountingApi.createTDSReturn(payload);
      setReturnResult(result);
    } catch {
      setError('Return filing failed. Verify return payload and payload structure.');
      setReturnResult(null);
    }
  }

  async function submitReconciliation() {
    setError('');
    try {
      const payload: TaxReconciliationRequest = {
        tenant_id: DEFAULT_ACCOUNTING_TENANT,
        reference_id: recReference,
        reported_amount: Number(reportedAmount) || 0,
        recorded_amount: Number(recordedAmount) || 0,
        metadata: { source: 'tax-engine-console' },
      };
      const result = await accountingApi.reconcileTax(payload);
      setReconciliationResult(result);
    } catch {
      setError('Reconciliation failed. Confirm the amounts and check backend connectivity.');
      setReconciliationResult(null);
    }
  }

  async function generateEInvoice() {
    setError('');
    try {
      const payload: EInvoiceCreate = {
        tenant_id: DEFAULT_ACCOUNTING_TENANT,
        invoice_id: einvoiceId,
        invoice_date: new Date(einvoiceDate).toISOString(),
        amount: Number(einvoiceAmount) || 0,
        metadata: { created_by: 'finance-console' },
      };
      const result = await accountingApi.createEInvoice(payload);
      setEinvoiceResult(result);
    } catch {
      setError('E-invoice creation failed. Verify invoice values and backend health.');
      setEinvoiceResult(null);
    }
  }

  async function generateEWayBill() {
    setError('');
    try {
      const payload: EWayBillCreate = {
        tenant_id: DEFAULT_ACCOUNTING_TENANT,
        invoice_id: einvoiceId,
        vehicle_number: ewayVehicle,
        transporter_name: ewayTransporter,
        from_place: ewayFrom,
        to_place: ewayTo,
        distance_km: Number(ewayDistance) || 0,
      };
      const result = await accountingApi.createEWayBill(payload);
      setEwayResult(result);
    } catch {
      setError('E-way bill creation failed. Confirm transport details and backend availability.');
      setEwayResult(null);
    }
  }

  return (
    <AppShell>
      <div className="space-y-6 p-6">
        <div className="rounded-md border border-border-default bg-background-surface p-6">
          <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
            <div>
              <div className="text-sm font-semibold uppercase tracking-wide text-accent-primary">Enterprise Tax Engine</div>
              <h1 className="mt-2 text-2xl font-semibold text-text-primary">Tax compliance, filings, and automated reconciliation</h1>
              <p className="mt-2 max-w-3xl text-sm text-text-secondary">
                Monitor GST, TDS, e-invoice and e-way bill workflows while validating tax returns, ledger postings, and compliance health.
              </p>
            </div>
            <div className="rounded-md border border-border-default bg-background-default px-3 py-2 text-sm text-text-secondary">
              Tenant {DEFAULT_ACCOUNTING_TENANT}
            </div>
          </div>
        </div>

        {loading ? (
          <div className="rounded-md border border-border-default bg-background-surface p-6 text-sm text-text-secondary">Loading tax engine workspace…</div>
        ) : (
          <div className="space-y-6">
            {error ? (
              <div className="rounded-md border border-border-default bg-danger-surface p-4 text-sm text-danger-foreground">{error}</div>
            ) : null}

            <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
              <div className="rounded-md border border-border-default bg-background-surface p-4">
                <div className="text-sm text-text-secondary">GST Transactions</div>
                <div className="mt-2 text-2xl font-semibold text-text-primary">{dashboard?.total_gst_transactions ?? 0}</div>
              </div>
              <div className="rounded-md border border-border-default bg-background-surface p-4">
                <div className="text-sm text-text-secondary">TDS Transactions</div>
                <div className="mt-2 text-2xl font-semibold text-text-primary">{dashboard?.total_tds_transactions ?? 0}</div>
              </div>
              <div className="rounded-md border border-border-default bg-background-surface p-4">
                <div className="text-sm text-text-secondary">E-invoices</div>
                <div className="mt-2 text-2xl font-semibold text-text-primary">{dashboard?.total_einvoices ?? 0}</div>
              </div>
              <div className="rounded-md border border-border-default bg-background-surface p-4">
                <div className="text-sm text-text-secondary">Compliance Health</div>
                <div className="mt-2 text-2xl font-semibold text-text-primary">{compliance?.compliance_health ?? 'n/a'}</div>
              </div>
            </div>

            <div className="grid gap-6 xl:grid-cols-[1.3fr_0.7fr]">
              <div className="rounded-md border border-border-default bg-background-surface p-4">
                <div className="mb-4 text-lg font-semibold text-text-primary">Tax Rates</div>
                <div className="grid gap-2">
                  {rates.length > 0 ? (
                    rates.map((rate) => (
                      <div key={rate.id} className="rounded-md border border-border-light bg-background-default p-3">
                        <div className="flex items-center justify-between gap-3">
                          <div>
                            <div className="text-sm font-semibold text-text-primary">{rate.tax_type}</div>
                            <div className="text-xs text-text-secondary">{rate.status} • Effective {new Date(rate.effective_date).toLocaleDateString()}</div>
                          </div>
                          <div className="text-lg font-semibold text-text-primary">{rate.rate}%</div>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-sm text-text-secondary">No tax rates configured for this tenant.</div>
                  )}
                </div>
              </div>

              <div className="rounded-md border border-border-default bg-background-surface p-4">
                <div className="mb-4 text-lg font-semibold text-text-primary">Compliance Summary</div>
                <div className="space-y-3 text-sm text-text-secondary">
                  <div>GST compliance: {compliance?.gst_compliance ?? 'n/a'}</div>
                  <div>TDS compliance: {compliance?.tds_compliance ?? 'n/a'}</div>
                  <div>ITC utilization: {compliance?.itc_utilization ?? 0}%</div>
                  <div>Open returns: {compliance?.outstanding_returns ?? 0}</div>
                </div>
              </div>
            </div>

            <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
              <div className="rounded-md border border-border-default bg-background-surface p-4">
                <div className="mb-4 text-lg font-semibold text-text-primary">Tax Calculation</div>
                <div className="grid gap-3 md:grid-cols-2">
                  <label className="space-y-2 text-sm text-text-secondary">
                    Tax type
                    <select className="w-full rounded-md border border-border-default bg-background-default px-3 py-2 text-sm" value={taxType} onChange={(event) => setTaxType(event.target.value)}>
                      <option value="GST">GST</option>
                      <option value="TDS">TDS</option>
                      <option value="TCS">TCS</option>
                      <option value="IGST">IGST</option>
                    </select>
                  </label>
                  <label className="space-y-2 text-sm text-text-secondary">
                    Jurisdiction
                    <input className="w-full rounded-md border border-border-default bg-background-default px-3 py-2 text-sm" value={jurisdiction} onChange={(event) => setJurisdiction(event.target.value)} placeholder="Jurisdiction" />
                  </label>
                  <label className="space-y-2 text-sm text-text-secondary">
                    Base amount
                    <input className="w-full rounded-md border border-border-default bg-background-default px-3 py-2 text-sm" type="number" value={baseAmount} onChange={(event) => setBaseAmount(event.target.value)} placeholder="Base amount" />
                  </label>
                  <div className="flex items-end justify-end">
                    <button type="button" onClick={runCalculation} className="inline-flex h-10 items-center justify-center rounded-md bg-accent-primary px-4 text-sm font-semibold text-accent-onPrimary">
                      Calculate tax
                    </button>
                  </div>
                </div>
                {calculation ? (
                  <div className="mt-4 rounded-md border border-border-light bg-background-default p-4 text-sm text-text-secondary">
                    <div className="font-semibold text-text-primary">Calculation result</div>
                    <div className="mt-2 grid gap-2 sm:grid-cols-2">
                      <div>Tax type: {calculation.tax_type}</div>
                      <div>Rate: {calculation.tax_rate}%</div>
                      <div>Tax amount: {formatAmount(calculation.tax_amount)}</div>
                      <div>Total due: {formatAmount(calculation.total_amount)}</div>
                    </div>
                  </div>
                ) : null}
              </div>

              <div className="rounded-md border border-border-default bg-background-surface p-4">
                <div className="mb-4 text-lg font-semibold text-text-primary">Reconciliation</div>
                <label className="space-y-2 text-sm text-text-secondary">
                  Reference ID
                  <input className="w-full rounded-md border border-border-default bg-background-default px-3 py-2 text-sm" value={recReference} onChange={(event) => setRecReference(event.target.value)} placeholder="Reference ID" />
                </label>
                <label className="space-y-2 text-sm text-text-secondary">
                  Reported amount
                  <input className="w-full rounded-md border border-border-default bg-background-default px-3 py-2 text-sm" type="number" value={reportedAmount} onChange={(event) => setReportedAmount(event.target.value)} placeholder="Reported amount" />
                </label>
                <label className="space-y-2 text-sm text-text-secondary">
                  Recorded amount
                  <input className="w-full rounded-md border border-border-default bg-background-default px-3 py-2 text-sm" type="number" value={recordedAmount} onChange={(event) => setRecordedAmount(event.target.value)} placeholder="Recorded amount" />
                </label>
                <button type="button" onClick={submitReconciliation} className="mt-4 inline-flex h-10 items-center justify-center rounded-md bg-accent-primary px-4 text-sm font-semibold text-accent-onPrimary">
                  Reconcile tax
                </button>
                {reconciliationResult ? (
                  <div className="mt-4 rounded-md border border-border-light bg-background-default p-4 text-sm text-text-secondary">
                    <div className="font-semibold text-text-primary">Reconciliation saved</div>
                    <div className="mt-2">Difference: {formatAmount(reconciliationResult.difference_amount)}</div>
                    <div>Status: {reconciliationResult.status}</div>
                  </div>
                ) : null}
              </div>
            </div>

            <div className="grid gap-6">
              <div className="rounded-md border border-border-default bg-background-surface p-4">
                <div className="mb-4 text-lg font-semibold text-text-primary">Tax Returns</div>
                <div className="grid gap-3 md:grid-cols-3">
                  <label className="space-y-2 text-sm text-text-secondary">
                    Return type
                    <select className="w-full rounded-md border border-border-default bg-background-default px-3 py-2 text-sm" value={returnType} onChange={(event) => setReturnType(event.target.value)}>
                      <option value="GSTR-1">GSTR-1</option>
                      <option value="GSTR-3B">GSTR-3B</option>
                      <option value="TDS-1">TDS-1</option>
                      <option value="TDS-2">TDS-2</option>
                    </select>
                  </label>
                  <label className="space-y-2 text-sm text-text-secondary">
                    Period
                    <input className="w-full rounded-md border border-border-default bg-background-default px-3 py-2 text-sm" value={returnPeriod} onChange={(event) => setReturnPeriod(event.target.value)} placeholder="yyyy-mm" />
                  </label>
                  <div className="flex items-end justify-end">
                    <button type="button" onClick={submitReturn} className="inline-flex h-10 items-center justify-center rounded-md bg-accent-primary px-4 text-sm font-semibold text-accent-onPrimary">
                      File return
                    </button>
                  </div>
                </div>
                <label className="mt-3 block space-y-2 text-sm text-text-secondary">
                  Return details
                  <textarea className="h-32 w-full rounded-md border border-border-default bg-background-default px-3 py-2 text-sm" value={returnDetails} onChange={(event) => setReturnDetails(event.target.value)} />
                </label>
                {returnResult ? (
                  <div className="mt-4 rounded-md border border-border-light bg-background-default p-4 text-sm text-text-secondary">
                    <div className="font-semibold text-text-primary">Return filed</div>
                    <div className="mt-2">Type: {returnResult.return_type}</div>
                    <div>Period: {returnResult.period}</div>
                    <div>Status: {returnResult.status}</div>
                  </div>
                ) : null}
              </div>

              <div className="rounded-md border border-border-default bg-background-surface p-4">
                <div className="mb-4 text-lg font-semibold text-text-primary">E-invoice &amp; E-way bill</div>
                <div className="grid gap-3 md:grid-cols-2">
                  <label className="space-y-2 text-sm text-text-secondary">
                    Invoice ID
                    <input className="w-full rounded-md border border-border-default bg-background-default px-3 py-2 text-sm" value={einvoiceId} onChange={(event) => setEinvoiceId(event.target.value)} placeholder="Invoice ID" />
                  </label>
                  <label className="space-y-2 text-sm text-text-secondary">
                    Invoice date
                    <input className="w-full rounded-md border border-border-default bg-background-default px-3 py-2 text-sm" type="date" value={einvoiceDate} onChange={(event) => setEinvoiceDate(event.target.value)} />
                  </label>
                  <label className="space-y-2 text-sm text-text-secondary">
                    Amount
                    <input className="w-full rounded-md border border-border-default bg-background-default px-3 py-2 text-sm" type="number" value={einvoiceAmount} onChange={(event) => setEinvoiceAmount(event.target.value)} placeholder="Amount" />
                  </label>
                  <div className="flex items-end justify-end gap-2">
                    <button type="button" onClick={generateEInvoice} className="inline-flex h-10 items-center justify-center rounded-md bg-accent-primary px-4 text-sm font-semibold text-accent-onPrimary">
                      Generate e-invoice
                    </button>
                    <button type="button" onClick={generateEWayBill} className="inline-flex h-10 items-center justify-center rounded-md bg-background-default px-4 text-sm font-semibold text-text-primary border border-border-default">
                      Generate e-way bill
                    </button>
                  </div>
                </div>
                <div className="grid gap-3 md:grid-cols-2 mt-3">
                  <label className="space-y-2 text-sm text-text-secondary">
                    Vehicle number
                    <input className="w-full rounded-md border border-border-default bg-background-default px-3 py-2 text-sm" value={ewayVehicle} onChange={(event) => setEwayVehicle(event.target.value)} />
                  </label>
                  <label className="space-y-2 text-sm text-text-secondary">
                    Transporter
                    <input className="w-full rounded-md border border-border-default bg-background-default px-3 py-2 text-sm" value={ewayTransporter} onChange={(event) => setEwayTransporter(event.target.value)} />
                  </label>
                  <label className="space-y-2 text-sm text-text-secondary">
                    From
                    <input className="w-full rounded-md border border-border-default bg-background-default px-3 py-2 text-sm" value={ewayFrom} onChange={(event) => setEwayFrom(event.target.value)} />
                  </label>
                  <label className="space-y-2 text-sm text-text-secondary">
                    To
                    <input className="w-full rounded-md border border-border-default bg-background-default px-3 py-2 text-sm" value={ewayTo} onChange={(event) => setEwayTo(event.target.value)} />
                  </label>
                </div>
                <label className="mt-3 space-y-2 text-sm text-text-secondary">
                  Distance (km)
                  <input className="w-full rounded-md border border-border-default bg-background-default px-3 py-2 text-sm" type="number" value={ewayDistance} onChange={(event) => setEwayDistance(event.target.value)} />
                </label>
                {einvoiceResult || ewayResult ? (
                  <div className="mt-4 rounded-md border border-border-light bg-background-default p-4 text-sm text-text-secondary">
                    {einvoiceResult ? (
                      <div>
                        <div className="font-semibold text-text-primary">E-invoice generated</div>
                        <div>ID: {einvoiceResult.invoice_id}</div>
                        <div>IRN: {einvoiceResult.irn}</div>
                      </div>
                    ) : null}
                    {ewayResult ? (
                      <div className="mt-3">
                        <div className="font-semibold text-text-primary">E-way bill generated</div>
                        <div>Number: {ewayResult.ewaybill_number}</div>
                        <div>Vehicle: {ewayResult.vehicle_number}</div>
                      </div>
                    ) : null}
                  </div>
                ) : null}
              </div>
            </div>

            <div className="rounded-md border border-border-default bg-background-surface p-4">
              <div className="mb-4 text-lg font-semibold text-text-primary">Tax Ledger</div>
              <div className="overflow-x-auto">
                <table className="min-w-full text-sm">
                  <thead>
                    <tr className="bg-background-default text-left text-text-secondary">
                      <th className="p-2">Entry</th>
                      <th className="p-2">Type</th>
                      <th className="p-2">Tax Type</th>
                      <th className="p-2">Amount</th>
                      <th className="p-2">Date</th>
                      <th className="p-2">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {ledger.map((entry) => (
                      <tr key={entry.id} className="border-t border-border-light hover:bg-gray-50">
                        <td className="p-2 text-text-primary">{entry.reference_id ?? entry.id}</td>
                        <td className="p-2 text-text-secondary">{entry.entry_type}</td>
                        <td className="p-2 text-text-secondary">{entry.tax_type ?? '-'}</td>
                        <td className="p-2 text-text-primary">{formatAmount(entry.amount)}</td>
                        <td className="p-2 text-text-secondary">{new Date(entry.entry_date).toLocaleDateString()}</td>
                        <td className="p-2 text-text-secondary">{entry.status}</td>
                      </tr>
                    ))}
                    {ledger.length === 0 ? (
                      <tr>
                        <td colSpan={6} className="p-4 text-center text-text-secondary">No tax ledger entries available.</td>
                      </tr>
                    ) : null}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
}
