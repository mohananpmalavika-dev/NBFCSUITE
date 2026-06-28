import { Download, RefreshCw, Search, SlidersHorizontal, Sparkles, Upload } from 'lucide-react';
import { Button } from '../foundation/Button';
import { IconButton } from '../foundation/IconButton';

export interface GridToolbarProps {
  searchQuery: string;
  onSearchChange: (value: string) => void;
  onRefresh?: () => void;
  onExport?: () => void;
  onImport?: () => void;
  onAiRequest?: () => void;
}

export function GridToolbar({
  searchQuery,
  onSearchChange,
  onRefresh,
  onExport,
  onImport,
  onAiRequest,
}: GridToolbarProps) {
  return (
    <div className="flex flex-col gap-3 border-b border-border-default bg-background-surface p-4 lg:flex-row lg:items-center lg:justify-between">
      <div className="flex min-w-0 flex-1 items-center gap-3 rounded-xl border border-border-default bg-background-elevated px-4 py-3">
        <Search className="h-4 w-4 shrink-0 text-text-muted" />
        <input
          value={searchQuery}
          onChange={(event) => onSearchChange(event.target.value)}
          type="search"
          aria-label="Search grid"
          placeholder="Search records, exact values, partial text..."
          className="min-w-0 flex-1 bg-transparent text-sm text-text-primary outline-none placeholder:text-text-muted"
        />
      </div>
      <div className="flex flex-wrap gap-2">
        <Button variant="secondary" size="sm" icon={<SlidersHorizontal className="h-4 w-4" />}>
          Filter
        </Button>
        <IconButton label="Refresh grid" icon={<RefreshCw className="h-4 w-4" />} onClick={onRefresh} />
        <IconButton label="Import records" icon={<Upload className="h-4 w-4" />} onClick={onImport} />
        <IconButton label="Export records" icon={<Download className="h-4 w-4" />} onClick={onExport} />
        <Button size="sm" icon={<Sparkles className="h-4 w-4" />} onClick={onAiRequest}>
          Ask FinDNA
        </Button>
      </div>
    </div>
  );
}
