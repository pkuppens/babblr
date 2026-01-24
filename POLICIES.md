# Policies and Guidelines

This document provides policies for using and developing Babblr.
It is not legal advice.

---

# Part 1: User Policies

## Acceptable use

You must not use Babblr to:

- Break the law, violate others' rights, or facilitate harm
- Attempt unauthorized access to systems, accounts, or data
- Generate or distribute malware
- Harass, threaten, or dox people

## AI output disclaimer

Babblr may produce incorrect or misleading output.

- You are responsible for verifying outputs before acting on them.
- Babblr is intended for language learning and conversational practice.
- Babblr does not provide professional advice (including medical, legal, or financial advice).

## Privacy note

Babblr may send your prompts to third-party AI providers depending on your configuration.
Do not input secrets or sensitive personal data unless you understand the implications.

See `ENVIRONMENT.md` for configuration details.

---

# Part 2: Developer Policies

These policies guide development practices for contributors.

## Git Workflow

### Branching Strategy
- **main**: Protected branch, always deployable
- **feature/\***: Feature branches for new work
- Never commit directly to `main`
- All changes go through pull requests

### Branch Naming
Use the format: `feature/ISSUE_NUMBER-short-description`
- Example: `feature/123-add-user-auth`
- Keep descriptions short (max 5 words)
- Use lowercase and hyphens

### Commit Messages
Format: `#ISSUE_NUMBER: type: description`

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `test`: Adding/updating tests
- `refactor`: Code refactoring
- `chore`: Maintenance tasks

Example: `#123: feat: add user authentication endpoint`

## Pull Requests

### Requirements
- Link to the GitHub issue being addressed
- Clear description of changes
- Tests pass (automated CI)
- Pre-commit hooks pass
- Documentation updated if needed

### Review Process
- Request review from maintainer (pkuppens)
- GitHub Copilot review for automated checks
- Address all review comments before merge
- Squash and merge preferred for clean history

## Code Quality

### Pre-commit Hooks
Pre-commit hooks are configured and must pass:
- Run automatically on commit
- Can be run manually: `pre-commit run --all-files`
- Never skip hooks (`--no-verify`) without explicit approval

### Testing Requirements
- Backend: pytest for unit and integration tests
- Frontend: Appropriate testing based on change type
- New features should include tests
- Bug fixes should include regression tests

### Documentation
- Update relevant documentation with code changes
- Architecture changes require `docs/ARCHITECTURE.md` updates
- Keep `CLAUDE.md` current with development guidelines

### Database Schema Documentation
All database models must be documented in `docs/DATABASE_SCHEMA.md`:

**Required for new models:**
- Mermaid ER diagram showing relationships
- Table definition with all columns, types, constraints, and descriptions
- Relationship descriptions (foreign keys, cascades)
- Validation rules for each field
- Examples of common query patterns

**Required for schema changes:**
- Update existing table documentation
- Update ER diagrams
- Document migration strategy if applicable
- Note any breaking changes

**Validation requirements:**
- All NOT NULL fields must have validation rules documented
- Enum/choice fields must list all valid values
- Numeric fields must specify valid ranges
- Date/time fields must document temporal constraints
- Foreign key relationships must be clearly defined

See `docs/DATABASE_SCHEMA.md` for the complete schema reference and documentation template.

## GitHub Actions and CI/CD

### Workflow Modification Policy

All changes to GitHub Actions workflows and composite actions require approval:

**Protected paths** (require @pkuppens approval):
- `.github/workflows/**` - All workflow files
- `.github/actions/**` - All composite actions
- `.github/dependabot.yml` - Dependency updates configuration
- `.github/CODEOWNERS` - Code ownership rules

**Enforcement**:
- CODEOWNERS file defines required reviewers
- Branch protection rules enforce approval requirements
- Automated tools (GitHub Copilot) may suggest but cannot merge without approval

**Rationale**:
- Workflows have elevated permissions and access to secrets
- Security implications of workflow changes must be reviewed
- Consistency in CI/CD patterns across repository
- Prevention of accidental breaking changes

### Security Workflow Changes

Changes to security scanning workflows require additional scrutiny:

**Review checklist**:
- Security tool configuration changes
- Permission elevation requests
- Secret access modifications
- New external actions added

**Documentation requirements**:
- Document why change is needed
- Document security implications
- Update security documentation if needed

### Pre-commit/Pre-push Alignment

Local checks should indicate if CI will likely pass:

**Pre-commit hooks** (fast checks):
- Ruff format and lint
- Gitleaks secret scanning
- Markdown validation

**Pre-push hooks** (slower checks):
- Unit tests
- Type checking
- Frontend tests

See `docs/ci/GITHUB_ACTIONS_GUIDE.md` for pre-push hook example.

### CI Failure Policy

If CI fails on your PR:

1. **Review logs** - Check which job failed and why
2. **Reproduce locally** - Run the same command locally
3. **Fix the issue** - Make necessary code changes
4. **Re-run CI** - Push fix or re-run failed jobs
5. **Don't skip checks** - Never merge with failing CI

See `docs/ci/TROUBLESHOOTING_CI.md` for common issues.

## Issue Management

### Issue Updates
- Add comments to track implementation progress
- Update issue description if requirements change
- Use labels appropriately (draft, blocked, etc.)

### Closed Issues
- Closed issues may be reopened if implementation doesn't match
- Verify closed issues still work when making related changes

