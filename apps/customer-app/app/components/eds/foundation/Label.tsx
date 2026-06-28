import type { LabelHTMLAttributes, ReactNode } from 'react';

export interface LabelProps extends LabelHTMLAttributes<HTMLLabelElement> {
  children: ReactNode;
  required?: boolean;
}

export function Label({ children, required = false, className = '', ...props }: LabelProps) {
  return (
    <label className={`text-sm font-semibold text-text-primary ${className}`} {...props}>
      {children}
      {required ? <span className="ml-1 text-accent-danger">*</span> : null}
    </label>
  );
}
