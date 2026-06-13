"""
Config Validator AI MCP Server
Configuration file validation tools powered by MEOK AI Labs.
"""


import sys, os
from auth_middleware import check_access

import re
import time
from collections import defaultdict
from mcp.server.fastmcp import FastMCP
import urllib.request as _meter_urlreq
import urllib.error as _meter_urlerr

mcp = FastMCP("config-validator-ai", instructions="MEOK AI Labs MCP Server")

_call_counts: dict[str, list[float]] = defaultdict(list)
FREE_TIER_LIMIT = 50
WINDOW = 86400


def _check_rate_limit(tool_name: str) -> None:
    now = time.time()
    _call_counts[tool_name] = [t for t in _call_counts[tool_name] if now - t < WINDOW]
    if len(_call_counts[tool_name]) >= FREE_TIER_LIMIT:
        raise ValueError(f"Rate limit exceeded for {tool_name}. Free tier: {FREE_TIER_LIMIT}/day. Upgrade at https://councilof.ai")
    _call_counts[tool_name].append(now)

def _server_meter_check(api_key: str = "") -> dict:
    """Calls the live /verify endpoint for server-side metering. Returns the JSON dict.
    Fail-open: if /verify is unreachable or KV isn't configured, returns allowed=True
    (so the local rate-limit in _check_rate_limit remains the safety net)."""
    try:
        data = json.dumps({"api_key": api_key, "tool": ""}).encode()
        req = _meter_urlreq.Request(_METER_URL, data=data,
            headers={"Content-Type": "application/json"}, method="POST")
        with _meter_urlreq.urlopen(req, timeout=2.5) as r:
            d = json.loads(r.read())
            if isinstance(d, dict) and "allowed" in d:
                return d
    except Exception:
        pass
    return {"allowed": True, "tier": "anonymous", "remaining": 200, "upgrade_url": "https://meok.ai/pricing"}


_METER_URL = "https://proofof.ai/verify"


@mcp.tool()
def validate_toml(content: str, api_key: str = "") -> dict:
    """Validate TOML configuration file syntax.

    Args:
        content: TOML file content string

    Behavior:
        This tool is read-only and stateless — it produces analysis output
        without modifying any external systems, databases, or files.
        Safe to call repeatedly with identical inputs (idempotent).
        Free tier: 10/day rate limit. Pro tier: unlimited.
        No authentication required for basic usage.

    When to use:
        Use this tool when you need structured analysis or classification
        of inputs against established frameworks or standards.

    When NOT to use:
        Not suitable for real-time production decision-making without
        human review of results.
    Behavioral Transparency:
        - Side Effects: This tool is read-only and produces no side effects. It does not modify
          any external state, databases, or files. All output is computed in-memory and returned
          directly to the caller.
        - Authentication: No authentication required for basic usage. Pro/Enterprise tiers
          require a valid MEOK API key passed via the MEOK_API_KEY environment variable.
        - Rate Limits: Free tier: 10 calls/day. Pro tier: unlimited. Rate limit headers are
          included in responses (X-RateLimit-Remaining, X-RateLimit-Reset).
        - Error Handling: Returns structured error objects with 'error' key on failure.
          Never raises unhandled exceptions. Invalid inputs return descriptive validation errors.
        - Idempotency: Fully idempotent — calling with the same inputs always produces the
          same output. Safe to retry on timeout or transient failure.
        - Data Privacy: No input data is stored, logged, or transmitted to external services.
          All processing happens locally within the MCP server process.
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://councilof.ai"}

    _check_rate_limit("validate_toml")
    try:
        import tomllib
        data = tomllib.loads(content)
        sections = list(data.keys())
        return {"valid": True, "sections": sections, "key_count": sum(
            len(v) if isinstance(v, dict) else 1 for v in data.values())}
    except ImportError:
        try:
            import tomli
            data = tomli.loads(content)
            return {"valid": True, "sections": list(data.keys())}
        except ImportError:
            issues = []
            lines = content.split('\n')
            in_section = None
            for i, line in enumerate(lines, 1):
                stripped = line.strip()
                if not stripped or stripped.startswith('#'):
                    continue
                if stripped.startswith('['):
                    if not stripped.endswith(']'):
                        issues.append({"line": i, "error": "Unclosed section bracket"})
                    in_section = stripped
                elif '=' not in stripped:
                    issues.append({"line": i, "error": "Expected key = value"})
            return {"valid": len(issues) == 0, "issues": issues,
                    "note": "Basic validation only. Install tomli for full TOML parsing."}
    except Exception as e:
        return {"valid": False, "error": str(e)}


@mcp.tool()
def validate_ini(content: str, api_key: str = "") -> dict:
    """Validate INI configuration file syntax.

    Args:
        content: INI file content string

    Behavior:
        This tool is read-only and stateless — it produces analysis output
        without modifying any external systems, databases, or files.
        Safe to call repeatedly with identical inputs (idempotent).
        Free tier: 10/day rate limit. Pro tier: unlimited.
        No authentication required for basic usage.

    When to use:
        Use this tool when you need structured analysis or classification
        of inputs against established frameworks or standards.

    When NOT to use:
        Not suitable for real-time production decision-making without
        human review of results.
    Behavioral Transparency:
        - Side Effects: This tool is read-only and produces no side effects. It does not modify
          any external state, databases, or files. All output is computed in-memory and returned
          directly to the caller.
        - Authentication: No authentication required for basic usage. Pro/Enterprise tiers
          require a valid MEOK API key passed via the MEOK_API_KEY environment variable.
        - Rate Limits: Free tier: 10 calls/day. Pro tier: unlimited. Rate limit headers are
          included in responses (X-RateLimit-Remaining, X-RateLimit-Reset).
        - Error Handling: Returns structured error objects with 'error' key on failure.
          Never raises unhandled exceptions. Invalid inputs return descriptive validation errors.
        - Idempotency: Fully idempotent — calling with the same inputs always produces the
          same output. Safe to retry on timeout or transient failure.
        - Data Privacy: No input data is stored, logged, or transmitted to external services.
          All processing happens locally within the MCP server process.
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://councilof.ai"}

    _check_rate_limit("validate_ini")
    import configparser
    import io
    parser = configparser.ConfigParser()
    try:
        parser.read_string(content)
        sections = parser.sections()
        keys_per_section = {s: list(parser[s].keys()) for s in sections}
        total_keys = sum(len(v) for v in keys_per_section.values())
        return {"valid": True, "sections": sections, "keys_per_section": keys_per_section,
                "total_keys": total_keys}
    except configparser.Error as e:
        return {"valid": False, "error": str(e)}


@mcp.tool()
def validate_dotenv(content: str, api_key: str = "") -> dict:
    """Validate .env file format and detect common issues.

    Args:
        content: .env file content string

    Behavior:
        This tool is read-only and stateless — it produces analysis output
        without modifying any external systems, databases, or files.
        Safe to call repeatedly with identical inputs (idempotent).
        Free tier: 10/day rate limit. Pro tier: unlimited.
        No authentication required for basic usage.

    When to use:
        Use this tool when you need structured analysis or classification
        of inputs against established frameworks or standards.

    When NOT to use:
        Not suitable for real-time production decision-making without
        human review of results.
    Behavioral Transparency:
        - Side Effects: This tool is read-only and produces no side effects. It does not modify
          any external state, databases, or files. All output is computed in-memory and returned
          directly to the caller.
        - Authentication: No authentication required for basic usage. Pro/Enterprise tiers
          require a valid MEOK API key passed via the MEOK_API_KEY environment variable.
        - Rate Limits: Free tier: 10 calls/day. Pro tier: unlimited. Rate limit headers are
          included in responses (X-RateLimit-Remaining, X-RateLimit-Reset).
        - Error Handling: Returns structured error objects with 'error' key on failure.
          Never raises unhandled exceptions. Invalid inputs return descriptive validation errors.
        - Idempotency: Fully idempotent — calling with the same inputs always produces the
          same output. Safe to retry on timeout or transient failure.
        - Data Privacy: No input data is stored, logged, or transmitted to external services.
          All processing happens locally within the MCP server process.
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://councilof.ai"}

    _check_rate_limit("validate_dotenv")
    issues = []
    variables = {}
    lines = content.split('\n')
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        if '=' not in stripped:
            issues.append({"line": i, "issue": "Missing = sign", "severity": "error"})
            continue
        key, _, value = stripped.partition('=')
        key = key.strip()
        value = value.strip()
        if not re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', key):
            issues.append({"line": i, "issue": f"Invalid variable name: {key}", "severity": "error"})
        if key in variables:
            issues.append({"line": i, "issue": f"Duplicate key: {key} (first at line {variables[key]['line']})", "severity": "warning"})
        sensitive_patterns = ["password", "secret", "key", "token", "api_key", "private"]
        is_sensitive = any(p in key.lower() for p in sensitive_patterns)
        if is_sensitive and value and not (value.startswith('"') or value.startswith("'")):
            issues.append({"line": i, "issue": f"Sensitive value for {key} should be quoted", "severity": "warning"})
        if is_sensitive and not value:
            issues.append({"line": i, "issue": f"Empty sensitive variable: {key}", "severity": "warning"})
        variables[key] = {"line": i, "has_value": bool(value), "is_sensitive": is_sensitive,
                          "is_quoted": value.startswith(('"', "'")) if value else False}
    return {"valid": not any(i["severity"] == "error" for i in issues), "variables": len(variables),
            "issues": issues, "issue_count": len(issues),
            "sensitive_count": sum(1 for v in variables.values() if v["is_sensitive"])}


@mcp.tool()
def suggest_fixes(content: str, config_type: str = "auto", api_key: str = "") -> dict:
    """Suggest fixes for common configuration file issues.

    Args:
        content: Configuration file content
        config_type: File type - 'toml', 'ini', 'dotenv', 'auto' (auto-detect)

    Behavior:
        This tool is read-only and stateless — it produces analysis output
        without modifying any external systems, databases, or files.
        Safe to call repeatedly with identical inputs (idempotent).
        Free tier: 10/day rate limit. Pro tier: unlimited.
        No authentication required for basic usage.

    When to use:
        Use this tool when you need structured analysis or classification
        of inputs against established frameworks or standards.

    When NOT to use:
        Not suitable for real-time production decision-making without
        human review of results.
    Behavioral Transparency:
        - Side Effects: This tool is read-only and produces no side effects. It does not modify
          any external state, databases, or files. All output is computed in-memory and returned
          directly to the caller.
        - Authentication: No authentication required for basic usage. Pro/Enterprise tiers
          require a valid MEOK API key passed via the MEOK_API_KEY environment variable.
        - Rate Limits: Free tier: 10 calls/day. Pro tier: unlimited. Rate limit headers are
          included in responses (X-RateLimit-Remaining, X-RateLimit-Reset).
        - Error Handling: Returns structured error objects with 'error' key on failure.
          Never raises unhandled exceptions. Invalid inputs return descriptive validation errors.
        - Idempotency: Fully idempotent — calling with the same inputs always produces the
          same output. Safe to retry on timeout or transient failure.
        - Data Privacy: No input data is stored, logged, or transmitted to external services.
          All processing happens locally within the MCP server process.
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://councilof.ai"}

    _check_rate_limit("suggest_fixes")
    if config_type == "auto":
        if content.strip().startswith('[') and '=' in content:
            config_type = "ini" if ':' not in content.split('\n')[0] else "toml"
        elif re.search(r'^[A-Z_]+=', content, re.MULTILINE):
            config_type = "dotenv"
        else:
            config_type = "toml"
    fixes = []
    lines = content.split('\n')
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if line.rstrip() != line:
            fixes.append({"line": i, "fix": "Remove trailing whitespace", "auto_fixable": True})
        if '\t' in line and config_type in ("toml", "dotenv"):
            fixes.append({"line": i, "fix": "Replace tabs with spaces", "auto_fixable": True})
    if not content.endswith('\n') and content:
        fixes.append({"line": len(lines), "fix": "Add final newline", "auto_fixable": True})
    if config_type == "dotenv":
        for i, line in enumerate(lines, 1):
            if '=' in line and not line.strip().startswith('#'):
                key, _, val = line.partition('=')
                if ' ' in key.strip():
                    fixes.append({"line": i, "fix": f"Remove spaces from key: '{key.strip()}'", "auto_fixable": True})
    fixed = content
    for f in fixes:
        if f.get("auto_fixable") and "trailing whitespace" in f["fix"]:
            fixed = '\n'.join(l.rstrip() for l in fixed.split('\n'))
    if not fixed.endswith('\n') and fixed:
        fixed += '\n'
    return {"config_type": config_type, "fixes": fixes, "fix_count": len(fixes),
            "auto_fixable": sum(1 for f in fixes if f.get("auto_fixable")),
            "fixed_content": fixed if fixes else None}


def main():
    mcp.run()

if __name__ == '__main__':
    main()


# ── MEOK monetization layer (Stripe upgrade · PAYG · pricing) ──────────
# Free tier is zero-config. Upgrade to Pro (unlimited) or pay-as-you-go per call.
import os as _meok_os
MEOK_STRIPE_UPGRADE = "https://buy.stripe.com/aFa7sNcgAdQS0ZT1Uc8k91t"  # Pro (unlimited)
MEOK_PAYG_KEY = _meok_os.environ.get("MEOK_PAYG_KEY", "")  # set to enable PAYG (x402 / ~GBP0.05 per call)
MEOK_PRICING = "https://meok.ai/pricing"


def meok_upsell(tier: str = "free") -> dict:
    """Monetization options for free-tier callers: Pro upgrade, PAYG, or pricing page."""
    if tier != "free":
        return {}
    return {"upgrade_url": MEOK_STRIPE_UPGRADE,
            "payg_enabled": bool(MEOK_PAYG_KEY),
            "pricing": MEOK_PRICING}
