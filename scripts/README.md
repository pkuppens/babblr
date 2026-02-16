# Scripts Directory

This directory contains maintenance and utility scripts for the Babblr project.

## Available Scripts

### cleanup-merged-branches.sh

**Purpose**: Clean up merged git branches and stale GitHub Actions workflow runs.

**What it cleans**:
- Local branches merged into main
- Remote branches merged into main
- GitHub Actions runs for branches that no longer exist
- Superseded workflow runs (older runs when a newer completed run exists)

**Usage**:
```bash
# Validation mode (dry-run, default)
./scripts/cleanup-merged-branches.sh

# Execute cleanup
./scripts/cleanup-merged-branches.sh --execute

# Show help
./scripts/cleanup-merged-branches.sh --help
```

**Requirements**:
- `gh` CLI (GitHub CLI) installed and authenticated
- Write access to repository (for --execute mode)

**Safety Features**:
- Protected branches (main, master, develop, HEAD) are never deleted
- Dry-run mode by default - must explicitly use `--execute` to make changes

**When to use**:
- After merging multiple PRs
- Weekly/monthly repository maintenance
- When GitHub Actions runs accumulate

### cleanup-github-actions.sh

**Purpose**: Clean up obsolete GitHub Actions workflow runs.

**What it cleans**:
1. Obsolete approval runs (queued/waiting older than 7 days)
2. Runs on PR refs (refs/pull/*)
3. Runs for branches that no longer exist
4. Superseded runs (keeps most recent completed + failed for debugging)
5. Orphaned runs (workflow file deleted, runs still exist)

**Usage**:
```bash
# Dry-run (default)
./scripts/cleanup-github-actions.sh

# Execute cleanup
./scripts/cleanup-github-actions.sh --execute

# Show help
./scripts/cleanup-github-actions.sh --help
```

**Requirements**:
- `gh` CLI with workflow scope: `gh auth refresh -s workflow`
- Python 3 (for JSON processing)
- Run from repository root

**When to use**:
- When GitHub Actions runs accumulate
- After merging many PRs
- Before major releases

### Repository Cleanup (GitHub Action)

Both scripts run automatically via `.github/workflows/cleanup.yml`:
- **Trigger**: After CI completes on main, or manually via workflow_dispatch
- **Runs**: Branch cleanup first, then workflow run cleanup
- See [docs/ci/REPOSITORY_CLEANUP.md](../docs/ci/REPOSITORY_CLEANUP.md) for full documentation

### no-commit-to-main.sh

**Purpose**: Pre-commit hook that prevents direct commits to the main branch.

**Usage**: Automatically invoked by git pre-commit hook. See POLICIES.md for details.

### check_markdown_local_links.py

**Purpose**: Validate local links in markdown files.

**Usage**: Invoked by CI/CD pipeline. See `.github/workflows/ci.yml` for details.

## Adding New Scripts

1. Create script in `scripts/` directory
2. Make executable: `chmod +x scripts/your-script.sh`
3. Follow ASCII-only convention (no Unicode/emoji in .sh or .bat files)
4. Use ASCII prefixes: `[OK]`, `[ERROR]`, `[WARNING]`, `[INFO]`, `[SETUP]`, `[START]`
5. Update this README with script documentation
6. Consider adding to `.claude/commands/` for easy invocation via Claude Code

## Script Conventions

**Output Prefixes**:
- `[OK]` - Success messages
- `[ERROR]` - Error messages
- `[WARNING]` - Warning messages
- `[INFO]` - Informational messages
- `[SETUP]` - Setup/initialization messages
- `[START]` - Starting process messages

**Best Practices**:
- Always use `set -e` to exit on errors
- Provide `--help` flag for usage information
- Implement `--dry-run` or validation mode when appropriate
- Test scripts locally before committing
- Document requirements and dependencies
- Use meaningful exit codes (0 = success, non-zero = failure)
