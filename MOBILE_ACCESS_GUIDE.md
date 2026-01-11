# 📱 MOBILE ACCESS GUIDE - Smart Multi-Tenant SaaS Platform

## 🎯 Complete Guide to Access Your App on Mobile Devices

This guide will help you access your local development server from your Android/iOS phone and install it as a Progressive Web App (PWA).

---

## 📋 TABLE OF CONTENTS

1. [Find Your Computer's IP Address](#1-find-your-computers-ip-address)
2. [Configure Django for Network Access](#2-configure-django-for-network-access)
3. [Start Servers with Network Access](#3-start-servers-with-network-access)
4. [Access from Mobile Browser](#4-access-from-mobile-browser)
5. [Install as PWA on Android](#5-install-as-pwa-on-android)
6. [Install as PWA on iOS](#6-install-as-pwa-on-ios)
7. [Troubleshooting](#7-troubleshooting)

---

## 1. Find Your Computer's IP Address

### Windows (PowerShell):

**Method 1 - Quick Command:**
```powershell
ipconfig | findstr /i "IPv4"
```

**Method 2 - Full Details:**
```powershell
Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -like '*Wi-Fi*' -or $_.InterfaceAlias -like '*Ethernet*'} | Select-Object IPAddress, InterfaceAlias
```

**Method 3 - GUI Method:**
1. Press `Win + R`
2. Type `ncpa.cpl` and press Enter
3. Right-click your active network adapter (Wi-Fi or Ethernet)
4. Click "Status" → "Details"
5. Find "IPv4 Address"

### Expected Output:
```
IPv4 Address: 192.168.1.100
```
**⚠️ Important:** Your IP address will look like `192.168.x.x` or `10.0.x.x`. Note it down!

### Example IP Addresses:
- `192.168.1.100` (Most common for home networks)
- `192.168.0.50` (Some routers)
- `10.0.0.25` (Some corporate networks)
- `172.16.0.10` (Less common)

---

## 2. Configure Django for Network Access

### Step 1: Update Django Settings

Open `backend/school_saas/settings.py` and find the `ALLOWED_HOSTS` line:

**Before:**
```python
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')
```

**After (add your IP):**
```python
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '192.168.1.100',  # ← Replace with YOUR IP address
    '*',  # Allow all (for development only)
]
```

### Step 2: Add CORS Headers (if needed)

If you see CORS errors, add these to `settings.py`:

```python
# Add to INSTALLED_APPS
INSTALLED_APPS = [
    # ... existing apps
    'corsheaders',
]

# Add to MIDDLEWARE (at the top)
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Add this
    'django.middleware.security.SecurityMiddleware',
    # ... rest of middleware
]

# Add CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://192.168.1.100:3000",  # ← Replace with YOUR IP
]

CORS_ALLOW_CREDENTIALS = True
```

**Install CORS package:**
```powershell
cd backend
pip install django-cors-headers
```

### Step 3: Update Next.js Configuration

Your `frontend/next.config.js` is already configured! Just update the IP in the images section:

```javascript
images: {
  domains: ['localhost', '192.168.1.100'],  // ← Add YOUR IP here
}
```

---

## 3. Start Servers with Network Access

### Terminal 1 - Django Backend (PowerShell):
```powershell
cd backend
python manage.py runserver 0.0.0.0:8000
```

**✅ Success Message:**
```
Starting development server at http://0.0.0.0:8000/
Quit the server with CTRL-BREAK.
```

**What `0.0.0.0:8000` means:**
- Listens on ALL network interfaces
- Accessible from your computer (localhost:8000)
- Accessible from your phone (192.168.1.100:8000)

### Terminal 2 - Next.js Frontend (PowerShell):
```powershell
cd frontend
npm run dev -- -H 0.0.0.0
```

**✅ Success Message:**
```
ready - started server on 0.0.0.0:3000
```

**Alternative command:**
```powershell
$env:HOST="0.0.0.0"; npm run dev
```

---

## 4. Access from Mobile Browser

### Prerequisites:
✅ Your phone and computer must be on the **SAME Wi-Fi network**
✅ Firewall should allow connections (see troubleshooting)
✅ Both servers are running

### Step-by-Step Access:

1. **On Your Phone:**
   - Open Chrome (Android) or Safari (iOS)
   - Type in the address bar: `http://192.168.1.100:3000`
     - ⚠️ Replace `192.168.1.100` with YOUR actual IP address
   - Press Enter

2. **Expected Result:**
   - You should see your app's homepage
   - If you see a blank page, check the browser console
   - If connection fails, see troubleshooting section

3. **Test the Backend API:**
   - Open: `http://192.168.1.100:8000/admin`
   - You should see Django admin login

### URL Format Reference:
```
Frontend: http://YOUR_IP_ADDRESS:3000
Backend:  http://YOUR_IP_ADDRESS:8000
Admin:    http://YOUR_IP_ADDRESS:8000/admin
API:      http://YOUR_IP_ADDRESS:8000/api/
```

**Example URLs (replace with your IP):**
```
http://192.168.1.100:3000          ← Main app
http://192.168.1.100:3000/dashboard ← Dashboard
http://192.168.1.100:8000/admin    ← Django admin
http://192.168.1.100:8000/api/     ← API endpoints
```

---

## 5. Install as PWA on Android

### Method 1: Chrome (Recommended)

**Step 1: Access the App**
- Open Chrome browser on Android
- Navigate to: `http://192.168.1.100:3000`

**Step 2: Install Prompt**
- After a few seconds, you'll see an "Install" banner at the bottom
- Tap "Install" or "Add to Home Screen"

**Step 3: Manual Installation (if no prompt)**
1. Tap the **three dots** (⋮) in the top-right corner
2. Select **"Add to Home screen"** or **"Install app"**
3. Edit the app name if desired (default: "SmartApp")
4. Tap **"Add"** or **"Install"**

**Step 4: Verify Installation**
- Check your home screen for the "SmartApp" icon
- Tap the icon to launch as a standalone app
- Status bar will match app theme color (green)

### Method 2: Samsung Internet Browser

1. Open Samsung Internet
2. Navigate to your app
3. Tap the menu icon (three lines)
4. Select "Add page to" → "Home screen"
5. Confirm installation

### Features on Android PWA:
✅ Full-screen experience (no browser UI)
✅ Appears in app drawer and home screen
✅ Offline support with cached data
✅ Push notifications (when configured)
✅ Background sync
✅ Can share files/text to the app

---

## 6. Install as PWA on iOS

### Step 1: Open in Safari (REQUIRED)
- ⚠️ **Must use Safari** - Chrome/Firefox don't support iOS PWA installation
- Open Safari on iPhone/iPad
- Navigate to: `http://192.168.1.100:3000`

### Step 2: Add to Home Screen

1. Tap the **Share button** (square with arrow) at the bottom
2. Scroll down and tap **"Add to Home Screen"**
3. Edit the name if desired (default: "SmartApp")
4. Tap **"Add"** in the top-right corner

### Step 3: Verify Installation
- Check your home screen for the app icon
- Tap to launch
- App opens in full screen (no Safari UI)

### iOS PWA Features:
✅ Full-screen mode
✅ Home screen icon
✅ Splash screen on launch
✅ Offline caching
⚠️ Limited background features vs Android
⚠️ No push notifications (iOS limitation)

---

## 7. Troubleshooting

### ❌ Problem: "Site can't be reached" on mobile

**Solution 1: Check Firewall**

**Windows Firewall:**
```powershell
# Allow Python through firewall
New-NetFirewallRule -DisplayName "Django Dev Server" -Direction Inbound -Program "C:\Path\To\Python\python.exe" -Action Allow

# Or allow ports directly
New-NetFirewallRule -DisplayName "Django Port 8000" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "Next.js Port 3000" -Direction Inbound -LocalPort 3000 -Protocol TCP -Action Allow
```

**Quick Test (Temporary):**
```powershell
# Disable firewall temporarily to test
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled False

# Re-enable after testing!
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled True
```

**Solution 2: Verify Same Network**
- Phone Wi-Fi: Settings → Wi-Fi → Check network name
- Computer Wi-Fi: System Tray → Wi-Fi icon → Check network name
- **Must be identical!**

**Solution 3: Test Connection**

On your phone's browser, try:
1. `http://192.168.1.100:3000` (your app)
2. `http://192.168.1.1` (usually your router)
3. If router loads but app doesn't, it's a firewall issue

---

### ❌ Problem: PWA install banner doesn't appear

**Requirements for PWA install prompt:**
1. ✅ Must be served over HTTPS (or localhost)
2. ✅ Must have valid `manifest.json`
3. ✅ Must have service worker registered
4. ✅ Service worker must control the page
5. ✅ Must have valid icons (192px and 512px)
6. ✅ User must interact with page for 30 seconds

**Solution:**
- Wait 30 seconds after page loads
- Scroll or click something on the page
- Look for install banner at bottom (Android) or use Safari share menu (iOS)

**Force Check (Chrome DevTools on desktop):**
1. Open Chrome DevTools (F12)
2. Go to "Application" tab
3. Click "Manifest" - check for errors
4. Click "Service Workers" - verify registered

---

### ❌ Problem: Icons not showing

**Create placeholder icons quickly:**

You need these icon sizes in `frontend/public/`:
- icon-72.png (72×72)
- icon-96.png (96×96)
- icon-128.png (128×128)
- icon-144.png (144×144)
- icon-152.png (152×152)
- icon-192.png (192×192)
- icon-384.png (384×384)
- icon-512.png (512×512)

**Quick Solution:**
1. Find any logo/image
2. Use online tool: https://www.favicon-generator.org/
3. Upload image → Generate → Download all sizes
4. Place in `frontend/public/`

---

### ❌ Problem: CORS errors in browser console

**Error message:**
```
Access to fetch at 'http://192.168.1.100:8000/api/' from origin 
'http://192.168.1.100:3000' has been blocked by CORS policy
```

**Solution:**
See [Section 2: Configure Django for Network Access](#2-configure-django-for-network-access)

Install and configure `django-cors-headers`

---

### ❌ Problem: "Invalid Host header" error

**Error in Django logs:**
```
Invalid HTTP_HOST header: '192.168.1.100:8000'
```

**Solution:**
Update `ALLOWED_HOSTS` in `backend/school_saas/settings.py`:
```python
ALLOWED_HOSTS = ['*']  # Allow all for development
```

---

### ❌ Problem: Next.js won't start with -H flag

**Error:**
```
Unknown option: -H
```

**Solutions:**

**Option 1: Environment variable**
```powershell
$env:HOST="0.0.0.0"
npm run dev
```

**Option 2: Update package.json**
```json
{
  "scripts": {
    "dev": "next dev -H 0.0.0.0",
    "dev:local": "next dev"
  }
}
```

**Option 3: Create next.config.js server config**
Already done! Your config is ready.

---

## 📊 Connection Test Checklist

Use this checklist to verify everything works:

### On Your Computer:
- [ ] Django running on `0.0.0.0:8000`
- [ ] Next.js running on `0.0.0.0:3000`
- [ ] Firewall allows ports 3000 and 8000
- [ ] Know your IP address (e.g., 192.168.1.100)

### On Your Phone:
- [ ] Connected to same Wi-Fi as computer
- [ ] Can access `http://YOUR_IP:3000` in browser
- [ ] Can access `http://YOUR_IP:8000/admin`
- [ ] See app content (not error page)
- [ ] Can interact with app

### PWA Installation:
- [ ] Install banner appears (Android) OR
- [ ] "Add to Home Screen" available (iOS Safari)
- [ ] App icon appears on home screen
- [ ] App launches in standalone mode
- [ ] Offline page works (turn off Wi-Fi, try to navigate)

---

## 🚀 Quick Start Commands

**Copy-paste these commands (replace IP address):**

### Terminal 1 - Backend:
```powershell
cd "C:\Users\DELL\Desktop\New folder\backend"
python manage.py runserver 0.0.0.0:8000
```

### Terminal 2 - Frontend:
```powershell
cd "C:\Users\DELL\Desktop\New folder\frontend"
$env:HOST="0.0.0.0"
npm run dev
```

### On Phone Browser:
```
http://192.168.1.100:3000
```

---

## 🔐 Security Notes

⚠️ **For Development Only:**
- `0.0.0.0` and `ALLOWED_HOSTS = ['*']` are for LOCAL DEVELOPMENT
- **Never use in production!**
- For production, use proper domain names and HTTPS

⚠️ **Network Security:**
- Anyone on your Wi-Fi can access your app
- Use only on trusted networks
- Close servers when not testing

---

## 📱 Testing on Multiple Devices

You can test on multiple devices simultaneously:

1. **Phone 1 (Android):** `http://192.168.1.100:3000`
2. **Phone 2 (iOS):** `http://192.168.1.100:3000`
3. **Tablet:** `http://192.168.1.100:3000`
4. **Another Computer:** `http://192.168.1.100:3000`

All will connect to the same backend database!

---

## ✅ Success Indicators

**You've succeeded when:**
1. ✅ Phone browser loads app at `http://YOUR_IP:3000`
2. ✅ App is interactive (can click buttons, navigate)
3. ✅ PWA install banner appears
4. ✅ App installed on home screen
5. ✅ App opens in full-screen mode
6. ✅ Offline page shows when Wi-Fi disabled

---

## 🆘 Still Having Issues?

### Common Mistakes:
1. ❌ Using `localhost` instead of IP address on phone
2. ❌ Phone on cellular data instead of Wi-Fi
3. ❌ Different Wi-Fi networks (phone vs computer)
4. ❌ Firewall blocking connections
5. ❌ Typo in IP address
6. ❌ Servers not started with `0.0.0.0`

### Debug Commands:

**Check if server is listening:**
```powershell
netstat -an | findstr "3000"
netstat -an | findstr "8000"
```

Expected output:
```
TCP    0.0.0.0:3000    0.0.0.0:0    LISTENING
TCP    0.0.0.0:8000    0.0.0.0:0    LISTENING
```

**Test connection from computer:**
```powershell
# Test frontend
curl http://localhost:3000

# Test backend
curl http://localhost:8000
```

---

## 📖 Additional Resources

- [PWA Checklist](https://web.dev/pwa-checklist/)
- [Service Workers Guide](https://developers.google.com/web/fundamentals/primers/service-workers)
- [Web App Manifest](https://web.dev/add-manifest/)

---

**🎉 Congratulations! Your app is now mobile-ready!**

For production deployment (real domain, HTTPS, app stores), see the deployment guide.
