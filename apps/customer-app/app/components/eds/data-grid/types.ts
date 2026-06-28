import type { ReactNode } from 'react';

export type GridDensity = 'comfortable' | 'compact';
export type GridViewMode = 'table' | 'cards';
export type GridSortDirection = 'asc' | 'desc';
export type GridStatus = 'draft' | 'pending' | 'approved' | 'rejected' | 'closed';

export interface GridColumn<Row> {
  key: keyof Row & string;
  label: string;
  sortable?: boolean;
  filterable?: boolean;
  hidden?: boolean;
  pinned?: 'left' | 'right';
  align?: 'left' | 'right';
  render?: (row: Row) => ReactNode;
}

export interface GridSavedView {
  id: string;
  label: string;
  shared?: boolean;
  search?: string;
  visibleColumns?: string[];
}

export interface GridBulkAction<Row> {
  label: string;
  permission?: string;
  onAction?: (rows: Row[]) => void;
}

export interface GridRowAction<Row> {
  label: string;
  onAction?: (row: Row) => void;
}

export interface GridPaginationState {
  page: number;
  pageSize: number;
}

export interface GridEvent {
  name:
    | 'GRID_OPENED'
    | 'SEARCH_EXECUTED'
    | 'FILTER_APPLIED'
    | 'VIEW_CHANGED'
    | 'ROW_SELECTED'
    | 'BULK_ACTION'
    | 'EXPORT_COMPLETED'
    | 'AI_REQUESTED';
  metadata?: Record<string, string | number | boolean>;
}

export interface DataGridContract {
  id: string;
  module: string;
  supportsSelection: boolean;
  supportsSavedViews: boolean;
  supportsColumnManager: boolean;
  supportsExport: boolean;
  supportsAuditMode: boolean;
  supportsAiAssistant: boolean;
  performanceTarget: {
    searchMs: number;
    sortMs: number;
    exportMs: number;
  };
}
