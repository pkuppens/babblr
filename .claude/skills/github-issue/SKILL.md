---
name: github-issue
description: Manage GitHub issues - fetch details, update descriptions, add comments, close issues. Use when working with GitHub issues, reviewing issue status, or tracking implementation progress.
allowed-tools: Bash(gh:*), Read, Write
---

# GitHub Issue Management

Manage GitHub issues via `gh` CLI.

## Core Commands

```bash
# Fetch issue details
gh issue view <number> --json number,title,body,state,labels,comments

# Update description
gh issue edit <number> --body "$(cat <<'EOF'
Updated description...
EOF
)"

# Add comment
gh issue comment <number> --body "$(cat <<'EOF'
## Progress Update

**Status:** [analyzing|in_progress|blocked|ready_for_review]

- Point 1
- Point 2
EOF
)"

# Close issue
gh issue close <number> --reason completed
```

## Comment Templates

**Implementation Analysis:**
```markdown
## Implementation Analysis

**Already implemented:** [list]
**Test coverage:** [list]
**Still needed:** [list]
```

**Completion Summary:**
```markdown
## Implementation Complete

PR: #<number>

**Changes:** [summary]
**Testing:** [how tested]
```

## Best Practices

- Add comments to track progress
- Use structured format (headers, lists)
- Reference related PRs and issues
- Keep description current with requirements
