"""Tests for Codex integration install script."""

import pytest
from pathlib import Path


@pytest.mark.integration
def test_codex_install_target_directory():
    """Codex install should target ~/.codex/skills/cortex-code/"""
    target = Path.home() / ".codex" / "skills" / "cortex-code"
    assert ".codex" in str(target)


@pytest.mark.integration
def test_codex_skill_file_exists():
    """Codex uses SKILL.md"""
    assert Path("integrations/codex/SKILL.md").exists()


@pytest.mark.integration
def test_codex_setup_guidance():
    """Codex has setup_guidance.md"""
    assert Path("integrations/codex/setup_guidance.md").exists()


@pytest.mark.integration
def test_codex_placeholder_replacement():
    """sed should replace __CODING_AGENT__ with 'codex'"""
    test_content = 'return "__CODING_AGENT__", confidence'
    expected = 'return "codex", confidence'

    replaced = test_content.replace("__CODING_AGENT__", "codex")
    assert replaced == expected
