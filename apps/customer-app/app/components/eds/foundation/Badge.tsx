import type { CSSProperties, ReactNode } from 'react';

export type BadgeTone = 'neutral' | 'accent' | 'success' | 'warning' | 'danger';

export interface BadgeProps {
  children: ReactNode;
  tone?: BadgeTone;
  className?: string;
}

const toneClassMap: Record<BadgeTone, string> = {
  neutral: 'bg-background-elevated text-text-secondary',
  accent: 'bg-background-accent text-accent-primary',
  success: 'bg-background-elevated',
  warning: 'bg-background-elevated',
  danger: 'bg-background-elevated',
};

const toneStyleMap: Partial<Record<BadgeTone, CSSProperties>> = {
  success: { color: 'var(--accent-success)' },
  warning: { color: 'var(--accent-warning)' },
  danger: { color: 'var(--accent-danger)' },
};

export function Badge({ children, tone = 'neutral', className = '' }: BadgeProps) {
  return (
    <span
      className={`inline-flex rounded-full px-3 py-1 text-sm font-semibold ${toneClassMap[tone]} ${className}`}
      style={toneStyleMap[tone]}
    >
      {children}
    </span>
  );
}
