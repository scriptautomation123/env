---
layout: default
title: Blog Articles
---

<div class="blog-index">
  <div class="blog-header animate-fade-in-up">
    <h1>All <span class="gradient-text">Articles</span></h1>
    <p>Deep-dives into enterprise engineering, cloud-native patterns, and AI-powered tooling</p>
  </div>

  <div class="blog-filters animate-fade-in-up delay-1">
    <button class="filter-btn active" data-filter="all">All</button>
    <button class="filter-btn" data-filter="architecture">Architecture</button>
    <button class="filter-btn" data-filter="ai">AI</button>
    <button class="filter-btn" data-filter="openshift">OpenShift</button>
    <button class="filter-btn" data-filter="migration">Migration</button>
    <button class="filter-btn" data-filter="tls">TLS / Security</button>
  </div>

  <div class="post-grid">
    {% for post in site.posts %}
    <article class="post-card animate-on-scroll" data-categories="{{ post.categories | join: ' ' }}">
      <div class="post-card-header">
        <div class="post-card-tags">
          {% for category in post.categories limit:2 %}
          <span class="tag tag-{{ category | slugify }}">{{ category }}</span>
          {% endfor %}
        </div>
        <time class="post-card-date" datetime="{{ post.date | date_to_xmlschema }}">
          {{ post.date | date: "%b %d, %Y" }}
        </time>
      </div>
      <h3 class="post-card-title">
        <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
      </h3>
      <p class="post-card-excerpt">{{ post.excerpt | strip_html | truncatewords: 30 }}</p>
      <div class="post-card-footer">
        <div class="post-card-author">
          <div class="author-avatar">PE</div>
          <span>{{ post.author | default: "Principal Engineer" }}</span>
        </div>
        <a href="{{ post.url | relative_url }}" class="post-card-link">
          Read more
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
        </a>
      </div>
    </article>
    {% endfor %}
  </div>
</div>
