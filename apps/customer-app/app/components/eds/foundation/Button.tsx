import type { ButtonHTMLAttributes, ReactNode } from 'react';

export type ButtonVariant = 'primary' | 'secondary' | 'ghost';
export type ButtonSize = 'sm' | 'md';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  icon?: ReactNode;
  fullWidth?: boolean;
}

const variantClassMap: Record<ButtonVariant, string> = {
  primary: 'border-transparent shadow-sm',
  secondary: 'border bg-background-surface text-text-secondary',
  ghost: 'border-transparent bg-transparent text-text-secondary shadow-none',
};

const sizeClassMap: Record<ButtonSize, string> = {
  sm: 'px-3 py-2 text-sm',
  md: 'px-4 py-2.5 text-sm',
};

export function Button({
  children,
  className = '',
  variant = 'primary',
  size = 'md',
  icon,
  fullWidth = false,
  type = 'button',
  style,
  ...props
}: ButtonProps) {
  return (
    <button
      type={type}
      className={`inline-flex items-center justify-center gap-2 rounded-full border font-semibold transition focus:outline-none focus:ring-2 focus:ring-[var(--border-focus)] ${variantClassMap[variant]} ${sizeClassMap[size]} ${fullWidth ? 'w-full' : ''} ${className}`}
      style={{
        backgroundColor: variant === 'primary' ? 'var(--accent-primary)' : undefined,
        color: variant === 'primary' ? 'var(--accent-on-primary)' : undefined,
        borderColor: variant === 'secondary' ? 'var(--border-default)' : undefined,
        ...style,
      }}
      {...props}
    >
      {icon ? <span className="shrink-0">{icon}</span> : null}
      {children}
    </button>
  );
}
