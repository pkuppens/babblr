---
name: cleanup
description: Clean up merged git branches and GitHub Actions workflow runs
allowed-tools: Bash(./scripts/cleanup-merged-branches.sh:*)
---

# Repository Cleanup Command

Cleans up merged branches and stale GitHub Actions workflow runs to keep the repository tidy.

## What This Command Does

1. **Identifies merged branches** (local and remote) that have been integrated into main
2. **Finds GitHub Actions runs** for branches that no longer exist
3. **Identifies superseded workflow runs** (older runs when a newer successful run exists)
4. **Optionally deletes** all of the above (with user confirmation)

## Usage

### Validation Mode (Default)
Shows what would be cleaned up without making any changes:

```bash
./scripts/cleanup-merged-branches.sh
```

### Execution Mode
Actually performs the cleanup:

```bash
./scripts/cleanup-merged-branches.sh --execute
```

### Help
Show detailed help:

```bash
./scripts/cleanup-merged-branches.sh --help
```

## Expected Behavior

The validation run should:
- ✅ Report 0 merged branches (if repository is clean)
- ⚠️ Report multiple GitHub Actions runs for deleted branches
- ⚠️ Report superseded workflow runs
- 📊 Show total items that can be cleaned

The execution run will:
- Delete identified workflow runs using `gh run delete`
- Delete merged branches (if any exist)
- Show progress for each deletion
- Provide a summary of cleaned items

## Protected Branches

The following branches are NEVER deleted:
- main
- master
- develop
- HEAD

## Requirements

- `gh` CLI (GitHub CLI) installed and authenticated
- Git repository
- Write access to repository (for execution mode)

## Safety Features

- **Dry-run by default**: Never makes changes unless `--execute` is used
- **Branch protection**: Critical branches are never touched
- **Progress reporting**: Shows what's being deleted in real-time
- **Error handling**: Continues even if individual deletions fail

## When to Use

Run this command:
- After merging multiple PRs
- Weekly/monthly as part of repository maintenance
- When GitHub Actions runs accumulate
- Before major releases to clean up history

## Example Output

```
[WARNING] DRY-RUN MODE - No changes will be made
[INFO] Repository: pkuppens/babblr
[INFO] Main branch: main

[OK] No local merged branches to clean up
[OK] No remote merged branches to clean up
[WARNING] Found 70 workflow run(s) for deleted branches
[WARNING] Found 48 superseded workflow run(s)

Would clean up:
  - Local merged branches: 0
  - Remote merged branches: 0
  - Workflow runs for deleted branches: 70
  - Superseded workflow runs: 48

[WARNING] Total items to clean: 118
```
