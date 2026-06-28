import type { ElementType, HTMLAttributes, ReactNode } from 'react';
import { cn } from '../utils/cn';

export type TypographyVariant =
  | 'display'
  | 'h1'
  | 'h2'
  | 'h3'
  | 'body'
  | 'bodySmall'
  | 'caption'
  | 'label'
  | 'code';

export interface TypographyProps extends HTMLAttributes<HTMLElement> {
  as?: ElementType;
  children: ReactNode;
  variant?: TypographyVariant;
  tone?: 'primary' | 'secondary' | 'muted' | 'danger' | 'success';
}

const variantClassMap: Record<TypographyVariant, string> = {
  display: 'text-3xl font-semibold leading-tight',
  h1: 'text-2xl font-semibold leading-tight',
  h2: 'text-xl font-semibold leading-snug',
  h3: 'text-lg font-semibold leading-snug',
  body: 'text-sm leading-6',
  bodySmall: 'text-xs leading-5',
  caption: 'text-xs leading-5',
  label: 'text-xs font-semibold uppercase tracking-[0.16em]',
  code: 'font-mono text-sm leading-6',
};

const toneClassMap = {
  primary: 'text-text-primary',
  secondary: 'text-text-secondary',
  muted: 'text-text-muted',
  danger: 'text-accent-danger',
  success: 'text-accent-success',
};

export function Typography({
  as,
  children,
  className,
  variant = 'body',
  tone = 'primary',
  ...props
}: TypographyProps) {
  const Component = as ?? (variant === 'h1' ? 'h1' : variant === 'h2' ? 'h2' : variant === 'h3' ? 'h3' : 'p');

  return (
    <Component className={cn(variantClassMap[variant], toneClassMap[tone], className)} {...props}>
      {children}
    </Component>
  );
}
