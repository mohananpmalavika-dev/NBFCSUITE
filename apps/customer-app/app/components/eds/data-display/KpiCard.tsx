export interface KpiCardProps {
  label: string;
  value: string;
  helper?: string;
}

export function KpiCard({ label, value, helper }: KpiCardProps) {
  return (
    <div className="rounded-3xl border p-4 shadow-sm" style={{ borderColor: 'var(--border-default)', backgroundColor: 'var(--background-elevated)' }}>
      <p className="text-xs uppercase tracking-[0.24em]" style={{ color: 'var(--text-muted)' }}>{label}</p>
      <p className="mt-3 text-2xl font-semibold" style={{ color: 'var(--text-primary)' }}>{value}</p>
      {helper ? <p className="mt-2 text-sm" style={{ color: 'var(--text-secondary)' }}>{helper}</p> : null}
    </div>
  );
}
