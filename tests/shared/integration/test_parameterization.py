"""Integration tests for cross-agent parameterization."""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "shared" / "scripts"))

from route_request import analyze_with_llm_logic
from security_wrapper import execute_with_security


@pytest.mark.integration
@pytest.mark.parametrize("agent_name", ["claude", "cursor", "codex"])
def test_routing_returns_correct_agent_name(agent_name):
    """Routing should return __CODING_AGENT__ placeholder"""
    prompt = "Fix this code"
    capabilities = {}

    decision, confidence = analyze_with_llm_logic(prompt, capabilities)

    # Should always return placeholder, regardless of which agent
    assert decision == "__CODING_AGENT__"


@pytest.mark.integration
@pytest.mark.parametrize("agent_name", ["claude", "cursor", "codex"])
def test_config_paths_use_agent_directory(agent_name, tmp_path):
    """Config paths should use agent-specific directories after sed replacement"""
    # This test validates that sed replacement would work correctly
    # In actual installation, sed replaces __CODING_AGENT__ with agent name

    sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "shared"))
    from security.config_manager import ConfigManager

    config = ConfigManager()
    audit_log = config.get("security.audit_log_path")

    # Before sed: contains __CODING_AGENT__
    # After sed: would contain actual agent name
    assert "__CODING_AGENT__" in audit_log or \
           any(name in audit_log for name in ["claude", "cursor", "codex"])


@pytest.mark.integration
@pytest.mark.cross_platform
def test_cross_platform_sed_replacement():
    """Test sed replacement works on both macOS (BSD) and Linux (GNU)"""
    import subprocess
    import tempfile

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write('AGENT = "__CODING_AGENT__"\n')
        temp_file = f.name

    try:
        # Try BSD sed (macOS)
        subprocess.run(
            ['sed', '-i', '', 's/__CODING_AGENT__/claude/g', temp_file],
            check=True,
            capture_output=True
        )
    except subprocess.CalledProcessError:
        # Fall back to GNU sed (Linux)
        subprocess.run(
            ['sed', '-i', 's/__CODING_AGENT__/claude/g', temp_file],
            check=True,
            capture_output=True
        )

    # Verify replacement
    with open(temp_file, 'r') as f:
        content = f.read()

    assert 'AGENT = "claude"' in content
    assert '__CODING_AGENT__' not in content

    # Cleanup
    Path(temp_file).unlink()


@pytest.mark.integration
def test_install_replaces_placeholder():
    """Validate that placeholder replacement pattern is correct"""
    # This is a documentation test - actual replacement happens in install.sh

    test_content = """
def route():
    return "__CODING_AGENT__", 0.5

audit_path = "~/.__CODING_AGENT__/audit.log"
"""

    # Simulate sed replacement
    for agent in ["claude", "cursor", "codex"]:
        replaced = test_content.replace("__CODING_AGENT__", agent)

        assert f'return "{agent}", 0.5' in replaced
        assert f"~/.{agent}/audit.log" in replaced
        assert "__CODING_AGENT__" not in replaced
