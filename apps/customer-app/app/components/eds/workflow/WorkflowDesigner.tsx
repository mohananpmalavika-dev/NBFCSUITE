import { GitBranch, Settings2 } from 'lucide-react';
import { Badge } from '../foundation/Badge';
import type { WorkflowDesignerNode } from './types';

export interface WorkflowDesignerProps {
  nodes: WorkflowDesignerNode[];
}

const nodeToneMap = {
  start: 'success',
  task: 'accent',
  approval: 'warning',
  decision: 'accent',
  'parallel-merge': 'neutral',
  notification: 'neutral',
  delay: 'warning',
  script: 'neutral',
  end: 'success',
} as const;

export function WorkflowDesigner({ nodes }: WorkflowDesignerProps) {
  return (
    <section className="rounded-xl border border-border-default bg-background-surface p-4 shadow-sm">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h3 className="text-lg font-semibold text-text-primary">Workflow Designer</h3>
          <p className="mt-1 text-sm text-text-secondary">Low-code definition surface for stages, actions, conditions, owners, and notifications.</p>
        </div>
        <Badge tone="accent">Configurable</Badge>
      </div>

      <div className="mt-4 overflow-x-auto">
        <div className="flex min-w-max items-stretch gap-3">
          {nodes.map((node, index) => (
            <div key={node.id} className="flex items-center gap-3">
              <article className="w-48 rounded-xl border border-border-default bg-background-elevated p-3">
                <div className="flex items-center justify-between gap-2">
                  <Badge tone={nodeToneMap[node.type]} className="text-xs">{node.type}</Badge>
                  <Settings2 className="h-4 w-4 text-text-muted" />
                </div>
                <p className="mt-3 text-sm font-semibold text-text-primary">{node.label}</p>
                {node.owner ? <p className="mt-1 text-xs text-text-muted">{node.owner}</p> : null}
                {node.condition ? <p className="mt-2 text-xs leading-5 text-text-secondary">{node.condition}</p> : null}
              </article>
              {index < nodes.length - 1 ? <GitBranch className="h-4 w-4 shrink-0 text-text-muted" /> : null}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
