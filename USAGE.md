# MCP Server Usage Examples

## Quick Start

1. **Complete Setup**: Run `000_complete_setup.bat` to set everything up
2. **Run MCP Server**: Run `006_run_mcp_server.bat` to start the server
3. **Test CLI**: Run `007_run_cli.bat` to see CLI options
4. **Demo**: Run `009_demo.bat` to see a working example

## CLI Usage Examples

### Export a project to JSON:
```bash
python cli.py export . -o my_project.json
```

### Export including hidden files:
```bash
python cli.py export . -o my_project.json --include-hidden
```

### Import project from JSON:
```bash
python cli.py import ./restored_project -f my_project.json
```

### Import with overwrite:
```bash
python cli.py import ./restored_project -f my_project.json --overwrite
```

## MCP Integration

### With GitHub Copilot:

1. Start the MCP server: `006_run_mcp_server.bat`
2. Configure your MCP client to connect to the server
3. Use natural language commands like:
   - "Export this project to JSON"
   - "Import the project structure from this JSON"

### Available MCP Tools:

1. **export_project**: Exports current directory structure to JSON
2. **import_project**: Imports project structure from JSON to target directory

## Batch File Reference

- `000_init.bat` - Initialize git repository
- `001_env.bat` - Create virtual environment
- `002_activate.bat` - Activate virtual environment
- `003_setup.bat` - Install dependencies
- `004_run.bat` - Interactive menu to run different components
- `005_run_test.bat` - Run pytest tests
- `005_run_code_cov.bat` - Run tests with coverage
- `006_run_mcp_server.bat` - Start MCP server
- `007_run_cli.bat` - Run CLI tool
- `008_deactivate.bat` - Deactivate virtual environment
- `009_demo.bat` - Run demonstration
- `000_complete_setup.bat` - Complete setup process

## Project Structure After Setup

```
package_json_mcp/
├── src/
│   └── mcp_server.py          # Main MCP server implementation
├── tests/
│   └── test_mcp_server.py     # Test suite
├── cli.py                     # Command-line interface
├── main.py                    # Original main application
├── requirements.txt           # Python dependencies
├── mcp_config.json           # MCP server configuration
├── README.md                 # Documentation
└── *.bat                     # Batch files for easy execution
```