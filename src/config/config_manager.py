#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration Management Module
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ConfigManager:
    """Configuration file management"""
    
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.config_dir.mkdir(exist_ok=True)
    
    def list_configs(self) -> List[Path]:
        """List all configuration files"""
        return list(self.config_dir.glob("*.json"))
    
    def load_config(self, config_file: Path) -> Optional[Dict]:
        """Load configuration from file"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Cannot load config {config_file}: {e}")
            return None
    
    def save_config(self, config: Dict, filename: str) -> bool:
        """Save configuration to file"""
        config_file = self.config_dir / f"{filename}.json"
        try:
            config['updated_at'] = datetime.now().isoformat()
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Config saved: {config_file}")
            return True
        except Exception as e:
            logger.error(f"Cannot save config: {e}")
            return False
    
    def load_template(self) -> Optional[Dict]:
        """Load template configuration"""
        template_file = self.config_dir / "template.json"
        if not template_file.exists():
            logger.error("Template file not found!")
            return None
        
        return self.load_config(template_file)
    
    def create_config(self, name: str, description: str, pbf_path: str, 
                     render_type: str, min_zoom: int, max_zoom: int, 
                     bbox: Optional[Dict] = None) -> Dict:
        """Create new configuration"""
        config = {
            "name": name,
            "description": description,
            "pbf_path": pbf_path,
            "render_type": render_type,
            "zoom_levels": {
                "min_zoom": min_zoom,
                "max_zoom": max_zoom
            },
            "style": "osm-carto",
            "output_format": "png",
            "tile_size": 256,
            "created_at": datetime.now().isoformat()
        }
        
        if bbox:
            config["bbox"] = bbox
        
        return config
    
    def validate_config(self, config: Dict) -> bool:
        """Basic config validation"""
        required_fields = ['name', 'pbf_path', 'render_type', 'zoom_levels']
        
        for field in required_fields:
            if field not in config:
                logger.error(f"Missing required field: {field}")
                return False
        
        # Validate zoom levels
        zoom_levels = config.get('zoom_levels', {})
        min_zoom = zoom_levels.get('min_zoom')
        max_zoom = zoom_levels.get('max_zoom')
        
        if not (isinstance(min_zoom, int) and isinstance(max_zoom, int)):
            logger.error("Invalid zoom levels")
            return False
        
        if not (0 <= min_zoom <= max_zoom <= 20):
            logger.error("Zoom levels must be between 0-20")
            return False
        
        # Validate bbox for bbox type
        if config.get('render_type') == 'bbox' and 'bbox' not in config:
            logger.error("Bbox required for bbox render type")
            return False
        
        return True
    
    def create_template_file(self) -> bool:
        """Create a default template.json file"""
        template_file = self.config_dir / "template.json"
        
        if template_file.exists():
            logger.warning("Template file already exists")
            return False
        
        template_config = {
            "name": "project_name",
            "description": "Project description",
            "pbf_path": "/pbf/region.osm.pbf",
            "render_type": "bbox",
            "bbox": {
                "min_lon": -10.0,
                "min_lat": 35.0,
                "max_lon": 5.0,
                "max_lat": 45.0
            },
            "zoom_levels": {
                "min_zoom": 0,
                "max_zoom": 12
            },
            "style": "osm-carto",
            "output_format": "png",
            "tile_size": 256,
            "created_at": "2024-01-01T00:00:00"
        }
        
        try:
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(template_config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Template file created: {template_file}")
            return True
        except Exception as e:
            logger.error(f"Cannot create template file: {e}")
            return False
    
    def create_sample_configs(self) -> bool:
        """Create sample configuration files"""
        samples = {
            "cyprus_sample": {
                "name": "cyprus_sample",
                "description": "Cyprus island sample configuration",
                "pbf_path": "/pbf/cyprus-latest.osm.pbf",
                "render_type": "bbox",
                "bbox": {
                    "min_lon": 32.2,
                    "min_lat": 34.5,
                    "max_lon": 34.7,
                    "max_lat": 35.7
                },
                "zoom_levels": {
                    "min_zoom": 0,
                    "max_zoom": 14
                },
                "style": "osm-carto",
                "output_format": "png",
                "tile_size": 256
            },
            "turkey_sample": {
                "name": "turkey_sample", 
                "description": "Turkey sample configuration",
                "pbf_path": "/pbf/turkey-latest.osm.pbf",
                "render_type": "bbox",
                "bbox": {
                    "min_lon": 26.0,
                    "min_lat": 36.0,
                    "max_lon": 45.0,
                    "max_lat": 42.0
                },
                "zoom_levels": {
                    "min_zoom": 0,
                    "max_zoom": 12
                },
                "style": "osm-carto",
                "output_format": "png",
                "tile_size": 256
            }
        }
        
        created_count = 0
        for filename, config in samples.items():
            config_file = self.config_dir / f"{filename}.json"
            if not config_file.exists():
                try:
                    config['created_at'] = datetime.now().isoformat()
                    with open(config_file, 'w', encoding='utf-8') as f:
                        json.dump(config, f, indent=2, ensure_ascii=False)
                    created_count += 1
                    logger.info(f"Sample config created: {filename}")
                except Exception as e:
                    logger.error(f"Cannot create sample {filename}: {e}")
        
        return created_count > 0
