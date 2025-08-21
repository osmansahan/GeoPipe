#!/bin/bash

# OSM Tile Generator - Emergency Reset Script for Linux/macOS
# This script performs a complete system cleanup and reset

echo "OSM Tile Generator - Emergency Reset"
echo "===================================="
echo "This script will stop all containers and clean up resources."
echo "WARNING: This will remove all generated tiles and database content!"
echo ""
read -p "Are you sure you want to proceed? (y/n): " confirm

if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
    echo "Operation cancelled."
    exit 0
fi

echo ""
echo "1. Stopping all containers..."
docker-compose down -v

echo ""
echo "2. Removing Docker volumes..."
docker volume prune -f

echo ""
echo "3. Cleaning tile cache..."
if [ -d "tiles" ]; then
    rm -rf tiles/*
    mkdir -p tiles
    echo "Tile cache cleaned."
else
    mkdir -p tiles
    echo "Tiles directory created."
fi

echo ""
echo "4. Checking for Docker services..."
docker-compose up -d

echo ""
echo "5. Verifying services..."
sleep 5
docker-compose ps

echo ""
echo "Reset complete. System is ready for a fresh start."
echo "You can now run the main application with: python osm_pipeline.py"
