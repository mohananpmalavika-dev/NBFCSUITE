# Frontend Microservices Routing Guide

## Overview

The frontend can now dynamically route to 19+ microservices using two approaches:

1. **Development Mode**: Direct service URLs (localhost:8001-8019)
2. **Production Mode**: API Gateway with path-based routing (single entry point)

---

## Architecture

```
Local Development:
┌─────────────────────────────────────────────────────────┐
│ Frontend (Next.js) - Port 3000                          │
├─────────────────────────────────────────────────────────┤
│ .env.local configuration:                               │
│ • NEXT_PUBLIC_AUTH_API_URL=http://localhost:8001        │
│ • NEXT_PUBLIC_HRMS_API_URL=http://localhost:8012        │
│ • NEXT_PUBLIC_LOS_API_URL=http://localhost:8002         │
│ • ... (all 19 services)                                 │
├─────────────────────────────────────────────────────────┤
│ Direct HTTP calls to individual services                │
└─────────────────────────────────────────────────────────┘
        ↓         ↓         ↓         ↓         ↓
   Auth   LOS    HRMS    Account   ...
  (8001) (8002) (8012)   (8008)

Render Production:
┌─────────────────────────────────────────────────────────┐
│ Frontend (Next.js) on Vercel                            │
├─────────────────────────────────────────────────────────┤
│ .env.production configuration:                          │
│ • NEXT_PUBLIC_API_GATEWAY_URL=https://api.myapp.com    │
├─────────────────────────────────────────────────────────┤
│ All requests routed through single API Gateway          │
└─────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────┐
│ Nginx API Gateway - Port 8080                           │
│ (Render service)                                        │
├─────────────────────────────────────────────────────────┤
│ Path-based routing:                                     │
│ • /auth/*        → auth-service:8000                    │
│ • /los/*         → los-service:8000                     │
│ • /hrms/*        → hrms-service:8000                    │
│ • /accounting/*  → accounting-service:8000              │
│ • ... (all 19 services)                                 │
└─────────────────────────────────────────────────────────┘
        ↓         ↓         ↓         ↓         ↓
   Auth   LOS    HRMS    Account   ...
```

---

## Setup Instructions

### 1. Local Development Setup

The `.env.local` file is already configured with all service URLs:

```bash
# apps/customer-app/.env.local
NEXT_PUBLIC_AUTH_API_URL=http://localhost:8001
NEXT_PUBLIC_HRMS_API_URL=http://localhost:8012
NEXT_PUBLIC_LOS_API_URL=http://localhost:8002
# ... etc (all 19 services)
```

**Start local development:**
```bash
cd apps/customer-app
npm install
npm run dev  # Starts on http://localhost:3000
```

**Start all services with Docker Compose:**
```bash
docker-compose up
```

Services will be available at:
- Frontend: http://localhost:3000
- Auth Service: http://localhost:8001
- LOS Service: http://localhost:8002
- HRMS Service: http://localhost:8012
- ... (see docker-compose.yml for all ports)

---

### 2. Production Setup (Render)

For Render production, use the API Gateway:

**Create `.env.production` in frontend:**
```bash
# apps/customer-app/.env.production
NEXT_PUBLIC_API_GATEWAY_URL=https://api-gateway.yourapp.onrender.com
```

**Deploy Nginx API Gateway to Render:**

1. Create a new Render service:
   - Name: `api-gateway`
   - Environment: Docker
   - Dockerfile Path: `infra/nginx/Dockerfile`
   - Port: 8080
   - No environment variables needed

2. All requests will automatically route:
   - `https://frontend.vercel.app/api/auth/login` → internally calls `https://api-gateway.onrender.com/auth/login`
   - This routes to: `http://auth-service:8000/login`

---

## Code Implementation

### Updated api.ts - Service URL Resolution

```typescript
// getServiceURL() function intelligently routes requests:

const getServiceURL = (serviceName: string): string => {
  const apiGateway = process.env.NEXT_PUBLIC_API_GATEWAY_URL;
  
  if (apiGateway) {
    // Production: Use API Gateway with path routing
    return `${apiGateway}/${serviceName}`;
  }
  
  // Development: Use individual service URLs
  const serviceUrls: Record<string, string> = {
    auth: process.env.NEXT_PUBLIC_AUTH_API_URL || 'http://localhost:8001',
    hrms: process.env.NEXT_PUBLIC_HRMS_API_URL || 'http://localhost:8012',
    los: process.env.NEXT_PUBLIC_LOS_API_URL || 'http://localhost:8002',
    // ... all 19 services
  };
  
  return serviceUrls[serviceName] || 'http://localhost:8000';
};

// Example usage:
const hrmsAxiosInstance = axios.create({
  baseURL: getServiceURL('hrms'),  // Automatically uses correct URL
});
```

### Using Services in Components

```typescript
// Example: Call HRMS service
import { hrmsAxiosInstance } from '@/lib/api';

export async function getDepartments(tenantId: string) {
  const response = await hrmsAxiosInstance.get('/departments', {
    params: { tenant_id: tenantId },
    headers: {
      'X-Tenant-Id': tenantId,
      'X-User-Id': userId,
    },
  });
  return response.data;
}

// Works in both:
// - Local: calls http://localhost:8012/departments
// - Render: calls https://api-gateway.onrender.com/hrms/departments
```

---

## Service Mapping

| Service | Local Port | Env Variable | Production Path |
|---------|-----------|--------------|-----------------|
| Auth | 8001 | NEXT_PUBLIC_AUTH_API_URL | /auth |
| LOS | 8002 | NEXT_PUBLIC_LOS_API_URL | /los |
| LMS | 8003 | NEXT_PUBLIC_LMS_API_URL | /lms |
| Collections | 8004 | NEXT_PUBLIC_COLLECTIONS_API_URL | /collections |
| Customer | 8005 | NEXT_PUBLIC_CUSTOMER_API_URL | /customer |
| FinDNA | 8006 | NEXT_PUBLIC_FINDNA_API_URL | /findna |
| Deposits | 8007 | NEXT_PUBLIC_DEPOSITS_API_URL | /deposits |
| Accounting | 8008 | NEXT_PUBLIC_ACCOUNTING_API_URL | /accounting |
| CRM | 8009 | NEXT_PUBLIC_CRM_API_URL | /crm |
| Document | 8010 | NEXT_PUBLIC_DOCUMENT_API_URL | /document |
| Compliance | 8011 | NEXT_PUBLIC_COMPLIANCE_API_URL | /compliance |
| HRMS | 8012 | NEXT_PUBLIC_HRMS_API_URL | /hrms |
| Gold Loans | 8013 | NEXT_PUBLIC_GOLD_API_URL | /gold |
| Treasury | 8014 | NEXT_PUBLIC_TREASURY_API_URL | /treasury |
| Wealth | 8015 | NEXT_PUBLIC_WEALTH_API_URL | /wealth |
| Insurance | 8016 | NEXT_PUBLIC_INSURANCE_API_URL | /insurance |
| Procurement | 8017 | NEXT_PUBLIC_PROCUREMENT_API_URL | /procurement |
| Platform | 8018 | NEXT_PUBLIC_PLATFORM_API_URL | /platform |
| Notifications | 8019 | NEXT_PUBLIC_NOTIFICATIONS_API_URL | /notifications |

---

## Nginx API Gateway Features

### CORS Support
All cross-origin headers are automatically included:
- `Access-Control-Allow-Origin: *`
- `Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS, PATCH`
- `Access-Control-Allow-Headers: Authorization, X-Tenant-Id, X-User-Id, ...`

### Multi-Tenant Headers
All headers are passed through:
- `X-Tenant-Id`
- `X-User-Id`
- `X-Scope-Organization-Id`
- `X-Scope-Zone-Id`
- `X-Scope-Region-Id`
- `X-Scope-Area-Id`
- `X-Scope-Branch-Id`

### Health Checks
- Gateway: `http://localhost:8080/health` → "API Gateway is running"
- Each service has individual health checks

### Large File Support
- Max body size: 100MB
- Suitable for document uploads

---

## Troubleshooting

### Issue: Service returns 404 in production
**Solution**: Ensure:
1. API Gateway is deployed and running
2. NEXT_PUBLIC_API_GATEWAY_URL is set correctly in .env.production
3. Individual services are running behind nginx
4. Service name matches route (e.g., `/hrms/` for HRMS service)

### Issue: CORS errors in development
**Solution**: 
- All CORS headers are configured in nginx
- Frontend should work with both direct URLs and API Gateway
- Check browser console for actual error

### Issue: Large file upload fails
**Solution**: 
- Increase `client_max_body_size` in nginx.conf if needed
- Currently set to 100MB
- Ensure backend service also accepts large uploads

---

## Deployment Checklist

### Local Development
- [ ] `.env.local` exists with all service URLs
- [ ] `docker-compose up` starts all services
- [ ] Frontend loads at http://localhost:3000
- [ ] API calls work to all services

### Render Production
- [ ] Create `.env.production` with `NEXT_PUBLIC_API_GATEWAY_URL`
- [ ] Deploy Nginx as separate Render service
- [ ] Deploy all 19+ backend services to Render
- [ ] Deploy frontend to Vercel
- [ ] Test API calls through API Gateway
- [ ] Verify CORS headers in browser DevTools

---

## Future Enhancements

1. **Rate Limiting**: Add rate limiting per service in nginx
2. **Caching**: Add Redis caching layer for frequently accessed endpoints
3. **Load Balancing**: Add multiple instances of services with load balancing
4. **Authentication**: Add API Gateway authentication/authorization
5. **Metrics**: Add Prometheus metrics collection
6. **Circuit Breaker**: Add circuit breaker pattern for service failures
