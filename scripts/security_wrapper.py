#!/usr/bin/env python3
"""
Security wrapper orchestrator for cortex-code skill.

Coordinates all security components:
- ConfigManager: Load and validate configuration
- AuditLogger: Log all executions
- CacheManager: Secure caching
- PromptSanitizer: Remove PII and detect injection
- ApprovalHandler: Tool prediction and user approval

This is the main entry point for secure Cortex execution.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional, Dict, Any

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from security.config_manager import ConfigManager
from security.audit_logger import AuditLogger
from security.cache_manager import CacheManager
from security.prompt_sanitizer import PromptSanitizer
from security.approval_handler import ApprovalHandler


def execute_with_security(
    prompt: str,
    config_path: Optional[str] = None,
    org_policy_path: Optional[str] = None,
    dry_run: bool = False,
    envelope: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Execute prompt with full security orchestration.

    This function:
    1. Loads configuration (with org policy override)
    2. Initializes all security components
    3. Sanitizes prompt if enabled
    4. Determines approval mode
    5. In dry-run mode: returns initialization status
    6. In live mode: TODO - Week 2 implementation

    Args:
        prompt: User prompt to execute
        config_path: Path to user config file (optional)
        org_policy_path: Path to organization policy file (optional)
        dry_run: If True, only initialize and validate (don't execute)
        envelope: Cortex envelope dict (optional)

    Returns:
        Dict with execution results or initialization status
    """
    # Step 1: Load configuration
    config_path_obj = Path(config_path) if config_path else None
    org_policy_path_obj = Path(org_policy_path) if org_policy_path else None

    config_manager = ConfigManager(
        config_path=config_path_obj,
        org_policy_path=org_policy_path_obj
    )

    # Extract config values
    approval_mode = config_manager.get("security.approval_mode")
    audit_log_path = Path(config_manager.get("security.audit_log_path"))
    audit_log_rotation = config_manager.get("security.audit_log_rotation")
    audit_log_retention = config_manager.get("security.audit_log_retention")
    cache_dir = Path(config_manager.get("security.cache_dir"))
    sanitize_enabled = config_manager.get("security.sanitize_conversation_history")
    confidence_threshold = config_manager.get("security.tool_prediction_confidence_threshold")
    allowed_envelopes = config_manager.get("security.allowed_envelopes")

    # Step 2: Initialize security components
    audit_logger = AuditLogger(
        log_path=audit_log_path,
        rotation_size=audit_log_rotation,
        retention_days=audit_log_retention
    )

    cache_manager = CacheManager(cache_dir=cache_dir)

    prompt_sanitizer = PromptSanitizer()

    approval_handler = ApprovalHandler(confidence_threshold=confidence_threshold)

    # Step 3: Sanitize prompt if enabled
    sanitized_prompt = prompt
    if sanitize_enabled:
        sanitized_prompt = prompt_sanitizer.sanitize(prompt)

    # Step 4: Determine approval mode
    # In prompt mode, user must approve tools
    # In auto mode, tools are auto-approved
    # In deny mode, execution is blocked

    # Step 5: Dry-run mode - return initialization status
    if dry_run:
        return {
            "status": "initialized",
            "dry_run": True,
            "prompt": prompt,
            "sanitized_prompt": sanitized_prompt,
            "config": {
                "approval_mode": approval_mode,
                "audit_log_path": str(audit_log_path),
                "cache_dir": str(cache_dir),
                "sanitize_enabled": sanitize_enabled,
                "confidence_threshold": confidence_threshold,
                "allowed_envelopes": allowed_envelopes
            },
            "audit_logger": str(type(audit_logger).__name__),
            "cache_manager": str(type(cache_manager).__name__),
            "prompt_sanitizer": str(type(prompt_sanitizer).__name__),
            "approval_handler": str(type(approval_handler).__name__)
        }

    # Step 6: Full execution flow (TODO: Week 2)
    # This will include:
    # - Tool prediction with approval handler
    # - User approval flow (if prompt mode)
    # - Cortex execution
    # - Result caching
    # - Audit logging
    # - Error handling

    return {
        "status": "not_implemented",
        "message": "Full execution flow is TODO for Week 2"
    }


def main():
    """CLI entry point for security wrapper."""
    parser = argparse.ArgumentParser(
        description="Security wrapper for cortex-code skill"
    )
    parser.add_argument(
        "--prompt",
        required=True,
        help="User prompt to execute"
    )
    parser.add_argument(
        "--config",
        help="Path to user config file"
    )
    parser.add_argument(
        "--org-policy",
        help="Path to organization policy file"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry-run mode: initialize and validate only"
    )
    parser.add_argument(
        "--envelope",
        help="Cortex envelope JSON string"
    )

    args = parser.parse_args()

    # Parse envelope if provided
    envelope = None
    if args.envelope:
        try:
            envelope = json.loads(args.envelope)
        except json.JSONDecodeError as e:
            print(json.dumps({
                "status": "error",
                "message": f"Invalid envelope JSON: {e}"
            }))
            sys.exit(1)

    # Execute with security
    try:
        result = execute_with_security(
            prompt=args.prompt,
            config_path=args.config,
            org_policy_path=args.org_policy,
            dry_run=args.dry_run,
            envelope=envelope
        )
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(json.dumps({
            "status": "error",
            "message": str(e)
        }))
        sys.exit(1)


if __name__ == "__main__":
    main()
