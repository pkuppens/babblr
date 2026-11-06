# Codebase inventory with CodeGraph

[CodeGraph](https://github.com/colbymchenry/codegraph) builds a local code graph
of a repository. It gives AI agents fast, semantic answers through MCP. This
page is a short summary. The upstream README and the
[documentation site](https://colbymchenry.github.io/codegraph/) are the source
of truth. Do not copy them here.

Tracking issue: [#359](https://github.com/pkuppens/babblr/issues/359).

## What it is for

- It parses source files and stores symbols, calls, and imports in a local
  SQLite database (`.codegraph/`).
- It supports 20+ languages. This includes Python and TypeScript, which Babblr
  uses.
- It runs 100% local. It needs no API key and sends no data out.
- It exposes the graph to agents as an MCP server. The agent asks one question
  and gets the relevant source, the call paths, and the impact radius. This
  replaces many grep and read steps.

## How it differs from Understand-Anything

| | CodeGraph | [Understand-Anything](understand-anything.md) |
| --- | --- | --- |
| Main use | Agent queries over MCP | Human-readable architecture graph and dashboard |
| Index | Local SQLite, auto-synced by a file watcher | `knowledge-graph.json`, committed to git |
| Output | Source snippets, call paths, blast radius | Interactive dashboard |
| Shared in git | No (local index) | Yes |

The two tools do different jobs. They can be used together.

## Setup (once per developer machine)

CodeGraph is a global tool. It is not a project dependency. Do not add it to
`backend/` or `frontend/`.

```powershell
# Windows (PowerShell)
irm https://raw.githubusercontent.com/colbymchenry/codegraph/main/install.ps1 | iex

# Or, if Node is present
npm i -g @colbymchenry/codegraph
```

Open a new terminal. Then connect CodeGraph to your agents:

```bash
codegraph install
```

This step adds the MCP server to Claude Code and other agents it finds. It does
not index any code.

Read the install script before you run it. Use `codegraph uninstall` to remove
everything.

## Run an index

```bash
cd babblr
codegraph init      # create .codegraph/ and build the full graph
codegraph status    # show counts and pending files
```

Auto-sync is on by default. A file watcher updates the graph after each file
change. You do not need to run `codegraph sync`. Use `codegraph sync` only when
the watcher is off.

`.codegraph/` is local and machine-specific. It is listed in `.gitignore`. Do
not commit it.

## Use it with MCP (semantic queries)

After `codegraph install`, the MCP server starts with `codegraph serve --mcp`.
The agent sees one tool: `codegraph_explore`. It answers questions such as:

- "Which code calls the LLM provider factory?"
- "What does a request to the conversation endpoint touch, from router to
  database?"
- "Where do I add a new LLM provider?"
- "What breaks if I change the `Message` model?"

Other tools (`codegraph_search`, `codegraph_callers`, `codegraph_callees`,
`codegraph_impact`, `codegraph_files`, `codegraph_node`, `codegraph_status`)
work but are hidden by default.

To check the connection in Claude Code, run `/mcp` and look for `codegraph`.

## Results for Babblr

Run the commands above and add the findings under
[Inventory results](#inventory-results). Include real output only.

## Inventory results

_Not yet recorded. See issue #359 for the open work._

| Item | Value |
| --- | --- |
| CodeGraph version | |
| Files, nodes, and edges (`codegraph status`) | |
| Index time (first run) | |
| Gaps or wrong edges found | |

Component diagram: _to add in `docs/diagrams/codegraph-components.md` after a
real run._

## Verdict

_To add after the run: pros, cons, cost, and a recommendation._
