# JBoss Migration Analyzer

A thin, rule-based scanner that detects JBoss EAP patterns in your codebase and
reports them as structured findings for migration to Spring Boot embedded Tomcat.

## Quick Start

```bash
# Scan a project directory (text output)
python analyzer/jboss_migration_analyzer.py /path/to/project

# JSON output
python analyzer/jboss_migration_analyzer.py /path/to/project --format json

# All formats (text + JSON + summary)
python analyzer/jboss_migration_analyzer.py /path/to/project --format all

# Scan a single file
python analyzer/jboss_migration_analyzer.py current-dc.yaml --single-file
```

## How It Works

The analyzer loads regex patterns from `rules.yaml` and applies them against
file names and file contents. It emits structured findings with:

- **rule_id** — unique identifier (e.g., `JBOSS-TLS-001`)
- **category** — `tls_ssl`, `jndi`, `deployment_descriptors`, `classloading`,
  `logging`, or `configuration`
- **severity** — `critical`, `high`, `medium`, `low`, or `info`
- **file** / **line** — exact location
- **snippet** — the matched line (truncated to 200 chars)

## Rules

Rules live in `rules.yaml`. Each rule has:

| Field          | Description |
|----------------|-------------|
| `id`           | Unique identifier |
| `category`     | Grouping for the finding |
| `severity`     | Impact level |
| `description`  | Human-readable explanation |
| `file_pattern` | Glob restricting which files to check (optional) |
| `pattern`      | Regex applied to file contents |
| `name_pattern` | Regex applied to file names/paths |

Add new rules by editing `rules.yaml` — no Python changes needed.

## MCP Server Mode (Copilot Integration)

The analyzer can run as a [Model Context Protocol](https://modelcontextprotocol.io/)
stdio server, allowing GitHub Copilot in VS Code to call it as a tool:

```bash
python analyzer/jboss_migration_analyzer.py --mcp-mode
```

This is configured automatically via `.vscode/mcp.json`. The MCP server exposes:

| Tool                       | Description |
|----------------------------|-------------|
| `scan_project(path)`       | Scan a directory tree for migration issues |
| `scan_file(path)`          | Scan a single file |
| `list_rules()`             | List all loaded detection rules |
| `check_deployment_config(path)` | Scan a deployment YAML for JBoss vestiges |

## Copilot Prompt Files

Reusable prompt recipes are in `.github/prompts/`:

| Prompt | Use |
|--------|-----|
| `migration-scan.prompt.md` | Full project scan with prioritized checklist |
| `tls-migration.prompt.md` | TLS/SSL keystore → PEM migration analysis |
| `deployment-config-review.prompt.md` | OpenShift YAML review for JBoss vestiges |
| `deep-analysis.prompt.md` | AI-powered gap detection beyond regex rules |

Invoke in Copilot Chat: type `#prompt:migration-scan` (or use the command palette).

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    Copilot Chat                          │
│  ┌────────────────────────────────────────────────────┐  │
│  │  copilot-instructions.md  →  AI reasoning layer   │  │
│  │  prompt files             →  repeatable workflows  │  │
│  └─────────────────┬──────────────────────────────────┘  │
│                    │ MCP tool calls                       │
│  ┌─────────────────▼──────────────────────────────────┐  │
│  │  jboss_migration_analyzer.py  (MCP server)         │  │
│  │  └── rules.yaml (deterministic pattern matching)   │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

**Layer 1** (analyzer + rules) handles repeatable pattern matching.
**Layer 2** (MCP server) lets Copilot call the analyzer mid-conversation.
**Layer 3** (instructions) tells Copilot how to interpret and extend results.
**Layer 4** (prompts) provides reusable migration workflows.
**Layer 5** (Copilot AI) fills gaps the rules can't cover.
