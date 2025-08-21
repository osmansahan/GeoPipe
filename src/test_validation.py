#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Tile Validation Test

A simplified test script for validating tiles within the src structure.
"""

import sys
import json
from pathlib import Path
from utils.tile_validator import TileValidator

def test_validation(config_path: str = None):
    """Test tile validation functionality"""
    
    # Use default config if not provided
    if not config_path:
        config_path = "config/cyprus.json"
    
    # Check if config exists
    config_file = Path(config_path)
    if not config_file.exists():
        print(f"ERROR: Config file not found: {config_path}")
        return False
    
    # Load config
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        print(f"ERROR: Error loading config: {e}")
        return False
    
    # Setup paths
    project_name = config['name']
    tiles_dir = Path("tiles")
    output_dir = tiles_dir / project_name
    
    print(f"Testing validation for project: {project_name}")
    print(f"Tiles directory: {output_dir}")
    
    if not output_dir.exists():
        print(f"ERROR: Tiles directory does not exist: {output_dir}")
        return False
    
    # Initialize validator
    validator = TileValidator(output_dir)
    
    # Run basic validation
    print("Running validation report...")
    report = validator.get_validation_report(config)
    
    # Display results
    print(f"\nValidation Results:")
    print(f"   Expected tiles: {report['expected']:,}")
    print(f"   Valid tiles: {report['valid']:,}")
    print(f"   Missing tiles: {report['missing']:,}")
    print(f"   Completion rate: {report['completion_rate']:.1f}%")
    
    if report['missing'] == 0:
        print("SUCCESS: All tiles are valid and complete!")
        return True
    else:
        print(f"WARNING: {report['missing']} tiles are missing or invalid")
        
        # Show first few missing tiles
        missing_tiles = report.get('missing_tiles', [])
        if missing_tiles:
            print(f"\nFirst 5 missing tiles:")
            for i, (z, x, y) in enumerate(missing_tiles[:5]):
                print(f"   {i+1}. Zoom {z}, X {x}, Y {y}")
            
            if len(missing_tiles) > 5:
                print(f"   ... and {len(missing_tiles) - 5} more")
        
        return False

def run_detailed_test(config_path: str = None):
    """Run detailed validation test"""
    
    # Use default config if not provided
    if not config_path:
        config_path = "config/cyprus.json"
    
    # Check if config exists
    config_file = Path(config_path)
    if not config_file.exists():
        print(f"ERROR: Config file not found: {config_path}")
        return False
    
    # Load config
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        print(f"ERROR: Error loading config: {e}")
        return False
    
    # Setup paths
    project_name = config['name']
    tiles_dir = Path("tiles")
    output_dir = tiles_dir / project_name
    
    print(f"Detailed validation test for: {project_name}")
    
    if not output_dir.exists():
        print(f"ERROR: Tiles directory does not exist: {output_dir}")
        return False
    
    # Initialize validator
    validator = TileValidator(output_dir)
    
    # Run detailed validation
    print("Running detailed validation scan...")
    report = validator.detailed_validation_report(config)
    
    if not report:
        print("ERROR: Failed to generate detailed report")
        return False
    
    # Display detailed results
    print(f"\nDetailed Validation Results:")
    print(f"   Project: {report['project_name']}")
    print(f"   Total expected: {report['total_expected']:,}")
    print(f"   Total valid: {report['total_valid']:,}")
    print(f"   Total missing: {report['total_missing']:,}")
    print(f"   Overall completion: {report['overall_completion']:.1f}%")
    
    # Show per-zoom statistics
    if 'zoom_stats' in report:
        print(f"\nPer-Zoom Statistics:")
        for zoom, stats in report['zoom_stats'].items():
            completion = stats['completion_rate']
            status = "OK" if completion == 100 else "WARN" if completion >= 90 else "ERROR"
            print(f"   {status} Zoom {zoom:2d}: {stats['valid']:4,}/{stats['expected']:4,} "
                  f"({completion:5.1f}%)")
    
    return report['total_missing'] == 0

def main():
    """Main function"""
    print("Tile Validation Test")
    print("=" * 50)
    
    # Parse command line arguments
    config_path = None
    detailed = False
    
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if arg == "--detailed":
                detailed = True
            elif not arg.startswith("--"):
                config_path = arg
    
    try:
        if detailed:
            success = run_detailed_test(config_path)
        else:
            success = test_validation(config_path)
        
        print(f"\n{'SUCCESS: Test completed successfully!' if success else 'WARNING: Test completed with issues'}")
        
    except KeyboardInterrupt:
        print("\nINFO: Test interrupted by user")
    except Exception as e:
        print(f"ERROR: Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
