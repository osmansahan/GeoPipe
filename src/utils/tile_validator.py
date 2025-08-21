#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tile Validation and Recovery Utilities
"""

import logging
import math
import time
import subprocess
import json
from pathlib import Path
from typing import List, Tuple, Dict

logger = logging.getLogger(__name__)

class TileValidator:
    """Validate and manage tile completeness"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
    
    def validate_tile(self, tile_path: Path) -> bool:
        """Validate if a tile is complete and valid"""
        if not tile_path.exists():
            return False
        
        try:
            # PNG header check
            with open(tile_path, 'rb') as f:
                header = f.read(8)
                if header != b'\x89PNG\r\n\x1a\n':
                    return False
            
            return True
            
        except Exception as e:
            logger.warning(f"Error validating tile {tile_path}: {e}")
            return False
    
    def find_missing_tiles(self, config: Dict) -> List[Tuple[int, int, int]]:
        """Find missing or invalid tiles based on config"""
        missing_tiles = []
        
        bbox = config.get('bbox')
        render_type = config.get('render_type', 'bbox')
        zoom_levels = config.get('zoom_levels', {})
        min_zoom = zoom_levels.get('min_zoom', 0)
        max_zoom = zoom_levels.get('max_zoom', 12)
        
        if render_type != 'bbox' or not bbox:
            logger.warning("Only bbox validation is supported")
            return missing_tiles
        
        for zoom in range(min_zoom, max_zoom + 1):
            min_x, max_y = self._deg2num(bbox['min_lat'], bbox['min_lon'], zoom)
            max_x, min_y = self._deg2num(bbox['max_lat'], bbox['max_lon'], zoom)
            
            # Ensure bounds
            max_tiles = 2 ** zoom
            min_x = max(0, min_x)
            max_x = min(max_tiles - 1, max_x)
            min_y = max(0, min_y)
            max_y = min(max_tiles - 1, max_y)
            
            for x in range(min_x, max_x + 1):
                for y in range(min_y, max_y + 1):
                    tile_path = self.output_dir / str(zoom) / str(x) / f"{y}.png"
                    
                    if not self.validate_tile(tile_path):
                        missing_tiles.append((zoom, x, y))
        
        return missing_tiles
    
    def _deg2num(self, lat_deg: float, lon_deg: float, zoom: int) -> Tuple[int, int]:
        """Convert coordinates to tile numbers"""
        lat_rad = math.radians(lat_deg)
        n = 2.0 ** zoom
        x = int((lon_deg + 180.0) / 360.0 * n)
        y = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
        return (x, y)
    
    def calculate_expected_tiles(self, config: Dict) -> int:
        """Calculate total expected tiles for config"""
        bbox = config.get('bbox')
        render_type = config.get('render_type', 'bbox')
        zoom_levels = config.get('zoom_levels', {})
        min_zoom = zoom_levels.get('min_zoom', 0)
        max_zoom = zoom_levels.get('max_zoom', 12)
        
        if render_type != 'bbox' or not bbox:
            return 0
        
        total_tiles = 0
        for zoom in range(min_zoom, max_zoom + 1):
            min_x, max_y = self._deg2num(bbox['min_lat'], bbox['min_lon'], zoom)
            max_x, min_y = self._deg2num(bbox['max_lat'], bbox['max_lon'], zoom)
            
            # Ensure bounds
            max_tiles = 2 ** zoom
            min_x = max(0, min_x)
            max_x = min(max_tiles - 1, max_x)
            min_y = max(0, min_y)
            max_y = min(max_tiles - 1, max_y)
            
            tiles_this_zoom = (max_x - min_x + 1) * (max_y - min_y + 1)
            total_tiles += tiles_this_zoom
        
        return total_tiles
    
    def get_validation_report(self, config: Dict) -> Dict:
        """Get comprehensive validation report"""
        expected_tiles = self.calculate_expected_tiles(config)
        missing_tiles = self.find_missing_tiles(config)
        
        # Count valid tiles
        valid_tiles = 0
        if self.output_dir.exists():
            for tile_file in self.output_dir.rglob("*.png"):
                if self.validate_tile(tile_file):
                    valid_tiles += 1
        
        return {
            'expected': expected_tiles,
            'valid': valid_tiles,
            'missing': len(missing_tiles),
            'missing_tiles': missing_tiles,
            'completion_rate': (valid_tiles / expected_tiles * 100) if expected_tiles > 0 else 0
        }
    
    def download_missing_tiles(self, missing_tiles: List[Tuple[int, int, int]], config: Dict) -> int:
        """Download missing tiles with robust retry mechanism"""
        if not missing_tiles:
            logger.info("No missing tiles to download")
            return 0
        
        logger.info(f"Downloading {len(missing_tiles)} missing tiles...")
        
        project_name = config['name']
        base_url = "http://localhost/tile"
        
        success_count = 0
        final_failures = []
        
        for i, (zoom, x, y) in enumerate(missing_tiles, 1):
            tile_dir = self.output_dir / str(zoom) / str(x)
            tile_dir.mkdir(parents=True, exist_ok=True)
            
            tile_path = tile_dir / f"{y}.png"
            tile_url = f"{base_url}/{zoom}/{x}/{y}.png"
            
            # Try to download with enhanced retry
            if self._download_tile_with_retry(tile_url, tile_path, max_retries=10):
                success_count += 1
            else:
                final_failures.append((zoom, x, y))
            
            # Status update every 50 tiles
            if i % 50 == 0 or i == len(missing_tiles):
                success_rate = (success_count / i * 100)
                logger.info(f"Progress: {i}/{len(missing_tiles)} tiles processed ({success_rate:.1f}% success)")
        
        logger.info(f"Download completed: {success_count} successful, {len(final_failures)} failed")
        
        if final_failures:
            logger.warning(f"Failed tiles (first 10): {final_failures[:10]}")
            if len(final_failures) > 10:
                logger.warning(f"... and {len(final_failures) - 10} more failed")
        
        return success_count
    
    def _download_tile_with_retry(self, tile_url: str, tile_path: Path, max_retries: int = 5) -> bool:
        """Enhanced download tile with robust retry mechanism"""
        for attempt in range(max_retries):
            try:
                # Use curl with better options for reliability
                cmd = [
                    'curl', '-s', '-L', '--max-time', '30', '--retry', '2', 
                    '--retry-delay', '1', '-o', str(tile_path), tile_url
                ]
                result = subprocess.run(cmd, timeout=45, capture_output=True)
                
                if result.returncode == 0 and self.validate_tile(tile_path):
                    return True
                
                # Clean up invalid file
                if tile_path.exists():
                    tile_path.unlink()
                    
            except subprocess.TimeoutExpired:
                if tile_path.exists():
                    tile_path.unlink()
            except Exception as e:
                logger.debug(f"Download attempt {attempt + 1} failed: {e}")
                if tile_path.exists():
                    tile_path.unlink()
            
            # Exponential backoff with jitter
            if attempt < max_retries - 1:
                wait_time = (0.5 * (2 ** attempt)) + (0.1 * attempt)
                time.sleep(wait_time)
        
        return False
    
    def detailed_validation_report(self, config: Dict) -> Dict:
        """Get detailed validation report with per-zoom statistics"""
        bbox = config.get('bbox')
        render_type = config.get('render_type', 'bbox')
        zoom_levels = config.get('zoom_levels', {})
        min_zoom = zoom_levels.get('min_zoom', 0)
        max_zoom = zoom_levels.get('max_zoom', 12)
        
        if render_type != 'bbox' or not bbox:
            logger.warning("Only bbox validation is supported")
            return {}
        
        project_name = config['name']
        logger.info(f"Scanning tiles for project: {project_name}")
        logger.info(f"Zoom range: {min_zoom} - {max_zoom}")
        logger.info(f"Output directory: {self.output_dir}")
        
        total_expected = 0
        total_valid = 0
        zoom_stats = {}
        missing_tiles = []
        
        for zoom in range(min_zoom, max_zoom + 1):
            min_x, max_y = self._deg2num(bbox['min_lat'], bbox['min_lon'], zoom)
            max_x, min_y = self._deg2num(bbox['max_lat'], bbox['max_lon'], zoom)
            
            # Ensure bounds
            max_tiles = 2 ** zoom
            min_x = max(0, min_x)
            max_x = min(max_tiles - 1, max_x)
            min_y = max(0, min_y)
            max_y = min(max_tiles - 1, max_y)
            
            zoom_expected = (max_x - min_x + 1) * (max_y - min_y + 1)
            zoom_valid = 0
            zoom_missing = 0
            
            for x in range(min_x, max_x + 1):
                for y in range(min_y, max_y + 1):
                    tile_path = self.output_dir / str(zoom) / str(x) / f"{y}.png"
                    
                    if self.validate_tile(tile_path):
                        zoom_valid += 1
                        total_valid += 1
                    else:
                        missing_tiles.append((zoom, x, y))
                        zoom_missing += 1
                    
                    total_expected += 1
            
            completion_rate = (zoom_valid / zoom_expected * 100) if zoom_expected > 0 else 0
            zoom_stats[zoom] = {
                'expected': zoom_expected,
                'valid': zoom_valid,
                'missing': zoom_missing,
                'completion_rate': completion_rate
            }
            
            logger.info(f"Zoom {zoom}: {zoom_valid}/{zoom_expected} tiles ({completion_rate:.1f}% complete)")
            if zoom_missing > 0:
                logger.info(f"  Missing: {zoom_missing} tiles")
        
        overall_completion = (total_valid / total_expected * 100) if total_expected > 0 else 0
        logger.info(f"Overall completion: {total_valid}/{total_expected} tiles ({overall_completion:.1f}%)")
        
        return {
            'project_name': project_name,
            'total_expected': total_expected,
            'total_valid': total_valid,
            'total_missing': len(missing_tiles),
            'overall_completion': overall_completion,
            'zoom_stats': zoom_stats,
            'missing_tiles': missing_tiles
        }