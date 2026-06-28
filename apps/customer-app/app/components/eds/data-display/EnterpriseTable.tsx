import { Typography } from '../foundation/Typography';

export interface EnterpriseTableColumn<Row> {
  key: keyof Row;
  label: string;
  align?: 'left' | 'right';
}

export interface EnterpriseTableProps<Row extends Record<string, string>> {
  columns: Array<EnterpriseTableColumn<Row>>;
  rows: Row[];
  emptyMessage?: string;
}

const alignClassMap = {
  left: 'text-left',
  right: 'text-right',
};

export function EnterpriseTable<Row extends Record<string, string>>({
  columns,
  rows,
  emptyMessage = 'No records found.',
}: EnterpriseTableProps<Row>) {
  return (
    <div className="overflow-hidden rounded-xl border border-border-default bg-background-surface shadow-sm">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-border-default text-sm">
          <thead className="bg-background-elevated">
            <tr>
              {columns.map((column) => (
                <th
                  key={String(column.key)}
                  scope="col"
                  className={`px-4 py-3 ${alignClassMap[column.align ?? 'left']} text-xs font-semibold uppercase tracking-[0.16em] text-text-muted`}
                >
                  {column.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-border-default">
            {rows.map((row, index) => (
              <tr key={index} className="hover:bg-background-elevated">
                {columns.map((column) => (
                  <td
                    key={String(column.key)}
                    className={`px-4 py-3 ${alignClassMap[column.align ?? 'left']} text-text-primary`}
                  >
                    {row[column.key]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {rows.length === 0 ? (
        <div className="px-4 py-8 text-center">
          <Typography tone="secondary">{emptyMessage}</Typography>
        </div>
      ) : null}
    </div>
  );
}
