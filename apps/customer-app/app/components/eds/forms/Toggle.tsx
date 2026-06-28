'use client';

import type { ButtonHTMLAttributes } from 'react';
import { cn } from '../utils/cn';

export interface ToggleProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  checked: boolean;
  label: string;
}

export function Toggle({ checked, label, className, type = 'button', ...props }: ToggleProps) {
  return (
    <button
      type={type}
      role="switch"
      aria-checked={checked}
      className={cn('inline-flex items-center gap-3 text-sm font-semibold text-text-primary', className)}
      {...props}
    >
      <span
        className={cn(
          'relative inline-flex h-6 w-11 rounded-full transition duration-normal ease-standard',
          checked ? 'bg-accent-primary' : 'bg-background-elevated',
        )}
      >
        <span
          className={cn(
            'absolute top-1 h-4 w-4 rounded-full bg-background-surface shadow-sm transition duration-normal ease-standard',
            checked ? 'left-6' : 'left-1',
          )}
        />
      </span>
      {label}
    </button>
  );
}
