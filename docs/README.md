# Principal Engineer Blog

A modern, responsive Jekyll site documenting cloud-native architecture, OpenShift deployments, and AI-driven engineering tools.

## Quick Start

### Local Development

```bash
cd docs
bundle install
bundle exec jekyll serve
```

Visit `http://localhost:4000/env` in your browser.

### Site Structure

```
docs/
├── _config.yml           # Jekyll configuration
├── _posts/               # Blog articles (markdown)
├── index.md              # Homepage
├── blog.md               # Blog archive
└── Gemfile               # Dependencies
```

### Writing Posts

1. Create a new file in `_posts/` with format: `YYYY-MM-DD-title.md`
2. Include front matter (see existing posts for template)
3. Write in markdown
4. Push to main—GitHub Pages auto-publishes

### Theme

[Just the Docs](https://just-the-docs.github.io/just-the-docs/) — clean, responsive, built for technical documentation.

## Deployment

GitHub Pages automatically publishes changes from the `docs` folder on the `main` branch.

**Repository settings:** Settings → Pages → Source: Deploy from a branch → Branch: `main` folder: `/docs`

## Featured Articles

- **[OpenClaw: Intelligent Agents for Complex Engineering Tasks](/_posts/2026-03-31-openclaw-intelligent-agents.md)** — Explores agent-driven automation for multistep engineering workflows.
- **[OpenShift Spring Boot Deployment: From Legacy TLS to Cloud-Native Architecture](/_posts/2026-03-31-openshift-deployment-evolution.md)** — Technical analysis of certificate management modernization with $876K 5-year savings potential.

---

**Author:** Principal Engineer  
**Last updated:** March 31, 2026
