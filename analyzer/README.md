# JBoss Migration Analyzer

> **Copilot-driven migration analysis via instructions + tools — not a monolithic analyzer.**

Treat GitHub Copilot as a migration analyst you equip with a runbook and tool
access. The deterministic work (file scanning, pattern matching) is handled by a
thin, rule-based Python scanner. The non-deterministic work (contextual judgment,
edge-case detection, risk triage) is delegated to Copilot through custom
instructions and reusable prompt files. Three Copilot mechanisms — **MCP tool
servers**, **custom instructions**, and **prompt files** — combine so both parts
are repeatable without writing a monolithic analysis engine.

---

## Quick Start

```bash
# Scan a project directory (human-readable text)
python analyzer/jboss_migration_analyzer.py /path/to/project

# JSON output (structured findings for CI pipelines or downstream tooling)
python analyzer/jboss_migration_analyzer.py /path/to/project --format json

# All formats (text + JSON + category/severity summary)
python analyzer/jboss_migration_analyzer.py /path/to/project --format all

# Scan a single file
python analyzer/jboss_migration_analyzer.py current-dc.yaml --single-file
```

**Prerequisites:** Python 3.10+ and PyYAML (`pip install pyyaml`). Both are
pre-installed in the devcontainer.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      Copilot Chat                            │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Layer 5 — AI reasoning (contextual judgment, triage)  │  │
│  │  Layer 4 — prompt files (repeatable workflows)         │  │
│  │  Layer 3 — copilot-instructions.md (migration runbook) │  │
│  └─────────────────────┬──────────────────────────────────┘  │
│                        │ MCP tool calls (JSON-RPC / stdio)   │
│  ┌─────────────────────▼──────────────────────────────────┐  │
│  │  Layer 2 — jboss_migration_analyzer.py  (MCP server)   │  │
│  │  Layer 1 — rules.yaml (deterministic pattern matching) │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

| Layer | Artifact | Type | Effort | Repeatability |
|-------|----------|------|--------|---------------|
| 1 | `analyzer/jboss_migration_analyzer.py` + `rules.yaml` | Code (thin, rule-based) | Medium (one-time) | 100 % deterministic |
| 2 | `.vscode/mcp.json` | Config | Low | Automatic |
| 3 | `.github/copilot-instructions.md` | Instructions | Low | Consistent AI behavior |
| 4 | `.github/prompts/*.prompt.md` | Prompt templates | Low | Reusable workflows |
| 5 | Copilot's AI reasoning | Zero code | Zero | Adaptive per project |

The key insight: **~200 lines of Python + ~5 config/markdown files**. Everything
else is Copilot applying its reasoning to structured scanner data. The scanner
handles "repeatable pattern matching"; the AI handles "this looks like a
JBoss-ism the rules didn't cover."

---

## Layer 1 — The Analyzer Script (Thin and Rule-Based)

`jboss_migration_analyzer.py` does **only** what regex can do reliably:

- Scan a project directory for known JBoss-isms (JNDI lookups, `jboss-web.xml`,
  `standalone.xml` references, EAP-specific annotations, keystore patterns)
- Emit **structured JSON** — file path, line number, rule ID, category, severity,
  code snippet
- Load rules from `rules.yaml` so patterns can be added without touching Python
- **No natural-language analysis, no recommendations** — that is Copilot's job

### Finding Schema

Every finding emitted by the scanner contains:

| Field | Example |
|-------|---------|
| `rule_id` | `JBOSS-TLS-001` |
| `category` | `tls_ssl` · `jndi` · `deployment_descriptors` · `classloading` · `logging` · `configuration` |
| `severity` | `critical` · `high` · `medium` · `low` · `info` |
| `file` | `current-dc.yaml` |
| `line` | `67` |
| `snippet` | `value: "JKS"` (truncated to 200 chars) |

### Rule Definition (`rules.yaml`)

| Field | Description |
|-------|-------------|
| `id` | Unique identifier (e.g., `JBOSS-TLS-001`) |
| `category` | Finding grouping |
| `severity` | Impact level |
| `description` | Human-readable explanation |
| `file_pattern` | Glob restricting which files to check (optional, default `*`) |
| `pattern` | Python regex applied to file **contents** |
| `name_pattern` | Python regex applied to file **names/paths** |

Add new rules by editing `rules.yaml` — no Python changes needed. The scanner
currently ships **28 rules** across 6 categories.

---

## Layer 2 — MCP Tool Server (Copilot Integration)

This is the key architectural decision. Instead of Copilot reading output from a
terminal, the analyzer is registered as a
[Model Context Protocol](https://modelcontextprotocol.io/) tool that Copilot Chat
can **call mid-conversation**.

### Registration (`.vscode/mcp.json`)

```json
{
  "servers": {
    "jboss-migration": {
      "type": "stdio",
      "command": "python",
      "args": ["${workspaceFolder}/analyzer/jboss_migration_analyzer.py", "--mcp-mode"],
      "description": "Scans a project for JBoss migration issues"
    }
  }
}
```

### Exposed Tools

| Tool | Description |
|------|-------------|
| `scan_project(path)` | Walk a directory tree and return all findings as JSON |
| `scan_file(path)` | Scan a single file |
| `list_rules()` | Return the full ruleset with IDs, categories, and descriptions |
| `check_deployment_config(path)` | Scan an OpenShift/K8s YAML for JBoss vestiges |

### Running the MCP Server Manually

```bash
python analyzer/jboss_migration_analyzer.py --mcp-mode
```

The server reads JSON-RPC messages on stdin and writes responses to stdout.
It implements the MCP `initialize`, `tools/list`, and `tools/call` methods.

### Why This Matters

You say "scan this project" in Copilot Chat and Copilot invokes the tool, gets
structured JSON, then layers AI reasoning on top — all within a single
conversation turn.

---

## Layer 3 — Custom Instructions (`.github/copilot-instructions.md`)

This file encodes the **repeatable migration runbook as AI behavior**. When
Copilot is asked to analyze a JBoss migration, the instructions tell it to:

1. **Start with the scanner.** Call `scan_project` to get deterministic findings.
2. **Group by category.** TLS/SSL, JNDI, Deployment Descriptors, Classloading,
   Logging, Configuration.
3. **Assess each finding.** Hard blocker vs. soft deprecation? Config-only fix
   vs. code change? What is the Spring Boot equivalent?
4. **Add AI observations.** Flag anything the scanner missed — implicit module
   dependencies, EAP-specific CDI behaviors, Undertow-vs-Tomcat differences,
   HikariCP datasource migration, EJB remote → REST/gRPC.
5. **Produce a risk-ordered checklist.** Critical → info, with effort estimates
   (config-only / small code change / significant refactor).

### Reference Files

| File | Role |
|------|------|
| `current-dc.yaml` | **Before** — Legacy JBoss-style OpenShift DeploymentConfig with PKCS12 keystores, EAP mount paths (`/opt/eap/...`), `--add-opens` flags |
| `new-dc.yaml` | **After** — Spring Boot 3.1+ PEM certs, `/etc/tls/private`, clean `JAVA_TOOL_OPTIONS` |

The instructions direct Copilot to compare against these files whenever TLS
findings surface.

---

## Layer 4 — Prompt Files (`.github/prompts/*.prompt.md`)

Reusable "recipes" your team invokes from Copilot Chat with
`#prompt:<name>` or via the VS Code command palette.

| Prompt File | Invocation | What It Does |
|-------------|------------|-------------|
| `migration-scan.prompt.md` | `#prompt:migration-scan` | Full project scan → severity summary → prioritized checklist with AI observations |
| `tls-migration.prompt.md` | `#prompt:tls-migration` | TLS/SSL deep-dive comparing current config against Spring Boot 3.1+ PEM best practices; references `current-dc.yaml` / `new-dc.yaml` |
| `deployment-config-review.prompt.md` | `#prompt:deployment-config-review` | OpenShift YAML audit for legacy mount paths, keystore refs, EAP-era JVM flags, `JAVA_APP_JAR` |
| `deep-analysis.prompt.md` | `#prompt:deep-analysis` | Per-finding contextual analysis, dependency-graph reasoning, AI gap detection, risk categorization (🔴 blocker / 🟡 pre-migration / 🟢 post-migration) |

---

## Layer 5 — Where the AI Fills the Gaps

The scanner catches what regex can match. Copilot, guided by the custom
instructions, fills in what it cannot:

- **Contextual inference.** The scanner finds `jboss-web.xml` but Copilot also
  notices the project uses JBoss Modules for classloading isolation — something
  hard to regex for but obvious to an LLM reading `module.xml`.
- **Dependency graph reasoning.** "This app uses Hibernate with a JBoss-managed
  datasource. After migration, configure HikariCP in `application.yml`."
- **Risk triage.** The scanner flags 47 findings. Copilot triages: "5 are
  blockers, 12 are config-only, 30 are warnings for post-migration."
- **Code generation on demand.** Pick a finding, say "fix this one," and Copilot
  generates the Spring Boot equivalent informed by scanner context.

---

## End-to-End Workflow

```
You (Copilot Chat):  #prompt:migration-scan /path/to/legacy-app

Copilot:
  1. Calls scan_project("/path/to/legacy-app") via MCP  →  structured JSON
  2. Applies copilot-instructions.md reasoning
  3. Adds AI observations the scanner missed
  4. Returns a prioritized migration checklist

You:  "Deep dive on the TLS findings"

Copilot:
  1. Calls check_deployment_config() via MCP
  2. Compares against new-dc.yaml pattern
  3. Generates the specific env-var changes needed

You:  "Generate the fix for finding JBOSS-TLS-001"

Copilot:
  1. Reads the flagged file and surrounding context
  2. Writes the Spring Boot equivalent
  3. You review and commit
```

---

## Smoke Test Results

Running the analyzer against this repo's own deployment configs:

| Target | Findings | Key Hits |
|--------|----------|----------|
| `current-dc.yaml` | **16** | `JBOSS-TLS-001` (JKS type), `JBOSS-TLS-002` (.jks path), `JBOSS-TLS-003` (keystore password), `JBOSS-TLS-004` (EAP mount path), `JBOSS-CL-002` (--add-opens ×6), `JBOSS-LOG-002` (log4j-openshift), `JBOSS-CFG-004` (JAVA_APP_JAR) |
| `new-dc.yaml` | **0** | Clean — target state confirmed |

MCP JSON-RPC: `initialize` → `tools/list` → `tools/call` all return correctly.

---

## Adding or Modifying Rules

1. Open `analyzer/rules.yaml`.
2. Add a new entry under `rules:` with `id`, `category`, `severity`,
   `description`, and either `pattern` (content regex) or `name_pattern`
   (filename regex).
3. Optionally restrict to specific file types via `file_pattern` (e.g.,
   `*.{java,xml}`).
4. Run the scanner against a known-positive file to verify the rule fires.
5. No Python changes required.
