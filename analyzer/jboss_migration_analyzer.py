#!/usr/bin/env python3
"""JBoss Migration Analyzer — thin, rule-based scanner with MCP server mode.

Scans a project directory for JBoss-to-Spring-Boot migration issues using
regex patterns loaded from rules.yaml.  Emits structured JSON output.

Usage (CLI):
    python jboss_migration_analyzer.py <directory> [--format json|text|all]
    python jboss_migration_analyzer.py <file> --single-file [--format json|text|all]

Usage (MCP server):
    python jboss_migration_analyzer.py --mcp-mode
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

import yaml  # PyYAML — available in the devcontainer Python feature

# ── Constants ────────────────────────────────────────────────────────────

RULES_PATH = Path(__file__).parent / "rules.yaml"
# File extensions worth scanning (skip binaries/images/etc.)
TEXT_EXTENSIONS = {
    ".java", ".xml", ".yaml", ".yml", ".properties", ".json",
    ".sh", ".bat", ".cmd", ".env", ".cfg", ".conf", ".txt",
    ".gradle", ".kts", ".groovy", ".md",
}
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2 MB — skip very large files

# ── Rule Loading ─────────────────────────────────────────────────────────


def _expand_brace_glob(pattern: str) -> list[str]:
    """Expand a brace glob pattern into multiple fnmatch patterns.

    Example: "*.{yaml,yml,xml}" → ["*.yaml", "*.yml", "*.xml"]
    """
    import re as _re
    m = _re.search(r"\{([^}]+)\}", pattern)
    if not m:
        return [pattern]
    prefix = pattern[: m.start()]
    suffix = pattern[m.end() :]
    return [f"{prefix}{alt.strip()}{suffix}" for alt in m.group(1).split(",") if alt.strip()]


def load_rules(path: Path = RULES_PATH) -> list[dict[str, Any]]:
    """Load migration rules from YAML and pre-compile regexes."""
    with open(path, encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    rules = data.get("rules", [])
    for rule in rules:
        if "pattern" in rule:
            rule["_compiled"] = re.compile(rule["pattern"])
        if "name_pattern" in rule:
            rule["_name_compiled"] = re.compile(rule["name_pattern"])
        # Expand file_pattern brace globs into a list for fnmatch
        # e.g. "*.{yaml,yml,xml}" → ["*.yaml", "*.yml", "*.xml"]
        fp = rule.get("file_pattern", "*")
        rule["_file_globs"] = _expand_brace_glob(fp)
    return rules


# ── Scanning ─────────────────────────────────────────────────────────────


def _should_scan(filepath: Path) -> bool:
    """Return True if the file is a scannable text file."""
    if filepath.suffix.lower() not in TEXT_EXTENSIONS:
        return False
    try:
        if filepath.stat().st_size > MAX_FILE_SIZE:
            return False
    except OSError:
        return False
    return True


def _matches_file_glob(filename: str, globs: list[str]) -> bool:
    """Check if a filename matches any of the given glob patterns."""
    return any(fnmatch.fnmatch(filename, g) for g in globs)


def scan_file(filepath: Path, rules: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Scan a single file and return findings."""
    findings: list[dict[str, Any]] = []
    rel_path = str(filepath)
    filename = filepath.name

    # Name-pattern rules (match against file path, no need to read contents)
    for rule in rules:
        compiled = rule.get("_name_compiled")
        if compiled and compiled.search(rel_path):
            findings.append({
                "rule_id": rule["id"],
                "category": rule["category"],
                "severity": rule["severity"],
                "description": rule["description"],
                "file": rel_path,
                "line": 0,
                "snippet": f"(file name match: {filename})",
            })

    # Content-pattern rules
    content_rules = [r for r in rules if "_compiled" in r]
    if not content_rules or not _should_scan(filepath):
        return findings

    try:
        lines = filepath.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return findings

    for line_num, line_text in enumerate(lines, start=1):
        for rule in content_rules:
            if not _matches_file_glob(filename, rule["_file_globs"]):
                continue
            match = rule["_compiled"].search(line_text)
            if match:
                findings.append({
                    "rule_id": rule["id"],
                    "category": rule["category"],
                    "severity": rule["severity"],
                    "description": rule["description"],
                    "file": rel_path,
                    "line": line_num,
                    "snippet": line_text.strip()[:200],
                })

    return findings


def scan_project(root: str | Path, rules: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Walk a directory tree and scan all text files."""
    root = Path(root)
    findings: list[dict[str, Any]] = []
    for dirpath, dirnames, filenames in os.walk(root):
        # Skip hidden dirs and common non-source dirs
        dirnames[:] = [
            d for d in dirnames
            if not d.startswith(".")
            and d not in {
                "node_modules", "target", "build", "__pycache__", ".git",
                "dist", "out", "bin", ".gradle", ".mvn", "vendor",
            }
        ]
        for fname in filenames:
            fpath = Path(dirpath) / fname
            findings.extend(scan_file(fpath, rules))
    return findings


def check_deployment_config(filepath: str | Path, rules: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Scan a single deployment YAML for JBoss vestiges."""
    return scan_file(Path(filepath), rules)


# ── Output Formatting ────────────────────────────────────────────────────

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}


def _sort_findings(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(findings, key=lambda f: SEVERITY_ORDER.get(f["severity"], 99))


def format_json(findings: list[dict[str, Any]]) -> str:
    return json.dumps({"total": len(findings), "findings": _sort_findings(findings)}, indent=2)


def format_text(findings: list[dict[str, Any]]) -> str:
    if not findings:
        return "No JBoss migration issues found."
    lines = [f"Found {len(findings)} migration issue(s):\n"]
    for f in _sort_findings(findings):
        loc = f"{f['file']}:{f['line']}" if f["line"] else f["file"]
        lines.append(f"  [{f['severity'].upper():8s}] {f['rule_id']:16s} {loc}")
        lines.append(f"             {f['description']}")
        if f.get("snippet") and not f["snippet"].startswith("(file name"):
            lines.append(f"             > {f['snippet']}")
        lines.append("")
    return "\n".join(lines)


def format_summary(findings: list[dict[str, Any]]) -> dict[str, Any]:
    """Produce a summary grouped by category and severity."""
    by_category: dict[str, list[dict[str, Any]]] = {}
    by_severity: dict[str, int] = {}
    for f in findings:
        by_category.setdefault(f["category"], []).append(f)
        by_severity[f["severity"]] = by_severity.get(f["severity"], 0) + 1
    return {
        "total": len(findings),
        "by_severity": by_severity,
        "by_category": {k: len(v) for k, v in by_category.items()},
    }


# ── MCP Server Mode ─────────────────────────────────────────────────────


def _mcp_response(req_id: Any, result: Any) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def _mcp_error(req_id: Any, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}


def run_mcp_server() -> None:
    """Run as a JSON-RPC stdio MCP server."""
    rules = load_rules()
    tool_defs = [
        {
            "name": "scan_project",
            "description": "Scan a project directory for JBoss migration issues. Returns structured findings sorted by severity.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Absolute or relative path to the project directory to scan"},
                },
                "required": ["path"],
            },
        },
        {
            "name": "scan_file",
            "description": "Scan a single file for JBoss migration issues.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to the file to scan"},
                },
                "required": ["path"],
            },
        },
        {
            "name": "list_rules",
            "description": "List all migration detection rules with their IDs, categories, severities, and descriptions.",
            "inputSchema": {"type": "object", "properties": {}},
        },
        {
            "name": "check_deployment_config",
            "description": "Scan an OpenShift/Kubernetes deployment YAML for JBoss vestiges (legacy paths, keystore refs, EAP flags).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to the deployment YAML file"},
                },
                "required": ["path"],
            },
        },
    ]

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue

        req_id = msg.get("id")
        method = msg.get("method", "")
        params = msg.get("params", {})

        if method == "initialize":
            resp = _mcp_response(req_id, {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "jboss-migration-analyzer", "version": "1.0.0"},
            })
        elif method == "notifications/initialized":
            continue  # no response needed for notifications
        elif method == "tools/list":
            resp = _mcp_response(req_id, {"tools": tool_defs})
        elif method == "tools/call":
            tool_name = params.get("name", "")
            tool_args = params.get("arguments", {})
            try:
                if tool_name == "scan_project":
                    target = tool_args.get("path", ".")
                    findings = scan_project(target, rules)
                    result_text = format_json(findings)
                elif tool_name == "scan_file":
                    target = tool_args.get("path", "")
                    findings = scan_file(Path(target), rules)
                    result_text = format_json(findings)
                elif tool_name == "list_rules":
                    rule_list = [
                        {"id": r["id"], "category": r["category"], "severity": r["severity"], "description": r["description"]}
                        for r in rules
                    ]
                    result_text = json.dumps(rule_list, indent=2)
                elif tool_name == "check_deployment_config":
                    target = tool_args.get("path", "")
                    findings = check_deployment_config(target, rules)
                    result_text = format_json(findings)
                else:
                    resp = _mcp_error(req_id, -32601, f"Unknown tool: {tool_name}")
                    sys.stdout.write(json.dumps(resp) + "\n")
                    sys.stdout.flush()
                    continue
                resp = _mcp_response(req_id, {
                    "content": [{"type": "text", "text": result_text}],
                })
            except Exception as exc:
                resp = _mcp_error(req_id, -32000, str(exc))
        else:
            resp = _mcp_error(req_id, -32601, f"Method not found: {method}")

        sys.stdout.write(json.dumps(resp) + "\n")
        sys.stdout.flush()


# ── CLI Entry Point ──────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scan a project for JBoss-to-Spring-Boot migration issues."
    )
    parser.add_argument("path", nargs="?", default=".", help="Directory or file to scan")
    parser.add_argument("--format", choices=["json", "text", "all"], default="text",
                        help="Output format (default: text)")
    parser.add_argument("--single-file", action="store_true",
                        help="Scan a single file instead of a directory")
    parser.add_argument("--mcp-mode", action="store_true",
                        help="Run as an MCP stdio server for Copilot integration")
    args = parser.parse_args()

    if args.mcp_mode:
        run_mcp_server()
        return

    rules = load_rules()

    if args.single_file:
        findings = scan_file(Path(args.path), rules)
    else:
        findings = scan_project(args.path, rules)

    if args.format == "json":
        print(format_json(findings))
    elif args.format == "text":
        print(format_text(findings))
    else:  # "all"
        print(format_text(findings))
        print("\n--- JSON ---\n")
        print(format_json(findings))
        print("\n--- Summary ---\n")
        print(json.dumps(format_summary(findings), indent=2))


if __name__ == "__main__":
    main()
