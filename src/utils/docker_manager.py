#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced Docker Management for OSM Tile Generator
Provides bulletproof Docker operations with comprehensive error handling
"""

import subprocess
import time
import logging
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import psutil

logger = logging.getLogger(__name__)

class DockerManager:
    """Advanced Docker management with bulletproof operations"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.compose_file = project_root / "docker-compose.yml"
        self.max_retries = 3
        self.retry_delay = 10
        
    def check_system_requirements(self) -> Tuple[bool, List[str]]:
        """Comprehensive system requirements check"""
        issues = []
        
        # Check available memory
        memory = psutil.virtual_memory()
        if memory.total < 4 * 1024 * 1024 * 1024:  # 4GB
            issues.append(f"Insufficient RAM: {memory.total // (1024**3)}GB (minimum 4GB required)")
        
        # Check available disk space
        disk = psutil.disk_usage(str(self.project_root))
        if disk.free < 10 * 1024 * 1024 * 1024:  # 10GB
            issues.append(f"Insufficient disk space: {disk.free // (1024**3)}GB (minimum 10GB required)")
        
        # Check Docker installation
        if not self._check_docker_installation():
            issues.append("Docker Desktop not installed or not running")
        
        # Check internet connectivity
        if not self._check_internet_connection():
            issues.append("No internet connection (required for Docker images)")
        
        return len(issues) == 0, issues
    
    def _check_docker_installation(self) -> bool:
        """Check Docker installation and service status"""
        try:
            # Check Docker CLI
            result = subprocess.run(['docker', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                return False
            
            # Check Docker daemon
            result = subprocess.run(['docker', 'info'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                return False
            
            # Check Docker Compose
            result = subprocess.run(['docker-compose', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
            
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _check_internet_connection(self) -> bool:
        """Check internet connectivity for Docker downloads"""
        try:
            # Try to reach Docker Hub
            result = subprocess.run(['docker', 'pull', '--quiet', 'hello-world'], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                # Clean up test image
                subprocess.run(['docker', 'rmi', 'hello-world'], 
                             capture_output=True, text=True)
                return True
        except subprocess.TimeoutExpired:
            pass
        return False
    
    def ensure_images_available(self) -> bool:
        """Ensure all required Docker images are available with progress"""
        required_images = [
            'postgis/postgis:15-3.3',
            'nginx:alpine', 
            'overv/openstreetmap-tile-server'
        ]
        
        print("\n" + "="*60)
        print("DOCKER IMAGE VERIFICATION AND DOWNLOAD")
        print("="*60)
        
        for image in required_images:
            print(f"\n📦 Checking {image}...")
            
            if self._is_image_available(image):
                print(f"✅ {image} already available")
                continue
            
            print(f"⬇️  Downloading {image}...")
            if not self._pull_image_with_progress(image):
                print(f"❌ Failed to download {image}!")
                return False
            print(f"✅ {image} downloaded successfully")
        
        print(f"\n✅ All Docker images ready!")
        return True
    
    def _is_image_available(self, image: str) -> bool:
        """Check if Docker image is available locally"""
        try:
            result = subprocess.run(['docker', 'image', 'inspect', image], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            return False
    
    def _pull_image_with_progress(self, image: str) -> bool:
        """Pull Docker image with progress indication"""
        for attempt in range(self.max_retries):
            try:
                print(f"   📥 Attempt {attempt + 1}/{self.max_retries}")
                
                process = subprocess.Popen(
                    ['docker', 'pull', image],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    universal_newlines=True
                )
                
                # Show progress
                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output and ('Downloading' in output or 'Extracting' in output):
                        # Show simplified progress
                        if 'Downloading' in output:
                            print("   📥 Downloading...", end='\r')
                        elif 'Extracting' in output:
                            print("   📤 Extracting... ", end='\r')
                
                if process.returncode == 0:
                    print("   ✅ Completed!         ")
                    return True
                else:
                    print(f"   ❌ Error (code: {process.returncode})")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
            
            if attempt < self.max_retries - 1:
                print(f"   ⏳ Waiting {self.retry_delay} seconds...")
                time.sleep(self.retry_delay)
        
        return False
    
    def start_services_robust(self) -> bool:
        """Start Docker services with comprehensive error handling"""
        print("\n" + "="*60)
        print("STARTING DOCKER SERVICES")
        print("="*60)
        
        # Stop any existing services first
        print("🔄 Stopping existing services...")
        self._stop_services_silent()
        
        # Start services with retries
        for attempt in range(self.max_retries):
            print(f"\n🚀 Starting services (Attempt {attempt + 1}/{self.max_retries})")
            
            try:
                result = subprocess.run(
                    ['docker-compose', 'up', '-d'],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )
                
                if result.returncode == 0:
                    # Wait for services to be ready
                    if self._wait_for_services_ready():
                        print("✅ All services started successfully!")
                        return True
                    else:
                        print("⚠️  Services started but not ready")
                else:
                    print(f"❌ Docker Compose error: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                print("⏰ Timeout - services took too long")
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
            
            if attempt < self.max_retries - 1:
                print(f"⏳ Waiting {self.retry_delay} seconds...")
                time.sleep(self.retry_delay)
        
        return False
    
    def _stop_services_silent(self):
        """Silently stop all services"""
        try:
            subprocess.run(['docker-compose', 'down'], 
                         cwd=self.project_root,
                         capture_output=True, timeout=60)
        except:
            pass
    
    def _wait_for_services_ready(self, timeout: int = 120) -> bool:
        """Wait for all services to be ready"""
        print("⏳ Waiting for services to become ready...")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Check PostgreSQL
                pg_result = subprocess.run(
                    ['docker', 'exec', 'osm_postgres', 'pg_isready', '-U', 'osm'],
                    capture_output=True, timeout=10
                )
                
                # Check OSM Tools
                osm_result = subprocess.run(
                    ['docker', 'exec', 'osm_tools', 'pgrep', 'renderd'],
                    capture_output=True, timeout=10
                )
                
                # Check Nginx
                nginx_result = subprocess.run(
                    ['docker', 'exec', 'osm_nginx', 'nginx', '-t'],
                    capture_output=True, timeout=10
                )
                
                if (pg_result.returncode == 0 and 
                    osm_result.returncode == 0 and 
                    nginx_result.returncode == 0):
                    return True
                    
            except subprocess.TimeoutExpired:
                pass
            
            print(".", end="", flush=True)
            time.sleep(2)
        
        print("\n⚠️  Some services may not be fully ready")
        return False
    
    def verify_pbf_import_ready(self, pbf_file: Path) -> bool:
        """Verify that PBF import infrastructure is ready"""
        print(f"\n📋 Checking PBF import readiness: {pbf_file.name}")
        
        # Check if file exists and readable
        if not pbf_file.exists():
            print(f"❌ PBF file not found: {pbf_file}")
            return False
        
        # Check file size and warn if very large
        file_size = pbf_file.stat().st_size / (1024**3)  # GB
        if file_size > 5:
            print(f"⚠️  Large PBF file ({file_size:.1f}GB) - import may take a long time")
            response = input("Continue? (y/N): ").strip().lower()
            if response not in ['y', 'yes']:
                return False
        
        # Check if database is accessible
        try:
            result = subprocess.run(
                ['docker', 'exec', 'osm_postgres', 'psql', '-U', 'osm', '-d', 'gis', '-c', 'SELECT 1;'],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode != 0:
                print("❌ Cannot access PostgreSQL database")
                return False
        except subprocess.TimeoutExpired:
            print("❌ PostgreSQL connection timeout")
            return False
        
        # Check if imposm3 is available
        try:
            result = subprocess.run(
                ['docker', 'exec', 'osm_tools', 'which', 'imposm'],
                capture_output=True, timeout=10
            )
            if result.returncode != 0:
                print("❌ Imposm3 not found")
                return False
        except subprocess.TimeoutExpired:
            print("❌ Imposm3 check timeout")
            return False
        
        print("✅ PBF import infrastructure ready")
        return True
    
    def get_service_status(self) -> Dict[str, str]:
        """Get detailed status of all services"""
        try:
            result = subprocess.run(['docker-compose', 'ps', '--format', 'json'],
                                  cwd=self.project_root,
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                services = {}
                for line in result.stdout.strip().split('\n'):
                    if line:
                        service_info = json.loads(line)
                        services[service_info['Service']] = service_info['State']
                return services
            else:
                return {}
        except:
            return {}
    
    def emergency_cleanup(self) -> bool:
        """Emergency cleanup in case of stuck services"""
        print("\n🆘 EMERGENCY CLEANUP")
        print("="*40)
        
        try:
            # Force stop and remove containers
            subprocess.run(['docker-compose', 'down', '--remove-orphans', '--volumes'],
                         cwd=self.project_root, timeout=60)
            
            # Clean up any stuck containers
            subprocess.run(['docker', 'container', 'prune', '-f'], timeout=30)
            
            # Clean up networks
            subprocess.run(['docker', 'network', 'prune', '-f'], timeout=30)
            
            print("✅ Emergency cleanup completed")
            return True
        except:
            print("❌ Emergency cleanup failed")
            return False
