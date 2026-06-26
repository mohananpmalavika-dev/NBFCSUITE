# NBFCSUITE Customer Web App

Next.js-based customer portal for loan management, KYC, payments, and financial services.

## Features

- 🔐 User Authentication (JWT)
- 💰 Loan Management (view loans, EMI, payments)
- 📄 Document Management (upload, view KYC)
- 📊 Dashboard (loans, payments, score)
- 💳 Payment Processing
- 📱 Responsive Design
- 🎨 Modern UI/UX

## Tech Stack

- **Framework:** Next.js 14
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **State Management:** Zustand (optional)
- **API Client:** Axios
- **Charts:** Recharts (for analytics)

## Setup

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
cd C:\NBFCSUITE\apps\customer-app

# Install dependencies
npm install

# Create .env.local (copy from .env.example if exists)
cp .env.example .env.local

# Update API URL if needed (default: http://localhost:8000)
# NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Development

```bash
npm run dev
# Open http://localhost:3000
```

### Build

```bash
npm run build
npm start
```

## Project Structure

```
customer-app/
├── app/
│   ├── layout.tsx              # Root layout
│   ├── page.tsx                # Dashboard
│   ├── login/
│   │   └── page.tsx            # Login page
│   ├── loans/
│   │   ├── page.tsx            # Loans list
│   │   └── [id]/page.tsx       # Loan details
│   ├── payments/
│   │   └── page.tsx            # Payment history
│   ├── documents/
│   │   └── page.tsx            # KYC documents
│   ├── kyc/
│   │   └── page.tsx            # KYC status
│   ├── score/
│   │   └── page.tsx            # Credit/Behavior score
│   └── settings/
│       └── page.tsx            # User settings
├── lib/
│   ├── api.ts                  # API client wrapper
│   └── auth-context.tsx        # Auth state management
├── components/
│   ├── Navbar.tsx              # Navigation bar
│   ├── Card.tsx                # Reusable card
│   ├── Button.tsx              # Reusable button
│   └── ...
├── public/
│   └── ...                      # Static assets
├── package.json
├── tsconfig.json
├── next.config.js
├── tailwind.config.js           # Tailwind config
└── .env.example                 # Environment template
```

## API Integration

All API calls go through `lib/api.ts` which wraps Axios and handles:
- JWT token management
- Error handling
- Request/response interceptors

Example:
```typescript
import { apiClient } from '@/lib/api';

// Login
const response = await apiClient.login('username', 'password');

// Fetch loans
const loans = await apiClient.getLoanDetails('LOAN-001');

// Record payment
await apiClient.recordPayment('LOAN-001', { amount: 15800, mode: 'upi' });
```

## Authentication

Uses JWT tokens from Auth Service:
- Tokens stored in context (can be extended to localStorage)
- Automatic token injection in API requests
- Protected routes redirect to login if no token

## Environment Variables

Create `.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Pages to Implement

- [ ] Loan Application Form
- [ ] EMI Calculator
- [ ] Payment Gateway Integration
- [ ] E-Signature for documents
- [ ] Video KYC Flow
- [ ] AI Financial Assistant Chat
- [ ] Notifications/Alerts
- [ ] Mobile responsive refinements

## Testing

```bash
npm run lint
npm run type-check
```

## Deployment

### Docker

```bash
docker build -t nbfcsuite/customer-app .
docker run -p 3000:3000 nbfcsuite/customer-app
```

### Kubernetes

```bash
kubectl apply -f k8s/deployment.yaml
```

## Contributing

See `../../CONTRIBUTING.md`

---

**Last Updated:** 2026-06-26
