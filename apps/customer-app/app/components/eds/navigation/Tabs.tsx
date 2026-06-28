'use client';

import { useState } from 'react';
import type { ReactNode } from 'react';
import { cn } from '../utils/cn';

export interface TabItem {
  id: string;
  label: string;
  content: ReactNode;
}

export interface TabsProps {
  items: TabItem[];
  defaultValue?: string;
}

export function Tabs({ items, defaultValue }: TabsProps) {
  const [activeId, setActiveId] = useState(defaultValue ?? items[0]?.id);
  const activeItem = items.find((item) => item.id === activeId) ?? items[0];

  return (
    <div>
      <div role="tablist" className="flex gap-2 overflow-x-auto border-b border-border-default">
        {items.map((item) => {
          const selected = item.id === activeItem?.id;

          return (
            <button
              key={item.id}
              type="button"
              role="tab"
              aria-selected={selected}
              className={cn(
                'whitespace-nowrap border-b-2 px-3 py-2 text-sm font-semibold transition duration-normal ease-standard focus:outline-none focus:ring-2 focus:ring-border-focus',
                selected
                  ? 'border-accent-primary text-accent-primary'
                  : 'border-transparent text-text-secondary',
              )}
              onClick={() => setActiveId(item.id)}
            >
              {item.label}
            </button>
          );
        })}
      </div>
      <div className="pt-4" role="tabpanel">
        {activeItem?.content}
      </div>
    </div>
  );
}
