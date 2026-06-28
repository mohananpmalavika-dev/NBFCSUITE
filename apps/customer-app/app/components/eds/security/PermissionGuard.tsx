import type { ReactNode } from 'react';

export interface PermissionGuardProps {
  allowed: boolean;
  children: ReactNode;
  fallback?: ReactNode;
}

export function PermissionGuard({ allowed, children, fallback = null }: PermissionGuardProps) {
  return allowed ? <>{children}</> : <>{fallback}</>;
}
