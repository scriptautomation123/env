---
description: "Analyze TLS/SSL configuration for JBoss-to-Spring-Boot migration"
---

# TLS Migration Review

Compare the current TLS configuration against Spring Boot 3.1+ PEM certificate
best practices.

## Steps

1. Call `scan_project` (or `scan_file` for a specific deployment YAML) to find
   all TLS/SSL-related findings (rule IDs starting with `JBOSS-TLS-*`).
2. For each finding, show the **current** pattern and the **target** pattern:
   - Reference `current-dc.yaml` in this repo as the legacy "before" example.
   - Reference `new-dc.yaml` in this repo as the modern "after" example.
3. Explain the migration path for each:
   - **Keystore type** (JKS/PKCS12) → PEM via `server.ssl.certificate`
   - **Keystore password** → eliminated (PEM needs no password)
   - **Mount path** (`/opt/eap/...`) → `/etc/tls/private`
   - **Key alias** → not needed with PEM
4. If the project uses Spring Boot 3.1+, mention the **SSL Bundles API** as an
   advanced option for hot-reload and per-bundle trust stores.
5. Produce a concrete diff or env-var mapping showing exactly what to change.
