# 🚀 Vercel Environment Setup Guide

Your Smart App frontend is deployed on Vercel, but it needs to connect to your Railway backend. Follow these steps:

## ⚙️ Set Environment Variables on Vercel

### Step 1: Go to Vercel Project Settings
1. Visit https://vercel.com/dashboard
2. Click on your project: **smart-app**
3. Go to **Settings** tab
4. Click **Environment Variables** (left sidebar)

### Step 2: Add These Environment Variables

Add **3 environment variables** (all Production):

| Variable | Value | Scope |
|----------|-------|-------|
| `NEXT_PUBLIC_API_URL` | `https://smart-app-production.up.railway.app/api` | Production |
| `NEXT_PUBLIC_APP_URL` | `https://smart-app-XXXXXXXX.vercel.app` | Production |
| `API_KEY` | *(leave empty if not used)* | Production |

**How to add:**
1. Click **"Add New"**
2. Enter variable name (e.g., `NEXT_PUBLIC_API_URL`)
3. Enter the value from above
4. Select **Production** from "Environment" dropdown
5. Click **Save**
6. Repeat for all 3 variables

### Step 3: Redeploy

After adding environment variables:

1. Go to **Deployments** tab
2. Click the **⋮** (three dots) on the latest deployment
3. Click **Redeploy**
4. Wait for build to complete ✅

### Step 4: Verify

Once redeployed:
1. Visit your Vercel URL: https://smart-app-XXXXXXXX.vercel.app
2. You should see the home page (no localhost errors)
3. Try accessing Dashboard - it should work!

## 🔗 Your URLs

Find these in:

**Railway Backend:**
- URL: https://smart-app-production.up.railway.app
- API Endpoint: https://smart-app-production.up.railway.app/api
- Admin: https://smart-app-production.up.railway.app/admin

**Vercel Frontend:**
- Go to https://vercel.com/dashboard
- Click **smart-app** project
- URL shown at top-right (e.g., https://smart-app-XXXXXXXX.vercel.app)

## ✅ Expected Results

✓ **Before**: "Firefox can't establish a connection to localhost:8000"
✓ **After**: Dashboard loads with 3D visualization and metrics

## 🆘 Still Getting Errors?

### Error: "No business/tenant found"
- Go to `/admin` (e.g., https://smart-app-production.up.railway.app/admin)
- Create a business/tenant with your details
- Refresh the dashboard

### Error: "Failed to load dashboard metrics"
1. Check environment variables are set
2. Verify Railway backend is running: https://smart-app-production.up.railway.app/api/
3. Try hard refresh: `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)

### Check Current Environment
Visit: `https://smart-app-XXXXXXXX.vercel.app/debug` (shows env variables)

---

**Need Help?**
- Check Vercel Build Logs: Settings → Build & Deployment → Build Logs
- Check Railway Logs: Dashboard → smart-app-backend → Logs
- Verify internet connection and that APIs are accessible
