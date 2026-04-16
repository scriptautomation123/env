---
description: "Review OpenShift DeploymentConfig YAML for JBoss vestiges"
---

# Deployment Config Review

Analyze the provided OpenShift DeploymentConfig (or Deployment) YAML for
JBoss EAP vestiges that should be modernized for Spring Boot embedded Tomcat.

## Steps

1. Call `check_deployment_config` with the path to the YAML file.
2. Review each finding and explain:
   - **Legacy mount paths** — `/opt/eap/standalone/configuration/cert` should
     become `/etc/tls/private` (Linux FHS convention).
   - **Keystore references** — `.jks` / `.p12` file paths should be replaced
     with PEM cert/key references.
   - **JAVA_TOOL_OPTIONS flags** — identify EAP-era `--add-opens` flags that
     may no longer be needed, encryption key system properties that should move
     to Spring Boot config, and log4j references that should become Logback.
   - **JAVA_APP_JAR** — JBoss s2i convention; Spring Boot uses executable JARs
     directly.
3. Produce a side-by-side comparison table:
   | Setting | Current (JBoss-style) | Target (Spring Boot) |
4. Generate the updated YAML snippet with all vestiges removed.
5. Flag any security concerns (e.g., hardcoded encryption keys in env vars).
