# Smart Multi-Tenant SaaS - PowerShell Launcher
# Starts both Django and Next.js servers for mobile access

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Smart Multi-Tenant SaaS Launcher" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get computer's IP address
Write-Host "Finding your IP address..." -ForegroundColor Yellow
$ipAddress = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -like '*Wi-Fi*' -or $_.InterfaceAlias -like '*Ethernet*'} | Select-Object -First 1).IPAddress

if ($ipAddress) {
    Write-Host "✅ Your IP Address: " -NoNewline -ForegroundColor Green
    Write-Host $ipAddress -ForegroundColor White
    Write-Host ""
    Write-Host "📱 Access your app on mobile at:" -ForegroundColor Cyan
    Write-Host "   Frontend: http://$ipAddress:3000" -ForegroundColor White
    Write-Host "   Backend:  http://$ipAddress:8000/admin" -ForegroundColor White
} else {
    Write-Host "⚠️  Could not detect IP address automatically" -ForegroundColor Yellow
    Write-Host "   Run: ipconfig | findstr IPv4" -ForegroundColor White
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Start Django Backend
Write-Host "[1/2] Starting Django Backend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'C:\Users\DELL\Desktop\New folder\backend'; python manage.py runserver 0.0.0.0:8000"

# Wait 3 seconds
Start-Sleep -Seconds 3

# Start Next.js Frontend
Write-Host "[2/2] Starting Next.js Frontend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'C:\Users\DELL\Desktop\New folder\frontend'; `$env:HOST='0.0.0.0'; npm run dev"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Servers Starting..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Two new PowerShell windows have opened:" -ForegroundColor Green
Write-Host "   1. Django Backend (Port 8000)" -ForegroundColor White
Write-Host "   2. Next.js Frontend (Port 3000)" -ForegroundColor White
Write-Host ""
Write-Host "⏳ Wait for both to show 'ready' messages." -ForegroundColor Yellow
Write-Host ""
Write-Host "📱 Then access on your phone:" -ForegroundColor Cyan
if ($ipAddress) {
    Write-Host "   http://$ipAddress:3000" -ForegroundColor White
}
Write-Host ""
Write-Host "🔥 Pro Tip:" -ForegroundColor Magenta
Write-Host "   - Keep both terminal windows open" -ForegroundColor White
Write-Host "   - Phone must be on same Wi-Fi" -ForegroundColor White
Write-Host "   - Install as PWA: Chrome menu → 'Add to Home screen'" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to close this window..." -ForegroundColor Gray
Write-Host "(Leave the other 2 windows open!)" -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
