import type { InputHTMLAttributes } from 'react';
import { Label } from '../foundation/Label';
import { Typography } from '../foundation/Typography';
import { cn } from '../utils/cn';

export interface TextInputProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  helperText?: string;
  errorText?: string;
}

export function TextInput({ label, helperText, errorText, id, className, required, ...props }: TextInputProps) {
  const inputId = id ?? label.toLowerCase().replace(/\s+/g, '-');

  return (
    <div className="space-y-2">
      <Label htmlFor={inputId} required={required}>
        {label}
      </Label>
      <input
        id={inputId}
        required={required}
        aria-invalid={Boolean(errorText)}
        className={cn(
          'w-full rounded-xl border bg-background-surface px-3 py-2 text-sm text-text-primary outline-none transition duration-normal ease-standard placeholder:text-text-muted focus:ring-2 focus:ring-border-focus',
          errorText ? 'border-accent-danger' : 'border-border-default',
          className,
        )}
        {...props}
      />
      {errorText ? (
        <Typography variant="caption" tone="danger">
          {errorText}
        </Typography>
      ) : helperText ? (
        <Typography variant="caption" tone="muted">
          {helperText}
        </Typography>
      ) : null}
    </div>
  );
}
