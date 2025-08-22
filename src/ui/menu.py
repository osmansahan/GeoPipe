#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
User Interface Menu System
"""

import logging
from pathlib import Path
from typing import Dict, Optional

from ..utils.system_utils import SystemUtils
from ..utils.docker_manager import DockerManager
from ..config.config_manager import ConfigManager
from ..utils.pbf_utils import PBFManager
from ..core.tile_generator import TileGenerator

logger = logging.getLogger(__name__)

class MenuSystem:
    """Main menu system for OSM tile generator"""
    
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.config_manager = ConfigManager(root_dir / "config")
        self.pbf_manager = PBFManager(root_dir / "pbf")
        self.tile_generator = TileGenerator(root_dir)
        self.docker_manager = DockerManager(root_dir)
    
    def print_header(self):
        """Print application header"""
        SystemUtils.clear_screen()
        print("=" * 60)
        print("     OSM TILE GENERATOR")
        print("     Professional Edition v3.0 (Modular)")
        print("=" * 60)
        print()
    
    def main_menu(self):
        """Main menu"""
        self.print_header()
        print("OSM TILE GENERATOR")
        print("=" * 50)
        print("1. Use existing config")
        print("2. Create new config")
        print("0. Exit")
        print("=" * 50)
        
        choice = input("\nYour choice (0-2): ").strip()
        
        if choice == "1":
            self.use_existing_config()
        elif choice == "2":
            self.create_new_config()
        elif choice == "0":
            print("\nGoodbye!")
            return False
        else:
            print("\nInvalid choice!")
            input("\nPress Enter to continue...")
        
        return True
    
    def use_existing_config(self):
        """Use existing configuration"""
        self.print_header()
        print("USE EXISTING CONFIG")
        print("=" * 50)
        
        config_files = self.config_manager.list_configs()
        
        if not config_files:
            print("No existing configurations found.")
            print("Please create a new configuration.")
            input("\nPress Enter to continue...")
            return
        
        # Display configs
        print("Available configurations:")
        for i, config_file in enumerate(config_files, 1):
            config = self.config_manager.load_config(config_file)
            if config:
                print(f"{i}. {config.get('name', config_file.stem)}")
                print(f"   Description: {config.get('description', 'No description')}")
                print(f"   PBF File: {config.get('pbf_path', 'Unknown')}")
                print(f"   Type: {config.get('render_type', 'unknown')}")
                
                zoom_levels = config.get('zoom_levels', {})
                min_zoom = zoom_levels.get('min_zoom', '?')
                max_zoom = zoom_levels.get('max_zoom', '?')
                print(f"   Zoom: {min_zoom}-{max_zoom}")
                
                if config.get('render_type') == 'bbox' and config.get('bbox'):
                    bbox = config['bbox']
                    print(f"   Area: {bbox['min_lat']:.2f},{bbox['min_lon']:.2f} to {bbox['max_lat']:.2f},{bbox['max_lon']:.2f}")
                print()
        
        # Select config
        try:
            choice = int(input("Select configuration (number): ")) - 1
            if 0 <= choice < len(config_files):
                config_file = config_files[choice]
                config = self.config_manager.load_config(config_file)
                if config:
                    self._start_generation(config)
            else:
                print("Error: Invalid choice!")
        except ValueError:
            print("Error: Invalid number!")
        
        input("\nPress Enter to continue...")
    
    def create_new_config(self):
        """Create new configuration"""
        self.print_header()
        print("CREATE NEW CONFIG")
        print("=" * 50)
        
        # Project name
        while True:
            name = input("Project name: ").strip()
            if name and name.replace('_', '').replace('-', '').isalnum():
                config_file_path = self.config_manager.config_dir / f"{name}.json"
                if config_file_path.exists():
                    overwrite = input(f"Project '{name}' already exists. Overwrite? (y/N): ").strip().lower()
                    if overwrite in ['y', 'yes']:
                        break
                    else:
                        continue
                else:
                    break
            print("Error: Project name can only contain letters, numbers, underscore and dash!")
        
        # Description
        description = input("Description: ").strip()
        if not description:
            description = f'{name} OSM tiles'
        
        # PBF file selection
        pbf_path = self._select_pbf_file()
        if not pbf_path:
            input("\nPress Enter to continue...")
            return
        
        # Render type
        print("\nRender Type:")
        print("1. full - Entire PBF file")
        print("2. bbox - Specific area")
        
        while True:
            render_choice = input("Choice (1-2): ").strip()
            if render_choice in ["1", "2"]:
                render_type = "full" if render_choice == "1" else "bbox"
                break
            print("Error: Invalid choice!")
        
        # Bbox information
        bbox = None
        if render_type == "bbox":
            bbox = self._get_bbox_input(pbf_path)
            if not bbox:
                input("\nPress Enter to continue...")
                return
        
        # Zoom levels
        print("\nZoom Levels:")
        try:
            min_zoom = int(input("Min zoom (0-20): "))
            max_zoom = int(input("Max zoom (0-20): "))
            
            if not (0 <= min_zoom <= max_zoom <= 20):
                print("Error: Invalid zoom values!")
                input("\nPress Enter to continue...")
                return
        except ValueError:
            print("Error: Invalid zoom value!")
            input("\nPress Enter to continue...")
            return
        
        # Create and save config
        config = self.config_manager.create_config(
            name, description, pbf_path, render_type, min_zoom, max_zoom, bbox
        )
        
        # Show summary and confirm
        self.show_config_summary(config)
        
        confirm = input("\nSave and start generation? (y/N): ").strip().lower()
        
        if confirm in ['y', 'yes']:
            if self.config_manager.save_config(config, name):
                print(f"\nConfiguration saved!")
                self._start_generation(config)
            else:
                print("Error: Cannot save configuration!")
        else:
            print("Cancelled.")
        
        input("\nPress Enter to continue...")
    
    def _select_pbf_file(self) -> Optional[str]:
        """Select PBF file"""
        print("\nPBF FILE SELECTION")
        print("-" * 30)
        
        pbf_files = self.pbf_manager.list_pbf_files()
        
        if not pbf_files:
            print("No PBF files found.")
            return None
        
        print("Available PBF files:")
        for i, pbf_file in enumerate(pbf_files, 1):
            info = self.pbf_manager.get_pbf_info(pbf_file)
            print(f"{i}. {info['name']} ({info['size_mb']:.1f} MB)")
        
        try:
            choice = int(input("Select PBF file (number): ")) - 1
            if 0 <= choice < len(pbf_files):
                return f"/pbf/{pbf_files[choice].name}"
            else:
                print("Error: Invalid choice!")
                return None
        except ValueError:
            print("Error: Invalid number!")
            return None
    
    def _get_bbox_input(self, pbf_path: str) -> Optional[Dict]:
        """Get bounding box coordinates"""
        print("\nBOUNDING BOX COORDINATES")
        print("-" * 30)
        
        # Show PBF bounds if available
        pbf_bounds = self.pbf_manager.get_pbf_bounds(pbf_path)
        
        if pbf_bounds:
            print(f"PBF coverage area:")
            print(f"  Longitude: {pbf_bounds['min_lon']:.3f} to {pbf_bounds['max_lon']:.3f}")
            print(f"  Latitude: {pbf_bounds['min_lat']:.3f} to {pbf_bounds['max_lat']:.3f}")
            print("Your bbox must be within this area!\n")
        
        try:
            min_lon = float(input("Min Longitude: "))
            min_lat = float(input("Min Latitude: "))
            max_lon = float(input("Max Longitude: "))
            max_lat = float(input("Max Latitude: "))
            
            bbox = {
                "min_lon": min_lon,
                "min_lat": min_lat,
                "max_lon": max_lon,
                "max_lat": max_lat
            }
            
            # Validate coordinates
            if not self.pbf_manager.validate_bbox_coordinates(bbox):
                return None
            
            # Validate against PBF bounds
            if pbf_bounds and not self.pbf_manager.validate_bbox_against_pbf(bbox, pbf_bounds):
                print("\nError: Bounding box is outside the PBF file coverage area!")
                return None
            
            return bbox
            
        except ValueError:
            print("Error: Invalid coordinate value!")
            return None
    
    def show_config_summary(self, config: Dict):
        """Show configuration summary"""
        print("\n" + "=" * 50)
        print("CONFIGURATION SUMMARY")
        print("=" * 50)
        print(f"Project Name: {config.get('name', 'Unknown')}")
        print(f"Description: {config.get('description', 'No description')}")
        print(f"PBF File: {config.get('pbf_path', 'Unknown')}")
        print(f"Render Type: {config.get('render_type', 'unknown')}")
        
        if config.get('render_type') == 'bbox' and config.get('bbox'):
            bbox = config['bbox']
            print(f"Bounding Box:")
            print(f"  Min Longitude: {bbox['min_lon']}")
            print(f"  Min Latitude: {bbox['min_lat']}")
            print(f"  Max Longitude: {bbox['max_lon']}")
            print(f"  Max Latitude: {bbox['max_lat']}")
        
        zoom_levels = config.get('zoom_levels', {})
        print(f"Zoom Levels: {zoom_levels.get('min_zoom', '?')} - {zoom_levels.get('max_zoom', '?')}")
        print(f"Output Format: {config.get('output_format', 'png')}")
        print(f"Tile Size: {config.get('tile_size', 256)}px")
        
        # Estimate tile count
        if config.get('render_type') == 'bbox' and config.get('bbox') and zoom_levels:
            total_tiles = self.tile_generator.estimate_tile_count(
                config['bbox'], 
                zoom_levels['min_zoom'], 
                zoom_levels['max_zoom']
            )
            print(f"Estimated Tiles: ~{total_tiles:,}")
        
        print("=" * 50)
    
    def _start_generation(self, config: Dict):
        """Start tile generation with bulletproof Docker handling"""
        self.print_header()
        print("STARTING TILE GENERATION WITH TRACKING")
        print("=" * 60)
        
        # 1. Comprehensive system check
        print("[1] Checking system requirements...")
        requirements_ok, issues = self.docker_manager.check_system_requirements()
        if not requirements_ok:
            print("\nERROR: System requirements not met:")
            for issue in issues:
                print(f"   - {issue}")
            print("\nPlease resolve the issues and try again.")
            input("\nPress Enter to continue...")
            return
        print("OK: System requirements met")
        
        # 2. Check PBF file
        print(f"\n[2] Checking PBF file...")
        pbf_path = self.root_dir / config['pbf_path'].lstrip('/')
        if not pbf_path.exists():
            print(f"ERROR: PBF file not found: {pbf_path}")
            input("\nPress Enter to continue...")
            return
        print(f"OK: PBF file exists: {pbf_path.name}")
        
        # 3. Ensure Docker images are available
        print(f"\n[3] Checking Docker images...")
        if not self.docker_manager.ensure_images_available():
            print("ERROR: Docker images could not be prepared!")
            print("Check your internet connection and try again.")
            input("\nPress Enter to continue...")
            return
        
        # 4. Start Docker services robustly
        print(f"\n[4] Starting Docker services...")
        if not self.docker_manager.start_services_robust():
            print("ERROR: Docker services could not be started!")
            print("Do you want to perform an emergency cleanup?")
            response = input("(y/N): ").strip().lower()
            if response in ['y', 'yes']:
                self.docker_manager.emergency_cleanup()
            input("\nPress Enter to continue...")
            return
        
        # 5. Verify PBF import readiness
        print(f"\n[5] Checking PBF import readiness...")
        if not self.docker_manager.verify_pbf_import_ready(pbf_path):
            print("ERROR: PBF import infrastructure is not ready!")
            input("\nPress Enter to continue...")
            return
        
        # 6. Start generation
        print(f"\n[6] Starting tile generation...")
        print("=" * 60)
        print("SUCCESS: ALL CHECKS PASSED - STARTING PRODUCTION")
        print("=" * 60)
        
        success = self.tile_generator.generate_tiles(config)
        
        print("\n" + "=" * 60)
        if success:
            print(f"SUCCESS! {config['name']} tile generation completed!")
            print(f"Files saved in: tiles/{config['name']}/ directory")
        else:
            print(f"FAILED! {config['name']} tile generation could not be completed!")
            print("Check log files: osm_pipeline.log")
        print("=" * 60)
        
        input("\nPress Enter to continue...")
    
    def run(self):
        """Run the menu system"""
        try:
            while self.main_menu():
                pass
        except KeyboardInterrupt:
            print("\n\nProgram terminated.")
        except Exception as e:
            print(f"\nUnexpected error: {e}")
            logger.error(f"Menu system error: {e}")
