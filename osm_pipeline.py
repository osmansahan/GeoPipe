#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OSM Tile Generator - Professional Pipeline (Modular Edition)
Professional OSM tile generation system using modular architecture

Features:
- Interactive CLI menu
- Config file management
- PBF file management and download
- Project-based tile organization
- Bbox validation
- Progress monitoring
"""

import sys
import logging
from pathlib import Path

# Windows encoding fix
if sys.platform == 'win32':
    import codecs
    import os
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    try:
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)
    except AttributeError:
        # Fallback for older Python versions or different console types
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Logging setup with safe formatting
try:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('osm_pipeline.log', encoding='utf-8', errors='replace'),
            logging.StreamHandler(sys.stdout)
        ]
    )
except Exception:
    # Fallback to basic logging if there are encoding issues
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
logger = logging.getLogger(__name__)

# Import modular components
from src.ui.menu import MenuSystem

class OSMPipeline:
    """Main OSM Pipeline class - Modular wrapper"""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent
        
        # Initialize modular menu system
        self.menu_system = MenuSystem(self.root_dir)
        
        logger.info("OSM Pipeline initialized (Modular Edition)")
    
    def main_menu(self):
        """Main menu - Delegate to modular menu system"""
        self.menu_system.main_menu()

def main():
    """Main function"""
    try:
        pipeline = OSMPipeline()
        while True:
            pipeline.main_menu()
    except KeyboardInterrupt:
        print("\n\nProgram terminated.")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        logger.error(f"Main program error: {e}")

if __name__ == "__main__":
    main()