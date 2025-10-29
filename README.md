# MCP Project Packager

A Model Context Protocol (MCP) server that provides project packaging and extraction services. This tool allows you to export entire project structures into JSON format (respecting .gitignore rules) and import them elsewhere.

## Features

- **Export Service**: Collects all files and folders in a project, respecting .gitignore specifications, and packages them into a structured JSON format
- **Import Service**: Takes JSON input and extracts/recreates the complete file structure in a target directory
- **Smart File Handling**: Automatically detects text vs binary files and encodes them appropriately
- **Gitignore Support**: Respects .gitignore rules to exclude unwanted files
- **Configurable**: Options for including/excluding hidden files and overwriting existing files

## Installation

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### As an MCP Server

The server can be integrated with any MCP-compatible LLM tool (like GitHub Copilot):

```bash
python src/mcp_server.py
```

### Available Tools

#### 1. export_project
Exports a project directory structure to JSON format.

**Parameters:**
- `project_path` (required): Path to the project directory to export
- `include_hidden` (optional): Whether to include hidden files and directories (default: false)

**Example:**
```json
{
  "name": "export_project",
  "arguments": {
    "project_path": "/path/to/your/project",
    "include_hidden": false
  }
}
```

#### 2. import_project
Imports/extracts a project structure from JSON data to a target directory.

**Parameters:**
- `json_data` (required): JSON string containing the project structure data
- `target_path` (required): Path where to extract/import the project
- `overwrite` (optional): Whether to overwrite existing files (default: false)

**Example:**
```json
{
  "name": "import_project",
  "arguments": {
    "json_data": "{\"metadata\":{...},\"files\":{...}}",
    "target_path": "/path/to/extract",
    "overwrite": false
  }
}
```

### Testing

Run the test suite to verify functionality:

```bash
python tests/test_mcp_server.py
```

## JSON Structure

The exported JSON contains:

```json
{
  "metadata": {
    "export_timestamp": 1635789123.456,
    "project_name": "my-project",
    "project_path": "/path/to/project",
    "include_hidden": false
  },
  "structure": [
    {
      "name": "README.md",
      "path": "README.md",
      "type": "file",
      "size": 1234,
      "modified": 1635789100.0
    }
  ],
  "files": {
    "README.md": {
      "name": "README.md",
      "path": "README.md",
      "size": 1234,
      "modified": 1635789100.0,
      "type": "text",
      "content": "# My Project\n...",
      "encoding": "utf-8"
    }
  }
}
```

## Integration with GitHub Copilot

To use this MCP server with GitHub Copilot or other MCP-compatible tools:

1. Start the MCP server
2. Configure your LLM tool to connect to the MCP server
3. Use the tools through natural language commands:
   - "Export the current project to JSON"
   - "Import this project structure to a new directory"

## Supported File Types

- **Text files**: Stored as UTF-8 text content
- **Binary files**: Encoded as base64 for safe JSON transport
- **Error handling**: Files that can't be read are logged with error information

## Default Ignore Patterns

In addition to .gitignore rules, these patterns are ignored by default:
- `.git/`, `__pycache__/`, `*.pyc`, `.pytest_cache/`
- `node_modules/`, `.vscode/`, `.idea/`, `*.log`
- `.env`, `.DS_Store`, `Thumbs.db`, `*.tmp`

## License

MIT License - see LICENSE file for details.

## Installation


1.  **Initialize git (Windows):**
    Run the `000_init.bat` file.

2.  **Create a virtual environment (Windows):**
    Run the `001_env.bat` file.

3.  **Activate the virtual environment (Windows):**
    Run the `002_activate.bat` file.

4.  **Install dependencies:**
    Run the `003_setup.bat` file. This will install all the packages listed in `requirements.txt`.

5.  **Deactivate the virtual environment (Windows):**
    Run the `008_deactivate.bat` file.

## Usage

1.  **Run the main application (Windows):**
    Run the `004_run.bat` file.

    [Provide instructions on how to use your application.]

## Batch Files (Windows)

This project includes the following batch files to help with common development tasks on Windows:

* `000_init.bat`: Initialized git and also usn and pwd config setup also done.
* `001_env.bat`: Creates a virtual environment named `venv`.
* `002_activate.bat`: Activates the `venv` virtual environment.
* `003_setup.bat`: Installs the Python packages listed in `requirements.txt` using `pip`.
* `004_run.bat`: Executes the main Python script (`main.py`).
* `005_run_test.bat`: Executes the pytest  scripts (`test_main.py`).
* `005_run_code_cov.bat`: Executes the code coverage pytest  scripts (`test_main.py`).
* `008_deactivate.bat`: Deactivates the currently active virtual environment.

## Contributing

[Explain how others can contribute to your project.]

## License

[Specify the project license, if any.]
