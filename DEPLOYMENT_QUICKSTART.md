# 🚀 DEPLOYMENT QUICKSTART - Get Live in 30 Minutes!

## Choose Your Path

### 🎯 Path 1: FREE Demo (Recommended First)
**Platform**: Render.com  
**Cost**: FREE  
**Time**: 20-30 minutes  
**Best For**: Testing, demos, POC

### 🎯 Path 2: Production Ready
**Platform**: DigitalOcean  
**Cost**: $20-40/month  
**Time**: 2-4 hours  
**Best For**: Real clients, production use

### 🎯 Path 3: Enterprise Scale
**Platform**: AWS/Azure  
**Cost**: $100+/month  
**Time**: 1-2 days  
**Best For**: High traffic, compliance needs

---

# 🏃 PATH 1: RENDER.COM (START HERE!)

## Step 1: Prepare Repository (5 mins)

```bash
# Navigate to your project
cd c:\NBFCSUITE

# Initialize git if not done
git init
git add .
git commit -m "Initial commit: NBFC Financial Suite"

# Create GitHub repository (via GitHub website)
# Then push:
git remote add origin https://github.com/YOUR_USERNAME/nbfc-suite.git
git branch -M main
git push -u origin main
```

## Step 2: Sign Up on Render (2 mins)

1. Visit: https://dashboard.render.com/register
2. Click "Sign up with GitHub"
3. Authorize Render to access repositories

## Step 3: Deploy Backend (8 mins)

1. **Create Web Service**
   - Dashboard → Click "New +" → "Web Service"
   - Select your `nbfc-suite` repository
   - Click "Connect"

2. **Configure Service**
   ```
   Name: nbfc-backend
   Region: Oregon (US West)
   Branch: main
   Root Directory: backend
   Runtime: Python 3
   Python Version: 3.11.9
   Build Command: pip install --upgrade pip && pip install -r requirements.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   Instance Type: Free
   ```

3. **Add Environment Variables** (Click "Advanced" → "Add Environment Variable")
   
   Copy-paste each line:
   ```
   PYTHON_VERSION=3.11.9
   SECRET_KEY=nbfc2026_change_this_in_production_min32chars
   JWT_SECRET_KEY=jwt2026_change_this_in_production_min32chars
   JWT_ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   REFRESH_TOKEN_EXPIRE_DAYS=7
   APP_ENV=production
   LOG_LEVEL=INFO
   ENABLE_SWAGGER=true
   CORS_ORIGINS=*
   TENANT_ISOLATION_ENABLED=true
   DEFAULT_TENANT=default
   ```

4. **Create Service** → Wait 10-15 minutes for build
   - Watch logs in real-time
   - Service URL will be: `https://nbfc-backend-XXXX.onrender.com`

## Step 4: Create Database (3 mins)

1. **New PostgreSQL**
   - Dashboard → "New +" → "PostgreSQL"
   - Name: `nbfc-postgres`
   - Region: Oregon (same as backend)
   - PostgreSQL Version: 15
   - Instance Type: Free
   - Click "Create Database"

2. **Get Connection String**
   - Click on database → Info tab
   - Copy "Internal Database URL"
   - Should look like: `postgresql://user:pass@dpg-xxx/dbname`

3. **Add to Backend**
   - Go back to backend service
   - Environment → Add Variable
   ```
   DATABASE_URL=<paste-internal-database-url>
   ```
   - Service will auto-redeploy

## Step 5: Run Migrations (2 mins)

1. **Open Shell**
   - Backend service → "Shell" tab (top right)
   - Wait for shell to connect

2. **Run Migration**
   ```bash
   cd backend
   alembic upgrade head
   ```
   
   You should see:
   ```
   INFO  [alembic.runtime.migration] Running upgrade -> xxx, Initial migration
   INFO  [alembic.runtime.migration] Running upgrade xxx -> yyy, Add gold loan tables
   ```

## Step 6: Deploy Frontend (5 mins)

1. **Create Static Site**
   - Dashboard → "New +" → "Static Site"
   - Select your `nbfc-suite` repository

2. **Configure**
   ```
   Name: nbfc-frontend
   Branch: main
   Root Directory: frontend/apps/admin-portal
   Build Command: npm install --legacy-peer-deps && npm run build
   Publish Directory: .next
   ```

3. **Environment Variables**
   ```
   NODE_ENV=production
   NEXT_PUBLIC_API_URL=https://nbfc-backend-XXXX.onrender.com/api/v1
   ```
   *(Replace XXXX with your actual backend URL)*

4. **Create Static Site** → Wait 10-15 minutes

## Step 7: Test & Access (5 mins)

### Test Backend
```bash
# Health check
curl https://nbfc-backend-XXXX.onrender.com/health

# Should return: {"status":"healthy","timestamp":"..."}
```

### Access Application
1. **Frontend**: `https://nbfc-frontend-XXXX.onrender.com`
2. **API Docs**: `https://nbfc-backend-XXXX.onrender.com/docs`
3. **Login**: 
   - Username: `admin`
   - Password: `admin123`
   *(Create this user in Step 8)*

## Step 8: Create Admin User (3 mins)

1. **Backend Shell**
   - Backend service → Shell tab

2. **Create User**
   ```python
   python -c "
   import asyncio
   from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
   from sqlalchemy.orm import sessionmaker
   from services.auth.service import AuthService
   import os

   async def create_admin():
       engine = create_async_engine(os.getenv('DATABASE_URL'))
       async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
       
       async with async_session() as session:
           service = AuthService(session)
           try:
               user = await service.create_user(
                   email='admin@nbfcsuite.com',
                   username='admin',
                   password='Admin@123',
                   first_name='System',
                   last_name='Administrator',
                   is_superuser=True
               )
               print(f'✅ Admin created: {user.email}')
           except Exception as e:
               print(f'❌ Error: {e}')

   asyncio.run(create_admin())
   "
   ```

## 🎉 SUCCESS!

Your application is now live:

| Service | URL | Status |
|---------|-----|--------|
| **Frontend** | https://nbfc-frontend-XXXX.onrender.com | ✅ Live |
| **Backend API** | https://nbfc-backend-XXXX.onrender.com | ✅ Live |
| **API Docs** | https://nbfc-backend-XXXX.onrender.com/docs | ✅ Live |
| **Database** | Internal (PostgreSQL 15) | ✅ Running |

### Login Credentials
- **URL**: Your frontend URL
- **Username**: `admin`
- **Password**: `Admin@123`

---

# 🏃 PATH 2: DIGITALOCEAN (PRODUCTION)

## Prerequisites
- Domain name (optional but recommended)
- Credit card for $5-20/month hosting

## Quick Deploy with Docker

### Step 1: Create Droplet (5 mins)

1. **Sign up**: https://digitalocean.com
2. **Create Droplet**:
   - Image: Ubuntu 22.04 LTS
   - Plan: Basic - $20/month (2GB RAM, 2 vCPU)
   - Data center: Choose nearest
   - Authentication: SSH Key (recommended) or Password
   - Hostname: `nbfc-suite`

3. **Note your IP**: `123.456.789.10`

### Step 2: Initial Setup (10 mins)

```bash
# SSH into server
ssh root@123.456.789.10

# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Verify
docker --version
docker-compose --version
```

### Step 3: Deploy Application (15 mins)

```bash
# Create directory
mkdir -p /opt/nbfc-suite
cd /opt/nbfc-suite

# Clone repository
git clone https://github.com/YOUR_USERNAME/nbfc-suite.git .

# Create environment file
cp .env.staging.example .env.staging

# Edit environment (use nano or vi)
nano .env.staging
```

**Update these values**:
```env
DB_PASSWORD=YOUR_SECURE_PASSWORD_HERE
REDIS_PASSWORD=YOUR_SECURE_REDIS_PASSWORD
SECRET_KEY=YOUR_SECRET_KEY_MIN_32_CHARS
JWT_SECRET_KEY=YOUR_JWT_SECRET_KEY_MIN_32_CHARS
CORS_ORIGINS=http://123.456.789.10,http://yourdomain.com
NEXT_PUBLIC_API_URL=http://123.456.789.10:8000/api/v1
```

```bash
# Start services
docker-compose -f docker-compose.staging.yml up -d

# Check status
docker-compose -f docker-compose.staging.yml ps

# View logs
docker-compose -f docker-compose.staging.yml logs -f
```

### Step 4: Run Migrations (2 mins)

```bash
docker-compose -f docker-compose.staging.yml exec backend alembic upgrade head
```

### Step 5: Access Application

- **Frontend**: `http://123.456.789.10:3000`
- **Backend**: `http://123.456.789.10:8000`
- **API Docs**: `http://123.456.789.10:8000/docs`

### Step 6: Setup Domain & SSL (Optional, 20 mins)

```bash
# Install Nginx & Certbot
apt install nginx certbot python3-certbot-nginx -y

# Stop Docker nginx
docker-compose -f docker-compose.staging.yml stop nginx

# Get SSL certificate
certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Start nginx again
docker-compose -f docker-compose.staging.yml start nginx
```

---

# 🏃 PATH 3: AWS (ENTERPRISE)

## Using Elastic Beanstalk (Simplest AWS Option)

### Step 1: Setup AWS CLI (10 mins)

```bash
# Install AWS CLI
pip install awscli awsebcli

# Configure
aws configure
# Enter: Access Key ID, Secret Access Key, Region (us-east-1)

# Verify
aws sts get-caller-identity
```

### Step 2: Initialize Application (5 mins)

```bash
cd c:\NBFCSUITE

# Initialize Elastic Beanstalk
eb init -p docker nbfc-suite --region us-east-1

# Create environment
eb create nbfc-production --database.engine postgres
```

### Step 3: Configure Environment (10 mins)

```bash
# Set environment variables
eb setenv \
  SECRET_KEY=your_secret_key \
  JWT_SECRET_KEY=your_jwt_secret \
  CORS_ORIGINS=https://your-domain.com

# Deploy
eb deploy

# Open in browser
eb open
```

---

# 🔧 TROUBLESHOOTING

## Common Issues

### 1. Build Fails on Render
**Error**: `Pillow build failed`  
**Fix**: Ensure `backend/runtime.txt` contains `python-3.11.9`

### 2. Database Connection Failed
**Error**: `Cannot connect to database`  
**Fix**: 
- Verify DATABASE_URL is set
- Use "Internal Database URL" from Render
- Check database is in same region

### 3. CORS Errors
**Error**: `CORS policy blocked`  
**Fix**: Update CORS_ORIGINS:
```
CORS_ORIGINS=https://your-frontend.onrender.com,http://localhost:3000
```

### 4. Frontend Can't Reach Backend
**Error**: `Network error` or `Failed to fetch`  
**Fix**: Update frontend env:
```
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com/api/v1
```

### 5. Service Sleeps (Render Free)
**Issue**: First request takes 60 seconds  
**Fix**: 
- Upgrade to paid plan ($7/month)
- Or use keep-alive service: https://uptimerobot.com

---

# 📊 DEPLOYMENT COMPARISON

| Feature | Render (Free) | DigitalOcean | AWS |
|---------|---------------|--------------|-----|
| **Monthly Cost** | $0 | $20-40 | $50-200+ |
| **Setup Time** | 30 mins | 2-4 hours | 4-8 hours |
| **Performance** | Good | Very Good | Excellent |
| **Uptime** | 99%* | 99.9% | 99.95% |
| **Auto-scaling** | No | Manual | Yes |
| **SSL** | Free | Free (Let's Encrypt) | Free |
| **Support** | Community | 24/7 | Enterprise |

*Service sleeps after 15 minutes of inactivity

---

# 📝 POST-DEPLOYMENT CHECKLIST

- [ ] Application accessible via URL
- [ ] Health check returns 200 OK
- [ ] API documentation loads (/docs)
- [ ] Login successful with admin credentials
- [ ] Dashboard displays correctly
- [ ] Create test customer
- [ ] Create test loan application
- [ ] Test file upload
- [ ] Check all modules accessible
- [ ] Setup monitoring (optional)
- [ ] Configure backups
- [ ] Document URLs and credentials
- [ ] Share with stakeholders

---

# 🎯 RECOMMENDED WORKFLOW

## Phase 1: Demo (Week 1)
✅ Deploy to Render (FREE)  
✅ Test all features  
✅ Get feedback  
✅ Fix bugs

## Phase 2: Pilot (Week 2-4)
✅ Deploy to DigitalOcean ($20/month)  
✅ Add custom domain  
✅ Setup SSL  
✅ Onboard test users  
✅ Monitor performance

## Phase 3: Production (Month 2+)
✅ Scale on DigitalOcean or move to AWS  
✅ Setup backups  
✅ Configure monitoring  
✅ Implement CI/CD  
✅ Full launch

---

# 🚀 WHAT'S NEXT?

1. **Choose your deployment path** (Path 1 recommended to start)
2. **Follow the steps** (copy-paste commands)
3. **Test your deployment**
4. **Share the URL** with stakeholders
5. **Get feedback** and iterate

Need help? I can:
- ✅ Debug specific deployment errors
- ✅ Create custom deployment scripts
- ✅ Setup CI/CD pipeline
- ✅ Configure monitoring & alerts
- ✅ Optimize for production

---

**Ready to deploy? Start with Path 1 (Render) - takes just 30 minutes!** 🎉

**Last Updated**: July 6, 2026  
**Version**: 2.0.0  
**Status**: Production Ready ✅
