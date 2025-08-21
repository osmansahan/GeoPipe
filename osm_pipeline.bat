@echo off
SETLOCAL

:: Set the title of the console window
title OSM Tile Generator Pipeline - Professional Edition

:: Display a header
echo.
echo ===============================================
echo   OSM TILE GENERATOR PIPELINE
echo   Professional Edition v2.0
echo ===============================================
echo.

:: Check if Python is installed and in PATH
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not found. Please install Python and add it to your PATH.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Check if Docker is running
echo Checking Docker Desktop status...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ============================================
    echo   DOCKER DESKTOP ISSUE DETECTED
    echo ============================================
    echo.
    echo Docker Desktop is not running or not installed.
echo.
echo Solution steps:
echo 1. Try starting Docker Desktop
echo 2. Try restarting your computer
echo 3. If not installed, download Docker Desktop from:
echo    https://www.docker.com/products/docker-desktop
echo.
echo Please restart this program after Docker Desktop is running.
    echo.
    pause
    exit /b 1
)
echo Docker Desktop is running - OK!

:: Navigate to the script's directory
cd /d "%~dp0"

:: Run the Professional OSM Pipeline
python osm_pipeline.py

echo.
echo Press any key to continue . . .
pause >nul
ENDLOCAL
