# Claude Code Integration

This document explains how Babblr integrates with Claude Code, including custom commands and skills.

## Overview

Claude Code provides two mechanisms for extending its capabilities:

1. **Slash Commands** - Explicit prompts invoked with `/command-name`
2. **Skills** - Capabilities Claude can auto-activate based on context

## Commands vs Skills

| Aspect | Slash Commands | Skills |
|--------|---------------|--------|
| **Location** | `.claude/commands/*.md` | `.claude/skills/skill-name/SKILL.md` |
| **Invocation** | Explicit: `/command-name` | Automatic: Claude chooses based on description |
| **File structure** | Single `.md` file | Directory with `SKILL.md` + optional files |
| **Discovery** | Manual (user types it) | Automatic (Claude matches description) |
| **Best for** | Deliberate actions with specific inputs | Reusable capabilities across workflows |

### When to Use Commands

Use commands when:
- The action requires specific user input (e.g., issue number)
- You want explicit control over when it runs
- The workflow is complex and shouldn't auto-trigger

Example: `/implement-issue 123`

### When to Use Skills

Use skills when:
- The capability should be available across multiple workflows
- Claude should be able to suggest using it
- The functionality is a reusable building block

Example: GitHub issue management skills that multiple commands can use

## Project Structure

```
.claude/
├── commands/                    # Slash commands
│   ├── implement-issue.md       # /implement-issue <number>
│   └── tdd.md                   # /tdd <description>
└── skills/                      # Auto-activating skills
    ├── github-issue/
    │   └── SKILL.md             # GitHub issue management
    ├── git-workflow/
    │   └── SKILL.md             # Branch and PR workflows
    ├── codebase-analysis/
    │   └── SKILL.md             # Implementation and test analysis
    └── project-policies/
        └── SKILL.md             # Policy compliance
```

## Available Commands

### `/implement-issue <number>`

Implements a GitHub issue following project policies:
1. Fetches and analyzes the issue
2. Reviews accuracy against codebase
3. Checks existing implementation and tests
4. Creates feature branch (if needed)
5. Implements changes
6. Updates documentation
7. Runs pre-commit hooks
8. Creates PR with reviewers

Usage:
```
/implement-issue 11
```

### `/tdd <description>`

Test-Driven Development workflow:
1. Plan the implementation
2. Write failing tests (RED)
3. Implement minimal code (GREEN)
4. Refactor (REFACTOR)
5. Review

Usage:
```
/tdd add user authentication
```

## Available Skills

Skills are automatically discovered from `.claude/skills/`. Each skill:
- Has a `description` field that Claude uses for matching
- Can be used standalone or composed by commands
- Should have single responsibility

### `github-issue`

Manage GitHub issues - fetch details, update descriptions, add comments, close issues.

**Triggers:** Working with GitHub issues, reviewing issue status, tracking implementation progress.

**Capabilities:**
- Fetch issue details with `gh issue view`
- Update issue title/description
- Add structured comments
- Close/reopen issues

### `git-workflow`

Git branch management and pull request workflows.

**Triggers:** Creating feature branches, pushing changes, creating PRs.

**Capabilities:**
- Branch naming convention (`feature/<issue>-<desc>`)
- Commit message format (`#<issue>: <type>: <desc>`)
- PR creation with templates
- Pre-commit validation

### `codebase-analysis`

Analyze codebase for existing implementations and test coverage.

**Triggers:** Checking what's implemented, finding related code, assessing test coverage.

**Capabilities:**
- Search for code patterns
- Check test coverage
- Analyze architecture
- Report implementation status

### `project-policies`

Check and enforce project policies from CLAUDE.md and POLICIES.md.

**Triggers:** Validating implementations, checking code style, ensuring compliance.

**Capabilities:**
- Policy compliance checklist
- Pre-commit verification
- Documentation requirements
- Security checks

### Skill Development Guidelines

1. **Single responsibility** - Each skill does one thing well
2. **Clear description** - Help Claude know when to use it
3. **Composable** - Skills can be used by commands or other skills
4. **Documented** - Include usage examples in SKILL.md
5. **Tool restrictions** - Use `allowed-tools` to limit scope

## Creating New Commands

1. Create `.claude/commands/my-command.md`
2. Add YAML frontmatter:
   ```yaml
   ---
   description: Brief description of what the command does
   argument-hint: <required-argument>
   ---
   ```
3. Write the prompt/instructions
4. Use `$ARGUMENTS` placeholder for user input

## Creating New Skills

1. Create directory `.claude/skills/my-skill/`
2. Create `SKILL.md` with frontmatter:
   ```yaml
   ---
   name: my-skill
   description: When to use this skill. Be specific so Claude matches correctly.
   ---
   ```
3. Write the skill instructions
4. Optionally add supporting files in the same directory

## Best Practices

### For Commands
- Use clear, action-oriented names
- Include `argument-hint` for required inputs
- Document in this file when adding new commands

### For Skills
- Write precise descriptions for accurate matching
- Keep skills focused (single responsibility)
- Test that Claude activates them appropriately

### General
- Follow project policies in CLAUDE.md and POLICIES.md
- Update this documentation when adding commands/skills
- Use `.tmp/` for scratch files during complex workflows
