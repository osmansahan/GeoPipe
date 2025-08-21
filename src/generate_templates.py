#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Template Generator Entry Point

Simple entry point for template generation within the src structure.
"""

import sys
from pathlib import Path
from utils.template_manager import TemplateManager

def print_header():
    """Print application header"""
    print("=" * 60)
    print("     OSM TILE GENERATOR")
    print("     Template Generator")
    print("=" * 60)
    print()

def main():
    """Main function for simple template generation"""
    try:
        print_header()
        
        # Initialize template manager
        manager = TemplateManager()
        print(f"Config directory: {manager.config_dir}")
        print()
        
        print("Creating template configuration file...")
        
        # Create template file
        filename = manager.create_template_file()
        
        print()
        print("=" * 60)
        print("GENERATION COMPLETE")
        print("=" * 60)
        
        if filename:
            print(f"✅ Template file created: {filename}")
            print("This file contains the configuration schema structure.")
            print("You can copy and modify this template for your projects.")
            print()
            print(f"📁 Template file location: config/{filename}")
            print("🖊️ Edit this file with your project-specific values!")
        else:
            print("❌ Failed to create template file.")
            return 1
        
        print("=" * 60)
        
        return 0
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1
    finally:
        # Keep window open on Windows
        if sys.platform == 'win32':
            input("\nPress Enter to exit...")

if __name__ == "__main__":
    sys.exit(main())
