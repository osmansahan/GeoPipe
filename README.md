# GeoPipe: OpenStreetMap Tile Generator

<div align="center">

![Version](https://img.shields.io/badge/version-3.0-blue)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)
![Docker](https://img.shields.io/badge/docker-required-blue)

**Professional-grade Docker-based system for generating map tiles from OpenStreetMap data**

</div>

---

## 🎯 Overview

GeoPipe is a powerful and user-friendly tool that processes OpenStreetMap data in Protocolbuffer Binary Format (`.osm.pbf`) and generates standard map tiles in PNG format. These tiles can be used in web mapping applications, GIS systems, and any project requiring custom map tiles.

**Key Features:**
- 🐳 **Docker-based architecture** - Zero configuration hassles
- 🖥️ **Cross-platform support** - Works on Windows, Linux, and macOS
- 🎛️ **Interactive CLI** - User-friendly command-line interface
- ⚡ **High performance** - Optimized for speed and efficiency
- 🔧 **Flexible configuration** - Support for custom areas and zoom levels
- 📦 **Template system** - Quick setup for common regions

---

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Getting Started](#-getting-started)
- [Configuration](#-configuration)
- [Usage Guide](#-usage-guide)
- [Templates](#-templates)
- [Troubleshooting](#-troubleshooting)
- [Directory Structure](#-directory-structure)
- [Advanced Features](#-advanced-features)

---

## 🚀 Quick Start

**For experienced users - get up and running in 3 steps:**

```bash
# 1. Clone and enter directory
git clone https://github.com/osmansahan/GeoPipe.git
cd GeoPipe

# 2. Start services
docker-compose up -d

# 3. Run application
./osm_pipeline.bat    # Windows
python osm_pipeline.py # Linux/macOS
```

---

## 💾 Installation

### Prerequisites

| Requirement | Version | Installation |
|-------------|---------|--------------|
| **Git** | Latest | [Download Git](https://git-scm.com/downloads) |
| **Docker Desktop** | Latest | [Download Docker](https://www.docker.com/products/docker-desktop/) |
| **Python** | 3.6+ | [Download Python](https://www.python.org/downloads/) |

### Step-by-Step Installation

#### 1️⃣ Clone the Repository

```bash
git clone https://github.com/osmansahan/GeoPipe.git
cd GeoPipe
```

#### 2️⃣ Install Python Dependencies

```bash
# Windows
pip install -r requirements.txt

# Linux/macOS
pip3 install -r requirements.txt
```

#### 3️⃣ Configure Docker

Ensure Docker Desktop is running and allocate at least **4GB RAM** in Docker settings:
- Windows/macOS: Docker Desktop → Settings → Resources → Memory
- Linux: Docker should use available system memory

#### 4️⃣ Download Map Data

Visit [Geofabrik Downloads](https://download.geofabrik.de/) and download the `.osm.pbf` file for your region:

```bash
# Example: Download Cyprus data
wget https://download.geofabrik.de/europe/cyprus-latest.osm.pbf
mv cyprus-latest.osm.pbf pbf/
```

#### 5️⃣ Start Services

```bash
docker-compose up -d
```

Verify all services are running:
```bash
docker-compose ps
```

You should see all services with status `Up`:
- `osm_postgres` (Database)
- `osm_nginx` (Web server)  
- `osm_tools` (Tile generator)

---

## 🏁 Getting Started

### Launch the Application

**Windows:**
```cmd
osm_pipeline.bat
```

**Linux/macOS:**
```bash
python osm_pipeline.py
```

### Main Menu

```
===== GeoPipe: OSM Tile Generator =====

1. 📁 Use existing configuration
2. ➕ Create new project
3. 🚪 Exit

Enter your choice [1-3]:
```

### Your First Project

**Option 1: Use existing configuration (Recommended for beginners)**
- Select a pre-configured project like `cyprus.json`
- The system will automatically start generating tiles

**Option 2: Create new project**
- Follow the interactive setup wizard
- Recommended settings for testing:
  - Zoom levels: 8-12
  - Render mode: `bbox` (for small areas)

---

## ⚙️ Configuration

### Project Configuration Files

Configuration files are stored in the `config/` directory as JSON files:

```json
{
  "project_name": "cyprus",
  "description": "Cyprus Island Map Tiles",
  "pbf_file": "cyprus-latest.osm.pbf",
  "render_mode": "full",
  "min_zoom": 8,
  "max_zoom": 14
}
```

### Configuration Options

| Parameter | Description | Options |
|-----------|-------------|---------|
| `project_name` | Unique project identifier | Any alphanumeric string |
| `description` | Project description | Any text |
| `pbf_file` | Source data file | File in `pbf/` directory |
| `render_mode` | Rendering scope | `full` or `bbox` |
| `min_zoom` | Minimum zoom level | 0-18 (0 = world view) |
| `max_zoom` | Maximum zoom level | 0-18 (18 = street level) |

### Bounding Box Configuration

For custom areas, use `bbox` mode:

```json
{
  "project_name": "london_center",
  "description": "London City Center",
  "pbf_file": "england-latest.osm.pbf",
  "render_mode": "bbox",
  "bbox": {
    "min_lat": 51.45,
    "max_lat": 51.55,
    "min_lon": -0.2,
    "max_lon": 0.1
  },
  "min_zoom": 10,
  "max_zoom": 16
}
```

**💡 Tip:** Use [bboxfinder.com](http://bboxfinder.com/) to find coordinates for your area.

---

## 📖 Usage Guide

### Interactive CLI Features

The application provides real-time feedback during operation:

- **Progress Indicators:** Shows completion percentage and ETA
- **Memory Monitoring:** Displays resource usage
- **Error Handling:** Clear error messages with solutions
- **Log Output:** Detailed logging for troubleshooting

### CLI Commands During Operation

| Key Combination | Action |
|-----------------|--------|
| `Ctrl+C` | Gracefully stop current operation |
| `Enter` | Continue after pause |
| `q` | Quick exit (during non-critical operations) |

### Understanding Output

```
🗺️  Generating tiles for project: cyprus
📊 Zoom levels: 8-14 (7 levels)
📍 Area: Full dataset
💾 Estimated tiles: 12,845
⏱️  Estimated time: 25 minutes

Processing zoom level 8... ████████████████████ 100% (256/256)
Processing zoom level 9... ████████████████████ 100% (1024/1024)
...
```

### Generated Output

Tiles are organized in standard XYZ format:

```
tiles/
└── cyprus/
    ├── 8/
    │   ├── 156/
    │   │   ├── 98.png
    │   │   └── 99.png
    │   └── 157/
    │       └── 98.png
    └── 9/
        └── ...
```

---

## 📝 Templates

### Using Template Generator

GeoPipe includes a template generator to quickly create configurations:

**Windows:**
```cmd
cd config
generate_templates.bat
```

**Linux/macOS:**
```bash
python src/generate_templates.py
```

### Template Features

The template generator will:

1. **Scan for PBF files** in the `pbf/` directory
2. **Generate configurations** for each found file
3. **Set reasonable defaults** for zoom levels and rendering
4. **Validate configurations** against the schema

### Customizing Templates

Edit generated templates to:
- Add bounding box constraints
- Adjust zoom level ranges  
- Change project descriptions
- Set specific rendering parameters

---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 🐳 Docker Issues

**Problem:** Docker services won't start
```bash
# Check Docker status
docker info

# Restart Docker services  
docker-compose down
docker-compose up -d

# Check logs
docker-compose logs
```

**Problem:** Port conflicts (5432, 8081 already in use)
```bash
# Windows - Find process using port
netstat -ano | findstr :5432

# Linux/macOS - Find process using port  
lsof -i :5432

# Stop conflicting process or change port in docker-compose.yml
```

#### 🗄️ Database Issues

**Problem:** Database import fails
```bash
# Check database logs
docker-compose logs osm_postgres

# Reset database
docker-compose down -v
docker-compose up -d
```

#### 🗺️ Tile Generation Issues

**Problem:** Empty or incorrect tiles
- Verify PBF file is not corrupted
- Check bounding box coordinates
- Ensure zoom levels are appropriate for area size

**Problem:** Out of memory errors
- Reduce zoom level range
- Use smaller bounding box
- Increase Docker memory allocation

### Emergency Reset

If you encounter persistent issues:

**Windows:**
```cmd
emergency_reset.bat
```

**Linux/macOS:**  
```bash
bash emergency_reset.sh
```

This will completely reset the system and clear all data.

### Getting Help

- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed solutions
- Review logs in `osm_pipeline.log`
- Check Docker container logs: `docker-compose logs`

---

## 📁 Directory Structure

```
GeoPipe/
├── 📁 config/                    # Project configurations
│   ├── 📄 config_schema.json     # Configuration validation schema
│   ├── 📄 cyprus.json            # Example: Cyprus configuration
│   ├── 📄 Kosova.json            # Example: Kosovo configuration
│   └── 🔧 generate_templates.bat # Template generator (Windows)
│
├── 📁 pbf/                       # OpenStreetMap data files
│   ├── 🗺️ cyprus-latest.osm.pbf   # Example: Cyprus map data
│   └── 🗺️ kosovo-latest.osm.pbf   # Example: Kosovo map data
│
├── 📁 src/                       # Source code
│   ├── 📁 config/                # Configuration management
│   ├── 📁 core/                  # Core processing engine
│   ├── 📁 ui/                    # User interface
│   └── 📁 utils/                 # Utility functions
│
├── 📁 tiles/                     # Generated tile output
│   └── 📁 {project_name}/        # Tiles organized by project
│       └── 📁 {z}/{x}/{y}.png    # Standard XYZ tile structure
│
├── 🐳 docker-compose.yml         # Docker service definitions
├── 🔧 nginx.conf                 # Web server configuration  
├── 🚀 osm_pipeline.py            # Main application (Linux/macOS)
├── 🚀 osm_pipeline.bat           # Main application (Windows)
├── 📋 requirements.txt           # Python dependencies
├── 🆘 emergency_reset.bat        # Reset script (Windows)
└── 🆘 emergency_reset.sh         # Reset script (Linux/macOS)
```

---

## 🚀 Advanced Features

### Performance Optimization

#### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **RAM** | 4GB | 8GB+ |
| **CPU** | 2 cores | 4+ cores |
| **Storage** | 10GB free | SSD with 50GB+ |
| **Docker Memory** | 2GB | 4GB+ |

#### Resource Allocation

Edit `docker-compose.yml` for better performance:

```yaml
services:
  osm_postgres:
    deploy:
      resources:
        limits:
          memory: 4G
        reservations:
          memory: 2G
```

### Custom Styling

Advanced users can modify the map appearance:

1. **Access the rendering container:**
   ```bash
   docker exec -it osm_tools bash
   ```

2. **Edit style configuration:**
   ```bash
   nano /home/renderer/src/openstreetmap-carto/style.xml
   ```

3. **Restart rendering service:**
   ```bash
   supervisorctl restart renderd
   ```

### Batch Processing

For multiple projects, create a batch script:

```bash
#!/bin/bash
for config in config/*.json; do
    echo "Processing $config"
    python osm_pipeline.py --config "$config" --batch
done
```

---

## 📊 Performance Expectations

### Tile Generation Speed

| Area Size | Zoom Levels | Estimated Time | Tile Count |
|-----------|-------------|----------------|------------|
| Small city | 8-14 | 15-30 minutes | ~10,000 |
| Large city | 8-16 | 1-3 hours | ~100,000 |
| Small country | 8-14 | 2-6 hours | ~500,000 |
| Large country | 8-16 | 8-24 hours | ~5,000,000 |

### Storage Requirements

| Zoom Level | Tiles per Level | Storage per Level |
|------------|-----------------|-------------------|
| 8 | ~1,000 | ~5MB |
| 10 | ~16,000 | ~80MB |
| 12 | ~250,000 | ~1.2GB |
| 14 | ~4,000,000 | ~20GB |
| 16 | ~64,000,000 | ~320GB |

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgements

- **[OpenStreetMap](https://www.openstreetmap.org/)** - Community-driven map data
- **[Geofabrik](https://download.geofabrik.de/)** - PBF data extracts
- **[Overv/openstreetmap-tile-server](https://github.com/Overv/openstreetmap-tile-server)** - Docker tile server
- **OSM Community** - Contributors worldwide

---

## 📚 Additional Resources

- **[Technical Documentation](PROJECT_DOCUMENTATION.md)** - Detailed system architecture
- **[Troubleshooting Guide](TROUBLESHOOTING.md)** - Comprehensive problem solving
- **[OpenStreetMap Wiki](https://wiki.openstreetmap.org/)** - OSM documentation
- **[Tile Server Guide](https://switch2osm.org/)** - Additional tile server resources

---

<div align="center">

**Made with ❤️ for the OpenStreetMap community**

[⭐ Star this project](https://github.com/osmansahan/GeoPipe) | [🐛 Report Issues](https://github.com/osmansahan/GeoPipe/issues) | [🤝 Contribute](https://github.com/osmansahan/GeoPipe/pulls)

</div>