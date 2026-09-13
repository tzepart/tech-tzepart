# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A personal tech blog: a dependency-free static site (no build step, no npm,
no bundler) deployed to GitHub Pages. Live at
https://tzepart.github.io/tech-tzepart/.

## Commands

There is no build, lint, or test tooling — the entire "toolchain" is a local
static file server, since the site loads post content via `fetch()` and
won't work under `file://`:

```bash
python3 -m http.server 8000
```

Then visit `http://localhost:8000`. Deployment is automatic: pushing to
`main` triggers `.github/workflows/static.yml`, which uploads the repo root
as-is to GitHub Pages (no build step there either — `path: '.'`).

## Architecture

### Data-driven posts and homepage

`posts/posts.json` is the single source of truth for post metadata (slug,
title, tag, date, dateLabel, readTime, excerpt, format, featured). Nothing
about individual posts is hardcoded into `index.html` or into per-post pages
— everything is rendered client-side at page load:

- `assets/js/home.js` fetches `posts/posts.json`, picks the `featured: true`
  post (or the newest one) for the hero slot, renders the rest into the post
  grid, and derives the topic pills from the set of tags in use. It targets
  `#featuredPost`, `#postGrid`, and `#topicPills` in `index.html`.
- `assets/js/post.js` runs on every `posts/<slug>/index.html` page. It
  derives the slug from `location.pathname` (not from any per-file
  variable), looks up that slug in `../posts.json`, fills in the title/tag/
  date/read-time placeholders, fetches `hero.html` (optional) and
  `content.html` or `content.md` (whichever `entry.format` says), builds
  the Table of Contents from the rendered `<h2>` elements, and activates
  Mermaid diagrams.

Consequence: **every `posts/<slug>/index.html` file is byte-identical** —
it's a dumb shell whose only job is to load `post.js`, which does all the
work based on the URL. Never hand-edit a post's `index.html`; if the shell
needs to change, change it everywhere (or start from `posts/_template/`).

### Adding/editing a post

1. Copy `posts/_template/` to `posts/<slug>/`.
2. Keep exactly one of `content.html` or `content.md` (delete the other),
   and edit it. Delete `hero.html` if the post has no hero illustration.
3. Add one entry to `posts/posts.json` with a matching `"format": "html"`
   or `"format": "md"`.

Both content formats go through the same pipeline: only `<h2>` (HTML) /
`##` (Markdown) headings become TOC entries; Mermaid diagrams work in both
(` ```mermaid ` fences in Markdown, `<pre class="mermaid">` in HTML);
Markdown tables render natively, and HTML posts can use plain `<table>`.
Markdown is parsed client-side via `marked` and diagrams via `mermaid`,
both loaded from jsDelivr in the post shell — there is no server-side
rendering.

### Styling and theme

Everything shares one stylesheet, `assets/css/style.css`. Light/dark theme
is CSS custom properties on `:root`, overridden both by
`prefers-color-scheme` and by an explicit `data-theme` attribute set via
`assets/js/main.js` (the theme toggle button), so dark mode works whether
the user has an OS preference or has manually toggled it. Hand-drawn SVG
diagrams (in `content.html` files) use shared CSS classes (`dg-box`,
`dg-box-accent`, `dg-text`, `dg-line`, etc.) rather than inline colors, so
they stay theme-aware without extra JS.

### Path conventions

All internal links/assets use **relative paths** (never root-absolute
`/...`) because GitHub Pages project sites are served from a subpath. Pages
two levels deep (`posts/<slug>/*`) reference the shared stylesheet and
scripts as `../../assets/...`.
