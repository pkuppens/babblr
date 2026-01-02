@echo off
REM Setup script for backend virtual environment using uv (Windows)
REM This creates .venv in the backend directory (not root)

setlocal enabledelayedexpansion

echo Setting up backend virtual environment with uv
echo.

REM Check if we're in the backend directory
if not exist "pyproject.toml" (
    echo [ERROR] This script must be run from the backend directory
    echo    Run: cd backend ^&^& setup-venv.bat
    pause
    exit /b 1
)

REM Check if uv is available
where uv >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] uv is not installed
    echo    Install with: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('uv --version') do set UV_VERSION=%%i
echo [OK] uv found: %UV_VERSION%
echo.

REM Remove existing .venv if it exists
if exist ".venv" (
    echo [INFO] Removing existing .venv...
    rmdir /s /q .venv
    if %errorlevel% neq 0 (
        echo [WARNING] Could not remove existing .venv completely
    )
)

REM Create new virtual environment
echo [INFO] Creating virtual environment with uv...
uv venv
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create virtual environment
    pause
    exit /b 1
)

if not exist ".venv" (
    echo [ERROR] Failed to create virtual environment
    pause
    exit /b 1
)

echo [OK] Virtual environment created: %CD%\.venv
echo.

REM Install dependencies
echo [INFO] Installing dependencies from pyproject.toml...
uv pip install -e ".[dev]"
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo [OK] Dependencies installed
echo.

REM Verify installation
echo [INFO] Verifying installation...
uv run python -c "import fastapi; import whisper; print('[OK] Core dependencies verified')" 2>nul
if %errorlevel% equ 0 (
    echo [OK] Installation verified successfully
) else (
    echo [WARNING] Some dependencies may not be installed correctly
)

echo.
echo Setup complete!
echo.
echo Virtual environment location: %CD%\.venv
echo.
echo Next steps:
echo 1. Create .env file if needed: copy .env.example .env
echo 2. Add your ANTHROPIC_API_KEY to backend\.env
echo 3. Run backend: run-backend.bat (from project root)
echo.

pause

