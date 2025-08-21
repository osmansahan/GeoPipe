# GeoPipe: OpenStreetMap Tile Generator

![Version](https://img.shields.io/badge/version-3.0-blue)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)

GeoPipe is a professional-grade, Docker-based system for generating map tiles from OpenStreetMap data. This tool processes OpenStreetMap data in Protocolbuffer Binary Format (`.osm.pbf`) and generates standard map tiles in PNG format that can be used in web mapping applications.

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Detailed Installation Guide](#-detailed-installation-guide)
- [Using the Application](#-using-the-application)
- [Project Configuration](#-project-configuration)
- [Working with Templates](#-working-with-templates)
- [Tile Generation Process](#-tile-generation-process)
- [Troubleshooting](#-troubleshooting)
- [Directory Structure](#-directory-structure)
- [Advanced Usage](#-advanced-usage)

## 🚀 Quick Start

For those familiar with Docker and mapping tools, here's how to get started quickly:

```bash
# Clone the repository
git clone https://github.com/osmansahan/GeoPipe.git
cd GeoPipe

# Start Docker services
docker-compose up -d

# Run the application
# Windows:
osm_pipeline.bat
# Linux/macOS:
python osm_pipeline.py

# Select option 1 to use an existing config (e.g., cyprus.json)
# Or select option 2 to create a new project
```

## 📥 Detailed Installation Guide

### Prerequisites

Before installing GeoPipe, make sure you have the following software installed:

1. **Git** - For cloning the repository
   - Windows: Download from [git-scm.com](https://git-scm.com/downloads)
   - Linux: `sudo apt install git` (Ubuntu/Debian) or `sudo yum install git` (CentOS/RHEL)
   - macOS: `brew install git` (using Homebrew)

2. **Docker Desktop** - For running containerized services
   - Download from [docker.com](https://www.docker.com/products/docker-desktop/)
   - Make sure Docker Compose is included (it comes with Docker Desktop)
   - Allocate at least 4GB of RAM to Docker in the settings

3. **Python 3.6+** - For running the main application
   - Windows: Download from [python.org](https://www.python.org/downloads/) or Microsoft Store
   - Linux: Usually pre-installed, or `sudo apt install python3 python3-pip`
   - macOS: `brew install python`

### Installation Steps

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/osmansahan/GeoPipe.git
   cd GeoPipe
   ```

2. **Install Python Dependencies**:
   ```bash
   # Windows
   pip install -r requirements.txt
   
   # Linux/macOS
   pip3 install -r requirements.txt
   ```

3. **Prepare Data Directory**:
   - Download OpenStreetMap PBF files from [Geofabrik](https://download.geofabrik.de/)
   - Place the downloaded `.osm.pbf` files in the `pbf/` directory
   - Example: Download `cyprus-latest.osm.pbf` and place it in `pbf/cyprus-latest.osm.pbf`

4. **Start Docker Services**:
   ```bash
   # Windows/Linux/macOS
   docker-compose up -d
   ```

5. **Verify Services**:
   ```bash
   docker-compose ps
   ```
   All services (`osm_postgres`, `osm_nginx`, `osm_tools`) should show status as "Up".

## 🖥️ Using the Application

GeoPipe provides an interactive Command Line Interface (CLI) for managing tile generation projects.

### Starting the Application

- **Windows**:
  ```bash
  osm_pipeline.bat
  ```

- **Linux/macOS**:
  ```bash
  python osm_pipeline.py
  # or
  python3 osm_pipeline.py
  ```

### Main Menu Options

When you start the application, you'll see the following menu:

```
===== OSM Tile Generator =====
1. Use existing config
2. Create new config
3. Exit
Enter your choice:
```

- **Option 1**: Use an existing project configuration file
- **Option 2**: Create a new project configuration
- **Option 3**: Exit the application

### Interactive CLI Commands

During operation, the CLI provides real-time feedback and progress information:

- Progress indicators show tile generation status
- Error messages are displayed in red with detailed information
- Status updates show which zoom levels are being processed
- Memory usage and performance statistics are displayed periodically

You can press `Ctrl+C` at any time to gracefully stop the process.

## 🔧 Project Configuration

### Creating a New Project

When selecting option 2 from the main menu, you'll be guided through creating a new project:

1. **Project Name**: Enter a unique identifier (e.g., `albania`, `istanbul`)
2. **Project Description**: Add a brief description of what this project covers
3. **Select PBF File**: Choose from available `.osm.pbf` files in the `pbf/` directory
4. **Rendering Scope**: Choose between:
   - `full`: Process the entire PBF file
   - `bbox`: Specify a geographic bounding box (you'll need to enter coordinates)
5. **Zoom Levels**: Specify minimum and maximum zoom levels
   - Recommended for testing: 8-12 (higher zoom levels generate more tiles)
   - Production: 0-14 (can generate millions of tiles for large areas)

### Using Existing Configurations

When selecting option 1, you'll see a list of available configuration files:

```
Available configurations:
1. cyprus.json
2. Kosova.json
Enter the number of your choice:
```

Select a number to load that configuration and begin tile generation.

### Configuration File Format

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

For bounding box mode, the configuration includes coordinates:

```json
{
  "project_name": "nicosia",
  "description": "Nicosia City Map Tiles",
  "pbf_file": "cyprus-latest.osm.pbf",
  "render_mode": "bbox",
  "bbox": {
    "min_lat": 35.1,
    "max_lat": 35.2,
    "min_lon": 33.3,
    "max_lon": 33.4
  },
  "min_zoom": 10,
  "max_zoom": 16
}
```

## 📝 Working with Templates

GeoPipe includes a template generation system to help create configuration files for different regions.

### Using generate_templates.bat

The `config/generate_templates.bat` script (Windows) or `src/generate_templates.py` (all platforms) helps create configuration templates:

```bash
# Windows
cd config
generate_templates.bat

# Linux/macOS
python src/generate_templates.py
```

This tool will:
1. Scan the `pbf/` directory for available `.osm.pbf` files
2. Generate template configuration files for each PBF file
3. Allow you to customize zoom levels and rendering mode
4. Save the templates to the `config/` directory

### Customizing Templates

You can edit the generated templates manually to:
- Adjust bounding box coordinates
- Change zoom levels
- Modify project descriptions
- Set specific rendering parameters

The template system follows the JSON schema defined in `config/config_schema.json`.

## 🗺️ Tile Generation Process

### How Tiles Are Generated

When you start a project, GeoPipe:

1. **Loads Configuration**: Reads the project settings from the JSON file
2. **Prepares Database**: Checks if the PBF data is already imported into PostgreSQL
   - If not, imports the data using Imposm3 (this happens only once per PBF file)
3. **Calculates Tile Grid**: Determines which tiles need to be generated based on zoom levels
4. **Renders Tiles**: For each tile coordinate (z/x/y):
   - Sends a request to the rendering engine
   - Mapnik processes the request using data from PostgreSQL
   - Generates a 256x256 pixel PNG image
   - Saves the image to the appropriate directory
5. **Monitors Progress**: Shows real-time progress and statistics

### Output Structure

Generated tiles are stored in the `tiles/` directory with the following structure:

```
tiles/
└── {project_name}/
    └── {zoom_level}/
        └── {x_coordinate}/
            └── {y_coordinate}.png
```

Example: `tiles/cyprus/11/1423/982.png`

### Performance Considerations

- **Memory Usage**: Higher zoom levels require more memory
- **Disk Space**: A single country can generate gigabytes of tiles
- **Processing Time**: Varies based on area size and zoom levels
  - Small country at zoom 0-12: ~30 minutes
  - Large country at zoom 0-14: Several hours

## 🔍 Troubleshooting

### Common Issues

- **Docker Services Not Starting**: 
  ```bash
  # Check Docker status
  docker info
  
  # Restart Docker
  # Windows: Restart Docker Desktop
  # Linux: sudo systemctl restart docker
  ```

- **Database Import Errors**:
  ```bash
  # Check container logs
  docker-compose logs osm_postgres
  docker-compose logs osm_tools
  ```

- **Tile Generation Failures**:
  ```bash
  # Check application logs
  # Windows
  type osm_pipeline.log
  
  # Linux/macOS
  cat osm_pipeline.log
  ```

### Emergency Reset

If you encounter persistent issues, you can reset the entire system:

- **Windows**:
  ```bash
  emergency_reset.bat
  ```

- **Linux/macOS**:
  ```bash
  bash emergency_reset.sh
  ```

This will:
1. Stop all containers
2. Remove Docker volumes
3. Clear the tile cache
4. Restart the services

For more detailed troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

## 📁 Directory Structure

```
GeoPipe/
├── config/                  # Project configuration files
│   ├── config_schema.json   # JSON schema for validation
│   ├── cyprus.json          # Example configuration
│   ├── Kosova.json          # Example configuration
│   └── generate_templates.bat # Template generation script
├── pbf/                     # OpenStreetMap PBF data files
│   ├── cyprus-latest.osm.pbf # Example PBF file
│   └── kosovo-latest.osm.pbf # Example PBF file
├── src/                     # Source code
│   ├── config/              # Configuration management modules
│   ├── core/                # Core processing modules
│   ├── ui/                  # User interface modules
│   └── utils/               # Utility functions
├── tiles/                   # Generated tile output
├── docker-compose.yml       # Docker service definitions
├── emergency_reset.bat      # Windows reset script
├── emergency_reset.sh       # Linux/macOS reset script
├── nginx.conf               # Nginx configuration
├── osm_pipeline.bat         # Windows launcher
├── osm_pipeline.py          # Main application
└── requirements.txt         # Python dependencies
```

## 🚀 Advanced Usage

### Custom Styling

GeoPipe uses the standard OSM Carto style by default. Advanced users can modify the styling by:

1. Accessing the `osm_tools` container:
   ```bash
   docker exec -it osm_tools bash
   ```

2. Editing the Mapnik style file:
   ```bash
   nano /home/renderer/src/openstreetmap-carto/style.xml
   ```

3. Restarting the rendering service:
   ```bash
   supervisorctl restart renderd
   ```

### Performance Tuning

For better performance on powerful systems:

1. Edit `docker-compose.yml` to allocate more resources:
   ```yaml
   services:
     osm_postgres:
       deploy:
         resources:
           limits:
             memory: 4G
   ```

2. Optimize PostgreSQL settings in the container:
   ```bash
   docker exec -it osm_postgres bash
   nano /var/lib/postgresql/data/postgresql.conf
   # Increase shared_buffers, work_mem, etc.
   ```

3. Restart services with new settings:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- [OpenStreetMap](https://www.openstreetmap.org/) for providing the map data
- [Geofabrik](https://download.geofabrik.de/) for providing PBF extracts
- [Overv/openstreetmap-tile-server](https://github.com/Overv/openstreetmap-tile-server) for the Docker image
- All contributors to the OSM ecosystem

---

For technical details about the system architecture and implementation, see [PROJECT_DOCUMENTATION.md](PROJECT_DOCUMENTATION.md).