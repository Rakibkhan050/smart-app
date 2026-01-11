# ⚡ Quick Fix: Configure Vercel Environment Variables

## Problem
Your Vercel frontend is trying to connect to `localhost:8000`, which doesn't exist when deployed.

## Solution
Set environment variables on Vercel pointing to your Railway backend.

## 📋 Step-by-Step

### 1. Go to Vercel Dashboard
Open: https://vercel.com/dashboard

### 2. Select Your Project
Click: **smart-app** (your project)

### 3. Open Settings
Click: **Settings** tab (top menu)

### 4. Add Environment Variables
Click: **Environment Variables** (left sidebar)

### 5. Add 2 Required Variables

**Variable 1: NEXT_PUBLIC_API_URL**
- Name: `NEXT_PUBLIC_API_URL`
- Value: `https://smart-app-production.up.railway.app/api`
- Scope: Production ✓
- Click: Add ✓

**Variable 2: NEXT_PUBLIC_APP_URL**
- Name: `NEXT_PUBLIC_APP_URL`
- Value: Find from Vercel URL (top-right of dashboard, e.g., `https://smart-app-XXXXXXXX.vercel.app`)
- Scope: Production ✓
- Click: Add ✓

### 6. Redeploy
- Go to: **Deployments** tab
- Click: ⋮ (three dots) on latest deployment
- Select: **Redeploy**
- Wait ⏳ for build to complete (2-3 minutes)

### 7. Test
Visit: Your Vercel URL (e.g., https://smart-app-XXXXXXXX.vercel.app)

## ✅ Verify It Works

If setup correctly, you should see:
- ✅ Home page loads (no localhost error)
- ✅ Dashboard shows metrics
- ✅ Can login and navigate

If still getting errors:
1. Visit `/debug` on your Vercel URL to check environment variables
2. Verify Railway backend is running: https://smart-app-production.up.railway.app/api/
3. Do a hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)

## 🎯 Your URLs

**Railway Backend:**
```
https://smart-app-production.up.railway.app
API: https://smart-app-production.up.railway.app/api
Admin: https://smart-app-production.up.railway.app/admin
```

**Vercel Frontend:**
```
https://smart-app-XXXXXXXX.vercel.app
Debug: https://smart-app-XXXXXXXX.vercel.app/debug
```

---

**Still having issues?** Check the debug page at `/debug` for diagnostic information.
