---
description: Implement a GitHub issue following project policies and best practices
argument-hint: <issue-number>
---

# Implement GitHub Issue

Implement issue #$ARGUMENTS following project policies. This command orchestrates multiple skills for a complete workflow.

**If no issue number provided, list open issues:**
```bash
gh issue list --state open --limit 10
```

## Skills Used

This command uses these skills (Claude will auto-activate them):
- **github-issue** - Fetch, update, comment on issues
- **git-workflow** - Branch management, commits, PRs
- **codebase-analysis** - Check existing implementation and tests
- **project-policies** - Ensure compliance with guidelines

## Workflow

### Phase 1: Setup & Analysis

1. **Check prerequisites**
   ```bash
   gh --version || echo "Install gh CLI: https://cli.github.com/"
   git branch --show-current
   ```

2. **Check for existing work**
   - Look for `.tmp/<issue>-*.md` scratch file
   - Check for existing branch `feature/<issue>-*`
   - If found, offer to resume with recap

3. **Fetch issue** (uses github-issue skill)
   ```bash
   gh issue view $ARGUMENTS --json number,title,body,state,labels,comments
   ```

4. **Read policies** (uses project-policies skill)
   - Read `CLAUDE.md` and `POLICIES.md`
   - Note any relevant constraints

5. **Create scratch file** at `.tmp/<issue>-<slug>.md`

### Phase 2: Review & Validate

1. **Analyze issue against codebase** (uses codebase-analysis skill)
   - Search for related code
   - Check test coverage
   - Identify what exists vs what's needed

2. **Check for discrepancies**
   - If issue description outdated: propose update
   - If code doesn't match issue: present options
   - Recommend based on policies

3. **Update issue if needed** (uses github-issue skill)
   - Update description with findings
   - Add analysis comment

### Phase 3: Implement

1. **Create/switch to feature branch** (uses git-workflow skill)
   ```bash
   git checkout -b feature/$ARGUMENTS-<slug> main
   ```

2. **Implement changes**
   - Follow patterns from codebase
   - Add tests as appropriate
   - Make small, logical commits

3. **Update documentation** if needed
   - `VALIDATION.md` for user-facing features
   - `docs/ARCHITECTURE.md` for architecture changes

### Phase 4: Finalize

1. **Run pre-commit** (uses project-policies skill)
   ```bash
   pre-commit run --all-files
   ```

2. **Run tests** (uses codebase-analysis skill)
   ```bash
   cd backend && uv run pytest tests/ -v
   ```

3. **Create PR** (uses git-workflow skill)
   ```bash
   gh pr create --title "#$ARGUMENTS: <title>" --reviewer pkuppens
   ```

4. **Update issue** (uses github-issue skill)
   - Add completion comment with PR link
   - Close if fully implemented

5. **Update scratch file** with final status

## Resume Capability

If `.tmp/<issue>-*.md` exists:
1. Read scratch file for context
2. Show recap of completed checkpoints
3. Ask: Continue from checkpoint or start fresh?

## Decision Points

At each decision point:
1. Check policies first for guidance
2. Only ask user if policies don't resolve
3. Document decisions in scratch file

## Output

Provide summary:
- PR link
- Key decisions made
- Any follow-up items
- Manual testing steps if applicable
