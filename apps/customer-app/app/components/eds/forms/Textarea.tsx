import type { TextareaHTMLAttributes } from 'react';
import { Label } from '../foundation/Label';
import { Typography } from '../foundation/Typography';
import { cn } from '../utils/cn';

export interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label: string;
  helperText?: string;
  errorText?: string;
}

export function Textarea({ label, helperText, errorText, id, className, required, ...props }: TextareaProps) {
  const textareaId = id ?? label.toLowerCase().replace(/\s+/g, '-');

  return (
    <div className="space-y-2">
      <Label htmlFor={textareaId} required={required}>
        {label}
      </Label>
      <textarea
        id={textareaId}
        required={required}
        aria-invalid={Boolean(errorText)}
        className={cn(
          'min-h-24 w-full rounded-xl border bg-background-surface px-3 py-2 text-sm text-text-primary outline-none transition duration-normal ease-standard placeholder:text-text-muted focus:ring-2 focus:ring-border-focus',
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
