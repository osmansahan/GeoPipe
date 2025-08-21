#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tile Validation Test Script

This script provides a command-line interface for testing and validating
tile completeness using the TileValidator class.
"""

import sys
import json
import logging
from pathlib import Path
from typing import Dict, Optional

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from utils.tile_validator import TileValidator
from config.config_manager import ConfigManager

def setup_logging(verbose: bool = False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('validation_test.log')
        ]
    )

def load_config(config_file: str) -> Optional[Dict]:
    """Load configuration from file"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except Exception as e:
        logging.error(f"Error loading config file: {e}")
        return None

def print_validation_report(report: Dict):
    """Print formatted validation report"""
    print("="*60)
    print("TILE VALIDATION REPORT")
    print("="*60)
    
    if not report:
        print("No validation data available")
        return
    
    print(f"Project: {report.get('project_name', 'Unknown')}")
    print(f"Total Expected: {report.get('total_expected', 0):,} tiles")
    print(f"Total Valid: {report.get('total_valid', 0):,} tiles")
    print(f"Total Missing: {report.get('total_missing', 0):,} tiles")
    print(f"Overall Completion: {report.get('overall_completion', 0):.1f}%")
    
    if 'zoom_stats' in report:
        print("\nPer-Zoom Statistics:")
        print("-" * 40)
        for zoom, stats in report['zoom_stats'].items():
            print(f"Zoom {zoom:2d}: {stats['valid']:5,}/{stats['expected']:5,} "
                  f"({stats['completion_rate']:5.1f}%)")
            if stats['missing'] > 0:
                print(f"         Missing: {stats['missing']:,} tiles")
    
    print("="*60)

def run_validation_test(config_file: str, fix_missing: bool = False, verbose: bool = False):
    """Run complete validation test"""
    setup_logging(verbose)
    logger = logging.getLogger(__name__)
    
    logger.info(f"Starting validation test for config: {config_file}")
    
    # Load configuration
    config = load_config(config_file)
    if not config:
        return False
    
    # Determine output directory
    project_name = config['name']
    tiles_dir = Path("tiles")
    output_dir = tiles_dir / project_name
    
    if not output_dir.exists():
        logger.error(f"Output directory does not exist: {output_dir}")
        return False
    
    # Initialize validator
    validator = TileValidator(output_dir)
    
    # Get detailed validation report
    logger.info("Performing detailed validation scan...")
    report = validator.detailed_validation_report(config)
    
    if not report:
        logger.error("Failed to generate validation report")
        return False
    
    # Print report
    print_validation_report(report)
    
    # Check if tiles are missing
    missing_tiles = report.get('missing_tiles', [])
    
    if not missing_tiles:
        print("\nSUCCESS: All tiles are present and valid - 100% completion!")
        return True
    
    print(f"\nWARNING: Found {len(missing_tiles)} missing or invalid tiles")
    
    if fix_missing:
        print("\nINFO: Attempting to download missing tiles...")
        downloaded = validator.download_missing_tiles(missing_tiles, config)
        
        if downloaded > 0:
            # Re-validate after download attempt
            print("\nINFO: Re-validating after download attempt...")
            final_report = validator.detailed_validation_report(config)
            
            remaining_missing = final_report.get('missing_tiles', [])
            
            if not remaining_missing:
                print("\nSUCCESS: All tiles completed successfully - 100% coverage achieved!")
                return True
            else:
                print(f"\nWARNING: {len(remaining_missing)} tiles still missing after retry")
                print("These tiles may require manual investigation or server-side fixes")
                return False
        else:
            print("\nERROR: No tiles were successfully downloaded")
            return False
    else:
        print(f"\nINFO: To attempt downloading missing tiles, run with --fix flag:")
        print(f"   python validate_test.py {config_file} --fix")
        return False

def run_quick_test(config_file: str):
    """Run quick validation test using basic validator"""
    config = load_config(config_file)
    if not config:
        return False
    
    project_name = config['name']
    tiles_dir = Path("tiles")
    output_dir = tiles_dir / project_name
    
    if not output_dir.exists():
        print(f"ERROR: Output directory does not exist: {output_dir}")
        return False
    
    validator = TileValidator(output_dir)
    report = validator.get_validation_report(config)
    
    print(f"Quick Test Results for '{project_name}':")
    print(f"  Expected: {report['expected']:,} tiles")
    print(f"  Valid: {report['valid']:,} tiles")
    print(f"  Missing: {report['missing']:,} tiles")
    print(f"  Completion: {report['completion_rate']:.1f}%")
    
    return report['missing'] == 0

def main():
    """Main CLI interface"""
    if len(sys.argv) < 2:
        print("Usage: python validate_test.py <config_file> [options]")
        print("Options:")
        print("  --fix       Attempt to download missing tiles")
        print("  --quick     Run quick validation test only")
        print("  --verbose   Enable verbose logging")
        print()
        print("Examples:")
        print("  python validate_test.py config/cyprus.json")
        print("  python validate_test.py config/cyprus.json --fix")
        print("  python validate_test.py config/cyprus.json --quick")
        sys.exit(1)
    
    config_file = sys.argv[1]
    fix_missing = '--fix' in sys.argv
    quick_mode = '--quick' in sys.argv
    verbose = '--verbose' in sys.argv
    
    if not Path(config_file).exists():
        print(f"ERROR: Config file does not exist: {config_file}")
        sys.exit(1)
    
    try:
        if quick_mode:
            success = run_quick_test(config_file)
        else:
            success = run_validation_test(config_file, fix_missing, verbose)
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\nINFO: Validation test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Validation test failed: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
