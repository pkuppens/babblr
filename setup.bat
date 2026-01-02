@echo off
REM Setup script for Babblr Language Learning App with uv (Windows)

echo Setting up Babblr Language Learning App with uv
echo.

REM Check prerequisites
echo Checking prerequisites...

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python 3 is not installed. Please install Python 3.12 or higher.
    exit /b 1
)

where node >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed. Please install Node.js 22 or higher.
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
echo [OK] Python %PYTHON_VERSION% found
echo [OK] Node.js %NODE_VERSION% found
echo.

REM Check if uv is installed
where uv >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] uv is not installed. Installing uv...
    echo.
    echo uv is a fast Python package installer and resolver.
    echo Installing via official installer...
    echo.
    
    REM Install uv using PowerShell
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    
    REM Add to PATH for current session
    set "PATH=%USERPROFILE%\.cargo\bin;%PATH%"
    
    REM Check if installation succeeded
    where uv >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install uv. Please install manually:
        echo    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
        echo    Or: pip install uv
        exit /b 1
    )
    
    echo [OK] uv installed successfully
) else (
    for /f "tokens=*" %%i in ('uv --version') do set UV_VERSION=%%i
    echo [OK] uv %UV_VERSION% found
    echo Updating uv to latest version...
    uv self update 2>nul || echo [WARNING] Could not auto-update uv (may need manual update)
)

echo.

REM Setup backend
echo [SETUP] Setting up backend with uv...
cd backend
if %errorlevel% neq 0 (
    echo [ERROR] Cannot access backend directory
    exit /b 1
)

REM Create virtual environment with uv
if not exist ".venv" (
    echo Creating Python virtual environment with uv...
    uv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment
        exit /b 1
    )
)

if not exist ".env" (
    echo Creating .env file from .env.example...
    if exist ".env.example" (
        copy /Y .env.example .env >nul
        echo [WARNING] Please add your ANTHROPIC_API_KEY to backend\.env before running the app
    )
)

echo Installing Python dependencies with uv...
uv pip install -e ".[dev]"
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install backend dependencies
    exit /b 1
)

echo [OK] Backend setup complete
echo.

REM Setup frontend
echo [SETUP] Setting up frontend...
cd ..\frontend
if %errorlevel% neq 0 (
    echo [ERROR] Cannot access frontend directory
    exit /b 1
)

echo Installing Node.js dependencies...
call npm install
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install frontend dependencies
    exit /b 1
)

echo [OK] Frontend setup complete
echo.

REM Done
echo Setup complete!
echo.
echo Next steps:
echo 1. Add your Anthropic API key to backend\.env
echo 2. Start the backend: run-backend.bat
echo 3. Start the frontend: run-frontend.bat
echo.
echo Documentation:
echo    - See UV_SETUP.md for detailed uv usage
echo    - See QUICKSTART.md for quick start guide
echo.
echo Note: Backend uses uv for fast package management (.venv)
echo Happy learning!

cd ..
pause

