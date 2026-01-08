---
description: Implement a GitHub issue following project policies and best practices
argument-hint: <issue-number>
---

# Implement GitHub Issue Workflow

You are implementing a GitHub issue for this repository. Follow this workflow carefully, using project policies as your guide. Be interactive at key decision points, but resolve decisions from policies when possible.

## Issue Number

$ARGUMENTS

**If no issue number was provided above, ask the user for the issue number before proceeding. List the open github issues with number and title as suggestions.**

---

## Prerequisites Check

Before starting, verify the environment is ready:

### 1. Check gh CLI
```bash
gh --version
```
If not installed, inform the user:
> GitHub CLI (`gh`) is required. Install from: https://cli.github.com/
> After installation, run `gh auth login` to authenticate.

### 2. Check Current Branch
```bash
git branch --show-current
```
If on `main`, you'll create a feature branch in Phase 2.

### 3. Check for Existing Work
Look for existing scratch files and branches:
```bash
# Check for scratch file
ls .tmp/*-*.md 2>/dev/null || echo "No existing scratch files"

# Check for existing branch
git branch -a | grep -i "feature/ISSUE_NUMBER" || echo "No existing branch"
```

If existing work is found, offer to **resume with a recap** of previous progress.

---

## Phase 1: FETCH & ANALYZE ISSUE

### 1.1 Fetch Issue Details
```bash
gh issue view ISSUE_NUMBER --json number,title,body,state,labels,comments,assignees
```

### 1.2 Read Project Policies
Before making any decisions, read and understand:
- `CLAUDE.md` - Development guidelines and working style
- `POLICIES.md` - Project policies and acceptable use
- `docs/DEVELOPMENT.md` (if exists) - Development workflow

### 1.3 Create Scratch File
Create `.tmp/ISSUE_NUMBER-title-slug.md` to track progress:
```markdown
# Issue #ISSUE_NUMBER: [Title]

## Status: analyzing | in_progress | ready_for_review | blocked
## Branch: feature/ISSUE_NUMBER-title-slug
## Started: [date]
## Last Updated: [date]

## Issue Summary
[Original issue description]

## Analysis
[Your analysis of what needs to be done]

## Checkpoints
- [ ] Issue reviewed and validated
- [ ] Implementation planned
- [ ] Code implemented
- [ ] Tests written
- [ ] Documentation updated
- [ ] Pre-commit hooks pass
- [ ] PR created

## Decisions Made
[Document key decisions and their rationale]

## Blockers
[Any blockers encountered]
```

### 1.4 Analyze Issue State & Labels

Consider issue metadata as implementation hints:
- **State: open** - Normal implementation flow
- **State: closed** - Verify implementation still matches description
- **Label: draft** - More freedom to suggest issue edits
- **Label: blocked** - Check and update blocker status
- **Label: bug** - Focus on fix + regression test
- **Label: enhancement** - May need architecture consideration

---

## Phase 2: REVIEW & VALIDATE ISSUE

### 2.1 Check Issue Accuracy
Compare issue description against:
1. Current codebase state
2. Project policies in `CLAUDE.md` and `POLICIES.md`
3. Project vision and architecture patterns

### 2.2 Identify Discrepancies
If code exists but doesn't match the issue:
- Present both options:
  - (a) Propose changes to align **code with issue**
  - (b) Propose changes to align **issue with code**
- Make a recommendation based on policies and project vision
- Ask user only if policies don't provide clear guidance

### 2.3 Update Issue if Needed
If the issue title or description needs updating:
```bash
# Update title
gh issue edit ISSUE_NUMBER --title "Updated title"

# Update body (use heredoc for multiline)
gh issue edit ISSUE_NUMBER --body "$(cat <<'EOF'
Updated description here...
EOF
)"

# Add comment explaining changes
gh issue comment ISSUE_NUMBER --body "$(cat <<'EOF'
## Issue Updated

**Changes made:**
- [List changes]

**Reason:**
- [Explain why updates were needed]
EOF
)"
```

---

## Phase 3: CHECK EXISTING IMPLEMENTATION

### 3.1 Search for Related Code
Search the codebase for existing implementation:
```bash
# Search for keywords from issue title/description
# Look in relevant directories based on issue type
```

### 3.2 Check Test Coverage
```bash
# Run relevant tests
cd backend && uv run pytest tests/ -v --collect-only | grep -i "related_keywords"

# Check coverage for specific modules
uv run pytest tests/test_unit.py -v -k "related_test_pattern"
```

### 3.3 Document Findings
In the scratch file, document:
- Which parts are already implemented
- Which parts have test coverage
- Which parts are missing

### 3.4 Update Issue with Progress
```bash
gh issue comment ISSUE_NUMBER --body "$(cat <<'EOF'
## Implementation Analysis

**Already implemented:**
- [List existing functionality]

**Test coverage:**
- [List covered scenarios]

**Still needed:**
- [List remaining work]
EOF
)"
```

---

## Phase 4: PLAN IMPLEMENTATION

### 4.1 Create Feature Branch
```bash
# Create branch with proper naming
git checkout -b feature/ISSUE_NUMBER-title-slug main
```

Branch naming convention: `feature/ISSUE_NUMBER-title-slug`
- Use lowercase
- Replace spaces with hyphens
- Keep slug short but descriptive (max 5 words)

### 4.2 Plan the Work
Create a detailed implementation plan:
1. Files to create/modify
2. Tests to write (follow TDD where practical)
3. Documentation to update
4. Architecture considerations

### 4.3 Check Architecture Impact
If the issue affects architecture:
- Check `docs/ARCHITECTURE.md` (create if needed)
- Document any architecture decisions (ADRs)
- Update diagrams if needed

---

## Phase 5: IMPLEMENT

### 5.1 Implementation Guidelines
- Follow patterns in `CLAUDE.md`
- Use existing code patterns from the codebase
- Keep changes focused on the issue scope
- Make small, logical commits

### 5.2 Commit Convention
Use this commit message format:
```
#ISSUE_NUMBER: type: description

[optional body with more details]
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`

Example:
```bash
git commit -m "#123: feat: add user authentication endpoint"
```

### 5.3 Test Requirements
Be practical about testing:
- **Backend Python**: pytest in `backend/tests/`
- **Frontend React**: Integration/E2E tests may be more appropriate
- **UI changes**: May need manual validation steps

### 5.4 Update Scratch File
After each significant step, update `.tmp/ISSUE_NUMBER-title-slug.md`:
- Mark completed checkpoints
- Document decisions made
- Note any blockers

---

## Phase 6: DOCUMENTATION

### 6.1 Check VALIDATION.md
Determine if this issue's "good weather path" should be in the smoke test:
- VALIDATION.md is for critical user-facing flows
- Not every feature needs to be here
- Focus on core application functionality

If needed, add a validation step to `VALIDATION.md`.

### 6.2 Update Architecture Documentation
If this issue changes architecture:
1. Ensure `docs/` folder exists
2. Create/update `docs/ARCHITECTURE.md`
3. Add architecture decision records if significant
4. Update any Mermaid diagrams

### 6.3 Update Other Documentation
Check and update if relevant:
- `README.md` - Only if user-facing features change
- `DEVELOPMENT.md` - If development workflow changes
- `docs/` files - For implementation details

### 6.4 Update Policies if Needed
If implementation revealed policy gaps:
- Update `CLAUDE.md` with new guidelines
- Update `POLICIES.md` if needed

---

## Phase 7: VALIDATE

### 7.1 Run Pre-commit Hooks
```bash
# Run pre-commit on all changed files
git diff --name-only HEAD~1 | xargs pre-commit run --files
```

If hooks modify files, commit the changes:
```bash
git add -A && git commit -m "#ISSUE_NUMBER: chore: apply pre-commit fixes"
```

### 7.2 Run Tests
```bash
# Backend tests
cd backend && uv run pytest tests/ -v

# Frontend lint
cd frontend && npm run lint
```

### 7.3 Build Check
```bash
# Backend type check
cd backend && uv run pyright

# Frontend build
cd frontend && npm run build
```

---

## Phase 8: CREATE PULL REQUEST

### 8.1 Push Branch
```bash
git push -u origin feature/ISSUE_NUMBER-title-slug
```

### 8.2 Create PR
```bash
gh pr create --title "#ISSUE_NUMBER: [Title from issue]" --body "$(cat <<'EOF'
## Summary
[Brief description of changes]

Closes #ISSUE_NUMBER

## Changes
- [List of changes]

## Testing
- [How this was tested]

## Documentation
- [Documentation updates made]

## Checklist
- [ ] Tests pass
- [ ] Pre-commit hooks pass
- [ ] Documentation updated
- [ ] No breaking changes (or documented)

---
Generated with Claude Code
EOF
)" --reviewer pkuppens
```

### 8.3 Request Copilot Review
After PR is created, GitHub Copilot review should be automatic if enabled in repo settings.
If not automatic:
```bash
gh pr edit PR_NUMBER --add-reviewer @copilot
```

### 8.4 Update Issue
```bash
gh issue comment ISSUE_NUMBER --body "$(cat <<'EOF'
## Pull Request Created

PR: #PR_NUMBER

**Implementation complete and ready for review.**

Changes include:
- [Summary of implementation]
EOF
)"
```

---

## Phase 9: CLEANUP & HANDOFF

### 9.1 Final Scratch File Update
Update `.tmp/ISSUE_NUMBER-title-slug.md` with final status:
- Mark all completed checkpoints
- Note PR number
- Document any follow-up items

### 9.2 Summary
Provide a summary to the user:
- PR link
- Key implementation decisions
- Any follow-up issues to create
- Manual testing steps if applicable

---

## Error Handling

### If gh CLI fails
Check authentication:
```bash
gh auth status
```

### If branch already exists
```bash
# Check if it's your branch
git log feature/ISSUE_NUMBER-title-slug --oneline -5

# If resuming, checkout and continue
git checkout feature/ISSUE_NUMBER-title-slug
```

### If pre-commit hooks fail
1. Review the failures
2. Fix issues manually or let hooks auto-fix
3. Re-run hooks to verify
4. Commit fixes

### If tests fail
1. Analyze failure
2. Determine if test or implementation needs fixing
3. Fix and re-run
4. Document any known issues

---

## Resume Capability

If you find existing work (scratch file or branch):

1. Read the scratch file for context
2. Show a recap to the user:
   - What was completed
   - What's remaining
   - Any blockers noted
3. Ask if user wants to:
   - Continue from last checkpoint
   - Start fresh (archive old scratch file)

---

## Key Policies Reference

Refer to these documents during implementation:
- `CLAUDE.md`: Development guidelines, code style, testing strategy
- `POLICIES.md`: Project policies, acceptable use
- `VALIDATION.md`: Smoke test checklist

Always check these documents before making decisions. Update them if you discover gaps or inconsistencies.
