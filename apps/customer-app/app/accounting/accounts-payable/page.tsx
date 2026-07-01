import Link from 'next/link';

export default function AccountsPayablePage() {
  return (
    <div className="space-y-6 p-6">
      <div className="rounded-2xl border border-border-muted bg-background-surface p-6 shadow-sm">
        <h1 className="text-2xl font-semibold">Accounts Payable</h1>
        <p className="mt-2 max-w-2xl text-sm text-foreground-muted">
          Manage supplier invoices, vendor payables, and payments from the accounting workspace.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <div className="rounded-2xl border border-border-muted bg-background-surface p-6 shadow-sm">
          <h2 className="text-lg font-semibold">Quick links</h2>
          <ul className="mt-4 space-y-2 text-sm text-foreground-muted">
            <li>
              <Link href="/accounting/accounts-payable/vendors" className="text-primary-foreground hover:underline">
                Vendor master
              </Link>
            </li>
            <li>
              <Link href="/accounting/accounts-payable/invoices" className="text-primary-foreground hover:underline">
                AP invoice registry
              </Link>
            </li>
            <li>
              <Link href="/accounting/accounts-payable/dashboard" className="text-primary-foreground hover:underline">
                AP dashboard
              </Link>
            </li>
          </ul>
        </div>

        <div className="rounded-2xl border border-border-muted bg-background-surface p-6 shadow-sm">
          <h2 className="text-lg font-semibold">Overview</h2>
          <p className="mt-4 text-sm text-foreground-muted">
            This section will surface enterprise accounts payable workflows, vendor ledger details, and supplier payment tracking.
          </p>
        </div>
      </div>
    </div>
  );
}
