# CLAUDE.md

This file is the index for AI coding agents that work in this repository. It
holds the rules that apply to every session. Topic detail lives in the linked
files, which agents read on demand.

> **Note**: This is a living document. Update it when project conventions
> change. Keep it short — put detail in `docs/agents/` or the reference docs.

## Working Style

**Be a critical thinker, not a yes-machine.** The user may not know everything,
and that is fine. Your job is to:

- **Challenge assumptions** when you see issues, gaps, or better alternatives
- **Point out risks** before they become problems (security, performance, maintainability)
- **Ask clarifying questions** rather than guess or make silent assumptions
- **Disagree respectfully** when you have technical concerns. Explain your reasoning.
- **Suggest improvements** even when nobody asked, if you see something wrong

However, **the user stays in control**. After you voice a concern:

- Accept the user's final decision
- Do what they ask, even if you advised otherwise
- Do not repeat an objection after they acknowledge it

This applies to code, architecture, documentation, and process decisions.

## Language and Writing Style

Babblr is multilingual by nature. Write all natural language — comments,
docstrings, identifiers, commit messages, PR and issue text, Markdown docs, and
English UI text — in **ASD-STE100 Simplified Technical English (STE)**: short
active sentences, simple tenses, common words, no long noun clusters.

Exceptions: language-learning content in the target languages, English written
to a set CEFR level (most notably C1-C2 tutor material), and verbatim
third-party text. When you are not sure, ask.

Full guidance: [`docs/agents/writing-style.md`](docs/agents/writing-style.md).

## Startup: Branch Check

At the start of every conversation, check the branch:

```bash
git branch --show-current
```

If you are on `main`:

1. **Stop and tell the user.** Direct commits to `main` are not allowed.
2. Switch to a feature branch, or create one from the latest `origin/main`:
   ```bash
   git fetch origin
   git checkout -b feature/<issue>-<short-description> origin/main
   ```
3. Do not change any code until you are on a feature branch.

This keeps every change on a pull request, for review and CI.

## Project Overview

Babblr is a desktop language learning app for conversational practice with an AI
tutor. It supports Spanish, Italian, German, French, Dutch, and English, with
adaptive CEFR difficulty levels (A1-C2).

- **Frontend**: Electron + React + TypeScript (`frontend/`)
- **Backend**: Python FastAPI, async SQLite via SQLAlchemy (`backend/`)
- **LLM providers**: swappable (ollama, claude, gemini, mock), set by `LLM_PROVIDER`

## Documentation Map

### Agent guides (`docs/agents/`)

| File | Read it when you need |
| --- | --- |
| [`writing-style.md`](docs/agents/writing-style.md) | The STE rules, examples, and the shell-script text convention |
| [`commands.md`](docs/agents/commands.md) | Backend, frontend, or Docker commands |
| [`architecture.md`](docs/agents/architecture.md) | Code layout, the LLM provider pattern, how to add an endpoint or provider, the test strategy |
| [`ci-cd.md`](docs/agents/ci-cd.md) | Workflow overview, pre-push checks, the rule that workflow changes need @pkuppens approval |
| [`understand-anything.md`](docs/agents/understand-anything.md) | To build or view the codebase knowledge graph |
| [`issue-tracker.md`](docs/agents/issue-tracker.md) | GitHub Issues conventions (the `gh` CLI) |
| [`triage-labels.md`](docs/agents/triage-labels.md) | The five canonical triage labels |
| [`domain.md`](docs/agents/domain.md) | To read `CONTEXT.md` and `docs/adr/` before you explore the code |

Agent guides are not preloaded into context. A skill (for example `/to-tickets`
or `/triage`) reads the file it needs when it needs it.

### Reference docs

| File | Content |
| --- | --- |
| [`POLICIES.md`](POLICIES.md) | Git workflow, branch naming, commit format, PR requirements, GitHub Actions policy |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Contributor guide, code style, AI-assisted development, licensing |
| [`DEVELOPMENT.md`](DEVELOPMENT.md) | Full development workflow and project structure |
| [`ENVIRONMENT.md`](ENVIRONMENT.md) | API key and environment variable configuration |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Full system architecture and design decisions |
| [`docs/adr/`](docs/adr/) | Architecture Decision Records |
| [`CONTEXT.md`](CONTEXT.md) | Domain terms and bounded-context notes |
| [`VALIDATION.md`](VALIDATION.md) | Smoke-test checklist |
| [`backend/tests/README.md`](backend/tests/README.md) | Test documentation |
| [`docs/ci/CI_PIPELINE.md`](docs/ci/CI_PIPELINE.md) | CI/CD pipeline architecture |
| [`docs/ci/GITHUB_ACTIONS_GUIDE.md`](docs/ci/GITHUB_ACTIONS_GUIDE.md) | GitHub Actions developer guide |
| [`docs/ci/SECURITY_SCANNING.md`](docs/ci/SECURITY_SCANNING.md) | Security scanning tools and process |
| [`docker/README.md`](docker/README.md) | Docker Compose setup |

## Git Workflow (summary)

Full policy: [`POLICIES.md`](POLICIES.md).

- **Branch naming**: `feature/<issue>-<short-description>` (for example `feature/123-add-user-auth`)
- **Commit format**: `#<issue>: <type>: <description>`, where `<type>` is one of
  `feat`, `fix`, `docs`, `test`, `refactor`, `chore`
- **PR requirements**: link the issue, tests pass, pre-commit hooks pass
- Never commit to `main`. Every change goes through a pull request.
