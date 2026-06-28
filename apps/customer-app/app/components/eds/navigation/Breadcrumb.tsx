import { ChevronRight } from 'lucide-react';

export interface BreadcrumbProps {
  items: string[];
}

export function Breadcrumb({ items }: BreadcrumbProps) {
  return (
    <nav aria-label="Breadcrumb" className="flex flex-wrap items-center gap-2 text-xs font-semibold uppercase tracking-[0.16em] text-text-muted">
      {items.map((item, index) => (
        <span key={`${item}-${index}`} className="inline-flex items-center gap-2">
          {index > 0 ? <ChevronRight className="h-3 w-3" aria-hidden="true" /> : null}
          {item}
        </span>
      ))}
    </nav>
  );
}
