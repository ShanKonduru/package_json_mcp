#!/usr/bin/env python3
"""
Test script for the MCP Project Packager server.
"""

import asyncio
import json
import tempfile
import os
from pathlib import Path
import sys

# Add src to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
src_dir = os.path.join(parent_dir, 'src')
sys.path.insert(0, src_dir)

try:
    from mcp_server import ProjectPackager
except ImportError as e:
    print(f"Error importing ProjectPackager: {e}")
    print(f"Current directory: {current_dir}")
    print(f"Parent directory: {parent_dir}")
    print(f"Src directory: {src_dir}")
    print(f"Python path: {sys.path}")
    sys.exit(1)


async def test_export_import():
    """Test the export and import functionality."""
    packager = ProjectPackager()
    
    # Create a temporary test project
    with tempfile.TemporaryDirectory() as temp_dir:
        test_project = Path(temp_dir) / "test_project"
        test_project.mkdir()
        
        # Create some test files
        (test_project / "README.md").write_text("# Test Project\nThis is a test project.")
        (test_project / "main.py").write_text("print('Hello, World!')")
        
        # Create a subdirectory with files
        sub_dir = test_project / "src"
        sub_dir.mkdir()
        (sub_dir / "__init__.py").write_text("")
        (sub_dir / "utils.py").write_text("def helper_function():\n    return 'helper'")
        
        # Create a .gitignore file
        (test_project / ".gitignore").write_text("*.pyc\n__pycache__/\n.env")
        
        print(f"Created test project at: {test_project}")
        
        # Test export
        print("\n=== Testing Export ===")
        try:
            exported_data = packager.export_project(str(test_project))
            print(f"Export successful!")
            print(f"Found {len(exported_data['files'])} files")
            print("Files:", list(exported_data['files'].keys()))
            
            # Save exported data to file for inspection
            export_file = Path(temp_dir) / "exported_project.json"
            with open(export_file, 'w') as f:
                json.dump(exported_data, f, indent=2)
            print(f"Exported data saved to: {export_file}")
            
        except Exception as e:
            print(f"Export failed: {e}")
            return
        
        # Test import
        print("\n=== Testing Import ===")
        import_dir = Path(temp_dir) / "imported_project"
        
        try:
            result = packager.import_project(exported_data, str(import_dir))
            print(f"Import successful!")
            print(f"Created {result['created_files']} files")
            print(f"Created {result['created_directories']} directories")
            
            # Verify imported files
            print("\n=== Verifying Import ===")
            for file_path in exported_data['files'].keys():
                imported_file = import_dir / file_path
                if imported_file.exists():
                    print(f"✓ {file_path} imported successfully")
                else:
                    print(f"✗ {file_path} missing after import")
            
        except Exception as e:
            print(f"Import failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_export_import())