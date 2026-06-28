import type { InputHTMLAttributes } from 'react';
import { Search } from 'lucide-react';
import { cn } from '../utils/cn';

export interface SearchBarProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
}

export function SearchBar({ label, className, ...props }: SearchBarProps) {
  return (
    <div className={cn('flex min-w-0 flex-1 items-center gap-3 rounded-xl border border-border-default bg-background-elevated px-4 py-3', className)}>
      <Search className="h-4 w-4 shrink-0 text-text-muted" aria-hidden="true" />
      <input
        type="search"
        aria-label={label}
        className="min-w-0 flex-1 bg-transparent text-sm text-text-primary outline-none placeholder:text-text-muted"
        {...props}
      />
    </div>
  );
}
