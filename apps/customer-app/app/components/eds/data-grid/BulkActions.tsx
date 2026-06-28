import { Badge } from '../foundation/Badge';
import { Button } from '../foundation/Button';
import type { GridBulkAction } from './types';

export interface BulkActionsProps<Row> {
  selectedRows: Row[];
  actions: Array<GridBulkAction<Row>>;
  onClearSelection: () => void;
}

export function BulkActions<Row>({ selectedRows, actions, onClearSelection }: BulkActionsProps<Row>) {
  if (selectedRows.length === 0) {
    return null;
  }

  return (
    <div className="flex flex-col gap-3 border-b border-border-default bg-background-elevated p-3 lg:flex-row lg:items-center lg:justify-between">
      <div className="flex items-center gap-3">
        <Badge tone="accent">{selectedRows.length} selected</Badge>
        <button type="button" className="text-sm font-semibold text-text-secondary" onClick={onClearSelection}>
          Clear selection
        </button>
      </div>
      <div className="flex flex-wrap gap-2">
        {actions.map((action) => (
          <Button
            key={action.label}
            size="sm"
            variant="secondary"
            onClick={() => action.onAction?.(selectedRows)}
          >
            {action.label}
          </Button>
        ))}
      </div>
    </div>
  );
}
