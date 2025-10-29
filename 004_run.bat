@echo off
echo Choose what to run:
echo 1. Main application (main.py)
echo 2. MCP Server
echo 3. CLI Tool
echo 4. Test MCP functionality
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    echo Running main application...
    python main.py
) else if "%choice%"=="2" (
    echo Starting MCP Server...
    python src\mcp_server.py
) else if "%choice%"=="3" (
    echo Running CLI tool...
    python cli.py --help
) else if "%choice%"=="4" (
    echo Testing MCP functionality...
    python tests\test_mcp_server.py
) else (
    echo Invalid choice. Running main application by default...
    python main.py
)
