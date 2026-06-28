import { ChevronLeft, ChevronRight } from 'lucide-react';
import { IconButton } from '../foundation/IconButton';

export interface GridPaginationProps {
  page: number;
  pageSize: number;
  totalRows: number;
  onPageChange: (page: number) => void;
}

export function GridPagination({ page, pageSize, totalRows, onPageChange }: GridPaginationProps) {
  const totalPages = Math.max(Math.ceil(totalRows / pageSize), 1);
  const start = totalRows === 0 ? 0 : (page - 1) * pageSize + 1;
  const end = Math.min(page * pageSize, totalRows);

  return (
    <div className="flex flex-col gap-3 border-t border-border-default bg-background-surface px-4 py-3 text-sm text-text-secondary sm:flex-row sm:items-center sm:justify-between">
      <span>
        Showing {start}-{end} of {totalRows}
      </span>
      <div className="flex items-center gap-3">
        <IconButton
          label="Previous page"
          icon={<ChevronLeft className="h-4 w-4" />}
          size="sm"
          disabled={page <= 1}
          onClick={() => onPageChange(Math.max(page - 1, 1))}
        />
        <span className="font-semibold text-text-primary">
          Page {page} / {totalPages}
        </span>
        <IconButton
          label="Next page"
          icon={<ChevronRight className="h-4 w-4" />}
          size="sm"
          disabled={page >= totalPages}
          onClick={() => onPageChange(Math.min(page + 1, totalPages))}
        />
      </div>
    </div>
  );
}
