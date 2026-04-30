"""Regression tests for cortexcode-tool config and cache hardening."""

import os
import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cortexcode_tool.security.cache_manager import CacheManager


def test_cli_example_config_defaults_to_prompt():
    config = yaml.safe_load(Path("integrations/cli-tool/config.yaml.example").read_text())

    assert config["security"]["approval_mode"] == "prompt"


def test_cli_setup_writes_prompt_default():
    setup_text = Path("integrations/cli-tool/setup.sh").read_text()

    assert 'approval_mode: "prompt"' in setup_text
    assert 'approval_mode: "auto"' not in setup_text


def test_cli_cache_directory_chmod_failure_is_nonfatal(tmp_path):
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()

    with pytest.warns(RuntimeWarning, match="Could not set secure permissions"):
        with pytest.MonkeyPatch.context() as monkeypatch:
            monkeypatch.setattr(os, "chmod", lambda *_args, **_kwargs: (_ for _ in ()).throw(PermissionError("denied")))
            cache = CacheManager(cache_dir)

    assert cache.cache_dir == cache_dir
