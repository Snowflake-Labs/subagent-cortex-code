# Cortex Code Skill for Codex

This repository contains a **Codex skill** named `cortex-code` that helps Codex route Snowflake-specific tasks to the local **Cortex Code CLI**.

This README covers the **skill only**.
It does **not** cover configuring Codex model inference through Snowflake / Corvo.

---

## What this skill does

The `cortex-code` skill gives Codex a structured workflow for Snowflake-related tasks such as:

- listing Snowflake databases, schemas, tables, and warehouses
- writing or explaining Snowflake SQL
- working with Snowpark, Cortex, dynamic tables, streams, and tasks
- handling Snowflake governance and security topics
- routing specialized Snowflake operations to the local `cortex` CLI

Codex remains the main assistant and orchestrator. The skill helps Codex decide when to invoke `cortex` for Snowflake-specialized work.

---

## What this skill does not do

This skill does not:

- configure Codex’s model provider
- configure Snowflake / Corvo inference for Codex itself
- replace the local `cortex` CLI
- replace your Snowflake connection setup

You still need a working local `cortex` installation and a valid Snowflake/Cortex connection.

---

## Prerequisites

Before using this skill, make sure:

- Codex CLI is installed
- Cortex Code CLI is installed
- `cortex` works in your shell
- your local `cortex` CLI is already configured to connect to Snowflake

Quick checks:

```bash
which cortex
cortex --version
cortex skill list
```

---

## Install the skill into Codex

Clone the Cortex Code integration repository and run the installation script:

```bash
# Clone the repository
git clone https://github.com/Snowflake-Labs/subagent-cortex-code.git
cd subagent-cortex-code

# Run the installation script
cd integrations/codex
./install.sh
```

This will:
- Copy shared scripts and security modules to `~/.codex/skills/cortex-code/`
- Parameterize for Codex environment
- Create default configuration if not exists
- Make scripts executable

Then restart Codex.

---

## Verify Codex sees the skill

In a fresh Codex session, ask:

```text
which skill do you have
```

You should see:

```text
cortex-code
```

If you do not see it:

- confirm the installed folder exists at `~/.codex/skills/cortex-code`
- restart Codex
- make sure `SKILL.md` exists inside the installed folder

---

## How the skill works

### 1. Skill trigger

The skill should be relevant for prompts such as:

- `how many db i have in snowflake`
- `show my Snowflake warehouses`
- `create a table in DB_stock.public called tmp_to_drop`
- `help me write a Snowpark query`

### 2. Routing

The skill uses:

```text
scripts/route_request.py
```

to classify requests into:

- `cortex`
- `codex`
- `blocked`

### 3. Execution paths

There are two main execution paths.

#### Security wrapper

```bash
python3 scripts/security_wrapper.py --prompt "USER_PROMPT_HERE" --envelope '{"mode":"RO"}'
```

Use the wrapper when you want the full skill security flow.

#### Direct executor

```bash
python3 scripts/execute_cortex.py --prompt "USER_PROMPT_HERE" --envelope RO
```

Use the direct executor when you want to invoke Cortex directly.

---

## Important envelope syntax

The two commands do **not** use the same envelope syntax.

### Wrapper syntax

Use JSON:

```bash
--envelope '{"mode":"RO"}'
```

### Executor syntax

Use plain values:

```bash
--envelope RO
```

This distinction matters.

---

## Approval behavior

This skill currently stays close to the original Claude-style implementation.

That means you may see two layers of approval:

### Codex harness approval

Codex may ask permission before running shell commands.

### Skill-internal approval

The wrapper may also return approval instructions such as:

- `approve`
- `approve_all`
- `deny`

This comes from the skill’s own internal security model.

---

## Common workflow

A typical Snowflake request in Codex may look like this:

1. Codex recognizes the prompt as Snowflake-related
2. Codex reads `SKILL.md`
3. Codex runs `scripts/route_request.py`
4. If routed to `cortex`, Codex uses the wrapper or executor
5. Cortex performs the Snowflake-specific work
6. Codex summarizes the result back to you

---

## Troubleshooting

### Skill does not appear in Codex

Check:

```bash
find ~/.codex/skills/cortex-code -maxdepth 2 | sort | head -100
```

Then restart Codex.

### Wrapper says `Invalid envelope JSON`

You passed the wrong envelope form.

Use:

```bash
python3 scripts/security_wrapper.py --prompt "..." --envelope '{"mode":"RO"}'
```

### Executor stalls or does not return visible output

Check whether `cortex` works directly:

```bash
which cortex
cortex skill list
```

Also inspect:

```bash
python3 ~/.codex/skills/cortex-code/scripts/execute_cortex.py --help
```

### Skill asks for approval twice

That is currently expected because:

- Codex has its own harness approval
- the skill wrapper has its own approval model

---

## Development workflow

This skill is part of the multi-IDE Cortex Code integration monorepo:

```text
https://github.com/Snowflake-Labs/subagent-cortex-code
```

The Codex-specific files live in:

```text
integrations/codex/
```

The shared code (scripts and security modules) lives in:

```text
shared/scripts/
shared/security/
```

To update the installed skill after making changes:

```bash
cd /path/to/subagent-cortex-code/integrations/codex
./install.sh
```

Restart Codex after installing updates.

---

## Key files

- `SKILL.md` — Codex skill definition and workflow
- `scripts/route_request.py` — prompt routing
- `scripts/security_wrapper.py` — secure wrapper execution path
- `scripts/execute_cortex.py` — direct Cortex execution path
- `security/config_manager.py` — config defaults and overrides
- `references/` — supporting docs and troubleshooting references

---

## Summary

Use this skill when you want Codex to handle Snowflake-related tasks through the local `cortex` CLI.

The skill is part of the multi-CodingAgent Cortex Code integration monorepo at:

```text
https://github.com/Snowflake-Labs/subagent-cortex-code
```

The installed runtime copy is at:

```text
~/.codex/skills/cortex-code
```
