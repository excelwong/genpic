@echo off
chcp 65001 >nul 2>&1
title GenPic - Run Every 10 Minutes

:: ============================================================
:: Find Python - try multiple locations
:: ============================================================
set PYTHON=

:: Method 1: python in PATH
where python >nul 2>&1
if %errorlevel% equ 0 set PYTHON=python

:: Method 2: py launcher
if "%PYTHON%"=="" (
    where py >nul 2>&1
    if %errorlevel% equ 0 set PYTHON=py
)

:: Method 3: known install path
if "%PYTHON%"=="" (
    if exist "C:\Python314\python.exe" set PYTHON=C:\Python314\python.exe
)

:: Method 4: user AppData install
if "%PYTHON%"=="" (
    for /d %%i in ("C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python3*") do (
        if exist "%%i\python.exe" set PYTHON=%%i\python.exe
    )
)

if "%PYTHON%"=="" (
    echo [ERROR] Python not found. Please install Python and add it to PATH.
    echo.
    pause
    exit /b 1
)

echo ========================================
echo   GenPic Scheduler
echo   Python: %PYTHON%
echo   Runs script.py every 10 minutes
echo   Press Ctrl+C to stop
echo ========================================
echo.

:loop
echo [%date% %time%] Runnin script.py...
"%PYTHON%" "C:\Cloud-Excel\list\genpic\script.py"
if errorlevel 1 (
    echo [%date% %time%] ERROR: script.py exited with code %errorlevel%
)
echo [%date% %time%] Done. Waiting 3 minutes...
echo.
timeout /t 180 /nobreak >nul
goto loop
