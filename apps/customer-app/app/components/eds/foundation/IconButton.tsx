import type { ButtonHTMLAttributes, ReactNode } from 'react';
import { cn } from '../utils/cn';

export interface IconButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  label: string;
  icon: ReactNode;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'primary' | 'secondary' | 'ghost';
}

const sizeClassMap = {
  sm: 'h-8 w-8',
  md: 'h-10 w-10',
  lg: 'h-12 w-12',
};

const variantClassMap = {
  primary: 'border-transparent bg-accent-primary shadow-sm',
  secondary: 'border-border-default bg-background-surface text-text-secondary shadow-xs',
  ghost: 'border-transparent bg-transparent text-text-secondary',
};

export function IconButton({
  label,
  icon,
  size = 'md',
  variant = 'secondary',
  className,
  style,
  type = 'button',
  ...props
}: IconButtonProps) {
  return (
    <button
      type={type}
      aria-label={label}
      title={label}
      className={cn(
        'inline-flex shrink-0 items-center justify-center rounded-xl border transition duration-normal ease-standard focus:outline-none focus:ring-2 focus:ring-border-focus disabled:cursor-not-allowed disabled:opacity-60',
        sizeClassMap[size],
        variantClassMap[variant],
        className,
      )}
      style={{
        color: variant === 'primary' ? 'var(--accent-on-primary)' : undefined,
        ...style,
      }}
      {...props}
    >
      {icon}
    </button>
  );
}
