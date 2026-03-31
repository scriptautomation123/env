---
layout: home
title: Principal Engineer Blog
nav_order: 1
---

# Welcome to the Principal Engineer Blog

Deep technical insights on cloud-native architecture, container orchestration, and enterprise deployment patterns.

Hosted on GitHub Pages with Jekyll.

---

## Recent Articles

{% for post in site.posts limit:5 %}
- **[{{ post.title }}]({{ post.url }})** — {{ post.date | date: "%B %d, %Y" }}
  
  {{ post.excerpt | strip_html | truncatewords: 20 }}

{% endfor %}

[View all articles →](/env/blog)
