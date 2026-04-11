---
name: cortex-code
description: Routes Snowflake-related operations to Cortex Code CLI for specialized Snowflake expertise. Use when the user asks about Snowflake databases, warehouses, schemas, tables, SQL on Snowflake, Cortex AI features, Snowpark, dynamic tables, streams, tasks, governance, or Snowflake security. Do not use for general programming, local file operations, non-Snowflake databases, web development, or infrastructure unrelated to Snowflake.
metadata:
  author: Snowflake Integration Team
  compatibility: Requires Cortex Code CLI installed and configured
---

# Cortex Code Integration for Codex

This skill lets Codex delegate Snowflake-specific work to Cortex Code CLI while Codex remains the primary assistant for general coding and local repository tasks.

## Routing Principle

Only Snowflake-specific operations go to Cortex Code. Everything else stays in Codex.

## How to use this skill

When this skill triggers, follow this workflow.

### 1. Discover Cortex capabilities if needed

If Cortex capabilities are not cached yet, or the cache appears stale, run:

```bash
python3 scripts/discover_cortex.py
```

This discovers available Cortex skills and caches them for later routing decisions.

### 2. Route the user request

Analyze the user prompt before acting:

```bash
python3 scripts/route_request.py --prompt "USER_PROMPT_HERE"
```

Interpret the routing result as:
- `cortex` → delegate to Cortex Code
- `codex` → handle locally in Codex
- `blocked` → do not execute; explain why and ask for a safer reformulation if needed

### 3. If routed to Codex

Handle the request directly using Codex tools and normal local workflow. Do not invoke Cortex.

Typical Codex-handled requests include:
- local file reads/writes/edits
- Git operations
- web or app development unrelated to Snowflake
- general Python, JavaScript, shell, or infrastructure work
- non-Snowflake databases

### 4. If routed to Cortex

Choose an envelope based on the task:
- `RO` for read-only or query operations
- `RW` for changes in Snowflake-managed objects
- `RESEARCH` for exploratory work
- `DEPLOY` only for high-trust deployment-style operations

**With approval_mode: "auto" (default in config.yaml), execute directly:**

```bash
python3 /Users/tjia/.codex/skills/cortex-code/scripts/execute_cortex.py --prompt "USER_PROMPT_HERE" --envelope RO
```

**Note**: This takes 10-20 seconds. Wait for completion.

### 5. Present results back in Codex

After Cortex finishes:
- summarize the result clearly for the user
- include key findings, SQL, errors, or next actions
- keep Codex as the user-facing orchestrator

## Security expectations

Use the built-in security flow from the bundled scripts:
- prompt sanitization
- credential path blocking
- audit logging
- approval modes
- envelope-based tool restrictions

Default config path:

```bash
~/.codex/skills/cortex-code/config.yaml
```

Default audit log path:

```bash
~/.codex/skills/cortex-code/audit.log
```

Optional org policy path:

```bash
~/.snowflake/cortex/codex-skill-policy.yaml
```

## Notes for Codex

- Treat `codex` as the local-handling route.
- Do not route local file operations to Cortex.
- Do not send credential files, local secrets, or unrelated repo context to Cortex.
- Prefer minimal context when invoking Cortex, unless recent conversation materially improves the Snowflake task.
- If the user explicitly asks to use Cortex for a Snowflake task, prefer the Cortex route unless blocked by security rules.

## Useful scripts

- `scripts/discover_cortex.py` — discover Cortex skills and cache capabilities
- `scripts/route_request.py` — route prompt to `cortex` or `codex`
- `scripts/security_wrapper.py` — enforce approvals and envelopes
- `scripts/execute_cortex.py` — run Cortex in headless mode
- `scripts/read_cortex_sessions.py` — inspect recent Cortex sessions
- `scripts/predict_tools.py` — predict likely tool usage for approvals
