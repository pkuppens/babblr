#!/bin/bash
# cleanup-merged-branches.sh
# Cleans up merged git branches and their GitHub Actions workflow runs
#
# Usage:
#   ./cleanup-merged-branches.sh                    # Dry-run mode (validation)
#   ./cleanup-merged-branches.sh --execute          # Execute cleanup
#   ./cleanup-merged-branches.sh --help             # Show help

set -e

# ASCII-only output per CLAUDE.md
DRY_RUN=true
MAIN_BRANCH="main"
PROTECTED_BRANCHES="main|master|develop|HEAD"

# Colors for output (optional, works in most terminals)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

function print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

function print_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

function print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

function print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

function show_help() {
    cat << EOF
GitHub Branch and Workflow Run Cleanup Script

This script cleans up:
1. Local branches merged into main
2. Remote branches merged into main (via GitHub API)
3. GitHub Actions runs for deleted branches
4. Superseded GitHub Actions runs (older runs when newer successful run exists)

Usage:
    $0                    # Dry-run mode (shows what would be cleaned)
    $0 --execute          # Execute cleanup
    $0 --help             # Show this help

Protected branches (never deleted): $PROTECTED_BRANCHES

Requirements:
- gh CLI (GitHub CLI) installed and authenticated
- git repository
- Write access to repository (for --execute mode)

EOF
    exit 0
}

# Parse arguments
for arg in "$@"; do
    case $arg in
        --execute)
            DRY_RUN=false
            shift
            ;;
        --help|-h)
            show_help
            ;;
        *)
            print_error "Unknown argument: $arg"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

if [ "$DRY_RUN" = true ]; then
    print_warning "DRY-RUN MODE - No changes will be made"
    print_info "Run with --execute to perform actual cleanup"
    echo ""
fi

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    print_error "gh CLI is not installed. Install from: https://cli.github.com/"
    exit 1
fi

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    print_error "Not in a git repository"
    exit 1
fi

# Get repository info
REPO=$(gh repo view --json nameWithOwner --jq .nameWithOwner)
print_info "Repository: $REPO"
print_info "Main branch: $MAIN_BRANCH"
echo ""

# ============================================================================
# STEP 1: Find merged local branches
# ============================================================================
print_info "STEP 1: Checking local merged branches..."
MERGED_LOCAL_BRANCHES=$(git branch --merged "$MAIN_BRANCH" | grep -v "^\*" | grep -vE "^\s*($PROTECTED_BRANCHES)\s*$" | sed 's/^[* ]*//' || true)

if [ -z "$MERGED_LOCAL_BRANCHES" ]; then
    print_success "No local merged branches to clean up"
else
    BRANCH_COUNT=$(echo "$MERGED_LOCAL_BRANCHES" | wc -l)
    print_warning "Found $BRANCH_COUNT local merged branch(es):"
    echo "$MERGED_LOCAL_BRANCHES" | while read -r branch; do
        echo "  - $branch"
    done

    if [ "$DRY_RUN" = false ]; then
        echo "$MERGED_LOCAL_BRANCHES" | while read -r branch; do
            print_info "Deleting local branch: $branch"
            git branch -d "$branch"
        done
        print_success "Deleted $BRANCH_COUNT local branch(es)"
    fi
fi
echo ""

# ============================================================================
# STEP 2: Find remote branches merged into main
# ============================================================================
print_info "STEP 2: Checking remote merged branches..."

# Get all remote branches
REMOTE_BRANCHES=$(git branch -r --merged "origin/$MAIN_BRANCH" | grep -v "HEAD" | grep -vE "($PROTECTED_BRANCHES)" | sed 's/origin\///' | sed 's/^[* ]*//' || true)

if [ -z "$REMOTE_BRANCHES" ]; then
    print_success "No remote merged branches to clean up"
else
    REMOTE_COUNT=$(echo "$REMOTE_BRANCHES" | wc -l)
    print_warning "Found $REMOTE_COUNT remote merged branch(es):"
    echo "$REMOTE_BRANCHES" | while read -r branch; do
        echo "  - $branch"
    done

    if [ "$DRY_RUN" = false ]; then
        echo "$REMOTE_BRANCHES" | while read -r branch; do
            print_info "Deleting remote branch: $branch"
            git push origin --delete "$branch" || print_warning "Failed to delete $branch (may already be deleted)"
        done
        print_success "Attempted to delete $REMOTE_COUNT remote branch(es)"
    fi
fi
echo ""

# ============================================================================
# STEP 3: Clean up GitHub Actions runs for deleted branches
# ============================================================================
print_info "STEP 3: Checking GitHub Actions runs for deleted branches..."

# Get all existing branches (local + remote)
EXISTING_BRANCHES=$(git branch -a | sed 's/remotes\/origin\///' | sed 's/^[* ]*//' | grep -v "HEAD" | sort -u)

# Get unique branches from workflow runs
print_info "Fetching workflow runs (this may take a moment)..."
WORKFLOW_BRANCHES=$(gh run list --limit 1000 --json headBranch --jq 'map(.headBranch) | unique | .[]')

DELETED_BRANCH_RUNS=0
DELETED_BRANCH_SUCCESS=0
FIRST_DELETION_ATTEMPT=true

while IFS= read -r branch; do
    # Check if branch still exists
    if ! echo "$EXISTING_BRANCHES" | grep -qx "$branch"; then
        # Branch doesn't exist anymore, find its runs
        RUN_IDS=$(gh run list --branch "$branch" --limit 1000 --json databaseId --jq '.[].databaseId')

        if [ -n "$RUN_IDS" ]; then
            RUN_COUNT=$(echo "$RUN_IDS" | wc -l)
            DELETED_BRANCH_RUNS=$((DELETED_BRANCH_RUNS + RUN_COUNT))
            print_warning "Branch '$branch' deleted, has $RUN_COUNT workflow run(s)"

            if [ "$DRY_RUN" = false ]; then
                echo "$RUN_IDS" | while read -r run_id; do
                    print_info "Deleting run $run_id for branch: $branch"
                    DELETE_OUTPUT=$(echo "y" | gh run delete "$run_id" 2>&1)
                    DELETE_EXIT=$?

                    if [ $DELETE_EXIT -eq 0 ]; then
                        DELETED_BRANCH_SUCCESS=$((DELETED_BRANCH_SUCCESS + 1))
                    else
                        print_warning "Failed to delete run $run_id"
                        print_error "Error: $DELETE_OUTPUT"

                        # If first deletion fails, likely a permission issue - abort
                        if [ "$FIRST_DELETION_ATTEMPT" = true ]; then
                            print_error "First deletion attempt failed - likely permission issue"
                            print_error "Please check that you have 'workflow' scope in GitHub token"
                            print_error "Run: gh auth refresh -s workflow"
                            exit 1
                        fi
                    fi
                    FIRST_DELETION_ATTEMPT=false
                done
            fi
        fi
    fi
done <<< "$WORKFLOW_BRANCHES"

if [ $DELETED_BRANCH_RUNS -eq 0 ]; then
    print_success "No workflow runs for deleted branches"
else
    print_warning "Found $DELETED_BRANCH_RUNS workflow run(s) for deleted branches"
    if [ "$DRY_RUN" = false ]; then
        print_success "Successfully deleted $DELETED_BRANCH_SUCCESS of $DELETED_BRANCH_RUNS run(s)"
    fi
fi
echo ""

# ============================================================================
# STEP 4: Clean up superseded workflow runs
# ============================================================================
print_info "STEP 4: Checking for superseded workflow runs..."
print_info "Strategy: Keep only most recent completed run per workflow+branch combination"

# Get all workflow runs and save to temp file
# Use a temp file in the current directory to avoid Git Bash/Windows Python path translation issues
# The file will be cleaned up at the end of the script
TEMP_RUNS_FILE="cleanup_runs_temp_$$.json"
gh run list --limit 1000 --json databaseId,status,conclusion,workflowName,headBranch,createdAt > "$TEMP_RUNS_FILE"

# Find runs to keep (most recent per workflow+branch)
# Use Python for JSON processing since jq may not be available
KEEP_RUNS=$(python << EOF
import json, sys
with open("$TEMP_RUNS_FILE") as f:
    data = json.load(f)

from collections import defaultdict
groups = defaultdict(list)
for run in data:
    key = run['workflowName'] + '|' + run['headBranch']
    groups[key].append(run)

keep_ids = []
for key, runs in groups.items():
    completed = [r for r in runs if r['status'] == 'completed']
    if completed:
        completed.sort(key=lambda x: x['createdAt'], reverse=True)
        keep_ids.append(str(completed[0]['databaseId']))

print('\n'.join(keep_ids))
EOF
)

KEEP_COUNT=$(echo "$KEEP_RUNS" | wc -l)
print_info "Will keep $KEEP_COUNT run(s) (most recent completed per workflow+branch)"

# Get all run IDs
ALL_RUN_IDS=$(python << EOF
import json
with open("$TEMP_RUNS_FILE") as f:
    data = json.load(f)
print('\n'.join([str(r['databaseId']) for r in data]))
EOF
)
TOTAL_RUNS=$(echo "$ALL_RUN_IDS" | wc -l)

SUPERSEDED_COUNT=0
SUPERSEDED_DELETED=0

FIRST_SUPERSEDED_ATTEMPT=true

echo "$ALL_RUN_IDS" | while read -r run_id; do
    # Check if this run should be kept
    if echo "$KEEP_RUNS" | grep -qx "$run_id"; then
        continue
    fi

    SUPERSEDED_COUNT=$((SUPERSEDED_COUNT + 1))

    # Get details for this run
    RUN_INFO=$(python << EOF
import json
with open("$TEMP_RUNS_FILE") as f:
    data = json.load(f)
run = next((r for r in data if r['databaseId'] == $run_id), None)
if run:
    print(run['workflowName'] + ' [' + (run.get('conclusion') or run['status']) + '] on ' + run['headBranch'])
else:
    print('Unknown')
EOF
)

    if [ "$DRY_RUN" = false ]; then
        print_info "Deleting superseded run $run_id: $RUN_INFO"
        DELETE_OUTPUT=$(echo "y" | gh run delete "$run_id" 2>&1)
        DELETE_EXIT=$?

        if [ $DELETE_EXIT -eq 0 ]; then
            SUPERSEDED_DELETED=$((SUPERSEDED_DELETED + 1))
        else
            print_warning "Failed to delete run $run_id"
            print_error "Error: $DELETE_OUTPUT"

            # If first deletion fails and we haven't successfully deleted anything yet
            if [ "$FIRST_SUPERSEDED_ATTEMPT" = true ] && [ $DELETED_BRANCH_SUCCESS -eq 0 ]; then
                print_error "No runs have been deleted - likely permission issue"
                print_error "Please check that you have 'workflow' scope in GitHub token"
                print_error "Run: gh auth refresh -s workflow"
                exit 1
            fi
        fi
        FIRST_SUPERSEDED_ATTEMPT=false
    fi
done

SUPERSEDED_COUNT=$(echo "$ALL_RUN_IDS" | wc -l)
SUPERSEDED_COUNT=$((SUPERSEDED_COUNT - KEEP_COUNT))

if [ $SUPERSEDED_COUNT -eq 0 ]; then
    print_success "No superseded workflow runs to clean up"
else
    print_warning "Found $SUPERSEDED_COUNT superseded workflow run(s)"
    if [ "$DRY_RUN" = false ]; then
        print_success "Deleted $SUPERSEDED_DELETED superseded run(s)"
    fi
fi

# Cleanup temp file
rm -f "$TEMP_RUNS_FILE"

echo ""

# ============================================================================
# SUMMARY
# ============================================================================
echo "========================================"
print_success "CLEANUP SUMMARY"
echo "========================================"
echo ""

if [ "$DRY_RUN" = true ]; then
    echo "DRY-RUN MODE - No changes were made"
    echo ""
    echo "Would clean up:"
else
    echo "EXECUTION MODE - Changes were made"
    echo ""
    echo "Results:"
fi

TOTAL_BRANCHES=$(echo "$MERGED_LOCAL_BRANCHES" | wc -l)
TOTAL_REMOTE=$(echo "$REMOTE_BRANCHES" | wc -l)
[ -z "$MERGED_LOCAL_BRANCHES" ] && TOTAL_BRANCHES=0
[ -z "$REMOTE_BRANCHES" ] && TOTAL_REMOTE=0

if [ "$DRY_RUN" = true ]; then
    echo "  - Local merged branches: $TOTAL_BRANCHES"
    echo "  - Remote merged branches: $TOTAL_REMOTE"
    echo "  - Workflow runs for deleted branches: $DELETED_BRANCH_RUNS"
    echo "  - Superseded workflow runs: $SUPERSEDED_COUNT"
else
    echo "  - Local merged branches: deleted $TOTAL_BRANCHES of $TOTAL_BRANCHES"
    echo "  - Remote merged branches: deleted $TOTAL_REMOTE of $TOTAL_REMOTE"
    echo "  - Workflow runs for deleted branches: deleted $DELETED_BRANCH_SUCCESS of $DELETED_BRANCH_RUNS"
    echo "  - Superseded workflow runs: deleted $SUPERSEDED_DELETED of $SUPERSEDED_COUNT"
fi
echo ""

TOTAL_CLEANUP=$((TOTAL_BRANCHES + TOTAL_REMOTE + DELETED_BRANCH_RUNS + SUPERSEDED_COUNT))

if [ $TOTAL_CLEANUP -eq 0 ]; then
    print_success "Repository is clean! No cleanup needed."
else
    if [ "$DRY_RUN" = true ]; then
        print_warning "Total items to clean: $TOTAL_CLEANUP"
        echo ""
        print_info "Run with --execute to perform cleanup:"
        echo "    $0 --execute"
    else
        TOTAL_DELETED=$((TOTAL_BRANCHES + TOTAL_REMOTE + DELETED_BRANCH_SUCCESS + SUPERSEDED_DELETED))
        print_success "Successfully deleted $TOTAL_DELETED of $TOTAL_CLEANUP items"

        TOTAL_FAILED=$((TOTAL_CLEANUP - TOTAL_DELETED))
        if [ $TOTAL_FAILED -gt 0 ]; then
            print_warning "$TOTAL_FAILED deletion(s) failed"
            echo ""
            print_info "Common reasons for failures:"
            echo "  - Insufficient permissions (need 'workflow' scope)"
            echo "  - Runs already deleted"
            echo "  - Network issues"
            echo ""
            print_info "To add workflow scope: gh auth refresh -s workflow"
        fi
    fi
fi

echo ""
