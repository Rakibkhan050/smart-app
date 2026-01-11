# ⚡ Vercel Environment Variables - Quick Setup Guide

**Time Required: 5 minutes** ⏱️

---

## ✅ What You Need (Copy These Values)

```
NEXT_PUBLIC_API_URL = https://smart-app-production.up.railway.app/api

NEXT_PUBLIC_APP_URL = https://smart-app-rakib-khan-git-main-banglades...vercel.app
```

> Note: Replace the Vercel URL with your actual Vercel domain from your project

---

## 🚀 Step-by-Step Setup

### Step 1: Go to Vercel Dashboard
1. Open: https://vercel.com/dashboard
2. Login with your account
3. Find your project: **smart-app** (or your project name)
4. Click to open the project

### Step 2: Go to Settings
1. Click **Settings** tab (top menu)
2. Click **Environment Variables** (left sidebar)

### Step 3: Add NEXT_PUBLIC_API_URL
1. Click **Add New** button
2. Fill in:
   - **Name:** `NEXT_PUBLIC_API_URL`
   - **Value:** `https://smart-app-production.up.railway.app/api`
   - **Environments:** Select "Production" ✓
3. Click **Save** button

### Step 4: Add NEXT_PUBLIC_APP_URL
1. Click **Add New** button again
2. Fill in:
   - **Name:** `NEXT_PUBLIC_APP_URL`
   - **Value:** Your Vercel URL (copy from Domains section)
     - Format: `https://your-vercel-domain.vercel.app`
   - **Environments:** Select "Production" ✓
3. Click **Save** button

### Step 5: Redeploy Your App
1. Go to **Deployments** tab
2. Find the latest deployment
3. Click the **...** (three dots) on the right
4. Select **Redeploy** (or **Promote to Production**)
5. Wait 30-60 seconds for build to complete
6. You'll see "✓ Ready" when done

### Step 6: Test Your App
1. Open your Vercel domain in browser
2. Check the **Debug** page (/debug)
3. Verify:
   - ✅ NEXT_PUBLIC_API_URL is showing correctly
   - ✅ NEXT_PUBLIC_APP_URL is showing correctly
   - ✅ No "localhost" warnings
   - ✅ API connection test passes

---

## 🔍 How to Find Your Vercel URL

### Method 1: From Vercel Dashboard
1. Go to your project on vercel.com
2. Look for **Domains** section
3. Your URL looks like: `smart-app-rakib-khan-git-main-banglades...vercel.app`

### Method 2: From GitHub Deployment
1. Go to your GitHub repo
2. Look for deployment URL in commits/logs
3. Or check Environment Deployments section

---

## ✅ Verification Checklist

After redeploy, verify:

- [ ] Environment variables show on `/debug` page
- [ ] No "localhost" warnings on `/debug`
- [ ] API test button on `/debug` shows green ✅
- [ ] Dashboard loads (or shows helpful error about missing tenant)
- [ ] No Firefox "can't connect to localhost:8000" errors
- [ ] Mobile app can be installed from home screen

---

## 🆘 Troubleshooting

### Issue: Still showing localhost:8000
**Solution:** 
- Clear browser cache (Ctrl+Shift+Del in Chrome)
- Hard refresh (Ctrl+Shift+R)
- Wait 60 seconds for Railway to apply changes
- Check `/debug` page to confirm env vars are loaded

### Issue: "No business/tenant found" error
**Solution:** This is normal! You need to create a business first:
1. Visit: https://smart-app-production.up.railway.app/admin
2. Create a Tenant (business)
3. Create admin user for that business
4. Then try accessing dashboard again

### Issue: API connection test fails
**Solution:**
- Verify Railway backend is running (check Railway dashboard)
- Check NEXT_PUBLIC_API_URL is exactly: `https://smart-app-production.up.railway.app/api`
- Copy-paste the URL to avoid typos
- Wait 2-3 minutes for Railway to fully start if just deployed

### Issue: Redeploy keeps failing
**Solution:**
- Check Vercel build logs (click deployment → View logs)
- Look for errors in console
- Environment variables should NOT affect build (they're client-side)
- Try manual redeploy in Vercel UI again

---

## 💡 Pro Tips

**Tip 1:** You can set Preview environment variables too for testing before production

**Tip 2:** Environment variables take effect after redeploy only

**Tip 3:** Public variables (`NEXT_PUBLIC_*`) are visible in browser (safe - URLs only)

**Tip 4:** Use the `/debug` page to diagnose any environment issues

**Tip 5:** Keep Railway backend URL the same across all apps

---

## 📊 After Setup: What's Next?

Once environment variables are set and app is working:

1. **Create Your First Business** (5 min)
   - Visit `/admin`
   - Create Tenant + Products + Zones

2. **Add Your First User** (2 min)
   - Create business admin
   - Set password
   - Login to test dashboard

3. **Test Features** (10 min)
   - Create order
   - Test payment (Stripe test mode)
   - Test delivery tracking
   - Track live location

4. **Install Mobile App** (1 min)
   - On iOS/Android
   - Click Install button on home screen
   - Test offline functionality

---

## 🎯 Success Indicators

✅ **You'll know it's working when:**
- Dashboard loads without "localhost" errors
- Debug page shows your Railway URL
- API connectivity test passes
- No Firefox "can't establish connection" errors

---

## ⏱️ Timeline

| Step | Time |
|------|------|
| Go to Vercel | 1 min |
| Add env variables | 2 min |
| Redeploy | 2 min |
| Test & verify | 1 min |
| **Total** | **~6 min** |

---

## 🆘 Need Help?

1. Check `/debug` page - shows detailed diagnostics
2. Check Vercel deployment logs - shows build errors
3. Check Railway logs - shows backend errors
4. Re-read SETUP_CHECKLIST.md for detailed troubleshooting

---

**Your app is ready! Just 5 minutes away from going live.** 🚀

**Questions?** Check GETTING_STARTED.md for complete documentation.
