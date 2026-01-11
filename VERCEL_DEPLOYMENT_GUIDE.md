# 🚀 VERCEL DEPLOYMENT GUIDE - Frontend (Next.js)

## 🎯 Deploy Your Frontend to Get Public URL

This guide will help you deploy your Next.js frontend to Vercel and get a public URL like `smartapp.vercel.app` that anyone can access from anywhere.

---

## 📋 TABLE OF CONTENTS

1. [What You'll Get](#1-what-youll-get)
2. [Prerequisites](#2-prerequisites)
3. [Prepare Your Project](#3-prepare-your-project)
4. [Deploy to Vercel](#4-deploy-to-vercel)
5. [Configure Environment Variables](#5-configure-environment-variables)
6. [Custom Domain (Optional)](#6-custom-domain-optional)
7. [Troubleshooting](#7-troubleshooting)

---

## 1. What You'll Get

After deployment:
- ✅ **Public URL:** `https://smartapp.vercel.app` (or your custom name)
- ✅ **Automatic HTTPS:** Free SSL certificate
- ✅ **Global CDN:** Fast loading worldwide
- ✅ **Automatic Deploys:** Push to GitHub = Auto deploy
- ✅ **Zero Configuration:** Vercel auto-detects Next.js
- ✅ **Free Plan:** Perfect for this project
- ✅ **Mobile App Installation:** Works as PWA from any device

**Cost:** FREE (Vercel Hobby Plan)

---

## 2. Prerequisites

### Required Accounts:

1. **GitHub Account** (Free)
   - Sign up: https://github.com/signup
   - Used to store your code

2. **Vercel Account** (Free)
   - Sign up: https://vercel.com/signup
   - Use "Continue with GitHub" for easy setup

### Install Git (if not installed):

```powershell
# Check if Git is installed
git --version

# If not installed, download from:
# https://git-scm.com/download/win
```

---

## 3. Prepare Your Project

### Step 1: Initialize Git Repository

```powershell
cd "C:\Users\DELL\Desktop\New folder"

# Initialize Git
git init

# Create .gitignore
```

Create `.gitignore` file in project root:

```gitignore
# Dependencies
node_modules/
.pnp
.pnp.js

# Testing
/coverage

# Next.js
/.next/
/out/

# Production
/build

# Misc
.DS_Store
*.pem

# Debug
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Local env files
.env*.local
.env

# Vercel
.vercel

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
*.egg-info/
dist/
build/

# Database
*.sqlite3
db.sqlite3

# IDE
.vscode/
.idea/
*.swp
*.swo
```

### Step 2: Update Frontend Configuration

Update `frontend/next.config.js`:

```javascript
const { i18n } = require('./next-i18next.config');

module.exports = {
  reactStrictMode: true,
  i18n,
  
  // Production optimization
  compress: true,
  poweredByHeader: false,
  
  // PWA Configuration
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'X-DNS-Prefetch-Control',
            value: 'on'
          },
          {
            key: 'Strict-Transport-Security',
            value: 'max-age=63072000; includeSubDomains; preload'
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff'
          },
          {
            key: 'X-Frame-Options',
            value: 'SAMEORIGIN'
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block'
          }
        ]
      },
      {
        source: '/sw.js',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=0, must-revalidate'
          },
          {
            key: 'Service-Worker-Allowed',
            value: '/'
          }
        ]
      },
      {
        source: '/manifest.json',
        headers: [
          {
            key: 'Content-Type',
            value: 'application/manifest+json'
          },
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable'
          }
        ]
      }
    ];
  },

  // Image optimization
  images: {
    domains: ['localhost', 'smartapp.vercel.app'], // Update with your domain
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
  },

  // Environment variables (available in browser)
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://your-backend.railway.app',
  }
};
```

### Step 3: Create Vercel Configuration

Create `vercel.json` in frontend folder:

```json
{
  "version": 2,
  "name": "smart-saas-frontend",
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/next"
    }
  ],
  "routes": [
    {
      "src": "/sw.js",
      "headers": {
        "Cache-Control": "public, max-age=0, must-revalidate",
        "Service-Worker-Allowed": "/"
      },
      "dest": "/sw.js"
    },
    {
      "src": "/manifest.json",
      "headers": {
        "Content-Type": "application/manifest+json",
        "Cache-Control": "public, max-age=31536000, immutable"
      },
      "dest": "/manifest.json"
    },
    {
      "src": "/(.*)",
      "dest": "/$1"
    }
  ],
  "env": {
    "NEXT_PUBLIC_API_URL": "@api_url"
  },
  "regions": ["iad1"]
}
```

### Step 4: Commit to Git

```powershell
cd "C:\Users\DELL\Desktop\New folder"

# Add all files
git add .

# Commit
git commit -m "Initial commit - Smart SaaS Project"

# Check status
git status
```

### Step 5: Push to GitHub

**Create new repository on GitHub:**
1. Go to: https://github.com/new
2. Repository name: `smart-saas-project`
3. Description: "Smart Multi-Tenant SaaS Platform"
4. Choose "Private" (recommended) or "Public"
5. Click "Create repository"

**Push your code:**

```powershell
# Add GitHub remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/smart-saas-project.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**Enter your GitHub credentials when prompted.**

---

## 4. Deploy to Vercel

### Option 1: Deploy via Vercel Website (Recommended)

**Step 1: Import Project**
1. Go to: https://vercel.com/new
2. Click "Continue with GitHub"
3. Select your repository: `smart-saas-project`
4. Click "Import"

**Step 2: Configure Project**
- **Framework Preset:** Next.js (auto-detected)
- **Root Directory:** `frontend`
- **Build Command:** `npm run build`
- **Output Directory:** `.next`
- **Install Command:** `npm install`

**Step 3: Deploy**
- Click "Deploy"
- Wait 2-3 minutes for deployment
- You'll get a URL like: `https://smart-saas-project.vercel.app`

---

### Option 2: Deploy via Vercel CLI

```powershell
# Install Vercel CLI
npm install -g vercel

# Navigate to frontend
cd "C:\Users\DELL\Desktop\New folder\frontend"

# Login to Vercel
vercel login

# Deploy
vercel

# Follow prompts:
# Set up and deploy: Yes
# Which scope: Your account
# Link to existing project: No
# Project name: smart-saas-frontend
# Directory: ./ (current)
# Override settings: No

# Production deployment
vercel --prod
```

**Your app is now live!** 🎉

---

## 5. Configure Environment Variables

### Step 1: Add Environment Variables in Vercel

1. Go to: https://vercel.com/dashboard
2. Select your project: `smart-saas-frontend`
3. Go to: **Settings** → **Environment Variables**

### Required Variables:

| Variable Name | Value | Environment |
|---------------|-------|-------------|
| `NEXT_PUBLIC_API_URL` | `https://your-backend.railway.app` | Production |
| `NEXT_PUBLIC_APP_URL` | `https://smartapp.vercel.app` | Production |
| `NEXT_PUBLIC_WS_URL` | `wss://your-backend.railway.app` | Production |

**Add each variable:**
1. Name: `NEXT_PUBLIC_API_URL`
2. Value: Your backend URL (from Railway/Render)
3. Environment: Production, Preview, Development
4. Click "Add"

### Step 2: Redeploy

After adding variables:
1. Go to: **Deployments** tab
2. Click "..." on latest deployment
3. Click "Redeploy"

Or via CLI:
```powershell
cd frontend
vercel --prod
```

---

## 6. Custom Domain (Optional)

### Option 1: Use Vercel Subdomain (Free)

Your app is already live at:
- `https://your-project-name.vercel.app`

**Customize the subdomain:**
1. Vercel Dashboard → Your Project
2. **Settings** → **Domains**
3. Add domain: `smartapp.vercel.app`
4. Click "Add"

---

### Option 2: Use Your Own Domain (Paid)

**If you own a domain (e.g., smartapp.com):**

1. **Add Domain in Vercel:**
   - Settings → Domains
   - Add: `smartapp.com` and `www.smartapp.com`
   - Click "Add"

2. **Update DNS Records:**
   - Go to your domain registrar (GoDaddy, Namecheap, etc.)
   - Add these DNS records:

**For Root Domain (smartapp.com):**
```
Type: A
Name: @
Value: 76.76.21.21
TTL: 3600
```

**For WWW (www.smartapp.com):**
```
Type: CNAME
Name: www
Value: cname.vercel-dns.com
TTL: 3600
```

3. **Wait for DNS Propagation:**
   - Usually takes 5 minutes to 48 hours
   - Check status in Vercel dashboard

4. **Enable HTTPS:**
   - Vercel automatically provisions SSL certificate
   - Free via Let's Encrypt

---

### Option 3: Free Domain Options

**Get a free domain:**

1. **Freenom** (free .tk, .ml, .ga domains)
   - https://www.freenom.com

2. **InfinityFree** (free subdomain)
   - https://infinityfree.net

3. **DuckDNS** (free subdomain)
   - https://www.duckdns.org

**Then follow Option 2 steps above.**

---

## 7. Troubleshooting

### ❌ Build Failed: "Module not found"

**Solution: Check package.json**

```powershell
cd frontend

# Verify all dependencies
npm install

# Test build locally
npm run build

# If successful, commit and push
git add package.json package-lock.json
git commit -m "Fix dependencies"
git push
```

---

### ❌ Environment Variables Not Working

**Check:**
1. Variable names start with `NEXT_PUBLIC_` (for client-side)
2. Added to all environments (Production, Preview, Development)
3. Redeployed after adding variables

**Verify in code:**
```typescript
// In your component
console.log('API URL:', process.env.NEXT_PUBLIC_API_URL);
```

---

### ❌ API Calls Failing (CORS Errors)

**This means your backend needs configuration.**

Your Django backend must allow requests from Vercel:

In `backend/school_saas/settings.py`:
```python
CORS_ALLOWED_ORIGINS = [
    "https://smartapp.vercel.app",
    "https://your-project.vercel.app",
]

# Or for development (not recommended for production):
CORS_ALLOW_ALL_ORIGINS = True
```

**See:** [RAILWAY_DEPLOYMENT_GUIDE.md](./RAILWAY_DEPLOYMENT_GUIDE.md) for backend setup.

---

### ❌ Service Worker Not Working

**Check manifest.json start_url:**

```json
{
  "start_url": "/",
  "scope": "/"
}
```

**Verify service worker registration:**
- Open: `https://your-app.vercel.app`
- DevTools (F12) → Application → Service Workers
- Should show registered and activated

---

### ❌ Icons Not Loading

**Ensure icons exist:**
```powershell
cd frontend/public
ls icon-*.png
```

**Required sizes:**
- icon-72.png
- icon-96.png
- icon-128.png
- icon-144.png
- icon-152.png
- icon-192.png
- icon-384.png
- icon-512.png

**Generate icons:** See [PWA_DEPLOYMENT_GUIDE.md](./PWA_DEPLOYMENT_GUIDE.md) Section 4

---

## ✅ Deployment Checklist

### Pre-Deployment:
- [ ] Git repository initialized
- [ ] .gitignore created
- [ ] Dependencies installed (`npm install`)
- [ ] Build works locally (`npm run build`)
- [ ] Environment variables documented
- [ ] Icons generated (8 sizes)
- [ ] Code committed and pushed to GitHub

### Vercel Setup:
- [ ] Vercel account created
- [ ] GitHub connected to Vercel
- [ ] Project imported from GitHub
- [ ] Root directory set to `frontend`
- [ ] Deployment successful
- [ ] Environment variables added
- [ ] Project redeployed after variables

### Testing:
- [ ] Public URL accessible
- [ ] PWA manifest loads
- [ ] Service worker registers
- [ ] Can install as PWA on mobile
- [ ] API calls work (after backend deployed)
- [ ] Images load correctly
- [ ] Navigation works

---

## 🎯 Post-Deployment Tasks

### 1. Update Manifest URLs

Edit `frontend/public/manifest.json`:
```json
{
  "start_url": "https://smartapp.vercel.app/",
  "scope": "https://smartapp.vercel.app/"
}
```

### 2. Update API Calls

Replace hardcoded localhost URLs with environment variable:

```typescript
// Before
const API_URL = 'http://localhost:8000';

// After
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
```

### 3. Test PWA Installation

**On Android:**
1. Open: `https://smartapp.vercel.app`
2. Chrome should show "Install app" banner
3. Tap Install

**On iOS:**
1. Open in Safari
2. Share → Add to Home Screen
3. App installs

### 4. Enable Analytics (Optional)

Vercel provides free analytics:

1. Dashboard → Your Project → Analytics
2. Enable "Vercel Analytics"
3. See visitor stats, page views, performance

---

## 🚀 Automatic Deployments

### Every Git Push = Auto Deploy

**Workflow:**
```powershell
# Make changes to your code
cd "C:\Users\DELL\Desktop\New folder"

# Stage changes
git add .

# Commit
git commit -m "Add new feature"

# Push to GitHub
git push

# Vercel automatically:
# 1. Detects push
# 2. Builds project
# 3. Deploys to preview URL
# 4. If on main branch, deploys to production
```

**View deployments:**
- Vercel Dashboard → Deployments
- See all deployments, preview URLs, build logs

---

## 📊 Deployment Info

**What Vercel Provides:**

| Feature | Details |
|---------|---------|
| **URL** | `https://your-project.vercel.app` |
| **SSL** | Automatic HTTPS with free certificate |
| **CDN** | Global edge network (fast worldwide) |
| **Bandwidth** | 100GB/month (Hobby plan) |
| **Build Time** | Unlimited (fair use) |
| **Domains** | Unlimited custom domains |
| **Environments** | Production, Preview, Development |
| **Serverless Functions** | 100GB-hours/month |
| **Cost** | **FREE** for Hobby plan |

**Upgrade limits** (if needed):
- Pro Plan: $20/month - More bandwidth, team features

---

## 🔗 Important URLs

| Resource | URL |
|----------|-----|
| **Vercel Dashboard** | https://vercel.com/dashboard |
| **Documentation** | https://vercel.com/docs |
| **CLI Reference** | https://vercel.com/docs/cli |
| **Examples** | https://vercel.com/templates |
| **Status** | https://vercel-status.com |
| **Community** | https://github.com/vercel/vercel/discussions |

---

## 💡 Pro Tips

**Tip 1: Preview Deployments**
- Every branch gets a unique preview URL
- Test features before merging to main
- Share preview links with team

**Tip 2: Environment Variables per Environment**
- Development: Use localhost API
- Preview: Use staging API
- Production: Use production API

**Tip 3: Instant Rollback**
- Dashboard → Deployments
- Click previous deployment
- Click "Promote to Production"
- Instant rollback!

**Tip 4: Edge Functions**
- Add `/api` routes in Next.js
- Serverless functions at the edge
- Fast response times globally

**Tip 5: Vercel CLI for Speed**
```powershell
cd frontend
vercel dev  # Local development with serverless functions
vercel     # Deploy to preview
vercel --prod  # Deploy to production
```

---

## 🎉 Success!

After following this guide:

✅ Your frontend is **LIVE** at `https://smartapp.vercel.app`
✅ Anyone can access it from **any device, anywhere**
✅ **HTTPS enabled** (required for PWA)
✅ **PWA installable** on Android & iOS
✅ **Automatic deployments** on every push
✅ **FREE hosting** on Vercel

**Next Step:** Deploy your backend!
- See: [RAILWAY_DEPLOYMENT_GUIDE.md](./RAILWAY_DEPLOYMENT_GUIDE.md)
- Or: [RENDER_DEPLOYMENT_GUIDE.md](./RENDER_DEPLOYMENT_GUIDE.md)

---

**Deployment Date:** January 11, 2026
**Expected URL:** `https://smart-saas-project.vercel.app`
**Cost:** FREE (Vercel Hobby Plan)
**Setup Time:** 15-30 minutes
