# OSM Tile Generator - Installation and Usage Guide

This documentation provides comprehensive instructions for installing, configuring, and operating the **OSM Tile Generator Professional Edition v3.0**, a modular system for generating map tiles from OpenStreetMap data.

---

## Project Description

The OSM Tile Generator is a professional-grade, Docker-based system that processes OpenStreetMap data in Protocolbuffer Binary Format (`.osm.pbf`) and generates standard map tiles in PNG format. The system employs a modular architecture with an interactive Command Line Interface (CLI) for project management and tile generation operations. The generated tiles are compatible with standard web mapping libraries and can be integrated into various mapping applications.

---

## System Requirements and Prerequisites

The following software components must be installed and properly configured before proceeding with the installation:

### 1.1 Git Version Control System
-   **Purpose**: Required for repository cloning and source code management
-   **Installation**: Download the appropriate version from [git-scm.com/downloads](https://git-scm.com/downloads/) and follow the standard installation procedure for your operating system
-   **Verification**: Execute `git --version` in your terminal to confirm successful installation

### 1.2 Docker Desktop Platform
-   **Purpose**: Provides containerization infrastructure for PostgreSQL/PostGIS database, Mapnik rendering engine, and associated services
-   **Installation**: Download the platform-specific installer from [www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/) and complete the installation process
-   **Post-Installation**: System restart may be required. Ensure Docker Desktop service is running before proceeding
-   **Verification**: Execute `docker --version` and `docker-compose --version` to confirm proper installation

---

## Installation Procedure

### 2.1 Repository Cloning
Execute the following commands to obtain the project source code:

1.  **Terminal Access**:
    -   **Windows**: Launch `PowerShell` or `Command Prompt`
    -   **macOS/Linux**: Open the `Terminal` application

2.  **Repository Cloning**:
    ```bash
    git clone [REPOSITORY_URL]
    cd geo
    ```
    Replace `[REPOSITORY_URL]` with the actual repository location provided by your system administrator.

3.  **Directory Verification**:
    Confirm the presence of the following essential directories and files:
    ```
    geo/
    ├── pbf/                    # OSM data storage
    ├── config/                 # Project configurations
    ├── tiles/                  # Generated tile output
    ├── src/                    # Source code modules
    ├── docker-compose.yml      # Service definitions
    ├── osm_pipeline.py         # Main application entry point
    └── osm_pipeline.bat        # Windows launcher script
    ```

---

## Data Source Configuration

### 3.1 OpenStreetMap Data Acquisition
The system requires OpenStreetMap data in Protocolbuffer Binary Format (`.osm.pbf`) for tile generation operations.

1.  **Official Data Repository**:
    Access the authoritative data source at [Geofabrik Download Server](https://download.geofabrik.de/)

2.  **Regional Data Selection**:
    Navigate the hierarchical structure to locate the desired geographic region:
    ```
    Continental Division → Country/Region → Administrative Subdivision
    Example: Europe → Germany → germany-latest.osm.pbf
    ```

3.  **Data File Deployment**:
    Transfer the downloaded `.osm.pbf` file to the project's data directory:
    ```bash
    # Example for cyprus-latest.osm.pbf (as observed in current installation)
    cp ~/Downloads/cyprus-latest.osm.pbf ./pbf/
    ```

4.  **Current Data Inventory**:
    The following data files are currently available:
    ```
    pbf/
    ├── cyprus-latest.osm.pbf       # Cyprus region data
    ├── kosovo-latest.osm.pbf       # Kosovo region data
    └── region.osm.pbf              # Generic region data
    ```

---

## System Operation and Tile Generation

### 4.1 Service Infrastructure Initialization
Execute the following commands to activate the containerized services:

1.  **Docker Services Deployment**:
    ```bash
    docker-compose up -d
    ```
    This command initializes the following services:
    - `osm_postgres`: PostgreSQL database with PostGIS extension
    - `osm_nginx`: Nginx reverse proxy server
    - `osm_tools`: OpenStreetMap tile server with Mapnik rendering engine

2.  **Service Status Verification**:
    ```bash
    docker-compose ps
    ```
    Confirm all services display "Up" status before proceeding.

### 4.2 Application Execution
Launch the main application using the appropriate method for your operating system:

-   **Windows Systems**:
    ```bash
    osm_pipeline.bat
    ```

-   **Unix-based Systems (macOS/Linux)**:
    ```bash
    python osm_pipeline.py
    ```

### 4.3 Project Configuration Process
The system provides two operational modes:

**Option 1: New Project Creation**
1. Select menu option `2` (Create new config)
2. Provide the following configuration parameters:
   - **Project Identifier**: Unique alphanumeric project name
   - **Project Description**: Descriptive text for documentation purposes
   - **Data Source**: Select from available PBF files in the data inventory
   - **Rendering Scope**: Choose between `full` (entire dataset) or `bbox` (geographic bounding box)
   - **Zoom Level Range**: Specify minimum and maximum zoom levels (recommended: 8-12 for testing)

**Option 2: Existing Project Utilization**
1. Select menu option `1` (Use existing config)
2. Choose from available project configurations:
   - `cyprus.json` - Cyprus region configuration
   - `Kosova.json` - Kosovo region configuration

### 4.4 Automated Error Prevention and Recovery

The system includes comprehensive error prevention mechanisms:

-   **Automatic System Validation**: Pre-flight checks for Docker, memory, disk space, and network connectivity
-   **Progressive Docker Management**: Automated image downloading with retry mechanisms and progress tracking
-   **Service Health Monitoring**: Continuous verification of PostgreSQL, Renderd, and Nginx service status
-   **PBF Import Validation**: Comprehensive checks for data file integrity and import infrastructure readiness
-   **Emergency Recovery Tools**: Built-in cleanup and reset capabilities for system recovery

### 4.5 Tile Generation Output
Upon completion, generated tiles will be organized in the following directory structure:
```
tiles/{project-name}/
├── {zoom-level}/
│   ├── {x-coordinate}/
│   │   └── {y-coordinate}.png
```

Example output location: `tiles/cyprus/11/1423/982.png`

### 4.6 Emergency Recovery Procedures

If the system encounters critical issues:

1.  **Automatic Recovery**: The system will attempt automatic recovery for most common issues
2.  **Manual Reset**: Execute `emergency_reset.bat` (Windows) to perform complete system cleanup
3.  **Service Restart**: Use `docker-compose restart` to restart individual services
4.  **Log Analysis**: Check `osm_pipeline.log` for detailed error information