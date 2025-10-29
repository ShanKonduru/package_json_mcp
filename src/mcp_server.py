#!/usr/bin/env python3
"""
MCP Server for Project Packaging and Extraction

This server provides two main services:
1. export_project: Exports project structure to JSON (respecting .gitignore)
2. import_project: Imports/extracts project structure from JSON
"""

import json
import os
import base64
import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import mcp.types as types
from mcp.server import Server
from mcp.server.stdio import stdio_server
import argparse
import sys

try:
    from gitignore_parser import parse_gitignore
except ImportError:
    # Fallback implementation if gitignore_parser is not available
    def parse_gitignore(gitignore_path):
        """Fallback gitignore parser"""
        try:
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                patterns = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            def matches(file_path):
                for pattern in patterns:
                    if pattern in file_path or file_path.endswith(pattern):
                        return True
                return False
            return matches
        except FileNotFoundError:
            return lambda x: False


class ProjectPackager:
    """Handles project packaging and extraction operations."""
    
    def __init__(self):
        self.default_ignore_patterns = [
            '.git/', '__pycache__/', '*.pyc', '.pytest_cache/',
            'node_modules/', '.vscode/', '.idea/', '*.log',
            '.env', '.DS_Store', 'Thumbs.db', '*.tmp'
        ]
    
    def _should_ignore(self, path: Path, gitignore_matcher=None, use_default_ignores: bool = True) -> bool:
        """Check if a path should be ignored based on gitignore and default patterns."""
        path_str = str(path)
        
        # Check gitignore first
        if gitignore_matcher and gitignore_matcher(path_str):
            return True
        
        # Check default patterns only if enabled
        if use_default_ignores:
            for pattern in self.default_ignore_patterns:
                if pattern.endswith('/'):
                    if pattern[:-1] in path.parts:
                        return True
                elif pattern.startswith('*'):
                    if path_str.endswith(pattern[1:]):
                        return True
                elif pattern in path_str:
                    return True
        
        return False
    
    def _read_file_content(self, file_path: Path) -> Dict[str, Any]:
        """Read file content and return as base64 if binary, text if readable."""
        try:
            # Try to read as text first
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                return {
                    'type': 'text',
                    'content': content,
                    'encoding': 'utf-8'
                }
        except (UnicodeDecodeError, UnicodeError):
            # If text reading fails, read as binary
            with open(file_path, 'rb') as f:
                content = f.read()
                return {
                    'type': 'binary',
                    'content': base64.b64encode(content).decode('ascii'),
                    'encoding': 'base64'
                }
    
    def export_project(self, project_path: str, include_hidden: bool = False, use_default_ignores: bool = True) -> Dict[str, Any]:
        """
        Export project structure to JSON format.
        
        Args:
            project_path: Path to the project directory
            include_hidden: Whether to include hidden files/directories
            use_default_ignores: Whether to apply default ignore patterns when no .gitignore exists
            
        Returns:
            Dictionary containing the complete project structure
        """
        project_path = Path(project_path).resolve()
        
        if not project_path.exists():
            raise FileNotFoundError(f"Project path does not exist: {project_path}")
        
        if not project_path.is_dir():
            raise ValueError(f"Project path is not a directory: {project_path}")
        
        # Setup gitignore matcher
        gitignore_path = project_path / '.gitignore'
        gitignore_matcher = None
        has_gitignore = gitignore_path.exists()
        
        if has_gitignore:
            gitignore_matcher = parse_gitignore(str(gitignore_path))
        
        project_data = {
            'metadata': {
                'export_timestamp': asyncio.get_event_loop().time(),
                'project_name': project_path.name,
                'project_path': str(project_path),
                'include_hidden': include_hidden,
                'use_default_ignores': use_default_ignores,
                'has_gitignore': has_gitignore
            },
            'structure': {},
            'files': {}
        }
        
        def scan_directory(current_path: Path, relative_path: str = ""):
            """Recursively scan directory structure."""
            items = []
            
            try:
                for item in current_path.iterdir():
                    # Skip hidden files unless requested
                    if not include_hidden and item.name.startswith('.') and item.name not in ['.gitignore', '.gitkeep']:
                        continue
                    
                    item_relative = os.path.join(relative_path, item.name) if relative_path else item.name
                    
                    # Check if should be ignored
                    if self._should_ignore(item, gitignore_matcher, use_default_ignores):
                        continue
                    
                    if item.is_file():
                        # Store file information
                        file_info = {
                            'name': item.name,
                            'path': item_relative,
                            'size': item.stat().st_size,
                            'modified': item.stat().st_mtime,
                            'type': 'file'
                        }
                        
                        # Read file content
                        try:
                            content_data = self._read_file_content(item)
                            file_info.update(content_data)
                            project_data['files'][item_relative] = file_info
                        except Exception as e:
                            file_info['error'] = str(e)
                            file_info['type'] = 'error'
                            project_data['files'][item_relative] = file_info
                        
                        items.append(file_info)
                        
                    elif item.is_dir():
                        # Recursively scan subdirectory
                        dir_info = {
                            'name': item.name,
                            'path': item_relative,
                            'type': 'directory',
                            'children': scan_directory(item, item_relative)
                        }
                        items.append(dir_info)
            
            except PermissionError as e:
                print(f"Permission denied accessing {current_path}: {e}")
            
            return items
        
        project_data['structure'] = scan_directory(project_path)
        
        return project_data
    
    def import_project(self, json_data: Union[str, Dict], target_path: str, overwrite: bool = False) -> Dict[str, Any]:
        """
        Import/extract project structure from JSON.
        
        Args:
            json_data: JSON string or dictionary containing project data
            target_path: Path where to extract the project
            overwrite: Whether to overwrite existing files
            
        Returns:
            Dictionary with import results
        """
        if isinstance(json_data, str):
            try:
                data = json.loads(json_data)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON data: {e}")
        else:
            data = json_data
        
        target_path = Path(target_path).resolve()
        
        # Create target directory if it doesn't exist
        target_path.mkdir(parents=True, exist_ok=True)
        
        results = {
            'created_files': 0,
            'created_directories': 0,
            'skipped_files': 0,
            'errors': []
        }
        
        # Extract files
        for file_path, file_info in data.get('files', {}).items():
            full_path = target_path / file_path
            
            # Create parent directories
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Check if file exists and overwrite setting
            if full_path.exists() and not overwrite:
                results['skipped_files'] += 1
                continue
            
            try:
                if file_info.get('type') == 'text':
                    # Write text file
                    with open(full_path, 'w', encoding=file_info.get('encoding', 'utf-8')) as f:
                        f.write(file_info['content'])
                
                elif file_info.get('type') == 'binary':
                    # Write binary file
                    content = base64.b64decode(file_info['content'])
                    with open(full_path, 'wb') as f:
                        f.write(content)
                
                elif file_info.get('type') == 'error':
                    results['errors'].append(f"Skipped {file_path}: {file_info.get('error', 'Unknown error')}")
                    continue
                
                results['created_files'] += 1
                
            except Exception as e:
                results['errors'].append(f"Error creating {file_path}: {e}")
        
        return results


# Initialize the MCP server
server = Server("project-packager")

# Initialize the packager
packager = ProjectPackager()


@server.list_tools()
async def list_tools() -> List[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="export_project",
            description="Export a project directory structure to JSON format, respecting .gitignore rules",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Path to the project directory to export"
                    },
                    "include_hidden": {
                        "type": "boolean",
                        "description": "Whether to include hidden files and directories (default: false)",
                        "default": False
                    },
                    "use_default_ignores": {
                        "type": "boolean",
                        "description": "Whether to apply default ignore patterns when no .gitignore exists (default: true)",
                        "default": True
                    }
                },
                "required": ["project_path"]
            }
        ),
        types.Tool(
            name="import_project",
            description="Import/extract a project structure from JSON data to a target directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "json_data": {
                        "type": "string",
                        "description": "JSON string containing the project structure data"
                    },
                    "target_path": {
                        "type": "string",
                        "description": "Path where to extract/import the project"
                    },
                    "overwrite": {
                        "type": "boolean",
                        "description": "Whether to overwrite existing files (default: false)",
                        "default": False
                    }
                },
                "required": ["json_data", "target_path"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle tool calls."""
    
    if name == "export_project":
        try:
            project_path = arguments["project_path"]
            include_hidden = arguments.get("include_hidden", False)
            use_default_ignores = arguments.get("use_default_ignores", True)
            
            result = packager.export_project(project_path, include_hidden, use_default_ignores)
            
            metadata = result['metadata']
            status_info = f"Successfully exported project from {project_path}\n"
            status_info += f"Found {len(result['files'])} files\n"
            status_info += f"Has .gitignore: {metadata['has_gitignore']}\n"
            status_info += f"Using default ignores: {metadata['use_default_ignores']}\n"
            status_info += f"Including hidden files: {metadata['include_hidden']}\n"
            
            return [
                types.TextContent(
                    type="text",
                    text=status_info + f"Project data:\n{json.dumps(result, indent=2)}"
                )
            ]
            
        except Exception as e:
            return [
                types.TextContent(
                    type="text",
                    text=f"Error exporting project: {str(e)}"
                )
            ]
    
    elif name == "import_project":
        try:
            json_data = arguments["json_data"]
            target_path = arguments["target_path"]
            overwrite = arguments.get("overwrite", False)
            
            result = packager.import_project(json_data, target_path, overwrite)
            
            return [
                types.TextContent(
                    type="text",
                    text=f"Successfully imported project to {target_path}\n" +
                         f"Created {result['created_files']} files\n" +
                         f"Created {result['created_directories']} directories\n" +
                         f"Skipped {result['skipped_files']} existing files\n" +
                         (f"Errors: {len(result['errors'])}\n" + "\n".join(result['errors']) if result['errors'] else "No errors")
                )
            ]
            
        except Exception as e:
            return [
                types.TextContent(
                    type="text",
                    text=f"Error importing project: {str(e)}"
                )
            ]
    
    else:
        return [
            types.TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )
        ]


async def main():
    """Main entry point for the MCP server."""
    parser = argparse.ArgumentParser(description="Project Packager MCP Server")
    parser.add_argument("--port", type=int, help="Port to run server on")
    args = parser.parse_args()
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())