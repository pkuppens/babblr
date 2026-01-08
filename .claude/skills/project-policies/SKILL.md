---
name: project-policies
description: Check and enforce project policies from CLAUDE.md and POLICIES.md. Use when validating implementations against project standards, checking code style requirements, or ensuring compliance with development guidelines.
allowed-tools: Read, Glob, Grep
---

# Project Policies

This skill ensures implementations comply with project policies and guidelines.

## Policy Documents

### Primary Policy Files
- `CLAUDE.md` - Development guidelines, code patterns, testing strategy
- `POLICIES.md` - User policies and developer workflow guidelines
- `docs/ARCHITECTURE.md` - System architecture and design decisions

### Always Check Before Implementation
1. Read `CLAUDE.md` for development guidelines
2. Read `POLICIES.md` Part 2 for developer policies
3. Check `docs/ARCHITECTURE.md` for architectural constraints

## Key Policies

### Git Workflow
- Never commit directly to `main`
- Use feature branches: `feature/<issue>-<description>`
- All changes through pull requests
- Commit format: `#<issue>: <type>: <description>`

### Code Quality
- Pre-commit hooks must pass
- No skipping hooks without approval
- Follow existing code patterns

### Testing Requirements
- Backend: pytest for unit/integration tests
- New features need tests
- Bug fixes need regression tests

### Documentation
- Update relevant docs with code changes
- Architecture changes need `docs/ARCHITECTURE.md` updates
- Keep `CLAUDE.md` current

## Compliance Checklist

Before submitting PR:

- [ ] On feature branch (not main)
- [ ] Commit messages follow convention
- [ ] Pre-commit hooks pass
- [ ] Tests pass
- [ ] Documentation updated if needed
- [ ] No security vulnerabilities introduced
- [ ] Follows existing code patterns

## Checking Compliance

### Verify Branch
```bash
git branch --show-current
# Should NOT be 'main'
```

### Verify Commit Format
```bash
git log --oneline -5
# Should show: #<issue>: <type>: <description>
```

### Verify Pre-commit
```bash
pre-commit run --all-files
# All checks should pass
```

### Verify Tests
```bash
cd backend && uv run pytest tests/ -v
# All tests should pass
```

## Policy Violations

### Critical (Must Fix)
- Committing to main
- Skipping pre-commit hooks
- Breaking existing tests
- Security vulnerabilities

### Warning (Should Fix)
- Missing tests for new code
- Outdated documentation
- Non-standard commit messages

### Minor (Consider)
- Code style inconsistencies
- Missing type hints
- Verbose implementations

## Updating Policies

If implementation reveals policy gaps:

1. Document the gap
2. Propose policy update
3. Update `CLAUDE.md` or `POLICIES.md`
4. Include policy update in PR

## Policy Reference Quick Links

### Development Guidelines
- See `CLAUDE.md` > "Quick Commands"
- See `CLAUDE.md` > "Architecture"
- See `CLAUDE.md` > "Testing Strategy"

### Developer Workflow
- See `POLICIES.md` > "Part 2: Developer Policies"
- See `POLICIES.md` > "Git Workflow"
- See `POLICIES.md` > "Pull Requests"

### Architecture Decisions
- See `docs/ARCHITECTURE.md`
- Check for ADRs (Architecture Decision Records)
