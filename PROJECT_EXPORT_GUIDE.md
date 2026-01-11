# 📦 PROJECT EXPORT & ZIP GUIDE - Smart Multi-Tenant SaaS

## 🎯 How to Download/Export Your Entire Project

This guide shows you how to create a complete backup ZIP file of your project including the database, code, and configurations.

---

## 📋 TABLE OF CONTENTS

1. [Quick Export (Recommended)](#1-quick-export-recommended)
2. [Selective Export Options](#2-selective-export-options)
3. [Include Database](#3-include-database)
4. [Exclude Large Files](#4-exclude-large-files)
5. [Automated Backup Script](#5-automated-backup-script)
6. [Verify Your Backup](#6-verify-your-backup)
7. [Restore from Backup](#7-restore-from-backup)

---

## 1. Quick Export (Recommended)

### Option A: Complete Project with Database

**PowerShell Command (Run from Desktop):**

```powershell
# Navigate to parent directory
cd "C:\Users\DELL\Desktop"

# Create zip with database
Compress-Archive -Path "New folder" -DestinationPath "SmartApp-Backup-$(Get-Date -Format 'yyyy-MM-dd').zip" -Force

# Success message
Write-Host "✅ Backup created: SmartApp-Backup-$(Get-Date -Format 'yyyy-MM-dd').zip" -ForegroundColor Green
```

**What this creates:**
- File: `SmartApp-Backup-2026-01-11.zip`
- Location: `C:\Users\DELL\Desktop\`
- Size: ~50-200 MB (depending on database size)
- **Includes:** All code, database, uploads, node_modules

---

### Option B: Exclude node_modules (Smaller File)

**PowerShell Command:**

```powershell
cd "C:\Users\DELL\Desktop"

# Get all items except node_modules
$items = Get-ChildItem "New folder" -Recurse | Where-Object {
    $_.FullName -notmatch 'node_modules' -and
    $_.FullName -notmatch '__pycache__' -and
    $_.FullName -notmatch '.next'
}

# Create zip
$items | Compress-Archive -DestinationPath "SmartApp-Backup-Lite-$(Get-Date -Format 'yyyy-MM-dd').zip" -Force

Write-Host "✅ Lite backup created (no node_modules)" -ForegroundColor Green
```

**What this creates:**
- File: `SmartApp-Backup-Lite-2026-01-11.zip`
- Size: ~5-20 MB (much smaller!)
- **Excludes:** node_modules, __pycache__, .next cache
- **Note:** Run `npm install` after extracting

---

## 2. Selective Export Options

### Export Backend Only (Django + Database)

```powershell
cd "C:\Users\DELL\Desktop"

Compress-Archive -Path "New folder\backend" -DestinationPath "Backend-Only-$(Get-Date -Format 'yyyy-MM-dd').zip" -Force

Write-Host "✅ Backend exported with database" -ForegroundColor Green
```

**Contents:**
- All Django apps
- `db.sqlite3` (database)
- Python requirements
- Models, admin, APIs
- Media files (receipts, uploads)

---

### Export Frontend Only (Next.js)

```powershell
cd "C:\Users\DELL\Desktop"

# Exclude node_modules and build cache
$frontendItems = Get-ChildItem "New folder\frontend" -Recurse | Where-Object {
    $_.FullName -notmatch 'node_modules' -and
    $_.FullName -notmatch '.next'
}

$frontendItems | Compress-Archive -DestinationPath "Frontend-Only-$(Get-Date -Format 'yyyy-MM-dd').zip" -Force

Write-Host "✅ Frontend exported (excluding node_modules)" -ForegroundColor Green
```

---

### Export Documentation Only

```powershell
cd "C:\Users\DELL\Desktop"

$docFiles = @(
    "New folder\README.md",
    "New folder\MOBILE_ACCESS_GUIDE.md",
    "New folder\COMPLETE_MODELS_DOCUMENTATION.md",
    "New folder\API_STRUCTURE_GUIDE.md",
    "New folder\SETUP_MIGRATION_GUIDE.md",
    "New folder\FINAL_DELIVERY_SUMMARY.md",
    "New folder\FILES_MANIFEST.md",
    "New folder\QUICK_START.md"
)

$docFiles | Compress-Archive -DestinationPath "Documentation-$(Get-Date -Format 'yyyy-MM-dd').zip" -Force

Write-Host "✅ Documentation exported" -ForegroundColor Green
```

---

## 3. Include Database

### Export Database Separately

**Option 1: Copy SQLite Database**

```powershell
# Copy database to Desktop
Copy-Item "C:\Users\DELL\Desktop\New folder\backend\db.sqlite3" -Destination "C:\Users\DELL\Desktop\db-backup-$(Get-Date -Format 'yyyy-MM-dd').sqlite3"

Write-Host "✅ Database backed up to Desktop" -ForegroundColor Green
```

**Option 2: Create Database Dump (JSON format)**

```powershell
cd "C:\Users\DELL\Desktop\New folder\backend"

# Export all data to JSON
python manage.py dumpdata --natural-foreign --natural-primary --indent 2 -o "database-backup-$(Get-Date -Format 'yyyy-MM-dd').json"

Write-Host "✅ Database exported to JSON" -ForegroundColor Green
```

**Option 3: Export Specific App Data**

```powershell
cd "C:\Users\DELL\Desktop\New folder\backend"

# Export only tenants data
python manage.py dumpdata tenants --indent 2 -o "tenants-backup.json"

# Export only users data
python manage.py dumpdata users --indent 2 -o "users-backup.json"

# Export only drivers data
python manage.py dumpdata drivers --indent 2 -o "drivers-backup.json"

Write-Host "✅ App-specific data exported" -ForegroundColor Green
```

---

## 4. Exclude Large Files

### Smart Backup (Production-Ready)

```powershell
cd "C:\Users\DELL\Desktop"

# Define exclusions
$excludePatterns = @(
    '*node_modules*',
    '*__pycache__*',
    '*.pyc',
    '*.pyo',
    '*.log',
    '*.tmp',
    '*.next*',
    '*.git*',
    '*.DS_Store',
    '*Thumbs.db'
)

# Get items excluding patterns
$items = Get-ChildItem "New folder" -Recurse | Where-Object {
    $item = $_
    $exclude = $false
    foreach ($pattern in $excludePatterns) {
        if ($item.FullName -like $pattern) {
            $exclude = $true
            break
        }
    }
    -not $exclude
}

# Create clean backup
$items | Compress-Archive -DestinationPath "SmartApp-Clean-$(Get-Date -Format 'yyyy-MM-dd').zip" -Force

Write-Host "✅ Clean backup created (production-ready)" -ForegroundColor Green
```

**What's excluded:**
- ❌ node_modules (can reinstall)
- ❌ Python cache files
- ❌ Next.js build cache
- ❌ Git history
- ❌ Log files
- ❌ Temporary files

**What's included:**
- ✅ All source code
- ✅ Database (db.sqlite3)
- ✅ Configuration files
- ✅ Documentation
- ✅ Media uploads
- ✅ Static files

---

## 5. Automated Backup Script

### Create Backup Script File

Save this as `backup-project.ps1`:

```powershell
# SmartApp Automated Backup Script
# Usage: .\backup-project.ps1

param(
    [string]$BackupType = "full",  # Options: full, lite, backend, frontend
    [string]$OutputPath = "C:\Users\DELL\Desktop\Backups"
)

# Create output directory if it doesn't exist
if (-not (Test-Path $OutputPath)) {
    New-Item -ItemType Directory -Path $OutputPath | Out-Null
    Write-Host "📁 Created backup directory: $OutputPath" -ForegroundColor Cyan
}

$timestamp = Get-Date -Format 'yyyy-MM-dd_HHmmss'
$projectPath = "C:\Users\DELL\Desktop\New folder"

Write-Host "🚀 Starting backup process..." -ForegroundColor Yellow
Write-Host "Type: $BackupType" -ForegroundColor Cyan
Write-Host "Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan

switch ($BackupType) {
    "full" {
        Write-Host "📦 Creating full backup (including node_modules)..." -ForegroundColor Yellow
        $zipName = "SmartApp-Full-$timestamp.zip"
        Compress-Archive -Path $projectPath -DestinationPath "$OutputPath\$zipName" -Force
    }
    
    "lite" {
        Write-Host "📦 Creating lite backup (excluding node_modules)..." -ForegroundColor Yellow
        $zipName = "SmartApp-Lite-$timestamp.zip"
        
        $items = Get-ChildItem $projectPath -Recurse | Where-Object {
            $_.FullName -notmatch 'node_modules' -and
            $_.FullName -notmatch '__pycache__' -and
            $_.FullName -notmatch '.next' -and
            $_.FullName -notmatch '.git'
        }
        
        $items | Compress-Archive -DestinationPath "$OutputPath\$zipName" -Force
    }
    
    "backend" {
        Write-Host "📦 Creating backend backup..." -ForegroundColor Yellow
        $zipName = "Backend-$timestamp.zip"
        Compress-Archive -Path "$projectPath\backend" -DestinationPath "$OutputPath\$zipName" -Force
    }
    
    "frontend" {
        Write-Host "📦 Creating frontend backup..." -ForegroundColor Yellow
        $zipName = "Frontend-$timestamp.zip"
        
        $items = Get-ChildItem "$projectPath\frontend" -Recurse | Where-Object {
            $_.FullName -notmatch 'node_modules' -and
            $_.FullName -notmatch '.next'
        }
        
        $items | Compress-Archive -DestinationPath "$OutputPath\$zipName" -Force
    }
}

# Get file size
$fileSize = (Get-Item "$OutputPath\$zipName").Length / 1MB
$fileSizeFormatted = "{0:N2}" -f $fileSize

Write-Host "" -ForegroundColor Green
Write-Host "✅ Backup completed successfully!" -ForegroundColor Green
Write-Host "📁 Location: $OutputPath\$zipName" -ForegroundColor Cyan
Write-Host "📊 Size: $fileSizeFormatted MB" -ForegroundColor Cyan
Write-Host "" -ForegroundColor Green

# Also backup database separately
Write-Host "💾 Creating separate database backup..." -ForegroundColor Yellow
Copy-Item "$projectPath\backend\db.sqlite3" -Destination "$OutputPath\database-$timestamp.sqlite3" -ErrorAction SilentlyContinue

if (Test-Path "$OutputPath\database-$timestamp.sqlite3") {
    $dbSize = (Get-Item "$OutputPath\database-$timestamp.sqlite3").Length / 1MB
    Write-Host "✅ Database backed up: $("{0:N2}" -f $dbSize) MB" -ForegroundColor Green
}

Write-Host ""
Write-Host "🎉 All backups complete!" -ForegroundColor Green
```

### Run the Backup Script

```powershell
# Full backup (including node_modules)
.\backup-project.ps1 -BackupType "full"

# Lite backup (excluding node_modules) - RECOMMENDED
.\backup-project.ps1 -BackupType "lite"

# Backend only
.\backup-project.ps1 -BackupType "backend"

# Frontend only
.\backup-project.ps1 -BackupType "frontend"

# Custom output location
.\backup-project.ps1 -BackupType "lite" -OutputPath "D:\MyBackups"
```

---

## 6. Verify Your Backup

### Check ZIP Contents

```powershell
# List contents of backup
$zipPath = "C:\Users\DELL\Desktop\SmartApp-Backup-2026-01-11.zip"

Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip = [System.IO.Compression.ZipFile]::OpenRead($zipPath)

Write-Host "📦 Backup contains $($zip.Entries.Count) files" -ForegroundColor Cyan
Write-Host ""
Write-Host "Top-level contents:" -ForegroundColor Yellow

$zip.Entries | Where-Object { $_.FullName -notmatch '/' -or $_.FullName.Split('/').Count -eq 2 } | Select-Object -First 20 | ForEach-Object {
    Write-Host "  📄 $($_.FullName)"
}

$zip.Dispose()
```

### Verify Database Included

```powershell
# Check if database is in backup
$zipPath = "C:\Users\DELL\Desktop\SmartApp-Backup-2026-01-11.zip"

Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip = [System.IO.Compression.ZipFile]::OpenRead($zipPath)

$dbFile = $zip.Entries | Where-Object { $_.Name -eq "db.sqlite3" }

if ($dbFile) {
    $dbSizeMB = $dbFile.Length / 1MB
    Write-Host "✅ Database found in backup!" -ForegroundColor Green
    Write-Host "   Size: $("{0:N2}" -f $dbSizeMB) MB" -ForegroundColor Cyan
} else {
    Write-Host "❌ Database NOT found in backup!" -ForegroundColor Red
}

$zip.Dispose()
```

---

## 7. Restore from Backup

### Extract Backup

**Method 1: Windows Explorer (GUI)**
1. Right-click the ZIP file
2. Select "Extract All..."
3. Choose destination folder
4. Click "Extract"

**Method 2: PowerShell Command**

```powershell
# Extract to specific location
$zipPath = "C:\Users\DELL\Desktop\SmartApp-Backup-2026-01-11.zip"
$extractPath = "C:\Users\DELL\Desktop\Restored Project"

Expand-Archive -Path $zipPath -DestinationPath $extractPath -Force

Write-Host "✅ Project restored to: $extractPath" -ForegroundColor Green
```

### Restore Steps

**1. Extract the ZIP**
```powershell
Expand-Archive -Path "SmartApp-Backup-2026-01-11.zip" -DestinationPath "Restored Project" -Force
```

**2. Install Dependencies**

**Backend:**
```powershell
cd "Restored Project\backend"
pip install -r requirements.txt
```

**Frontend:**
```powershell
cd "Restored Project\frontend"
npm install
```

**3. Verify Database**
```powershell
# Check database exists
Test-Path "Restored Project\backend\db.sqlite3"
# Should return: True
```

**4. Run Migrations (if needed)**
```powershell
cd "Restored Project\backend"
python manage.py migrate
```

**5. Start Servers**

**Terminal 1:**
```powershell
cd "Restored Project\backend"
python manage.py runserver
```

**Terminal 2:**
```powershell
cd "Restored Project\frontend"
npm run dev
```

**6. Test Access**
- Backend: http://localhost:8000/admin
- Frontend: http://localhost:3000

---

## 📊 Backup Size Reference

| Backup Type | Approximate Size | Contents |
|-------------|-----------------|----------|
| Full (with node_modules) | 150-300 MB | Everything |
| Lite (no node_modules) | 5-20 MB | Code + DB |
| Backend Only | 3-10 MB | Django + DB |
| Frontend Only | 2-10 MB | Next.js code |
| Database Only | 1-5 MB | SQLite file |
| Documentation | <1 MB | MD files |

---

## 🔄 Scheduled Backups

### Create Daily Backup Task

**PowerShell Script for Task Scheduler:**

Save as `daily-backup.ps1`:

```powershell
# Daily Backup Script
$backupRoot = "C:\Users\DELL\Desktop\Backups"
$projectPath = "C:\Users\DELL\Desktop\New folder"
$date = Get-Date -Format 'yyyy-MM-dd'

# Keep only last 7 days of backups
Get-ChildItem $backupRoot -Filter "SmartApp-*.zip" | 
    Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-7) } |
    Remove-Item -Force

# Create new backup
Compress-Archive -Path $projectPath -DestinationPath "$backupRoot\SmartApp-Auto-$date.zip" -Force

# Log
Add-Content "$backupRoot\backup-log.txt" "$(Get-Date): Backup created - SmartApp-Auto-$date.zip"
```

**Create Scheduled Task:**
```powershell
# Run this once to schedule daily backups
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-File `"C:\Users\DELL\Desktop\daily-backup.ps1`""
$trigger = New-ScheduledTaskTrigger -Daily -At 2AM
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERNAME" -LogonType S4U

Register-ScheduledTask -TaskName "SmartApp Daily Backup" -Action $action -Trigger $trigger -Principal $principal -Description "Automatic daily backup of SmartApp project"

Write-Host "✅ Scheduled daily backup at 2 AM" -ForegroundColor Green
```

---

## 📤 Share/Transfer Options

### 1. Cloud Upload (After Creating ZIP)

**Google Drive:**
- Drag ZIP to Google Drive folder
- Share link with others

**OneDrive:**
- Copy ZIP to OneDrive folder
- Right-click → Share

**Dropbox:**
- Copy ZIP to Dropbox folder
- Get shareable link

---

### 2. USB Transfer

```powershell
# Copy to USB drive (replace E: with your USB drive letter)
Copy-Item "SmartApp-Backup-2026-01-11.zip" -Destination "E:\" -Force

Write-Host "✅ Copied to USB drive" -ForegroundColor Green
```

---

### 3. Network Share

```powershell
# Copy to network location
$networkPath = "\\NetworkServer\Backups"
Copy-Item "SmartApp-Backup-2026-01-11.zip" -Destination $networkPath -Force
```

---

## 🎯 Quick Commands Summary

### Create Backups:

```powershell
# Full backup
cd "C:\Users\DELL\Desktop"
Compress-Archive -Path "New folder" -DestinationPath "SmartApp-Full-$(Get-Date -Format 'yyyy-MM-dd').zip" -Force

# Lite backup (recommended)
$items = Get-ChildItem "New folder" -Recurse | Where-Object {$_.FullName -notmatch 'node_modules|__pycache__|.next'}
$items | Compress-Archive -DestinationPath "SmartApp-Lite-$(Get-Date -Format 'yyyy-MM-dd').zip" -Force

# Database only
Copy-Item "New folder\backend\db.sqlite3" -Destination "database-$(Get-Date -Format 'yyyy-MM-dd').sqlite3"
```

### Restore:

```powershell
# Extract
Expand-Archive -Path "SmartApp-Backup-2026-01-11.zip" -DestinationPath "Restored" -Force

# Install dependencies
cd Restored\backend; pip install -r requirements.txt
cd ..\frontend; npm install
```

---

## ✅ Backup Checklist

Before calling a backup "complete", verify:

- [ ] ZIP file created successfully
- [ ] File size is reasonable (>5 MB for lite, >50 MB for full)
- [ ] Database (db.sqlite3) is included
- [ ] Can extract ZIP without errors
- [ ] All important files present
- [ ] Documentation included
- [ ] Media uploads included (if any)
- [ ] Configuration files included

---

## 🆘 Troubleshooting

### ❌ "Access Denied" Error

**Solution:**
```powershell
# Run PowerShell as Administrator
Start-Process powershell -Verb runAs
```

---

### ❌ ZIP File Too Large

**Solution: Use Lite Backup**
```powershell
# Excludes node_modules (biggest folder)
$items = Get-ChildItem "New folder" -Recurse | Where-Object {$_.FullName -notmatch 'node_modules'}
$items | Compress-Archive -DestinationPath "SmartApp-Lite.zip" -Force
```

---

### ❌ Compress-Archive Fails

**Alternative: Use 7-Zip**

```powershell
# If 7-Zip installed
& "C:\Program Files\7-Zip\7z.exe" a -tzip "SmartApp-Backup.zip" "New folder"
```

---

**🎉 Your project is now safely backed up and portable!**

You can now transfer this ZIP file to any computer, extract it, install dependencies, and run the entire application.
