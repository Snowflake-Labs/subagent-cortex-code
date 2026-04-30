# Claude Security Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix Claude Code integration security/correctness failures from the Carvana evaluation and verify with focused regression tests plus the full suite.

**Architecture:** Keep the existing shared-script architecture, but make the execution boundary safer and testable: defaults become prompt-first, wrappers and Python CLI agree on `--output-file`, subprocess lifecycle is bounded, and stdout/stderr roles are explicit. Avoid broad refactors while adding regression tests for each reported failure.

**Tech Stack:** Python 3, pytest, shell wrappers, YAML config, Markdown docs.

---

## File Structure

- Modify `shared/scripts/execute_cortex.py`: add output-file support, timeout/error handling, stderr draining, safer envelope blocklists, non-stdout heartbeat, robust tool_result content handling.
- Modify `scripts/execute_cortex.py`: keep root script aligned with shared execution behavior where applicable.
- Modify `shared/scripts/execute_cortex_async.sh` and `shared/scripts/execute_cortex_codex.sh`: rely on supported CLI contract and avoid unsafe Python string interpolation when reading result files.
- Modify `integrations/claude-code/config.yaml`: change shipped approval mode to `prompt`.
- Modify `integrations/claude-code/install.sh`, `README.md`, and `integrations/claude-code/skill.md`: align docs with prompt default and explicit auto-mode risk.
- Modify `shared/scripts/route_request.py` or `tests/shared/unit/test_route_request.py`: restore test import compatibility.
- Add/modify tests in `tests/unit/test_execute_cortex.py`, `tests/shared/unit/test_route_request.py`, and optionally wrapper-focused tests.

## Tasks

### Task 1: Restore test collection

**Files:**
- Modify: `shared/scripts/route_request.py`
- Test: `tests/shared/unit/test_route_request.py`

- [ ] Add a backwards-compatible alias `CODING_AGENT_INDICATORS = CLAUDE_CODE_INDICATORS` near the existing indicator list.
- [ ] Run `pytest tests/shared/unit/test_route_request.py -q` and verify collection progresses beyond the import error.

### Task 2: Fix wrapper/CLI output-file contract

**Files:**
- Modify: `shared/scripts/execute_cortex.py`
- Modify: `scripts/execute_cortex.py`
- Test: `tests/unit/test_execute_cortex.py`

- [ ] Add failing tests proving `main()` accepts `--output-file` and writes the JSON result to that file without corrupting stdout.
- [ ] Add argparse support for `--output-file` and write JSON atomically enough for wrapper usage.
- [ ] Run `pytest tests/unit/test_execute_cortex.py -q` and verify the new tests pass.

### Task 3: Harden subprocess lifecycle

**Files:**
- Modify: `shared/scripts/execute_cortex.py`
- Modify: `scripts/execute_cortex.py`
- Test: `tests/unit/test_execute_cortex.py`

- [ ] Add tests for timeout behavior, stderr capture on nonzero exit, exception cleanup, and list-valued tool_result content.
- [ ] Replace unbounded `process.wait()` with timeout-aware completion and kill/wait cleanup.
- [ ] Drain stderr concurrently or through a safe non-deadlocking pattern.
- [ ] Move heartbeat output to stderr.
- [ ] Run `pytest tests/unit/test_execute_cortex.py -q`.

### Task 4: Tighten envelope defaults

**Files:**
- Modify: `shared/scripts/execute_cortex.py`
- Modify: `scripts/execute_cortex.py`
- Test: `tests/unit/test_execute_cortex.py`

- [ ] Add tests showing RO and RESEARCH block `Bash` entirely and RW blocks destructive shell patterns at minimum.
- [ ] Update envelope blocklists to include `Bash` for read-only/research modes.
- [ ] Run execute-cortex unit tests.

### Task 5: Align Claude security defaults and docs

**Files:**
- Modify: `integrations/claude-code/config.yaml`
- Modify: `integrations/claude-code/install.sh`
- Modify: `README.md`
- Modify: `integrations/claude-code/skill.md`

- [ ] Change shipped Claude config to `approval_mode: "prompt"`.
- [ ] Update installer comments to stop claiming auto is created for CLI usage.
- [ ] Update docs so auto mode is opt-in, not the Claude default.
- [ ] Add a note that headless auto mode uses `--bypass` and must be considered trusted/opt-in.

### Task 6: Comprehensive verification

**Files:**
- All changed files.

- [ ] Run focused tests: `pytest tests/shared/unit/test_route_request.py tests/unit/test_execute_cortex.py -q`.
- [ ] Run full suite: `pytest -q`.
- [ ] Run shell integration smoke if feasible: `bash test_all_integrations.sh`.
- [ ] Inspect `git diff --check` and `git status --short`.

### Task 7: PR creation

**Files:**
- Git branch metadata only.

- [ ] Commit the implementation with a clear message.
- [ ] Push `fix/claude-security-hardening` to `origin`.
- [ ] Create a GitHub PR summarizing security/correctness fixes and test evidence.
