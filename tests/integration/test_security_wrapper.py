"""Integration tests for security wrapper orchestrator."""
import json
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.security_wrapper import execute_with_security


class TestSecurityWrapperInitialization:
    """Test security wrapper initialization and component setup."""

    def test_security_wrapper_initialization(self, temp_dir, sample_config):
        """Test that security wrapper initializes all components correctly in dry-run mode."""
        # Create config files
        config_path = temp_dir / "config.yaml"
        config_path.write_text("""
security:
  approval_mode: prompt
  audit_log_path: {}/audit.log
  cache_dir: {}/.cache
  sanitize_conversation_history: true
""".format(temp_dir, temp_dir))

        # Execute with dry-run (should not actually call Cortex)
        result = execute_with_security(
            prompt="Test prompt",
            config_path=str(config_path),
            dry_run=True
        )

        # Verify initialization
        assert result["status"] == "initialized"
        assert "config" in result
        assert "audit_logger" in result
        assert "cache_manager" in result
        assert "prompt_sanitizer" in result
        assert "approval_handler" in result
        assert result["dry_run"] is True


class TestSecurityWrapperApprovalFlow:
    """Test security wrapper approval mode flow."""

    def test_security_wrapper_prompt_mode_flow(self, temp_dir):
        """Test approval flow with prompt mode."""
        # Create config with prompt mode
        config_path = temp_dir / "config.yaml"
        config_path.write_text("""
security:
  approval_mode: prompt
  audit_log_path: {}/audit.log
  cache_dir: {}/.cache
  sanitize_conversation_history: true
  allowed_envelopes: ["RO", "RW"]
""".format(temp_dir, temp_dir))

        # Mock user approval
        with patch('builtins.input', return_value='y'):
            result = execute_with_security(
                prompt="List all files in the database",
                config_path=str(config_path),
                dry_run=True
            )

        # Verify prompt mode was detected
        assert result["status"] == "initialized"
        assert result["config"]["approval_mode"] == "prompt"
        assert "approval_handler" in result

    def test_security_wrapper_auto_mode(self, temp_dir):
        """Test wrapper with auto approval mode."""
        # Create config with auto mode
        config_path = temp_dir / "config.yaml"
        config_path.write_text("""
security:
  approval_mode: auto
  audit_log_path: {}/audit.log
  cache_dir: {}/.cache
""".format(temp_dir, temp_dir))

        result = execute_with_security(
            prompt="Test auto-approval",
            config_path=str(config_path),
            dry_run=True
        )

        assert result["status"] == "initialized"
        assert result["config"]["approval_mode"] == "auto"


class TestSecurityWrapperSanitization:
    """Test security wrapper prompt sanitization."""

    def test_security_wrapper_sanitization(self, temp_dir):
        """Test that prompt sanitization works correctly."""
        config_path = temp_dir / "config.yaml"
        config_path.write_text("""
security:
  approval_mode: auto
  audit_log_path: {}/audit.log
  cache_dir: {}/.cache
  sanitize_conversation_history: true
""".format(temp_dir, temp_dir))

        # Prompt with PII
        prompt = "Query user data for email@test.com with credit card 1234-5678-9012-3456"

        result = execute_with_security(
            prompt=prompt,
            config_path=str(config_path),
            dry_run=True
        )

        # Verify sanitization occurred
        assert result["status"] == "initialized"
        sanitized = result.get("sanitized_prompt", "")
        assert "<EMAIL>" in sanitized
        assert "<CREDIT_CARD>" in sanitized
        assert "email@test.com" not in sanitized
        assert "1234-5678-9012-3456" not in sanitized

    def test_security_wrapper_no_sanitization_when_disabled(self, temp_dir):
        """Test that sanitization can be disabled."""
        config_path = temp_dir / "config.yaml"
        config_path.write_text("""
security:
  approval_mode: auto
  audit_log_path: {}/audit.log
  cache_dir: {}/.cache
  sanitize_conversation_history: false
""".format(temp_dir, temp_dir))

        prompt = "Query user data for email@test.com"

        result = execute_with_security(
            prompt=prompt,
            config_path=str(config_path),
            dry_run=True
        )

        # Verify no sanitization
        assert result["status"] == "initialized"
        sanitized = result.get("sanitized_prompt", prompt)
        # When disabled, original prompt should be preserved
        assert "email@test.com" in sanitized or sanitized == prompt


class TestSecurityWrapperOrgPolicy:
    """Test security wrapper with organization policy override."""

    def test_security_wrapper_org_policy_override(self, temp_dir):
        """Test that org policy overrides user config."""
        config_path = temp_dir / "config.yaml"
        config_path.write_text("""
security:
  approval_mode: auto
  audit_log_path: {}/audit.log
  cache_dir: {}/.cache
""".format(temp_dir, temp_dir))

        org_policy_path = temp_dir / "org_policy.yaml"
        org_policy_path.write_text("""
security:
  approval_mode: prompt
  allowed_envelopes: ["RO"]
""")

        result = execute_with_security(
            prompt="Test org policy",
            config_path=str(config_path),
            org_policy_path=str(org_policy_path),
            dry_run=True
        )

        # Verify org policy overrode user config
        assert result["status"] == "initialized"
        assert result["config"]["approval_mode"] == "prompt"
        assert result["config"]["allowed_envelopes"] == ["RO"]


class TestSecurityWrapperErrorHandling:
    """Test security wrapper error handling."""

    def test_security_wrapper_missing_config(self):
        """Test wrapper handles missing config gracefully."""
        result = execute_with_security(
            prompt="Test",
            config_path="/nonexistent/config.yaml",
            dry_run=True
        )

        # Should fall back to defaults
        assert result["status"] == "initialized"
        assert "config" in result

    def test_security_wrapper_malformed_config(self, temp_dir):
        """Test wrapper handles malformed config gracefully."""
        config_path = temp_dir / "config.yaml"
        config_path.write_text("invalid: yaml: content: [")

        result = execute_with_security(
            prompt="Test",
            config_path=str(config_path),
            dry_run=True
        )

        # Should fall back to defaults
        assert result["status"] == "initialized"
        assert "config" in result


class TestSecurityWrapperRouting:
    """Test security wrapper routing integration."""

    def test_security_wrapper_routing_to_cortex(self, temp_dir):
        """Test that Snowflake prompts route to cortex."""
        config_path = temp_dir / "config.yaml"
        config_path.write_text("""
security:
  approval_mode: auto
  audit_log_path: {}/audit.log
  cache_dir: {}/.cache
""".format(temp_dir, temp_dir))

        # Snowflake-specific prompt
        result = execute_with_security(
            prompt="Query Snowflake database for sales data",
            config_path=str(config_path),
            dry_run=True
        )

        # Verify routing to cortex
        assert result["status"] == "initialized"
        assert "routing" in result
        assert result["routing"]["decision"] == "cortex"
        assert result["routing"]["confidence"] > 0.5

    def test_security_wrapper_routing_to_claude(self, temp_dir):
        """Test that non-Snowflake prompts route to claude."""
        config_path = temp_dir / "config.yaml"
        config_path.write_text("""
security:
  approval_mode: auto
  audit_log_path: {}/audit.log
  cache_dir: {}/.cache
""".format(temp_dir, temp_dir))

        # Local file operation prompt
        result = execute_with_security(
            prompt="Read local file config.json and parse it",
            config_path=str(config_path),
            dry_run=True
        )

        # Verify routing to claude
        assert result["status"] == "initialized"
        assert "routing" in result
        assert result["routing"]["decision"] == "claude"

    def test_security_wrapper_blocks_credential_files(self, temp_dir):
        """Test that prompts with credential files are blocked."""
        config_path = temp_dir / "config.yaml"
        config_path.write_text("""
security:
  approval_mode: auto
  audit_log_path: {}/audit.log
  cache_dir: {}/.cache
  credential_file_allowlist:
    - "~/.ssh/*"
    - "**/credentials.json"
    - "**/.env"
""".format(temp_dir, temp_dir))

        # Test SSH credential file
        result = execute_with_security(
            prompt="Read ~/.ssh/id_rsa file and analyze it",
            config_path=str(config_path),
            dry_run=True
        )

        # Verify blocking
        assert result["status"] == "blocked"
        assert "credential file" in result["reason"].lower()
        assert "pattern_matched" in result

        # Test credentials.json
        result2 = execute_with_security(
            prompt="Parse credentials.json for database connection",
            config_path=str(config_path),
            dry_run=True
        )

        assert result2["status"] == "blocked"
        assert "credential file" in result2["reason"].lower()

        # Test .env file
        result3 = execute_with_security(
            prompt="Check .env file for API keys",
            config_path=str(config_path),
            dry_run=True
        )

        assert result3["status"] == "blocked"
        assert "credential file" in result3["reason"].lower()
