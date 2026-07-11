/**
 * Exit Status Badge Component
 * Displays status badges for resignations, clearances, settlements, and documents
 */

import React from 'react';
import {
  ResignationStatus,
  ClearanceStatus,
  SettlementStatus,
  RESIGNATION_STATUS_LABELS,
  RESIGNATION_STATUS_COLORS,
  CLEARANCE_STATUS_LABELS,
  CLEARANCE_STATUS_COLORS,
  SETTLEMENT_STATUS_LABELS,
  SETTLEMENT_STATUS_COLORS
} from '@/types/exit.types';

interface ExitStatusBadgeProps {
  status: ResignationStatus | ClearanceStatus | SettlementStatus;
  type: 'resignation' | 'clearance' | 'settlement';
  size?: 'sm' | 'md' | 'lg';
}

const ExitStatusBadge: React.FC<ExitStatusBadgeProps> = ({ 
  status, 
  type,
  size = 'md' 
}) => {
  const getStatusLabel = () => {
    switch (type) {
      case 'resignation':
        return RESIGNATION_STATUS_LABELS[status as ResignationStatus];
      case 'clearance':
        return CLEARANCE_STATUS_LABELS[status as ClearanceStatus];
      case 'settlement':
        return SETTLEMENT_STATUS_LABELS[status as SettlementStatus];
      default:
        return status;
    }
  };

  const getStatusColor = () => {
    switch (type) {
      case 'resignation':
        return RESIGNATION_STATUS_COLORS[status as ResignationStatus];
      case 'clearance':
        return CLEARANCE_STATUS_COLORS[status as ClearanceStatus];
      case 'settlement':
        return SETTLEMENT_STATUS_COLORS[status as SettlementStatus];
      default:
        return 'gray';
    }
  };

  const colorClasses: Record<string, string> = {
    blue: 'bg-blue-100 text-blue-800 border-blue-200',
    green: 'bg-green-100 text-green-800 border-green-200',
    yellow: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    red: 'bg-red-100 text-red-800 border-red-200',
    gray: 'bg-gray-100 text-gray-800 border-gray-200',
    purple: 'bg-purple-100 text-purple-800 border-purple-200',
    orange: 'bg-orange-100 text-orange-800 border-orange-200'
  };

  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-1 text-sm',
    lg: 'px-3 py-1.5 text-base'
  };

  const color = getStatusColor();
  const label = getStatusLabel();

  return (
    <span 
      className={`
        inline-flex items-center font-medium rounded-full border
        ${colorClasses[color] || colorClasses.gray}
        ${sizeClasses[size]}
      `}
    >
      <span className="w-1.5 h-1.5 mr-1.5 rounded-full bg-current opacity-70"></span>
      {label}
    </span>
  );
};

export default ExitStatusBadge;
