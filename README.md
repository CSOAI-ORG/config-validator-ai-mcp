<div align="center">

# Config Validator Ai MCP

**Config Validator AI MCP Server**

[![PyPI](https://img.shields.io/pypi/v/meok-config-validator-ai-mcp)](https://pypi.org/project/meok-config-validator-ai-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MEOK AI Labs](https://img.shields.io/badge/MEOK_AI_Labs-MCP_Server-purple)](https://meok.ai)

</div>

## Overview

Config Validator AI MCP Server
Configuration file validation tools powered by MEOK AI Labs.

## Tools

| Tool | Description |
|------|-------------|
| `validate_toml` | Validate TOML configuration file syntax. |
| `validate_ini` | Validate INI configuration file syntax. |
| `validate_dotenv` | Validate .env file format and detect common issues. |
| `suggest_fixes` | Suggest fixes for common configuration file issues. |

## Installation

```bash
pip install meok-config-validator-ai-mcp
```

## Usage with Claude Desktop

Add to your Claude Desktop MCP config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "config-validator-ai": {
      "command": "python",
      "args": ["-m", "meok_config_validator_ai_mcp.server"]
    }
  }
}
```

## Usage with FastMCP

```python
from mcp.server.fastmcp import FastMCP

# This server exposes 4 tool(s) via MCP
# See server.py for full implementation
```

## License

MIT © [MEOK AI Labs](https://meok.ai)
