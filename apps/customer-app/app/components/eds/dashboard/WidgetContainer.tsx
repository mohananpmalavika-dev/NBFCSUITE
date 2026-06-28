import type { ReactNode } from 'react';
import { Badge } from '../foundation/Badge';
import { Typography } from '../foundation/Typography';
import { cn } from '../utils/cn';
import type { WidgetCategory } from './types';

export interface WidgetContainerProps {
  title: string;
  description?: string;
  category: WidgetCategory;
  refreshPolicy?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
  children: ReactNode;
  className?: string;
}

const sizeClassMap = {
  sm: 'col-span-4 md:col-span-4 xl:col-span-3',
  md: 'col-span-4 md:col-span-4 xl:col-span-4',
  lg: 'col-span-4 md:col-span-8 xl:col-span-6',
  xl: 'col-span-4 md:col-span-8 xl:col-span-8',
  full: 'col-span-4 md:col-span-8 xl:col-span-12',
};

export function WidgetContainer({
  title,
  description,
  category,
  refreshPolicy,
  size = 'md',
  children,
  className,
}: WidgetContainerProps) {
  return (
    <article
      className={cn(
        'rounded-xl border border-border-default bg-background-surface p-4 shadow-sm',
        sizeClassMap[size],
        className,
      )}
      data-widget-category={category}
    >
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <Typography as="h3" variant="h3">
            {title}
          </Typography>
          {description ? (
            <Typography tone="secondary" className="mt-1">
              {description}
            </Typography>
          ) : null}
        </div>
        <div className="flex flex-wrap gap-2">
          <Badge tone="accent">{category}</Badge>
          {refreshPolicy ? <Badge tone="neutral">{refreshPolicy}</Badge> : null}
        </div>
      </div>
      <div className="mt-4">{children}</div>
    </article>
  );
}
