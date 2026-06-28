import type { GridColumn } from './types';

export interface ColumnManagerProps<Row> {
  columns: Array<GridColumn<Row>>;
  visibleColumnKeys: string[];
  onToggleColumn: (key: string) => void;
}

export function ColumnManager<Row>({ columns, visibleColumnKeys, onToggleColumn }: ColumnManagerProps<Row>) {
  return (
    <div className="rounded-xl border border-border-default bg-background-elevated p-3">
      <p className="text-sm font-semibold text-text-primary">Column Manager</p>
      <div className="mt-3 flex flex-wrap gap-2">
        {columns.map((column) => {
          const visible = visibleColumnKeys.includes(column.key);

          return (
            <button
              key={column.key}
              type="button"
              aria-pressed={visible}
              onClick={() => onToggleColumn(column.key)}
              className={`rounded-full px-3 py-1 text-sm font-semibold transition duration-normal ease-standard ${
                visible
                  ? 'bg-background-accent text-accent-primary'
                  : 'border border-border-default bg-background-surface text-text-muted'
              }`}
            >
              {column.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}
