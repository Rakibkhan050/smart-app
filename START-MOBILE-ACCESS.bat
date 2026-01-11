@echo off
REM Smart Multi-Tenant SaaS - Start Servers for Mobile Access
REM This script starts both Django and Next.js servers for network access

echo ========================================
echo  Smart Multi-Tenant SaaS Launcher
echo ========================================
echo.
echo Starting servers for mobile access...
echo.

REM Get computer's IP address
echo Your IP Address:
ipconfig | findstr /i "IPv4"
echo.
echo Access your app on mobile at:
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4"') do (
    set IP=%%a
    set IP=!IP: =!
)
echo Frontend: http://%IP:~1%:3000
echo Backend:  http://%IP:~1%:8000/admin
echo.
echo ========================================
echo.

REM Start Django backend in new window
echo [1/2] Starting Django Backend...
start "Django Backend - Port 8000" cmd /k "cd /d C:\Users\DELL\Desktop\New folder\backend && python manage.py runserver 0.0.0.0:8000"

REM Wait 3 seconds
timeout /t 3 /nobreak > nul

REM Start Next.js frontend in new window
echo [2/2] Starting Next.js Frontend...
start "Next.js Frontend - Port 3000" cmd /k "cd /d C:\Users\DELL\Desktop\New folder\frontend && set HOST=0.0.0.0 && npm run dev"

echo.
echo ========================================
echo  Servers Starting...
echo ========================================
echo.
echo Two new terminal windows have opened:
echo   1. Django Backend (Port 8000)
echo   2. Next.js Frontend (Port 3000)
echo.
echo Wait for both to show "ready" messages.
echo.
echo Then access on your phone:
echo   http://%IP:~1%:3000
echo.
echo Press any key to close this window...
echo (Leave the other 2 windows open!)
pause > nul
