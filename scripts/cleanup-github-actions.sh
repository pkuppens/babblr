#!/bin/bash
# cleanup-github-actions.sh
# Cleans up obsolete GitHub Actions workflow runs
#
# Targets:
# 1. Runs that required approval but are now obsolete (queued/waiting, old)
# 2. Runs on PR refs (refs/pull/*) - ephemeral, no value after merge/close
# 3. Runs for branches that no longer exist
# 4. Superseded runs (keeps only most recent completed per workflow+branch)
# 5. Orphaned workflow runs (workflow file deleted, runs still exist)
#
# Usage:
# ./cleanup-github-actions.sh # Dry-run (show what would be cleaned)
# ./cleanup-github-actions.sh --execute # Execute cleanup
# ./cleanup-github-actions.sh --help # Show help
#
# Based on: pkuppens/on_prem_rag
# Requires: gh CLI with workflow scope (gh auth refresh -s workflow)

set -e

DRY_RUN=true
STALE_DAYS=7 # Runs queued/waiting older than this are considered obsolete

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[OK]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

show_help() {
  cat << EOF
GitHub Actions Workflow Run Cleanup

Cleans up:
1. Obsolete approval runs - queued/waiting runs older than ${STALE_DAYS} days
2. PR ref runs - all runs on refs/pull/* (ephemeral, no value after merge/close)
3. Runs for branches that no longer exist
4. Superseded runs - keeps only most recent completed per workflow+branch
5. Orphaned workflow runs - runs for workflow files that have been deleted

Usage:
  $0 # Dry-run
  $0 --execute # Execute cleanup
  $0 --help # This help

Requirements:
- gh CLI installed and authenticated (in PATH)
- Workflow scope: gh auth refresh -s workflow
- On Windows: run from Git Bash or a terminal where 'gh' works
EOF
  exit 0
}

for arg in "$@"; do
  case $arg in
    --execute) DRY_RUN=false ;;
    --help|-h) show_help ;;
    *) print_error "Unknown argument: $arg"; exit 1 ;;
  esac
done

if [ "$DRY_RUN" = true ]; then
  print_warning "DRY-RUN MODE - No changes will be made"
  print_info "Run with --execute to perform cleanup"
  echo ""
fi

command -v gh >/dev/null 2>&1 || { print_error "gh CLI required (ensure it is in PATH). Install: https://cli.github.com/"; exit 1; }
git rev-parse --git-dir >/dev/null 2>&1 || { print_error "Not in a git repository"; exit 1; }
PYTHON="${PYTHON:-$(command -v python3 2>/dev/null || command -v python 2>/dev/null)}"
if [ -z "$PYTHON" ] || ! $PYTHON -c "import json" 2>/dev/null; then
  print_error "python3 or python required (set PYTHON=path/to/python to override)"
  exit 1
fi

REPO=$(gh repo view --json nameWithOwner --jq .nameWithOwner)
print_info "Repository: $REPO"
echo ""

# Fetch latest refs for accurate branch check
print_info "Fetching latest refs..."
git fetch origin --prune 2>/dev/null || true

# Use temp file in current directory (avoids Windows path issues in Git Bash)
TEMP_RUNS="cleanup_actions_runs_$$.json"
gh run list --limit 1000 --json databaseId,status,conclusion,workflowName,headBranch,createdAt > "$TEMP_RUNS"

# Existing branches (local + remote, normalized)
EXISTING_BRANCHES=$(git branch -a | sed 's/remotes\/origin\///' | sed 's/^[* ]*//' | grep -v "HEAD" | sort -u)

# ============================================================================
# STEP 1: Obsolete approval runs (queued/waiting, old)
# ============================================================================
print_info "STEP 1: Checking for obsolete queued/waiting runs (older than ${STALE_DAYS} days)..."

STALE_CUTOFF=$($PYTHON -c "from datetime import datetime, timedelta; print((datetime.utcnow() - timedelta(days=${STALE_DAYS})).strftime('%Y-%m-%dT%H:%M:%SZ'))")

OBSOLETE_APPROVAL_IDS=$($PYTHON << PYEOF
import json
from datetime import datetime

with open("$TEMP_RUNS") as f:
  data = json.load(f)

cutoff = "$STALE_CUTOFF"
stale = []
for r in data:
  if r['status'] in ('queued', 'pending', 'waiting'):
    if r.get('createdAt', '') < cutoff:
      stale.append(str(r['databaseId']))
print('\n'.join(stale))
PYEOF
)

OBSOLETE_COUNT=0
OBSOLETE_DELETED=0

for run_id in $OBSOLETE_APPROVAL_IDS; do
  [ -z "$run_id" ] && continue
  OBSOLETE_COUNT=$((OBSOLETE_COUNT + 1))
  if [ "$DRY_RUN" = false ]; then
    print_info "Deleting obsolete run $run_id"
    if echo "y" | gh run delete "$run_id" 2>/dev/null; then
      OBSOLETE_DELETED=$((OBSOLETE_DELETED + 1))
    else
      print_warning "Failed to delete run $run_id (need: gh auth refresh -s workflow)"
    fi
  else
    print_warning "Would delete obsolete run $run_id"
  fi
done

[ $OBSOLETE_COUNT -eq 0 ] && print_success "No obsolete approval runs" || print_warning "Found $OBSOLETE_COUNT obsolete run(s)"
echo ""

# ============================================================================
# STEP 2: Runs on PR refs (refs/pull/*)
# ============================================================================
print_info "STEP 2: Checking for runs on PR refs (refs/pull/*)..."

PR_REF_BRANCHES=$($PYTHON -c "
import json
with open('$TEMP_RUNS') as f:
  data = json.load(f)
seen = set()
for r in data:
  b = r.get('headBranch', '')
  if b.startswith('refs/pull/') and b not in seen:
    seen.add(b)
    print(b)
")

PR_REF_RUNS=0
PR_REF_DELETED=0

while IFS= read -r branch; do
  branch="${branch%$'\r'}"
  [ -z "$branch" ] && continue
  RUN_IDS=$(gh run list --branch "$branch" --limit 1000 --json databaseId --jq '.[].databaseId')
  if [ -n "$RUN_IDS" ]; then
    for run_id in $RUN_IDS; do
      PR_REF_RUNS=$((PR_REF_RUNS + 1))
      if [ "$DRY_RUN" = false ]; then
        print_info "Deleting run $run_id (PR ref '$branch')"
        if echo "y" | gh run delete "$run_id" 2>/dev/null; then
          PR_REF_DELETED=$((PR_REF_DELETED + 1))
        fi
      else
        print_warning "Would delete run $run_id (PR ref '$branch')"
      fi
    done
  fi
done <<< "$PR_REF_BRANCHES"

[ $PR_REF_RUNS -eq 0 ] && print_success "No PR ref runs" || print_warning "Found $PR_REF_RUNS run(s) on PR refs"
echo ""

# ============================================================================
# STEP 3: Runs for deleted branches
# ============================================================================
print_info "STEP 3: Checking runs for deleted branches..."

WORKFLOW_BRANCHES=$($PYTHON -c "
import json
with open('$TEMP_RUNS') as f:
  data = json.load(f)
seen = set()
for r in data:
  b = r.get('headBranch', '')
  if b and b not in seen:
    seen.add(b)
    print(b)
")

DELETED_BRANCH_RUNS=0
DELETED_BRANCH_SUCCESS=0

while IFS= read -r branch; do
  branch="${branch%$'\r'}"  # Strip Windows CR
  [ -z "$branch" ] && continue
  # PR refs already handled in Step 2
  case "$branch" in refs/pull/*) continue ;; esac
  # Check if branch exists
  if ! echo "$EXISTING_BRANCHES" | grep -qxF "$branch"; then
    RUN_IDS=$(gh run list --branch "$branch" --limit 1000 --json databaseId --jq '.[].databaseId')
    if [ -n "$RUN_IDS" ]; then
      for run_id in $RUN_IDS; do
        DELETED_BRANCH_RUNS=$((DELETED_BRANCH_RUNS + 1))
        if [ "$DRY_RUN" = false ]; then
          print_info "Deleting run $run_id (branch '$branch' deleted)"
          if echo "y" | gh run delete "$run_id" 2>/dev/null; then
            DELETED_BRANCH_SUCCESS=$((DELETED_BRANCH_SUCCESS + 1))
          fi
        else
          print_warning "Would delete run $run_id (branch '$branch' deleted)"
        fi
      done
    fi
  fi
done <<< "$WORKFLOW_BRANCHES"

[ $DELETED_BRANCH_RUNS -eq 0 ] && print_success "No runs for deleted branches" || print_warning "Found $DELETED_BRANCH_RUNS run(s) for deleted branches"
echo ""

# ============================================================================
# STEP 4: Superseded runs (keep most recent and failed runs for debugging)
# ============================================================================
print_info "STEP 4: Checking superseded runs (keeping most recent + failed runs for debugging)..."

KEEP_RUNS=$($PYTHON << PYEOF
import json
from collections import defaultdict

with open("$TEMP_RUNS") as f:
  data = json.load(f)

groups = defaultdict(list)
for r in data:
  key = r['workflowName'] + '|' + r['headBranch']
  groups[key].append(r)

keep = []
for runs in groups.values():
  completed = [r for r in runs if r['status'] == 'completed']
  if completed:
    # Sort by creation date (newest first)
    completed.sort(key=lambda x: x['createdAt'], reverse=True)

    # Keep the most recent completed run
    keep.append(str(completed[0]['databaseId']))

    # Also keep failed runs that came after the last successful run
    # This helps with debugging issues that haven't been resolved
    last_success_date = None
    for run in completed:
      if run.get('conclusion') == 'success':
        last_success_date = run['createdAt']
        break

    # Keep all failed runs that are newer than the last success
    for run in completed:
      if run.get('conclusion') == 'failure':
        if last_success_date is None or run['createdAt'] > last_success_date:
          keep.append(str(run['databaseId']))

print('\n'.join(keep))
PYEOF
)

ALL_IDS=$($PYTHON -c "import json; f=open('$TEMP_RUNS'); d=json.load(f); print('\n'.join(str(r['databaseId']) for r in d))")
SUPERSEDED_COUNT=0
SUPERSEDED_DELETED=0

for run_id in $ALL_IDS; do
  run_id="${run_id%$'\r'}"
  [ -z "$run_id" ] && continue
  echo "$KEEP_RUNS" | grep -qxF "$run_id" && continue
  SUPERSEDED_COUNT=$((SUPERSEDED_COUNT + 1))
  if [ "$DRY_RUN" = false ]; then
    RUN_INFO=$($PYTHON -c "
import json
f=open('$TEMP_RUNS')
for r in json.load(f):
  if r['databaseId']==$run_id:
    print(r['workflowName']+' ['+(r.get('conclusion') or r['status'])+'] on '+r['headBranch'])
    break
" 2>/dev/null) || RUN_INFO="(unknown)"
    print_info "Deleting superseded $run_id: $RUN_INFO"
    echo "y" | gh run delete "$run_id" 2>/dev/null && SUPERSEDED_DELETED=$((SUPERSEDED_DELETED + 1)) || true
  fi
done

[ $SUPERSEDED_COUNT -eq 0 ] && print_success "No superseded runs" || print_warning "Found $SUPERSEDED_COUNT superseded run(s)"
echo ""

# ============================================================================
# STEP 5: Orphaned workflow runs (workflow file deleted, runs still exist)
# ============================================================================
print_info "STEP 5: Checking for runs from deleted/orphaned workflows..."

# Get unique workflow names from the runs we fetched
WORKFLOW_NAMES=$($PYTHON -c "
import json
with open('$TEMP_RUNS') as f:
  data = json.load(f)
seen = set()
for r in data:
  name = r.get('workflowName', '')
  if name and name not in seen:
    seen.add(name)
    print(name)
")

# Get workflow names that currently have .yml files
ACTIVE_WORKFLOWS=""
for yml_file in .github/workflows/*.yml; do
  [ -f "$yml_file" ] || continue
  # Extract the 'name:' field from each workflow file
  WF_NAME=$($PYTHON -c "
import re, sys
with open('$yml_file', encoding='utf-8') as f:
  for line in f:
    m = re.match(r'^name:\s*(.+)', line)
    if m:
      print(m.group(1).strip().strip('\"').strip(\"'\"))
      break
")
  [ -n "$WF_NAME" ] && ACTIVE_WORKFLOWS="$ACTIVE_WORKFLOWS
$WF_NAME"
done

ORPHANED_COUNT=0
ORPHANED_DELETED=0

while IFS= read -r wf_name; do
  wf_name="${wf_name%$'\r'}"
  [ -z "$wf_name" ] && continue
  # Check if this workflow name exists in active workflow files
  if ! echo "$ACTIVE_WORKFLOWS" | grep -qxF "$wf_name"; then
    # This workflow has runs but no corresponding .yml file — orphaned
    ORPHAN_IDS=$($PYTHON -c "
import json
with open('$TEMP_RUNS') as f:
  data = json.load(f)
for r in data:
  if r.get('workflowName') == '$wf_name':
    print(r['databaseId'])
")
    for run_id in $ORPHAN_IDS; do
      run_id="${run_id%$'\r'}"
      [ -z "$run_id" ] && continue
      ORPHANED_COUNT=$((ORPHANED_COUNT + 1))
      if [ "$DRY_RUN" = false ]; then
        print_info "Deleting orphaned run $run_id (workflow '$wf_name' no longer exists)"
        echo "y" | gh run delete "$run_id" 2>/dev/null && ORPHANED_DELETED=$((ORPHANED_DELETED + 1)) || true
      else
        print_warning "Would delete orphaned run $run_id (workflow '$wf_name' no longer exists)"
      fi
    done
  fi
done <<< "$WORKFLOW_NAMES"

[ $ORPHANED_COUNT -eq 0 ] && print_success "No orphaned workflow runs" || print_warning "Found $ORPHANED_COUNT orphaned run(s)"
echo ""

rm -f "$TEMP_RUNS"

# ============================================================================
# SUMMARY
# ============================================================================
echo "========================================"
print_success "CLEANUP SUMMARY"
echo "========================================"
TOTAL=$((OBSOLETE_COUNT + PR_REF_RUNS + DELETED_BRANCH_RUNS + SUPERSEDED_COUNT + ORPHANED_COUNT))
if [ "$DRY_RUN" = true ]; then
  echo "Would clean: $TOTAL runs (obsolete: $OBSOLETE_COUNT, pr-refs: $PR_REF_RUNS, deleted-branch: $DELETED_BRANCH_RUNS, superseded: $SUPERSEDED_COUNT, orphaned: $ORPHANED_COUNT)"
  echo ""
  print_info "Run with --execute to perform: $0 --execute"
else
  DELETED=$((OBSOLETE_DELETED + PR_REF_DELETED + DELETED_BRANCH_SUCCESS + SUPERSEDED_DELETED + ORPHANED_DELETED))
  echo "Deleted: $DELETED of $TOTAL runs"
fi
echo ""
