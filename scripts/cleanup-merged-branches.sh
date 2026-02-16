#!/bin/bash
# cleanup-merged-branches.sh
# Cleans up branches that have been merged into the main branch
#
# Features:
# 1. Deletes local branches that have been merged into main
# 2. Deletes remote branches that have been merged into main
# 3. Protects important branches (main, master, develop, etc.)
# 4. Works both locally and in GitHub Actions environment
#
# Usage:
#   ./cleanup-merged-branches.sh              # Dry-run (show what would be cleaned)
#   ./cleanup-merged-branches.sh --execute    # Execute cleanup
#   ./cleanup-merged-branches.sh --local-only # Only clean local branches
#   ./cleanup-merged-branches.sh --remote-only# Only clean remote branches
#   ./cleanup-merged-branches.sh --help       # Show help
#
# Workflow run cleanup: use cleanup-github-actions.sh (no overlap)
# Based on: pkuppens/on_prem_rag

set -e

DRY_RUN=true
CLEAN_LOCAL=true
CLEAN_REMOTE=true
MAIN_BRANCH="main"

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
Branch Cleanup Script

Cleans up branches that have been merged into the main branch:
- Local branches that have been merged
- Remote branches that have been merged

Protected branches (never deleted):
- main, master, develop, development, staging, production
- Any branch matching: release/*, hotfix/*

Usage:
  $0 # Dry-run (shows what would be deleted)
  $0 --execute # Execute cleanup
  $0 --local-only # Only clean local branches
  $0 --remote-only # Only clean remote branches
  $0 --help # Show this help

Requirements:
- git installed
- Write permissions for remote branch deletion (gh CLI or git credentials)
- Must be run from within a git repository
EOF
  exit 0
}

for arg in "$@"; do
  case $arg in
    --execute) DRY_RUN=false ;;
    --local-only) CLEAN_LOCAL=true; CLEAN_REMOTE=false ;;
    --remote-only) CLEAN_LOCAL=false; CLEAN_REMOTE=true ;;
    --help|-h) show_help ;;
    *) print_error "Unknown argument: $arg"; exit 1 ;;
  esac
done

git rev-parse --git-dir >/dev/null 2>&1 || { print_error "Not in a git repository"; exit 1; }

if [ "$DRY_RUN" = true ]; then
  print_warning "DRY-RUN MODE - No changes will be made"
  print_info "Run with --execute to perform cleanup"
  echo ""
fi

print_info "Fetching latest refs from remote..."
git fetch origin --prune 2>/dev/null || print_warning "Failed to fetch from remote"
echo ""

# Determine the default branch
if git show-ref --verify --quiet refs/heads/main; then
  MAIN_BRANCH="main"
  MAIN_REF="main"
elif git show-ref --verify --quiet refs/heads/master; then
  MAIN_BRANCH="master"
  MAIN_REF="master"
elif git show-ref --verify --quiet refs/remotes/origin/main; then
  MAIN_BRANCH="main"
  MAIN_REF="origin/main"
elif git show-ref --verify --quiet refs/remotes/origin/master; then
  MAIN_BRANCH="master"
  MAIN_REF="origin/master"
else
  print_error "Could not find main or master branch"
  exit 1
fi

print_info "Using base branch: $MAIN_BRANCH"
echo ""

is_protected_branch() {
  local branch=$1
  case "$branch" in
    main|master|develop|development|staging|production)
      return 0
      ;;
    release/*|hotfix/*)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

# ============================================================================
# STEP 1: Clean up local merged branches
# ============================================================================
if [ "$CLEAN_LOCAL" = true ]; then
  print_info "STEP 1: Checking local branches merged into $MAIN_BRANCH..."

  LOCAL_COUNT=0
  LOCAL_DELETED=0

  MERGED_BRANCHES=$(git branch --merged "$MAIN_REF" | grep -v "^\*" | grep -v "^  $MAIN_BRANCH$" | sed 's/^[ *]*//' || true)

  if [ -n "$MERGED_BRANCHES" ]; then
    while IFS= read -r branch; do
      [ -z "$branch" ] && continue
      if is_protected_branch "$branch"; then
        print_info "Skipping protected branch: $branch"
        continue
      fi

      LOCAL_COUNT=$((LOCAL_COUNT + 1))

      if [ "$DRY_RUN" = false ]; then
        print_info "Deleting local branch: $branch"
        if git branch -d "$branch" 2>/dev/null; then
          LOCAL_DELETED=$((LOCAL_DELETED + 1))
          print_success "Deleted: $branch"
        else
          print_warning "Failed to delete: $branch (may have unmerged commits)"
        fi
      else
        print_warning "Would delete local branch: $branch"
      fi
    done <<< "$MERGED_BRANCHES"
  fi

  if [ $LOCAL_COUNT -eq 0 ]; then
    print_success "No local merged branches to clean"
  else
    if [ "$DRY_RUN" = false ]; then
      print_success "Deleted $LOCAL_DELETED of $LOCAL_COUNT local branches"
    else
      print_warning "Found $LOCAL_COUNT local branch(es) to clean"
    fi
  fi
  echo ""
fi

# ============================================================================
# STEP 2: Clean up remote merged branches
# ============================================================================
if [ "$CLEAN_REMOTE" = true ]; then
  print_info "STEP 2: Checking remote branches merged into origin/$MAIN_BRANCH..."

  REMOTE_COUNT=0
  REMOTE_DELETED=0

  if ! git show-ref --verify --quiet "refs/remotes/origin/$MAIN_BRANCH"; then
    git fetch origin "$MAIN_BRANCH:refs/remotes/origin/$MAIN_BRANCH" 2>/dev/null || print_warning "Could not fetch origin/$MAIN_BRANCH"
  fi

  MERGED_REMOTE_BRANCHES=$(git branch -r --merged "origin/$MAIN_BRANCH" 2>/dev/null | grep "origin/" | grep -v "origin/$MAIN_BRANCH$" | grep -v "origin/HEAD" | sed 's/^[ ]*//' | sed 's|origin/||' || true)

  if [ -n "$MERGED_REMOTE_BRANCHES" ]; then
    while IFS= read -r branch; do
      [ -z "$branch" ] && continue
      if is_protected_branch "$branch"; then
        print_info "Skipping protected remote branch: $branch"
        continue
      fi

      REMOTE_COUNT=$((REMOTE_COUNT + 1))

      if [ "$DRY_RUN" = false ]; then
        print_info "Deleting remote branch: origin/$branch"

        if git push origin --delete "$branch" 2>/dev/null; then
          REMOTE_DELETED=$((REMOTE_DELETED + 1))
          print_success "Deleted: origin/$branch"
        elif command -v gh >/dev/null 2>&1; then
          REPO=$(gh repo view --json nameWithOwner --jq .nameWithOwner 2>/dev/null || echo "")
          if [ -n "$REPO" ]; then
            print_info "Trying to delete with gh CLI..."
            if gh api --method DELETE "/repos/$REPO/git/refs/heads/$branch" 2>/dev/null; then
              REMOTE_DELETED=$((REMOTE_DELETED + 1))
              print_success "Deleted: origin/$branch (via gh CLI)"
            else
              print_warning "Failed to delete: origin/$branch (may lack permissions)"
            fi
          else
            print_warning "Failed to delete: origin/$branch"
          fi
        else
          print_warning "Failed to delete: origin/$branch (need gh CLI or push access)"
        fi
      else
        print_warning "Would delete remote branch: origin/$branch"
      fi
    done <<< "$MERGED_REMOTE_BRANCHES"
  fi

  if [ $REMOTE_COUNT -eq 0 ]; then
    print_success "No remote merged branches to clean"
  else
    if [ "$DRY_RUN" = false ]; then
      print_success "Deleted $REMOTE_DELETED of $REMOTE_COUNT remote branches"
    else
      print_warning "Found $REMOTE_COUNT remote branch(es) to clean"
    fi
  fi
  echo ""
fi

# ============================================================================
# SUMMARY
# ============================================================================
echo "========================================"
print_success "CLEANUP SUMMARY"
echo "========================================"

if [ "$DRY_RUN" = true ]; then
  TOTAL=$((${LOCAL_COUNT:-0} + ${REMOTE_COUNT:-0}))
  echo "Would clean: $TOTAL branches (local: ${LOCAL_COUNT:-0}, remote: ${REMOTE_COUNT:-0})"
  echo ""
  print_info "Run with --execute to perform cleanup: $0 --execute"
else
  TOTAL_DELETED=$((${LOCAL_DELETED:-0} + ${REMOTE_DELETED:-0}))
  TOTAL_FOUND=$((${LOCAL_COUNT:-0} + ${REMOTE_COUNT:-0}))
  echo "Deleted: $TOTAL_DELETED of $TOTAL_FOUND branches"
  if [ $TOTAL_DELETED -lt $TOTAL_FOUND ]; then
    print_warning "Some branches could not be deleted (check permissions or unmerged commits)"
  fi
fi
echo ""
