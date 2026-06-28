import type { ReactNode } from 'react';

export type DashboardPersona =
  | 'executive'
  | 'branch'
  | 'hr'
  | 'accounting'
  | 'lending'
  | 'customer'
  | 'treasury'
  | 'risk';

export type WidgetCategory =
  | 'kpi'
  | 'alert'
  | 'quick-action'
  | 'chart'
  | 'task'
  | 'approval'
  | 'activity'
  | 'ai'
  | 'forecast'
  | 'risk';

export interface DashboardWidgetContract {
  id: string;
  title: string;
  category: WidgetCategory;
  permissions?: string[];
  refreshPolicy: string;
  drilldownTarget?: string;
  exportable?: boolean;
  supportedSizes: Array<'sm' | 'md' | 'lg' | 'xl' | 'full'>;
}

export interface DashboardAction {
  label: string;
  icon?: ReactNode;
  onClick?: () => void;
}
