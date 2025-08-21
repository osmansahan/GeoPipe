#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PBF File Utilities
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class PBFManager:
    """PBF file management utilities"""
    
    def __init__(self, pbf_dir: Path):
        self.pbf_dir = pbf_dir
        self.pbf_dir.mkdir(exist_ok=True)
    
    def list_pbf_files(self) -> List[Path]:
        """List all PBF files"""
        return list(self.pbf_dir.glob("*.pbf"))
    
    def get_pbf_info(self, pbf_file: Path) -> Dict:
        """Get PBF file information"""
        if not pbf_file.exists():
            return {}
        
        size_mb = pbf_file.stat().st_size / (1024 * 1024)
        mod_time = datetime.fromtimestamp(pbf_file.stat().st_mtime)
        
        return {
            'name': pbf_file.name,
            'size_mb': size_mb,
            'modified': mod_time.strftime('%Y-%m-%d %H:%M'),
            'path': f"/pbf/{pbf_file.name}"
        }
    
    def get_pbf_bounds(self, pbf_path: str) -> Optional[Dict]:
        """Get PBF file geographic bounds (simplified approach)"""
        pbf_filename = pbf_path.split('/')[-1].lower()
        
        # Known bounds for common regions
        known_bounds = {
            'cyprus-latest.osm.pbf': {
                'min_lon': 32.0, 'max_lon': 35.0,
                'min_lat': 34.5, 'max_lat': 35.8
            },
            'turkey-latest.osm.pbf': {
                'min_lon': 25.5, 'max_lon': 45.0,
                'min_lat': 35.8, 'max_lat': 42.5
            },
            'greece-latest.osm.pbf': {
                'min_lon': 19.0, 'max_lon': 30.0,
                'min_lat': 34.0, 'max_lat': 42.0
            },
            'italy-latest.osm.pbf': {
                'min_lon': 6.0, 'max_lon': 19.0,
                'min_lat': 35.0, 'max_lat': 48.0
            },
            'germany-latest.osm.pbf': {
                'min_lon': 5.5, 'max_lon': 15.5,
                'min_lat': 47.0, 'max_lat': 55.5
            }
        }
        
        return known_bounds.get(pbf_filename)
    
    def validate_bbox_against_pbf(self, bbox: Dict, pbf_bounds: Dict) -> bool:
        """Validate that bbox is within PBF bounds"""
        return (bbox['min_lon'] >= pbf_bounds['min_lon'] and
                bbox['max_lon'] <= pbf_bounds['max_lon'] and
                bbox['min_lat'] >= pbf_bounds['min_lat'] and
                bbox['max_lat'] <= pbf_bounds['max_lat'])
    
    def validate_bbox_coordinates(self, bbox: Dict) -> bool:
        """Validate bbox coordinate values"""
        try:
            min_lon = float(bbox['min_lon'])
            max_lon = float(bbox['max_lon'])
            min_lat = float(bbox['min_lat'])
            max_lat = float(bbox['max_lat'])
            
            # Basic validation
            if not (-180 <= min_lon <= 180 and -180 <= max_lon <= 180):
                logger.error("Longitude must be between -180 and 180")
                return False
            
            if not (-90 <= min_lat <= 90 and -90 <= max_lat <= 90):
                logger.error("Latitude must be between -90 and 90")
                return False
            
            if min_lon >= max_lon:
                logger.error("Min longitude must be less than max longitude")
                return False
            
            if min_lat >= max_lat:
                logger.error("Min latitude must be less than max latitude")
                return False
            
            return True
            
        except (ValueError, KeyError, TypeError):
            logger.error("Invalid bbox format")
            return False
