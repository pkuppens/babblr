# Scripts Directory

This directory contains maintenance and utility scripts for the Babblr project.

## Available Scripts

### Repository Cleanup (two scripts, no overlap)

Clean up merged branches and obsolete GitHub Actions runs. Run both for full cleanup.

| Script | Cleans | Requirements |
|--------|--------|--------------|
| `cleanup-merged-branches.sh` | Local + remote branches merged into main | git, push access (gh optional) |
| `cleanup-github-actions.sh` | Workflow runs: obsolete, PR refs, deleted branches, superseded, orphaned | gh + workflow scope, Python 3 |

**Usage** (both scripts):
```bash
# Dry-run (default)
./scripts/cleanup-merged-branches.sh
./scripts/cleanup-github-actions.sh

# Execute
./scripts/cleanup-merged-branches.sh --execute
./scripts/cleanup-github-actions.sh --execute
```

**cleanup-merged-branches.sh** also supports `--local-only`, `--remote-only`. Protected: main, master, develop, release/*, hotfix/*.

**cleanup-github-actions.sh** keeps failed runs for debugging; needs `gh auth refresh -s workflow`.

**Automated**: Both run via `.github/workflows/cleanup.yml` after CI on main. See [docs/ci/REPOSITORY_CLEANUP.md](../docs/ci/REPOSITORY_CLEANUP.md).

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
