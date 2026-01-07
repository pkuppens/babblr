@echo off
REM Setup script for Babblr Language Learning App with uv (Windows)

echo Setting up Babblr Language Learning App with uv
echo.

REM Check prerequisites
echo Checking prerequisites...

REM Check for Python 3.12 specifically using py launcher
py -3.12 -V >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python 3.12 is not installed.
    echo.
    echo Install Python 3.12 using one of these methods:
    echo   winget install -e --id Python.Python.3.12
    echo   Or download from: https://www.python.org/downloads/
    echo.
    echo After installation, restart your terminal and run setup.bat again.
    exit /b 1
)

where node >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed.
    echo.
    echo Install Node.js 22+ using one of these methods:
    echo   winget install -e --id OpenJS.NodeJS.LTS
    echo   Or download from: https://nodejs.org/
    exit /b 1
)

for /f "tokens=*" %%i in ('py -3.12 -V') do set PYTHON_VERSION=%%i
for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
echo [OK] %PYTHON_VERSION% found
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

REM Create virtual environment with uv using Python 3.12
if not exist ".venv" (
    echo Creating Python 3.12 virtual environment with uv...
    uv venv --python 3.12
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment
        exit /b 1
    )
)

if not exist ".env" (
    echo Creating .env file from .env.example...
    if exist ".env.example" (
        copy /Y .env.example .env >nul
        echo [OK] Created .env with default settings (LLM_PROVIDER=ollama)
    )
)

echo Installing Python dependencies with uv...
uv pip install -e ".[dev]"
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install backend dependencies
    exit /b 1
)

REM Install pre-commit hooks (idempotent) if this is a git repo
where git >nul 2>&1
if %errorlevel% equ 0 (
    git rev-parse --is-inside-work-tree >nul 2>&1
    if %errorlevel% equ 0 (
        for /f "delims=" %%H in ('git rev-parse --git-path hooks 2^>nul') do set "GIT_HOOKS=%%H"
        if defined GIT_HOOKS (
            if not exist "%GIT_HOOKS%\pre-commit" (
                echo [SETUP] Installing pre-commit hooks...
                uv run pre-commit install 2>nul || echo [WARNING] Could not install pre-commit hooks
            ) else (
                echo [OK] pre-commit hooks already installed
            )
        )
    )
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
echo 1. Review backend\.env for LLM provider settings:
echo    - Default: LLM_PROVIDER=ollama (requires Ollama running locally)
echo    - Optional: Set ANTHROPIC_API_KEY for Claude
echo    - Optional: Set GOOGLE_API_KEY for Gemini
echo 2. Start the backend: run-backend.bat
echo 3. Start the frontend: run-frontend.bat
echo.
echo Documentation:
echo    - See ENVIRONMENT.md for LLM provider configuration
echo    - See QUICKSTART.md for quick start guide
echo.
echo Happy learning!

cd ..
pause

