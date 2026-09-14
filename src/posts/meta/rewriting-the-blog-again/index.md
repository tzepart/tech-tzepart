---
title: Why I Rewrote My Blog for the Fourth Time
date: 2026-09-12
summary: A short retrospective on over-engineering a static site, chasing the perfect build tool, and eventually just shipping plain HTML.
---

<figure class="post-hero">
  <svg viewBox="0 0 760 260" role="img" aria-labelledby="hero1-title">
    <title id="hero1-title">Four stacked browser windows, each simpler than the last</title>
    <rect x="40" y="170" width="300" height="60" rx="8" class="dg-box" />
    <rect x="70" y="130" width="300" height="60" rx="8" class="dg-box" />
    <rect x="100" y="90" width="300" height="60" rx="8" class="dg-box" />
    <rect x="130" y="40" width="300" height="60" rx="8" class="dg-box-accent" />
    <circle cx="150" cy="55" r="4" class="dg-box-accent" />
    <circle cx="163" cy="55" r="4" class="dg-box-accent" />
    <circle cx="176" cy="55" r="4" class="dg-box-accent" />
    <text x="280" y="73" class="dg-text">&lt;html&gt; only</text>
    <text x="250" y="123" class="dg-text-sm">v3 · static site generator</text>
    <text x="220" y="163" class="dg-text-sm">v2 · React SPA</text>
    <text x="190" y="203" class="dg-text-sm">v1 · Jekyll</text>
  </svg>
  <figcaption>Four versions of the same idea, each one lighter than the last.</figcaption>
</figure>

<h2>A brief history of bad decisions</h2>
<p>
  Every year or so I get the urge to rewrite this blog. Not because the old
  version was broken — it usually still rendered fine — but because I'd
  read one blog post about a new build tool and suddenly felt like my
  setup was <em>obviously</em> obsolete. This is the story of four
  rewrites, and how I finally landed on the least interesting stack
  possible: plain files.
</p>

<h2>Version 1: the Jekyll years</h2>
<p>
  The first version was Jekyll, because that's what GitHub Pages
  supported natively at the time. It worked. I wrote Markdown, Liquid
  templates turned it into HTML, and I didn't think about it again for
  two years. In hindsight, "it worked and I didn't think about it" was
  the correct end state — I just didn't recognize it yet.
</p>

<h2>Version 2: the React overreach</h2>
<p>
  Then I decided a <em>blog</em> needed client-side routing, a component
  library, and hot module reloading. I rebuilt the whole thing as a
  single-page React app with a headless CMS behind it. Time-to-first-post
  went from "open a text editor" to "configure a webhook, wait for a
  build, hope the CMS schema migration didn't break the homepage query."
</p>
<blockquote>
  The lesson I refused to learn here: a blog with twelve posts does not
  have a scaling problem.
</blockquote>

<h2>Version 3: the static site generator rabbit hole</h2>
<p>
  Next came the "let's have my cake and eat it too" phase: a static site
  generator that pre-rendered the React components into HTML at build
  time. This was strictly better than v2, but it came with its own tax —
  a content-layer GraphQL schema for querying my own Markdown files, and
  a plugin ecosystem I had to keep pinned to exact versions or the build
  would quietly stop working.
</p>

<figure class="diagram">
  <svg viewBox="0 0 680 200" role="img" aria-labelledby="diagram1-title">
    <title id="diagram1-title">Build complexity across four blog versions</title>
    <defs>
      <marker id="arrow-v1" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">
        <path d="M0,0 L8,4 L0,8 Z" fill="currentColor" class="dg-text-sm" />
      </marker>
    </defs>
    <line x1="40" y1="160" x2="640" y2="160" class="dg-line" />
    <line x1="40" y1="160" x2="40" y2="20" class="dg-line" />

    <rect x="70" y="130" width="90" height="30" rx="6" class="dg-box" />
    <text x="115" y="145" class="dg-text-sm">Jekyll</text>

    <rect x="230" y="80" width="90" height="30" rx="6" class="dg-box" />
    <text x="275" y="95" class="dg-text-sm">React SPA</text>

    <rect x="390" y="40" width="110" height="30" rx="6" class="dg-box" />
    <text x="445" y="55" class="dg-text-sm">SSG + GraphQL</text>

    <rect x="540" y="130" width="90" height="30" rx="6" class="dg-box-accent" />
    <text x="585" y="145" class="dg-text-sm">Plain HTML</text>

    <text x="20" y="20" class="dg-text-sm" transform="rotate(-90 20 20)">complexity</text>
    <text x="640" y="180" class="dg-text-sm">time</text>
  </svg>
  <figcaption>Complexity crept up for three versions, then I gave up and it fell off a cliff.</figcaption>
</figure>

<h2>Version 4: just HTML</h2>
<p>
  The current version — the one you're reading — is a handful of static
  HTML files, one shared stylesheet, and about forty lines of vanilla
  JavaScript for a dark-mode toggle. No build step, no dependencies to
  patch, no lockfile to argue with Dependabot about.
</p>
<pre><code>.
├── index.html
├── posts/
│   └── rewriting-the-blog-again/index.html
└── assets/
    ├── css/style.css
    └── js/main.js</code></pre>
<p>
  Deploys are a git push. The GitHub Actions workflow just uploads the
  repository as-is to Pages — there's nothing to build because there's
  nothing to compile.
</p>

<h2>What I'd tell past me</h2>
<ul>
  <li>Match the tool to the actual traffic and update frequency, not the tool you want an excuse to use.</li>
  <li>A build step is a liability you're taking on, not a feature you're getting for free.</li>
  <li>"Boring technology" is a compliment, especially for something that just needs to keep working.</li>
</ul>
