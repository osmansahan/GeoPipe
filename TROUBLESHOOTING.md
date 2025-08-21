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
# Restart containers
docker-compose down
docker-compose up -d

# Check logs
docker-compose logs osm_tools
docker-compose logs osm_postgres
```

#### Problem: "Port already in use" error
**Solution:**
```bash
# Check used ports
netstat -ano | findstr :5432
netstat -ano | findstr :8081

# Stop conflicting service or change port in docker-compose.yml
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
# Check that the PBF file is in the correct location
ls -la pbf/
# Check file permissions
chmod 644 pbf/*.pbf
```

#### Problem: No write permission to Tiles folder
**Solution:**
```bash
# Fix directory permissions
chmod 755 tiles/
sudo chown -R $USER:$USER tiles/
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
# Application log
tail -f osm_pipeline.log

# Docker container logs
docker-compose logs -f osm_tools
docker-compose logs -f osm_postgres

# System resource usage
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
# Clean Docker cache
docker system prune -a -f

# Clean tile cache
rm -rf tiles/*
```

## 📞 Technical Support

If the problem persists:
1. Check the `osm_pipeline.log` file
2. Save the output of `docker-compose logs`
3. Note your system information (OS, Docker version, RAM)
4. Specify the PBF file and configuration you are using

Share this information with the technical support team.