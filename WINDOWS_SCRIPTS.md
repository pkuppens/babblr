# Windows Scripts Guide

This project includes Windows CMD/batch file versions of all setup and run scripts for Windows users.

## Available Scripts

### Setup Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `setup.bat` | Full project setup (backend + frontend) | Run from project root |
| `backend/setup-venv.bat` | Backend virtual environment setup only | Run from `backend/` directory |

### Run Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `run-backend.bat` | Start backend server | Run from project root |
| `run-frontend.bat` | Start frontend in dev mode | Run from project root |

## Quick Start (Windows)

### Initial Setup

```cmd
REM Clone repository
git clone https://github.com/pkuppens/babblr.git
cd babblr

REM Run setup (installs uv, creates venv, installs dependencies)
setup.bat
```

### Running the Application

**Terminal 1 - Backend:**
```cmd
run-backend.bat
```

**Terminal 2 - Frontend:**
```cmd
run-frontend.bat
```

## Script Details

### setup.bat

Full project setup script that:
- Checks for Python 3.12+ and Node.js 22+
- Installs uv if not present (using PowerShell installer)
- Creates `backend/.venv` virtual environment
- Installs backend dependencies
- Installs frontend dependencies
- Creates `.env` file from example

**Usage:**
```cmd
REM From project root
setup.bat
```

### run-backend.bat

Backend startup script that:
- Changes to `backend/` directory
- Unsets conflicting VIRTUAL_ENV variables
- Creates `.venv` if it doesn't exist
- Uses `backend/.venv` explicitly
- Loads `backend/.env`
- Runs backend using uv

**Usage:**
```cmd
REM From project root
run-backend.bat
```

### run-frontend.bat

Frontend startup script that:
- Changes to `frontend/` directory
- Runs Electron in development mode

**Usage:**
```cmd
REM From project root
run-frontend.bat
```

### backend/setup-venv.bat

Backend virtual environment setup script that:
- Verifies it's run from `backend/` directory
- Removes existing `.venv` if present
- Creates fresh virtual environment
- Installs all dependencies (including dev)
- Verifies installation

**Usage:**
```cmd
cd backend
setup-venv.bat
```

## Comparison: Bash vs Windows

| Task | Linux/macOS | Windows |
|------|-------------|---------|
| Full setup | `./setup.sh` | `setup.bat` |
| Backend venv only | `cd backend && ./setup-venv.sh` | `cd backend && setup-venv.bat` |
| Run backend | `./run-backend.sh` | `run-backend.bat` |
| Run frontend | `./run-frontend.sh` | `run-frontend.bat` |

## Notes

- All Windows scripts use CMD batch syntax (`.bat` files)
- Scripts automatically handle path differences (backslashes vs forward slashes)
- Virtual environment is always created in `backend/.venv` (not root)
- Scripts include error handling and user-friendly messages
- All scripts pause at the end so you can see any error messages

## Troubleshooting

### "uv is not recognized"

The setup script will try to install uv automatically. If it fails:
1. Install manually: `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`
2. Restart your terminal
3. Run setup again

### "Cannot access backend directory"

Make sure you're running the script from the project root directory where `backend/` folder exists.

### Scripts close immediately

If a script closes before you can read the output:
1. Run from Command Prompt (not double-clicking)
2. Or add `pause` at the end of the script (already included in most scripts)

## See Also

- [QUICKSTART.md](QUICKSTART.md) - Quick start guide with platform-specific instructions
- [UV_SETUP.md](UV_SETUP.md) - Detailed uv usage guide
- [VIRTUAL_ENVIRONMENT_SETUP.md](VIRTUAL_ENVIRONMENT_SETUP.md) - Virtual environment setup guide

