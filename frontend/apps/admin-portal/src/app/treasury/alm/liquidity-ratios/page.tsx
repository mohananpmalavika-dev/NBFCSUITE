"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Download, RefreshCw, TrendingUp, TrendingDown, AlertTriangle, CheckCircle } from "lucide-react";
import { almService } from '@/services/almService';
import type { LiquidityRatiosResponse } from '@/types/alm';
import { formatCurrency } from '@/lib/utils';

interface RatioThresholds {
  critical: number;
  warning: number;
  good: number;
}

const RATIO_THRESHOLDS: Record<string, RatioThresholds> = {
  lcr: { critical: 60, warning: 80, good: 100 },
  nsfr: { critical: 80, warning: 90, good: 100 },
  current_ratio: { critical: 0.8, warning: 1.0, good: 1.5 },
  quick_ratio: { critical: 0.5, warning: 0.8, good: 1.0 },
  slr: { critical: 18, warning: 20, good: 25 },
  crr: { critical: 3, warning: 4, good: 4.5 },
};

export default function LiquidityRatiosPage() {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<LiquidityRatiosResponse | null>(null);
  const [selectedDate, setSelectedDate] = useState<string>(
    new Date().toISOString().split('T')[0]
  );

  useEffect(() => {
    fetchData();
  }, [selectedDate]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const response = await almService.getLiquidityRatios(selectedDate);
      setData(response);
    } catch (error) {
      console.error('Failed to fetch liquidity ratios:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    try {
      await almService.exportLiquidityRatios(selectedDate, 'excel');
    } catch (error) {
      console.error('Export failed:', error);
    }
  };

  const getRatioStatus = (ratioKey: string, value: number | null): {
    status: 'good' | 'warning' | 'critical';
    icon: React.ReactNode;
    color: string;
  } => {
    if (value === null) {
      return { status: 'warning', icon: <AlertTriangle className="h-4 w-4" />, color: 'text-gray-500' };
    }

    const threshold = RATIO_THRESHOLDS[ratioKey];
    if (!threshold) {
      return { status: 'good', icon: <CheckCircle className="h-4 w-4" />, color: 'text-blue-600' };
    }

    if (value >= threshold.good) {
      return { status: 'good', icon: <CheckCircle className="h-4 w-4" />, color: 'text-green-600' };
    } else if (value >= threshold.warning) {
      return { status: 'warning', icon: <AlertTriangle className="h-4 w-4" />, color: 'text-yellow-600' };
    } else {
      return { status: 'critical', icon: <TrendingDown className="h-4 w-4" />, color: 'text-red-600' };
    }
  };

  const formatRatio = (value: number | null, isPercentage: boolean = true): string => {
    if (value === null) return 'N/A';
    return isPercentage ? `${value.toFixed(2)}%` : value.toFixed(2);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <RefreshCw className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!data) {
    return (
      <div className="flex items-center justify-center h-96">
        <p className="text-muted-foreground">No data available</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Liquidity Ratios</h1>
          <p className="text-muted-foreground">
            Comprehensive liquidity metrics and regulatory compliance indicators
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={fetchData}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button onClick={handleExport}>
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* Date Selector */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center gap-4">
            <label className="text-sm font-medium">Analysis Date:</label>
            <input
              type="date"
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
              className="border rounded px-3 py-2"
            />
          </div>
        </CardContent>
      </Card>

      {/* Key Regulatory Ratios */}
      <div className="grid gap-4 md:grid-cols-3">
        <RatioCard
          title="LCR (Liquidity Coverage Ratio)"
          value={data.lcr}
          threshold={100}
          description="High-quality liquid assets vs. net cash outflows over 30 days"
          ratioKey="lcr"
        />
        <RatioCard
          title="NSFR (Net Stable Funding Ratio)"
          value={data.nsfr}
          threshold={100}
          description="Available stable funding vs. required stable funding"
          ratioKey="nsfr"
        />
        <RatioCard
          title="SLR (Statutory Liquidity Ratio)"
          value={data.slr}
          threshold={18}
          description="Liquid assets as percentage of net demand and time liabilities"
          ratioKey="slr"
        />
      </div>

      {/* Traditional Liquidity Ratios */}
      <Card>
        <CardHeader>
          <CardTitle>Traditional Liquidity Ratios</CardTitle>
          <CardDescription>Classic financial ratios for liquidity assessment</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            <RatioMetric
              label="Current Ratio"
              value={data.current_ratio}
              ratioKey="current_ratio"
              info="Current assets divided by current liabilities"
            />
            <RatioMetric
              label="Quick Ratio"
              value={data.quick_ratio}
              ratioKey="quick_ratio"
              info="Quick assets divided by current liabilities"
            />
            <RatioMetric
              label="Cash Ratio"
              value={data.cash_ratio}
              ratioKey="cash_ratio"
              info="Cash and cash equivalents divided by current liabilities"
            />
            <RatioMetric
              label="Loan to Deposit Ratio"
              value={data.loan_to_deposit_ratio}
              isPercentage={true}
              info="Total loans divided by total deposits"
            />
            <RatioMetric
              label="Liquid Asset Ratio"
              value={data.liquid_asset_ratio}
              isPercentage={true}
              info="Liquid assets divided by total assets"
            />
            <RatioMetric
              label="Advances to Assets Ratio"
              value={data.advances_to_assets_ratio}
              isPercentage={true}
              info="Total advances divided by total assets"
            />
          </div>
        </CardContent>
      </Card>

      {/* Regulatory Reserve Ratios */}
      <Card>
        <CardHeader>
          <CardTitle>Reserve Ratios</CardTitle>
          <CardDescription>Regulatory reserve requirements and compliance</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-4">
              <RatioMetric
                label="CRR (Cash Reserve Ratio)"
                value={data.crr}
                ratioKey="crr"
                isPercentage={true}
                info="Cash reserves with RBI as % of NDTL"
              />
              <div className="pl-4 border-l-2 border-muted">
                <p className="text-sm text-muted-foreground">Required CRR Balance</p>
                <p className="text-xl font-bold">{formatCurrency(data.crr_balance)}</p>
              </div>
            </div>
            <div className="space-y-4">
              <RatioMetric
                label="SLR (Statutory Liquidity Ratio)"
                value={data.slr}
                ratioKey="slr"
                isPercentage={true}
                info="Liquid assets as % of NDTL"
              />
              <div className="pl-4 border-l-2 border-muted">
                <p className="text-sm text-muted-foreground">Required SLR Holdings</p>
                <p className="text-xl font-bold">{formatCurrency(data.slr_holdings)}</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Basel III Liquidity Metrics */}
      <Card>
        <CardHeader>
          <CardTitle>Basel III Liquidity Metrics</CardTitle>
          <CardDescription>International regulatory framework compliance</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {/* LCR Details */}
            <div className="p-4 border rounded-lg">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-lg">LCR Components</h3>
                <Badge variant={data.lcr && data.lcr >= 100 ? "default" : "destructive"}>
                  {formatRatio(data.lcr)}
                </Badge>
              </div>
              <div className="grid gap-3 md:grid-cols-2">
                <div>
                  <p className="text-sm text-muted-foreground">High-Quality Liquid Assets (HQLA)</p>
                  <p className="text-lg font-semibold text-green-600">{formatCurrency(data.hqla)}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Net Cash Outflows (30 days)</p>
                  <p className="text-lg font-semibold text-red-600">{formatCurrency(data.net_cash_outflows_30d)}</p>
                </div>
              </div>
              <div className="mt-3">
                <div className="w-full bg-muted rounded-full h-3">
                  <div
                    className={`h-3 rounded-full ${data.lcr && data.lcr >= 100 ? 'bg-green-600' : 'bg-red-600'}`}
                    style={{ width: `${Math.min(data.lcr || 0, 100)}%` }}
                  />
                </div>
                <p className="text-xs text-muted-foreground mt-1">Minimum requirement: 100%</p>
              </div>
            </div>

            {/* NSFR Details */}
            <div className="p-4 border rounded-lg">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-lg">NSFR Components</h3>
                <Badge variant={data.nsfr && data.nsfr >= 100 ? "default" : "destructive"}>
                  {formatRatio(data.nsfr)}
                </Badge>
              </div>
              <div className="grid gap-3 md:grid-cols-2">
                <div>
                  <p className="text-sm text-muted-foreground">Available Stable Funding (ASF)</p>
                  <p className="text-lg font-semibold text-green-600">{formatCurrency(data.available_stable_funding)}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Required Stable Funding (RSF)</p>
                  <p className="text-lg font-semibold text-red-600">{formatCurrency(data.required_stable_funding)}</p>
                </div>
              </div>
              <div className="mt-3">
                <div className="w-full bg-muted rounded-full h-3">
                  <div
                    className={`h-3 rounded-full ${data.nsfr && data.nsfr >= 100 ? 'bg-green-600' : 'bg-red-600'}`}
                    style={{ width: `${Math.min(data.nsfr || 0, 100)}%` }}
                  />
                </div>
                <p className="text-xs text-muted-foreground mt-1">Minimum requirement: 100%</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Additional Liquidity Metrics */}
      <Card>
        <CardHeader>
          <CardTitle>Additional Liquidity Metrics</CardTitle>
          <CardDescription>Supplementary indicators for comprehensive assessment</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            <RatioMetric
              label="Deposit Concentration Ratio"
              value={data.deposit_concentration_ratio}
              isPercentage={true}
              info="Top 20 depositors as % of total deposits"
            />
            <RatioMetric
              label="Interbank Ratio"
              value={data.interbank_ratio}
              isPercentage={true}
              info="Interbank borrowings as % of total liabilities"
            />
            <RatioMetric
              label="Wholesale Funding Ratio"
              value={data.wholesale_funding_ratio}
              isPercentage={true}
              info="Wholesale funding as % of total funding"
            />
            <RatioMetric
              label="Core Deposit Ratio"
              value={data.core_deposit_ratio}
              isPercentage={true}
              info="Core deposits as % of total deposits"
            />
            <RatioMetric
              label="Volatile Liability Ratio"
              value={data.volatile_liability_ratio}
              isPercentage={true}
              info="Volatile liabilities as % of total liabilities"
            />
            <RatioMetric
              label="Liquidity Cushion Ratio"
              value={data.liquidity_cushion_ratio}
              isPercentage={true}
              info="Excess liquidity as % of total assets"
            />
          </div>
        </CardContent>
      </Card>

      {/* Contractual Maturity Mismatch */}
      <Card>
        <CardHeader>
          <CardTitle>Contractual Maturity Mismatch</CardTitle>
          <CardDescription>Short-term liquidity risk indicators</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <div className="p-4 border rounded-lg">
              <p className="text-sm text-muted-foreground mb-2">1-30 Days Mismatch</p>
              <p className={`text-2xl font-bold ${
                data.maturity_mismatch_1_30d && data.maturity_mismatch_1_30d >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                {formatCurrency(data.maturity_mismatch_1_30d || 0)}
              </p>
            </div>
            <div className="p-4 border rounded-lg">
              <p className="text-sm text-muted-foreground mb-2">31-90 Days Mismatch</p>
              <p className={`text-2xl font-bold ${
                data.maturity_mismatch_31_90d && data.maturity_mismatch_31_90d >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                {formatCurrency(data.maturity_mismatch_31_90d || 0)}
              </p>
            </div>
            <div className="p-4 border rounded-lg">
              <p className="text-sm text-muted-foreground mb-2">91-180 Days Mismatch</p>
              <p className={`text-2xl font-bold ${
                data.maturity_mismatch_91_180d && data.maturity_mismatch_91_180d >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                {formatCurrency(data.maturity_mismatch_91_180d || 0)}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Compliance Status */}
      <Card>
        <CardHeader>
          <CardTitle>Regulatory Compliance Status</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <ComplianceItem
              label="LCR Compliance"
              required={100}
              actual={data.lcr || 0}
              unit="%"
            />
            <ComplianceItem
              label="NSFR Compliance"
              required={100}
              actual={data.nsfr || 0}
              unit="%"
            />
            <ComplianceItem
              label="SLR Compliance"
              required={18}
              actual={data.slr || 0}
              unit="%"
            />
            <ComplianceItem
              label="CRR Compliance"
              required={4}
              actual={data.crr || 0}
              unit="%"
            />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function RatioCard({
  title,
  value,
  threshold,
  description,
  ratioKey
}: {
  title: string;
  value: number | null;
  threshold: number;
  description: string;
  ratioKey: string;
}) {
  const status = value !== null && value >= threshold ? 'compliant' : 'non-compliant';
  
  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold">{value !== null ? value.toFixed(2) : 'N/A'}</span>
            <span className="text-muted-foreground">%</span>
          </div>
          <Badge variant={status === 'compliant' ? 'default' : 'destructive'}>
            {status === 'compliant' ? 'Compliant' : 'Below Threshold'}
          </Badge>
          <p className="text-xs text-muted-foreground">{description}</p>
          <div className="pt-2">
            <p className="text-xs text-muted-foreground mb-1">Minimum: {threshold}%</p>
            <div className="w-full bg-muted rounded-full h-2">
              <div
                className={`h-2 rounded-full ${status === 'compliant' ? 'bg-green-600' : 'bg-red-600'}`}
                style={{ width: `${Math.min((value || 0) / threshold * 100, 100)}%` }}
              />
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function RatioMetric({
  label,
  value,
  ratioKey,
  isPercentage = false,
  info
}: {
  label: string;
  value: number | null;
  ratioKey?: string;
  isPercentage?: boolean;
  info?: string;
}) {
  const status = ratioKey ? getRatioStatus(ratioKey, value) : null;
  
  return (
    <div className="p-4 border rounded-lg">
      <div className="flex items-center justify-between mb-2">
        <p className="text-sm font-medium">{label}</p>
        {status && <span className={status.color}>{status.icon}</span>}
      </div>
      <p className="text-2xl font-bold">
        {value !== null ? (isPercentage ? `${value.toFixed(2)}%` : value.toFixed(2)) : 'N/A'}
      </p>
      {info && <p className="text-xs text-muted-foreground mt-2">{info}</p>}
    </div>
  );
}

function ComplianceItem({
  label,
  required,
  actual,
  unit
}: {
  label: string;
  required: number;
  actual: number;
  unit: string;
}) {
  const isCompliant = actual >= required;
  const percentage = (actual / required) * 100;
  
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium">{label}</span>
        <div className="flex items-center gap-2">
          <span className="text-sm">{actual.toFixed(2)}{unit} / {required}{unit}</span>
          {isCompliant ? (
            <CheckCircle className="h-4 w-4 text-green-600" />
          ) : (
            <AlertTriangle className="h-4 w-4 text-red-600" />
          )}
        </div>
      </div>
      <div className="w-full bg-muted rounded-full h-2">
        <div
          className={`h-2 rounded-full ${isCompliant ? 'bg-green-600' : 'bg-red-600'}`}
          style={{ width: `${Math.min(percentage, 100)}%` }}
        />
      </div>
    </div>
  );
}

function getRatioStatus(ratioKey: string, value: number | null) {
  if (value === null) {
    return { status: 'warning', icon: <AlertTriangle className="h-4 w-4" />, color: 'text-gray-500' };
  }

  const threshold = RATIO_THRESHOLDS[ratioKey];
  if (!threshold) {
    return { status: 'good', icon: <CheckCircle className="h-4 w-4" />, color: 'text-blue-600' };
  }

  if (value >= threshold.good) {
    return { status: 'good', icon: <CheckCircle className="h-4 w-4" />, color: 'text-green-600' };
  } else if (value >= threshold.warning) {
    return { status: 'warning', icon: <AlertTriangle className="h-4 w-4" />, color: 'text-yellow-600' };
  } else {
    return { status: 'critical', icon: <TrendingDown className="h-4 w-4" />, color: 'text-red-600' };
  }
}
