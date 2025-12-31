# UV Setup Guide for Babblr

This guide covers setting up the Babblr project using `uv`, a fast Python package and project manager.

## What is uv?

`uv` is an extremely fast Python package installer and resolver written in Rust. It's designed as a drop-in replacement for pip, pip-tools, and virtualenv, but significantly faster.

## Installing uv

### macOS and Linux

```bash
# Using curl
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or using pip
pip install uv
```

### Windows

```powershell
# Using PowerShell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or using pip
pip install uv
```

### Verify Installation

```bash
uv --version
```

## Updating uv

Keep uv up to date to get the latest features and performance improvements:

```bash
# Self-update uv
uv self update

# Or if installed via pip
pip install --upgrade uv
```

## Setting Up Babblr with uv

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment with uv:
```bash
# uv automatically creates and manages virtual environments
uv venv
```

3. Install dependencies:
```bash
# Install all dependencies from pyproject.toml
uv pip install -e .

# Or install with dev dependencies
uv pip install -e ".[dev]"
```

4. Create `.env` file:
```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### Running the Backend

With uv, you can run the backend using the installed script:

```bash
# Activate the virtual environment (optional with uv)
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate  # On Windows

# Run using the installed script
babblr-backend

# Or run directly with uv
uv run python -m app.main
```

### Running Tests

```bash
# Run unit tests
uv run pytest tests/test_unit.py -v

# Run integration tests (requires backend running)
uv run pytest tests/test_integration.py -v

# Run all tests
uv run pytest tests/ -v
```

## Frontend Setup

The frontend still uses npm for Node.js dependencies:

```bash
cd frontend
npm install
npm run electron:dev
```

## Why Use uv?

1. **Speed**: 10-100x faster than pip
2. **Reliability**: Better dependency resolution
3. **Modern**: Built with Rust for performance
4. **Compatible**: Drop-in replacement for pip
5. **Lock files**: Automatic lock file generation (uv.lock)

## Common uv Commands

```bash
# Install package
uv pip install package-name

# Install from pyproject.toml
uv pip install -e .

# Install with extras
uv pip install -e ".[dev]"

# Update all packages
uv pip install --upgrade -e .

# Sync exact versions from lock file
uv pip sync

# Show installed packages
uv pip list

# Create requirements file
uv pip freeze > requirements.txt

# Run Python with uv
uv run python script.py

# Run pytest with uv
uv run pytest

# Update uv itself
uv self update
```

## Troubleshooting

### uv not found after installation

Make sure uv is in your PATH. The installer adds it to your shell configuration, but you may need to restart your terminal or run:

```bash
source ~/.bashrc  # or ~/.zshrc on macOS
```

### Permission errors

If you get permission errors, don't use `sudo`. Instead, use the user installation method:

```bash
pip install --user uv
```

### Virtual environment issues

If you have issues with the virtual environment:

```bash
# Remove existing venv
rm -rf .venv

# Recreate with uv
uv venv

# Reinstall dependencies
uv pip install -e ".[dev]"
```

## Migration from pip

If you're migrating from pip:

1. Your existing `requirements.txt` works with uv
2. `pyproject.toml` is the preferred way (already set up)
3. Replace `pip` commands with `uv pip`
4. Virtual environments work the same way

## Additional Resources

- [uv Documentation](https://github.com/astral-sh/uv)
- [uv Installation Guide](https://github.com/astral-sh/uv#installation)
- [Python Packaging with uv](https://packaging.python.org/)

## Quick Reference

| Task | pip Command | uv Command |
|------|-------------|------------|
| Install package | `pip install pkg` | `uv pip install pkg` |
| Install from pyproject.toml | `pip install -e .` | `uv pip install -e .` |
| Install dev deps | `pip install -e ".[dev]"` | `uv pip install -e ".[dev]"` |
| Create venv | `python -m venv venv` | `uv venv` |
| Update package | `pip install --upgrade pkg` | `uv pip install --upgrade pkg` |
| List packages | `pip list` | `uv pip list` |
| Freeze deps | `pip freeze` | `uv pip freeze` |
| Run script | `python script.py` | `uv run python script.py` |

## Notes

- The `backend/pyproject.toml` file is the single source of truth for dependencies
- `requirements.txt` is kept for backward compatibility but can be removed
- uv automatically manages virtual environments in `.venv/`
- Lock files (`uv.lock`) ensure reproducible installs (coming in future uv versions)
