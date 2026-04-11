# Cortexcode Tool

A standalone CLI tool that brings Cortex Code's Snowflake expertise to VSCode and terminal environments.

> **Note**: For Claude Code and Cursor coding agents, use the skill-based integrations in `integrations/claude-code/` or `integrations/cursor/` instead for better integration.

## Overview

**cortexcode-tool** enables AI-powered Snowflake operations from VSCode or terminal by:
- Intelligently routing Snowflake queries to Cortex Code CLI
- Providing enterprise-grade security (approval modes, audit logging, PII sanitization)
- Dynamically discovering Cortex capabilities
- Generating IDE-specific integration files

## Supported Environments

- **VSCode**: Task runner + code snippets via `.vscode/` config
- **Terminal**: Standalone CLI for any environment

## Quick Start

### Prerequisites

- Python 3.8+
- [Cortex Code CLI](https://docs.snowflake.com/en/user-guide/cortex-code/cortex-code-cli) v1.0.42+
- Snowflake connection configured

### Installation

```bash
# Clone repository
git clone https://github.com/Snowflake-Labs/subagent-cortex-code.git
cd subagent-cortex-code/integrations/cli-tool

# Run installation
./setup.sh

# Verify installation
cortexcode-tool --version
```

### Usage

```bash
# Query Snowflake
cortexcode-tool "Show me top 10 customers by revenue"

# Generate IDE integration files
cortexcode-tool --generate-ide-config

# Force capability rediscovery
cortexcode-tool --discover-capabilities
```

## Features

### Security (v2.0.0 Compatible)

- **Three approval modes**: prompt (default), auto, envelope_only
- **Prompt sanitization**: Automatic PII removal and injection detection
- **Credential blocking**: Prevents routing sensitive file paths
- **Audit logging**: Structured JSONL logs for compliance
- **Organization policy**: Enterprise override support

### Multi-IDE Integration

- **Adapter pattern**: Clean separation between core and IDE-specific code
- **Dynamic generation**: Creates IDE config files from discovered capabilities
- **Configurable**: Choose which IDEs to support via config.yaml

### Dynamic Discovery

- Discovers 35+ Cortex bundled skills automatically
- Caches capabilities with SHA256 validation
- Generates IDE rules based on discovered triggers

## Configuration

Create `~/.config/cortexcode-tool/config.yaml`:

```yaml
security:
  approval_mode: "prompt"  # prompt | auto | envelope_only

ide:
  targets:
    - "cursor"
    - "vscode"

cortex:
  connection_name: "default"
  default_envelope: "RW"
```

See `config.yaml.example` for full configuration options.

## Documentation

- [Design Specification](docs/2026-04-02-cortexcode-tool-design.md) - Complete architecture and design
- [User Guide](docs/USER_GUIDE.md) - Detailed usage instructions (coming soon)
- [IDE Integration](docs/IDE_INTEGRATION.md) - IDE-specific setup guides (coming soon)
- [Security](docs/SECURITY.md) - Security features and best practices (coming soon)

## Project Structure

```
cortexcode-tool/
├── cortexcode_tool/          # Main Python package
│   ├── security/             # Security components (from cortex-code v2.0.0)
│   ├── core/                 # Routing, execution, discovery
│   └── ide_adapters/         # Multi-IDE integration
├── tests/                    # Test suite
├── docs/                     # Documentation
├── setup.sh                  # Installation script
└── config.yaml.example       # Configuration template
```

## Development

### Setup Development Environment

```bash
# Clone repo
git clone https://github.com/Snowflake-Labs/subagent-cortex-code.git
cd subagent-cortex-code/integrations/cli-tool

# Create virtual environment (optional)
python3 -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e .
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=cortexcode_tool --cov-report=html tests/
```

## Architecture

**Core Principle**: Universal CLI with IDE-specific adapters

- **Core CLI**: Works from any terminal (IDE-agnostic)
- **Security Layer**: cortex-code v2.0.0 security components
- **IDE Adapters**: Generate integration files per IDE
- **Dynamic Discovery**: Auto-discover Cortex capabilities

See [Design Specification](docs/2026-04-02-cortexcode-tool-design.md) for detailed architecture.

## Contributing

Contributions welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

Apache 2.0

## Links

- **GitHub**: https://github.com/Snowflake-Labs/subagent-cortex-code
- **Cortex Code**: https://docs.snowflake.com/en/user-guide/cortex-code

## Version

**Current**: v0.1.0 (Development)  
**Status**: Pre-release

Based on cortex-code skill v2.0.0 security architecture.

---

**Copyright © 2026 Snowflake Inc. All rights reserved.**
