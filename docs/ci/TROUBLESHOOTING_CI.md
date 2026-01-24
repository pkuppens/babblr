# CI Troubleshooting Guide

This guide helps you debug common CI/CD issues in Babblr's GitHub Actions workflows.

## Quick Diagnosis

### Is CI Failing?

1. Go to **Actions** tab in GitHub
2. Find your workflow run
3. Check which job failed (red X icon)
4. Click on failed job to view logs

### Can't Find the Issue?

Check these common culprits:
- Lint errors (Ruff format/check)
- Type errors (Pyright)
- Test failures (pytest, Vitest)
- Dependency issues (outdated lock files)
- Cache corruption
- Permissions issues

## Common Issues and Solutions

### 1. Lint Failures

#### Ruff Format Check Fails

**Symptom**:
```
ruff format --check .
Would reformat: app/main.py
```

**Solution**:
```bash
cd backend
uv run ruff format .
git add .
git commit -m "fix: format code with ruff"
git push
```

#### Ruff Lint Check Fails

**Symptom**:
```
ruff check .
app/main.py:10:1: F401 [*] `os` imported but unused
```

**Solution**:
```bash
cd backend
uv run ruff check --fix .
# Review changes
git add .
git commit -m "fix: resolve ruff lint issues"
git push
```

### 2. Type Check Failures

#### Pyright Type Error

**Symptom**:
```
pyright
app/main.py:15:5 - error: Argument of type "str" cannot be assigned to parameter "x" of type "int"
```

**Solution**:
- Fix type annotations in code
- Add type ignore comment if false positive: `# type: ignore`
- Check if imports are correct

```python
# Before
def process(x: int) -> str:
    return x  # Error: int not compatible with str

# After
def process(x: int) -> str:
    return str(x)  # Fixed: convert to string
```

### 3. Test Failures

#### Unit Test Fails

**Symptom**:
```
pytest tests/test_unit.py
FAILED tests/test_unit.py::test_conversation_create - AssertionError
```

**Solution**:
```bash
# Run specific test locally with verbose output
cd backend
uv run pytest tests/test_unit.py::test_conversation_create -vv --tb=long

# Debug with pdb
uv run pytest tests/test_unit.py::test_conversation_create -vv --pdb
```

**Common causes**:
- Incorrect test assumptions
- Database state issues
- Mocked functions not working as expected
- Environment variables missing

#### Integration Test Fails

**Symptom**:
```
pytest tests/test_integration.py
FAILED tests/test_integration.py::test_api_endpoint
```

**Solution**:
- Integration tests need backend running
- Check if API keys are set (in GitHub Secrets)
- Verify idempotency (use unique test IDs)

### 4. Dependency Issues

#### UV Lock File Out of Date

**Symptom**:
```
uv sync
error: Lock file is out of date
```

**Solution**:
```bash
cd backend
uv lock --upgrade
git add uv.lock
git commit -m "chore: update uv lock file"
git push
```

#### NPM Lock File Out of Date

**Symptom**:
```
npm ci
npm ERR! `package-lock.json` out of date
```

**Solution**:
```bash
cd frontend
npm install
git add package-lock.json
git commit -m "chore: update package-lock.json"
git push
```

### 5. Cache Issues

#### Stale Cache Causing Build Failures

**Symptom**:
- Build works locally but fails in CI
- Dependencies seem mismatched
- Old files being used

**Solution**:

**Option 1: Delete cache via GitHub UI**
1. Go to **Actions** tab
2. Click **Caches** in left sidebar
3. Find and delete relevant caches
4. Re-run workflow

**Option 2: Clear cache in workflow**

Add to workflow:
```yaml
- name: Clear cache
  run: |
    rm -rf ~/.cache/uv
    rm -rf ~/.local/share/uv
```

**Option 3: Change cache key**

Temporarily modify cache key to force new cache:
```yaml
key: uv-v2-${{ runner.os }}-${{ hashFiles('backend/uv.lock') }}
```

### 6. Concurrency Issues

#### Workflow Cancelled Unexpectedly

**Symptom**:
```
Canceling since a higher priority waiting request exists
```

**Explanation**:
- Concurrency control cancels old runs when new commit pushed
- This is **expected behavior** and saves runner time

**Solution**:
- No action needed - latest commit will run
- If you need old run, disable concurrency temporarily

#### Multiple Workflows Running Simultaneously

**Symptom**:
- Same workflow running multiple times
- Confusion about which run to check

**Solution**:
- Wait for latest run to complete
- Cancel old runs manually if needed
- Check concurrency group configuration:

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

### 7. Matrix Build Failures

#### One Python Version Fails, Others Pass

**Symptom**:
```
Python 3.12: ✅ Success
Python 3.11: ❌ Failed
```

**Solution**:
- Check if code uses Python 3.12-specific features
- Test locally with specific Python version:

```bash
# Use uv to test with specific Python version
cd backend
uv run --python 3.11 pytest tests/test_unit.py -v
```

**Common causes**:
- `match` statement (Python 3.10+)
- Type hints (some require newer versions)
- Library version incompatibilities

### 8. Permission Errors

#### Permission Denied Writing to Repository

**Symptom**:
```
Error: Resource not accessible by integration
```

**Solution**:
- Check `permissions:` block in workflow
- Ensure job has necessary permissions:

```yaml
permissions:
  contents: write  # For creating releases
  security-events: write  # For CodeQL
```

#### Can't Access Secrets

**Symptom**:
```
Error: ANTHROPIC_API_KEY environment variable not set
```

**Solution**:
1. Go to repo Settings → Secrets and variables → Actions
2. Add secret with correct name
3. Reference in workflow:

```yaml
env:
  ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

### 9. Security Scan Failures

#### CodeQL Analysis Fails

**Symptom**:
```
CodeQL analysis failed
```

**Solutions**:
- Check if code compiles/builds successfully
- Review CodeQL logs for specific errors
- Try running CodeQL locally (if possible)

#### Gitleaks Detects Secret

**Symptom**:
```
Gitleaks detected secrets in commit abc1234
```

**Solutions**:

**Option 1: Remove secret from code**
```bash
# Remove secret
git commit -m "fix: remove hardcoded secret"
git push
```

**Option 2: Add to .gitleaksignore (if false positive)**
```bash
# Create .gitleaksignore
echo "path/to/file:line_number" >> .gitleaksignore
git add .gitleaksignore
git commit -m "chore: add gitleaks ignore"
git push
```

#### pip-audit Finds Vulnerability

**Symptom**:
```
pip-audit
Found 1 vulnerability: requests==2.28.0 (CVE-2023-xxxxx)
```

**Solutions**:
```bash
cd backend
# Update vulnerable package
uv pip install --upgrade requests
# Regenerate lock file
uv lock
git add uv.lock
git commit -m "fix: update requests to resolve CVE"
git push
```

#### npm audit Finds Vulnerability

**Symptom**:
```
npm audit
High severity vulnerability in lodash
```

**Solutions**:
```bash
cd frontend
# Try auto-fix
npm audit fix

# If that doesn't work, update manually
npm install lodash@latest

git add package.json package-lock.json
git commit -m "fix: update lodash to resolve vulnerability"
git push
```

### 10. Integration Test Not Running

#### Integration Test Skipped on PR

**Symptom**:
```
Backend Integration Tests: ⏭️ Skipped
```

**Explanation**:
- Integration tests only run on `main` branch by default
- This is intentional to reduce API costs

**Solution**:
- Add `run-integration` label to PR
- Push new commit or re-run workflow

### 11. Frontend Build Failures

#### TypeScript Compilation Error

**Symptom**:
```
npm run build
src/App.tsx:10:5 - error TS2322: Type 'string' is not assignable to type 'number'
```

**Solution**:
- Fix TypeScript errors in code
- Run `npm run build` locally to catch errors early

#### Vite Build Fails

**Symptom**:
```
npm run build
[vite] error: Could not resolve...
```

**Solutions**:
- Check if all imports are correct
- Verify dependencies installed: `npm ci`
- Clear node_modules and reinstall

### 12. Markdown Check Failures

#### Broken Link Detected

**Symptom**:
```
remark-validate-links
Link to docs/MISSING.md is broken
```

**Solution**:
- Fix broken link or create missing file
- Update all references to use correct path

#### Markdown Linting Error

**Symptom**:
```
markdownlint-cli2
README.md:5 MD001 Heading levels should only increment by one level at a time
```

**Solution**:
```bash
# Run markdownlint locally
npm install -g markdownlint-cli2
markdownlint-cli2 "**/*.md"

# Fix issues in files
git add .
git commit -m "docs: fix markdown linting issues"
git push
```

## Advanced Debugging

### Viewing Full Logs

1. Go to failed job in Actions tab
2. Click on failed step
3. Scroll through logs
4. Look for "Error:" or "FAILED" messages
5. Note line numbers and file names

### Re-running Workflows

**Re-run all jobs**:
1. Go to workflow run
2. Click **Re-run jobs** → **Re-run all jobs**

**Re-run failed jobs only**:
1. Go to workflow run
2. Click **Re-run jobs** → **Re-run failed jobs**

### Debugging with tmate (Advanced)

For interactive debugging, use tmate action:

```yaml
- name: Setup tmate session
  uses: mxschmitt/action-tmate@v3
  if: failure()
```

**Warning**: This exposes a shell session. Use with caution.

### Local CI Simulation

Run CI checks locally before pushing:

```bash
# Backend lint
cd backend
uv run ruff format --check .
uv run ruff check .
uv run pyright

# Backend tests
uv run pytest tests/test_unit.py -v -n auto

# Frontend
cd frontend
npm run lint
npm run format -- --check
npm run test
npm run build
```

## Getting Help

### Still Stuck?

1. Check this troubleshooting guide
2. Check GitHub Actions documentation
3. Check tool-specific documentation:
   - [Ruff](https://docs.astral.sh/ruff/)
   - [Pyright](https://github.com/microsoft/pyright)
   - [pytest](https://docs.pytest.org/)
   - [Vitest](https://vitest.dev/)
4. Search GitHub Issues for similar problems
5. Create new issue with:
   - Workflow run link
   - Full error message
   - Steps to reproduce

### Reporting CI Issues

When reporting issues, include:

1. **Workflow run link**: Direct link to failed run
2. **Error message**: Copy full error from logs
3. **Job name**: Which job failed (e.g., "backend-lint")
4. **Context**: What changed recently
5. **Local reproduction**: Can you reproduce locally?

## Prevention

### Before Pushing

Run pre-push checks:

```bash
#!/bin/bash
# Save as .git/hooks/pre-push

echo "[INFO] Running pre-push checks..."

# Lint
cd backend && uv run ruff format --check . && uv run ruff check .
if [ $? -ne 0 ]; then
  echo "[ERROR] Lint failed"
  exit 1
fi

# Tests
cd backend && uv run pytest tests/test_unit.py -v --tb=short -n auto
if [ $? -ne 0 ]; then
  echo "[ERROR] Tests failed"
  exit 1
fi

echo "[OK] Pre-push checks passed"
```

### During Development

- Run linters frequently: `uv run ruff check .`
- Run tests after changes: `uv run pytest tests/test_unit.py -v`
- Keep dependencies updated: Review Dependabot PRs
- Monitor CI status: Check Actions tab regularly

## Resources

- [CI Pipeline Architecture](CI_PIPELINE.md)
- [GitHub Actions Guide](GITHUB_ACTIONS_GUIDE.md)
- [Security Scanning Guide](SECURITY_SCANNING.md)
- [GitHub Actions Logs Documentation](https://docs.github.com/en/actions/monitoring-and-troubleshooting-workflows/using-workflow-run-logs)
