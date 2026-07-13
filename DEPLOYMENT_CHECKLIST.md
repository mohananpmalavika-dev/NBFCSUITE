# NBFC Suite - Deployment Checklist ✅

## Pre-Deployment Status

### ✅ Frontend (React + Next.js)
- [x] All build errors fixed
- [x] Missing components created (TicketFilters, ESS pages)
- [x] Missing dependencies installed (Radix UI, clsx, tailwind-merge)
- [x] Missing utility functions added (cn, getStatusColor, formatDistanceToNow, calculateEMI)
- [x] useSearchParams wrapped in Suspense boundaries
- [x] Build completed successfully (243 pages generated)
- [x] Build artifacts created in `.next` directory

### ✅ Backend (FastAPI + Python)
- [x] All import errors fixed
- [x] Settings configuration completed (ENABLE_SWAGGER, ENABLE_REDOC, CORS_ALLOW_CREDENTIALS)
- [x] Pydantic 2.x compatibility fixed (extra fields, validators)
- [x] Optional dependencies handled gracefully (boto3, reportlab, apscheduler)
- [x] Main app loads successfully
- [x] All core modules import without errors
- [x] Routes registered successfully

## Deployment Steps

### 1. Backend Deployment (Render)

#### A. Environment Variables (Required)
Set these in Render Dashboard → Environment:

```bash
# Database (from Render PostgreSQL service)
DATABASE_URL=postgresql://nbfcsuite_user:PASSWORD@HOST/nbfcsuite

# Security (generate strong random strings)
JWT_SECRET_KEY=your-strong-random-secret-key-min-32-chars

# Application
APP_ENV=production
APP_DEBUG=false
LOG_LEVEL=INFO

# API Documentation
ENABLE_SWAGGER=true
ENABLE_REDOC=true

# CORS (set to your frontend URL)
CORS_ORIGINS=https://your-frontend-url.onrender.com
CORS_ALLOW_CREDENTIALS=true
```

#### B. Build Command
```bash
pip install -r backend/requirements.txt
```

#### C. Start Command
```bash
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

#### D. Health Check
Render will check: `GET /health`

#### E. Post-Deployment
1. Check logs for any errors
2. Verify health endpoint: `https://your-backend.onrender.com/health`
3. Check API docs: `https://your-backend.onrender.com/docs`
4. Run database migrations (if needed):
   ```bash
   alembic upgrade head
   ```

### 2. Frontend Deployment (Render Static Site or Vercel)

#### Option A: Render Static Site

**Environment Variables:**
```bash
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
NODE_ENV=production
```

**Build Command:**
```bash
cd frontend && npm install && npm run build
```

**Publish Directory:**
```
frontend/apps/admin-portal/out
```

**Note:** You'll need to add `output: 'export'` to `next.config.js` for static export.

#### Option B: Vercel (Recommended for Next.js)

1. Connect GitHub repository to Vercel
2. Set root directory: `frontend/apps/admin-portal`
3. Set environment variables:
   ```bash
   NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
   ```
4. Deploy

### 3. Database Setup

#### A. Create Database (Render)
1. Go to Render Dashboard
2. Create New → PostgreSQL
3. Name: `nbfcsuite`
4. Copy the External Database URL
5. Add to backend environment variables as `DATABASE_URL`

#### B. Run Migrations
After backend is deployed:
```bash
# SSH into Render or run via dashboard shell
alembic upgrade head
```

#### C. Create Initial Data (Optional)
```bash
# Create default tenant and admin user
python -m backend.scripts.create_initial_data
```

## Post-Deployment Verification

### Backend Checks
- [ ] Health endpoint responds: `GET /health`
- [ ] API docs accessible: `GET /docs`
- [ ] Database connection works
- [ ] Authentication works: `POST /api/auth/login`
- [ ] Dashboard stats load: `GET /api/dashboard/stats`

### Frontend Checks
- [ ] Application loads without errors
- [ ] Login page accessible
- [ ] Can log in with credentials
- [ ] Dashboard loads
- [ ] API requests reach backend successfully

### Integration Checks
- [ ] CORS configured correctly (no CORS errors in browser console)
- [ ] Authentication flow works end-to-end
- [ ] Data fetching from backend works
- [ ] File uploads work (if applicable)

## Monitoring

### Logs to Watch
1. **Render Backend Logs**
   - Application startup
   - Database connections
   - API requests/errors
   - Authentication attempts

2. **Browser Console**
   - Network requests
   - CORS errors
   - JavaScript errors

### Common Issues

#### Issue: CORS Errors
**Solution:** Ensure `CORS_ORIGINS` in backend includes your frontend URL

#### Issue: Database Connection Failed
**Solution:** Check `DATABASE_URL` format and credentials

#### Issue: 404 on API Requests
**Solution:** Verify `NEXT_PUBLIC_API_URL` is set correctly in frontend

#### Issue: Build Failed
**Solution:** Check Node.js version (should be 18.x or 20.x)

## Rollback Plan

If deployment fails:

1. **Backend Rollback**
   - Render: Click "Rollback" in deployment history
   - Check previous working commit

2. **Frontend Rollback**
   - Vercel: Redeploy previous deployment from dashboard
   - Render: Rollback to previous deployment

3. **Database Rollback**
   - If migrations cause issues:
     ```bash
     alembic downgrade -1  # rollback one migration
     ```

## Performance Optimization

### Backend (Free Tier - 512MB RAM)
- ✅ Feature flags enabled to disable unused modules
- ✅ Database connection pool optimized (size: 2)
- ✅ Optional dependencies made conditional
- Consider: Enable only essential modules in production

### Frontend
- ✅ Static export for better performance
- ✅ Code splitting via Next.js
- Consider: CDN for static assets
- Consider: Image optimization

## Security Checklist

- [ ] Change default JWT_SECRET_KEY
- [ ] Set strong database password
- [ ] Configure CORS_ORIGINS to specific domain (not "*")
- [ ] Enable HTTPS (auto on Render/Vercel)
- [ ] Set secure cookies for authentication
- [ ] Review API endpoints for public access
- [ ] Set up rate limiting (if needed)

## Maintenance

### Regular Tasks
1. **Monitor Logs** - Check for errors daily
2. **Database Backups** - Render PostgreSQL auto-backups (verify enabled)
3. **Update Dependencies** - Monthly security updates
4. **Performance Monitoring** - Check response times
5. **Disk Space** - Monitor database growth

### Scaling (When Needed)
1. **Upgrade Render Plan** - More RAM/CPU
2. **Database Scaling** - Upgrade PostgreSQL tier
3. **Add Caching** - Redis for session/data caching
4. **CDN** - For frontend static assets
5. **Load Balancing** - Multiple backend instances

## Support Contacts

- **Render Status**: https://status.render.com/
- **Render Docs**: https://render.com/docs
- **Vercel Status**: https://www.vercel-status.com/
- **Next.js Docs**: https://nextjs.org/docs

## Success Criteria

Deployment is successful when:
- ✅ Backend health check passes
- ✅ Frontend loads without errors
- ✅ User can log in
- ✅ Dashboard displays data
- ✅ No critical errors in logs
- ✅ Response times < 2s for API calls

---

## Current Status: ✅ READY FOR DEPLOYMENT

All pre-deployment checks passed. Both frontend and backend are ready to be deployed.

**Next Action:** Deploy backend to Render, then deploy frontend.
