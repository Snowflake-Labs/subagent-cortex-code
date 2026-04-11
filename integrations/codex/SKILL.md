---
name: cortex-code
description: Routes Snowflake-related operations to Cortex Code CLI for specialized Snowflake expertise. Use when the user asks about Snowflake databases, warehouses, schemas, tables, SQL on Snowflake, Cortex AI features, Snowpark, dynamic tables, streams, tasks, governance, or Snowflake security. Do not use for general programming, local file operations, non-Snowflake databases, web development, or infrastructure unrelated to Snowflake.
metadata:
  author: Snowflake Integration Team
  compatibility: Requires Cortex Code CLI installed and configured
---

# Cortex Code Integration for Codex

This skill lets Codex delegate Snowflake-specific work to Cortex Code via the `cortexcode-tool` CLI while Codex remains the primary assistant for general coding and local repository tasks.

## Routing Principle

Only Snowflake-specific operations go to Cortex Code. Everything else stays in Codex. The cortexcode-tool automatically handles routing.

## How to use this skill

When this skill triggers, follow this simplified workflow.

### 1. Execute Snowflake queries via cortexcode-tool

For any Snowflake-related request, use cortexcode-tool directly:

```bash
cortexcode-tool "USER_PROMPT_HERE" --envelope RO --config /tmp/cortexcode-tool-codex.yaml
```

Choose envelope based on operation:
- `RO` for read-only queries (default for most operations)
- `RW` for data modifications or writes
- `RESEARCH` for exploratory work
- `DEPLOY` for deployment operations

**Note**: The cortexcode-tool CLI handles routing automatically and uses /tmp/ paths for Codex sandbox compatibility. Takes 15-30 seconds and returns clean formatted output.

### 2. Present results back in Codex

After cortexcode-tool finishes:
- The tool returns clean, formatted output (not JSON)
- Summarize the result clearly for the user
- Include key findings, SQL, errors, or next actions
- Keep Codex as the user-facing orchestrator

**Example output:**
```
✓ Routing to Cortex Code (confidence: 100.00%)
You have **64 databases** in your Snowflake account...
```

### 3. Handle non-Snowflake requests locally

For non-Snowflake requests, handle directly using Codex tools:
- Local file reads/writes/edits
- Git operations
- Web or app development unrelated to Snowflake
- General Python, JavaScript, shell, or infrastructure work
- Non-Snowflake databases

## Security expectations

The cortexcode-tool uses built-in security flow:
- Auto-approval mode (approval_mode: "auto")
- Audit logging to /tmp/cortexcode-tool-codex-audit.log
- Envelope-based tool restrictions
- Prompt sanitization
- Credential path blocking

Config file location: `/tmp/cortexcode-tool-codex.yaml`

## Notes for Codex

- Handle local file operations, git, and non-Snowflake work directly - don't use cortexcode-tool
- For Snowflake queries, use cortexcode-tool with appropriate envelope
- Keep context minimal when invoking Cortex
- cortexcode-tool automatically determines if a query is Snowflake-related
- If a query fails routing or times out, handle locally or explain the limitation

## Troubleshooting

### Error: Permission denied on cache directory
**Solution**: Use the provided config: `--config /tmp/cortexcode-tool-codex.yaml`

### Error: Cortexcode-tool not found
**Solution**: Install cortexcode-tool CLI first:
```bash
# Installation instructions in cortexcode-tool repository
```

### Query takes too long
**Note**: Queries typically take 15-30 seconds. If consistently slower, check Snowflake connection.

## Examples

**Snowflake database count:**
```bash
cortexcode-tool "How many databases do I have in Snowflake?" --envelope RO --config /tmp/cortexcode-tool-codex.yaml
```

**Query specific database:**
```bash
cortexcode-tool "What tables are in DB_STOCK database?" --envelope RO --config /tmp/cortexcode-tool-codex.yaml
```

**Data modification:**
```bash
cortexcode-tool "Create a backup table of SALES_DATA" --envelope RW --config /tmp/cortexcode-tool-codex.yaml
```
