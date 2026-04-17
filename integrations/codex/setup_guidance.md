# Codex + CoCo Skill Setup Guide

This guide explains how to set up **OpenAI Codex CLI** so that:

1. **Codex inference routes to Snowflake Cortex / Corvo** for the main assistant model responses.
2. The **`cortex-code` skill** is available inside Codex and can route Snowflake-specialized tasks to **Cortex Code CLI**.

This gives you a two-layer setup:

- **Layer 1 — Codex inference**: `codex` talks to Snowflake Cortex API for model responses.
- **Layer 2 — CoCo skill**: inside Codex, the `cortex-code` skill can invoke local `cortex` CLI for Snowflake-specialist execution.

---

## Architecture

```text
Codex CLI
  ├─ Main inference → Snowflake Cortex REST API / Corvo
  └─ Skill-based Snowflake execution → local cortex CLI
```

### What this means in practice

- When you launch `codex`, the assistant itself uses Snowflake-backed inference.
- When you ask Codex Snowflake-specific questions, the installed `cortex-code` skill can route those tasks through the local `cortex` CLI.
- Codex remains the main orchestrator and user-facing interface.

---

## Folder layout used in this setup

### Development copy

```text
/Users/<username>/Documents/Code/Codex/CoCo_skill
```

Use this folder to edit and maintain the skill.

### Installed global Codex skill

```text
~/.codex/skills/cortex-code
```

This is the version Codex discovers and uses in sessions.

---

## Prerequisites

Before using this setup, make sure you have all of the following:

- Codex CLI installed and working
- Cortex Code CLI installed and working
- A valid Snowhouse / Snowflake PAT token for Codex inference
- A working Snowflake/Cortex connection for the local `cortex` CLI
- A shell profile that exports the Snowhouse token for Codex

---

## Part 1: Configure Codex to use Snowflake for inference

This is the setup that makes plain `codex` route its model inference to Snowflake Cortex / Corvo.

### 1.1 Store the Snowhouse token in a file

Expected token file:

```text
~/.snowflake/snowflake_token
```

Make sure it exists and is readable only by your user:

```bash
ls -l ~/.snowflake/snowflake_token
chmod 600 ~/.snowflake/snowflake_token
```

### 1.2 Configure your shell to export `SNOWFLAKE_PAT`

Add this to `~/.zshrc`:

```bash
# Snowhouse PAT for Codex Cortex inference
if [ -f "$HOME/.snowflake/snowflake_token" ]; then
  export SNOWFLAKE_PAT="$(cat "$HOME/.snowflake/snowflake_token")"
fi
```

Reload your shell:

```bash
source ~/.zshrc
```

### 1.3 Configure Codex provider settings

Edit:

```text
~/.codex/config.toml
```

Recommended configuration:

```toml
model_provider = "sfc"
model = "openai-gpt-5.4"
approvals_reviewer = "user"
web_search = "disabled"

[model_providers.sfc]
name = "OpenAI"
base_url = "https://<your-account>.snowflakecomputing.com/api/v2/cortex/v1"
env_key = "SNOWFLAKE_PAT"
wire_api = "responses"

[memories]
generate_memories = true
use_memories = true

[features]
memories = true
```

### 1.4 Start Codex normally

Once the shell and config are set, you should be able to launch Codex directly:

```bash
codex
```

You should **not** need to type:

```bash
env OPENAI_API_KEY="$(cat ~/.snowflake/snowflake_token)" codex
```

That older workaround is no longer necessary if `SNOWFLAKE_PAT` is configured correctly.

---

## Part 2: Configure the `cortex-code` skill for Codex

This is the skill that lets Codex route Snowflake-specific work to the local `cortex` CLI.

### 2.1 Development source of truth

The maintained development copy lives here:

```text
/Users/<username>/Documents/Code/Codex/CoCo_skill
```

This directory now contains:

- Codex-compatible `SKILL.md`
- Claude-derived working scripts
- Codex-adjusted naming and paths
- docs, tests, security helpers, and references

### 2.2 Install the skill into Codex

Sync the development copy into the global Codex skills folder:

```bash
rsync -a --delete --exclude 'backups' \
  /Users/<username>/Documents/Code/Codex/CoCo_skill/ \
  ~/.codex/skills/cortex-code/
```

### 2.3 Restart Codex

After installation or updates, restart Codex so it reloads skills.

---

## Part 3: Verify the required tools

### 3.1 Verify Codex starts

```bash
codex
```

If Codex fails with a `401 Unauthorized` related to Snowhouse, check:

- `~/.codex/config.toml`
- `SNOWFLAKE_PAT` in your shell
- `~/.snowflake/snowflake_token`

### 3.2 Verify the local `cortex` CLI exists

```bash
which cortex
cortex --version
cortex skill list
```

If `cortex` is missing or broken, the skill may trigger but fail during execution.

### 3.3 Verify the skill is visible in Codex

Inside a fresh Codex session, ask:

```text
which skill do you have
```

You should see:

```text
cortex-code
```

If not, restart Codex and confirm the skill is installed at:

```text
~/.codex/skills/cortex-code
```

---

## Part 4: How the skill is expected to behave

### 4.1 Trigger behavior

The skill should apply to Snowflake/Cortex prompts such as:

- `how many db i have in snowflake`
- `list my Snowflake warehouses`
- `create a table in DB_stock.public called tmp_to_drop`
- `help me write a Snowpark query`

### 4.2 Routing behavior

The skill uses:

```text
scripts/route_request.py
```

to classify prompts as either:

- `cortex`
- `codex`
- `blocked`

### 4.3 Wrapper and executor behavior

The skill uses two main execution paths:

#### Wrapper

```bash
python3 scripts/security_wrapper.py --prompt "USER_PROMPT_HERE" --envelope '{"mode":"RO"}'
```

Use JSON envelope format with the wrapper.

#### Direct executor

```bash
python3 scripts/execute_cortex.py --prompt "USER_PROMPT_HERE" --envelope RO
```

Use plain envelope tokens with the direct executor.

### 4.4 Approval behavior

With the current Claude-like behavior, you may still see two kinds of approvals:

#### Codex harness approval

This is the real Codex permission prompt for shell commands.

Example:

```text
You approved codex to run python3 ... this time
```

#### Skill-internal approval

The wrapper may also return an approval payload such as:

- `approve`
- `approve_all`
- `deny`

This comes from the skill's own security model, inherited from the original Claude-style implementation.

This is expected with the current close-to-Claude setup.

---

## Part 5: Current design choices in this Codex port

This setup intentionally keeps a **close match** to the working Claude skill, with only the necessary Codex-specific changes.

### Kept close to Claude

- working script implementations from the Claude skill
- security wrappers and approval model
- routing logic structure
- audit logging and config model
- references and troubleshooting docs

### Adjusted for Codex

- all naming uses `Codex` instead of `Claude`
- paths use `~/.codex/skills/cortex-code`
- default audit/config examples point to Codex locations
- current `SKILL.md` is Codex-oriented

---

## Part 6: Important paths

### Main Codex config

```text
~/.codex/config.toml
```

### Snowhouse token

```text
~/.snowflake/snowflake_token
```

### Shell profile

```text
~/.zshrc
```

### Installed global skill

```text
~/.codex/skills/cortex-code
```

### Development copy

```text
/Users/<username>/Documents/Code/Codex/CoCo_skill
```

---

## Part 7: Typical update workflow

When you want to edit the skill:

1. Make changes in:
   ```text
   /Users/<username>/Documents/Code/Codex/CoCo_skill
   ```
2. Verify the files locally.
3. Sync them into the installed global skill:
   ```bash
   rsync -a --delete --exclude 'backups' \
     /Users/<username>/Documents/Code/Codex/CoCo_skill/ \
     ~/.codex/skills/cortex-code/
   ```
4. Restart Codex.
5. Retest with a Snowflake prompt.

---

## Part 8: Troubleshooting

### Problem: Codex fails at startup with 401 Unauthorized

Likely causes:

- invalid or wrong Snowhouse token
- `SNOWFLAKE_PAT` not exported
- wrong `env_key` in `~/.codex/config.toml`
- expired or mismatched Snowhouse PAT

Check:

```bash
source ~/.zshrc
echo "$SNOWFLAKE_PAT" | head -c 20
sed -n '1,80p' ~/.codex/config.toml
```

### Problem: `cortex-code` does not appear in skill list

Check:

```bash
find ~/.codex/skills/cortex-code -maxdepth 2 | sort | head -100
```

Then restart Codex.

### Problem: wrapper rejects `--envelope "RO"`

This is expected. The wrapper requires JSON envelopes.

Use:

```bash
python3 scripts/security_wrapper.py --prompt "..." --envelope '{"mode":"RO"}'
```

### Problem: executor still does not return results

If `cortex` works manually but the skill path stalls, the likely issue is in the script integration path rather than Codex inference.

Check:

```bash
which cortex
cortex skill list
python3 ~/.codex/skills/cortex-code/scripts/execute_cortex.py --help
```

### Problem: skill uses approval twice

That can happen because this port intentionally stays close to the Claude skill design.

You may see:

- Codex harness approval
- skill-internal wrapper approval

This is expected for the current design.

---

## Part 9: Current recommended mental model

Use this setup like this:

- **Codex** = the main assistant and orchestrator
- **Snowflake Cortex / Corvo** = the model inference backend for Codex
- **`cortex-code` skill** = the Snowflake specialist execution layer
- **local `cortex` CLI** = the tool the skill invokes for Snowflake work

---

## Part 10: Summary

If everything is configured correctly:

- `codex` starts normally and uses Snowflake-backed inference
- `cortex-code` appears in the available skills list
- Snowflake prompts are routed through the skill
- the skill can invoke local `cortex` CLI for Snowflake-specific work
- the development source of truth remains:

```text
/Users/<username>/Documents/Code/Codex/CoCo_skill
```

and the installed copy remains:

```text
~/.codex/skills/cortex-code
```

