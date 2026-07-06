# Database Setup Guide

## Problem: Gold Loan Page is Blank

The Gold Loan page (and other pages) appear blank because the backend cannot connect to a database. The application requires PostgreSQL to store and retrieve data.

## Quick Fix Options

### Option 1: Free Cloud Database (Recommended) ⭐

Use a free cloud PostgreSQL database - no installation needed!

#### A. Render.com (Easiest)
1. Go to https://dashboard.render.com/
2. Click "New +" → "PostgreSQL"
3. Name: `nbfc-suite-db`
4. Database: `nbfc_suite`
5. User: `nbfc_admin`
6. Region: Choose closest to you
7. Plan: **Free** (0.1 GB storage)
8. Click "Create Database"
9. Copy the **External Database URL** (looks like: `postgresql://user:pass@dpg-xxxxx.oregon-postgres.render.com/dbname`)
10. Update `backend/.env`:
```env
DATABASE_URL=postgresql://user:pass@dpg-xxxxx.oregon-postgres.render.com/dbname
```

#### B. Railway.app
1. Go to https://railway.app/
2. Click "Start a New Project" → "Provision PostgreSQL"
3. Copy the `DATABASE_URL` from the Variables tab
4. Update `backend/.env` with the copied URL

#### C. Supabase (Good for production)
1. Go to https://supabase.com/
2. Create a new project
3. Go to Settings → Database
4. Copy the Connection String (URI format)
5. Update `backend/.env` with the connection string

#### D. ElephantSQL
1. Go to https://www.elephantsql.com/
2. Sign up and create a new instance (Tiny Turtle - Free)
3. Copy the URL
4. Update `backend/.env`

### Option 2: Local PostgreSQL Installation

#### Windows
1. **Download PostgreSQL:**
   - Go to https://www.postgresql.org/download/windows/
   - Download PostgreSQL 15 or 16
   - Run the installer
   - Set password: `nbfc_secure_2026`
   - Port: `5432`

2. **Create Database:**
   ```cmd
   psql -U postgres
   CREATE DATABASE nbfc_suite;
   CREATE USER nbfc_admin WITH PASSWORD 'nbfc_secure_2026';
   GRANT ALL PRIVILEGES ON DATABASE nbfc_suite TO nbfc_admin;
   \q
   ```

3. **Verify Connection:**
   Your `backend/.env` should already have:
   ```env
   DATABASE_URL=postgresql://nbfc_admin:nbfc_secure_2026@localhost:5432/nbfc_suite
   ```

#### Using Docker (All Platforms)
```cmd
docker run -d ^
  --name nbfc-postgres ^
  -e POSTGRES_DB=nbfc_suite ^
  -e POSTGRES_USER=nbfc_admin ^
  -e POSTGRES_PASSWORD=nbfc_secure_2026 ^
  -p 5432:5432 ^
  postgres:15

# Verify it's running
docker ps
```

## After Setting Up Database

1. **Update `.env` file:**
   ```env
   DATABASE_URL=your_database_url_here
   ```

2. **Restart Backend:**
   ```cmd
   cd backend
   python main.py
   ```

3. **Initialize Database:**
   The backend will automatically create all tables on startup. You should see:
   ```
   ✅ Database tables created successfully
   ✅ Default tenant created
   ```

4. **Test Gold Loan Page:**
   - Go to http://localhost:3000/gold-loans
   - Page should now load with data or empty state (not blank)

## Troubleshooting

### Still Seeing Blank Page?

1. **Check Backend Logs:**
   - Look for database connection errors
   - Should see: "Database connection ready"

2. **Open Browser Console (F12):**
   - Check for API errors
   - Look at Network tab for failed requests

3. **Test API Directly:**
   ```
   http://localhost:8000/api/v1/gold-loans/statistics
   ```
   Should return JSON, not an error

### Database Connection Errors

**Error: "connection refused"**
- PostgreSQL is not running
- Wrong host/port in DATABASE_URL

**Error: "authentication failed"**
- Wrong username/password
- User doesn't have permissions

**Error: "database does not exist"**
- Create the database first (see instructions above)

## Current Configuration

Your current `.env` file is set to:
```env
DATABASE_URL=postgresql://nbfc_admin:nbfc_secure_2026@localhost:5432/nbfc_suite
```

This expects PostgreSQL running locally. If you don't want to install it, use Option 1 (Cloud Database).

## Need Help?

- Check backend logs: `python backend/main.py`
- Test health endpoint: http://localhost:8000/health
- Check database tables: http://localhost:8000/debug/tables
