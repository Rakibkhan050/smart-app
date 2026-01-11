# ✅ Vercel Environment Variables Setup Checklist

Follow these exact steps to complete your deployment:

---

## 📋 Information You Need

Before starting, have these values ready:

### Railway Backend (Already Set Up)
```
Backend URL: https://smart-app-production.up.railway.app
API URL: https://smart-app-production.up.railway.app/api
Admin URL: https://smart-app-production.up.railway.app/admin
```

### Vercel Frontend (Find in Vercel Dashboard)
```
Frontend URL: https://smart-app-rakib-khan-git-main-bangladesh1233bd-8458s-projects.vercel.app
(or check your Vercel project dashboard - shown at top)
```

---

## 🔧 STEP-BY-STEP SETUP

### ✓ Step 1: Open Vercel Dashboard
```
URL: https://vercel.com/dashboard
```
- Login with your account
- Look for project: **smart-app-rakib-khan**
- Click on it

### ✓ Step 2: Go to Settings
- Click the **Settings** tab (top menu)
- Left sidebar should appear

### ✓ Step 3: Select Environment Variables
- Click **Environment Variables** in left sidebar
- You should see a text field and "Add New" button

### ✓ Step 4: Add First Variable (API URL)

**Click "Add New"**

Fill in:
```
Name: NEXT_PUBLIC_API_URL
Value: https://smart-app-production.up.railway.app/api
Scope: Production (dropdown)
```

Then click **"Save"** or **"Add"**

### ✓ Step 5: Add Second Variable (App URL)

**Click "Add New" again**

Fill in:
```
Name: NEXT_PUBLIC_APP_URL
Value: https://smart-app-rakib-khan-git-main-bangladesh1233bd-8458s-projects.vercel.app
Scope: Production (dropdown)
```

Then click **"Save"** or **"Add"**

### ✓ Step 6: Verify Variables Added
- You should see both variables listed
- Both should show "Production" scope
- Values should be exactly as above

### ✓ Step 7: Redeploy
- Click **Deployments** tab (top menu)
- Find your latest deployment
- Click the **⋮** (three dots) on the right
- Click **Redeploy**
- Wait for deployment to complete (2-3 minutes)
- Status should say **Ready** ✅

---

## 🧪 Step 8: Test Your App

After redeploy completes:

1. **Visit your Vercel URL:**
   ```
   https://smart-app-rakib-khan-git-main-bangladesh1233bd-8458s-projects.vercel.app
   ```

2. **You should see:**
   - ✅ Home page loads without errors
   - ✅ No "localhost:8000" error
   - ✅ Navigation menu works
   - ✅ Can click "Dashboard" without errors

3. **Check debug page:**
   ```
   https://smart-app-rakib-khan-git-main-bangladesh1233bd-8458s-projects.vercel.app/debug
   ```
   - Should show environment variables
   - Should NOT say "NOT SET"
   - Should NOT say "Is Localhost: YES"

---

## ✨ Final Steps (After Tests Pass)

Once verified working:

1. **Try logging in:**
   - Visit `/auth/login`
   - Use test credentials if available
   - Or create new account

2. **Test Dashboard:**
   - Go to `/dashboard-3d`
   - Should load 3D visualization
   - Should show business metrics

3. **Test Other Features:**
   - Notifications
   - Payments
   - Tracking (if delivery data exists)

4. **Install on Mobile:**
   - Visit your Vercel URL on phone
   - Should see "Install" prompt
   - Can install as app (Android/iOS)

---

## 🆘 Troubleshooting

### Error: "Still seeing localhost:8000"
- ❌ Environment variables not set
- ✅ Go back to Step 3, verify both variables exist
- ✅ Check value is exactly: `https://smart-app-production.up.railway.app/api`

### Error: "Failed to load dashboard metrics"
- Visit `/debug` page
- Click "Test" button next to API endpoint
- If RED: Railway backend may be down
- Try: https://smart-app-production.up.railway.app/api/ in your browser

### Error: "No business/tenant found"
- This is NORMAL for new deployment
- Go to: https://smart-app-production.up.railway.app/admin
- Create a business/tenant
- Then refresh dashboard

---

## 📞 Quick Reference

**Your Project URLs:**
```
Vercel Frontend: https://smart-app-rakib-khan-git-main-bangladesh1233bd-8458s-projects.vercel.app
Railway Backend: https://smart-app-production.up.railway.app
```

**Environment Variables to Add:**
```
NEXT_PUBLIC_API_URL = https://smart-app-production.up.railway.app/api
NEXT_PUBLIC_APP_URL = https://smart-app-rakib-khan-git-main-bangladesh1233bd-8458s-projects.vercel.app
```

**Test URLs After Setup:**
```
Home: https://smart-app-rakib-khan-git-main-bangladesh1233bd-8458s-projects.vercel.app
Debug: https://smart-app-rakib-khan-git-main-bangladesh1233bd-8458s-projects.vercel.app/debug
Dashboard: https://smart-app-rakib-khan-git-main-bangladesh1233bd-8458s-projects.vercel.app/dashboard-3d
Admin: https://smart-app-production.up.railway.app/admin
```

---

## ✅ Mark Complete

Once all steps are done:
- [ ] Step 1: Opened Vercel Dashboard
- [ ] Step 2: Went to Settings
- [ ] Step 3: Clicked Environment Variables
- [ ] Step 4: Added NEXT_PUBLIC_API_URL
- [ ] Step 5: Added NEXT_PUBLIC_APP_URL
- [ ] Step 6: Verified both variables shown
- [ ] Step 7: Redeployed
- [ ] Step 8: Tested app loads without errors
- [ ] Verified at `/debug` page

**When all ✅ checked: Your app is live and ready!** 🚀
