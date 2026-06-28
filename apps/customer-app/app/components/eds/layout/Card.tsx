import type { ReactNode } from 'react';

export interface CardProps {
  children: ReactNode;
  title?: string;
  description?: string;
  actions?: ReactNode;
  className?: string;
}

export function Card({ children, title, description, actions, className = '' }: CardProps) {
  return (
    <section className={`rounded-3xl border p-6 shadow-sm ${className}`} style={{ borderColor: 'var(--border-default)', backgroundColor: 'var(--background-surface)' }}>
      {(title || description || actions) && (
        <div className="mb-6 flex flex-wrap items-start justify-between gap-4">
          <div>
            {title ? <h3 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>{title}</h3> : null}
            {description ? <p className="mt-2 text-sm" style={{ color: 'var(--text-secondary)' }}>{description}</p> : null}
          </div>
          {actions ? <div>{actions}</div> : null}
        </div>
      )}
      {children}
    </section>
  );
}
