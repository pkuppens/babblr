# GitHub Actions Developer Guide

This guide explains how to work with Babblr's GitHub Actions workflows and composite actions.

## Quick Reference

### Setting Up Git Hooks

Git hooks are already configured via `.pre-commit-config.yaml` and run automatically:

**Pre-commit hooks** (run on every commit):
- Prevent commits to main branch
- Gitleaks secret scanning
- Ruff format and lint (Python)
- Pyright type checking (Python)
- Backend unit tests (fast, parallel)
- ESLint and Prettier (Frontend)
- Frontend tests
- Markdown validation

**To install hooks**:
```bash
# From project root
pre-commit install
```

**To run hooks manually**:
```bash
# Run all hooks on all files
pre-commit run --all-files

# Run specific hook
pre-commit run ruff-format --all-files
```

### Running CI Locally (Manual Check)

If you want to run CI checks manually (without git hooks):

```bash
# Backend lint checks
cd backend
uv run ruff format --check .
uv run ruff check .
uv run pyright

# Backend unit tests
uv run pytest tests/test_unit.py -v --tb=short -n auto

# Frontend checks
cd ../frontend
npm run lint
npm run format -- --check
npm run test
npm run build
```

**Note**: Pre-commit hooks already run most of these checks automatically. Manual checks are useful for debugging or when hooks are disabled.

### Triggering Integration Tests on PR

Integration tests normally only run on the `main` branch. To run them on a PR:

1. Add the `run-integration` label to your PR
2. Push a new commit or re-run the workflow

### Viewing Workflow Runs

- Go to **Actions** tab in GitHub
- Click on workflow name (e.g., "CI")
- View recent runs and logs

### Checking Security Scans

- Go to **Security** tab → **Code scanning**
- View CodeQL alerts
- View secret scanning alerts (if any)

## Workflows

### CI Workflow (`ci.yml`)

**Purpose**: Fast feedback on code quality

**Triggers**:
- Push to main
- Pull requests to main
- Push to feature branches
- Manual dispatch

**Jobs**:
1. `backend-lint` - Ruff format/lint, Pyright (Python 3.11, 3.12)
2. `backend-test-unit` - Unit tests (Python 3.11, 3.12)
3. `backend-test-integration` - Integration tests (main branch only)
4. `frontend-test` - ESLint, Prettier, Vitest, Build
5. `markdown-check` - Markdown validation
6. `ci-summary` - Aggregated results

**Expected runtime**:
- PR: ~4 minutes
- Main: ~12 minutes (with integration tests)

### Security Workflow (`security.yml`)

**Purpose**: Proactive vulnerability detection

**Triggers**:
- Push to main
- Pull requests to main
- Push and PR only; no schedule (event-driven)
- Manual dispatch

**Jobs**:
1. `codeql` - Static analysis (Python, TypeScript)
2. `gitleaks` - Secret scanning
3. `pip-audit` - Python dependency audit
4. `npm-audit` - Node.js dependency audit
5. `security-summary` - Aggregated results

**Expected runtime**: ~10 minutes

### Release Workflow (`release.yml`)

**Purpose**: Automated release creation

**Triggers**:
- Git tags (`v*.*.*`)
- Manual dispatch

**Jobs**:
1. `build-backend` - Build Python wheel
2. `build-frontend` - Build Electron app
3. `attest` - Generate attestations
4. `create-release` - Create GitHub release (requires approval)
5. `release-summary` - Aggregated results

**Expected runtime**: ~15 minutes

## Composite Actions

Reusable actions in `.github/actions/`:

### `setup-python`

Sets up Python with UV and caching.

**Example**:
```yaml
- uses: ./.github/actions/setup-python
  with:
    python-version: '3.12'
    cache-key-prefix: 'lint'
    working-directory: 'backend'
```

### `setup-node`

Sets up Node.js with npm caching.

**Example**:
```yaml
- uses: ./.github/actions/setup-node
  with:
    node-version: '20'
    working-directory: 'frontend'
```

### `ruff`

Runs Ruff format and lint checks.

**Example**:
```yaml
- uses: ./.github/actions/ruff
  with:
    working-directory: 'backend'
```

### `run-backend-tests`

Runs backend pytest tests.

**Example**:
```yaml
- uses: ./.github/actions/run-backend-tests
  with:
    test-type: 'unit'  # or 'integration' or 'llm_providers'
    cache-whisper: 'true'
```

### `run-frontend-tests`

Runs frontend tests.

**Example**:
```yaml
- uses: ./.github/actions/run-frontend-tests
  with:
    skip-build: 'false'
```

## Configuration Variables

Set in GitHub repo settings → Secrets and variables → Actions → Variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `SUPPORTED_PYTHON_VERSIONS` | `["3.11", "3.12"]` | Python versions to test |
| `ARTIFACT_RETENTION_DAYS` | `90` | Days to keep artifacts |

## Debugging Failed Workflows

### Step 1: View Logs

1. Go to **Actions** tab
2. Click on failed workflow run
3. Click on failed job
4. Expand failed step to view logs

### Step 2: Reproduce Locally

```bash
# Run the exact commands from the failed step
cd backend
uv run pytest tests/test_unit.py -v --tb=short -n auto
```

### Step 3: Check Cache Issues

If you see cache-related issues:

1. Go to **Actions** tab → **Caches**
2. Delete old caches
3. Re-run workflow

### Step 4: Re-run Workflow

- Click **Re-run jobs** → **Re-run failed jobs**
- Or push a new commit to trigger workflow again

## Common Issues

### Integration Tests Not Running

**Symptom**: Integration tests skipped on PR

**Solution**: Add `run-integration` label to PR

### Stale Cache Issues

**Symptom**: Build fails with dependency mismatch

**Solution**: Delete caches in Actions tab → Caches

### Matrix Build Failures

**Symptom**: One Python version fails, others succeed

**Solution**: Fix the failing version or adjust matrix configuration

### Permission Denied Errors

**Symptom**: Workflow fails with permission errors

**Solution**: Check `permissions:` block in workflow file

## Best Practices

### 1. Use Composite Actions

Don't repeat setup steps - use composite actions:

❌ **Bad**:
```yaml
- name: Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: '3.12'
- name: Install uv
  run: curl -LsSf https://astral.sh/uv/install.sh | sh
- name: Install dependencies
  run: uv sync --dev
```

✅ **Good**:
```yaml
- uses: ./.github/actions/setup-python
  with:
    python-version: '3.12'
    cache-key-prefix: 'test'
```

### 2. Use Fail-Fast Matrices

Enable fail-fast to stop early on failures:

```yaml
strategy:
  fail-fast: true
  matrix:
    python-version: ['3.11', '3.12']
```

### 3. Use Concurrency Control

Cancel stale runs to save time:

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

### 4. Use Least Privilege Permissions

Default to read-only, elevate per-job:

```yaml
permissions:
  contents: read

jobs:
  security-scan:
    permissions:
      security-events: write
      contents: read
```

### 5. Cache Aggressively

Cache dependencies and build artifacts:

```yaml
- uses: actions/cache@v4
  with:
    path: ~/.cache/uv
    key: uv-${{ runner.os }}-${{ hashFiles('backend/uv.lock') }}
```

## Pre-push Hook

Create `.git/hooks/pre-push` to run checks before pushing:

```bash
#!/bin/bash
echo "[INFO] Running pre-push checks..."

# Check if on main branch
BRANCH=$(git branch --show-current)
if [ "$BRANCH" == "main" ]; then
  echo "[ERROR] Cannot push directly to main"
  exit 1
fi

# Run lint checks
echo "[INFO] Running lint checks..."
cd backend && uv run ruff format --check . && uv run ruff check .
if [ $? -ne 0 ]; then
  echo "[ERROR] Lint checks failed"
  exit 1
fi

# Run unit tests
echo "[INFO] Running unit tests..."
cd backend && uv run pytest tests/test_unit.py -v --tb=short -n auto
if [ $? -ne 0 ]; then
  echo "[ERROR] Unit tests failed"
  exit 1
fi

echo "[OK] Pre-push checks passed - CI should succeed"
```

Make it executable:
```bash
chmod +x .git/hooks/pre-push
```

## Modifying Workflows

### Adding a New Job

1. Edit workflow file (e.g., `ci.yml`)
2. Add job definition
3. Set dependencies with `needs:`
4. Test in PR before merging

**Example**:
```yaml
jobs:
  my-new-job:
    name: My New Job
    runs-on: ubuntu-latest
    needs: lint  # Run after lint job
    steps:
      - uses: actions/checkout@v4
      - run: echo "Hello World"
```

### Creating a New Composite Action

1. Create directory: `.github/actions/my-action/`
2. Create `action.yml` file
3. Define inputs and steps
4. Use in workflows

**Example**:
```yaml
name: 'My Action'
description: 'Does something useful'
inputs:
  my-input:
    description: 'Input description'
    required: true

runs:
  using: 'composite'
  steps:
    - name: Do something
      shell: bash
      run: echo "${{ inputs.my-input }}"
```

### Testing Workflow Changes

1. Create feature branch
2. Modify workflow file
3. Push to trigger workflow
4. View results in Actions tab
5. Iterate until working
6. Merge to main

## CODEOWNERS and Approval

All changes to `.github/workflows/**` and `.github/actions/**` require approval from @pkuppens per CODEOWNERS file.

This ensures:
- Security review of CI changes
- Consistency in workflow patterns
- Prevention of accidental breaking changes

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Composite Actions Guide](https://docs.github.com/en/actions/creating-actions/creating-a-composite-action)
- [Workflow Syntax Reference](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [CI Pipeline Architecture](CI_PIPELINE.md)
- [Security Scanning Guide](SECURITY_SCANNING.md)
- [Release Process Guide](RELEASE_PROCESS.md)
