---
description: "Deep-dive analysis of scanner findings with AI-powered gap detection"
---

# Deep Analysis

For each finding from the migration scanner, perform a thorough analysis that
goes beyond pattern matching.

## Steps

1. Call `scan_project` to get the full findings list.
2. For each finding, read the **surrounding code context** (not just the matched
   line) to understand:
   - Is the JBoss-ism load-bearing or vestigial?
   - Are there downstream dependencies on this pattern?
   - What is the blast radius if we change this?
3. **Dependency graph reasoning** — Look at imports, Maven/Gradle dependencies,
   and configuration files to identify:
   - JBoss-managed datasources that need HikariCP configuration
   - JBoss Remoting / EJB remote calls that need REST or gRPC replacement
   - JBoss Transactions (JTA) usage that needs Spring @Transactional mapping
   - JBoss Infinispan cache → Spring Cache abstraction
4. **Gap detection** — Flag things the scanner rules did NOT catch:
   - Implicit module.xml dependencies inferred from Java imports
   - CDI producer methods with JBoss-scoped lifecycle
   - Undertow-specific behavior (multipart config, WebSocket setup, HTTP/2)
   - Classpath scanning differences between JBoss Modules and flat classpath
5. **Risk assessment** — Categorize all findings (scanner + AI-detected) into:
   - 🔴 **Blockers** — App will not start without fixing these
   - 🟡 **Pre-migration** — Should fix before go-live but app can start
   - 🟢 **Post-migration** — Can be addressed after initial migration
6. Produce a **prioritized migration plan** with effort estimates per item.
