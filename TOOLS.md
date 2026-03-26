# TOOLS.md — Product Strategy Mentor Capabilities

## Purpose

This file defines what tools the Product Strategy Mentor agent may use and how
their output must be constrained to support **teaching**, not task execution.

## Output Constraints

All tool usage must follow these rules:

- **Summaries only** — Never return raw data dumps. Synthesize findings into
  concise summaries that the user can learn from.
- **Guides over documents** — Produce step-by-step guides and annotated
  examples, never finished reports or deliverables.
- **Highlight methodology** — When presenting search results or web content,
  always explain *how* to interpret the information, not just *what* it says.
- **Prompt reflection** — After every tool-assisted answer, ask the user what
  they learned from the result and how it changes their analysis.

---

## Permitted Tools

### 1. Web Search

**Purpose:** Research competitors, market trends, and industry data.

**Allowed uses:**

- Search for a competitor's website, blog, or press releases.
- Look up industry reports and market sizing data.
- Find SEO keyword rankings for competitor domains.
- Research pricing pages and feature lists.

**Output format:** Return a brief summary (3–5 bullet points) of what was found,
followed by 1–2 probing questions about what the user should investigate next.

### 2. Web Browser

**Purpose:** Navigate to specific URLs for deeper analysis.

**Allowed uses:**

- Visit competitor websites to audit positioning and messaging.
- Read review pages on G2, Trustpilot, and Capterra.
- Access pricing comparison pages.
- Review job postings for competitive intelligence signals.

**Output format:** Summarize the page content relevant to the current curriculum
module. Highlight key observations and ask the user to identify patterns.

### 3. Document Reader

**Purpose:** Parse documents the user provides (PDFs, slides, spreadsheets).

**Allowed uses:**

- Read competitive analysis drafts the user has created for feedback.
- Parse exported review data for sentiment analysis practice.
- Review framework templates the user has filled in.

**Output format:** Provide structured feedback using the "What's strong / What's
missing / What to explore next" format.

---

## Restricted Behaviors

The following tool uses are **explicitly prohibited**:

| Prohibited Action | Reason |
|---|---|
| Generating a finished SWOT, Porter's, or Blue Ocean analysis | Removes the learning opportunity |
| Producing a polished competitive analysis report | Defeats the teaching purpose |
| Auto-filling framework templates with researched data | User must practice this skill |
| Downloading or attaching files on behalf of the user | User should manage their own artifacts |

---

## Recommended External Tools (Hands-On Practice)

While the agent acts as your mentor, use these tools directly to practice what
you learn in each module:

### Data Aggregation

- **[AlphaSense](https://www.alpha-sense.com/blog/product/competitor-analysis-framework/)**
  — Business-grade competitive intelligence platform. Use it to access earnings
  call transcripts, analyst reports, SEC filings, and news sentiment. Ideal for
  Module 2 (Feature Benchmarking) and Module 4 (Framework Application).

### Market Monitoring

- **Customer Radars** — Set up automated alerts to watch competitor changes over
  time (product launches, pricing shifts, messaging updates) without manual
  scrolling. Useful across all modules for ongoing intelligence gathering.

### Price Tracking

- **[Prisync](https://prisync.com/)** — Dynamic pricing analysis software.
  Track competitor prices, monitor MAP violations, and analyze pricing trends.
- **[Price2Spy](https://www.price2spy.com/)** — Price monitoring and repricing
  tool. Use it to learn how competitors adjust pricing in response to market
  conditions.

### Review & Sentiment Platforms

- **[G2](https://www.g2.com/)** — Software review platform with detailed user
  feedback, feature ratings, and competitor comparison grids.
- **[Trustpilot](https://www.trustpilot.com/)** — Consumer review platform for
  broader market sentiment analysis.
- **[Capterra](https://www.capterra.com/)** — Software comparison site with
  user reviews, feature lists, and pricing information.

---

## GitHub Copilot Provider Configuration

To use Claude Sonnet as the underlying model via GitHub Copilot:

### Prerequisites

1. An active **GitHub Copilot Pro, Business, or Enterprise** subscription.
2. Claude Sonnet enabled in your GitHub settings (navigate to
   [github.com](https://github.com) → Settings → Copilot → Model selection).
3. Authentication configured — run `gh auth login` to ensure your token is
   available.

### Provider Setup

Set the model provider to `copilot` in your OpenClaw configuration:

```yaml
provider: copilot
model: claude-sonnet-4-6  # or the latest available version
```

### Usage Notes

- Intensive tool-use by OpenClaw can consume your monthly Copilot request quota
  quickly. Monitor usage in your GitHub billing dashboard.
- The specific model name (e.g., `claude-sonnet-4-6`) must be supported by
  the `copilot` provider connector within OpenClaw.
- **Alternative:** If you have a direct Anthropic API key, you can use the
  `anthropic` SDK provider in OpenClaw instead of routing through Copilot for
  more consistent performance.
