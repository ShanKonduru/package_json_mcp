@echo off
echo ==========================================
echo MCP Project Packager Demo
echo ==========================================
echo.

echo Creating a test directory structure...
mkdir demo_test_project 2>nul
cd demo_test_project
echo print("Hello from demo project!") > main.py
echo # Demo Project > README.md
echo *.pyc > .gitignore
echo __pycache__/ >> .gitignore
mkdir src 2>nul
echo def helper(): return "help" > src\utils.py
cd ..

echo.
echo Step 1: Exporting the demo project to JSON...
python cli.py export demo_test_project -o demo_export.json

echo.
echo Step 2: Creating import target directory...
mkdir demo_imported 2>nul

echo.
echo Step 3: Importing the project from JSON...
python cli.py import demo_imported -f demo_export.json

echo.
echo Step 4: Comparing original and imported structures...
echo Original structure:
dir /b /s demo_test_project
echo.
echo Imported structure:
dir /b /s demo_imported

echo.
echo Demo completed! Check demo_export.json for the exported structure.
echo Clean up with: rmdir /s /q demo_test_project demo_imported & del demo_export.json