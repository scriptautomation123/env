# Copilot Custom Instructions

## JBoss Migration Analysis Mode

When asked to analyze a JBoss-to-Spring-Boot migration:

1. **Start with the scanner.** Use the `scan_project` MCP tool to get structured
   findings. If scanning a single file, use `scan_file` instead. Never skip the
   deterministic scan — it catches patterns reliably that free-form analysis may
   miss.

2. **Group findings by category.** Present results organized by:
   - **TLS/SSL** — keystore → PEM migration, mount paths, password elimination
   - **JNDI** — lookup replacement, datasource externalization
   - **Deployment Descriptors** — jboss-web.xml, standalone.xml, ejb-jar.xml removal
   - **Classloading** — JBoss Modules → Maven/Gradle, --add-opens cleanup
   - **Logging** — JBoss Logging → SLF4J/Logback
   - **Configuration** — system properties, security domains, EAP annotations

3. **Assess each finding.** For every scanner hit, determine:
   - Is this a **hard blocker** (app won't start) or a **soft deprecation** (works but not idiomatic)?
   - What is the **Spring Boot equivalent**?
   - Is it a **config-only fix** or does it require **code changes**?

4. **Add AI-layer observations.** Flag anything the scanner didn't catch but that
   you recognize from context:
   - Implicit JBoss module dependencies visible in import statements
   - EAP-specific CDI behaviors (e.g., `@Produces` with JBoss-scoped beans)
   - Undertow vs. embedded Tomcat behavioral differences (multipart handling,
     WebSocket config, HTTP/2 defaults)
   - JBoss-managed datasource → HikariCP connection pool migration
   - JBoss Remoting / EJB remote calls that need REST or gRPC replacement

5. **Produce a migration checklist** ordered by **risk** (critical → info), not
   by file path. Include estimated effort per item (config-only / small code
   change / significant refactor).

## Reference Files in This Repo

- `current-dc.yaml` — Legacy JBoss-style OpenShift DeploymentConfig with PKCS12
  keystores, EAP mount paths, and --add-opens flags. This is the **before** state.
- `new-dc.yaml` — Target state using Spring Boot 3.1+ native PEM certificate
  support, clean JAVA_TOOL_OPTIONS, and /etc/tls/private mount path. This is the
  **after** state.

When reviewing TLS migration findings, always compare against these two files to
show the concrete before/after transformation.

## General Guidelines

- Always cite the specific rule ID (e.g., JBOSS-TLS-001) when referencing a
  scanner finding.
- When generating fix code, show the minimal diff — don't rewrite entire files.
- If a finding is a false positive, explain why and suggest the user can add an
  exclusion to `rules.yaml`.
- Use `list_rules` to show the user what patterns the scanner checks when they
  ask about coverage.
