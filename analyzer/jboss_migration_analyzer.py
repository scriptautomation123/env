#!/usr/bin/env python3
"""
jboss_migration_analyzer.py — JBoss → Spring Boot Embedded Tomcat Migration Analyzer

Scans a project directory for JBoss EAP artifacts, legacy configuration, and
source-code patterns that require refactoring to run as a Spring Boot
executable WAR on containers with embedded Tomcat.

Produces a structured JSON report and a human-readable summary.

Usage:
    python jboss_migration_analyzer.py <project_dir> [--output report.json] [--format json|text|all]

Example:
    python jboss_migration_analyzer.py /path/to/my-app --format all
"""

from __future__ import annotations

import argparse
import datetime
import fnmatch
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional

import yaml

# ── Constants ────────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_RULES_FILE = SCRIPT_DIR / "rules.yaml"

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
SEVERITY_COLOURS = {
    "critical": "\033[91m",  # red
    "high": "\033[93m",  # yellow
    "medium": "\033[33m",  # orange-ish
    "low": "\033[94m",  # blue
    "info": "\033[92m",  # green
}
RESET = "\033[0m"


# ── Data classes ─────────────────────────────────────────────────────────────


@dataclass
class Finding:
    """One detected issue."""

    rule_id: str
    name: str
    severity: str
    category: str
    description: str
    action: str
    matched_files: list[str] = field(default_factory=list)
    matched_lines: list[str] = field(default_factory=list)


@dataclass
class SpringBootInfo:
    """Detected Spring Boot metadata."""

    version: Optional[str] = None
    packaging: Optional[str] = None
    has_servlet_initializer: bool = False
    has_boot_maven_plugin: bool = False
    has_actuator: bool = False
    main_class: Optional[str] = None


@dataclass
class AnalysisReport:
    """Top-level analysis result."""

    project_dir: str
    analyzed_at: str
    total_files_scanned: int = 0
    spring_boot: SpringBootInfo = field(default_factory=SpringBootInfo)
    findings: list[Finding] = field(default_factory=list)
    summary: dict = field(default_factory=dict)


# ── Helpers ──────────────────────────────────────────────────────────────────


def load_rules(rules_path: Path) -> dict:
    """Load the YAML rules catalogue."""
    with open(rules_path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _glob_match(pattern: str, rel_path: str) -> bool:
    """Check whether *rel_path* matches the glob *pattern*."""
    # fnmatch doesn't handle ** natively; do a simple two-part check.
    if "**" in pattern:
        # Split on ** and check prefix/suffix.
        parts = pattern.split("**", 1)
        prefix = parts[0].rstrip("/")
        suffix = parts[1].lstrip("/")
        if prefix and not rel_path.startswith(prefix):
            return False
        return fnmatch.fnmatch(rel_path, f"*{suffix}") or fnmatch.fnmatch(
            os.path.basename(rel_path), suffix
        )
    return fnmatch.fnmatch(rel_path, pattern)


def _collect_files(project_dir: Path) -> list[Path]:
    """Walk *project_dir* and collect all regular files, skipping VCS dirs."""
    skip = {".git", ".svn", ".hg", "node_modules", "__pycache__", "target", "build"}
    result: list[Path] = []
    for root, dirs, files in os.walk(project_dir):
        dirs[:] = [d for d in dirs if d not in skip]
        for f in files:
            result.append(Path(root) / f)
    return result


def _read_text_safe(path: Path, max_bytes: int = 2 * 1024 * 1024) -> Optional[str]:
    """Read a text file, returning None for binary / unreadable files."""
    if path.stat().st_size > max_bytes:
        return None
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except (OSError, UnicodeDecodeError):
        return None


# ── Spring Boot metadata extraction ─────────────────────────────────────────


def _detect_spring_boot_version(pom_text: str) -> Optional[str]:
    """Try to extract the Spring Boot version from a pom.xml."""
    # Parent version
    m = re.search(
        r"<parent>.*?<artifactId>\s*spring-boot-starter-parent\s*</artifactId>"
        r".*?<version>\s*([^<]+?)\s*</version>",
        pom_text,
        re.DOTALL,
    )
    if m:
        return m.group(1).strip()
    # Property
    m = re.search(
        r"<spring-boot\.version>\s*([^<]+?)\s*</spring-boot\.version>", pom_text
    )
    if m:
        return m.group(1).strip()
    return None


def _detect_packaging(pom_text: str) -> Optional[str]:
    m = re.search(r"<packaging>\s*(\w+)\s*</packaging>", pom_text)
    return m.group(1).strip() if m else "jar"  # Maven default


def _enrich_spring_boot_info(
    info: SpringBootInfo, all_files: list[Path], project_dir: Path
) -> None:
    """Populate SpringBootInfo by scanning key files."""
    for fp in all_files:
        rel = str(fp.relative_to(project_dir))
        basename = fp.name

        # pom.xml
        if basename == "pom.xml":
            text = _read_text_safe(fp)
            if text:
                if info.version is None:
                    info.version = _detect_spring_boot_version(text)
                if info.packaging is None:
                    info.packaging = _detect_packaging(text)
                if "spring-boot-maven-plugin" in text:
                    info.has_boot_maven_plugin = True
                if "spring-boot-starter-actuator" in text:
                    info.has_actuator = True

        # build.gradle / build.gradle.kts
        if basename in ("build.gradle", "build.gradle.kts"):
            text = _read_text_safe(fp)
            if text:
                m = re.search(
                    r"org\.springframework\.boot['\"]?\s*version\s*['\"]?([^'\")\s]+)",
                    text,
                )
                if m and info.version is None:
                    info.version = m.group(1).strip()
                if "spring-boot-starter-actuator" in text:
                    info.has_actuator = True

        # Java sources
        if basename.endswith(".java"):
            text = _read_text_safe(fp)
            if text:
                if "extends SpringBootServletInitializer" in text:
                    info.has_servlet_initializer = True
                if "@SpringBootApplication" in text:
                    info.main_class = rel


# ── Rule evaluation engine ───────────────────────────────────────────────────


def _evaluate_file_glob_rule(
    rule: dict,
    all_files: list[Path],
    project_dir: Path,
) -> tuple[list[str], list[str]]:
    """Return (matched_files, matched_lines) for a single rule."""
    globs = rule.get("file_glob", [])
    contains = rule.get("file_contains")
    negate = rule.get("negate", False)

    if isinstance(contains, str):
        contains = [contains]

    matched_files: list[str] = []
    matched_lines: list[str] = []

    for fp in all_files:
        rel = str(fp.relative_to(project_dir))

        # Check glob
        glob_hit = any(_glob_match(g, rel) for g in globs)
        if not glob_hit:
            continue

        if contains is None:
            # Rule is purely a file-existence check
            if not negate:
                matched_files.append(rel)
            continue

        # File content check
        text = _read_text_safe(fp)
        if text is None:
            continue

        found_any = False
        for pattern in contains:
            for line_no, line in enumerate(text.splitlines(), 1):
                if re.search(pattern, line):
                    found_any = True
                    matched_lines.append(f"{rel}:{line_no}: {line.strip()}")

        if negate:
            if not found_any:
                matched_files.append(rel)
        else:
            if found_any:
                matched_files.append(rel)

    return matched_files, matched_lines


def _evaluate_pom_dependency_rule(
    rule: dict,
    all_files: list[Path],
    project_dir: Path,
) -> tuple[list[str], list[str]]:
    """Check for Maven dependencies matching groupId:artifactId patterns."""
    patterns = rule.get("pom_dependency", [])
    matched_files: list[str] = []
    matched_lines: list[str] = []

    for fp in all_files:
        if fp.name != "pom.xml":
            continue
        rel = str(fp.relative_to(project_dir))
        text = _read_text_safe(fp)
        if text is None:
            continue

        for pat in patterns:
            group_pat, art_pat = pat.split(":", 1)
            # Simple regex approach (handles namespaces loosely)
            dep_re = re.compile(
                r"<dependency>.*?"
                r"<groupId>\s*("
                + re.escape(group_pat).replace(r"\*", r"[^<]*")
                + r")\s*</groupId>.*?"
                r"<artifactId>\s*("
                + re.escape(art_pat).replace(r"\*", r"[^<]*")
                + r")\s*</artifactId>",
                re.DOTALL,
            )
            for m in dep_re.finditer(text):
                dep_str = f"{m.group(1)}:{m.group(2)}"
                matched_lines.append(f"{rel}: dependency {dep_str}")
                if rel not in matched_files:
                    matched_files.append(rel)

    return matched_files, matched_lines


def evaluate_rules(
    rules: dict,
    all_files: list[Path],
    project_dir: Path,
) -> list[Finding]:
    """Evaluate every rule category and return findings."""
    findings: list[Finding] = []

    for category, rule_list in rules.items():
        if not isinstance(rule_list, list):
            continue
        for rule in rule_list:
            # Choose evaluator
            if "pom_dependency" in rule:
                mf, ml = _evaluate_pom_dependency_rule(rule, all_files, project_dir)
            elif "file_glob" in rule:
                mf, ml = _evaluate_file_glob_rule(rule, all_files, project_dir)
            else:
                continue

            negate = rule.get("negate", False)

            # For negate rules that check file content, the rule fires if
            # *no* matching file contained the pattern.  We detect this as
            # mf being populated with glob-matching files that lacked the pattern.
            if negate and rule.get("file_contains") and not mf:
                # Negate rule didn't fire — all matching files contained the
                # pattern, so no finding.
                continue

            if mf or ml:
                findings.append(
                    Finding(
                        rule_id=rule["id"],
                        name=rule["name"],
                        severity=rule["severity"],
                        category=category,
                        description=rule.get("description", "").strip(),
                        action=rule.get("action", "").strip(),
                        matched_files=mf,
                        matched_lines=ml[:20],  # cap for readability
                    )
                )

    # Sort by severity
    findings.sort(key=lambda f: SEVERITY_ORDER.get(f.severity, 9))
    return findings


# ── Report builders ──────────────────────────────────────────────────────────


def _build_summary(findings: list[Finding]) -> dict:
    """Build a severity-count summary dict."""
    counts: dict[str, int] = {}
    for f in findings:
        counts[f.severity] = counts.get(f.severity, 0) + 1
    return {
        "total_findings": len(findings),
        "by_severity": counts,
        "migration_ready": counts.get("critical", 0) == 0
        and counts.get("high", 0) == 0,
    }


def build_report(
    project_dir: Path,
    rules: dict,
) -> AnalysisReport:
    """Run the full analysis and return a structured report."""
    all_files = _collect_files(project_dir)
    report = AnalysisReport(
        project_dir=str(project_dir),
        analyzed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        total_files_scanned=len(all_files),
    )

    # Enrich Spring Boot info
    _enrich_spring_boot_info(report.spring_boot, all_files, project_dir)

    # Evaluate rules
    report.findings = evaluate_rules(rules, all_files, project_dir)
    report.summary = _build_summary(report.findings)

    return report


# ── Output formatters ────────────────────────────────────────────────────────


def _sev_label(severity: str, colour: bool = True) -> str:
    if colour and sys.stdout.isatty():
        return f"{SEVERITY_COLOURS.get(severity, '')}{severity.upper()}{RESET}"
    return severity.upper()


def print_text_report(report: AnalysisReport) -> None:
    """Print a human-readable report to stdout."""
    colour = sys.stdout.isatty()
    hr = "=" * 72

    print(hr)
    print("  JBoss → Spring Boot Embedded Tomcat  ·  Migration Analysis Report")
    print(hr)
    print(f"  Project      : {report.project_dir}")
    print(f"  Analyzed at  : {report.analyzed_at}")
    print(f"  Files scanned: {report.total_files_scanned}")
    print()

    # Spring Boot info
    sb = report.spring_boot
    print("  ── Spring Boot Detection ──")
    print(f"  Version              : {sb.version or 'not detected'}")
    print(f"  Packaging            : {sb.packaging or 'not detected'}")
    print(f"  ServletInitializer   : {'yes' if sb.has_servlet_initializer else 'NO'}")
    print(f"  Boot Maven Plugin    : {'yes' if sb.has_boot_maven_plugin else 'NO'}")
    print(f"  Actuator             : {'yes' if sb.has_actuator else 'NO'}")
    print(f"  Main class           : {sb.main_class or 'not detected'}")
    print()

    # Summary
    s = report.summary
    print("  ── Summary ──")
    print(f"  Total findings       : {s['total_findings']}")
    for sev in ("critical", "high", "medium", "low", "info"):
        count = s.get("by_severity", {}).get(sev, 0)
        if count:
            print(f"    {_sev_label(sev, colour):>20s} : {count}")
    ready = s.get("migration_ready", False)
    status = (
        "✅  READY (no critical/high issues)"
        if ready
        else "❌  NOT READY (critical/high issues remain)"
    )
    print(f"  Migration readiness  : {status}")
    print()

    # Detailed findings
    if report.findings:
        print(hr)
        print("  ── Detailed Findings ──")
        print(hr)
        for i, f in enumerate(report.findings, 1):
            print()
            print(f"  [{i}] {_sev_label(f.severity, colour)}  {f.rule_id} — {f.name}")
            print(f"      Category   : {f.category}")
            print(f"      Description: {f.description}")
            if f.matched_files:
                print(f"      Files      : {', '.join(f.matched_files[:5])}")
                if len(f.matched_files) > 5:
                    print(f"                   … and {len(f.matched_files) - 5} more")
            if f.matched_lines:
                print("      Evidence   :")
                for line in f.matched_lines[:5]:
                    print(f"        → {line}")
                if len(f.matched_lines) > 5:
                    print(
                        f"        … and {len(f.matched_lines) - 5} more matches"
                    )
            print(f"      Action     : {f.action}")

    print()
    print(hr)
    print("  End of report")
    print(hr)


def write_json_report(report: AnalysisReport, output_path: Path) -> None:
    """Write the report as JSON."""
    data = asdict(report)
    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, default=str)
    print(f"JSON report written to {output_path}")


# ── CLI ──────────────────────────────────────────────────────────────────────


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze a project for JBoss → Spring Boot embedded Tomcat migration.",
    )
    parser.add_argument(
        "project_dir",
        type=Path,
        help="Path to the project directory to analyze.",
    )
    parser.add_argument(
        "--rules",
        type=Path,
        default=DEFAULT_RULES_FILE,
        help="Path to the YAML rules file (default: rules.yaml next to this script).",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        help="Path for JSON output file.",
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=["json", "text", "all"],
        default="text",
        help="Output format (default: text).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    project_dir = args.project_dir.resolve()
    if not project_dir.is_dir():
        print(f"Error: {project_dir} is not a directory.", file=sys.stderr)
        return 1

    rules_path = args.rules.resolve()
    if not rules_path.is_file():
        print(f"Error: rules file not found: {rules_path}", file=sys.stderr)
        return 1

    rules = load_rules(rules_path)
    report = build_report(project_dir, rules)

    fmt = args.format
    if fmt in ("text", "all"):
        print_text_report(report)

    if fmt in ("json", "all"):
        out = args.output or Path("migration-analysis.json")
        write_json_report(report, out)

    # Exit code reflects migration readiness
    return 0 if report.summary.get("migration_ready", False) else 2


if __name__ == "__main__":
    sys.exit(main())
