# Cortexcode Tool — CLI

A standalone CLI that brings Cortex Code's Snowflake expertise to VSCode, Windsurf, terminal, and any environment without a skills-based agent.

> **Claude Code and Cursor** use the skill-based integration via `npx skills add`. This CLI is for other environments.
> **Codex** installs this tool via `bash integrations/codex/install.sh` (which also writes the right config for Codex's sandbox).

## Supported environments

- VSCode (task runner + code snippets)
- Windsurf
- Terminal (any shell)
- Codex (via `integrations/codex/install.sh`)

## Install

```bash
git clone https://github.com/Snowflake-Labs/subagent-cortex-code.git
cd subagent-cortex-code/integrations/cli-tool
bash setup.sh
```

Installs `cortexcode-tool` to `~/.local/bin/`. Ensure `~/.local/bin` is in your `PATH`.

**Verify:**
```bash
cortexcode-tool --version
cortexcode-tool "How many databases do I have in Snowflake?"
```

## Prerequisites

- Python 3.8+
- Cortex Code CLI v1.0.42+ installed (`which cortex`)
- Active Snowflake connection (`cortex connections list`)

## Configuration

The tool auto-detects `~/.config/cortexcode-tool/config.yaml`. Create it from the example:

```bash
mkdir -p ~/.config/cortexcode-tool
cp config.yaml.example ~/.config/cortexcode-tool/config.yaml
# edit as needed
```

Key settings:
```yaml
security:
  approval_mode: "prompt"  # or "auto" or "envelope_only"

cortex:
  connection_name: "your-connection-name"
  default_envelope: "RW"
```

See `config.yaml.example` for all options.

## Usage

```bash
# Query Snowflake
cortexcode-tool "Show me top 10 customers by revenue"

# Specify security envelope
cortexcode-tool "List all databases" --envelope RO
cortexcode-tool "Create a backup table" --envelope RW

# Specify connection
cortexcode-tool "your question" --connection my-snowflake-connection
```

Envelopes:
- `RO` — read-only (blocks writes)
- `RW` — read-write (blocks destructive ops)
- `RESEARCH` — read + web access
- `DEPLOY` — full access

## Package structure

```
cortexcode-tool/
├── cortexcode_tool/          # Python package
│   ├── core/                 # Routing, execution, discovery
│   ├── security/             # Approval, audit, cache, sanitization
│   └── ide_adapters/         # VSCode, Cursor adapter
├── setup.sh                  # Install to ~/.local/bin/
├── uninstall.sh
└── config.yaml.example       # Configuration template
```

## Uninstall

```bash
bash uninstall.sh
```

## Troubleshooting

**`cortexcode-tool` not found:**
```bash
# Add ~/.local/bin to PATH
export PATH="$HOME/.local/bin:$PATH"
# Re-run setup
bash setup.sh
```

**No active connection:**
```bash
cortex connections list
cortex connections create
```

**Command hangs (approval prompt):**
```bash
# Check approval mode
cat ~/.config/cortexcode-tool/config.yaml | grep approval_mode
# For automated use, set: approval_mode: "auto"
```

---

Copyright © 2026 Snowflake Inc. All rights reserved.
