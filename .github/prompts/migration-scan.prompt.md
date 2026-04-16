---
description: "Run the JBoss migration scanner and produce a prioritized checklist"
---

# Migration Scan

Run the **jboss-migration** `scan_project` tool against the current workspace
(or the path the user provides).

## Steps

1. Call `scan_project` with the target directory.
2. Summarize the total number of findings grouped by **severity**
   (critical / high / medium / low / info).
3. For each **critical** and **high** finding:
   - Show the file path and line number.
   - Explain what the pattern means and why it matters for migration.
   - State whether the fix is config-only or requires code changes.
4. List **medium** and **low** findings in a summary table (rule ID, file, one-line note).
5. Add an **AI Observations** section for anything you notice in the scanned
   files that the rules didn't cover — e.g., implicit JBoss module usage,
   EAP-specific CDI patterns, Undertow assumptions.
6. Produce a final **Migration Checklist** ordered by risk, with checkboxes.
