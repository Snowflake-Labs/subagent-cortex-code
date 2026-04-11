---
name: cortex-code
description: Routes Snowflake-related operations to Cortex Code CLI for specialized Snowflake expertise
---

# Cortex Code Integration Skill

This skill enables Cursor to leverage Cortex Code's specialized Snowflake expertise by routing Snowflake-related operations to Cortex Code CLI.

## When to Use

Use this skill when the user asks about:
- Snowflake databases, warehouses, schemas, tables, views
- SQL queries for Snowflake data
- Data quality checks, validation, profiling
- Cortex AI features (Cortex Search, Cortex Analyst, ML functions)
- Semantic views, data modeling  
- Snowpark (Python/Scala), dynamic tables, streams, tasks
- Snowflake security, roles, policies, governance

## How It Works

When invoked, this skill:

1. **Routes the request** - Analyzes if the request is Snowflake-related
2. **Executes via Cortex Code** - Calls `cortex` CLI in headless mode
3. **Returns results** - Streams back SQL query results and analysis

## Usage in Cursor

```
/cortex-code

# Then ask your Snowflake question:
How many databases do I have in Snowflake?
Show me top 10 customers by revenue
Check data quality for SALES_DATA table
```

## Configuration

**Approval mode**: auto (no prompts, with audit logging)  
**Audit logs**: `~/.claude/skills/cortex-code/audit.log`  
**Security envelope**: RW (Read-Write operations allowed)

## Technical Details

- **Routing**: LLM-based semantic analysis
- **Execution**: `cortex -p "..." --input-format stream-json`
- **Connection**: Uses default Snowflake connection from `cortex` CLI
- **Tools**: Auto-approved via programmatic mode with envelope-based blocklist

## Examples

**Query databases:**
```
User: How many databases do I have?
Cortex: Executes `SELECT COUNT(*) FROM SNOWFLAKE.INFORMATION_SCHEMA.DATABASES`
```

**Data quality:**
```
User: Check data quality for SALES_DATA
Cortex: Analyzes schema, null rates, duplicates, data types
```

**Complex analysis:**
```
User: Show me revenue trends by region for Q1
Cortex: Writes and executes SQL query, returns formatted results
```
