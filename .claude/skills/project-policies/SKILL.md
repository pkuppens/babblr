---
name: project-policies
description: Check and enforce project policies from CLAUDE.md and POLICIES.md. Use when validating implementations against project standards, checking code style requirements, or ensuring compliance with development guidelines.
allowed-tools: Read, Glob, Grep
---

# Project Policies

Ensure implementations comply with project guidelines.

## Policy Documents

- `CLAUDE.md` - Development guidelines, code patterns, testing strategy
- `POLICIES.md` - User policies and developer workflow guidelines

## Key Policies

### Git Workflow
- Never commit directly to `main`
- Use feature branches: `feature/<issue>-<description>`
- Commit format: `#<issue>: <type>: <description>`

### Code Quality
- Pre-commit hooks must pass
- Follow existing code patterns

### Testing
- New features need tests
- Bug fixes need regression tests

## Compliance Checklist

Before submitting PR:

- [ ] On feature branch (not main)
- [ ] Commit messages follow convention
- [ ] Pre-commit hooks pass
- [ ] Tests pass
- [ ] No security vulnerabilities
- [ ] Follows existing code patterns

## Verify Compliance

```bash
# Verify branch
git branch --show-current  # Should NOT be 'main'

# Verify pre-commit
pre-commit run --all-files

# Verify tests
cd backend && uv run pytest tests/ -v
```

## Policy Violations

**Critical (Must Fix):** Committing to main, skipping hooks, breaking tests, security issues

**Warning (Should Fix):** Missing tests, outdated docs, non-standard commits
