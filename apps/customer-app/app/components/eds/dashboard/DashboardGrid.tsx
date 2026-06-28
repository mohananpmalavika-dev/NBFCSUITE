import type { HTMLAttributes, ReactNode } from 'react';
import { cn } from '../utils/cn';

export interface DashboardGridProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
}

export function DashboardGrid({ children, className, ...props }: DashboardGridProps) {
  return (
    <div className={cn('grid grid-cols-4 gap-4 md:grid-cols-8 xl:grid-cols-12', className)} {...props}>
      {children}
    </div>
  );
}
