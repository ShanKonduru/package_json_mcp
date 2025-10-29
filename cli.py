#!/usr/bin/env python3
"""
CLI wrapper for the MCP Project Packager.
Allows testing the functionality without MCP protocol.
"""

import argparse
import json
import sys
import os
from pathlib import Path

# Add src to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

try:
    from mcp_server import ProjectPackager
except ImportError as e:
    print(f"Error importing ProjectPackager: {e}")
    print(f"Current directory: {current_dir}")
    print(f"Src directory: {src_dir}")
    print(f"Python path: {sys.path}")
    sys.exit(1)


def export_command(args):
    """Handle export command."""
    packager = ProjectPackager()
    
    try:
        result = packager.export_project(args.project_path, args.include_hidden, args.use_default_ignores)
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"Project exported to: {args.output}")
        else:
            print(json.dumps(result, indent=2))
            
        metadata = result['metadata']
        print(f"\nSummary:")
        print(f"- Project: {metadata['project_name']}")
        print(f"- Files: {len(result['files'])}")
        print(f"- Has .gitignore: {metadata['has_gitignore']}")
        print(f"- Using default ignores: {metadata['use_default_ignores']}")
        print(f"- Including hidden files: {metadata['include_hidden']}")
        print(f"- Timestamp: {metadata['export_timestamp']}")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    return 0


def import_command(args):
    """Handle import command."""
    packager = ProjectPackager()
    
    try:
        # Read JSON data
        if args.json_file:
            with open(args.json_file, 'r') as f:
                json_data = json.load(f)
        else:
            json_data = json.loads(args.json_data)
        
        result = packager.import_project(json_data, args.target_path, args.overwrite)
        
        print(f"Import completed successfully!")
        print(f"- Target: {args.target_path}")
        print(f"- Created files: {result['created_files']}")
        print(f"- Created directories: {result['created_directories']}")
        print(f"- Skipped files: {result['skipped_files']}")
        
        if result['errors']:
            print(f"- Errors: {len(result['errors'])}")
            for error in result['errors']:
                print(f"  * {error}")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="MCP Project Packager CLI")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export project to JSON')
    export_parser.add_argument('project_path', help='Path to project directory')
    export_parser.add_argument('-o', '--output', help='Output JSON file path')
    export_parser.add_argument('--include-hidden', action='store_true',
                             help='Include hidden files and directories')
    export_parser.add_argument('--no-default-ignores', action='store_true',
                             help='Disable default ignore patterns (will package everything if no .gitignore)')
    export_parser.add_argument('--use-default-ignores', action='store_true', default=True,
                             help='Use default ignore patterns (default: true)')
    export_parser.set_defaults(use_default_ignores=True)
    
    # Import command
    import_parser = subparsers.add_parser('import', help='Import project from JSON')
    import_parser.add_argument('target_path', help='Target directory for import')
    
    # JSON input options (mutually exclusive)
    json_group = import_parser.add_mutually_exclusive_group(required=True)
    json_group.add_argument('-f', '--json-file', help='JSON file to import from')
    json_group.add_argument('-d', '--json-data', help='JSON data string')
    
    import_parser.add_argument('--overwrite', action='store_true',
                             help='Overwrite existing files')
    
    args = parser.parse_args()
    
    # Handle the no-default-ignores flag
    if hasattr(args, 'no_default_ignores') and args.no_default_ignores:
        args.use_default_ignores = False
    
    if args.command == 'export':
        return export_command(args)
    elif args.command == 'import':
        return import_command(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())