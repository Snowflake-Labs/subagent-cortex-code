# Cortex Code for Codex — CLI Install

Enables Codex to run Snowflake queries via the `cortexcode-tool` CLI.

Codex does not use a skill directory for this integration. Instead, `cortexcode-tool` is installed as a standalone CLI that Codex calls directly as a foreground command.

## Why CLI instead of skill?

Codex's sandbox blocks the interactive approval prompts that `cortex -p` requires without `--bypass`. The `cortexcode-tool` wraps `cortex` with `--bypass` and `approval_mode: auto`, making it safe and reliable in non-TTY environments. Codex calls it as a single foreground command and automatically waits for it to complete.

## Prerequisites

- Codex CLI installed
- Cortex Code CLI installed and configured (`which cortex` should return a path)
- Active Snowflake connection (`cortex connections list`)
- Python 3.8+

## Install

```bash
git clone https://github.com/Snowflake-Labs/subagent-cortex-code.git
cd subagent-cortex-code
bash integrations/codex/install.sh
```

The script:
1. Installs `cortexcode-tool` CLI to `~/.local/bin/` (via `integrations/cli-tool/setup.sh`)
2. Auto-detects your active Cortex connection from `cortex connections list`
3. Writes config to `~/.config/cortexcode-tool/config.yaml` (auto-detected — no `--config` flag needed)

## Verify

```bash
cortexcode-tool --version
cortexcode-tool "How many databases do I have in Snowflake?" --envelope RO
```

Expected: the tool runs for 30–90 seconds, then prints formatted results.

## Usage from Codex

**First time**: paste these into a Codex session to confirm the tool is discoverable:

```
which cortexcode-tool
cortexcode-tool --help
```

Once discovered, Codex will invoke `cortexcode-tool` for Snowflake questions automatically. You can be explicit or implicit — both work:

```bash
# Explicit
cortexcode-tool "How many databases do I have in Snowflake?"

# Implicit — Codex detects the Snowflake intent and calls cortexcode-tool on its own
How many databases do I have in Snowflake?
```

No need to specify `--envelope` in your prompts. Codex selects the appropriate envelope based on the operation.

Do **not** background the command (`& disown`). Codex automatically waits for foreground commands to complete (30–90 seconds is normal).

## What gets installed

```
~/.local/bin/cortexcode-tool          # CLI entry point
~/.local/lib/cortexcode-tool/         # Python package
~/.config/cortexcode-tool/config.yaml # Config (auto-detected by the tool)
```

Config example:
```yaml
security:
  approval_mode: "auto"
  audit_log_path: "/tmp/cortexcode-tool-codex-audit.log"
  cache_dir: "/tmp/cortexcode-tool-cache"

cortex:
  connection_name: "your-connection-name"
  default_envelope: "RW"

logging:
  file: "/tmp/cortexcode-tool-codex.log"
```

Audit/log paths use `/tmp/` to avoid Codex sandbox permission issues. The config itself lives at `~/.config/cortexcode-tool/` and survives reboots.

## Update connection

If you switch Cortex connections:
```bash
# Re-run install to auto-detect new active connection
bash integrations/codex/install.sh

# Or edit manually
vi ~/.config/cortexcode-tool/config.yaml
```

## Uninstall

```bash
bash integrations/cli-tool/uninstall.sh
rm -f ~/.config/cortexcode-tool/config.yaml
```

## Troubleshooting

**`cortexcode-tool` not found:**
```bash
which cortexcode-tool
# If missing, re-run: bash integrations/codex/install.sh
# Also ensure ~/.local/bin is in PATH
export PATH="$HOME/.local/bin:$PATH"
```

**Command hangs in Codex:**
```bash
# Verify approval_mode is auto (not prompt)
cat ~/.config/cortexcode-tool/config.yaml | grep approval_mode
# Must be: approval_mode: "auto"

# Verify Cortex connection works
cortex connections list
cortex -p "SHOW DATABASES;" --bypass --output-format stream-json
```

**Wrong connection used:**
```bash
# Check which connection is active
cortex connections list
# Edit config
vi ~/.config/cortexcode-tool/config.yaml  # update connection_name
```

**Permission errors on audit log:**
The config uses `/tmp/` paths for logs specifically to avoid Codex sandbox restrictions. If you see permission errors, verify `audit_log_path` and `cache_dir` in your config point to `/tmp/`.
