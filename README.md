# Config Validator AI MCP Server

> By [MEOK AI Labs](https://meok.ai) — Validate TOML, INI, and .env configuration files with fix suggestions

## Installation

```bash
pip install config-validator-ai-mcp
```

## Usage

```bash
python server.py
```

## Tools

### `validate_toml`
Validate TOML configuration file syntax and structure.

**Parameters:**
- `content` (str): TOML file content

### `validate_ini`
Validate INI configuration file syntax with section and key extraction.

**Parameters:**
- `content` (str): INI file content

### `validate_dotenv`
Validate .env file format and detect issues (invalid names, duplicates, exposed secrets).

**Parameters:**
- `content` (str): .env file content

### `suggest_fixes`
Suggest fixes for common configuration file issues with auto-fix support.

**Parameters:**
- `content` (str): Configuration file content
- `config_type` (str): File type — 'toml', 'ini', 'dotenv', 'auto'

## Authentication

Free tier: 50 calls/day. Upgrade at [meok.ai/pricing](https://meok.ai/pricing) for unlimited access.

## License

MIT — MEOK AI Labs
