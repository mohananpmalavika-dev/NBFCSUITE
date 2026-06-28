import { Badge } from '../foundation/Badge';
import type { GridSavedView } from './types';

export interface SavedViewsProps {
  views: GridSavedView[];
  activeViewId?: string;
  onViewChange: (view: GridSavedView) => void;
}

export function SavedViews({ views, activeViewId, onViewChange }: SavedViewsProps) {
  return (
    <div className="flex flex-wrap items-center gap-2">
      <span className="text-sm font-semibold text-text-secondary">Views</span>
      {views.map((view) => {
        const selected = view.id === activeViewId;

        return (
          <button
            key={view.id}
            type="button"
            className={`rounded-full px-3 py-1 text-sm font-semibold transition duration-normal ease-standard ${
              selected
                ? 'bg-accent-primary'
                : 'border border-border-default bg-background-surface text-text-secondary'
            }`}
            style={selected ? { color: 'var(--accent-on-primary)' } : undefined}
            onClick={() => onViewChange(view)}
          >
            {view.label}
            {view.shared ? <span className="ml-2"><Badge tone="neutral">org</Badge></span> : null}
          </button>
        );
      })}
    </div>
  );
}
