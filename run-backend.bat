@echo off
setlocal EnableExtensions EnableDelayedExpansion
REM Start backend server using uv (Windows)

REM Get script directory
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%"
set "BACKEND_DIR=%PROJECT_ROOT%backend"

REM Change to backend directory
pushd "%BACKEND_DIR%"
if %errorlevel% neq 0 (
    echo [ERROR] Cannot access backend directory: %BACKEND_DIR%
    goto :cleanup_fail
)

REM Unset VIRTUAL_ENV if it points to a different location (e.g., root .venv)
REM This ensures uv uses the backend\.venv instead
if defined VIRTUAL_ENV (
    set "CURRENT_VENV=%CD%\.venv"
    if not "%VIRTUAL_ENV%"=="%CURRENT_VENV%" (
        echo [INFO] Unsetting VIRTUAL_ENV to use backend\.venv
        set "VIRTUAL_ENV="
    )
)

REM Check if uv is available
where uv >nul 2>&1
if %errorlevel% equ 0 (
    echo [START] Starting Babblr backend with uv...
    echo    Working directory: %CD%
    echo    Virtual environment: %CD%\.venv
    
    REM Ensure .venv exists in backend directory
    if not exist ".venv" (
        echo [WARNING] Virtual environment not found. Creating .venv in backend directory...
        uv venv
        if %errorlevel% neq 0 (
            echo [ERROR] Failed to create virtual environment
            pause
            exit /b 1
        )
    )
    
    REM Set PYTHONPATH to backend directory
    set "PYTHONPATH=%CD%"
    
    REM Ensure .env is loaded from backend directory
    if exist ".env" (
        echo    Using .env from: %CD%\.env
    ) else (
        echo [WARNING] .env file not found in backend directory
    )
    
    REM Run using uv (preferred method)
    REM uv run automatically uses the .venv in the current directory
    uv run babblr-backend
) else (
    echo [WARNING] uv not found, falling back to standard Python...
    echo    For better performance, install uv: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    
    REM Fallback: manually activate venv if it exists
    if exist ".venv\Scripts\activate.bat" (
        call .venv\Scripts\activate.bat
    ) else if exist "venv\Scripts\activate.bat" (
        call venv\Scripts\activate.bat
    )
    
    set "PYTHONPATH=%CD%"
    cd app
    python main.py
)

:cleanup_ok
popd
pause
endlocal
exit /b 0

:cleanup_fail
popd
pause
endlocal
exit /b 1
