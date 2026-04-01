"""Configuration manager with 3-layer precedence."""
import copy
import sys
from pathlib import Path
from typing import Any, Optional, Dict
import yaml


class ConfigManager:
    """Manages security configuration with precedence: org policy > user config > defaults."""

    DEFAULT_CONFIG = {
        "security": {
            "approval_mode": "prompt",
            "tool_prediction_confidence_threshold": 0.7,
            "allow_tool_expansion": True,
            "audit_log_path": "~/.claude/skills/cortex-code/audit.log",
            "audit_log_rotation": "10MB",
            "audit_log_retention": 30,
            "sanitize_conversation_history": True,
            "sanitize_session_files": True,
            "max_history_items": 3,
            "cache_dir": "~/.cache/cortex-skill",
            "cache_permissions": "0600",
            "allowed_envelopes": ["RO", "RW", "RESEARCH"],
            "deploy_envelope_confirmation": True,
            "credential_file_allowlist": [
                "~/.ssh/*",
                "~/.snowflake/*",
                "**/.env",
                "**/.env.*",
                "**/credentials.json",
                "**/*_key.p8",
                "**/*_key.pem",
                "~/.aws/credentials",
                "~/.kube/config"
            ]
        }
    }

    def __init__(
        self,
        config_path: Optional[Path] = None,
        org_policy_path: Optional[Path] = None
    ):
        """Initialize config manager."""
        self._config = self._load_config(config_path, org_policy_path)

    def _load_config(
        self,
        config_path: Optional[Path],
        org_policy_path: Optional[Path]
    ) -> Dict:
        """Load configuration with 3-layer precedence."""
        # Start with defaults
        config = copy.deepcopy(self.DEFAULT_CONFIG)

        # Load user config if exists
        if config_path and config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    try:
                        user_config = yaml.safe_load(f) or {}
                        config = self._merge_config(config, user_config)
                    except yaml.YAMLError as e:
                        print(f"Warning: Failed to parse user config {config_path}: {e}", file=sys.stderr)
            except OSError as e:
                print(f"Warning: Failed to read user config {config_path}: {e}", file=sys.stderr)

        # Load org policy if exists
        if org_policy_path and org_policy_path.exists():
            try:
                with open(org_policy_path, 'r') as f:
                    try:
                        org_policy = yaml.safe_load(f) or {}

                        # If override flag set, org policy wins completely
                        if org_policy.get("security", {}).get("override_user_config"):
                            # Merge org policy over defaults (skip user config)
                            config = self._merge_config(copy.deepcopy(self.DEFAULT_CONFIG), org_policy)
                        else:
                            # Normal merge: org policy > user config > defaults
                            config = self._merge_config(config, org_policy)
                    except yaml.YAMLError as e:
                        print(f"Warning: Failed to parse org policy {org_policy_path}: {e}", file=sys.stderr)
            except OSError as e:
                print(f"Warning: Failed to read org policy {org_policy_path}: {e}", file=sys.stderr)

        return config

    def _merge_config(self, base: Dict, override: Dict) -> Dict:
        """Deep merge override into base."""
        result = copy.deepcopy(base)
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        return result

    def get(self, key: str, default: Any = None) -> Any:
        """Get config value by dot-notation key."""
        keys = key.split(".")
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value
