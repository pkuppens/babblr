# Repository Cleanup Command - Summary

## What Exists

### 1. Branch and Workflow Cleanup Script
**File**: `scripts/cleanup-merged-branches.sh`

A comprehensive bash script that:
- Identifies merged local and remote branches
- Finds GitHub Actions runs for deleted branches
- Identifies superseded workflow runs
- Provides dry-run validation mode (default)
- Executes cleanup with `--execute` flag

### 2. Workflow Run Cleanup Script
**File**: `scripts/cleanup-github-actions.sh`

Extended cleanup for workflow runs (from [on_prem_rag](https://github.com/pkuppens/on_prem_rag)):
- Obsolete queued/waiting runs (> 7 days)
- PR ref runs (refs/pull/*)
- Runs for deleted branches
- Superseded runs (keeps most recent + failed for debugging)
- Orphaned runs (workflow file deleted)

### 3. GitHub Actions Workflow
**File**: `.github/workflows/cleanup.yml`

Runs automatically after CI completes on main, or manually via workflow_dispatch. See [docs/ci/REPOSITORY_CLEANUP.md](docs/ci/REPOSITORY_CLEANUP.md).

### 4. Claude Code Command
**File**: `.claude/commands/cleanup.md`

Registered as `/cleanup` command in Claude Code for easy invocation.

### 5. Git Workflow Integration
**Updated**: `.claude/skills/git-workflow/SKILL.md`

Added cleanup section to existing git workflow documentation.

### 6. Scripts Documentation
**File**: `scripts/README.md`

Comprehensive documentation for all scripts in the repository.

## Validation Results

The initial validation run found:

```
✅ Local merged branches:            0
✅ Remote merged branches:           0
⚠️  Workflow runs for deleted branches: 70
⚠️  Superseded workflow runs:         48
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Total items to clean:             118
```

### Branches with Stale Runs
- Multiple dependabot branches (npm/yarn, pip)
- `feature/optimize-pytest-parallelization`
- `feature/prd-framework`
- `feature/weekly-security-updates`
- `fix/markdown-link-checker`

## Usage

### Via Command Line
```bash
# Validation (dry-run)
./scripts/cleanup-merged-branches.sh

# Execute cleanup
./scripts/cleanup-merged-branches.sh --execute

# Help
./scripts/cleanup-merged-branches.sh --help
```

### Via Claude Code
```
/cleanup
```

## What Gets Cleaned

### 1. Merged Branches
- **Local branches**: Branches merged into main (excluding protected branches)
- **Remote branches**: Branches merged into main via GitHub API

### 2. Orphaned Workflow Runs
- GitHub Actions runs for branches that no longer exist
- These accumulate from:
  - Merged and deleted feature branches
  - Merged and deleted dependabot branches
  - Failed or cancelled workflows

### 3. Superseded Runs
- Older workflow runs when a newer successful run exists
- Strategy: Keep only the most recent completed run per workflow+branch combination
- This prevents accumulation of historical runs

## Protected Branches

The following branches are **NEVER** deleted:
- `main`
- `master`
- `develop`
- `HEAD`

## Safety Features

1. **Dry-run by default**: Must explicitly use `--execute` to make changes
2. **Branch protection**: Critical branches are never touched
3. **Progress reporting**: Shows what's being deleted in real-time
4. **Error handling**: Continues even if individual deletions fail
5. **Clear output**: Uses ASCII prefixes `[OK]`, `[WARNING]`, `[INFO]`, `[ERROR]`

## Recommendations

### When to Run

Run cleanup:
- ✅ **After merging multiple PRs**: Prevent accumulation
- ✅ **Weekly/monthly maintenance**: Keep repository tidy
- ✅ **Before major releases**: Clean up history
- ✅ **When Actions quota is high**: Free up storage

### Execution Workflow

1. **Run validation first**: Always check what will be cleaned
   ```bash
   ./scripts/cleanup-merged-branches.sh
   ```

2. **Review the output**: Ensure nothing critical will be deleted

3. **Execute cleanup**: Run with --execute flag
   ```bash
   ./scripts/cleanup-merged-branches.sh --execute
   ```

4. **Monitor progress**: Watch for any errors or warnings

## Expected Behavior

### Validation Run (Current State)
```
[WARNING] DRY-RUN MODE - No changes will be made
[INFO] Repository: pkuppens/babblr
[INFO] Main branch: main

[INFO] STEP 1: Checking local merged branches...
[OK] No local merged branches to clean up

[INFO] STEP 2: Checking remote merged branches...
[OK] No remote merged branches to clean up

[INFO] STEP 3: Checking GitHub Actions runs for deleted branches...
[WARNING] Found 70 workflow run(s) for deleted branches
  - dependabot/github_actions/actions/cache-5: 2 runs
  - dependabot/npm_and_yarn/frontend/...: 52 runs
  - feature/optimize-pytest-parallelization: 6 runs
  - feature/weekly-security-updates: 4 runs
  - fix/markdown-link-checker: 4 runs
  ... and more

[INFO] STEP 4: Checking for superseded workflow runs...
[WARNING] Found 48 superseded workflow run(s)

========================================
Total items to clean: 118
========================================
```

### Execution Run
When run with `--execute`, the script will:
1. Delete each workflow run with `gh run delete <id> --confirm`
2. Show progress: `[INFO] Deleting run 12345: CI [success] on feature/branch`
3. Handle errors: `[WARNING] Failed to delete run 12345`
4. Provide summary of successful deletions

## Technical Details

### Dependencies
- **gh CLI**: GitHub CLI for API operations
- **git**: Standard git operations
- **bash**: Unix shell (works in Git Bash on Windows)

### GitHub API Rate Limits
- The script uses `gh` CLI which respects GitHub API rate limits
- For large repositories with many runs, the script may take several minutes
- Rate limit: 5,000 requests/hour for authenticated users

### Workflow Run Retention
- GitHub automatically deletes workflow runs after 90 days
- This script helps clean up before the 90-day window
- Reduces clutter in Actions tab
- Frees up storage quota

## Next Steps

To execute the cleanup:

```bash
# Review what will be cleaned
./scripts/cleanup-merged-branches.sh

# If satisfied with the preview, execute
./scripts/cleanup-merged-branches.sh --execute
```

The validation confirmed **118 items** ready for cleanup:
- **70 workflow runs** for deleted branches
- **48 superseded** workflow runs
- **0 branches** (repository is clean)

---

**Created**: 2026-02-09
**Status**: ✅ Validated, ready for execution
