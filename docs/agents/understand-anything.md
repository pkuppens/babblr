# Codebase analysis with Understand-Anything

[Understand-Anything](https://github.com/Egonex-AI/Understand-Anything) is a
Claude Code plugin. It produces an interactive knowledge graph of this repo's
architecture.

## Global setup (once per developer machine)

The plugin is a Claude Code plugin, not a project dependency:

```text
# In a Claude Code session
/plugin marketplace add Egonex-AI/Understand-Anything
/plugin install understand-anything
```

**Prerequisite**: Node.js 22.13 or later and pnpm 10 or later must be present
when the skill first builds its core (`packages/core/dist/`). If pnpm is
missing, install it:

```bash
npm install -g pnpm@10   # if Node is older than 22.13 (pnpm 11 needs 22.13 or later)
```

## Run the analysis (in a Claude Code session)

```text
/understand-anything:understand
```

This produces `.understand-anything/knowledge-graph.json`. Run it again after a
large structural change. Later runs are incremental.

## Output files

| Path | Tracked in git? | Purpose |
| --- | --- | --- |
| `.understand-anything/knowledge-graph.json` | Yes | shareable graph. Commit it so every contributor can use the dashboard |
| `.understand-anything/meta.json` | Yes | records the last analyzed commit hash, for incremental updates |
| `.understand-anything/config.json` | Yes | stores language and auto-update preferences |
| `.understand-anything/.understandignore` | Yes | controls which files the analysis excludes |
| `.understand-anything/intermediate/` | No (gitignored) | scratch files, cleaned up after each run |
| `.understand-anything/tmp/` | No (gitignored) | scratch files, cleaned up after each run |

## View the dashboard

After you generate the graph, start the dashboard in a Claude Code session:

```text
/understand-anything:understand-dashboard
```
