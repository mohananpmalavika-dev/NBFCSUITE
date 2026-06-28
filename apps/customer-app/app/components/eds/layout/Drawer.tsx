import type { ReactNode } from 'react';
import { X } from 'lucide-react';
import { IconButton } from '../foundation/IconButton';
import { Typography } from '../foundation/Typography';

export interface DrawerProps {
  children: ReactNode;
  open?: boolean;
  title: string;
  description?: string;
  onClose?: () => void;
}

export function Drawer({ children, open = true, title, description, onClose }: DrawerProps) {
  if (!open) {
    return null;
  }

  return (
    <aside className="hidden resize-x overflow-auto rounded-xl border border-border-default bg-background-surface p-5 shadow-lg xl:block">
      <div className="flex items-start justify-between gap-3">
        <div>
          <Typography as="h2" variant="h3">
            {title}
          </Typography>
          {description ? (
            <Typography tone="secondary" className="mt-1">
              {description}
            </Typography>
          ) : null}
        </div>
        {onClose ? <IconButton label="Close drawer" icon={<X className="h-4 w-4" />} size="sm" onClick={onClose} /> : null}
      </div>
      <div className="mt-6">{children}</div>
    </aside>
  );
}
