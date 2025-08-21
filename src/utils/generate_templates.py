#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Template Generator CLI for OSM Tile Generator

Command-line interface for generating and managing configuration templates.
"""

import sys
import logging
from pathlib import Path
from typing import List, Optional

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from utils.template_manager import TemplateManager

# Windows encoding fix
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)

def setup_logging(verbose: bool = False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(levelname)s: %(message)s',
        handlers=[logging.StreamHandler()]
    )

def print_header():
    """Print application header"""
    print("=" * 60)
    print("     OSM TILE GENERATOR")
    print("     Template Generator")
    print("=" * 60)
    print()

def print_usage():
    """Print usage information"""
    print("Usage: python generate_templates.py [options]")
    print()
    print("Options:")
    print("  --template [name]     Create template file (default: template.json)")
    print("  --samples [list]      Create sample configurations")
    print("  --all-samples         Create all sample configurations")
    print("  --list                List existing configuration files")
    print("  --info <file>         Show information about a config file")
    print("  --verbose             Enable verbose output")
    print("  --help                Show this help message")
    print()
    print("Examples:")
    print("  python generate_templates.py --template")
    print("  python generate_templates.py --template my_template")
    print("  python generate_templates.py --samples cyprus_sample turkey_sample")
    print("  python generate_templates.py --all-samples")
    print("  python generate_templates.py --list")
    print("  python generate_templates.py --info cyprus.json")

def create_template(manager: TemplateManager, template_name: Optional[str] = None) -> bool:
    """Create a template file"""
    print("Creating template configuration file...")
    
    filename = manager.create_template_file(template_name)
    
    if filename:
        print(f"✅ Template file created: {filename}")
        print("This file contains the configuration schema structure.")
        print("You can copy and modify this template for your projects.")
        return True
    else:
        print("❌ Failed to create template file.")
        return False

def create_samples(manager: TemplateManager, sample_names: List[str] = None) -> bool:
    """Create sample configuration files"""
    if sample_names is None:
        print("Creating all sample configuration files...")
        sample_names = list(manager.get_sample_configs().keys())
    else:
        print(f"Creating sample configurations: {', '.join(sample_names)}")
    
    created_count = manager.create_sample_configs(sample_names)
    
    if created_count > 0:
        print(f"✅ Created {created_count} sample configuration(s)")
        return True
    else:
        print("❌ No sample configurations were created")
        return False

def list_configs(manager: TemplateManager):
    """List existing configuration files"""
    templates = manager.list_templates()
    
    if not templates:
        print("No configuration files found in config directory")
        return
    
    print(f"Configuration files in {manager.config_dir}:")
    print("-" * 40)
    
    for template in templates:
        info = manager.get_config_info(template)
        if info:
            print(f"📄 {template}")
            if info.get('name'):
                print(f"   Name: {info['name']}")
            if info.get('description'):
                print(f"   Description: {info['description']}")
            if info.get('zoom_range'):
                print(f"   Zoom Range: {info['zoom_range']}")
            print()
        else:
            print(f"❌ {template} (invalid)")

def show_config_info(manager: TemplateManager, filename: str):
    """Show detailed information about a configuration file"""
    info = manager.get_config_info(filename)
    
    if info is None:
        print(f"❌ Could not load configuration file: {filename}")
        return
    
    print(f"Configuration File Information:")
    print("=" * 40)
    print(f"Filename: {info['filename']}")
    print(f"Name: {info['name']}")
    print(f"Description: {info['description']}")
    print(f"Render Type: {info['render_type']}")
    print(f"Zoom Range: {info['zoom_range']}")
    if info['created_at']:
        print(f"Created: {info['created_at']}")

def interactive_mode(manager: TemplateManager):
    """Run in interactive mode"""
    print("Interactive Template Generator")
    print("Select an option:")
    print("1. Create empty template")
    print("2. Create all sample configurations")
    print("3. List existing configurations")
    print("4. Exit")
    print()
    
    try:
        choice = input("Enter your choice (1-4): ").strip()
        
        if choice == "1":
            name = input("Template name (leave empty for default): ").strip()
            create_template(manager, name if name else None)
        elif choice == "2":
            create_samples(manager)
        elif choice == "3":
            list_configs(manager)
        elif choice == "4":
            print("Goodbye!")
            return
        else:
            print("Invalid choice")
            
    except KeyboardInterrupt:
        print("\nOperation cancelled")

def main():
    """Main function"""
    args = sys.argv[1:]
    
    # Parse arguments
    verbose = '--verbose' in args or '-v' in args
    setup_logging(verbose)
    
    try:
        print_header()
        
        # Initialize template manager
        manager = TemplateManager()
        print(f"Config directory: {manager.config_dir}")
        print()
        
        # Handle command line arguments
        if '--help' in args or '-h' in args:
            print_usage()
            return 0
        
        elif '--list' in args:
            list_configs(manager)
            return 0
        
        elif '--info' in args:
            try:
                info_index = args.index('--info')
                if info_index + 1 < len(args):
                    filename = args[info_index + 1]
                    show_config_info(manager, filename)
                else:
                    print("Error: --info requires a filename")
                    return 1
            except ValueError:
                print("Error: Invalid --info usage")
                return 1
            return 0
        
        elif '--template' in args:
            try:
                template_index = args.index('--template')
                template_name = None
                if template_index + 1 < len(args) and not args[template_index + 1].startswith('--'):
                    template_name = args[template_index + 1]
                
                success = create_template(manager, template_name)
                return 0 if success else 1
            except ValueError:
                print("Error: Invalid --template usage")
                return 1
        
        elif '--all-samples' in args:
            success = create_samples(manager)
            return 0 if success else 1
        
        elif '--samples' in args:
            try:
                samples_index = args.index('--samples')
                sample_names = []
                
                # Collect sample names after --samples
                for i in range(samples_index + 1, len(args)):
                    if args[i].startswith('--'):
                        break
                    sample_names.append(args[i])
                
                if not sample_names:
                    print("Error: --samples requires at least one sample name")
                    return 1
                
                success = create_samples(manager, sample_names)
                return 0 if success else 1
            except ValueError:
                print("Error: Invalid --samples usage")
                return 1
        
        else:
            # No specific arguments, run interactive mode or default action
            if not args:
                # Default behavior: create template
                print("No arguments provided. Creating default template...")
                success = create_template(manager)
                return 0 if success else 1
            else:
                print("Unknown arguments. Use --help for usage information.")
                return 1
        
    except KeyboardInterrupt:
        print("\n⏹️ Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        return 1
    finally:
        # Keep window open on Windows
        if sys.platform == 'win32' and '--no-pause' not in args:
            input("\nPress Enter to exit...")

if __name__ == "__main__":
    sys.exit(main())
