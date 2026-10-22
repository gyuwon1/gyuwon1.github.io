---
layout: page
title: 일본어
permalink: /japanese/
---

매일 단어 30개 (한자 · 히라가나 · 뜻 · 예문)

<ul class="post-list">
{% for post in site.categories.japanese %}
  <li>
    <span class="post-meta">{{ post.date | date: "%Y-%m-%d" }}</span>
    <h3><a href="{{ post.url | relative_url }}">{{ post.title }}</a></h3>
  </li>
{% endfor %}
</ul>
