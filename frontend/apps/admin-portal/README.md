# NBFC Suite - Admin Portal

Modern admin portal built with Next.js 14, TypeScript, and Tailwind CSS for managing the NBFC Financial Suite.

## 🚀 Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: Radix UI + Shadcn/ui
- **State Management**: Zustand
- **Data Fetching**: TanStack Query (React Query)
- **Forms**: React Hook Form + Zod
- **HTTP Client**: Axios
- **Charts**: Recharts
- **Icons**: Lucide React

## 📁 Project Structure

```
src/
├── app/                    # Next.js app directory
│   ├── dashboard/         # Dashboard pages
│   ├── customers/         # Customer management
│   ├── loans/            # Loan management
│   ├── deposits/         # Deposit management
│   ├── workflows/        # Workflow & tasks
│   ├── accounting/       # Accounting module
│   ├── login/            # Authentication
│   └── layout.tsx        # Root layout
├── components/           # React components
│   └── ui/              # UI components (Shadcn)
├── contexts/            # React contexts
│   └── auth-context.tsx # Authentication context
├── hooks/               # Custom React hooks
├── lib/                 # Utility libraries
│   ├── api-client.ts   # API client
│   ├── auth.ts         # Auth utilities
│   ├── utils.ts        # Helper functions
│   └── constants.ts    # App constants
├── services/           # API service layer
│   ├── customer.service.ts
│   ├── loan.service.ts
│   ├── deposit.service.ts
│   ├── workflow.service.ts
│   └── dashboard.service.ts
├── types/              # TypeScript types
│   └── index.ts
└── middleware.ts       # Next.js middleware
```

## 🛠️ Setup

### Prerequisites

- Node.js 18+
- npm 9+
- Backend API running on http://localhost:8000

### Installation

```bash
# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local

# Edit .env.local with your configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Development

```bash
# Start development server
npm run dev

# Open browser
# http://localhost:3000
```

### Build

```bash
# Build for production
npm run build

# Start production server
npm start
```

## 🔐 Authentication

The app uses JWT token-based authentication:

1. Login at `/login`
2. Token stored in localStorage
3. Auto-attached to API requests
4. Protected routes via middleware

**Demo Credentials:**
- Username: `admin`
- Password: `admin123`

## 📄 Available Pages

### Public Pages
- `/` - Landing page
- `/login` - Login page

### Protected Pages
- `/dashboard` - Main dashboard
- `/customers` - Customer list & management
- `/loans/applications` - Loan applications
- `/loans/accounts` - Active loan accounts
- `/deposits/accounts` - Deposit accounts
- `/workflows/tasks` - My tasks
- `/accounting/chart-of-accounts` - Chart of accounts
- `/reports` - Reports & analytics
- `/settings` - System settings

## 🎨 UI Components

Built using Shadcn/ui components:

- Button
- Card
- Input
- Label
- Badge
- Table
- Toast
- Skeleton
- And more...

## 📡 API Integration

All API calls go through the centralized API client (`src/lib/api-client.ts`):

```typescript
import { apiClient } from '@/lib/api-client'

// GET request
const response = await apiClient.get('/customers')

// POST request
const response = await apiClient.post('/customers', data)
```

Service layer abstracts API calls:

```typescript
import { customerService } from '@/services/customer.service'

// Get customers
const { data } = await customerService.getCustomers({ page: 1 })
```

## 🔧 Utility Functions

Common utilities in `src/lib/utils.ts`:

- `formatCurrency()` - Format Indian currency
- `formatDate()` - Format dates
- `formatPhone()` - Format phone numbers
- `calculateEMI()` - EMI calculation
- `isValidPAN()` - Validate PAN
- `isValidAadhaar()` - Validate Aadhaar
- And more...

## 🎯 Features

### Customer Management
- Customer list with search & filters
- Customer profile view
- Create/edit customer
- KYC management
- Document upload

### Loan Management
- Loan application workflow
- Application approval
- Loan account management
- Repayment tracking
- EMI schedule

### Deposit Management
- Open deposit accounts
- Manage savings/FD/RD/MIS
- Interest calculation
- Transactions

### Workflow & Tasks
- My tasks inbox
- Approve/reject workflows
- Task assignment
- SLA tracking

### Accounting
- Chart of accounts
- Journal entries
- Financial reports
- Trial balance

### Reports & Analytics
- Dashboard widgets
- Loan portfolio analytics
- Collection reports
- Custom reports

## 🚦 Middleware

Route protection via Next.js middleware (`src/middleware.ts`):

- Redirects unauthenticated users to `/login`
- Redirects authenticated users from `/login` to `/dashboard`
- Attaches auth token to requests

## 📱 Responsive Design

- Mobile-first approach
- Responsive layouts
- Touch-friendly UI
- Progressive enhancement

## 🔄 State Management

- **Auth State**: React Context (`auth-context.tsx`)
- **Server State**: TanStack Query
- **Form State**: React Hook Form
- **Local State**: React useState/useReducer

## 🧪 Development Guidelines

### Code Style
- Use TypeScript for type safety
- Follow React best practices
- Use functional components
- Implement proper error handling

### Component Structure
```typescript
'use client' // if client component

import { useState } from 'react'
import { Button } from '@/components/ui/button'

interface Props {
  // Props interface
}

export default function ComponentName({ }: Props) {
  // Component logic
  
  return (
    // JSX
  )
}
```

### API Calls
- Use service layer
- Handle loading states
- Show error messages
- Implement retry logic

## 📝 Environment Variables

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_API_VERSION=v1

# App Configuration
NEXT_PUBLIC_APP_NAME=NBFC Suite Admin Portal
NEXT_PUBLIC_APP_VERSION=2.0.0
```

## 🐛 Troubleshooting

### API Connection Issues
1. Check backend is running on port 8000
2. Verify CORS settings
3. Check .env.local configuration

### Authentication Issues
1. Clear localStorage
2. Check token expiry
3. Verify credentials

### Build Issues
1. Clear .next directory
2. Remove node_modules
3. Run `npm install` again

## 📚 Additional Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Shadcn/ui](https://ui.shadcn.com)
- [TanStack Query](https://tanstack.com/query)

## 🤝 Contributing

This is a private enterprise application. For changes:

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit for review

## 📄 License

Proprietary - All rights reserved

---

**NBFC Suite Admin Portal v2.0**  
*Tier-1 Enterprise Financial Platform*
