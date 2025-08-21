#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Template Manager for OSM Tile Generator

This module provides functionality for generating and managing configuration templates.
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class TemplateManager:
    """Manages configuration templates and sample configurations"""
    
    def __init__(self, config_dir: Path = None):
        """Initialize template manager
        
        Args:
            config_dir: Directory for configuration files (defaults to config/)
        """
        if config_dir is None:
            # Find config directory relative to project root
            project_root = Path(__file__).parent.parent.parent
            config_dir = project_root / "config"
        
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
    
    def get_default_template(self) -> Dict:
        """Get the default template configuration structure"""
        return {
            "name": "",
            "description": "",
            "pbf_path": "",
            "render_type": "bbox",
            "bbox": {
                "min_lon": 0.0,
                "min_lat": 0.0,
                "max_lon": 0.0,
                "max_lat": 0.0
            },
            "zoom_levels": {
                "min_zoom": 0,
                "max_zoom": 12
            },
            "style": "osm-carto",
            "output_format": "png",
            "tile_size": 256,
            "created_at": ""
        }
    
    def create_template_file(self, filename: str = None) -> Optional[str]:
        """Create a new template file
        
        Args:
            filename: Name for the template file (without extension)
            
        Returns:
            Filename of created template or None if failed
        """
        if filename is None:
            # Find next available template file name
            counter = 1
            while True:
                if counter == 1:
                    template_file = self.config_dir / "template.json"
                    filename = "template.json"
                else:
                    filename = f"template_{counter}.json"
                    template_file = self.config_dir / filename
                
                if not template_file.exists():
                    break
                counter += 1
        else:
            if not filename.endswith('.json'):
                filename += '.json'
            template_file = self.config_dir / filename
        
        logger.info(f"Creating template file: {filename}")
        
        template_config = self.get_default_template()
        
        try:
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(template_config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Template file created successfully: {filename}")
            return filename
        except Exception as e:
            logger.error(f"Failed to create template file: {e}")
            return None
    
    def get_sample_configs(self) -> Dict[str, Dict]:
        """Get predefined sample configurations"""
        return {
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
            },
            "greece_sample": {
                "name": "greece_sample",
                "description": "Greece sample configuration",
                "pbf_path": "/pbf/greece-latest.osm.pbf",
                "render_type": "bbox",
                "bbox": {
                    "min_lon": 19.0,
                    "min_lat": 34.0,
                    "max_lon": 30.0,
                    "max_lat": 42.0
                },
                "zoom_levels": {
                    "min_zoom": 0,
                    "max_zoom": 13
                },
                "style": "osm-carto",
                "output_format": "png",
                "tile_size": 256
            },
            "italy_sample": {
                "name": "italy_sample",
                "description": "Italy sample configuration", 
                "pbf_path": "/pbf/italy-latest.osm.pbf",
                "render_type": "bbox",
                "bbox": {
                    "min_lon": 6.0,
                    "min_lat": 35.0,
                    "max_lon": 19.0,
                    "max_lat": 48.0
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
    
    def create_sample_configs(self, samples: List[str] = None) -> int:
        """Create sample configuration files
        
        Args:
            samples: List of sample names to create (creates all if None)
            
        Returns:
            Number of successfully created samples
        """
        all_samples = self.get_sample_configs()
        
        if samples is None:
            samples = list(all_samples.keys())
        
        created_count = 0
        for sample_name in samples:
            if sample_name not in all_samples:
                logger.warning(f"Unknown sample: {sample_name}")
                continue
            
            config_file = self.config_dir / f"{sample_name}.json"
            if config_file.exists():
                logger.warning(f"Sample already exists: {sample_name}.json")
                continue
                
            try:
                config = all_samples[sample_name].copy()
                config['created_at'] = datetime.now().isoformat()
                
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                
                created_count += 1
                logger.info(f"Sample config created: {sample_name}.json")
            except Exception as e:
                logger.error(f"Failed to create sample {sample_name}: {e}")
        
        return created_count
    
    def create_custom_config(self, name: str, config_data: Dict) -> bool:
        """Create a custom configuration file
        
        Args:
            name: Name for the configuration (without extension)
            config_data: Configuration data dictionary
            
        Returns:
            True if successful, False otherwise
        """
        if not name.endswith('.json'):
            name += '.json'
        
        config_file = self.config_dir / name
        
        try:
            # Add metadata
            config_data = config_data.copy()
            config_data['created_at'] = datetime.now().isoformat()
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Custom config created: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to create custom config {name}: {e}")
            return False
    
    def list_templates(self) -> List[str]:
        """List all template files in config directory"""
        templates = []
        for file_path in self.config_dir.glob("*.json"):
            templates.append(file_path.name)
        return sorted(templates)
    
    def validate_config_structure(self, config: Dict) -> bool:
        """Validate that a configuration has the required structure
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = [
            'name', 'render_type', 'bbox', 'zoom_levels',
            'style', 'output_format', 'tile_size'
        ]
        
        for field in required_fields:
            if field not in config:
                logger.error(f"Missing required field: {field}")
                return False
        
        # Validate bbox structure
        bbox = config.get('bbox', {})
        bbox_fields = ['min_lon', 'min_lat', 'max_lon', 'max_lat']
        for field in bbox_fields:
            if field not in bbox:
                logger.error(f"Missing bbox field: {field}")
                return False
        
        # Validate zoom levels
        zoom = config.get('zoom_levels', {})
        if 'min_zoom' not in zoom or 'max_zoom' not in zoom:
            logger.error("Missing zoom level fields")
            return False
        
        return True
    
    def load_config(self, filename: str) -> Optional[Dict]:
        """Load a configuration file
        
        Args:
            filename: Name of the configuration file
            
        Returns:
            Configuration dictionary or None if failed
        """
        if not filename.endswith('.json'):
            filename += '.json'
        
        config_file = self.config_dir / filename
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            if self.validate_config_structure(config):
                return config
            else:
                logger.error(f"Invalid config structure in {filename}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to load config {filename}: {e}")
            return None
    
    def get_config_info(self, filename: str) -> Optional[Dict]:
        """Get basic information about a configuration file
        
        Args:
            filename: Name of the configuration file
            
        Returns:
            Dictionary with config info or None if failed
        """
        config = self.load_config(filename)
        if config is None:
            return None
        
        return {
            'filename': filename,
            'name': config.get('name', 'Unknown'),
            'description': config.get('description', ''),
            'created_at': config.get('created_at', ''),
            'render_type': config.get('render_type', ''),
            'zoom_range': f"{config.get('zoom_levels', {}).get('min_zoom', 0)}-{config.get('zoom_levels', {}).get('max_zoom', 12)}"
        }
