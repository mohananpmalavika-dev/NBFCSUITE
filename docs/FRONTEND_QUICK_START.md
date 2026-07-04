# Frontend Microservices Routing - Quick Start

## 📋 What Changed?

The frontend now intelligently routes to 19+ microservices using:
- **Local Dev**: Direct URLs per service (localhost:8001-8019)
- **Production**: Single API Gateway entry point

No more hardcoded single auth service!

---

## 🚀 Local Development (5 minutes)

### Step 1: Start Everything
```bash
# From project root
docker-compose up
```

This starts:
- ✅ PostgreSQL (port 5432)
- ✅ All 19 microservices (ports 8001-8019)
- ✅ Nginx API Gateway (port 8080) - optional
- ✅ Frontend (port 3000)

### Step 2: Access Frontend
```
http://localhost:3000
```

### Step 3: How It Works

The frontend **automatically** routes to correct services:

```typescript
// In api.ts - this works automatically!
const hrmsAxiosInstance = axios.create({
  baseURL: getServiceURL('hrms'),  // → http://localhost:8012
});

const accountingAxiosInstance = axios.create({
  baseURL: getServiceURL('accounting'),  // → http://localhost:8008
});

// Works for all 19 services!
```

---

## 🧪 Testing with API Gateway (Optional)

If you want to test the API Gateway in local dev:

### Edit `.env.local` (in apps/customer-app/):
```bash
# Comment this out:
# NEXT_PUBLIC_HRMS_API_URL=http://localhost:8012

# Add this:
NEXT_PUBLIC_API_GATEWAY_URL=http://localhost:8080
```

### Now all requests go through Nginx:
```
Frontend → Nginx (8080) → /hrms/ → HRMS Service (8012)
```

### Test it:
```bash
# This should return "API Gateway is running"
curl http://localhost:8080/health

# This should work:
curl http://localhost:8080/hrms/departments
```

---

## 🌐 Production on Render

### Step 1: Deploy Nginx API Gateway
Create a **new Render Service**:
- Name: `api-gateway`
- Docker Image: Use repository
- Dockerfile Path: `infra/nginx/Dockerfile`
- Port: 8080
- Publish: Yes (get public URL like: api-gateway-abc123.onrender.com)

### Step 2: Update Frontend `.env.production`
```bash
# In apps/customer-app/.env.production
NEXT_PUBLIC_API_GATEWAY_URL=https://api-gateway-abc123.onrender.com
```

### Step 3: Deploy Backend Services
Deploy each microservice separately (they're already dockerized):
```
auth-service → https://auth-service-abc123.onrender.com
los-service → https://los-service-abc123.onrender.com
... (all 19 services)
```

**Important**: Don't expose them publicly! They'll run on internal Render network.

### Step 4: Deploy Frontend to Vercel
```bash
# Vercel automatically uses .env.production
npm run build
vercel deploy
```

### Result:
```
Frontend (Vercel) 
  ↓ (API call)
API Gateway (Render, port 8080)
  ↓ (routes to /hrms/)
HRMS Service (Render, internal)
  ↓
Database (Render PostgreSQL)
```

---

## 📊 Service Map

| Service | Local | Env Var | Route |
|---------|-------|---------|-------|
| Auth | 8001 | NEXT_PUBLIC_AUTH_API_URL | `/auth` |
| LOS | 8002 | NEXT_PUBLIC_LOS_API_URL | `/los` |
| LMS | 8003 | NEXT_PUBLIC_LMS_API_URL | `/lms` |
| HRMS | 8012 | NEXT_PUBLIC_HRMS_API_URL | `/hrms` |
| Accounting | 8008 | NEXT_PUBLIC_ACCOUNTING_API_URL | `/accounting` |
| ... | ... | ... | ... |

See `FRONTEND_ROUTING_GUIDE.md` for complete list.

---

## 🔧 How It Works (Technical)

### 1. Service URL Resolution
```typescript
// In apps/customer-app/lib/api.ts
const getServiceURL = (serviceName: string): string => {
  const apiGateway = process.env.NEXT_PUBLIC_API_GATEWAY_URL;
  
  if (apiGateway) {
    // Production: http://api-gateway.com/serviceName
    return `${apiGateway}/${serviceName}`;
  }
  
  // Development: http://localhost:8001, http://localhost:8012, etc.
  const serviceUrls = {
    auth: process.env.NEXT_PUBLIC_AUTH_API_URL || 'http://localhost:8001',
    hrms: process.env.NEXT_PUBLIC_HRMS_API_URL || 'http://localhost:8012',
    // ... all services
  };
  
  return serviceUrls[serviceName];
};
```

### 2. Nginx API Gateway
```nginx
# infra/nginx/nginx.conf

location /hrms/ {
  proxy_pass http://hrms-service:8000/;  # Internal routing
}

location /accounting/ {
  proxy_pass http://accounting-service:8000/;  # Internal routing
}
# ... all services
```

### 3. Usage in Components
```typescript
// Example: Call HRMS
import { hrmsAxiosInstance } from '@/lib/api';

async function getDepartments(tenantId) {
  // Automatically uses correct URL:
  // Local: http://localhost:8012/departments
  // Render: https://api-gateway.com/hrms/departments
  const response = await hrmsAxiosInstance.get('/departments', {
    params: { tenant_id: tenantId }
  });
  return response.data;
}
```

---

## ✅ Verification Checklist

### Local Development
- [ ] `.env.local` exists in `apps/customer-app/`
- [ ] `docker-compose up` starts all services
- [ ] Frontend loads at http://localhost:3000
- [ ] API calls work to individual services
- [ ] (Optional) API Gateway works at http://localhost:8080

### Production
- [ ] API Gateway deployed to Render
- [ ] All 19 services deployed to Render
- [ ] Frontend `.env.production` has API Gateway URL
- [ ] Frontend deployed to Vercel
- [ ] API calls route through gateway correctly

---

## 🐛 Troubleshooting

### Issue: Service returns 404
```
Check:
1. Is service running? (docker-compose logs servicename)
2. Is URL correct in .env.local?
3. Does service have /health endpoint?
```

### Issue: CORS errors
```
Solution: Nginx automatically adds CORS headers
If still failing:
- Check browser DevTools Network tab
- Verify Nginx is running: curl http://localhost:8080/health
```

### Issue: "Cannot find module" errors
```
Solution: 
npm install in apps/customer-app
Restart dev server: npm run dev
```

### Issue: API Gateway doesn't route request
```
Check nginx logs:
docker-compose logs api-gateway
```

---

## 📚 Documentation

- **Full guide**: See `FRONTEND_ROUTING_GUIDE.md`
- **Environment setup**: See `.env.local` comments
- **Production config**: See `.env.production` comments

---

## 🎯 Next Steps

1. **Run locally**: `docker-compose up`
2. **Test frontend**: http://localhost:3000
3. **Check API calls**: Open DevTools Network tab
4. **For production**: Follow Render deployment steps in `.env.production`

That's it! 🚀
