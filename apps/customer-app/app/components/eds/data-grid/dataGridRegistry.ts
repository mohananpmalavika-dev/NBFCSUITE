import type { DataGridContract } from './types';

export const dataGridRegistry: DataGridContract[] = [
  {
    id: 'enterprise-grid',
    module: 'Shared Enterprise Grid',
    supportsSelection: true,
    supportsSavedViews: true,
    supportsColumnManager: true,
    supportsExport: true,
    supportsAuditMode: true,
    supportsAiAssistant: true,
    performanceTarget: {
      searchMs: 250,
      sortMs: 200,
      exportMs: 1000,
    },
  },
  {
    id: 'audit-grid',
    module: 'Audit Review Grid',
    supportsSelection: true,
    supportsSavedViews: true,
    supportsColumnManager: true,
    supportsExport: true,
    supportsAuditMode: true,
    supportsAiAssistant: false,
    performanceTarget: {
      searchMs: 250,
      sortMs: 200,
      exportMs: 1000,
    },
  },
  {
    id: 'approval-grid',
    module: 'Approval Queue Grid',
    supportsSelection: true,
    supportsSavedViews: true,
    supportsColumnManager: true,
    supportsExport: true,
    supportsAuditMode: true,
    supportsAiAssistant: true,
    performanceTarget: {
      searchMs: 250,
      sortMs: 200,
      exportMs: 1000,
    },
  },
];
