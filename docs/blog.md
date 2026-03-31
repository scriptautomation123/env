---
layout: default
title: Blog Index
nav_order: 2
has_children: false
---

# Blog Articles

## All Posts

{% for post in site.posts %}
### [{{ post.title }}]({{ post.url }})
*{{ post.date | date: "%B %d, %Y" }}*

{{ post.excerpt | strip_html }}

[Read more →]({{ post.url }})

---

{% endfor %}
