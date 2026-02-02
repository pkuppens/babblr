# Deployment Requirements

## Purpose

Deployment and distribution requirements.

## Distribution

### Electron Packaged Apps
- **macOS**: DMG installer
- **Windows**: EXE installer
- **Linux**: AppImage

### GitHub Releases
- Tagged releases (v1.0.0, v2.0.0)
- Release notes (changelog)
- Download links for all platforms

## Installation Prerequisites

- **Python**: 3.12+ (3.13 compatible)
- **Node.js**: 22+ LTS
- **uv**: Fast Python package manager

## Update Strategy

### Current (Manual)
- User downloads new release
- Runs installer
- Migrations handled automatically

### Future (Auto-Update)
- Electron auto-updater
- Background downloads
- Prompt to restart

## Deployment Environments

- **Development**: Local machine, Docker Compose
- **CI/CD**: GitHub Actions
- **Production**: User's local machine

See [docker/README.md](../../../docker/README.md) for Docker deployment.

---

**Version**: 1.0.0
**Last Updated**: 2026-02-02
