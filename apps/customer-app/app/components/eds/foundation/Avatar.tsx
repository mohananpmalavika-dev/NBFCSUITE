import type { ReactNode } from 'react';

export interface AvatarProps {
  initials: string;
  size?: 'sm' | 'md' | 'lg';
  tone?: 'accent' | 'neutral';
  icon?: ReactNode;
}

const sizeClassMap = {
  sm: 'h-8 w-8 text-xs',
  md: 'h-10 w-10 text-sm',
  lg: 'h-12 w-12 text-base',
};

export function Avatar({ initials, size = 'md', tone = 'accent', icon }: AvatarProps) {
  return (
    <div
      className={`flex items-center justify-center rounded-full font-semibold ${sizeClassMap[size]} ${tone === 'accent' ? 'bg-accent-primary' : 'bg-background-elevated text-text-primary'}`}
      style={tone === 'accent' ? { color: 'var(--accent-on-primary)' } : undefined}
    >
      {icon ?? initials}
    </div>
  );
}
