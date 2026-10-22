---
layout: page
title: CCNA
permalink: /ccna/
---

기초부터 매일 하나씩 (20~30분 분량)

<ul class="post-list">
{% for post in site.categories.ccna %}
  <li>
    <span class="post-meta">{{ post.date | date: "%Y-%m-%d" }}</span>
    <h3><a href="{{ post.url | relative_url }}">{{ post.title }}</a></h3>
  </li>
{% endfor %}
</ul>
