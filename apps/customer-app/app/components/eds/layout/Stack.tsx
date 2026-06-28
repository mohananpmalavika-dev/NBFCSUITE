import type { HTMLAttributes, ReactNode } from 'react';
import { cn } from '../utils/cn';

export interface StackProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
  gap?: 'sm' | 'md' | 'lg';
}

const gapClassMap = {
  sm: 'gap-2',
  md: 'gap-4',
  lg: 'gap-6',
};

export function Stack({ children, gap = 'md', className, ...props }: StackProps) {
  return (
    <div className={cn('flex flex-col', gapClassMap[gap], className)} {...props}>
      {children}
    </div>
  );
}
