# Repository Cleanup

This document describes the automated repository cleanup workflow and scripts.

## Overview

The Repository Cleanup workflow runs after CI completes on `main`. It removes merged branches and obsolete GitHub Actions workflow runs to keep the repository and Actions tab tidy.

**Source**: Based on [pkuppens/on_prem_rag](https://github.com/pkuppens/on_prem_rag/actions/workflows/cleanup.yml).

## Workflow

**File**: `.github/workflows/cleanup.yml`

**Triggers**:
- After `CI` workflow completes on `main` (workflow_run)
- Manual via `workflow_dispatch` (Actions tab → Repository Cleanup → Run workflow)

**Dependencies**:
- `CI` workflow must exist and complete successfully
- The cleanup workflow checks that CI has finished before running (avoids race conditions)

## Scripts

### 1. cleanup-merged-branches.sh

**Location**: `scripts/cleanup-merged-branches.sh`

**Cleans**:
- Local branches merged into main
- Remote branches merged into main (via `git push --delete`)
- GitHub Actions runs for branches that no longer exist
- Superseded runs (keeps most recent completed per workflow+branch)

### 2. cleanup-github-actions.sh

**Location**: `scripts/cleanup-github-actions.sh`

**Cleans** (5 steps):
1. **Obsolete approval runs** — queued/waiting runs older than 7 days
2. **PR ref runs** — all runs on `refs/pull/*` (ephemeral after merge/close)
3. **Deleted branch runs** — runs for branches that no longer exist
4. **Superseded runs** — keeps most recent completed + failed runs (for debugging)
5. **Orphaned runs** — runs for workflow files that have been deleted

## Running Locally

### Prerequisites
- `gh` CLI installed and authenticated
- Workflow scope for run deletion: `gh auth refresh -s workflow`
- Python 3 (for cleanup-github-actions.sh)

### Commands
```bash
# Dry-run (both scripts)
./scripts/cleanup-merged-branches.sh
./scripts/cleanup-github-actions.sh

# Execute cleanup
./scripts/cleanup-merged-branches.sh --execute
./scripts/cleanup-github-actions.sh --execute
```

### When to Run
- After merging multiple PRs
- When Actions tab has many stale runs
- Before major releases
- Weekly/monthly maintenance

## Protected Branches

The following branches are **never** deleted:
- `main`
- `master`
- `develop`
- `HEAD`

## Self-Cleaning

The Repository Cleanup workflow cleans its own old runs. Step 4 (superseded) keeps only the most recent completed run per workflow+branch, so at most 2 Repository Cleanup runs exist at any time (current + previous).

## Permissions

The workflow needs:
- `contents: write` — to delete remote branches
- `actions: write` — to delete workflow runs

The default `GITHUB_TOKEN` has these when specified in `permissions`.

## See Also

- [scripts/README.md](../../scripts/README.md) — Script documentation
- [CLEANUP_COMMAND_SUMMARY.md](../../CLEANUP_COMMAND_SUMMARY.md) — Historical cleanup summary
