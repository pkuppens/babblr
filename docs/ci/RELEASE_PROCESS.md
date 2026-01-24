# Release Process Guide

This guide explains how to create releases for Babblr using the automated release workflow.

## Overview

Babblr uses GitHub Actions to automate the release process:

1. Build backend and frontend artifacts
2. Generate artifact attestations for supply chain security
3. Create GitHub release with release notes
4. Attach artifacts to release

## Release Methods

### Method 1: Tag-based Release (Recommended)

Push a git tag to automatically trigger a release:

```bash
# Create and push a tag
git tag v1.0.0
git push origin v1.0.0
```

**Advantages**:
- Simple and automated
- Git tag provides permanent reference
- Clear version history in git

### Method 2: Manual Release

Manually trigger the release workflow:

1. Go to **Actions** tab → **Release** workflow
2. Click **Run workflow**
3. Select branch (usually `main`)
4. Enter version (e.g., `v1.0.0`)
5. Click **Run workflow**

**Advantages**:
- Control over timing
- Test release process
- Release from any branch (use with caution)

## Release Workflow

The release workflow runs these jobs:

### 1. Build Backend

Builds Python package artifacts:

**Outputs**:
- `babblr-*.whl` - Python wheel package
- `babblr-*.tar.gz` - Source distribution

**Location**: `backend-dist` artifact

### 2. Build Frontend

Builds Electron application for desktop:

**Outputs**:
- Platform-specific Electron app (e.g., `.dmg`, `.exe`, `.AppImage`)

**Location**: `frontend-dist` artifact

### 3. Generate Attestations

Creates cryptographic attestations for all artifacts:

**Purpose**:
- Prove who built the artifacts
- Prove when they were built
- Prove what source code was used
- Enable supply chain verification

**Technology**: GitHub's `actions/attest-build-provenance@v1`

### 4. Create GitHub Release

Creates release on GitHub with:

**Release notes**:
- Auto-generated from commits since last tag
- Lists all changes with commit hashes
- Includes installation instructions

**Artifacts**:
- Backend wheel and source distribution
- Frontend Electron application
- All artifacts have attestations attached

**Environment**: `production`
- Requires manual approval before release creation
- Set up in repo Settings → Environments

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):

**Format**: `vMAJOR.MINOR.PATCH`

- `MAJOR`: Breaking changes (e.g., `v2.0.0`)
- `MINOR`: New features, backwards compatible (e.g., `v1.1.0`)
- `PATCH`: Bug fixes, backwards compatible (e.g., `v1.0.1`)

**Examples**:
- `v1.0.0` - First stable release
- `v1.1.0` - Added new language support
- `v1.0.1` - Fixed bug in conversation save

## Pre-release Checklist

Before creating a release:

- [ ] All tests pass on `main` branch
- [ ] Security scans pass (no critical vulnerabilities)
- [ ] Documentation is up-to-date
- [ ] `CHANGELOG.md` updated (if exists)
- [ ] Version number determined (semantic versioning)
- [ ] Release notes drafted (what's new, what's fixed)

## Creating a Release (Step-by-Step)

### Step 1: Ensure Main Branch is Ready

```bash
# Make sure main is up-to-date
git checkout main
git pull origin main

# Verify tests pass locally
cd backend && uv run pytest tests/test_unit.py -v
cd frontend && npm run test
```

### Step 2: Create and Push Tag

```bash
# Create annotated tag with message
git tag -a v1.0.0 -m "Release version 1.0.0"

# Push tag to GitHub
git push origin v1.0.0
```

### Step 3: Monitor Workflow

1. Go to **Actions** tab
2. Find **Release** workflow run
3. Monitor build progress
4. Wait for jobs to complete

### Step 4: Approve Release

When prompted:

1. Review build artifacts
2. Check attestations generated
3. Approve release in **production** environment
4. Release will be created automatically

### Step 5: Verify Release

1. Go to **Releases** page
2. Verify release created with correct version
3. Check artifacts attached
4. Review release notes
5. Test download and installation

## Environment Setup

### Production Environment

Set up in repo Settings → Environments → New environment:

**Name**: `production`

**Protection rules**:
- Required reviewers: Add @pkuppens (or maintainer)
- Deployment branches: Limit to `main` branch only

**Purpose**:
- Manual approval gate before release creation
- Prevents accidental releases
- Ensures release quality

## Artifact Retention

**Release artifacts**: 90 days (configurable)
**PR artifacts**: 7 days (to save storage)

Configure in `vars.ARTIFACT_RETENTION_DAYS` (GitHub Actions variables).

## Release Notes

Release notes are auto-generated from commits:

**Format**:
```markdown
# Babblr v1.0.0

## Changes

- feat: add user authentication (#123)
- fix: resolve conversation save bug (#124)
- docs: update API documentation (#125)

## Artifacts

### Backend
- Python wheel package (.whl)
- Source distribution (.tar.gz)

### Frontend
- Electron application (platform-specific)

## Verification

All artifacts have been attested for supply chain security. View attestations in the GitHub UI.

## Installation

See [QUICKSTART.md](https://github.com/pkuppens/babblr/blob/main/QUICKSTART.md) for installation instructions.
```

## Viewing Attestations

Attestations prove artifact provenance:

1. Go to release page
2. Find artifact
3. Click **Attestations** badge
4. View build provenance details

**Includes**:
- Builder identity (GitHub Actions)
- Source repository and commit
- Workflow that built it
- Build timestamp

## Troubleshooting

### Release Workflow Fails at Build

**Symptom**: Backend or frontend build job fails

**Solutions**:
1. Check build logs for errors
2. Ensure dependencies are locked (`uv.lock`, `package-lock.json`)
3. Test build locally: `uv build` or `npm run electron:build`
4. Fix issue and create new tag

### Attestation Generation Fails

**Symptom**: `attest` job fails

**Solutions**:
1. Check if artifacts were created
2. Verify `id-token: write` permission set
3. Check GitHub status page for outages

### Release Creation Blocked

**Symptom**: Waiting for approval indefinitely

**Solutions**:
1. Check if production environment has reviewers configured
2. Notify reviewer (@pkuppens)
3. Check if reviewer has been added to repo

### Wrong Version in Release

**Symptom**: Release has wrong version number

**Solutions**:
1. Delete the release (not the tag)
2. Delete the tag: `git tag -d v1.0.0 && git push origin :refs/tags/v1.0.0`
3. Create correct tag
4. Re-run workflow

## Rolling Back a Release

If a release has issues:

### Option 1: Create Patch Release

```bash
# Fix the issue in main
git checkout main
# ... make fixes ...
git commit -m "fix: critical bug in v1.0.0"

# Create patch release
git tag v1.0.1
git push origin v1.0.1
```

### Option 2: Delete Release (Use with Caution)

1. Go to release page
2. Click **Delete** (three dots menu)
3. Confirm deletion
4. Delete tag: `git tag -d v1.0.0 && git push origin :refs/tags/v1.0.0`

**Warning**: Deleting releases can break existing installations. Use patch releases instead.

## Best Practices

### 1. Release from Main Branch

Always release from `main` branch:
- Ensures all tests pass
- Security scans completed
- Code review completed

### 2. Test Before Release

Run full test suite before creating release:
```bash
# Backend tests
cd backend && uv run pytest tests/ -v

# Frontend tests
cd frontend && npm run test

# Integration tests (if applicable)
cd backend && uv run pytest tests/test_integration.py -v
```

### 3. Write Good Release Notes

Manual release notes can be added:
1. Create release
2. Edit release notes
3. Add highlights, breaking changes, upgrade notes

### 4. Announce Releases

After release:
- Update documentation
- Notify users via appropriate channels
- Update installation guides

### 5. Monitor Post-Release

After release:
- Monitor for bug reports
- Check download statistics
- Gather user feedback

## Automation

### Scheduled Releases

To automate releases on schedule, add to workflow:

```yaml
on:
  schedule:
    - cron: '0 0 1 * *'  # First day of month
```

**Not recommended** unless you have:
- Excellent test coverage
- Automated changelog generation
- Semantic release tooling

### Release Candidates

For pre-releases, use tag format:

```bash
git tag v1.0.0-rc.1
git push origin v1.0.0-rc.1
```

Mark as pre-release in GitHub UI.

## Resources

- [Semantic Versioning](https://semver.org/)
- [GitHub Releases Documentation](https://docs.github.com/en/repositories/releasing-projects-on-github)
- [Artifact Attestations](https://docs.github.com/en/actions/security-guides/using-artifact-attestations)
- [GitHub Actions: workflow_dispatch](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#workflow_dispatch)
