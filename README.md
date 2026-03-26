# Claude Code Skill: Cortex Code Integration

This skill enables Claude Code to leverage Cortex Code's specialized Snowflake expertise by intelligently routing Snowflake-related operations to Cortex Code CLI in headless mode.

## Overview

The Cortex Code Integration Skill bridges Claude Code and Cortex Code CLI, allowing seamless delegation of Snowflake-specific tasks while maintaining Claude Code's general-purpose capabilities.

**Key Features:**
- 🎯 **Smart Routing**: LLM-based semantic routing automatically detects Snowflake operations
- 🔒 **Security Envelopes**: Configurable permission models (RO, RW, RESEARCH, DEPLOY, NONE)
- 🔄 **Programmatic Mode**: Auto-approval of tool calls via `--input-format stream-json`
- 📊 **Context Enrichment**: Passes conversation history to Cortex for informed execution
- 🛡️ **Permission Surfacing**: All Cortex tool calls visible to user via Claude Code UI

## Background

AI coding assistants excel as generalists, but domain expertise matters. Ask Claude Code to build a web server, and it excels. Ask it about Snowflake's dynamic tables, Snowpark optimization, or Cortex Search semantic views — and you're asking a general practitioner to perform specialist surgery.

Snowflake has that specialist: **Cortex Code**, an AI agent trained on Snowflake's entire technical stack. It knows the quirks of Snowflake's metadata views, when to use dynamic tables versus streams, and can debug semantic view configurations from institutional knowledge.

This skill bridges both agents using a **multi-agent harness pattern**: Claude Code acts as the orchestrator (managing conversation, routing, general tasks), while Cortex Code runs as a specialized agent (invoked only for Snowflake operations, executing autonomously, streaming results back). From the user's perspective, it's one conversation. Behind the scenes, two specialists collaborate — each in their domain of expertise.

## Architecture

```
User Request
    ↓
[Claude Code - Routing Layer]
    ↓
  Is Snowflake-related?
    ↓ YES                ↓ NO
[Cortex Code CLI]    [Claude Code]
    ↓                     ↓
Snowflake Execution   General Tasks
```

**Routing Principle**: ONLY Snowflake operations → Cortex Code. Everything else → Claude Code.

## Installation

### Prerequisites

#### 1. Claude Code CLI
Install and configure Claude Code CLI. Follow the [official installation guide](https://docs.anthropic.com/en/docs/claude-code).

#### 2. Cortex Code CLI
Install Cortex Code CLI (v1.0.42 or later):

```bash
# Install via official script
curl -LsS https://ai.snowflake.com/static/cc-scripts/install.sh | sh
```

After installation, verify:
```bash
which cortex
cortex --version
```

**Documentation:** https://docs.snowflake.com/en/user-guide/cortex-code/cortex-code-cli#install-cortex-code-cli

#### 3. uv Package Manager
Required for Python script execution in this skill:

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or via Homebrew
brew install uv
```

Verify installation:
```bash
which uv
uv --version
```

#### 4. Snowflake Connection Configuration
Configure a Snowflake connection in Cortex Code:

```bash
# Interactive connection setup
cortex connections create

# Or manually edit ~/.snowflake/cortex/settings.json
```

Your connection needs appropriate permissions for the databases/schemas you'll work with. See [Cortex Code permissions documentation](https://docs.snowflake.com/en/user-guide/cortex-code/cortex-code-cli#install-cortex-code-cli) for details.

**Minimum Required Permissions:**
- `USAGE` on database and schema
- `SELECT` on tables for read operations
- `CREATE TABLE`, `CREATE VIEW`, etc. for write operations (if using RW envelope)

#### 5. Python 3.8+
The skill scripts use Python standard library only (no external dependencies required).

### Setup

1. Clone this repository to your Claude Code skills directory:
   ```bash
   cd ~/.claude/skills/
   git clone https://github.com/sfc-gh-tjia/claude_skill_cortexcode.git cortex-code
   ```

2. Verify the skill is recognized:
   ```bash
   # In Claude Code CLI
   /skills list
   # Should show "cortex-code" in the list
   ```

3. The skill will automatically load when you mention Snowflake-related tasks.

## Usage

### Automatic Routing

The skill automatically activates when you mention Snowflake-related operations:

```
User: "Show me the top 10 customers by revenue in Snowflake"
→ Automatically routed to Cortex Code
→ SQL executed on Snowflake
→ Results returned to user
```

```
User: "Read the config.json file in this directory"
→ Handled by Claude Code directly
→ No Cortex involvement
```

### What Gets Routed to Cortex Code?

✅ **Routes to Cortex:**
- Snowflake databases, warehouses, schemas, tables
- SQL queries specifically for Snowflake
- Cortex AI features (Cortex Search, Cortex Analyst, ML functions)
- Snowpark, dynamic tables, streams, tasks
- Data governance, data quality in Snowflake
- Snowflake security, roles, policies
- User explicitly mentions "Cortex" or "Snowflake"

❌ **Stays in Claude Code:**
- Local file operations (reading, writing, editing local files)
- General programming (Python, JavaScript, etc. not Snowflake-specific)
- Non-Snowflake databases (PostgreSQL, MySQL, MongoDB, etc.)
- Web development, frontend work
- Infrastructure/DevOps unrelated to Snowflake
- Git operations, GitHub, version control

## Security Envelopes

The skill uses security envelopes to control which tools Cortex Code can execute:

| Envelope | Use Case | Blocked Tools |
|----------|----------|---------------|
| **RO** (Read-Only) | Queries and read operations | Edit, Write, destructive Bash |
| **RW** (Read-Write) | Data modifications | Destructive operations (rm -rf, sudo) |
| **RESEARCH** | Exploratory work | Write operations |
| **DEPLOY** | Full access | None (use cautiously) |
| **NONE** | Custom blocklist | Specify via --disallowed-tools |

Specify the envelope in your requests or the skill will choose based on the operation type.

## File Structure

```
cortex-code/
├── SKILL.md                    # Skill definition and documentation
├── README.md                   # This file
├── scripts/
│   ├── discover_cortex.py      # Discover Cortex capabilities
│   ├── route_request.py        # LLM-based routing logic
│   ├── execute_cortex.py       # Execute Cortex in headless mode
│   ├── read_cortex_sessions.py # Read Cortex session history
│   └── predict_tools.py        # Predict required tools
├── references/
│   ├── cortex-cli-reference.md # Cortex CLI documentation
│   ├── routing-examples.md     # Routing decision examples
│   └── troubleshooting-guide.md # Common issues and fixes
└── assets/                     # Optional assets (empty)
```

## How It Works

### Step 1: Request Analysis
```python
# User: "Check data quality for the SALES_DATA table"
python scripts/route_request.py --prompt "Check data quality for the SALES_DATA table"
# Output: {"route": "cortex", "confidence": 0.95, "reason": "Snowflake data quality check"}
```

### Step 2: Context Enrichment
- Gathers recent Claude Code conversation history
- Reads recent Cortex Code session files
- Builds enriched prompt with full context

### Step 3: Cortex Execution
```bash
python scripts/execute_cortex.py \
  --prompt "ENRICHED_PROMPT" \
  --envelope "RW" \
  --connection "connection_name"
```

### Step 4: Result Display
- Cortex output streamed back to Claude Code
- User sees results in Claude Code UI
- Full transparency of all tool calls

## Programmatic Mode

The skill uses `--input-format stream-json` to enable programmatic mode:
- All tool calls auto-approved (no interactive prompts)
- Works for built-in tools (Read, Write, Edit, Bash, Grep, Glob)
- Works for non-builtin tools (snowflake_sql_execute, data_diff, MCP tools)
- Bypasses org policies that block `--bypass` or `--dangerously-allow-all-tool-calls`
- Security controlled via `--disallowed-tools` blocklist

## Examples

### Example 1: Snowflake Query
```
User: "Show me the top 10 customers by revenue in Snowflake"

Routing: → Cortex Code (Snowflake SQL query)
Envelope: RW (allows SQL execution)
Cortex Action:
1. Uses snowflake_sql_execute to run:
   SELECT customer_name, SUM(revenue) as total
   FROM sales
   GROUP BY customer_name
   ORDER BY total DESC
   LIMIT 10
2. Returns formatted results

Result: Table displayed to user with top 10 customers
```

### Example 2: Local File Operation
```
User: "Read the config.json file in this directory"

Routing: → Claude Code (local file operation)
Claude Action: Uses Read tool directly, no Cortex involvement
Result: File contents displayed
```

### Example 3: Data Quality Check
```
User: "Check data quality for the SALES_DATA table"

Routing: → Cortex Code (Snowflake data quality - matches Cortex's data-quality skill)
Envelope: RW (allows SQL execution for analysis)
Cortex Action:
1. Runs data quality checks using its data-quality skill
2. Analyzes schema, null rates, duplicates, etc.
3. Generates quality report

Result: Comprehensive data quality report with recommendations
```

## Real-World Example: End-to-End Agent Deployment

**Scenario:** Build a Cortex Agent for macroeconomic analysis in 15 minutes

```
User: "Analyze the FINANCE__ECONOMICS database. Create a Cortex agent
with Cortex Analyst that can answer macro economic questions.
Put all curated assets in DB_STOCK."
```

**What Happens:**

**Minutes 0-2: Database Exploration** (Cortex Code)
- Explores 56 views in FINANCE__ECONOMICS.CYBERSYN
- Identifies 5 key tables: GDP, unemployment, inflation, interest rates, indicators

**Minutes 2-8: Semantic View Creation** (Cortex Code)
- Generates semantic model: 5 tables, 4 relationships, 3 verified queries
- Deploys to `DB_STOCK.CURATED.MACRO_ECONOMICS_INDICATORS`

**Minutes 8-12: Cortex Agent Creation** (Cortex Code)
- Creates `DB_STOCK.CURATED.MACRO_ECONOMICS_ANALYST`
- Configures with Cortex Analyst + semantic view

**Minutes 12-15: Testing** (Cortex Code)
- Tests 5 questions automatically
- Results: US GDP 0.7%, Unemployment 4.4%, UK inflation 3.03%

**Continued Collaboration:**
```
User: "Compare inflation rates across US, UK, Germany, France, Japan"
→ Cortex invokes the new agent → 8 seconds → UK 3.03%, US 2.39%,
  Germany 2.08%, Japan 2.08%, France 0.79%

User: "Research FIBO ontology for finance data modeling"
→ Claude Code handles directly → Returns FIBO, SDMX, XBRL analysis

User: "Analyze FINANCE__ECONOMICS structure for FIBO mapping"
→ Back to Cortex → Database analysis + semantic alignment →
  Recommendation: SDMX for timeseries, FIBO for entities
```

**Result:** Production-ready Cortex Agent deployed autonomously with semantic model, tested, and immediately queryable — all in one conversation flow.

## Troubleshooting

### Issue: "Cortex CLI not found"
**Cause:** Cortex Code is not installed or not in PATH

**Solution:**
```bash
which cortex
# If not found, check installation: ~/.snowflake/cortex/
```

### Issue: "Permission denied" despite programmatic mode
**Cause:** Tool is in the --disallowed-tools blocklist for current envelope

**Solution:**
1. Check which envelope is being used (RO/RW/RESEARCH/DEPLOY)
2. If operation is safe, switch to a less restrictive envelope
3. Or use envelope="NONE" with custom --disallowed-tools list

### Issue: Tools still requiring approval
**Cause:** Missing `--input-format stream-json` flag

**Solution:** Ensure both `--output-format stream-json` AND `--input-format stream-json` are present. The input format flag is what enables programmatic auto-approval mode.

### Issue: Routing sends Snowflake query to Claude Code
**Cause:** Routing logic didn't detect Snowflake keywords

**Solution:**
1. Check if user mentioned "Snowflake" explicitly
2. Review routing script logic in `scripts/route_request.py`
3. Add more trigger patterns to routing context

For more troubleshooting, see [troubleshooting-guide.md](references/troubleshooting-guide.md).

## Advanced Configuration

### Custom Routing Rules

Edit `scripts/route_request.py` to customize routing logic:

```python
# Add custom patterns
FORCE_CORTEX_PATTERNS = [
    "snowflake",
    "cortex",
    "warehouse",
    "snowpark"
]

FORCE_CLAUDE_PATTERNS = [
    "local file",
    "git commit",
    "python script"  # unless Snowpark
]
```

### Security Envelope Customization

Modify `scripts/execute_cortex.py` to define custom envelopes:

```python
SECURITY_ENVELOPES = {
    "CUSTOM": ["Edit", "Write", "Bash(rm *)", "Bash(sudo *)"]
}
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## References

- [Cortex CLI Reference](references/cortex-cli-reference.md)
- [Routing Examples](references/routing-examples.md)
- [Troubleshooting Guide](references/troubleshooting-guide.md)

## License

Copyright © 2026 Snowflake Inc. All rights reserved.

## Support

For issues or questions:
- Open an issue on [GitHub](https://github.com/sfc-gh-tjia/claude_skill_cortexcode/issues)
- Contact: Snowflake Integration Team

## Version

**Version:** 1.0.0
**Last Updated:** March 26, 2026
**Compatibility:** Cortex Code CLI v1.0.42+, Claude Code CLI latest
