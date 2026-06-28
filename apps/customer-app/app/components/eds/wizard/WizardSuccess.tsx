import { CheckCircle2, FileText, PlusCircle, UserCircle } from 'lucide-react';
import { Button } from '../foundation/Button';

export interface WizardSuccessProps {
  title: string;
  description?: string;
  onOpenRecord?: () => void;
  onCreateAnother?: () => void;
}

export function WizardSuccess({ title, description, onOpenRecord, onCreateAnother }: WizardSuccessProps) {
  return (
    <section className="rounded-xl border border-border-default bg-background-surface p-6 text-center">
      <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-background-accent text-accent-success">
        <CheckCircle2 className="h-7 w-7" />
      </div>
      <h3 className="mt-4 text-xl font-semibold text-text-primary">{title}</h3>
      {description ? <p className="mx-auto mt-2 max-w-xl text-sm leading-6 text-text-secondary">{description}</p> : null}
      <div className="mt-5 flex flex-wrap justify-center gap-2">
        <Button size="sm" icon={<UserCircle className="h-4 w-4" />} onClick={onOpenRecord}>
          Open profile
        </Button>
        <Button size="sm" variant="secondary" icon={<FileText className="h-4 w-4" />}>
          Print
        </Button>
        <Button size="sm" variant="secondary" icon={<PlusCircle className="h-4 w-4" />} onClick={onCreateAnother}>
          Create another
        </Button>
      </div>
    </section>
  );
}
