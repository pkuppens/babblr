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

## Issue Management

### Issue Updates
- Add comments to track implementation progress
- Update issue description if requirements change
- Use labels appropriately (draft, blocked, etc.)

### Closed Issues
- Closed issues may be reopened if implementation doesn't match
- Verify closed issues still work when making related changes

