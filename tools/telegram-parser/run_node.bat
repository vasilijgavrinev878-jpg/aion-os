@echo off
chcp 65001 >nul
title AION Node Client

echo ============================================
echo   AION INVITE MACHINE v2 — NODE CLIENT
echo   Runs Telegram accounts on THIS laptop
echo ============================================
echo.
set /p server="Server URL (default: http://localhost:5000): "
if "%server%"=="" set server=http://localhost:5000
echo.
echo 1. First run? Start with --setup to add accounts
echo 2. Then run without --setup for auto-mode
echo.

set /p mode="Run setup? (y/n): "
if /i "%mode%"=="y" (
    python node_client.py --server %server% --setup
) else (
    python node_client.py --server %server%
)

pause
