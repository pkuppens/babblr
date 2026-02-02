# Security Requirements

## Purpose

Security requirements and controls.

## Threat Model

### Threats
1. API key exposure
2. SQL injection
3. Dependency vulnerabilities

### Mitigations
1. Environment variables, .gitignore
2. SQLAlchemy ORM (parameterized queries)
3. Dependabot, npm audit, pip-audit

## Security Controls

### API Key Protection
- **Storage**: .env files, not committed to git
- **Access**: Backend only, not exposed to frontend

### SQL Injection Prevention
- **ORM**: SQLAlchemy with parameterized queries
- **Validation**: Pydantic schemas

### Dependency Scanning
- **Tools**: Dependabot, CodeQL, pip-audit, npm audit
- **Frequency**: Weekly automated scans
- **Policy**: Critical vulnerabilities patched within 7 days

## Secure Development

- Pre-commit hooks (Ruff linting)
- Code review required before merge
- CI/CD security checks

See [docs/ci/SECURITY_SCANNING.md](../../ci/SECURITY_SCANNING.md)

---

**Version**: 1.0.0
**Last Updated**: 2026-02-02
