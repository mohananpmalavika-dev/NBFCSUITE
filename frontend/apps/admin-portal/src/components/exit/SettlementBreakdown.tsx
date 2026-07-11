/**
 * Settlement Breakdown Component
 * Displays detailed Full & Final settlement breakdown
 */

import React from 'react';
import { ExitSettlement, SettlementComponent, SETTLEMENT_COMPONENT_TYPE_LABELS } from '@/types/exit.types';

interface SettlementBreakdownProps {
  settlement: ExitSettlement;
  components?: SettlementComponent[];
  showDetails?: boolean;
}

const SettlementBreakdown: React.FC<SettlementBreakdownProps> = ({
  settlement,
  components = [],
  showDetails = true
}) => {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 2
    }).format(amount);
  };

  return (
    <div className="space-y-6">
      {/* Summary Card */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6 border border-blue-200">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <p className="text-sm text-gray-600 mb-1">Gross Payable</p>
            <p className="text-2xl font-bold text-green-600">
              {formatCurrency(settlement.gross_payable)}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-600 mb-1">Total Deductions</p>
            <p className="text-2xl font-bold text-red-600">
              {formatCurrency(settlement.total_deductions)}
            </p>
          </div>
          <div className="md:border-l md:border-gray-300 md:pl-6">
            <p className="text-sm text-gray-600 mb-1">Net Payable</p>
            <p className="text-3xl font-bold text-blue-600">
              {formatCurrency(settlement.net_payable)}
            </p>
          </div>
        </div>
      </div>

      {showDetails && (
        <>
          {/* Earnings Section */}
          <div className="border border-gray-200 rounded-lg overflow-hidden">
            <div className="bg-green-50 px-4 py-3 border-b border-green-200">
              <h3 className="text-sm font-semibold text-green-800 flex items-center">
                <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                Earnings
              </h3>
            </div>
            <div className="bg-white divide-y divide-gray-200">
              {/* Basic Salary */}
              {settlement.basic_salary_amount > 0 && (
                <div className="px-4 py-3 flex justify-between items-center hover:bg-gray-50">
                  <div>
                    <p className="text-sm font-medium text-gray-900">Basic Salary</p>
                    {settlement.basic_salary_days && (
                      <p className="text-xs text-gray-500">
                        {settlement.basic_salary_days} days
                      </p>
                    )}
                  </div>
                  <p className="text-sm font-semibold text-gray-900">
                    {formatCurrency(settlement.basic_salary_amount)}
                  </p>
                </div>
              )}

              {/* Leave Encashment */}
              {settlement.leave_encashment_amount > 0 && (
                <div className="px-4 py-3 flex justify-between items-center hover:bg-gray-50">
                  <div>
                    <p className="text-sm font-medium text-gray-900">Leave Encashment</p>
                    <p className="text-xs text-gray-500">
                      {settlement.encashable_leaves} days of {settlement.total_leave_balance} total
                    </p>
                  </div>
                  <p className="text-sm font-semibold text-gray-900">
                    {formatCurrency(settlement.leave_encashment_amount)}
                  </p>
                </div>
              )}

              {/* Gratuity */}
              {settlement.gratuity_eligible && settlement.gratuity_amount > 0 && (
                <div className="px-4 py-3 flex justify-between items-center hover:bg-gray-50">
                  <div>
                    <p className="text-sm font-medium text-gray-900">Gratuity</p>
                    {settlement.years_of_service && (
                      <p className="text-xs text-gray-500">
                        {settlement.years_of_service} years of service
                      </p>
                    )}
                  </div>
                  <p className="text-sm font-semibold text-gray-900">
                    {formatCurrency(settlement.gratuity_amount)}
                  </p>
                </div>
              )}

              {/* Bonus */}
              {settlement.bonus_amount > 0 && (
                <div className="px-4 py-3 flex justify-between items-center hover:bg-gray-50">
                  <div>
                    <p className="text-sm font-medium text-gray-900">Bonus</p>
                  </div>
                  <p className="text-sm font-semibold text-gray-900">
                    {formatCurrency(settlement.bonus_amount)}
                  </p>
                </div>
              )}

              {/* Incentive */}
              {settlement.incentive_amount > 0 && (
                <div className="px-4 py-3 flex justify-between items-center hover:bg-gray-50">
                  <div>
                    <p className="text-sm font-medium text-gray-900">Incentive</p>
                  </div>
                  <p className="text-sm font-semibold text-gray-900">
                    {formatCurrency(settlement.incentive_amount)}
                  </p>
                </div>
              )}

              {/* Reimbursements */}
              {settlement.pending_reimbursement_amount > 0 && (
                <div className="px-4 py-3 flex justify-between items-center hover:bg-gray-50">
                  <div>
                    <p className="text-sm font-medium text-gray-900">Pending Reimbursements</p>
                  </div>
                  <p className="text-sm font-semibold text-gray-900">
                    {formatCurrency(settlement.pending_reimbursement_amount)}
                  </p>
                </div>
              )}

              {/* Components - Earnings */}
              {components.filter(c => !c.is_deduction).map((component) => (
                <div key={component.id} className="px-4 py-3 flex justify-between items-center hover:bg-gray-50">
                  <div>
                    <p className="text-sm font-medium text-gray-900">{component.component_name}</p>
                    {component.description && (
                      <p className="text-xs text-gray-500">{component.description}</p>
                    )}
                  </div>
                  <p className="text-sm font-semibold text-gray-900">
                    {formatCurrency(component.amount)}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Deductions Section */}
          <div className="border border-gray-200 rounded-lg overflow-hidden">
            <div className="bg-red-50 px-4 py-3 border-b border-red-200">
              <h3 className="text-sm font-semibold text-red-800 flex items-center">
                <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
                </svg>
                Deductions
              </h3>
            </div>
            <div className="bg-white divide-y divide-gray-200">
              {/* Notice Pay Recovery */}
              {settlement.notice_pay_recovery > 0 && (
                <div className="px-4 py-3 flex justify-between items-center hover:bg-gray-50">
                  <div>
                    <p className="text-sm font-medium text-gray-900">Notice Pay Recovery</p>
                    <p className="text-xs text-gray-500">
                      {settlement.notice_period_shortfall_days} days shortfall
                    </p>
                  </div>
                  <p className="text-sm font-semibold text-red-600">
                    - {formatCurrency(settlement.notice_pay_recovery)}
                  </p>
                </div>
              )}

              {/* Loan Recovery */}
              {settlement.loan_recovery > 0 && (
                <div className="px-4 py-3 flex justify-between items-center hover:bg-gray-50">
                  <div>
                    <p className="text-sm font-medium text-gray-900">Loan Recovery</p>
                  </div>
                  <p className="text-sm font-semibold text-red-600">
                    - {formatCurrency(settlement.loan_recovery)}
                  </p>
                </div>
              )}

              {/* Advance Recovery */}
              {settlement.advance_recovery > 0 && (
                <div className="px-4 py-3 flex justify-between items-center hover:bg-gray-50">
                  <div>
                    <p className="text-sm font-medium text-gray-900">Advance Recovery</p>
                  </div>
                  <p className="text-sm font-semibold text-red-600">
                    - {formatCurrency(settlement.advance_recovery)}
                  </p>
                </div>
              )}

              {/* Asset Loss Recovery */}
              {settlement.asset_loss_recovery > 0 && (
                <div className="px-4 py-3 flex justify-between items-center hover:bg-gray-50">
                  <div>
                    <p className="text-sm font-medium text-gray-900">Asset Loss Recovery</p>
                  </div>
                  <p className="text-sm font-semibold text-red-600">
                    - {formatCurrency(settlement.asset_loss_recovery)}
                  </p>
                </div>
              )}

              {/* Other Recovery */}
              {settlement.other_recovery > 0 && (
                <div className="px-4 py-3 flex justify-between items-center hover:bg-gray-50">
                  <div>
                    <p className="text-sm font-medium text-gray-900">Other Recovery</p>
                    {settlement.recovery_remarks && (
                      <p className="text-xs text-gray-500">{settlement.recovery_remarks}</p>
                    )}
                  </div>
                  <p className="text-sm font-semibold text-red-600">
                    - {formatCurrency(settlement.other_recovery)}
                  </p>
                </div>
              )}

              {/* TDS */}
              {settlement.tds_amount > 0 && (
                <div className="px-4 py-3 flex justify-between items-center hover:bg-gray-50">
                  <div>
                    <p className="text-sm font-medium text-gray-900">TDS</p>
                  </div>
                  <p className="text-sm font-semibold text-red-600">
                    - {formatCurrency(settlement.tds_amount)}
                  </p>
                </div>
              )}

              {/* Professional Tax */}
              {settlement.professional_tax > 0 && (
                <div className="px-4 py-3 flex justify-between items-center hover:bg-gray-50">
                  <div>
                    <p className="text-sm font-medium text-gray-900">Professional Tax</p>
                  </div>
                  <p className="text-sm font-semibold text-red-600">
                    - {formatCurrency(settlement.professional_tax)}
                  </p>
                </div>
              )}

              {/* Components - Deductions */}
              {components.filter(c => c.is_deduction).map((component) => (
                <div key={component.id} className="px-4 py-3 flex justify-between items-center hover:bg-gray-50">
                  <div>
                    <p className="text-sm font-medium text-gray-900">{component.component_name}</p>
                    {component.description && (
                      <p className="text-xs text-gray-500">{component.description}</p>
                    )}
                  </div>
                  <p className="text-sm font-semibold text-red-600">
                    - {formatCurrency(component.amount)}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Calculation Remarks */}
          {settlement.calculation_remarks && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h4 className="text-sm font-medium text-blue-900 mb-2">Calculation Notes</h4>
              <p className="text-sm text-blue-800">{settlement.calculation_remarks}</p>
            </div>
          )}

          {/* Settlement Period */}
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <h4 className="text-sm font-medium text-gray-900 mb-2">Settlement Period</h4>
            <div className="flex items-center text-sm text-gray-700">
              <svg className="w-4 h-4 mr-2 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <span>
                {new Date(settlement.settlement_from_date).toLocaleDateString()} to{' '}
                {new Date(settlement.settlement_to_date).toLocaleDateString()}
              </span>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default SettlementBreakdown;
