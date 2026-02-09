---
name: git-workflow
description: Git branch management and pull request workflows. Use when creating feature branches, pushing changes, creating PRs, or managing git operations for issue implementation.
allowed-tools: Bash(git:*), Bash(gh:*)
---

# Git Workflow Management

## Branch Naming

Format: `feature/<issue-number>-<short-description>`

Examples: `feature/123-add-user-auth`, `feature/45-fix-login-bug`

## Branch Operations

```bash
# Check current branch
git branch --show-current

# Create feature branch from main
git checkout main && git pull origin main
git checkout -b feature/<issue>-<description>

# Check for existing branch
git branch -a | grep -i "feature/<issue>"
```

## Commit Convention

Format: `#<issue>: <type>: <description>`

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`

```bash
# Simple commit
git commit -m "#123: feat: add user authentication endpoint"

# Multi-line commit
git commit -m "$(cat <<'EOF'
#123: feat: add user authentication

- Implement JWT token generation
- Add password hashing

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

## Pull Request

```bash
# Push branch
git push -u origin feature/<issue>-<description>

# Create PR
gh pr create --title "#<issue>: <title>" --body "$(cat <<'EOF'
## Summary
[Brief description]

Closes #<issue>

## Changes
- [Change 1]

## Testing
- [How tested]

---
Generated with Claude Code
EOF
)" --reviewer <reviewer>
```

## Pre-commit

```bash
pre-commit run --all-files

# If hooks auto-fix files
git add -A && git commit -m "#<issue>: chore: apply pre-commit fixes"
```

## Branch Cleanup

```bash
# Validate what can be cleaned (dry-run)
./scripts/cleanup-merged-branches.sh

# Execute cleanup
./scripts/cleanup-merged-branches.sh --execute
```

Cleans up:
- Merged local and remote branches
- GitHub Actions runs for deleted branches
- Superseded workflow runs

See `/cleanup` command for details.

## Safety Rules

- NEVER commit directly to `main`
- NEVER force push to shared branches
- NEVER skip pre-commit hooks without approval
- Always create PRs for code review
