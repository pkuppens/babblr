---
name: git-workflow
description: Git branch management and pull request workflows. Use when creating feature branches, pushing changes, creating PRs, or managing git operations for issue implementation.
allowed-tools: Bash(git:*), Bash(gh:*)
---

# Git Workflow Management

This skill provides git branching and PR workflows following gitflow conventions.

## Branch Naming Convention

Format: `feature/<issue-number>-<short-description>`

Examples:
- `feature/123-add-user-auth`
- `feature/45-fix-login-bug`
- `feature/78-update-docs`

Rules:
- Use lowercase
- Replace spaces with hyphens
- Keep description short (max 5 words)
- Always include issue number

## Branch Operations

### Check Current Branch
```bash
git branch --show-current
```

### Check for Existing Branch
```bash
git branch -a | grep -i "feature/<issue-number>" || echo "No existing branch"
```

### Create Feature Branch
```bash
# From main branch
git checkout main
git pull origin main
git checkout -b feature/<issue-number>-<description>
```

### Switch to Existing Branch
```bash
git checkout feature/<issue-number>-<description>
```

## Commit Convention

Format: `#<issue-number>: <type>: <description>`

Types:
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation only
- `test` - Adding/updating tests
- `refactor` - Code refactoring
- `chore` - Maintenance tasks

Examples:
```bash
git commit -m "#123: feat: add user authentication endpoint"
git commit -m "#45: fix: resolve login redirect loop"
git commit -m "#78: docs: update API documentation"
```

### Multi-line Commit (with body)
```bash
git commit -m "$(cat <<'EOF'
#123: feat: add user authentication

- Implement JWT token generation
- Add password hashing with bcrypt
- Create login/logout endpoints

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

## Pull Request Workflow

### Push Branch
```bash
git push -u origin feature/<issue-number>-<description>
```

### Create PR
```bash
gh pr create --title "#<issue>: <title>" --body "$(cat <<'EOF'
## Summary
[Brief description of changes]

Closes #<issue-number>

## Changes
- [Change 1]
- [Change 2]

## Testing
- [How this was tested]

## Checklist
- [ ] Tests pass
- [ ] Pre-commit hooks pass
- [ ] Documentation updated

---
Generated with Claude Code
EOF
)" --reviewer <reviewer>
```

### Request Additional Reviewers
```bash
gh pr edit <pr-number> --add-reviewer <username>
```

### Check PR Status
```bash
gh pr status
gh pr view <number>
```

## Pre-commit Validation

### Run Hooks on Changed Files
```bash
git diff --name-only HEAD~1 | xargs pre-commit run --files
```

### Run All Hooks
```bash
pre-commit run --all-files
```

### If Hooks Auto-fix Files
```bash
git add -A
git commit -m "#<issue>: chore: apply pre-commit fixes"
```

## Safety Rules

- NEVER commit directly to `main`
- NEVER force push to shared branches
- NEVER skip pre-commit hooks without approval
- Always create PRs for code review
- Verify branch before committing

## Troubleshooting

### Branch Already Exists
```bash
# Check if it's your work
git log feature/<issue>-<desc> --oneline -5

# Resume work
git checkout feature/<issue>-<desc>
```

### Merge Conflicts
```bash
git fetch origin
git merge origin/main
# Resolve conflicts, then:
git add .
git commit -m "#<issue>: chore: resolve merge conflicts"
```
