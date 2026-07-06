# Customer 360 / CIF Module - Frontend Implementation

## Overview

Complete frontend implementation for the Customer Information File (CIF) / Customer 360 module with comprehensive features for customer management, KYC verification, document management, and more.

## Features Implemented

### 1. **Customer 360 Header**
- Customer summary with avatar and initials
- Quick status indicators (KYC, Risk Rating, CIBIL Score)
- Blacklist and inactive status badges
- Contact information display
- Navigation back to customer list

### 2. **Customer Overview**
- Personal information display
- Contact details and address
- Identity information (PAN, Aadhaar)
- Financial profile
- System information

### 3. **KYC Management**
- **Aadhaar eKYC**
  - OTP-based verification
  - Biometric verification support
  - Real-time verification status
- **DigiLocker Integration**
  - OAuth flow implementation
  - Document fetching from DigiLocker
  - Automatic document storage
- **KYC Completion Tracking**
  - Progress percentage
  - Verification checklist
  - Multiple verification methods

### 4. **Document Vault**
- Document upload with metadata
- Document verification workflow
- Status tracking (Pending, Verified, Rejected, Expired)
- Document viewer
- Expiry date tracking
- Document type categorization
- Delete and download functionality

### 5. **Family Tree Management**
- Add/edit family members
- Relationship type selection
- Nominee designation with percentage
- Emergency contact marking
- Dependent tracking
- Nominee percentage validation (must total 100%)
- Family member demographics

### 6. **Bank Account Management**
- Multiple bank accounts support
- Primary account designation
- Account verification methods
  - Penny Drop (₹1 transfer)
  - Bank statement verification
  - Passbook verification
- IFSC code validation
- Disbursement and collection flags
- Account type support (Savings, Current, Overdraft)

### 7. **Credit Bureau Integration**
- Multi-bureau support (CIBIL, Equifax, Experian, CRIF)
- Credit report pulling
- Credit score display with color coding
- Bureau pull history
- Account statistics (Total, Active, Outstanding)
- Enquiry tracking (1M, 3M, 6M, 12M)
- Report download functionality

### 8. **Activity Timeline**
- Chronological activity tracking
- Activity categorization
- Important activity flagging
- Manual note addition
- Activity filtering
- Change tracking (old vs new values)
- Activity summary dashboard
- User attribution

### 9. **Risk Profiling**
- Risk rating display (Low, Medium, High, Very High)
- Risk score calculation
- Risk factor identification
- Positive factor highlighting
- Visual risk indicators
- Risk metrics dashboard

## Technical Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **UI Components**: shadcn/ui (Radix UI primitives)
- **State Management**: React Query (TanStack Query)
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **Form Handling**: React Hook Form (via shadcn forms)
- **API Client**: Axios with custom wrapper

## File Structure

```
frontend/apps/admin-portal/src/
├── components/
│   └── customers/
│       ├── customer-360-header.tsx       # Customer header component
│       ├── customer-overview.tsx         # Overview tab
│       ├── kyc-management.tsx            # KYC verification
│       ├── document-vault.tsx            # Document management
│       ├── family-tree.tsx               # Family members
│       ├── bank-accounts.tsx             # Bank accounts
│       ├── credit-bureau.tsx             # Credit reports
│       ├── customer-timeline.tsx         # Activity timeline
│       └── risk-profile.tsx              # Risk assessment
├── types/
│   ├── customer.types.ts                 # Customer type definitions
│   └── index.ts                          # Type exports
├── services/
│   └── customer.service.ts               # API service layer
└── app/
    └── customers/
        └── [id]/
            └── page.tsx                  # Customer 360 page

```

## Component Usage

### Customer 360 Page

```tsx
import { Customer360Header } from '@/components/customers/customer-360-header'
import { CustomerOverview } from '@/components/customers/customer-overview'
// ... other imports

export default function CustomerDetailPage() {
  const { data: customer } = useQuery({
    queryKey: ['customer', customerId],
    queryFn: () => customerService.getCustomer(customerId),
  })

  return (
    <div>
      <Customer360Header customer={customer.data} />
      <Tabs>
        <TabsContent value="overview">
          <CustomerOverview customer={customer.data} />
        </TabsContent>
        {/* Other tabs */}
      </Tabs>
    </div>
  )
}
```

## API Integration

All components use the centralized `customerService` for API calls:

```typescript
// Fetch customer
customerService.getCustomer(id)

// KYC operations
customerService.initiateAadhaarOTP(customerId, aadhaarNumber)
customerService.verifyAadhaarOTP(customerId, data)
customerService.initiateDigiLocker(customerId, redirectUri)

// Document operations
customerService.getDocuments(customerId)
customerService.uploadDocument(customerId, formData)
customerService.verifyDocument(customerId, documentId, status)

// Family operations
customerService.getFamilyMembers(customerId)
customerService.addFamilyMember(customerId, data)
customerService.validateNominees(customerId)

// Bank account operations
customerService.getBankAccounts(customerId)
customerService.addBankAccount(customerId, data)
customerService.verifyAccount(customerId, accountId, method)

// Bureau operations
customerService.pullCreditReport(customerId, provider)
customerService.getBureauHistory(customerId)
customerService.getLatestCreditScore(customerId)

// Timeline operations
customerService.getTimeline(customerId, filters)
customerService.logActivity(customerId, data)
```

## Key Features

### Real-time Validation
- Aadhaar number (12 digits)
- PAN number (10 characters)
- Mobile number (10 digits)
- IFSC code (11 characters)
- Nominee percentage (must total 100%)

### Status Indicators
- Color-coded badges for all statuses
- Icon-based status representation
- Progress bars for completion tracking

### Responsive Design
- Mobile-first approach
- Grid layouts for different screen sizes
- Collapsible sections for mobile

### Error Handling
- Toast notifications for all operations
- Detailed error messages from backend
- Optimistic UI updates with rollback

### Loading States
- Skeleton loaders for data fetching
- Button loading indicators
- Disabled states during mutations

## Future Enhancements

1. **Video KYC Integration**
2. **Biometric Device Integration**
3. **Document OCR for Auto-fill**
4. **Advanced Risk Scoring Algorithm**
5. **Loan Application Integration**
6. **WhatsApp Notification Integration**
7. **Email Campaign Management**
8. **Customer Portal Access**
9. **Consent Management**
10. **Audit Trail Viewer**

## Testing

Components are designed to be testable with:
- React Testing Library
- Mock Service Worker (MSW) for API mocking
- Jest for unit tests

## Performance Optimizations

- React Query caching
- Lazy loading of heavy components
- Optimistic updates
- Debounced search inputs
- Pagination for large lists

## Accessibility

- Semantic HTML structure
- ARIA labels where needed
- Keyboard navigation support
- Screen reader friendly
- Focus management in modals

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Contributing

When adding new features:
1. Follow existing component patterns
2. Use TypeScript strictly
3. Add proper error handling
4. Include loading states
5. Make components responsive
6. Add toast notifications
7. Update type definitions

## License

Proprietary - NBFC Suite
