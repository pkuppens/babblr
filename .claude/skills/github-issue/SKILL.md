---
name: github-issue
description: Manage GitHub issues - fetch details, update descriptions, add comments, close issues. Use when working with GitHub issues, reviewing issue status, or tracking implementation progress.
allowed-tools: Bash(gh:*), Read, Write
---

# GitHub Issue Management

This skill provides capabilities for managing GitHub issues via the `gh` CLI.

## Prerequisites

Ensure `gh` CLI is installed and authenticated:
```bash
gh auth status
```

If not authenticated:
```bash
gh auth login
```

## Capabilities

### Fetch Issue Details

Get comprehensive issue information:
```bash
gh issue view <number> --json number,title,body,state,labels,comments,assignees,milestone
```

### Update Issue Description

Update the issue body (use heredoc for multiline):
```bash
gh issue edit <number> --body "$(cat <<'EOF'
Updated description content here...
EOF
)"
```

### Update Issue Title

```bash
gh issue edit <number> --title "New title"
```

### Add Labels

```bash
gh issue edit <number> --add-label "label1,label2"
```

### Add Comment

Document progress, decisions, or analysis:
```bash
gh issue comment <number> --body "$(cat <<'EOF'
## Progress Update

**Status:** [analyzing|in_progress|blocked|ready_for_review]

**Summary:**
- Point 1
- Point 2

**Next Steps:**
- [ ] Task 1
- [ ] Task 2
EOF
)"
```

### Close Issue

```bash
gh issue close <number> --reason completed
# or
gh issue close <number> --reason "not planned"
```

### Reopen Issue

```bash
gh issue reopen <number>
```

## Best Practices

### Issue Updates
- Add comments to track implementation progress
- Use structured format (headers, lists) for readability
- Include context for decisions made
- Reference related PRs and issues

### Issue Description
- Keep description current with actual requirements
- Mark completed items in checklists
- Move deferred items to "Future Enhancements" section

### Labels as Hints
- `draft` - More freedom to suggest changes
- `blocked` - Check and document blockers
- `ai-ready` - Ready for AI implementation
- `bug` vs `enhancement` - Affects implementation approach

## Comment Templates

### Implementation Analysis
```markdown
## Implementation Analysis

**Already implemented:**
- [List existing functionality]

**Test coverage:**
- [List covered scenarios]

**Still needed:**
- [List remaining work]
```

### Completion Summary
```markdown
## Implementation Complete

PR: #<number>

**Changes:**
- [Summary of changes]

**Testing:**
- [How it was tested]
```
