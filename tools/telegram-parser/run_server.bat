@echo off
chcp 65001 >nul
title AION Server — Central Admin

echo ============================================
echo   AION INVITE MACHINE v2 — CENTRAL SERVER
echo   Node management / Campaigns / Analytics
echo ============================================
echo.
echo Admin panel: http://localhost:5000
echo Login:       /login  (default: admin123)
echo.
echo Start node clients on team laptops:
echo   python node_client.py --server http://YOUR_IP:5000
echo.
echo Press Ctrl+C to stop
echo.

python server.py
pause
