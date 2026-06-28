import type { ReactNode } from 'react';
import { Button } from '../foundation/Button';
import { Typography } from '../foundation/Typography';
import type { DashboardAction, DashboardPersona } from './types';

export interface DashboardLayoutProps {
  title: string;
  description?: string;
  persona: DashboardPersona;
  actions?: DashboardAction[];
  children: ReactNode;
}

export function DashboardLayout({ title, description, persona, actions = [], children }: DashboardLayoutProps) {
  return (
    <section className="space-y-6 rounded-xl border border-border-default bg-background-surface p-5 shadow-sm">
      <div className="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
        <div>
          <Typography variant="label" tone="muted">
            {persona} dashboard
          </Typography>
          <Typography as="h2" variant="h1" className="mt-2">
            {title}
          </Typography>
          {description ? (
            <Typography tone="secondary" className="mt-2 max-w-3xl">
              {description}
            </Typography>
          ) : null}
        </div>
        {actions.length > 0 ? (
          <div className="flex flex-wrap gap-3">
            {actions.map((action, index) => (
              <Button
                key={action.label}
                variant={index === 0 ? 'primary' : 'secondary'}
                size="sm"
                icon={action.icon}
                onClick={action.onClick}
              >
                {action.label}
              </Button>
            ))}
          </div>
        ) : null}
      </div>
      {children}
    </section>
  );
}
