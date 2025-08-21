# OSM Tile Generator - Troubleshooting Guide

This guide contains common problems and solutions you may encounter when using OSM Tile Generator.

## 🔧 Common Problems and Solutions

### 1. Docker Desktop Issues

#### Problem: "Docker Desktop is not running"
**Solution:**
```bash
# Start Docker Desktop on Windows
# Or from command line:
"C:\Program Files\Docker\Docker\Docker Desktop.exe"

# Start Docker service on Linux:
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group:
sudo usermod -aG docker $USER
# Then log out and log back in
```

#### Problem: "permission denied while trying to connect to the Docker daemon socket"
**Solution (Linux):**
```bash
sudo usermod -aG docker $USER
newgrp docker
# Or restart the system
```

### 2. Python Issues

#### Problem: "Python is not found"
**Solution:**
- Windows: Download Python from Microsoft Store or install from python.org and add to PATH
- Linux: `sudo apt install python3 python3-pip`
- macOS: `brew install python3`

#### Problem: Encoding errors
**Solution:** The project automatically uses UTF-8 encoding, but if the problem persists:
```bash
export PYTHONIOENCODING=utf-8
```

### 3. Container Issues

#### Problem: Containers not starting
**Solution:**
```bash
# Linux/macOS - Restart containers
docker-compose down
docker-compose up -d

# Windows PowerShell - Restart containers
docker-compose down
docker-compose up -d

# Linux/macOS - Check logs
docker-compose logs osm_tools
docker-compose logs osm_postgres

# Windows PowerShell - Check logs
docker-compose logs osm_tools
docker-compose logs osm_postgres
```

#### Problem: "Port already in use" error
**Solution:**
```bash
# Windows - Check used ports
netstat -ano | findstr :5432
netstat -ano | findstr :8081

# Linux/macOS - Check used ports
lsof -i :5432
lsof -i :8081

# Windows - Stop process by PID (replace PID with actual process ID)
taskkill /PID PID /F

# Linux/macOS - Stop process by PID (replace PID with actual process ID)
kill -9 PID

# Alternative: Change port in docker-compose.yml
```

### 4. Tile Generation Issues

#### Problem: Tiles are empty or incorrect
**Solution:**
- Check that the PBF file is correct
- Verify bounding box coordinates
- Restart the container: `docker-compose restart osm_tools`

#### Problem: "Out of memory" error
**Solution:**
- Allocate more RAM to Docker Desktop (Settings > Resources)
- Use a smaller bounding box
- Reduce zoom level

### 5. File and Directory Issues

#### Problem: PBF file not found
**Solution:**
```bash
# Linux/macOS - Check that the PBF file is in the correct location
ls -la pbf/
# Linux/macOS - Check file permissions
chmod 644 pbf/*.pbf

# Windows - Check that the PBF file is in the correct location
dir pbf\
# Windows - Check file permissions
icacls "pbf\*.pbf" /grant Everyone:R
```

#### Problem: No write permission to Tiles folder
**Solution:**
```bash
# Linux/macOS - Fix directory permissions
chmod 755 tiles/
sudo chown -R $USER:$USER tiles/

# Windows - Fix directory permissions
icacls "tiles" /grant Everyone:F
```

## 🚀 Performance Optimization

### Recommended System Requirements:
- **RAM**: At least 8GB (16GB for large cities)
- **Disk**: SSD preferred, at least 10GB free space
- **Processor**: Multi-core preferred

### Docker Settings:
```yaml
# Add resource limits in docker-compose.yml:
services:
  osm_tools:
    deploy:
      resources:
        limits:
          memory: 4G
        reservations:
          memory: 2G
```

## 📝 Log Inspection

### Check logs for debugging:
```bash
# Linux/macOS - Application log
tail -f osm_pipeline.log

# Windows - Application log
Get-Content -Path osm_pipeline.log -Wait
# or
type osm_pipeline.log

# Linux/macOS/Windows - Docker container logs
docker-compose logs -f osm_tools
docker-compose logs -f osm_postgres

# Linux/macOS/Windows - System resource usage
docker stats
```

## 🆘 Emergency Commands

### Complete system reset:
```bash
# Stop and remove all containers
docker-compose down -v

# Delete all Docker volumes (CAUTION: All data will be deleted!)
docker volume prune -f

# Restart
docker-compose up -d
```

### Clearing cache:
```bash
# Linux/macOS/Windows - Clean Docker cache
docker system prune -a -f

# Linux/macOS - Clean tile cache
rm -rf tiles/*

# Windows - Clean tile cache
rd /s /q tiles
mkdir tiles
# or
del /q /s tiles\*
```
