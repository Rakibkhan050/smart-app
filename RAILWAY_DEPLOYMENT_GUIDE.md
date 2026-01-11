# 🚂 RAILWAY DEPLOYMENT GUIDE - Backend (Django)

## 🎯 Deploy Your Backend to Get Public API

This guide will deploy your Django backend to Railway.app and provide a public API URL like `https://smartapp-production.up.railway.app` that your Vercel frontend can connect to.

---

## 📋 TABLE OF CONTENTS

1. [What You'll Get](#1-what-youll-get)
2. [Prerequisites](#2-prerequisites)
3. [Prepare Django for Production](#3-prepare-django-for-production)
4. [Deploy to Railway](#4-deploy-to-railway)
5. [Configure Database](#5-configure-database)
6. [Environment Variables](#6-environment-variables)
7. [Run Migrations & Create Admin](#7-run-migrations--create-admin)
8. [Connect Frontend to Backend](#8-connect-frontend-to-backend)
9. [Troubleshooting](#9-troubleshooting)

---

## 1. What You'll Get

After deployment:
- ✅ **Public API URL:** `https://smartapp-production.up.railway.app`
- ✅ **PostgreSQL Database:** Production-ready database
- ✅ **Automatic HTTPS:** Free SSL certificate
- ✅ **Auto Deploys:** Push to GitHub = Auto deploy
- ✅ **Django Admin:** Accessible at `/admin`
- ✅ **Static Files:** Served via WhiteNoise
- ✅ **Free Trial:** $5 credit/month (then $5/month)

**Cost:** $5 free credit, then ~$5-10/month

---

## 2. Prerequisites

### Required Accounts:

1. **Railway Account** (Free trial)
   - Sign up: https://railway.app/
   - Use "Login with GitHub" for easy setup

2. **GitHub Account** (already have from Vercel guide)
   - Your code should already be on GitHub

### Verify Git Repository:

```powershell
cd "C:\Users\DELL\Desktop\New folder"

# Check remote
git remote -v

# Should show your GitHub repository
```

---

## 3. Prepare Django for Production

### Step 1: Update requirements.txt

```powershell
cd backend

# Generate current requirements
pip freeze > requirements.txt
```

Add these production packages to `backend/requirements.txt`:

```txt
# Existing packages
Django>=4.2.0
djangorestframework>=3.14.0
django-cors-headers>=4.3.0
channels>=4.0.0
dj-database-url>=2.1.0
python-dotenv>=1.0.0
celery>=5.3.0
redis>=5.0.0
Pillow>=10.1.0

# Production packages (ADD THESE)
gunicorn>=21.2.0
whitenoise>=6.6.0
psycopg2-binary>=2.9.9
dj-static>=0.0.6
```

**Save and commit:**
```powershell
git add requirements.txt
git commit -m "Add production dependencies"
git push
```

---

### Step 2: Create Production Settings

Create `backend/school_saas/production_settings.py`:

```python
from .settings import *
import os
import dj_database_url

# SECURITY
DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# ALLOWED_HOSTS
ALLOWED_HOSTS = [
    '.railway.app',
    '.vercel.app',
    'localhost',
    '127.0.0.1',
]

# Get Railway domain if available
RAILWAY_STATIC_URL = os.environ.get('RAILWAY_STATIC_URL')
if RAILWAY_STATIC_URL:
    ALLOWED_HOSTS.append(RAILWAY_STATIC_URL)

# DATABASE - Use Railway PostgreSQL
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# STATIC FILES
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# MEDIA FILES
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')

# MIDDLEWARE - Add WhiteNoise
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

# CORS - Allow Vercel frontend
CORS_ALLOWED_ORIGINS = [
    "https://smartapp.vercel.app",
    "https://smart-saas-project.vercel.app",
    os.environ.get('FRONTEND_URL', ''),
]

CORS_ALLOW_CREDENTIALS = True

# CSRF
CSRF_TRUSTED_ORIGINS = [
    "https://*.railway.app",
    "https://*.vercel.app",
]

# SECURE SETTINGS
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# LOGGING
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

---

### Step 3: Create Procfile (Railway Command)

Create `backend/Procfile`:

```
web: gunicorn school_saas.wsgi --bind 0.0.0.0:$PORT
```

---

### Step 4: Create runtime.txt (Python Version)

Create `backend/runtime.txt`:

```
python-3.11.7
```

---

### Step 5: Update WSGI Configuration

Edit `backend/school_saas/wsgi.py`:

```python
import os
from django.core.wsgi import get_wsgi_application

# Use production settings if RAILWAY_ENVIRONMENT exists
if os.environ.get('RAILWAY_ENVIRONMENT'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_saas.production_settings')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_saas.settings')

application = get_wsgi_application()
```

---

### Step 6: Create .env.example

Create `backend/.env.example`:

```env
# Django Settings
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=False
DJANGO_SETTINGS_MODULE=school_saas.production_settings

# Database (Railway provides this automatically)
DATABASE_URL=postgresql://user:password@host:5432/database

# Frontend URL (Your Vercel deployment)
FRONTEND_URL=https://smartapp.vercel.app

# CORS Origins (comma-separated)
CORS_ALLOWED_ORIGINS=https://smartapp.vercel.app,https://smart-saas-project.vercel.app

# Email Settings (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True

# AWS S3 (optional - for media files)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=
AWS_S3_REGION_NAME=

# Redis (optional - for Celery)
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=django-db
```

---

### Step 7: Commit All Changes

```powershell
cd "C:\Users\DELL\Desktop\New folder"

# Add all new files
git add backend/

# Commit
git commit -m "Add Railway production configuration"

# Push to GitHub
git push
```

---

## 4. Deploy to Railway

### Step 1: Create Railway Project

1. Go to: https://railway.app/new
2. Click **"Deploy from GitHub repo"**
3. Select your repository: `smart-saas-project`
4. Click on the repository

### Step 2: Configure Service

Railway auto-detects your Django app!

**Verify settings:**
- **Root Directory:** Leave empty or set to `backend/`
- **Build Command:** Auto-detected
- **Start Command:** `gunicorn school_saas.wsgi --bind 0.0.0.0:$PORT`

**If not auto-detected, manually set:**
1. Click your service
2. Go to **Settings**
3. **Build Command:** `pip install -r requirements.txt`
4. **Start Command:** `gunicorn school_saas.wsgi --bind 0.0.0.0:$PORT`
5. **Root Directory:** `backend`

### Step 3: Add PostgreSQL Database

1. Click **"+ New"** in Railway project
2. Select **"Database"**
3. Choose **"PostgreSQL"**
4. Database is automatically provisioned
5. `DATABASE_URL` is automatically added to your service

---

## 5. Configure Database

### Automatic Configuration

Railway automatically:
- ✅ Creates PostgreSQL database
- ✅ Adds `DATABASE_URL` environment variable
- ✅ Connects to your Django service

**Verify:**
1. Click your PostgreSQL service
2. Go to **"Variables"** tab
3. Copy `DATABASE_URL` (starts with `postgresql://...`)

---

## 6. Environment Variables

### Step 1: Generate Secret Key

```powershell
# Generate a secure secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output (something like: `django-insecure-x7j#k2l...`)

### Step 2: Add Variables in Railway

1. Click your Django service
2. Go to **"Variables"** tab
3. Click **"+ New Variable"**

**Required Variables:**

| Variable Name | Value | Notes |
|---------------|-------|-------|
| `SECRET_KEY` | (generated above) | Django secret key |
| `DEBUG` | `False` | Production mode |
| `DJANGO_SETTINGS_MODULE` | `school_saas.production_settings` | Use production settings |
| `FRONTEND_URL` | `https://smartapp.vercel.app` | Your Vercel URL |
| `PORT` | `8000` | Default port |
| `RAILWAY_ENVIRONMENT` | `production` | Detect Railway |

**DATABASE_URL** is automatically provided by Railway's PostgreSQL service.

### Step 3: Add CORS Origins

Add as single variable with comma-separated values:

| Variable Name | Value |
|---------------|-------|
| `CORS_ALLOWED_ORIGINS` | `https://smartapp.vercel.app,https://smart-saas-project.vercel.app` |

---

## 7. Run Migrations & Create Admin

### Step 1: Open Railway Shell

1. Click your Django service
2. Click **"..."** menu (top right)
3. Select **"Open Terminal"** or **"Run Command"**

### Step 2: Run Migrations

```bash
# In Railway terminal
python manage.py migrate

# Create static files
python manage.py collectstatic --noinput

# Create superuser
python manage.py createsuperuser
```

**Follow prompts:**
- Username: `admin`
- Email: `your-email@example.com`
- Password: (choose a strong password)
- Password (again): (repeat)

### Alternative: Run via Railway CLI

**Install Railway CLI:**
```powershell
# Windows (PowerShell as Administrator)
iwr https://railway.app/install.ps1 | iex
```

**Run commands:**
```powershell
# Login
railway login

# Link to project
railway link

# Run migrations
railway run python manage.py migrate

# Create superuser
railway run python manage.py createsuperuser

# Collect static files
railway run python manage.py collectstatic --noinput
```

---

## 8. Connect Frontend to Backend

### Step 1: Get Railway URL

1. Railway Dashboard → Your Django service
2. Go to **"Settings"** → **"Domains"**
3. Click **"Generate Domain"**
4. Copy the URL (e.g., `https://smartapp-production.up.railway.app`)

### Step 2: Update Vercel Environment Variables

1. Go to: https://vercel.com/dashboard
2. Select your frontend project
3. Go to: **Settings** → **Environment Variables**

**Update/Add:**

| Variable Name | Value |
|---------------|-------|
| `NEXT_PUBLIC_API_URL` | `https://smartapp-production.up.railway.app` |
| `NEXT_PUBLIC_WS_URL` | `wss://smartapp-production.up.railway.app` |

4. Click **"Save"**
5. **Deployments** → Click **"..."** → **"Redeploy"**

### Step 3: Update Django CORS Settings

In Railway, update `CORS_ALLOWED_ORIGINS` variable to include your actual Vercel URL:

```
https://smartapp.vercel.app,https://smart-saas-project-abc123.vercel.app
```

### Step 4: Test Connection

1. Open your Vercel app: `https://smartapp.vercel.app`
2. Try to make an API call
3. Check browser console for errors
4. Verify in Railway logs: Service → **"Deployments"** → View logs

---

## 9. Troubleshooting

### ❌ Build Failed: "ModuleNotFoundError"

**Solution: Update requirements.txt**

```powershell
cd backend
pip freeze > requirements.txt

# Commit and push
git add requirements.txt
git commit -m "Update requirements"
git push
```

Railway will auto-redeploy.

---

### ❌ "DisallowedHost at /"

**Error message:**
```
Invalid HTTP_HOST header: 'your-app.up.railway.app'
```

**Solution: Check ALLOWED_HOSTS**

In `backend/school_saas/production_settings.py`:
```python
ALLOWED_HOSTS = [
    '.railway.app',
    '.vercel.app',
    'smartapp-production.up.railway.app',  # Add your specific domain
]
```

Commit and push to redeploy.

---

### ❌ "Database connection failed"

**Check:**
1. PostgreSQL service is running
2. `DATABASE_URL` exists in variables
3. `psycopg2-binary` in requirements.txt

**Test connection:**
```bash
# Railway terminal
python manage.py dbshell
```

If successful, you'll see PostgreSQL prompt.

---

### ❌ Static Files Not Loading

**Solution: Collect static files**

```bash
# Railway terminal
python manage.py collectstatic --noinput
```

**Verify WhiteNoise:**
- Check `MIDDLEWARE` includes `whitenoise.middleware.WhiteNoiseMiddleware`
- Check `STATICFILES_STORAGE` is set

---

### ❌ CORS Errors from Frontend

**Error in browser console:**
```
Access to fetch blocked by CORS policy
```

**Solution: Update CORS origins**

Railway Variables:
```
CORS_ALLOWED_ORIGINS=https://smartapp.vercel.app,https://your-preview.vercel.app
```

Or in `production_settings.py`:
```python
CORS_ALLOW_ALL_ORIGINS = True  # Only for testing! Remove in production
```

---

### ❌ 502 Bad Gateway

**Causes:**
1. App crashed during startup
2. Gunicorn not starting
3. Port binding issue

**Solution: Check logs**
1. Railway → Your service → **Deployments**
2. Click latest deployment
3. View logs for errors

**Common fix:**
Verify `Procfile`:
```
web: gunicorn school_saas.wsgi --bind 0.0.0.0:$PORT
```

---

## ✅ Deployment Checklist

### Pre-Deployment:
- [ ] Production settings file created
- [ ] requirements.txt updated with production packages
- [ ] Procfile created
- [ ] runtime.txt created
- [ ] WSGI updated for production
- [ ] .env.example documented
- [ ] Code committed and pushed to GitHub

### Railway Setup:
- [ ] Railway account created
- [ ] Project created from GitHub repo
- [ ] PostgreSQL database added
- [ ] Environment variables configured
- [ ] Domain generated
- [ ] Deployment successful

### Post-Deployment:
- [ ] Migrations ran successfully
- [ ] Superuser created
- [ ] Static files collected
- [ ] Django admin accessible (`/admin`)
- [ ] API endpoints responding
- [ ] CORS configured for frontend
- [ ] Frontend connected to backend

---

## 🎯 Post-Deployment Tasks

### 1. Verify Django Admin

Open: `https://your-app.up.railway.app/admin`

**Should see:**
- Django admin login page
- Static files loading (CSS/JS)
- Can login with superuser credentials

---

### 2. Test API Endpoints

```powershell
# Test health check (if you have one)
curl https://your-app.up.railway.app/api/health/

# Test admin API
curl https://your-app.up.railway.app/admin/

# Should return HTML or JSON response
```

---

### 3. Monitor Logs

**View real-time logs:**
1. Railway Dashboard → Your service
2. **Deployments** → Latest deployment
3. **View Logs**

**Look for:**
- ✅ `Booting worker with pid`
- ✅ `Listening at: http://0.0.0.0:PORT`
- ❌ Any errors or tracebacks

---

### 4. Setup Monitoring (Optional)

**Railway provides:**
- CPU usage
- Memory usage
- Network usage
- Deployment history

**External monitoring:**
- UptimeRobot (free): https://uptimerobot.com
- Pingdom (paid): https://www.pingdom.com
- New Relic (free tier): https://newrelic.com

---

## 🔄 Continuous Deployment

### Automatic Deployments

**Every push to main branch:**
1. Push code to GitHub
2. Railway detects changes
3. Builds new image
4. Runs migrations (if configured)
5. Deploys new version
6. Zero downtime deployment

**Manual deployment:**
```powershell
cd "C:\Users\DELL\Desktop\New folder"
git add .
git commit -m "Update feature"
git push

# Railway automatically deploys!
```

---

## 📊 Railway Plans & Pricing

**Trial Plan (First Month):**
- ✅ $5 free credit
- ✅ 500MB RAM
- ✅ 1GB storage
- ✅ PostgreSQL included

**Hobby Plan ($5/month after trial):**
- ✅ 8GB RAM
- ✅ 100GB storage
- ✅ Unlimited projects
- ✅ Custom domains

**Pro Plan ($20/month):**
- ✅ Team collaboration
- ✅ Priority support
- ✅ Higher resource limits

**Cost breakdown (typical):**
- Django service: ~$5/month
- PostgreSQL: Included
- Total: ~$5/month

---

## 🚀 Performance Optimization

### 1. Database Connection Pooling

Already configured in `production_settings.py`:
```python
DATABASES = {
    'default': dj_database_url.config(
        conn_max_age=600,  # Keep connections alive
    )
}
```

### 2. Static File Caching

WhiteNoise automatically:
- ✅ Compresses files
- ✅ Adds cache headers
- ✅ Serves from CDN

### 3. Enable Gzip

Already enabled in `Procfile`:
```
web: gunicorn school_saas.wsgi --bind 0.0.0.0:$PORT --workers 2
```

### 4. Add Redis (Optional)

For caching and Celery:
1. Railway → **"+ New"** → **Database** → **Redis**
2. `REDIS_URL` automatically added
3. Update `production_settings.py`:

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL'),
    }
}
```

---

## 🔗 Important URLs

| Resource | URL |
|----------|-----|
| **Railway Dashboard** | https://railway.app/dashboard |
| **Documentation** | https://docs.railway.app |
| **Status** | https://railway.app/status |
| **Community** | https://discord.gg/railway |
| **Pricing** | https://railway.app/pricing |

---

## 💡 Pro Tips

**Tip 1: Use Railway CLI**
- Faster than web interface
- Run migrations easily
- View logs in terminal

**Tip 2: Environment-Specific Settings**
- Development: SQLite, DEBUG=True
- Staging: PostgreSQL, DEBUG=True
- Production: PostgreSQL, DEBUG=False

**Tip 3: Backup Database**
```bash
# Railway terminal
pg_dump $DATABASE_URL > backup.sql
```

**Tip 4: View Environment Variables**
```bash
# Railway terminal
env | grep DATABASE_URL
env | grep SECRET_KEY
```

**Tip 5: Restart Service**
- Railway Dashboard → Service → **"..."** → **Restart**
- Or redeploy: Push empty commit

---

## 🎉 Success!

After following this guide:

✅ Your backend is **LIVE** at `https://your-app.up.railway.app`
✅ **PostgreSQL database** running in production
✅ **Django admin** accessible at `/admin`
✅ **API endpoints** ready for frontend
✅ **Automatic deployments** on every push
✅ **HTTPS enabled** by default
✅ **Connected to Vercel frontend**

**Next Steps:**
1. Test all API endpoints
2. Monitor logs for errors
3. Setup regular backups
4. Configure email service (SendGrid, Mailgun)
5. Add monitoring/alerts

---

**Deployment Date:** January 11, 2026
**Expected URL:** `https://smartapp-production.up.railway.app`
**Cost:** $5/month after free trial
**Setup Time:** 20-30 minutes
