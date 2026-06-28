import { Skeleton } from '../foundation/Skeleton';
import { Spinner } from '../foundation/Spinner';

export interface LoadingStateProps {
  label?: string;
  rows?: number;
}

export function LoadingState({ label = 'Loading workspace', rows = 3 }: LoadingStateProps) {
  return (
    <div className="rounded-xl border border-border-default bg-background-surface p-4">
      <Spinner label={label} />
      <div className="mt-4 space-y-3">
        {Array.from({ length: rows }).map((_, index) => (
          <Skeleton key={index} className="h-12 w-full" />
        ))}
      </div>
    </div>
  );
}
