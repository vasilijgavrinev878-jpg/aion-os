@echo off
chcp 65001 >nul
title AION Invite Machine — Deploy

echo ============================================
echo   AION Invite Machine v2 — DEPLOY
echo ============================================
echo.
echo   SERVER (central admin):
echo     run_server.bat
echo.
echo   NODE CLIENT (on each laptop):
echo     python node.py --server http://SERVER_IP:5000
echo.
echo   DOCKER:
echo     docker compose up -d
echo.
echo ============================================
echo.

:menu
echo 1) Start central server
echo 2) Start node client (this laptop)
echo 3) Exit
echo.
set /p choice="Choice (1-3): "

if "%choice%"=="1" (
    python server.py
) else if "%choice%"=="2" (
    set /p srv="Server URL (default: http://localhost:5000): "
    if "%srv%"=="" set srv=http://localhost:5000
    python node.py --server %srv%
) else (
    exit /b
)

pause
