
"use client";

import { useEffect, useMemo, useState } from 'react';
import type { ReactNode } from 'react';
import { usePathname } from 'next/navigation';
import {
  Banknote,
  Bell,
  Building2,
  ChartPie,
  CheckCircle2,
  ChevronRight,
  ClipboardList,
  Clock3,
  Command,
  Compass,
  DollarSign,
  FileText,
  HelpCircle,
  Home,
  LayoutDashboard,
  Layers,
  Menu,
  Palette,
  PanelRightOpen,
  PlusCircle,
  RefreshCw,
  Search,
  Settings2,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
  UserCircle,
  Users2,
  X,
} from 'lucide-react';
import { buildCssVariables, themes, type ThemeName } from '../../lib/design-tokens';
import type {
  WizardStep,
  WorkflowAnalyticsMetric,
  WorkflowAuditEntry,
  WorkflowComment,
  WorkflowDesignerNode,
  WorkflowTask,
  WorkflowTimelineItem,
} from './eds';
import {
  AISummary,
  AISummaryWidget,
  ActivityWidget,
  Alert,
  AlertWidget,
  ApprovalWidget,
  ApprovalCard,
  ApprovalInbox,
  Button as EDSButton,
  ChartWidget,
  Checkbox,
  Customer360Card,
  DashboardGrid,
  DashboardLayout,
  EnterpriseTable,
  EnterpriseGrid,
  EnterpriseWizard,
  KPIWidget,
  LoanSummaryCard,
  MetricCard,
  QuickActionsWidget,
  RoleBadge,
  TaskWidget,
  Textarea,
  TextInput,
  Toggle,
  WorkflowAnalytics,
  WorkflowDesigner,
  WorkflowViewer,
  WizardAttachments,
  WizardValidation,
  componentRegistry,
  dataGridRegistry,
  dashboardWidgetRegistry,
  workflowRegistry,
  wizardRegistry,
} from './eds';

const topNavItems = [
  { label: 'AI Assistant', icon: Sparkles },
  { label: 'Notifications', icon: Bell },
  { label: 'Approvals', icon: CheckCircle2 },
  { label: 'Tasks', icon: ClipboardList },
  { label: 'Help', icon: HelpCircle },
];

const navItems = [
  { label: 'Dashboard', icon: LayoutDashboard, href: '/' },
  { label: 'Customers', icon: Users2 },
  { label: 'Lending', icon: DollarSign },
  { label: 'Deposits', icon: Banknote },
  { label: 'Gold Loans', icon: FileText },
  { label: 'Treasury', icon: Compass },
  { label: 'Accounting', icon: FileText, href: '/accounting/chart-of-accounts' },
  { label: 'Financial Calendar', icon: ClipboardList, href: '/accounting/financial-calendar' },
  { label: 'Event Engine', icon: Layers, href: '/accounting/event-engine' },
  { label: 'Posting Rules', icon: Settings2, href: '/accounting/posting-rules' },
  { label: 'Finance Workspace', icon: ClipboardList, href: '/eom/finance' },
  { label: 'HRMS', icon: ShieldCheck, href: '/eom' },
  { label: 'CRM', icon: Users2 },
  { label: 'Risk', icon: ShieldAlert },
  { label: 'Compliance', icon: Layers },
  { label: 'Reports', icon: ChartPie },
  { label: 'Administration', icon: Settings2 },
  { label: 'AI', icon: Sparkles },
];

const mobileTabs = [
  { label: 'Home', icon: Home },
  { label: 'Search', icon: Search },
  { label: 'Tasks', icon: ClipboardList },
  { label: 'Alerts', icon: Bell },
  { label: 'Profile', icon: UserCircle },
];

const breadcrumbs = ['Home', 'Workspace', 'Expenses', 'Approval'];

const kpis = [
  { label: 'Pending Approvals', value: '38', change: '+6 today' },
  { label: 'SLA Health', value: '94%', change: 'On track' },
  { label: 'Exceptions', value: '7', change: 'Needs review' },
  { label: 'Avg Turnaround', value: '2.4h', change: 'Fast lane' },
];

const favorites = ['Employee Directory', 'Customer 360', 'General Ledger', 'Financial Calendar', 'Event Engine', 'Posting Rules', 'Finance Workspace'];
// Add EOM Dashboard favorite
favorites.unshift('EOM Dashboard');
const recent = ['Expense Approval', 'Branch 1204', 'Policy Exceptions'];

const commandActions = [
  'Create Employee',
  'Open Customer 360',
  'Find Loan Application',
  'Review Expense Approval',
  'Open General Ledger',
  'Show HRMS Dashboard',
  'Ask FinDNA',
];

const approvals = [
  { employee: 'Asha Menon', amount: 'INR 18,420', status: 'Policy matched' },
  { employee: 'Rohan Iyer', amount: 'INR 7,900', status: 'Manager approved' },
  { employee: 'Neha Shah', amount: 'INR 24,600', status: 'Receipt pending' },
];

const registryRows = [
  { component: 'EnterpriseTable', layer: 'Data Display', status: 'Typed API' },
  { component: 'ApprovalCard', layer: 'Workflow', status: 'Action Ready' },
  { component: 'AISummary', layer: 'AI', status: 'FinDNA Ready' },
  { component: 'PermissionGuard', layer: 'Security', status: 'RBAC Ready' },
];

const registryColumns = [
  { key: 'component' as const, label: 'Component' },
  { key: 'layer' as const, label: 'Layer' },
  { key: 'status' as const, label: 'Contract' },
];

const dashboardChartData = [
  { label: 'Jan', value: 58 },
  { label: 'Feb', value: 64 },
  { label: 'Mar', value: 71 },
  { label: 'Apr', value: 68 },
  { label: 'May', value: 79 },
  { label: 'Jun', value: 86 },
];

const dashboardAlerts = [
  { title: 'KYC renewals due for 24 high-value customers', severity: 'warning' as const, owner: 'Customer Ops' },
  { title: 'Branch 1204 cash limit exceeded', severity: 'danger' as const, owner: 'Treasury' },
];

const dashboardTasks = [
  { title: 'Review overdue collections queue', due: 'Today', owner: 'Anita', priority: 'high' as const },
  { title: 'Publish month-end dashboard layout', due: 'This week', owner: 'Finance PMO', priority: 'medium' as const },
  { title: 'Validate HR attendance exceptions', due: 'Tomorrow', owner: 'HR Ops', priority: 'low' as const },
];

const dashboardApprovals = [
  {
    workflowId: 'wf-demo-1',
    transactionTitle: 'Journal Approval',
    transactionId: 'TX-9001',
    submitter: 'Finance Officer',
    currentStageLabel: 'Current',
    stageStatus: 'pending' as const,
    slaStatus: 'safe' as const,
    slaLabel: '02:14',

    amount: 'INR 12.8L',
  },
  {
    workflowId: 'wf-demo-2',
    transactionTitle: 'Leave Approval',
    transactionId: 'TX-9002',
    submitter: 'HR Executive',
    currentStageLabel: 'Current',
    stageStatus: 'pending' as const,
    slaStatus: 'safe' as const,
    slaLabel: '06:20',

    amount: '8 employees',
  },
];


const dashboardActivities = [
  { title: 'Loan approved', description: 'Vehicle loan LN-7721 moved to disbursement.', time: '8 min ago' },
  { title: 'Voucher posted', description: 'JV-2042 posted by accounting operations.', time: '19 min ago' },
  { title: 'Alert acknowledged', description: 'Cash threshold alert assigned to Treasury.', time: '31 min ago' },
];

interface EmployeeGridRow {
  id: string;
  employee: string;
  branch: string;
  department: string;
  grade: string;
  status: 'draft' | 'pending' | 'approved' | 'rejected' | 'closed';
  manager: string;
  modifiedOn: string;
  version: string;
}

const employeeGridRows: EmployeeGridRow[] = [
  { id: 'EMP-1001', employee: 'Asha Menon', branch: 'Kollam', department: 'HR', grade: 'M2', status: 'approved', manager: 'Nisha Rao', modifiedOn: '28-Jun-2026', version: 'v4' },
  { id: 'EMP-1002', employee: 'Rohan Iyer', branch: 'Kochi', department: 'Finance', grade: 'M1', status: 'pending', manager: 'Arun Nair', modifiedOn: '28-Jun-2026', version: 'v2' },
  { id: 'EMP-1003', employee: 'Neha Shah', branch: 'Trivandrum', department: 'Operations', grade: 'S3', status: 'draft', manager: 'Meera Das', modifiedOn: '27-Jun-2026', version: 'v1' },
  { id: 'EMP-1004', employee: 'Vikram Rao', branch: 'Kollam', department: 'Collections', grade: 'S2', status: 'approved', manager: 'Nisha Rao', modifiedOn: '27-Jun-2026', version: 'v7' },
  { id: 'EMP-1005', employee: 'Farah Khan', branch: 'Kozhikode', department: 'Risk', grade: 'M3', status: 'rejected', manager: 'Deepak Varma', modifiedOn: '26-Jun-2026', version: 'v3' },
  { id: 'EMP-1006', employee: 'Joel Mathew', branch: 'Kochi', department: 'Audit', grade: 'M2', status: 'closed', manager: 'Anita Joseph', modifiedOn: '26-Jun-2026', version: 'v5' },
  { id: 'EMP-1007', employee: 'Priya Nambiar', branch: 'Trivandrum', department: 'Payroll', grade: 'S4', status: 'pending', manager: 'Meera Das', modifiedOn: '25-Jun-2026', version: 'v2' },
];

const employeeGridColumns = [
  { key: 'employee' as const, label: 'Employee', sortable: true, filterable: true },
  { key: 'branch' as const, label: 'Branch', sortable: true, filterable: true },
  { key: 'department' as const, label: 'Department', sortable: true, filterable: true },
  { key: 'grade' as const, label: 'Grade', sortable: true },
  { key: 'status' as const, label: 'Status', sortable: true, filterable: true },
  { key: 'manager' as const, label: 'Manager', sortable: true },
  { key: 'modifiedOn' as const, label: 'Modified On', sortable: true },
  { key: 'version' as const, label: 'Version', sortable: true },
];

const employeeSavedViews = [
  {
    id: 'default-hr',
    label: 'Default HR View',
    shared: true,
    visibleColumns: ['employee', 'branch', 'department', 'grade', 'status', 'manager', 'modifiedOn'],
  },
  {
    id: 'pending-payroll',
    label: 'Pending Payroll',
    search: 'pending',
    visibleColumns: ['employee', 'branch', 'department', 'status', 'manager'],
  },
  {
    id: 'audit-view',
    label: 'Audit View',
    shared: true,
    visibleColumns: ['employee', 'status', 'manager', 'modifiedOn', 'version'],
  },
];

const employeeWizardSteps = [
  { id: 'personal', label: 'Personal', description: 'Identity, contact, and nationality' },
  { id: 'employment', label: 'Employment', description: 'Role, joining date, and worker type' },
  { id: 'organization', label: 'Organization', description: 'Branch, department, manager, and grade' },
  { id: 'salary', label: 'Salary', description: 'Compensation, payroll, and approvals' },
  { id: 'documents', label: 'Documents', description: 'Required files and OCR checks' },
  { id: 'review', label: 'Review', description: 'Validate, approve, and submit' },
];

const employeeWizardChecklist = [
  { id: 'personal', label: 'Personal information captured', complete: true, required: true },
  { id: 'employment', label: 'Employment details confirmed', complete: true, required: true },
  { id: 'organization', label: 'Reporting manager assigned', complete: true, required: true },
  { id: 'salary', label: 'Salary reviewed by payroll', complete: false, required: true },
  { id: 'documents', label: 'Mandatory documents uploaded', complete: false, required: true },
];

const employeeWizardAttachments = [
  { id: 'photo', label: 'Photo', status: 'uploaded' as const, required: true, source: 'camera' as const },
  { id: 'aadhaar', label: 'Aadhaar', status: 'review' as const, required: true, source: 'ocr' as const },
  { id: 'pan', label: 'PAN', status: 'uploaded' as const, required: true, source: 'upload' as const },
  { id: 'offer-letter', label: 'Offer Letter', status: 'missing' as const, required: true, source: 'scanner' as const },
  { id: 'degree', label: 'Degree Certificate', status: 'missing' as const, source: 'upload' as const },
];

const employeeWizardValidationItems = [
  { id: 'client-email', level: 'client' as const, status: 'success' as const, message: 'Email, phone, and required fields are formatted correctly.' },
  { id: 'business-manager', level: 'business' as const, status: 'warning' as const, message: 'Payroll approval is recommended because salary exceeds the branch default.' },
  { id: 'server-employee-code', level: 'server' as const, status: 'success' as const, message: 'Employee code EMP-2048 is available and unique.' },
];

const employeeWizardReviewGroups = [
  {
    title: 'Personal',
    items: [
      { label: 'Employee', value: 'Anika Thomas', status: 'success' as const },
      { label: 'Nationality', value: 'Indian' },
      { label: 'Contact', value: '+91 98765 43210' },
    ],
  },
  {
    title: 'Employment',
    items: [
      { label: 'Designation', value: 'Branch Operations Officer' },
      { label: 'Branch', value: 'Kollam - 1204' },
      { label: 'Manager', value: 'Nisha Rao' },
    ],
  },
  {
    title: 'Salary',
    items: [
      { label: 'CTC', value: 'INR 8.4L' },
      { label: 'Payroll status', value: 'Needs payroll approval', status: 'warning' as const },
      { label: 'Effective date', value: '01-Jul-2026' },
    ],
  },
  {
    title: 'Documents',
    items: [
      { label: 'Uploaded', value: '3 of 5' },
      { label: 'OCR status', value: 'Aadhaar in review', status: 'warning' as const },
      { label: 'Missing', value: 'Offer letter' },
    ],
  },
];

const workflowTasks: WorkflowTask[] = [
  {
    workflowId: 'WF-HR-2048',
    transactionTitle: 'Employee Creation',
    transactionId: 'EMP-2048',
    submitter: 'Asha Menon',
    currentStageLabel: 'Payroll Approval',
    stageStatus: 'current',
    slaStatus: 'amber',
    slaLabel: '2 hours remaining',
    amount: 'INR 8.4L CTC',
    approverPrimary: 'Payroll Lead',
    module: 'HRMS',
    branch: 'Kollam 1204',
    priority: 'high',
  },
  {
    workflowId: 'WF-LN-7721',
    transactionTitle: 'Vehicle Loan Approval',
    transactionId: 'LN-7721',
    submitter: 'Branch Credit Officer',
    currentStageLabel: 'Risk + Legal Parallel Review',
    stageStatus: 'current',
    slaStatus: 'safe',
    slaLabel: '12 hours remaining',
    amount: 'INR 7.4L',
    approverPrimary: 'Risk Queue',
    module: 'Lending',
    branch: 'Kochi 1140',
    priority: 'medium',
    delegated: true,
  },
  {
    workflowId: 'WF-JV-2042',
    transactionTitle: 'Journal Voucher Approval',
    transactionId: 'JV-2042',
    submitter: 'Finance Officer',
    currentStageLabel: 'Finance Manager',
    stageStatus: 'current',
    slaStatus: 'breached',
    slaLabel: 'SLA breached',
    amount: 'INR 12.8L',
    approverPrimary: 'Finance Manager',
    module: 'Accounting',
    branch: 'Head Office',
    priority: 'critical',
    overdue: true,
  },
];

const workflowTimelineItems: WorkflowTimelineItem[] = [
  { title: 'Submitted', actor: 'Asha Menon', description: 'Employee onboarding submitted from EDS-009 wizard.', time: '09:10', state: 'completed' },
  { title: 'Manager reviewed', actor: 'Nisha Rao', description: 'Manager confirmed branch assignment and grade.', time: '09:22', state: 'completed' },
  { title: 'HR reviewed', actor: 'HR Operations', description: 'Document checklist reviewed with Aadhaar OCR pending.', time: '09:40', state: 'completed' },
  { title: 'Payroll approval', actor: 'Payroll Lead', description: 'Salary band exception requires approval before creation.', time: 'Now', state: 'current' },
  { title: 'Business action', actor: 'Workflow engine', description: 'Create employee after approval is granted.', state: 'pending' },
];

const workflowComments: WorkflowComment[] = [
  {
    id: 'comment-1',
    author: 'Nisha Rao',
    message: 'Branch assignment is correct. Please validate salary band before final creation.',
    time: '09:26',
    mentions: ['Payroll Lead'],
  },
  {
    id: 'comment-2',
    author: 'HR Operations',
    message: 'Aadhaar OCR review is pending, but PAN and photo are already uploaded.',
    time: '09:44',
    attachments: ['PAN.pdf', 'Photo.jpg'],
  },
];

const workflowAuditEntries: WorkflowAuditEntry[] = [
  { id: 'audit-1', event: 'WORKFLOW_CREATED', actor: 'Asha Menon', time: '09:10', description: 'Workflow draft created from employee onboarding wizard.' },
  { id: 'audit-2', event: 'WORKFLOW_STARTED', actor: 'Workflow engine', time: '09:11', description: 'Sequential HRMS workflow started.' },
  { id: 'audit-3', event: 'TASK_ASSIGNED', actor: 'Workflow engine', time: '09:12', description: 'Manager approval assigned to Nisha Rao.' },
  { id: 'audit-4', event: 'APPROVAL_GRANTED', actor: 'Nisha Rao', time: '09:22', description: 'Manager approval granted.' },
  { id: 'audit-5', event: 'TASK_ASSIGNED', actor: 'Workflow engine', time: '09:40', description: 'Payroll approval assigned with amber SLA.' },
];

const workflowDesignerNodes: WorkflowDesignerNode[] = [
  { id: 'start', label: 'Start', type: 'start', owner: 'Workflow engine' },
  { id: 'validation', label: 'Validation', type: 'task', owner: 'Rules engine', condition: 'Client, business, and server checks pass' },
  { id: 'manager', label: 'Manager Approval', type: 'approval', owner: 'Reporting manager' },
  { id: 'salary-decision', label: 'Salary Band Decision', type: 'decision', owner: 'Rules engine', condition: 'If salary exceeds branch band, route to payroll' },
  { id: 'payroll', label: 'Payroll Approval', type: 'approval', owner: 'Payroll Lead' },
  { id: 'notify', label: 'Notify Submitter', type: 'notification', owner: 'Notification engine' },
  { id: 'complete', label: 'Complete', type: 'end', owner: 'Audit engine' },
];

const workflowAnalyticsMetrics: WorkflowAnalyticsMetric[] = [
  { label: 'Average Approval Time', value: '2.4h', helper: 'Across HRMS approvals', tone: 'success' },
  { label: 'SLA Compliance', value: '94%', helper: 'Safe or amber workflows', tone: 'success' },
  { label: 'Escalations', value: '7', helper: 'Current week', tone: 'warning' },
  { label: 'Rejection Rate', value: '3.2%', helper: 'Below threshold', tone: 'neutral' },
  { label: 'Bottleneck Stage', value: 'Payroll', helper: 'Longest queue today', tone: 'warning' },
  { label: 'Workflow Volume', value: '1,284', helper: 'Month to date', tone: 'neutral' },
];

function renderEmployeeWizardStep(step: WizardStep) {
  if (step.id === 'personal') {
    return (
      <section className="space-y-4">
        <div>
          <h3 className="text-lg font-semibold text-text-primary">Personal Information</h3>
          <p className="mt-1 text-sm leading-6 text-text-secondary">
            Concise sections keep creation flows focused while preserving validation and audit context.
          </p>
        </div>
        <div className="grid gap-4 md:grid-cols-2">
          <TextInput label="Employee Code" defaultValue="EMP-2048" required helperText="Server validation confirms uniqueness." />
          <TextInput label="Full Name" defaultValue="Anika Thomas" required />
          <TextInput label="Email" defaultValue="anika.thomas@fincorp.example" type="email" required />
          <TextInput label="Phone" defaultValue="+91 98765 43210" required />
          <TextInput label="Nationality" defaultValue="Indian" helperText="PAN and Aadhaar fields remain visible for Indian employees." />
          <TextInput label="Date of Birth" defaultValue="1994-08-14" type="date" />
        </div>
      </section>
    );
  }

  if (step.id === 'employment') {
    return (
      <section className="space-y-4">
        <div>
          <h3 className="text-lg font-semibold text-text-primary">Employment Details</h3>
          <p className="mt-1 text-sm leading-6 text-text-secondary">
            Smart defaults can prefill worker type, probation policy, and joining branch.
          </p>
        </div>
        <div className="grid gap-4 md:grid-cols-2">
          <TextInput label="Designation" defaultValue="Branch Operations Officer" required />
          <TextInput label="Worker Type" defaultValue="Full-time" />
          <TextInput label="Joining Date" defaultValue="2026-07-01" type="date" />
          <TextInput label="Probation" defaultValue="6 months" />
        </div>
        <Textarea label="Role Notes" defaultValue="Primary responsibility includes teller exception handling and daily operations controls." />
      </section>
    );
  }

  if (step.id === 'organization') {
    return (
      <section className="space-y-4">
        <div>
          <h3 className="text-lg font-semibold text-text-primary">Organization Mapping</h3>
          <p className="mt-1 text-sm leading-6 text-text-secondary">
            Branch selection can default department, reporting manager, cost center, and grade rules.
          </p>
        </div>
        <div className="grid gap-4 md:grid-cols-2">
          <TextInput label="Branch" defaultValue="Kollam - 1204" required />
          <TextInput label="Department" defaultValue="Operations" required />
          <TextInput label="Reporting Manager" defaultValue="Nisha Rao" required />
          <TextInput label="Grade" defaultValue="S3" />
        </div>
        <WizardValidation items={employeeWizardValidationItems} />
      </section>
    );
  }

  if (step.id === 'salary') {
    return (
      <section className="space-y-4">
        <div>
          <h3 className="text-lg font-semibold text-text-primary">Salary and Payroll</h3>
          <p className="mt-1 text-sm leading-6 text-text-secondary">
            Salary fields support business validation and can branch into payroll approval when required.
          </p>
        </div>
        <div className="grid gap-4 md:grid-cols-3">
          <TextInput label="Annual CTC" defaultValue="840000" inputMode="numeric" required />
          <TextInput label="Payroll Group" defaultValue="Kerala Branch Payroll" />
          <TextInput label="Effective Date" defaultValue="2026-07-01" type="date" />
        </div>
        <div className="rounded-xl border border-border-default bg-background-elevated p-4 text-sm leading-6 text-text-secondary">
          Business rule: payroll approval is recommended because the salary is above the branch default band.
        </div>
      </section>
    );
  }

  if (step.id === 'documents') {
    return <WizardAttachments attachments={employeeWizardAttachments} />;
  }

  return (
    <section className="space-y-4">
      <div>
        <h3 className="text-lg font-semibold text-text-primary">Review and Submit</h3>
        <p className="mt-1 text-sm leading-6 text-text-secondary">
          Review groups, validation warnings, document status, and approval handoff are visible before submit.
        </p>
      </div>
      <WizardValidation items={employeeWizardValidationItems} />
    </section>
  );
}

export function AppShell({ children }: { children?: ReactNode }) {
  const [sidebarExpanded, setSidebarExpanded] = useState(true);
  const [themeName, setThemeName] = useState<ThemeName>('default');
  const [commandOpen, setCommandOpen] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(true);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const pathname = usePathname();
  const [autosaveEnabled, setAutosaveEnabled] = useState(true);
  const [dashboardPersona, setDashboardPersona] = useState<'executive' | 'branch'>('executive');
  const [lastGridEvent, setLastGridEvent] = useState('GRID_OPENED');
  const [lastWizardEvent, setLastWizardEvent] = useState('WIZARD_OPENED');
  const [activeWorkflowId, setActiveWorkflowId] = useState(workflowTasks[0].workflowId);
  const [lastWorkflowEvent, setLastWorkflowEvent] = useState('WORKFLOW_VIEWED');
  const [searchQuery, setSearchQuery] = useState('');

  const activeTheme = useMemo(() => themes[themeName], [themeName]);
  const libraryLayerCount = useMemo(
    () => new Set(componentRegistry.map((component) => component.layer)).size,
    [],
  );
  const activeDashboardTitle =
    dashboardPersona === 'executive' ? 'Executive Control Center' : 'Branch Operations Dashboard';
  const activeWorkflow = useMemo(
    () => workflowTasks.find((task) => task.workflowId === activeWorkflowId) ?? workflowTasks[0],
    [activeWorkflowId],
  );
  const visibleCommands = useMemo(
    () =>
      commandActions.filter((action) =>
        action.toLowerCase().includes(searchQuery.trim().toLowerCase()),
      ),
    [searchQuery],
  );

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', themeName);
    Object.assign(document.documentElement.style, buildCssVariables(activeTheme));
  }, [activeTheme, themeName]);

  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') {
        event.preventDefault();
        setCommandOpen(true);
      }

      if (event.key === 'Escape') {
        setCommandOpen(false);
        setMobileMenuOpen(false);
      }
    }

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  function cycleTheme() {
    setThemeName((current) =>
      current === 'default' ? 'dark' : current === 'dark' ? 'high-contrast' : 'default',
    );
  }

  const sidebar = (
    <aside
      className="flex h-full shrink-0 flex-col border-r bg-background-sidebar text-text-inverse transition-all duration-normal ease-standard"
      style={{ width: sidebarExpanded ? 'var(--shell-sidebar-expanded)' : 'var(--shell-sidebar-collapsed)' }}
      onMouseEnter={() => setSidebarExpanded(true)}
      onMouseLeave={() => setSidebarExpanded(false)}
    >
      <div className="flex h-16 items-center gap-3 border-b border-border-default px-4">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-background-sidebarSubtle">
          <Sparkles className="h-5 w-5" />
        </div>
        {sidebarExpanded && (
          <div className="min-w-0">
            <p className="truncate text-xs font-semibold uppercase tracking-[0.18em] text-text-inverseMuted">
              ARTH.OS
            </p>
            <p className="truncate text-sm font-semibold">Global Navigation</p>
          </div>
        )}
      </div>

      <nav className="flex-1 space-y-1 overflow-y-auto px-3 py-4" aria-label="Global navigation">
        {navItems.map((item) => {
          const Icon = item.icon;
          const href = item.href ?? '#';
          const isActive =
            item.href === '/'
              ? pathname === '/'
              : item.href === '/eom'
                ? pathname === '/eom' || (pathname.startsWith('/eom/') && !pathname.startsWith('/eom/finance'))
                : Boolean(item.href && pathname.startsWith(item.href));

          return (
            <a
              key={item.label}
              href={href}
              className="flex min-h-12 items-center gap-3 rounded-xl px-3 text-sm font-semibold text-text-inverse transition duration-normal ease-standard hover:bg-background-sidebarSubtle"
              style={isActive ? { backgroundColor: 'var(--background-sidebar-subtle)' } : undefined}
              title={sidebarExpanded ? undefined : item.label}
            >
              <Icon className="h-5 w-5 shrink-0 text-text-inverseMuted" />
              {sidebarExpanded && <span className="truncate">{item.label}</span>}
            </a>
          );
        })}
      </nav>

      {sidebarExpanded && (
        <div className="space-y-4 border-t border-border-default p-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-text-inverseMuted">
              Favorites
            </p>
              <div className="mt-3 space-y-2">
              {favorites.map((item) => {
                const href =
                  item === 'EOM Dashboard'
                    ? '/eom'
                    : item === 'Finance Workspace'
                      ? '/eom/finance'
                      : item === 'General Ledger'
                        ? '/accounting/chart-of-accounts'
                        : item === 'Financial Calendar'
                          ? '/accounting/financial-calendar'
                          : item === 'Event Engine'
                            ? '/accounting/event-engine'
                            : item === 'Posting Rules'
                              ? '/accounting/posting-rules'
                        : '#';
                return (
                  <a key={item} href={href} className="block truncate text-sm text-text-inverseMuted">
                    {item}
                  </a>
                );
              })}
            </div>
          </div>
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-text-inverseMuted">
              Recent
            </p>
            <div className="mt-3 space-y-2">
              {recent.map((item) => (
                <a key={item} href="#" className="block truncate text-sm text-text-inverseMuted">
                  {item}
                </a>
              ))}
            </div>
          </div>
        </div>
      )}
    </aside>
  );

  return (
    <div className="flex min-h-screen flex-col bg-background-default text-text-primary">
      <header className="sticky top-0 z-header h-16 border-b border-border-default bg-background-header backdrop-blur-sm">
        <div className="flex h-full items-center gap-3 px-4 sm:px-6">
          <button
            type="button"
            className="inline-flex h-10 w-10 items-center justify-center rounded-xl border border-border-default bg-background-surface text-text-secondary lg:hidden"
            onClick={() => {
              setSidebarExpanded(true);
              setMobileMenuOpen(true);
            }}
            aria-label="Open navigation"
          >
            <Menu className="h-5 w-5" />
          </button>

          <div className="flex min-w-0 items-center gap-3">
            <div className="hidden h-10 w-10 items-center justify-center rounded-xl bg-background-sidebar text-text-inverse sm:flex">
              <Sparkles className="h-5 w-5" />
            </div>
            <div className="min-w-0">
              <p className="truncate text-xs font-semibold uppercase tracking-[0.18em] text-text-muted">
                ARTH.OS
              </p>
              <p className="truncate text-sm font-semibold text-text-primary">Enterprise Shell</p>
            </div>
          </div>

          <button
            type="button"
            onClick={() => setCommandOpen(true)}
            className="ml-auto hidden h-10 min-w-0 flex-1 max-w-xl items-center gap-3 rounded-xl border border-border-default bg-background-elevated px-4 text-left text-sm text-text-muted shadow-xs md:flex"
            aria-label="Open global search"
          >
            <Search className="h-4 w-4 shrink-0" />
            <span className="truncate">Search customers, employees, loans, GL, reports...</span>
            <span className="ml-auto hidden items-center gap-1 rounded-md border border-border-default px-2 py-1 text-xs font-semibold lg:inline-flex">
              <Command className="h-3 w-3" /> K
            </span>
          </button>

          <div className="hidden items-center gap-2 md:flex">
            {topNavItems.map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.label}
                  type="button"
                  className="inline-flex h-10 w-10 items-center justify-center rounded-xl border border-border-default bg-background-surface text-text-secondary shadow-xs transition duration-normal ease-standard hover:border-border-focus"
                  aria-label={item.label}
                  title={item.label}
                >
                  <Icon className="h-5 w-5" />
                </button>
              );
            })}
          </div>

          <button
            type="button"
            onClick={cycleTheme}
            className="inline-flex h-10 w-10 items-center justify-center rounded-xl border border-border-default bg-background-surface text-text-secondary shadow-xs"
            aria-label="Cycle theme"
            title={`Theme: ${activeTheme.name}`}
          >
            <Palette className="h-5 w-5" />
          </button>

          <div className="hidden items-center gap-2 rounded-xl border border-border-default bg-background-surface px-3 py-2 text-sm text-text-secondary shadow-xs xl:flex">
            <span className="h-2.5 w-2.5 rounded-full bg-accent-success" />
            Branch 1204
          </div>
          <div className="hidden items-center gap-2 rounded-xl border border-border-default bg-background-surface px-3 py-2 text-sm text-text-secondary shadow-xs xl:flex">
            <Building2 className="h-4 w-4" />
            FinCorp
          </div>
        </div>
      </header>

      <div className="flex min-h-0 flex-1">
        <div className="hidden lg:block">{sidebar}</div>

        <main className="min-w-0 flex-1 overflow-y-auto pb-24 md:pb-0">
          <div className="border-b border-border-default bg-background-surface px-4 py-4 sm:px-6">
            <div className="flex flex-wrap items-center gap-2 text-xs font-semibold uppercase tracking-[0.16em] text-text-muted">
              {breadcrumbs.map((crumb, index) => (
                <span key={crumb} className="inline-flex items-center gap-2">
                  {index > 0 && <ChevronRight className="h-3 w-3" />}
                  {crumb}
                </span>
              ))}
            </div>
          </div>

          <section className="px-4 py-6 sm:px-6">
            <div className="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
              <div className="max-w-3xl">
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-accent-primary">
                  EDS-001 to EDS-005
                </p>
                <h1 className="mt-3 text-3xl font-semibold text-text-primary">
                  Expense Approval Workspace
                </h1>
                <p className="mt-3 text-sm leading-7 text-text-secondary">
                  Dashboard-first workspace with global navigation, contextual drawer, command search,
                  runtime themes, and token-backed shell surfaces.
                </p>
              </div>

              <div className="flex flex-wrap gap-3">
                <button
                  type="button"
                  className="rounded-full bg-accent-primary px-4 py-2 text-sm font-semibold shadow-sm"
                  style={{ color: 'var(--accent-on-primary)' }}
                >
                  New Approval
                </button>
                <button
                  type="button"
                  className="rounded-full border border-border-default bg-background-surface px-4 py-2 text-sm font-semibold text-text-secondary shadow-xs"
                >
                  Import
                </button>
                <button
                  type="button"
                  className="rounded-full border border-border-default bg-background-surface px-4 py-2 text-sm font-semibold text-text-secondary shadow-xs"
                >
                  Export
                </button>
                <button
                  type="button"
                  onClick={() => setDrawerOpen((open) => !open)}
                  className="inline-flex items-center gap-2 rounded-full border border-border-default bg-background-surface px-4 py-2 text-sm font-semibold text-text-secondary shadow-xs"
                >
                  <PanelRightOpen className="h-4 w-4" />
                  Context
                </button>
              </div>
            </div>

            <div className="mt-6">{children}</div>

            <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
              {kpis.map((kpi) => (
                <article
                  key={kpi.label}
                  className="rounded-xl border border-border-default bg-background-surface p-4 shadow-sm"
                >
                  <p className="text-xs font-semibold uppercase tracking-[0.16em] text-text-muted">
                    {kpi.label}
                  </p>
                  <p className="mt-3 text-2xl font-semibold text-text-primary">{kpi.value}</p>
                  <p className="mt-2 text-sm text-text-secondary">{kpi.change}</p>
                </article>
              ))}
            </div>

            <div className="mt-6 flex flex-col gap-3 border-y border-border-default bg-background-surface py-4 lg:flex-row lg:items-center lg:justify-between">
              <div className="flex min-w-0 flex-1 items-center gap-3 rounded-xl border border-border-default bg-background-elevated px-4 py-3">
                <Search className="h-4 w-4 shrink-0 text-text-muted" />
                <input
                  type="search"
                  aria-label="Search approvals"
                  placeholder="Search approvals, employees, policies..."
                  className="min-w-0 flex-1 bg-transparent text-sm text-text-primary outline-none placeholder:text-text-muted"
                />
              </div>
              <div className="flex flex-wrap gap-3">
                {['Department', 'Branch', 'Status', 'Save View'].map((filter) => (
                  <button
                    key={filter}
                    type="button"
                    className="rounded-full border border-border-default bg-background-surface px-4 py-2 text-sm font-semibold text-text-secondary shadow-xs"
                  >
                    {filter}
                  </button>
                ))}
              </div>
            </div>

            <div className="mt-6 grid gap-6 xl:grid-cols-[minmax(0,1fr)_var(--shell-right-drawer)]">
              <section className="min-w-0 rounded-xl border border-border-default bg-background-surface shadow-sm">
                <div className="flex items-center justify-between border-b border-border-default px-4 py-4">
                  <div>
                    <h2 className="text-lg font-semibold text-text-primary">Approval Queue</h2>
                    <p className="mt-1 text-sm text-text-secondary">List context stays visible while details open.</p>
                  </div>
                  <button
                    type="button"
                    className="rounded-full border border-border-default bg-background-elevated px-3 py-2 text-sm font-semibold text-text-secondary"
                  >
                    Bulk Action
                  </button>
                </div>

                <div className="divide-y divide-border-default">
                  {approvals.map((approval) => (
                    <button
                      key={approval.employee}
                      type="button"
                      onClick={() => setDrawerOpen(true)}
                      className="grid w-full gap-3 px-4 py-4 text-left transition duration-normal ease-standard hover:bg-background-elevated md:grid-cols-[1fr_auto_auto]"
                    >
                      <div>
                        <p className="font-semibold text-text-primary">{approval.employee}</p>
                        <p className="mt-1 text-sm text-text-secondary">{approval.status}</p>
                      </div>
                      <p className="font-semibold text-text-primary">{approval.amount}</p>
                      <span className="inline-flex items-center rounded-full bg-background-accent px-3 py-1 text-xs font-semibold text-accent-primary">
                        Review
                      </span>
                    </button>
                  ))}
                </div>
              </section>

              {drawerOpen && (
                <aside className="hidden resize-x overflow-auto rounded-xl border border-border-default bg-background-surface p-5 shadow-lg xl:block">
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <p className="text-xs font-semibold uppercase tracking-[0.16em] text-accent-primary">
                        Right Context Panel
                      </p>
                      <h2 className="mt-2 text-lg font-semibold text-text-primary">Expense Summary</h2>
                    </div>
                    <button
                      type="button"
                      onClick={() => setDrawerOpen(false)}
                      className="inline-flex h-9 w-9 items-center justify-center rounded-xl border border-border-default text-text-secondary"
                      aria-label="Close context panel"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  </div>

                  <div className="mt-6 space-y-4">
                    <div className="rounded-xl bg-background-elevated p-4">
                      <p className="text-sm font-semibold text-text-primary">AI Summary</p>
                      <p className="mt-2 text-sm leading-6 text-text-secondary">
                        FinDNA found matching travel policy, manager approval, and one receipt that needs
                        attachment before final posting.
                      </p>
                    </div>
                    <div className="rounded-xl bg-background-elevated p-4">
                      <p className="text-sm font-semibold text-text-primary">Audit Trail</p>
                      <div className="mt-3 space-y-3 text-sm text-text-secondary">
                        <p>Submitted by Asha Menon</p>
                        <p>Reviewed by Branch Manager</p>
                        <p>Pending Finance approval</p>
                      </div>
                    </div>
                    <button
                      type="button"
                      className="w-full rounded-full bg-accent-primary px-4 py-2 text-sm font-semibold"
                      style={{ color: 'var(--accent-on-primary)' }}
                    >
                      Approve Expense
                    </button>
                  </div>
                </aside>
              )}
            </div>

            <section className="mt-8 space-y-6 rounded-xl border border-border-default bg-background-surface p-5 shadow-sm">
              <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-accent-primary">
                    EDS-006
                  </p>
                  <h2 className="mt-2 text-2xl font-semibold text-text-primary">
                    Enterprise Component Library
                  </h2>
                  <p className="mt-2 max-w-3xl text-sm leading-6 text-text-secondary">
                    Reusable, theme-aware, accessible components now cover foundation, layout,
                    navigation, forms, data display, workflow, feedback, AI, banking, and security layers.
                  </p>
                </div>
                <RoleBadge role="Design System Maintainer" elevated />
              </div>

              <div className="grid gap-4 md:grid-cols-3">
                <MetricCard label="Component Contracts" value={`${componentRegistry.length}`} helper="Published from registry" />
                <MetricCard label="EDS Layers" value={`${libraryLayerCount}`} helper="Foundation to security" tone="success" />
                <MetricCard label="Theme Modes" value="3" helper="Light, dark, contrast" tone="warning" />
              </div>

              <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_360px]">
                <div className="space-y-6">
                  <EnterpriseTable columns={registryColumns} rows={registryRows} />

                  <div className="grid gap-4 lg:grid-cols-2">
                    <div className="rounded-xl border border-border-default bg-background-elevated p-4">
                      <h3 className="text-lg font-semibold text-text-primary">Form Controls</h3>
                      <div className="mt-4 space-y-4">
                        <TextInput label="Employee Search" placeholder="Search by name or employee ID" helperText="Supports validation and localized helper copy." />
                        <Checkbox label="Require approval audit note" defaultChecked />
                        <Toggle
                          checked={autosaveEnabled}
                          label="Autosave draft"
                          onClick={() => setAutosaveEnabled((enabled) => !enabled)}
                        />
                      </div>
                    </div>

                    <div className="space-y-4">
                      <ApprovalCard
                        title="Travel Expense"
                        requester="Asha Menon | Branch 1204"
                        amount="INR 18,420"
                        onApprove={() => setDrawerOpen(true)}
                      >
                        Includes semantic status, requester metadata, and an auditable action surface.
                      </ApprovalCard>
                      <Alert title="Component contract ready" tone="success">
                        EDS components expose typed props, theme tokens, focus states, and semantic variants.
                      </Alert>
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <AISummary
                    summary="FinDNA recommends approving the expense after receipt attachment. No duplicate claims were detected."
                    suggestions={['Request receipt', 'Approve after attachment', 'Add audit note']}
                  />
                  <Customer360Card
                    name="Nisha Rao"
                    customerId="CIF-104928"
                    risk="medium"
                    relationshipValue="INR 42.8L"
                  />
                  <LoanSummaryCard
                    accountNumber="LN-7721-001"
                    product="Vehicle Loan"
                    outstanding="INR 7.4L"
                    status="standard"
                  />
                  <div className="flex flex-wrap gap-3">
                    <EDSButton size="sm">Primary</EDSButton>
                    <EDSButton size="sm" variant="secondary">Secondary</EDSButton>
                  </div>
                </div>
              </div>
            </section>

            <DashboardLayout
              title={activeDashboardTitle}
              description="Monitor, understand, decide, and act from one reusable dashboard framework with standard widget contracts."
              persona={dashboardPersona}
              actions={[
                { label: 'Refresh', icon: <RefreshCw className="h-4 w-4" /> },
                { label: 'Save Layout', icon: <PlusCircle className="h-4 w-4" /> },
              ]}
            >
              <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-border-default bg-background-elevated p-3">
                <div className="flex flex-wrap gap-2">
                  {(['executive', 'branch'] as const).map((persona) => (
                    <button
                      key={persona}
                      type="button"
                      onClick={() => setDashboardPersona(persona)}
                      className={`rounded-full px-4 py-2 text-sm font-semibold transition duration-normal ease-standard ${
                        dashboardPersona === persona
                          ? 'bg-accent-primary'
                          : 'border border-border-default bg-background-surface text-text-secondary'
                      }`}
                      style={dashboardPersona === persona ? { color: 'var(--accent-on-primary)' } : undefined}
                    >
                      {persona === 'executive' ? 'Executive' : 'Branch Manager'}
                    </button>
                  ))}
                </div>
                <div className="flex flex-wrap gap-2 text-sm text-text-secondary">
                  <span className="rounded-full bg-background-surface px-3 py-2">
                    Widgets: {dashboardWidgetRegistry.length}
                  </span>
                  <span className="rounded-full bg-background-surface px-3 py-2">
                    Grid: 12 / 8 / 4
                  </span>
                  <span className="rounded-full bg-background-surface px-3 py-2">
                    Refresh SLA: under 1s cached
                  </span>
                </div>
              </div>

              <DashboardGrid>
                <KPIWidget
                  title={dashboardPersona === 'executive' ? 'Revenue' : 'Customers Today'}
                  value={dashboardPersona === 'executive' ? 'INR 18.4Cr' : '146'}
                  trend="up"
                  change={dashboardPersona === 'executive' ? '+8.2% vs last month' : '+18 since opening'}
                  drilldownTarget="/dashboards/revenue"
                />
                <KPIWidget
                  title={dashboardPersona === 'executive' ? 'Loan Book' : 'Collections'}
                  value={dashboardPersona === 'executive' ? 'INR 812Cr' : 'INR 42.6L'}
                  trend="up"
                  change={dashboardPersona === 'executive' ? '+4.7% portfolio growth' : '94% target achieved'}
                  drilldownTarget="/dashboards/loan-book"
                />
                <KPIWidget
                  title={dashboardPersona === 'executive' ? 'NPA' : 'Pending Approvals'}
                  value={dashboardPersona === 'executive' ? '2.1%' : '18'}
                  trend={dashboardPersona === 'executive' ? 'down' : 'up'}
                  change={dashboardPersona === 'executive' ? '-0.3% improvement' : '+5 urgent today'}
                  drilldownTarget="/dashboards/exceptions"
                />
                <KPIWidget
                  title={dashboardPersona === 'executive' ? 'Cash Position' : 'Cash Balance'}
                  value={dashboardPersona === 'executive' ? 'INR 96Cr' : 'INR 84.2L'}
                  trend="up"
                  change="Healthy buffer"
                  drilldownTarget="/dashboards/treasury"
                />
                <AlertWidget alerts={dashboardAlerts} />
                <QuickActionsWidget
                  actions={[
                    { label: dashboardPersona === 'executive' ? 'Open Risk Review' : 'Open Account' },
                    { label: dashboardPersona === 'executive' ? 'Branch Ranking' : 'Receive Payment' },
                    { label: dashboardPersona === 'executive' ? 'Portfolio Mix' : 'Create Loan' },
                  ]}
                />
                <ChartWidget
                  title={dashboardPersona === 'executive' ? 'Revenue Trend' : 'Daily Activity'}
                  description="Summary chart with a consistent drill-down path."
                  data={dashboardChartData}
                  drilldownTarget="/dashboards/charts/revenue-trend"
                />
                <TaskWidget tasks={dashboardTasks} />
                <ApprovalWidget approvals={dashboardApprovals} onApprove={() => setDrawerOpen(true)} />
                <ActivityWidget activities={dashboardActivities} />
                <AISummaryWidget
                  summary={
                    dashboardPersona === 'executive'
                      ? 'Branch revenue is above plan, but NPA movement is concentrated in two regions. Collections follow-up should be prioritized before month end.'
                      : 'Today is collection-heavy. Cash balance is healthy, but KYC renewals and pending approvals need attention before close of business.'
                  }
                  suggestions={['Open drill-down', 'Assign follow-up', 'Save this layout']}
                />
              </DashboardGrid>
            </DashboardLayout>

            <section className="mt-8 space-y-4">
              <div className="flex flex-col gap-3 rounded-xl border border-border-default bg-background-surface p-4 shadow-sm lg:flex-row lg:items-center lg:justify-between">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-accent-primary">
                    EDS-008
                  </p>
                  <h2 className="mt-2 text-2xl font-semibold text-text-primary">
                    Enterprise Data Grid Framework
                  </h2>
                  <p className="mt-2 max-w-3xl text-sm leading-6 text-text-secondary">
                    Search, filter, review, bulk update, export, approve, audit, and analyze from one reusable grid contract.
                  </p>
                </div>
                <div className="flex flex-wrap gap-2 text-sm text-text-secondary">
                  <span className="rounded-full bg-background-elevated px-3 py-2">
                    Contracts: {dataGridRegistry.length}
                  </span>
                  <span className="rounded-full bg-background-elevated px-3 py-2">
                    Last event: {lastGridEvent}
                  </span>
                </div>
              </div>

              <EnterpriseGrid
                title="Employee Operations Grid"
                description="Reference implementation for saved views, column personalization, row selection, bulk actions, audit context, AI prompts, and responsive table/card modes."
                columns={employeeGridColumns}
                rows={employeeGridRows}
                savedViews={employeeSavedViews}
                pageSize={4}
                auditMode
                bulkActions={[
                  { label: 'Approve', permission: 'employees.approve' },
                  { label: 'Assign', permission: 'employees.assign' },
                  { label: 'Export', permission: 'employees.export' },
                ]}
                rowActions={[
                  { label: 'View' },
                  { label: 'Audit' },
                  { label: 'Documents' },
                ]}
                onEvent={(event) => setLastGridEvent(event.name)}
              />
            </section>

            <section className="mt-8 space-y-4">
              <div className="flex flex-col gap-3 rounded-xl border border-border-default bg-background-surface p-4 shadow-sm lg:flex-row lg:items-center lg:justify-between">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-accent-primary">
                    EDS-009
                  </p>
                  <h2 className="mt-2 text-2xl font-semibold text-text-primary">
                    Enterprise Form & Wizard Framework
                  </h2>
                  <p className="mt-2 max-w-3xl text-sm leading-6 text-text-secondary">
                    Create, edit, validate, autosave, attach, review, approve, and submit through one reusable guided process contract.
                  </p>
                </div>
                <div className="flex flex-wrap gap-2 text-sm text-text-secondary">
                  <span className="rounded-full bg-background-elevated px-3 py-2">
                    Contracts: {wizardRegistry.length}
                  </span>
                  <span className="rounded-full bg-background-elevated px-3 py-2">
                    Last event: {lastWizardEvent}
                  </span>
                </div>
              </div>

              <EnterpriseWizard
                title="Employee Onboarding Wizard"
                description="Reference implementation for structured creation flows with drafts, validation, document checklist, AI guidance, review, and workflow handoff."
                steps={employeeWizardSteps}
                checklist={employeeWizardChecklist}
                attachments={employeeWizardAttachments}
                validationItems={employeeWizardValidationItems}
                reviewGroups={employeeWizardReviewGroups}
                approvalRequired
                approvalApprover="HR Operations Queue"
                aiTips={[
                  'Suggest designation from department and branch workload.',
                  'Summarize missing documents before approval handoff.',
                  'Validate salary band against branch policy.',
                ]}
                renderStep={renderEmployeeWizardStep}
                onEvent={(event) => setLastWizardEvent(event.name)}
              />
            </section>

            <section className="mt-8 space-y-4">
              <div className="flex flex-col gap-3 rounded-xl border border-border-default bg-background-surface p-4 shadow-sm lg:flex-row lg:items-center lg:justify-between">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-accent-primary">
                    EDS-010
                  </p>
                  <h2 className="mt-2 text-2xl font-semibold text-text-primary">
                    Workflow & Approval UX Framework
                  </h2>
                  <p className="mt-2 max-w-3xl text-sm leading-6 text-text-secondary">
                    Configure, execute, monitor, audit, and analyze approvals through one shared workflow UX contract.
                  </p>
                </div>
                <div className="flex flex-wrap gap-2 text-sm text-text-secondary">
                  <span className="rounded-full bg-background-elevated px-3 py-2">
                    Contracts: {workflowRegistry.length}
                  </span>
                  <span className="rounded-full bg-background-elevated px-3 py-2">
                    Last event: {lastWorkflowEvent}
                  </span>
                </div>
              </div>

              <div className="grid gap-4 xl:grid-cols-[420px_minmax(0,1fr)]">
                <ApprovalInbox
                  tasks={workflowTasks}
                  activeTaskId={activeWorkflowId}
                  onSelectTask={(workflowId) => {
                    setActiveWorkflowId(workflowId);
                    setLastWorkflowEvent('WORKFLOW_VIEWED');
                  }}
                  onAction={(workflowId, action) => {
                    setActiveWorkflowId(workflowId);
                    setLastWorkflowEvent(`ACTION_SELECTED:${action}`);
                  }}
                />
                <WorkflowViewer
                  workflow={activeWorkflow}
                  timeline={workflowTimelineItems}
                  comments={workflowComments}
                  auditEntries={workflowAuditEntries}
                  attachments={['OfferLetter.pdf', 'Aadhaar-OCR.json', 'SalaryBandReview.xlsx']}
                  availability={{
                    approve: true,
                    reject: true,
                    return: true,
                    requestChanges: true,
                    delegate: true,
                    escalate: true,
                    hold: true,
                  }}
                  onEvent={(event) => setLastWorkflowEvent(event.name)}
                />
              </div>

              <WorkflowDesigner nodes={workflowDesignerNodes} />
              <WorkflowAnalytics metrics={workflowAnalyticsMetrics} />
            </section>
          </section>
        </main>
      </div>

      <footer className="hidden h-8 items-center justify-between border-t border-border-default bg-background-surface px-6 text-xs text-text-secondary md:flex">
        <span>ARTH.OS v1.0 | Production | Branch 1204 | Connected</span>
        <span className="inline-flex items-center gap-2">
          <Clock3 className="h-3.5 w-3.5" />
          Theme: {activeTheme.name}
        </span>
      </footer>

      <nav className="fixed inset-x-0 bottom-0 z-sidebar grid h-[var(--shell-mobile-nav-height)] grid-cols-5 border-t border-border-default bg-background-surface md:hidden">
        {mobileTabs.map((item) => {
          const Icon = item.icon;
          return (
            <button
              key={item.label}
              type="button"
              className="flex flex-col items-center justify-center gap-1 text-xs font-semibold text-text-secondary"
              aria-label={item.label}
            >
              <Icon className="h-5 w-5" />
              {item.label}
            </button>
          );
        })}
      </nav>

      <button
        type="button"
        className="fixed bottom-24 right-6 z-ai inline-flex items-center gap-3 rounded-full bg-accent-primary px-5 py-3 text-sm font-semibold shadow-xl md:bottom-12"
        style={{ color: 'var(--accent-on-primary)' }}
      >
        <Sparkles className="h-5 w-5" />
        Ask FinDNA
      </button>

      {mobileMenuOpen && (
        <div className="fixed inset-0 z-drawer bg-background-header lg:hidden">
          <div className="absolute inset-y-0 left-0 shadow-xl">{sidebar}</div>
          <button
            type="button"
            className="absolute right-4 top-4 inline-flex h-10 w-10 items-center justify-center rounded-xl border border-border-default bg-background-surface text-text-secondary"
            onClick={() => setMobileMenuOpen(false)}
            aria-label="Close navigation"
          >
            <X className="h-5 w-5" />
          </button>
        </div>
      )}

      {commandOpen && (
        <div className="fixed inset-0 z-modal flex items-start justify-center bg-background-header px-4 py-20 backdrop-blur-sm">
          <div className="w-full max-w-2xl overflow-hidden rounded-xl border border-border-default bg-background-surface shadow-xl">
            <div className="flex items-center gap-3 border-b border-border-default px-4 py-4">
              <Search className="h-5 w-5 text-text-muted" />
              <input
                autoFocus
                value={searchQuery}
                onChange={(event) => setSearchQuery(event.target.value)}
                placeholder="Search ARTH.OS or run a command"
                className="min-w-0 flex-1 bg-transparent text-sm text-text-primary outline-none placeholder:text-text-muted"
              />
              <button
                type="button"
                onClick={() => setCommandOpen(false)}
                className="rounded-md border border-border-default px-2 py-1 text-xs font-semibold text-text-secondary"
              >
                Esc
              </button>
            </div>
            <div className="max-h-80 overflow-y-auto p-2">
              {visibleCommands.map((action) => (
                <button
                  key={action}
                  type="button"
                  className="flex w-full items-center justify-between rounded-xl px-4 py-3 text-left text-sm font-semibold text-text-primary hover:bg-background-elevated"
                  onClick={() => setCommandOpen(false)}
                >
                  {action}
                  <ChevronRight className="h-4 w-4 text-text-muted" />
                </button>
              ))}
              {visibleCommands.length === 0 && (
                <p className="px-4 py-6 text-sm text-text-secondary">No matching commands found.</p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
