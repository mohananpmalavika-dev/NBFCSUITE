import type { InputHTMLAttributes } from 'react';
import { Label } from '../foundation/Label';

export interface CheckboxProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
}

export function Checkbox({ label, id, className = '', ...props }: CheckboxProps) {
  const checkboxId = id ?? label.toLowerCase().replace(/\s+/g, '-');

  return (
    <div className="flex items-center gap-3">
      <input
        id={checkboxId}
        type="checkbox"
        className={`h-4 w-4 rounded border-border-default text-accent-primary focus:ring-border-focus ${className}`}
        {...props}
      />
      <Label htmlFor={checkboxId}>{label}</Label>
    </div>
  );
}
