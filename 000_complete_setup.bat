@echo off
echo ==========================================
echo MCP Project Packager - Complete Setup
echo ==========================================

echo Step 1: Creating virtual environment...
call 001_env.bat

echo.
echo Step 2: Activating virtual environment...
call 002_activate.bat

echo.
echo Step 3: Installing dependencies...
call 003_setup.bat

echo.
echo Setup complete! You can now:
echo - Run 004_run.bat to choose what to execute
echo - Run 006_run_mcp_server.bat to start the MCP server
echo - Run 007_run_cli.bat to use the CLI tool
echo - Run 009_demo.bat to see a demonstration
echo - Run 005_run_test.bat to run tests

echo.
echo MCP Server is ready for integration with GitHub Copilot or other MCP-compatible tools!