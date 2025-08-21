#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
System Utilities
"""

import os
import subprocess
import time
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class SystemUtils:
    """System and Docker utilities"""
    
    @staticmethod
    def clear_screen():
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def check_docker() -> bool:
        """Check if Docker is available"""
        try:
            result = subprocess.run(['docker', '--version'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    @staticmethod
    def check_docker_compose() -> bool:
        """Check if Docker Compose is available"""
        try:
            result = subprocess.run(['docker-compose', '--version'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    @staticmethod
    def check_containers() -> bool:
        """Check if OSM containers are running"""
        try:
            result = subprocess.run(['docker-compose', 'ps'], 
                                  capture_output=True, text=True)
            return "osm_tools" in result.stdout
        except Exception:
            return False
    
    @staticmethod
    def start_containers() -> bool:
        """Start Docker containers"""
        try:
            logger.info("Starting Docker containers...")
            subprocess.run(['docker-compose', 'up', '-d'], 
                         capture_output=True, text=True)
            time.sleep(5)
            return True
        except Exception as e:
            logger.error(f"Failed to start containers: {e}")
            return False
    
    @staticmethod
    def check_system() -> bool:
        """Complete system check"""
        logger.info("System check...")
        
        if not SystemUtils.check_docker():
            logger.error("Docker not found!")
            return False
        
        if not SystemUtils.check_docker_compose():
            logger.error("Docker Compose not found!")
            return False
        
        if not SystemUtils.check_containers():
            logger.warning("Containers not running. Starting...")
            if not SystemUtils.start_containers():
                return False
        
        logger.info("System check completed.")
        return True
    
    @staticmethod
    def get_directory_size(directory: Path) -> float:
        """Get directory size in MB"""
        if not directory.exists():
            return 0.0
        
        total_size = sum(f.stat().st_size for f in directory.rglob('*') if f.is_file())
        return total_size / (1024 * 1024)
    
    @staticmethod
    def count_files(directory: Path, pattern: str = "*") -> int:
        """Count files in directory matching pattern"""
        if not directory.exists():
            return 0
        
        return len(list(directory.rglob(pattern)))
