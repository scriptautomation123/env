# JBoss → Spring Boot Embedded Tomcat Migration Analyzer

Automated analysis tool that scans a JBoss / Spring Boot project and produces a
structured report of what was detected and what needs to be refactored to run as
a **Spring Boot executable WAR on containers with embedded Tomcat**.

## Quick Start

```bash
# Requires Python 3.10+ and PyYAML
pip install pyyaml

# Run against your project
python analyzer/jboss_migration_analyzer.py /path/to/my-jboss-app

# Output both text and JSON
python analyzer/jboss_migration_analyzer.py /path/to/my-jboss-app --format all

# Custom rules file and output location
python analyzer/jboss_migration_analyzer.py /path/to/my-jboss-app \
    --rules analyzer/rules.yaml \
    --output /tmp/report.json \
    --format json
```

## What It Detects

The analyzer evaluates ~25 rules across five categories:

### 1. JBoss Descriptors (`JBOSS-DESC-*`)
| Rule | Detects |
|------|---------|
| JBOSS-DESC-001 | `jboss-web.xml` — context root & virtual host config |
| JBOSS-DESC-002 | `jboss-deployment-structure.xml` — class-loading isolation |
| JBOSS-DESC-003 | `jboss-ejb3.xml` — EJB3 deployment descriptor |
| JBOSS-DESC-004 | `jboss-service.xml` — MBean service descriptor |
| JBOSS-DESC-005 | `jboss-classloading.xml` — legacy class-loading |

### 2. Build System (`BUILD-*`)
| Rule | Detects |
|------|---------|
| BUILD-001 | WAR packaging type |
| BUILD-002 | EAR packaging type |
| BUILD-003 | JBoss EAP / WildFly BOM or dependency |
| BUILD-004 | JBoss-specific Maven plugins |
| BUILD-005 | Missing `spring-boot-maven-plugin` |
| BUILD-006 | `spring-boot-starter-tomcat` scope check |
| BUILD-007 | Spring Boot version detection |

### 3. Source Code Patterns (`SRC-*`)
| Rule | Detects |
|------|---------|
| SRC-001 | JBoss/WildFly-specific Java imports |
| SRC-002 | JNDI lookup usage |
| SRC-003 | EJB annotations (`@Stateless`, `@MessageDriven`, etc.) |
| SRC-004 | `SpringBootServletInitializer` present (✓) |
| SRC-005 | `SpringBootServletInitializer` missing |
| SRC-006 | `javax.*` namespace (pre-Jakarta EE 10) |
| SRC-007 | JAX-RS annotations |

### 4. TLS / SSL Configuration (`TLS-*`)
| Rule | Detects |
|------|---------|
| TLS-001 | JKS keystore configuration |
| TLS-002 | PKCS12 keystore configuration |
| TLS-003 | Legacy JBoss EAP cert mount paths (`/opt/eap/…`) |
| TLS-004 | PEM TLS already configured (✓) |
| TLS-005 | Keystore password in plain text |

### 5. Deployment / Container (`DEPLOY-*`)
| Rule | Detects |
|------|---------|
| DEPLOY-001 | OpenShift `DeploymentConfig` (deprecated) |
| DEPLOY-002 | JBoss/WildFly base image in Dockerfile |
| DEPLOY-003 | Legacy `--add-opens` JVM flags |
| DEPLOY-004 | Missing health probes |
| DEPLOY-005 | `JAVA_APP_JAR` env var (JBoss s2i convention) |

## Report Output

### Text (human-readable)
```
========================================================================
  JBoss → Spring Boot Embedded Tomcat  ·  Migration Analysis Report
========================================================================
  Project      : /path/to/my-jboss-app
  Files scanned: 247

  ── Spring Boot Detection ──
  Version              : 3.2.1
  Packaging            : war
  ServletInitializer   : yes
  Boot Maven Plugin    : yes
  Actuator             : yes

  ── Summary ──
  Total findings       : 8
            CRITICAL   : 1
                HIGH   : 3
              MEDIUM   : 2
                INFO   : 2
  Migration readiness  : ❌  NOT READY (critical/high issues remain)

  ── Detailed Findings ──
  [1] CRITICAL  JBOSS-DESC-001 — jboss-web.xml detected
      ...
```

### JSON
```json
{
  "project_dir": "/path/to/my-jboss-app",
  "analyzed_at": "2026-03-31T02:10:00+00:00",
  "total_files_scanned": 247,
  "spring_boot": {
    "version": "3.2.1",
    "packaging": "war",
    "has_servlet_initializer": true,
    "has_boot_maven_plugin": true,
    "has_actuator": true,
    "main_class": "src/main/java/com/example/App.java"
  },
  "findings": [ ... ],
  "summary": {
    "total_findings": 8,
    "by_severity": {"critical": 1, "high": 3, "medium": 2, "info": 2},
    "migration_ready": false
  }
}
```

## Exit Codes

| Code | Meaning |
|------|---------|
| `0`  | Migration-ready — no critical or high findings |
| `1`  | Input error (bad path, missing rules file) |
| `2`  | Not migration-ready — critical/high findings exist |

This makes the analyzer suitable for CI/CD gating:
```bash
python analyzer/jboss_migration_analyzer.py ./my-app || echo "Migration blockers found"
```

## Extending Rules

Add new rules to `rules.yaml` using the existing structure:

```yaml
- id: CUSTOM-001
  name: "My custom check"
  severity: medium
  file_glob: ["**/*.xml"]
  file_contains: "some-pattern"
  description: "Explanation of what this detects."
  action: "Recommended remediation."
```

Rule fields:
- **`file_glob`** — file path patterns to match
- **`file_contains`** — regex patterns to search inside matching files
- **`pom_dependency`** — Maven `groupId:artifactId` patterns (wildcards supported)
- **`negate`** — `true` to fire when the pattern is *not* found (absence check)
- **`severity`** — `critical` | `high` | `medium` | `low` | `info`

## Prerequisites

- Python 3.10+
- [PyYAML](https://pypi.org/project/PyYAML/) (`pip install pyyaml`)
