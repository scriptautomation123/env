# env

## on windows 
C:\Users\swapa\.wslconfig

```
[wsl2]
networkingMode=Mirrored
```

## on Linux host

etc /etc/wsl.conf

```
systemd=true

[user]
default=swapanc

[network]
generateResolvConf = false
```

/etc/resolv.conf

```
nameserver 8.8.8.8
nameserver 8.8.4.4
```

## restart wsl and test dns lookup

```
wsl --shutdown
wsl
ping -c 3 google.com
```

## JBoss → Spring Boot Migration Analyzer

The `analyzer/` directory contains an automated analysis tool that scans a
JBoss / Spring Boot project and reports what needs to be refactored to run as a
Spring Boot executable WAR on containers with embedded Tomcat.

```bash
pip install pyyaml
python analyzer/jboss_migration_analyzer.py /path/to/my-jboss-app --format all
```

See [`analyzer/README.md`](analyzer/README.md) for full documentation, rule
catalogue, and CI/CD integration examples.

## OpenClaw Teaching Kernel

This repository includes an OpenClaw "Workspace-First" kernel configured as a
**Product Strategy Mentor**. Instead of executing tasks, the agent guides you
through competitive analysis and product strategy using Socratic instruction.

### Files

| File | Purpose |
|---|---|
| `SOUL.md` | Defines the agent identity, behavioral rules, teaching style, and the four-module curriculum (Competitor Identification → Feature Benchmarking → Customer Sentiment Analysis → Framework Application). |
| `TOOLS.md` | Declares permitted tools (web search, browser, document reader) with output constrained to summaries and guides. Lists recommended hands-on tools (AlphaSense, Prisync, Price2Spy, G2, Trustpilot, Capterra) and GitHub Copilot provider setup for Claude Sonnet. |

### Quick Start

1. Install [OpenClaw](https://docs.openclaw.ai) and ensure you have a GitHub
   Copilot Pro/Business/Enterprise subscription.
2. Enable Claude Sonnet in your GitHub settings (Settings → Copilot → Model
   selection).
3. Place `SOUL.md` and `TOOLS.md` in your OpenClaw workspace root.
4. Run OpenClaw — the agent will greet you in Teacher Mode and begin with
   Module 1 (Competitor Identification).
