import { cn } from '../utils/cn';

export interface SpinnerProps {
  label?: string;
  className?: string;
}

export function Spinner({ label = 'Loading', className }: SpinnerProps) {
  return (
    <span className={cn('inline-flex items-center gap-2 text-sm text-text-secondary', className)}>
      <span className="h-4 w-4 animate-spin rounded-full border-2 border-border-default border-t-accent-primary" />
      <span>{label}</span>
    </span>
  );
}
