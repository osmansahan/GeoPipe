#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tile Generation Core Module
"""

import math
import subprocess
import time
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple


from ..utils.tile_validator import TileValidator

logger = logging.getLogger(__name__)

class TileGenerator:
    """Core tile generation functionality"""
    
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.tiles_dir = root_dir / "tiles"
        
    def deg2num(self, lat_deg: float, lon_deg: float, zoom: int) -> Tuple[int, int]:
        """Convert coordinates to tile numbers"""
        lat_rad = math.radians(lat_deg)
        n = 2.0 ** zoom
        x = int((lon_deg + 180.0) / 360.0 * n)
        y = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
        return (x, y)
    
    def estimate_tile_count(self, bbox: Dict, min_zoom: int, max_zoom: int) -> int:
        """Estimate total tile count for bbox and zoom range"""
        total_tiles = 0
        for zoom in range(min_zoom, max_zoom + 1):
            min_x, max_y = self.deg2num(bbox['min_lat'], bbox['min_lon'], zoom)
            max_x, min_y = self.deg2num(bbox['max_lat'], bbox['max_lon'], zoom)
            
            # Ensure bounds
            max_tiles = 2 ** zoom
            min_x = max(0, min_x)
            max_x = min(max_tiles - 1, max_x)
            min_y = max(0, min_y)
            max_y = min(max_tiles - 1, max_y)
            
            tiles_this_zoom = (max_x - min_x + 1) * (max_y - min_y + 1)
            total_tiles += tiles_this_zoom
        
        return total_tiles
    
    def generate_tiles(self, config: Dict) -> bool:
        """Generate tiles using Docker container with real-time progress"""
        logger.info(f"Starting tile generation: {config['name']}")
        
        # Direct project output directory (no bbox/full separation)
        project_name = config['name']
        output_dir = self.tiles_dir / project_name
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Show initial progress info
        self._show_generation_info(config)
        
        # Calculate estimated tiles for progress tracking
        estimated_tiles = 0
        if config.get('render_type') == 'bbox' and config.get('bbox'):
            zoom_levels = config.get('zoom_levels', {})
            estimated_tiles = self.estimate_tile_count(
                config['bbox'], 
                zoom_levels.get('min_zoom', 0), 
                zoom_levels.get('max_zoom', 12)
            )
        
        # Create tile generation script (simplified for better performance)
        tile_script = self._create_simple_tile_script(config)
        
        try:
            logger.info(f"Generating {project_name} tiles...")
            print("\n" + "="*60)
            print("TILE GENERATION STARTED")
            print("="*60)
            print("Robust completion control enabled...")
            print("="*60)
            
            
            
            # Run script in container with real-time output (unbuffered Python)
            cmd = ['docker', 'exec', 'osm_tools', 'python3', '-u', '-c', tile_script]
            
            # Use Popen for real-time output with proper encoding and unbuffered
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT,  # Combine stderr with stdout
                text=True, 
                encoding='utf-8',
                errors='replace',
                universal_newlines=True,
                bufsize=0  # Unbuffered for real-time output
            )
            
            # Monitor progress in real-time
            output_lines = []
            
            try:
                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        line = output.strip()
                        if line:  # Only print non-empty lines
                            print(line)
                            output_lines.append(line)
                            
                # Get any remaining output
                remaining_output = process.stdout.read()
                if remaining_output:
                    remaining_lines = remaining_output.strip().split('\n')
                    for line in remaining_lines:
                        if line.strip():
                            print(line.strip())
                            output_lines.append(line.strip())
                            
            except Exception as e:
                print(f"Error reading output: {e}")
                
            stdout_lines = output_lines
            stderr_lines = []
            
            return_code = process.returncode
            
            # Print completion line
            print()
            
            # Validate tiles and check for missing ones
            validator = TileValidator(output_dir)
            validation_report = validator.get_validation_report(config)
            
            if return_code == 0:
                print("\n" + "="*60)
                print("TILE GENERATION COMPLETED SUCCESSFULLY")
                print("="*60)
                
                # Show final stats with validation
                print(f"Output Directory: {output_dir}")
                print(f"Expected Tiles: {validation_report['expected']}")
                print(f"Valid Tiles: {validation_report['valid']}")
                print(f"Missing Tiles: {validation_report['missing']}")
                print(f"Completion Rate: {validation_report['completion_rate']:.1f}%")
                print(f"Generation completed successfully")
                
                # Check if tiles are missing and offer retry
                if validation_report['missing'] > 0:
                    print(f"\nWARNING: {validation_report['missing']} tiles are missing or invalid!")
                    print("These tiles may need to be regenerated.")
                
                print("="*60)
                
                logger.info("Tile generation completed successfully")
                logger.info(f"Generated tiles: {validation_report['valid']}")
                
                # Always retry missing tiles for complete coverage
                if validation_report['missing'] > 0:
                    print(f"\nAttempting to complete missing tiles for 100% coverage...")
                    return self._retry_missing_tiles(config, validation_report)
                else:
                    print(f"\nAll tiles downloaded successfully - 100% completion!")
                    return True
            else:
                print("\n" + "="*60)
                print("TILE GENERATION FAILED")
                print("="*60)
                error_output = ''.join(stderr_lines)
                if error_output:
                    print(f"Error: {error_output}")
                print("="*60)
                
                logger.error(f"Tile generation error: {error_output}")
                return False
                
        except subprocess.TimeoutExpired:
            print("\nERROR: Tile generation timeout (1 hour)")
            logger.error("Tile generation timeout (1 hour)")
            return False
        except Exception as e:
            print(f"\nERROR: Tile generation exception: {e}")
            logger.error(f"Tile generation exception: {e}")
            return False
    
    def _show_generation_info(self, config: Dict):
        """Show generation information before starting"""
        print("\n" + "="*60)
        print("TILE GENERATION SETUP")
        print("="*60)
        print(f"Project: {config['name']}")
        print(f"Description: {config.get('description', 'No description')}")
        print(f"PBF File: {config['pbf_path']}")
        print(f"Render Type: {config['render_type']}")
        
        zoom_levels = config.get('zoom_levels', {})
        min_zoom = zoom_levels.get('min_zoom', 0)
        max_zoom = zoom_levels.get('max_zoom', 12)
        print(f"Zoom Range: {min_zoom} - {max_zoom}")
        
        if config.get('render_type') == 'bbox' and config.get('bbox'):
            bbox = config['bbox']
            print(f"Bounding Box:")
            print(f"   Longitude: {bbox['min_lon']:.3f} to {bbox['max_lon']:.3f}")
            print(f"   Latitude: {bbox['min_lat']:.3f} to {bbox['max_lat']:.3f}")
            
            # Calculate estimated tiles
            estimated = self.estimate_tile_count(bbox, min_zoom, max_zoom)
            print(f"Estimated Tiles: ~{estimated:,}")
        
        print("="*60)
    
    def _create_tile_script(self, config: Dict) -> str:
        """Create Python script for tile generation with detailed progress"""
        bbox = config.get('bbox', None)
        min_zoom = config['zoom_levels']['min_zoom']
        max_zoom = config['zoom_levels']['max_zoom']
        render_type = config['render_type']
        project_name = config['name']
        
        script = f'''
import math
import subprocess
import time
from pathlib import Path

def deg2num(lat_deg, lon_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    x = int((lon_deg + 180.0) / 360.0 * n)
    y = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return (x, y)

def calculate_zoom_tiles(zoom, render_type, bbox=None):
    """Calculate tile count for a zoom level"""
    if render_type == "full":
        max_tiles = 2 ** zoom
        return max_tiles * max_tiles
    else:
        min_x, max_y = deg2num(bbox['min_lat'], bbox['min_lon'], zoom)
        max_x, min_y = deg2num(bbox['max_lat'], bbox['max_lon'], zoom)
        
        max_tiles = 2 ** zoom
        min_x = max(0, min_x)
        max_x = min(max_tiles - 1, max_x)
        min_y = max(0, min_y)
        max_y = min(max_tiles - 1, max_y)
        
        return (max_x - min_x + 1) * (max_y - min_y + 1)

def generate_tiles():
    project_name = "{project_name}"
    render_type = "{render_type}"
    bbox = {bbox}
    min_zoom = {min_zoom}
    max_zoom = {max_zoom}

    print("=" * 60)
    print(f"TILE GENERATION: {{project_name}}")
    print("=" * 60)
    print(f"Render Type: {{render_type}}")
    print(f"Zoom Range: {{min_zoom}} - {{max_zoom}}")
    if bbox:
        print(f"Bbox: {{bbox['min_lat']:.3f}},{{bbox['min_lon']:.3f}} to {{bbox['max_lat']:.3f}},{{bbox['max_lon']:.3f}}")

    # Calculate total tiles for all zoom levels
    total_expected = 0
    zoom_info = {{}}
    for z in range(min_zoom, max_zoom + 1):
        tiles_for_zoom = calculate_zoom_tiles(z, render_type, bbox)
        zoom_info[z] = tiles_for_zoom
        total_expected += tiles_for_zoom
    
    print(f"Total Expected Tiles: {{total_expected:,}}")
    print("=" * 60)

    base_url = "http://localhost/tile"
    output_base = f"/data/tiles/{{project_name}}"

    total_tiles = 0
    total_generated = 0
    start_time = time.time()

    for zoom in range(min_zoom, max_zoom + 1):
        zoom_start_time = time.time()
        expected_tiles = zoom_info[zoom]
        
        print(f"\\nZOOM {{zoom}} - Expected: {{expected_tiles:,}} tiles")
        print("-" * 40)

        if render_type == "full":
            max_tiles = 2 ** zoom
            min_x, min_y = 0, 0
            max_x, max_y = max_tiles - 1, max_tiles - 1
        else:
            min_x, max_y = deg2num(bbox['min_lat'], bbox['min_lon'], zoom)
            max_x, min_y = deg2num(bbox['max_lat'], bbox['max_lon'], zoom)
            
            max_tiles = 2 ** zoom
            min_x = max(0, min_x)
            max_x = min(max_tiles - 1, max_x)
            min_y = max(0, min_y)
            max_y = min(max_tiles - 1, max_y)

        print(f"X Range: {{min_x}} - {{max_x}} ({{max_x - min_x + 1}} columns)")
        print(f"Y Range: {{min_y}} - {{max_y}} ({{max_y - min_y + 1}} rows)")

        zoom_tiles = 0
        zoom_generated = 0
        last_progress_time = time.time()

        for x in range(min_x, max_x + 1):
            x_tiles = 0
            x_generated = 0
            
            for y in range(min_y, max_y + 1):
                tile_dir = Path(f"{{output_base}}/{{zoom}}/{{x}}")
                tile_dir.mkdir(parents=True, exist_ok=True)

                tile_path = tile_dir / f"{{y}}.png"
                tile_url = f"{{base_url}}/{{zoom}}/{{x}}/{{y}}.png"

                zoom_tiles += 1
                total_tiles += 1
                x_tiles += 1

                try:
                    cmd = ['curl', '-s', '-o', str(tile_path), tile_url]
                    result = subprocess.run(cmd, timeout=30, capture_output=True)

                    if result.returncode == 0 and tile_path.exists():
                        zoom_generated += 1
                        total_generated += 1
                        x_generated += 1

                except subprocess.TimeoutExpired:
                    pass
                except Exception:
                    pass

                # Progress update every 3 seconds or every 10 tiles
                current_time = time.time()
                if (current_time - last_progress_time > 3) or (zoom_tiles % 10 == 0):
                    progress_pct = (zoom_tiles / expected_tiles) * 100
                    elapsed = current_time - zoom_start_time
                    if zoom_tiles > 0:
                        eta = (elapsed / zoom_tiles) * (expected_tiles - zoom_tiles)
                        rate = zoom_tiles / elapsed if elapsed > 0 else 0
                        # Create progress bar (Windows compatible)
                        bar_width = 30
                        filled = int(bar_width * progress_pct / 100)
                        bar = "#" * filled + "-" * (bar_width - filled)
                        print(f"  Progress: [{{bar}}] {{progress_pct:.1f}}% | {{zoom_generated}}/{{zoom_tiles}} | {{rate:.1f}} tiles/s | ETA: {{eta:.0f}}s", flush=True)
                    last_progress_time = current_time

                time.sleep(0.02)  # Reduced delay for faster processing
            
            # Show column completion
            if x_tiles > 50:  # Only for larger columns
                print(f"  Column X={{x}}: {{x_generated}}/{{x_tiles}} tiles")

        zoom_elapsed = time.time() - zoom_start_time
        zoom_rate = zoom_generated / zoom_elapsed if zoom_elapsed > 0 else 0
        
        print(f"\\nZoom {{zoom}} Complete:")
        print(f"  Generated: {{zoom_generated}}/{{zoom_tiles}} tiles")
        print(f"  Time: {{zoom_elapsed:.1f}}s")
        print(f"  Rate: {{zoom_rate:.1f}} tiles/sec")
        print(f"  Success Rate: {{(zoom_generated/zoom_tiles*100):.1f}}%")

    total_elapsed = time.time() - start_time
    overall_rate = total_generated / total_elapsed if total_elapsed > 0 else 0
    
    print("\\n" + "=" * 60)
    print("GENERATION COMPLETE")
    print("=" * 60)
    print(f"Total Generated: {{total_generated}}/{{total_tiles}} tiles")
    print(f"Total Time: {{total_elapsed:.1f}}s")
    print(f"Average Rate: {{overall_rate:.1f}} tiles/sec")
    print(f"Overall Success: {{(total_generated/total_tiles*100):.1f}}%")
    print("=" * 60)
    
    return total_generated

if __name__ == "__main__":
    result = generate_tiles()
    print(f"Final Result: {{result}} tiles generated")
'''
        return script
    
    def _create_simple_tile_script(self, config: Dict) -> str:
        """Create simplified Python script for tile generation"""
        bbox = config.get('bbox', None)
        min_zoom = config['zoom_levels']['min_zoom']
        max_zoom = config['zoom_levels']['max_zoom']
        render_type = config['render_type']
        project_name = config['name']
        
        script = f'''
import math
import subprocess
import time
import shutil
from pathlib import Path

def deg2num(lat_deg, lon_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    x = int((lon_deg + 180.0) / 360.0 * n)
    y = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return (x, y)

def validate_tile(tile_path):
    """Validate if tile is complete and valid"""
    if not tile_path.exists():
        return False
    
    # Quick PNG header check
    try:
        with open(tile_path, 'rb') as f:
            header = f.read(8)
            if header != b'\\x89PNG\\r\\n\\x1a\\n':
                return False
    except:
        return False
    
    return True

def download_tile_with_retry(tile_url, tile_path, zoom, x, y, max_retries=3):
    """Enhanced download tile with hybrid cache/download mechanism"""
    # First try to copy from renderd cache
    cache_tile_path = Path(f"/var/cache/renderd/tiles/default/{{zoom}}/{{x}}/{{y}}.png")
    
    if cache_tile_path.exists() and validate_tile(cache_tile_path):
        try:
            # Ensure output directory exists
            tile_path.parent.mkdir(parents=True, exist_ok=True)
            # Copy from cache
            shutil.copy2(str(cache_tile_path), str(tile_path))
            if validate_tile(tile_path):
                return True
        except Exception:
            pass
    
    # If cache copy failed, download via HTTP
    for attempt in range(max_retries):
        try:
            # Use curl with better options for reliability
            cmd = [
                'curl', '-s', '-L', '--max-time', '30', '--retry', '2', 
                '--retry-delay', '1', '-o', str(tile_path), tile_url
            ]
            result = subprocess.run(cmd, timeout=45, capture_output=True)
            
            if result.returncode == 0 and validate_tile(tile_path):
                return True
            
            # If failed, remove invalid file
            if tile_path.exists():
                tile_path.unlink()
                
        except subprocess.TimeoutExpired:
            if tile_path.exists():
                tile_path.unlink()
        except Exception:
            if tile_path.exists():
                tile_path.unlink()
        
        # Exponential backoff with jitter
        if attempt < max_retries - 1:
            wait_time = (0.5 * (2 ** attempt)) + (0.1 * attempt)
            time.sleep(wait_time)
    
    return False

def generate_tiles():
    project_name = "{project_name}"
    render_type = "{render_type}"
    bbox = {bbox}
    min_zoom = {min_zoom}
    max_zoom = {max_zoom}

    print(f"Starting generation for: {{project_name}}")
    
    base_url = "http://localhost/tile"
    output_base = f"/data/tiles/{{project_name}}"

    total_generated = 0
    failed_tiles = []

    for zoom in range(min_zoom, max_zoom + 1):
        print(f"Processing zoom level {{zoom}}...")

        if render_type == "full":
            max_tiles = 2 ** zoom
            min_x, min_y = 0, 0
            max_x, max_y = max_tiles - 1, max_tiles - 1
        else:
            min_x, max_y = deg2num(bbox['min_lat'], bbox['min_lon'], zoom)
            max_x, min_y = deg2num(bbox['max_lat'], bbox['max_lon'], zoom)
            
            max_tiles = 2 ** zoom
            min_x = max(0, min_x)
            max_x = min(max_tiles - 1, max_x)
            min_y = max(0, min_y)
            max_y = min(max_tiles - 1, max_y)

        zoom_generated = 0
        zoom_failed = 0

        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                tile_dir = Path(f"{{output_base}}/{{zoom}}/{{x}}")
                tile_dir.mkdir(parents=True, exist_ok=True)

                tile_path = tile_dir / f"{{y}}.png"
                tile_url = f"{{base_url}}/{{zoom}}/{{x}}/{{y}}.png"

                # Check if tile already exists and is valid
                if validate_tile(tile_path):
                    zoom_generated += 1
                    total_generated += 1
                    continue

                # Download tile with retry
                if download_tile_with_retry(tile_url, tile_path, zoom, x, y):
                    zoom_generated += 1
                    total_generated += 1
                else:
                    zoom_failed += 1
                    failed_tiles.append((zoom, x, y))

                # Minimal delay
                time.sleep(0.01)

        print(f"Zoom {{zoom}} completed: {{zoom_generated}} tiles ({{zoom_failed}} failed)")

    # Retry failed tiles with enhanced retry mechanism
    if failed_tiles:
        print(f"\\nRetrying {{len(failed_tiles)}} failed tiles with enhanced retry...")
        retry_success = 0
        final_failures = []
        
        for zoom, x, y in failed_tiles:
            tile_dir = Path(f"{{output_base}}/{{zoom}}/{{x}}")
            tile_path = tile_dir / f"{{y}}.png"
            tile_url = f"{{base_url}}/{{zoom}}/{{x}}/{{y}}.png"
            
            # Enhanced retry with more attempts
            if download_tile_with_retry(tile_url, tile_path, zoom, x, y, max_retries=10):
                retry_success += 1
                total_generated += 1
            else:
                final_failures.append((zoom, x, y))
        
        print(f"Retry completed: {{retry_success}}/{{len(failed_tiles)}} tiles recovered")
        if final_failures:
            print(f"Final failures: {{len(final_failures)}} tiles could not be downloaded")
            for zoom, x, y in final_failures[:5]:  # Show first 5 failures
                print(f"  Failed: {{zoom}}/{{x}}/{{y}}")
            if len(final_failures) > 5:
                print(f"  ... and {{len(final_failures) - 5}} more")

    print(f"Generation finished: {{total_generated}} tiles total")
    return total_generated

if __name__ == "__main__":
    result = generate_tiles()
'''
        return script
    
    def _retry_missing_tiles(self, config: Dict, validation_report: Dict) -> bool:
        """Retry missing tiles"""
        missing_count = validation_report['missing']
        
        if missing_count == 0:
            return True
        
        print(f"\n" + "="*60)
        print(f"RETRYING {missing_count} MISSING TILES")
        print("="*60)
        
        # Create retry script for missing tiles only
        retry_script = self._create_retry_script(config, validation_report['missing_tiles'])
        
        try:
            cmd = ['docker', 'exec', 'osm_tools', 'python3', '-u', '-c', retry_script]
            
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT,
                text=True, 
                encoding='utf-8',
                errors='replace',
                universal_newlines=True,
                bufsize=0
            )
            
            # Monitor retry progress
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    line = output.strip()
                    if line:
                        print(line)
            
            return_code = process.returncode
            
            if return_code == 0:
                # Re-validate after retry
                project_name = config['name']
                output_dir = self.tiles_dir / project_name
                
                validator = TileValidator(output_dir)
                final_report = validator.get_validation_report(config)
                
                print(f"\nRetry completed!")
                print(f"Final completion rate: {final_report['completion_rate']:.1f}%")
                print(f"Remaining missing tiles: {final_report['missing']}")
                
                return True
            else:
                print("Retry failed!")
                return False
                
        except Exception as e:
            print(f"Error during retry: {e}")
            return False
    
    def _create_retry_script(self, config: Dict, missing_tiles: list) -> str:
        """Create script to retry only missing tiles"""
        project_name = config['name']
        render_type = config['render_type']
        
        # Convert missing tiles list to string format for script
        missing_tiles_str = str(missing_tiles)
        
        script = f'''
import subprocess
import time
from pathlib import Path

def download_tile_with_retry(tile_url, tile_path, max_retries=5):
    """Enhanced download tile with robust retry mechanism"""
    for attempt in range(max_retries):
        try:
            # Use curl with better options for reliability
            cmd = [
                'curl', '-s', '-L', '--max-time', '30', '--retry', '2', 
                '--retry-delay', '1', '-o', str(tile_path), tile_url
            ]
            result = subprocess.run(cmd, timeout=45, capture_output=True)
            
            if result.returncode == 0 and tile_path.exists():
                # PNG header validation
                try:
                    with open(tile_path, 'rb') as f:
                        header = f.read(8)
                        if header == b'\\x89PNG\\r\\n\\x1a\\n':
                            return True
                    except Exception:
                        pass
            
            if tile_path.exists():
                tile_path.unlink()
                
        except subprocess.TimeoutExpired:
            if tile_path.exists():
                tile_path.unlink()
        except Exception:
            if tile_path.exists():
                tile_path.unlink()
        
        # Exponential backoff with jitter
        wait_time = (0.5 * (2 ** attempt)) + (0.1 * attempt)
        time.sleep(wait_time)
    
    return False

def retry_missing_tiles():
    project_name = "{project_name}"
    render_type = "{render_type}"
    missing_tiles = {missing_tiles_str}
    
    print(f"Retrying {{len(missing_tiles)}} missing tiles...")
    
    base_url = "http://localhost/tile"
    output_base = f"/data/tiles/{{project_name}}"
    
    success_count = 0
    
    for zoom, x, y in missing_tiles:
        tile_dir = Path(f"{{output_base}}/{{zoom}}/{{x}}")
        tile_dir.mkdir(parents=True, exist_ok=True)
        
        tile_path = tile_dir / f"{{y}}.png"
        tile_url = f"{{base_url}}/{{zoom}}/{{x}}/{{y}}.png"
        
        if download_tile_with_retry(tile_url, tile_path):
            success_count += 1
        
        if success_count % 10 == 0:
            print(f"Retry progress: {{success_count}}/{{len(missing_tiles)}}")
    
    print(f"Retry finished: {{success_count}}/{{len(missing_tiles)}} tiles recovered")
    return success_count

if __name__ == "__main__":
    result = retry_missing_tiles()
'''
        return script
