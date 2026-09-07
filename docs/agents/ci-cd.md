# CI/CD for agents

Short, agent-facing summary. For the full pipeline, see
[`docs/ci/CI_PIPELINE.md`](../ci/CI_PIPELINE.md),
[`docs/ci/GITHUB_ACTIONS_GUIDE.md`](../ci/GITHUB_ACTIONS_GUIDE.md), and
[`docs/ci/SECURITY_SCANNING.md`](../ci/SECURITY_SCANNING.md).

## Workflows

| Workflow | File | Runs on | Jobs |
| --- | --- | --- | --- |
| CI | `.github/workflows/ci.yml` | push to main, PRs, feature branches | backend lint and test (Python 3.11, 3.12), frontend test, markdown checks |
| Security | `.github/workflows/security.yml` | push to main, PRs, weekly on Monday | CodeQL, Gitleaks, pip-audit, npm audit |
| Release | `.github/workflows/release.yml` | git tags (`v*.*.*`), manual dispatch | build backend and frontend, generate attestations, create the release |

## Composite actions (`.github/actions/`)

- `setup-python` - Python and UV setup, with caching
- `setup-node` - Node.js setup, with npm caching
- `ruff` - Ruff format and lint checks
- `run-backend-tests` - backend pytest runner
- `run-frontend-tests` - frontend test runner

## Key behaviour

- **Concurrency control**: a new push cancels stale PR runs.
- **Fail-fast matrices**: if Python 3.12 fails, the 3.11 job stops.
- **Conditional execution**: integration tests run only on `main`, or on a PR
  with the `run-integration` label. To run them on a PR, add the label, then
  push a commit or re-run the workflow.
- **Least privilege**: the default token permission is `contents: read`. Jobs
  raise it only when they need to.

## Rule: workflow changes need approval

All changes to `.github/workflows/**` and `.github/actions/**` need approval
from @pkuppens, per CODEOWNERS.

To test a workflow change: create a feature branch, change the file, push to
trigger the run, then read the result in the Actions tab. Repeat until it works.

## Pre-push checks

Run these local checks before you push. They predict the CI result.

```bash
# Backend (from backend/)
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest tests/test_unit.py -vv --tb=short -n 8

# Frontend (from frontend/)
npm run lint
npm run format -- --check
npm run test
npm audit --audit-level=moderate
```

## When CI fails

1. Read the logs in the Actions tab.
2. Reproduce the failure locally with the same command.
3. Fix the cause.
4. Push, or re-run the workflow.

See [`docs/ci/TROUBLESHOOTING_CI.md`](../ci/TROUBLESHOOTING_CI.md) for more.

## Security scans

Weekly scans run CodeQL (Python and TypeScript), Gitleaks, pip-audit, and npm
audit. Results are in the Security tab, under Code scanning.
