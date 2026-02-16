# Security Scanning Guide

This document describes Babblr's security scanning strategy and tools.

## Overview

Babblr uses multiple security scanning tools to detect vulnerabilities:

- **CodeQL** - Static analysis for Python and TypeScript
- **Gitleaks** - Secret scanning
- **pip-audit** - Python dependency vulnerability scanning
- **npm audit** - Node.js dependency vulnerability scanning
- **Dependabot** - Automated dependency updates

## CodeQL Analysis

### What is CodeQL?

CodeQL is GitHub's semantic code analysis engine that finds security vulnerabilities and coding errors.

### How It Works

1. Extracts code into a queryable database
2. Runs security and quality queries
3. Reports findings in Security tab

### Supported Languages

- Python (backend)
- TypeScript/JavaScript (frontend)

### Query Suite

We use the `security-and-quality` query suite which includes:
- Security vulnerabilities (SQL injection, XSS, etc.)
- Code quality issues
- Best practice violations

### Viewing Results

1. Go to **Security** tab → **Code scanning**
2. Filter by language or severity
3. Click alert for details and remediation

### Configuration

See `.github/workflows/security.yml`:

```yaml
- uses: github/codeql-action/init@v3
  with:
    languages: ${{ matrix.language }}
    queries: security-and-quality
```

## Gitleaks Secret Scanning

### What is Gitleaks?

Gitleaks detects hardcoded secrets, passwords, API keys, and tokens in your code.

### How It Works

1. Scans all commits in repository
2. Uses regex patterns to detect secrets
3. Fails workflow if secrets found

### What It Detects

- AWS keys
- GitHub tokens
- API keys
- Private keys
- Passwords
- Database connection strings

### False Positives

If Gitleaks flags something that isn't a secret:

1. Add to `.gitleaksignore` file
2. Document why it's safe
3. Re-run workflow

### Configuration

See `.github/workflows/security.yml`:

```yaml
- uses: gitleaks/gitleaks-action@v2
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Python Dependency Scanning (pip-audit)

### What is pip-audit?

pip-audit scans Python dependencies for known vulnerabilities using the OSV database.

### How It Works

1. Exports installed packages
2. Checks each package against vulnerability database
3. Reports known CVEs

### Configuration

See `.github/workflows/security.yml`:

```yaml
- name: Run pip-audit
  run: |
    uv pip freeze | uv run pip-audit --strict --desc on -r /dev/stdin
```

### Handling Vulnerabilities

If pip-audit finds a vulnerability:

1. Check if fixed in newer version
2. Update dependency: `uv pip install --upgrade <package>`
3. Re-run workflow
4. If no fix available, assess risk and document

## Node.js Dependency Scanning (npm audit)

### What is npm audit?

npm audit scans Node.js dependencies for known vulnerabilities using the npm registry.

### How It Works

1. Checks `package-lock.json`
2. Queries npm registry for vulnerabilities
3. Reports known CVEs

### Configuration

See `.github/workflows/security.yml`:

```yaml
- name: Run npm audit
  run: |
    npm audit --audit-level=moderate
```

### Audit Levels

- `low` - Low severity vulnerabilities
- `moderate` - Moderate severity (we fail at this level)
- `high` - High severity
- `critical` - Critical severity

### Handling Vulnerabilities

If npm audit finds a vulnerability:

1. Run `npm audit fix` to auto-fix
2. If that doesn't work, manually update: `npm install <package>@latest`
3. Re-run workflow
4. If no fix available, assess risk and document

## Dependabot

### What is Dependabot?

Dependabot automatically creates PRs to update outdated dependencies.

### Configuration

See `.github/dependabot.yml`:

```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/backend"
    schedule:
      interval: "0 3 1-7 * 0"  # First Sunday of month at 03:00 UTC
  - package-ecosystem: "npm"
    directory: "/frontend"
    schedule:
      interval: "0 3 1-7 * 0"  # First Sunday of month at 03:00 UTC
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "0 3 1-7 * 0"  # First Sunday of month at 03:00 UTC
```

### How It Works

1. Checks for updates monthly (first Sunday at 03:00 UTC)
2. Creates PR for each update
3. Runs CI on PR
4. Reviewer approves and merges

### Handling Dependabot PRs

1. Review PR description for changes
2. Check CI results
3. Test locally if needed
4. Approve and merge if safe

## Security Workflow Schedule

The security workflow runs:

- On every push to main (required for CodeQL Security tab alerts)
- On every pull request to main (including Dependabot dependency-update PRs)
- Manually via workflow dispatch

### Why No Scheduled Cron?

Security issues come from code and dependencies. New code triggers push or PR. New dependency vulnerabilities trigger Dependabot PRs, which run the security scan before merge. A separate schedule is redundant.

## Security Summary

After security scans complete, view summary in:

1. **Actions** tab → Latest security workflow run
2. Click **Summary** to see aggregated results
3. Check each scan status

## Best Practices

### 1. Never Commit Secrets

❌ **Bad**:
```python
API_KEY = "sk-1234567890abcdef"  # gitleaks:allow - example only
```

✅ **Good**:
```python
import os
API_KEY = os.environ.get("API_KEY")
```

### 2. Use Environment Variables

Store secrets in:
- `.env` file (ignored by git)
- GitHub Secrets (for CI)
- Environment variables (for production)

### 3. Review Security Alerts Promptly

- Check Security tab weekly
- Prioritize critical/high severity
- Update dependencies promptly

### 4. Keep Dependencies Updated

- Review Dependabot PRs monthly (first Sunday)
- Test updates before merging
- Monitor release notes for breaking changes

### 5. Use `.env.example`

Provide template for environment variables:

```bash
# .env.example
API_KEY=your_api_key_here
DATABASE_URL=postgresql://localhost/db
```

## OIDC Architecture (Future)

For cloud deployments, use OIDC instead of long-lived secrets:

```yaml
permissions:
  id-token: write
  contents: read

- name: Configure AWS credentials
  uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::123456789012:role/GitHubActionsRole
    aws-region: us-east-1
```

See [OIDC_SETUP.md](OIDC_SETUP.md) for details.

## Artifact Attestations

For releases, we generate artifact attestations for supply chain security:

```yaml
- uses: actions/attest-build-provenance@v1
  with:
    subject-path: 'dist/*'
```

Attestations prove:
- Who built the artifact
- When it was built
- What source code was used
- What workflow produced it

View attestations in GitHub UI on release page.

## Troubleshooting

### CodeQL Analysis Fails

**Symptom**: CodeQL job fails with analysis error

**Solutions**:
1. Check if code compiles
2. Review CodeQL logs for errors
3. Try manual CodeQL scan locally

### Gitleaks False Positives

**Symptom**: Gitleaks flags non-secret code

**Solutions**:
1. Add to `.gitleaksignore`
2. Use inline ignore comment
3. Re-run workflow

### Dependency Audit Fails

**Symptom**: pip-audit or npm audit fails

**Solutions**:
1. Update vulnerable dependency
2. Check if fix available
3. Assess risk if no fix
4. Document exception if safe

### Dependabot PR Causes npm ci to Fail (Peer Dependency)

**Symptom**: Node.js Dependency Audit job fails with `ERESOLVE could not resolve` or peer dependency conflict

**Cause**: Dependabot updated a package (e.g. eslint) to a major version that is not yet supported by peer dependencies (e.g. @typescript-eslint only supports eslint ^8 || ^9).

**Solutions**:
1. Add the package to `ignore` in `.github/dependabot.yml` for `version-update:semver-major` until peers support it
2. Close the Dependabot PR and wait for a new one without the incompatible update
3. Manually update only the compatible packages and skip the breaking one

## Resources

- [GitHub Security Features](https://docs.github.com/en/code-security)
- [CodeQL Documentation](https://codeql.github.com/)
- [Gitleaks Documentation](https://github.com/gitleaks/gitleaks)
- [pip-audit Documentation](https://github.com/pypa/pip-audit)
- [npm audit Documentation](https://docs.npmjs.com/cli/v10/commands/npm-audit)
- [Dependabot Documentation](https://docs.github.com/en/code-security/dependabot)
