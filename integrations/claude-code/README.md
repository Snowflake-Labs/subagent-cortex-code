# Cortex Code Skill — Claude Code

Enables Claude Code to route Snowflake queries to Cortex Code CLI automatically.

## Prerequisites

- Claude Code CLI installed
- Cortex Code CLI installed and configured (`which cortex` should return a path)
- Active Snowflake connection (`cortex connections list`)
- Python 3.8+

## Install

```bash
npx skills add snowflake-labs/subagent-cortex-code --copy --global
```

This installs `skills/cortex-code/` from this repo to `~/.claude/skills/cortex-code/`.

**Verify:**
```bash
ls ~/.claude/skills/cortex-code/SKILL.md
```

Start Claude Code — the skill loads automatically and routes Snowflake questions to Cortex Code.

## Optional: configure security mode

```bash
cp ~/.claude/skills/cortex-code/config.yaml.example \
   ~/.claude/skills/cortex-code/config.yaml
```

Edit `~/.claude/skills/cortex-code/config.yaml`:
```yaml
security:
  approval_mode: "auto"   # or "prompt" (default) or "envelope_only"

cortex:
  connection_name: "your-connection-name"
```

Default is `prompt` mode — Claude Code will ask before executing Snowflake operations.
Use `auto` for fully automated workflows.

## What gets installed

```
~/.claude/skills/cortex-code/
├── SKILL.md                 # Skill definition loaded by Claude Code
├── config.yaml.example      # Configuration template
├── scripts/
│   ├── route_request.py     # LLM-based routing logic
│   ├── execute_cortex.py    # Headless Cortex execution (--bypass)
│   ├── discover_cortex.py   # Cortex capability discovery
│   ├── read_cortex_sessions.py
│   ├── predict_tools.py
│   └── security_wrapper.py
└── security/
    ├── config_manager.py
    ├── audit_logger.py
    ├── approval_handler.py
    ├── cache_manager.py
    ├── prompt_sanitizer.py
    └── policies/
```

## How it works

When you ask a Snowflake-related question:

1. Claude Code loads the skill and calls `scripts/route_request.py` to classify the request
2. If routed to Cortex: Claude Code enriches the prompt with session context, then calls `scripts/execute_cortex.py`
3. `execute_cortex.py` runs `cortex -p "..." --output-format stream-json --bypass` headlessly
4. Results stream back and Claude Code presents them to you

**Routing Principle**: ONLY Snowflake operations → Cortex. Everything else → Claude Code handles directly.

## What gets routed to Cortex

**Routed to Cortex:**
- Snowflake databases, warehouses, schemas, tables
- SQL queries on Snowflake
- Cortex AI features (Cortex Search, Cortex Analyst, ML functions)
- Snowpark, dynamic tables, streams, tasks
- Snowflake governance, data quality, security

**Stays in Claude Code:**
- Local file reads/writes/edits
- General Python, JavaScript, shell scripts
- Non-Snowflake databases (PostgreSQL, MySQL, etc.)
- Git, GitHub, CI/CD
- Web development

## Security envelopes

| Envelope | Use Case | What's blocked |
|----------|----------|----------------|
| **RO** | Queries and reads | Edit, Write, destructive Bash |
| **RW** | Data modifications | Destructive ops (rm -rf, sudo) |
| **RESEARCH** | Exploratory work | Write operations |
| **DEPLOY** | Full access | Nothing |
| **NONE** | Custom | Specify --disallowed-tools |

## Uninstall

```bash
bash integrations/claude-code/uninstall.sh
# or manually:
rm -rf ~/.claude/skills/cortex-code
```

## Troubleshooting

**Skill not loading:**
```bash
ls ~/.claude/skills/cortex-code/SKILL.md
# If missing, re-run: npx skills add snowflake-labs/subagent-cortex-code --copy
```

**Cortex not found:**
```bash
which cortex
# Install: curl -LsS https://ai.snowflake.com/static/cc-scripts/install.sh | sh
```

**No active connection:**
```bash
cortex connections list
cortex connections create
```

**Check approval mode:**
```bash
cat ~/.claude/skills/cortex-code/config.yaml | grep approval_mode
```

**Routing sends Snowflake query to Claude Code instead of Cortex:**
- Include "Snowflake" or "Cortex" explicitly in your question
- The router uses LLM logic + keyword detection; explicit mentions guarantee routing

For more: [SECURITY_GUIDE.md](../../SECURITY_GUIDE.md)
