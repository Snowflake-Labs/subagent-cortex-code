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

When this skill triggers, follow these steps **in separate commands** (do not chain with &&):

### Step 1: Discover Cortex capabilities (run once per session)

```bash
cd /Users/tjia/.codex/skills/cortex-code && python3 scripts/discover_cortex.py
```

Wait for this to complete before proceeding.

### Step 2: Route the user request

```bash
cd /Users/tjia/.codex/skills/cortex-code && python3 scripts/route_request.py --prompt "USER_PROMPT_HERE"
```

Interpret the result:
- `cortex` → proceed to Step 4
- `codex` → proceed to Step 3  
- `blocked` → explain to user

### Step 3: If routed to Codex

Handle the request directly using Codex tools and normal local workflow. Do not invoke Cortex.

Typical Codex-handled requests include:
- local file reads/writes/edits
- Git operations
- web or app development unrelated to Snowflake
- general Python, JavaScript, shell, or infrastructure work
- non-Snowflake databases

### Step 4: If routed to Cortex

Choose envelope based on the task:
- `RO` - read-only queries (SHOW, SELECT)  
- `RW` - data changes (INSERT, UPDATE, CREATE)
- `RESEARCH` - exploratory analysis
- `DEPLOY` - full access (use cautiously)

Execute with explicit cd to avoid path issues:

```bash
cd /Users/tjia/.codex/skills/cortex-code && python3 scripts/execute_cortex.py --prompt "USER_PROMPT_HERE" --envelope RO
```

**CRITICAL FOR CODEX**: This command takes 10-20 seconds. Do NOT chain it with other commands using &&. Run it as a standalone command and wait for it to complete. The script streams output as it executes.

### Step 5: Present results back to user

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
