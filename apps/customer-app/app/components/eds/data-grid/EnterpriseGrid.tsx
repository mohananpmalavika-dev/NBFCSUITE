'use client';

import { useEffect, useMemo, useRef, useState } from 'react';
import type { KeyboardEvent } from 'react';
import { ArrowDown, ArrowUp, MoreHorizontal } from 'lucide-react';
import { Badge } from '../foundation/Badge';
import { Button } from '../foundation/Button';
import { EmptyState } from '../feedback/EmptyState';
import { cn } from '../utils/cn';
import { AIGridAssistant } from './AIGridAssistant';
import { BulkActions } from './BulkActions';
import { ColumnManager } from './ColumnManager';
import { GridPagination } from './GridPagination';
import { GridToolbar } from './GridToolbar';
import { SavedViews } from './SavedViews';
import type {
  GridBulkAction,
  GridColumn,
  GridDensity,
  GridEvent,
  GridRowAction,
  GridSavedView,
  GridSortDirection,
  GridStatus,
  GridViewMode,
} from './types';

export interface EnterpriseGridProps<Row extends { id: string; status?: GridStatus }> {
  title: string;
  description?: string;
  columns: Array<GridColumn<Row>>;
  rows: Row[];
  savedViews?: GridSavedView[];
  bulkActions?: Array<GridBulkAction<Row>>;
  rowActions?: Array<GridRowAction<Row>>;
  pageSize?: number;
  auditMode?: boolean;
  onEvent?: (event: GridEvent) => void;
}

const alignClassMap = {
  left: 'text-left',
  right: 'text-right',
};

const densityClassMap: Record<GridDensity, string> = {
  comfortable: 'px-4 py-3',
  compact: 'px-3 py-2',
};

const statusToneMap = {
  draft: 'neutral',
  pending: 'warning',
  approved: 'success',
  rejected: 'danger',
  closed: 'accent',
} as const;

function stringifyCell(value: unknown) {
  if (value === null || value === undefined) {
    return '';
  }

  return String(value);
}

export function EnterpriseGrid<Row extends { id: string; status?: GridStatus }>({
  title,
  description,
  columns,
  rows,
  savedViews = [],
  bulkActions = [],
  rowActions = [],
  pageSize = 5,
  auditMode = false,
  onEvent,
}: EnterpriseGridProps<Row>) {
  const [searchQuery, setSearchQuery] = useState('');
  const [activeViewId, setActiveViewId] = useState(savedViews[0]?.id);
  const [visibleColumnKeys, setVisibleColumnKeys] = useState<string[]>(
    columns.filter((column) => !column.hidden).map((column) => column.key),
  );
  const [selectedRowIds, setSelectedRowIds] = useState<string[]>([]);
  const [sortKey, setSortKey] = useState<string | null>(null);
  const [sortDirection, setSortDirection] = useState<GridSortDirection>('asc');
  const [page, setPage] = useState(1);
  const [density, setDensity] = useState<GridDensity>('comfortable');
  const [viewMode, setViewMode] = useState<GridViewMode>('table');
  const searchInputRef = useRef<HTMLDivElement>(null);

  const visibleColumns = useMemo(
    () => columns.filter((column) => visibleColumnKeys.includes(column.key)),
    [columns, visibleColumnKeys],
  );

  const filteredRows = useMemo(() => {
    const normalizedQuery = searchQuery.trim().toLowerCase();

    if (!normalizedQuery) {
      return rows;
    }

    return rows.filter((row) =>
      columns.some((column) =>
        stringifyCell(row[column.key]).toLowerCase().includes(normalizedQuery),
      ),
    );
  }, [columns, rows, searchQuery]);

  const sortedRows = useMemo(() => {
    if (!sortKey) {
      return filteredRows;
    }

    return [...filteredRows].sort((first, second) => {
      const a = stringifyCell(first[sortKey as keyof Row]);
      const b = stringifyCell(second[sortKey as keyof Row]);
      const result = a.localeCompare(b, undefined, { numeric: true });
      return sortDirection === 'asc' ? result : -result;
    });
  }, [filteredRows, sortDirection, sortKey]);

  const paginatedRows = useMemo(() => {
    const start = (page - 1) * pageSize;
    return sortedRows.slice(start, start + pageSize);
  }, [page, pageSize, sortedRows]);

  const selectedRows = useMemo(
    () => rows.filter((row) => selectedRowIds.includes(row.id)),
    [rows, selectedRowIds],
  );

  useEffect(() => {
    onEvent?.({ name: 'GRID_OPENED', metadata: { rows: rows.length } });
  }, [onEvent, rows.length]);

  function emit(name: GridEvent['name'], metadata?: GridEvent['metadata']) {
    onEvent?.({ name, metadata });
  }

  function handleSearchChange(value: string) {
    setSearchQuery(value);
    setPage(1);
    emit('SEARCH_EXECUTED', { queryLength: value.length });
  }

  function handleSort(column: GridColumn<Row>) {
    if (!column.sortable) {
      return;
    }

    if (sortKey === column.key) {
      setSortDirection((current) => (current === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortKey(column.key);
      setSortDirection('asc');
    }
  }

  function handleToggleRow(rowId: string) {
    setSelectedRowIds((current) => {
      const next = current.includes(rowId)
        ? current.filter((id) => id !== rowId)
        : [...current, rowId];
      emit('ROW_SELECTED', { selected: next.length });
      return next;
    });
  }

  function handleToggleAll() {
    const pageIds = paginatedRows.map((row) => row.id);
    const allSelected = pageIds.every((id) => selectedRowIds.includes(id));
    const next = allSelected
      ? selectedRowIds.filter((id) => !pageIds.includes(id))
      : Array.from(new Set([...selectedRowIds, ...pageIds]));
    setSelectedRowIds(next);
    emit('ROW_SELECTED', { selected: next.length });
  }

  function handleViewChange(view: GridSavedView) {
    setActiveViewId(view.id);
    setSearchQuery(view.search ?? '');
    setVisibleColumnKeys(view.visibleColumns ?? columns.map((column) => column.key));
    setPage(1);
    emit('VIEW_CHANGED', { view: view.label });
  }

  function handleToggleColumn(key: string) {
    setVisibleColumnKeys((current) =>
      current.includes(key) ? current.filter((columnKey) => columnKey !== key) : [...current, key],
    );
  }

  function handleGridKeyDown(event: KeyboardEvent<HTMLDivElement>) {
    if (event.ctrlKey && event.key.toLowerCase() === 'a') {
      event.preventDefault();
      setSelectedRowIds(rows.map((row) => row.id));
      emit('ROW_SELECTED', { selected: rows.length });
    }

    if (event.ctrlKey && event.key.toLowerCase() === 'e') {
      event.preventDefault();
      emit('EXPORT_COMPLETED', { format: 'csv' });
    }

    if (event.ctrlKey && event.key.toLowerCase() === 'f') {
      event.preventDefault();
      searchInputRef.current?.querySelector('input')?.focus();
    }
  }

  return (
    <section
      className="overflow-hidden rounded-xl border border-border-default bg-background-surface shadow-sm"
      onKeyDown={handleGridKeyDown}
      tabIndex={0}
    >
      <div className="flex flex-col gap-3 border-b border-border-default p-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-accent-primary">EDS-008</p>
          <h2 className="mt-2 text-2xl font-semibold text-text-primary">{title}</h2>
          {description ? <p className="mt-2 max-w-3xl text-sm leading-6 text-text-secondary">{description}</p> : null}
        </div>
        <div className="flex flex-wrap gap-2">
          <Button
            size="sm"
            variant={viewMode === 'table' ? 'primary' : 'secondary'}
            onClick={() => setViewMode('table')}
          >
            Table
          </Button>
          <Button
            size="sm"
            variant={viewMode === 'cards' ? 'primary' : 'secondary'}
            onClick={() => setViewMode('cards')}
          >
            Cards
          </Button>
          <Button
            size="sm"
            variant="secondary"
            onClick={() => setDensity((current) => (current === 'comfortable' ? 'compact' : 'comfortable'))}
          >
            {density === 'comfortable' ? 'Compact' : 'Comfortable'}
          </Button>
        </div>
      </div>

      <div ref={searchInputRef}>
        <GridToolbar
          searchQuery={searchQuery}
          onSearchChange={handleSearchChange}
          onRefresh={() => emit('FILTER_APPLIED', { refresh: true })}
          onExport={() => emit('EXPORT_COMPLETED', { format: 'csv' })}
          onAiRequest={() => emit('AI_REQUESTED', { selected: selectedRowIds.length })}
        />
      </div>

      <div className="space-y-3 border-b border-border-default bg-background-elevated p-4">
        {savedViews.length > 0 ? (
          <SavedViews views={savedViews} activeViewId={activeViewId} onViewChange={handleViewChange} />
        ) : null}
        <ColumnManager columns={columns} visibleColumnKeys={visibleColumnKeys} onToggleColumn={handleToggleColumn} />
      </div>

      <BulkActions<Row>
        selectedRows={selectedRows}
        actions={bulkActions.map((action) => ({
          ...action,
          onAction: (selected) => {
            action.onAction?.(selected);
            emit('BULK_ACTION', { action: action.label, selected: selected.length });
          },
        }))}
        onClearSelection={() => setSelectedRowIds([])}
      />

      <div className="grid gap-0 xl:grid-cols-[minmax(0,1fr)_320px]">
        <div className="min-w-0">
          {sortedRows.length === 0 ? (
            <div className="p-4">
              <EmptyState title="No records found" description="Adjust search, filters, or saved views." />
            </div>
          ) : viewMode === 'table' ? (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-border-default text-sm">
                <thead className="bg-background-elevated">
                  <tr>
                    <th className="w-12 px-4 py-3 text-left">
                      <input
                        type="checkbox"
                        aria-label="Select page rows"
                        checked={paginatedRows.every((row) => selectedRowIds.includes(row.id))}
                        onChange={handleToggleAll}
                        className="h-4 w-4 rounded border-border-default text-accent-primary focus:ring-border-focus"
                      />
                    </th>
                    {visibleColumns.map((column) => {
                      const sorted = sortKey === column.key;

                      return (
                        <th
                          key={column.key}
                          scope="col"
                          className={cn(
                            'whitespace-nowrap px-4 py-3 text-xs font-semibold uppercase tracking-[0.16em] text-text-muted',
                            alignClassMap[column.align ?? 'left'],
                          )}
                        >
                          <button
                            type="button"
                            className="inline-flex items-center gap-2"
                            onClick={() => handleSort(column)}
                          >
                            {column.label}
                            {sorted ? (
                              sortDirection === 'asc' ? (
                                <ArrowUp className="h-3.5 w-3.5" />
                              ) : (
                                <ArrowDown className="h-3.5 w-3.5" />
                              )
                            ) : null}
                          </button>
                        </th>
                      );
                    })}
                    {rowActions.length > 0 ? <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-[0.16em] text-text-muted">Actions</th> : null}
                  </tr>
                </thead>
                <tbody className="divide-y divide-border-default">
                  {paginatedRows.map((row) => (
                    <tr key={row.id} className="hover:bg-background-elevated">
                      <td className={densityClassMap[density]}>
                        <input
                          type="checkbox"
                          aria-label={`Select row ${row.id}`}
                          checked={selectedRowIds.includes(row.id)}
                          onChange={() => handleToggleRow(row.id)}
                          className="h-4 w-4 rounded border-border-default text-accent-primary focus:ring-border-focus"
                        />
                      </td>
                      {visibleColumns.map((column) => (
                        <td
                          key={column.key}
                          className={cn(
                            densityClassMap[density],
                            alignClassMap[column.align ?? 'left'],
                            'whitespace-nowrap text-text-primary',
                          )}
                        >
                          {column.key === 'status' && row.status ? (
                            <Badge tone={statusToneMap[row.status]}>{row.status}</Badge>
                          ) : column.render ? (
                            column.render(row)
                          ) : (
                            stringifyCell(row[column.key])
                          )}
                        </td>
                      ))}
                      {rowActions.length > 0 ? (
                        <td className={cn(densityClassMap[density], 'text-right')}>
                          <button type="button" className="inline-flex h-8 w-8 items-center justify-center rounded-lg text-text-secondary">
                            <MoreHorizontal className="h-4 w-4" />
                          </button>
                        </td>
                      ) : null}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="grid gap-3 p-4 md:grid-cols-2">
              {paginatedRows.map((row) => (
                <button
                  key={row.id}
                  type="button"
                  onClick={() => handleToggleRow(row.id)}
                  className={`rounded-xl border p-4 text-left transition duration-normal ease-standard ${
                    selectedRowIds.includes(row.id)
                      ? 'border-border-focus bg-background-accent'
                      : 'border-border-default bg-background-surface'
                  }`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <p className="font-semibold text-text-primary">
                      {stringifyCell(visibleColumns[0] ? row[visibleColumns[0].key] : row.id)}
                    </p>
                    {row.status ? <Badge tone={statusToneMap[row.status]}>{row.status}</Badge> : null}
                  </div>
                  <div className="mt-3 space-y-2 text-sm text-text-secondary">
                    {visibleColumns.slice(1, 4).map((column) => (
                      <p key={column.key}>
                        <span className="font-semibold">{column.label}:</span> {stringifyCell(row[column.key])}
                      </p>
                    ))}
                  </div>
                </button>
              ))}
            </div>
          )}

          <GridPagination page={page} pageSize={pageSize} totalRows={sortedRows.length} onPageChange={setPage} />
        </div>

        <div className="border-t border-border-default p-4 xl:border-l xl:border-t-0">
          <AIGridAssistant selectedCount={selectedRowIds.length} />
          {auditMode ? (
            <div className="mt-4 rounded-xl border border-border-default bg-background-elevated p-4">
              <p className="text-sm font-semibold text-text-primary">Audit Mode</p>
              <p className="mt-2 text-sm leading-6 text-text-secondary">
                Created By, Modified On, Version, and history actions are available through row context.
              </p>
            </div>
          ) : null}
        </div>
      </div>
    </section>
  );
}
