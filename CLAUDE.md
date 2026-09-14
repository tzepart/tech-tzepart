# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A personal tech blog: Markdown sources in `src/posts/` are rendered to static
HTML in `dist/` by `build.py` (no static site generator, no Node), then
deployed to GitHub Pages. Live at https://tzepart.github.io/tech-tzepart/.

## Commands

```bash
pip install -r requirements.txt   # Markdown, Pygments, Jinja2, python-frontmatter
python build.py                   # wipes and regenerates dist/
cd dist && python -m http.server 8000
```

There is no test/lint tooling. `dist/` is gitignored and never committed.
Pushing to `main` triggers `.github/workflows/deploy.yml`, which runs the
build and uploads `dist/` to Pages.

## Architecture

`build.py` has three phases, kept separate so features (RSS, analytics, etc.)
can be layered on without touching discovery/rendering:

1. **Discover/load** — every directory under `src/posts/` containing
   `index.md` is a post; it must be exactly 2 or 3 levels deep
   (`<category>/<slug>` or `<category>/<sub-category>/<slug>`), and posts
   can't be nested in other posts. Category/sub-category come from the path,
   never from frontmatter. Frontmatter: `title` and `date` required, `tags`
   and `summary` optional. Other `.md` files in the directory are extra pages
   (optional `title`, `order`). All posts load and validate **before**
   `dist/` is touched, so a bad post fails the build without deleting output.
2. **Render** — python-markdown with `fenced_code`, `tables`, `codehilite`
   (Pygments classes, colored by CSS variables in `style.css`). ```` ```mermaid ````
   fences are converted to `<pre class="mermaid">` before Markdown runs, and
   the page is flagged so `base.html` includes the Mermaid script only there.
   Relative `href`/`src` URLs are rewritten: `foo.md` → `foo/`, and on extra
   pages (one directory deeper) relative URLs get a `../` prefix.
3. **Emit** — `dist/` is cleared, `src/static/` copied to `dist/static/`,
   each post/extra page written as `.../index.html` (clean URLs), each post's
   `assets/` copied alongside, and `dist/index.html` generated from the
   category tree.

Output must stay deterministic (sorted traversal, no build timestamps) —
running the build twice must produce byte-identical `dist/`.

## Conventions

- All links in templates are relative via the `root` variable (`./`,
  `../../../`, …) because GitHub Pages project sites are served from a
  subpath — never use root-absolute `/...` URLs.
- No JavaScript except the conditional Mermaid include. Theme is
  `prefers-color-scheme` only.
- One stylesheet, system font stack. Inline SVG diagrams use the shared
  `dg-*` classes so they follow the theme.
