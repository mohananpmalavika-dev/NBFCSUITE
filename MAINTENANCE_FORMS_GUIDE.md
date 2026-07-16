# Locker Maintenance - Forms Implementation Guide

## 🎯 Purpose
Quick reference guide for developers completing the remaining Maintenance module forms.

---

## 📋 Forms to Implement

### 1. Schedule Preventive Maintenance Dialog ⏳
**File**: `frontend/apps/admin-portal/src/app/lockers/maintenance/page.tsx`  
**Component**: `ScheduleMaintenanceDialog`  
**Status**: Placeholder exists, needs full implementation

#### Fields Required:
```typescript
{
  locker_id: string           // Required - Dropdown with search
  branch_id: string           // Required - Auto-filled from locker
  maintenance_type: enum      // Required - Select from MaintenanceType enum
  scheduled_date: date        // Required - Date picker
  scheduled_time: time        // Optional - Time picker
  is_recurring: boolean       // Optional - Checkbox
  recurring_frequency: enum   // Conditional - If is_recurring = true
  assigned_to: string         // Required - User/technician dropdown
  description: string         // Optional - Textarea (max 500 chars)
}
```

#### Validation Rules:
- ✅ Locker must be in "available" or "allocated" status
- ✅ Scheduled date cannot be in the past
- ✅ Recurring frequency required if is_recurring = true
- ✅ Assigned to must be active user with maintenance role
- ✅ Description max 500 characters

#### API Call:
```typescript
const result = await maintenanceService.schedulePreventiveMaintenance({
  locker_id: selectedLocker,
  branch_id: branchId,
  maintenance_type: maintenanceType,
  scheduled_date: formatDate(scheduledDate),
  scheduled_time: scheduledTime || undefined,
  is_recurring: isRecurring,
  recurring_frequency: isRecurring ? recurringFrequency : undefined,
  assigned_to: assignedTo,
  description: description || undefined
})
```

#### UI Pattern Reference:
Look at `SurrenderApplicationDialog` in surrender page for similar form pattern.

---

### 2. Report Breakdown Dialog ⏳
**File**: `frontend/apps/admin-portal/src/app/lockers/maintenance/page.tsx`  
**Component**: `ReportBreakdownDialog`  
**Status**: Placeholder exists, needs full implementation

#### Fields Required:
```typescript
{
  locker_id: string              // Required - Dropdown with search
  branch_id: string              // Required - Auto-filled from locker
  maintenance_type: enum         // Required - Breakdown types only
  priority: enum                 // Required - MaintenancePriority enum
  description: string            // Required - Textarea (min 10, max 1000 chars)
  customer_reported: boolean     // Optional - Checkbox
  customer_id: string            // Conditional - If customer_reported = true
  assigned_to: string            // Required - User/technician dropdown
}
```

#### Maintenance Type Options (Breakdown Only):
```typescript
- LOCK_JAMMING
- KEY_LOST
- LOCK_REPLACEMENT
- MASTER_KEY_REGENERATION
- LOCKER_REPAIR
```

#### Priority Options:
```typescript
- LOW (default)
- MEDIUM
- HIGH
- URGENT
- EMERGENCY
```

#### Validation Rules:
- ✅ Locker must exist and not be retired
- ✅ Description required with min 10 characters
- ✅ Customer ID required if customer_reported = true
- ✅ Priority URGENT or EMERGENCY should show warning message
- ✅ Auto-assign if only one technician available

#### API Call:
```typescript
const result = await maintenanceService.reportBreakdown({
  locker_id: selectedLocker,
  branch_id: branchId,
  maintenance_type: maintenanceType,
  priority: priority,
  description: description,
  customer_reported: customerReported,
  customer_id: customerReported ? customerId : undefined,
  assigned_to: assignedTo
})
```

#### UI Pattern Reference:
Similar to `BreakingInitiateDialog` in breaking page with priority selection.

---

### 3. Maintenance Details Dialog ⏳
**File**: `frontend/apps/admin-portal/src/app/lockers/maintenance/page.tsx`  
**Component**: `MaintenanceDetailsDialog`  
**Status**: Placeholder exists, needs tabbed implementation

#### Tab Structure:
```
┌─────────────────────────────────────────────────────────────┐
│ Tabs: [Details] [Action] [Cost] [Completion]               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Tab content based on maintenance status                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### Tab 1: Details (Read-only)
Display all maintenance record fields:
- Maintenance number, type, category, priority
- Locker details, branch
- Scheduled date/time, started date, completed date
- Assigned to, status
- Description, findings, recommendations
- Timestamps

#### Tab 2: Action (Type-specific forms)
Show appropriate form based on `maintenance_type`:

**A. Lock Servicing Form**:
```typescript
{
  lock_condition_before: string       // Required - Select (Good/Fair/Poor)
  lubrication_done: boolean          // Required
  parts_replaced: boolean            // Required
  replaced_parts_list: string[]      // Conditional - If parts_replaced
  lock_tested_after_servicing: bool  // Required
  lock_condition_after: string       // Required - Select (Good/Fair/Poor)
  action_taken: string               // Required - Textarea
}
```

**B. Key Duplication Form**:
```typescript
{
  number_of_keys_duplicated: number  // Required - Number input (1-10)
  key_type_duplicated: string        // Required - Select (Customer/Bank/Master)
  key_storage_location: string       // Required - Input
  action_taken: string               // Required - Textarea
}
```

**C. Cleaning Form**:
```typescript
{
  cleaning_type: enum                // Required - CleaningType enum
  areas_cleaned: string[]            // Required - Multi-select
  cleaning_materials_used: string[]  // Required - Multi-select
  sanitization_done: boolean         // Required
  action_taken: string               // Required - Textarea
}
```

**D. Vault Maintenance Form**:
```typescript
{
  humidity_level_before: number      // Optional - Number (0-100%)
  humidity_level_after: number       // Optional - Number (0-100%)
  dehumidifier_checked: boolean      // Required
  dehumidifier_condition: string     // Conditional - Select
  ventilation_checked: boolean       // Required
  action_taken: string               // Required - Textarea
}
```

**E. Fire Protection Check Form**:
```typescript
{
  fire_extinguisher_checked: boolean        // Required
  fire_extinguisher_expiry_date: date       // Conditional - Date picker
  smoke_detector_tested: boolean            // Required
  smoke_detector_working: boolean           // Conditional
  sprinkler_system_tested: boolean          // Required
  sprinkler_system_working: boolean         // Conditional
  action_taken: string                      // Required - Textarea
}
```

**F. Resolve Lock Jamming Form**:
```typescript
{
  jamming_cause: enum                       // Required - LockJammingCause
  jamming_resolution_steps: string[]        // Required - Multi-input
  lock_repaired: boolean                    // Required
  lock_replaced_due_to_jamming: boolean     // Required
  action_taken: string                      // Required - Textarea
}
```

**G. Handle Lost Key Form**:
```typescript
{
  fir_details: string                       // Required - Input
  indemnity_bond_collected: boolean         // Required
  indemnity_bond_path: string               // Conditional - File upload
  key_replacement_action: enum              // Required - KeyReplacementAction
  new_key_number: string                    // Conditional - Input
  customer_charge_amount: number            // Optional - Number
  action_taken: string                      // Required - Textarea
}
```

**H. Replace Lock Form**:
```typescript
{
  old_lock_number: string                   // Required - Input
  old_lock_condition: string                // Required - Select
  new_lock_number: string                   // Required - Input
  new_lock_type: string                     // Required - Input
  lock_installation_date: date              // Required - Date picker
  keys_issued_count: number                 // Required - Number (2-10)
  customer_notified_of_replacement: boolean // Required
  action_taken: string                      // Required - Textarea
}
```

**I. Regenerate Master Key Form**:
```typescript
{
  authorization_for_regeneration: string    // Required - Input
  new_master_key_number: string             // Required - Input
  all_affected_lockers: string[]            // Required - Multi-select
  customer_keys_retained: boolean           // Required
  action_taken: string                      // Required - Textarea
}
```

**J. Repair Locker Form**:
```typescript
{
  damage_type: string                       // Required - Select
  damage_description: string                // Required - Textarea
  damage_assessment_report_path: string     // Optional - File upload
  repair_materials_used: string[]           // Required - Multi-input
  before_repair_photos: string[]            // Optional - File upload (multi)
  after_repair_photos: string[]             // Optional - File upload (multi)
  customer_charged: boolean                 // Optional
  customer_charge_reason: string            // Conditional - Input
  customer_charge_amount: number            // Conditional - Number
  action_taken: string                      // Required - Textarea
}
```

#### Tab 3: Cost (Editable if not completed)
```typescript
{
  labor_cost: number                        // Required - Number
  material_cost: number                     // Required - Number
  external_service_cost: number             // Optional - Number
  // Auto-calculated:
  total_maintenance_cost: number            // Read-only
  customer_charged: boolean                 // Checkbox
  customer_charge_reason: string            // Conditional - Input
  customer_charge_amount: number            // Conditional - Number
  customer_charge_gst_amount: number        // Auto-calculated (18%)
  customer_total_charge: number             // Auto-calculated
}
```

#### Tab 4: Completion (Only if status = IN_PROGRESS)
```typescript
{
  completed_date: date                      // Required - Date picker
  quality_check_done: boolean               // Required
  quality_check_by: string                  // Conditional - User dropdown
  quality_check_passed: boolean             // Conditional - Checkbox
  quality_check_remarks: string             // Conditional - Textarea
  customer_satisfaction_rating: number      // Optional - Star rating (1-5)
  customer_satisfaction_feedback: string    // Optional - Textarea
  recommendations: string                   // Optional - Textarea
  completion_certificate_path: string       // Optional - File upload
}
```

---

## 🎨 UI Component Library

### Use shadcn/ui Components:
```typescript
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { Checkbox } from '@/components/ui/checkbox'
import { Calendar } from '@/components/ui/calendar'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
```

### Form Validation with Zod:
```typescript
import { z } from 'zod'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'

const scheduleMaintenanceSchema = z.object({
  locker_id: z.string().uuid(),
  maintenance_type: z.enum([...MaintenanceType values...]),
  scheduled_date: z.date().min(new Date()),
  is_recurring: z.boolean().optional(),
  recurring_frequency: z.enum([...RecurringFrequency values...]).optional(),
  assigned_to: z.string().uuid(),
  description: z.string().max(500).optional()
}).refine((data) => {
  if (data.is_recurring && !data.recurring_frequency) {
    return false
  }
  return true
}, {
  message: "Recurring frequency required when is_recurring is true"
})
```

---

## 🔄 State Management Pattern

### Use React Query:
```typescript
// Mutation for scheduling
const scheduleMutation = useMutation({
  mutationFn: (data) => maintenanceService.schedulePreventiveMaintenance(data),
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['maintenance'] })
    toast({ title: 'Success', description: 'Maintenance scheduled' })
    onClose()
  },
  onError: (error) => {
    toast({ title: 'Error', description: error.message, variant: 'destructive' })
  }
})

// Submit handler
const onSubmit = (data) => {
  scheduleMutation.mutate(data)
}
```

---

## 📸 File Upload Implementation

### Photo Upload Component:
```typescript
import { useState } from 'react'
import { Upload } from 'lucide-react'

function PhotoUpload({ onUpload, maxFiles = 5 }) {
  const [files, setFiles] = useState<File[]>([])
  
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(e.target.files || [])
    if (files.length + selectedFiles.length > maxFiles) {
      toast({ title: 'Error', description: `Max ${maxFiles} files allowed` })
      return
    }
    setFiles([...files, ...selectedFiles])
    onUpload([...files, ...selectedFiles])
  }
  
  return (
    <div>
      <Label>Upload Photos (Max {maxFiles})</Label>
      <input
        type="file"
        accept="image/*"
        multiple
        onChange={handleFileChange}
        className="hidden"
        id="photo-upload"
      />
      <Button
        type="button"
        variant="outline"
        onClick={() => document.getElementById('photo-upload')?.click()}
      >
        <Upload className="mr-2 h-4 w-4" />
        Upload Photos ({files.length}/{maxFiles})
      </Button>
      {/* Preview thumbnails */}
      <div className="grid grid-cols-3 gap-2 mt-2">
        {files.map((file, index) => (
          <div key={index} className="relative">
            <img
              src={URL.createObjectURL(file)}
              alt={`Preview ${index + 1}`}
              className="w-full h-24 object-cover rounded"
            />
            <Button
              size="sm"
              variant="destructive"
              className="absolute top-1 right-1"
              onClick={() => {
                const newFiles = files.filter((_, i) => i !== index)
                setFiles(newFiles)
                onUpload(newFiles)
              }}
            >
              ×
            </Button>
          </div>
        ))}
      </div>
    </div>
  )
}
```

---

## 🧪 Testing Checklist

### Unit Tests (Per Form):
```typescript
describe('ScheduleMaintenanceDialog', () => {
  test('renders all required fields', () => {})
  test('validates required fields', () => {})
  test('shows recurring options when checkbox checked', () => {})
  test('submits form with valid data', () => {})
  test('shows error message on API failure', () => {})
})
```

### Integration Tests:
```typescript
describe('Maintenance Workflow', () => {
  test('schedule preventive maintenance', async () => {})
  test('report breakdown maintenance', async () => {})
  test('perform maintenance action', async () => {})
  test('complete with quality check', async () => {})
})
```

---

## 📚 Reference Examples

### Similar Forms in Codebase:
1. **Breaking Initiate Dialog** - Complex form with multiple witnesses
2. **Surrender Application Dialog** - Form with conditional fields
3. **Allocation Create Dialog** - Form with dropdown dependencies
4. **Key Handover Dialog** - Form with file uploads

### Copy Patterns From:
```
frontend/apps/admin-portal/src/app/lockers/breaking/page.tsx
frontend/apps/admin-portal/src/app/lockers/surrender/page.tsx
```

---

## ⚡ Quick Start Commands

### Run Development Server:
```bash
cd frontend/apps/admin-portal
npm run dev
```

### Run Tests:
```bash
npm run test
npm run test:watch  # Watch mode
npm run test:coverage  # Coverage report
```

### Build for Production:
```bash
npm run build
npm run start
```

---

## 🎯 Success Criteria

### Form Completion Checklist:
- ✅ All fields implemented with proper types
- ✅ Validation working (client-side with Zod)
- ✅ API integration working
- ✅ Error handling implemented
- ✅ Loading states shown
- ✅ Success messages displayed
- ✅ Forms reset after submission
- ✅ File upload working (if applicable)
- ✅ Responsive design (mobile-friendly)
- ✅ Accessibility compliant (ARIA labels)
- ✅ Tests passing (unit + integration)

---

## 💡 Tips & Best Practices

1. **Use TypeScript strictly** - No `any` types
2. **Validate both client and server side**
3. **Show loading states** during API calls
4. **Handle errors gracefully** with user-friendly messages
5. **Use optimistic updates** where appropriate
6. **Keep forms simple** - one task per form
7. **Add helpful placeholder text**
8. **Use proper label associations** for accessibility
9. **Test on mobile devices** - forms should work on small screens
10. **Follow existing patterns** from Breaking/Surrender modules

---

## 📞 Need Help?

### Documentation References:
- `LOCKER_MAINTENANCE_COMPLETE.md` - Full technical specs
- `LOCKER_MODULE_ROADMAP.md` - Overall progress
- shadcn/ui docs: https://ui.shadcn.com/
- React Hook Form docs: https://react-hook-form.com/
- Zod docs: https://zod.dev/

### Code References:
- Breaking module: `src/app/lockers/breaking/`
- Surrender module: `src/app/lockers/surrender/`
- Service layer: `src/services/locker.service.ts`

---

**Document Version**: 1.0  
**Created**: Current Session  
**Target Completion**: 3-4 days  
**Priority**: High
