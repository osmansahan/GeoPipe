@echo off
SETLOCAL

title OSM Tile Generator - Emergency Reset

echo.
echo ================================================
echo   OSM TILE GENERATOR - EMERGENCY RESET
echo ================================================
echo.
echo This script resets all Docker services and
echo brings the system to a clean state.
echo.
echo WARNING: This operation will:
echo - Stop all running containers
echo - Delete Docker volumes (including database)
echo - Clean Docker networks
echo - Clear Docker cache
echo.

set /p "confirm=Are you sure you want to continue? (yes/no): "

if /i "%confirm%" NEQ "yes" (
    echo Operation cancelled.
    pause
    exit /b 0
)

echo.
echo ===========================================
echo   STARTING EMERGENCY CLEANUP...
echo ===========================================

cd /d "%~dp0"

echo.
echo 1. Stopping containers...
docker-compose down --remove-orphans --volumes
if %errorlevel% neq 0 (
    echo Error occurred while stopping containers.
)

echo.
echo 2. Cleaning unused containers...
docker container prune -f
if %errorlevel% neq 0 (
    echo Error occurred during container cleanup.
)

echo.
echo 3. Cleaning unused networks...
docker network prune -f
if %errorlevel% neq 0 (
    echo Error occurred during network cleanup.
)

echo.
echo 4. Cleaning Docker cache...
docker system prune -f
if %errorlevel% neq 0 (
    echo Error occurred during cache cleanup.
)

echo.
echo 5. Checking volumes...
docker volume ls

echo.
echo ===========================================
echo   EMERGENCY CLEANUP COMPLETED
echo ===========================================
echo.
echo System cleaned. You can run the main application again:
echo - osm_pipeline.bat (Windows)
echo - python osm_pipeline.py (Cross-platform)
echo.
echo Since all data was deleted:
echo - Your PBF files were preserved (in pbf/ folder)
echo - Your config files were preserved (in config/ folder)
echo - Generated tiles were preserved (in tiles/ folder)
echo - Only Docker database and cache were cleaned
echo.

pause
ENDLOCAL
