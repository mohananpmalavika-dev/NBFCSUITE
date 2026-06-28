export interface DividerProps {
  orientation?: 'horizontal' | 'vertical';
  className?: string;
}

export function Divider({ orientation = 'horizontal', className = '' }: DividerProps) {
  return (
    <div
      aria-hidden="true"
      className={`${orientation === 'horizontal' ? 'h-px w-full' : 'h-full w-px'} bg-border-default ${className}`}
    />
  );
}
