@echo off
chcp 65001 >nul
title AION — Обновление документации
cls
echo.
echo   ╔═══════════════════════════════════════════╗
echo   ║   AION — Обновление документации         ║
echo   ╚═══════════════════════════════════════════╝
echo.

cd /d "%~dp0"

python docs/generate.py

if %errorlevel% neq 0 (
    echo.
    echo   ❌ Ошибка! Проверь, что Python установлен.
    echo.
    pause
    exit /b 1
)

echo.
echo   🖥️  Открываю сайт...
echo.

start "" "docs/index.html"

timeout /t 5 /nobreak >nul
