import type { ButtonHTMLAttributes, ReactNode } from 'react';
import { cn } from '../utils/cn';

export interface ChipProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  selected?: boolean;
}

export function Chip({ children, selected = false, className, type = 'button', ...props }: ChipProps) {
  return (
    <button
      type={type}
      aria-pressed={selected}
      className={cn(
        'inline-flex items-center rounded-full border px-3 py-1 text-sm font-semibold transition duration-normal ease-standard focus:outline-none focus:ring-2 focus:ring-border-focus',
        selected
          ? 'border-transparent bg-accent-primary'
          : 'border-border-default bg-background-surface text-text-secondary',
        className,
      )}
      style={selected ? { color: 'var(--accent-on-primary)' } : undefined}
      {...props}
    >
      {children}
    </button>
  );
}
