# tech-tzepart

A personal tech blog, built as a plain static site and deployed to GitHub Pages.

**Live site:** https://tzepart.github.io/tech-tzepart/

## Status

The homepage currently ships with placeholder/dummy posts and copy while the
real content and design are still in progress.

## Stack

No build step — just static HTML, CSS, and vanilla JS. Posts and homepage
listings are data-driven: everything is rendered client-side from
`posts/posts.json` plus small content files, so adding a post never means
hand-editing the homepage.

```
.
├── index.html               # homepage shell; content is rendered by assets/js/home.js
├── posts/
│   ├── posts.json           # manifest: one entry per post (metadata for homepage + post page)
│   ├── _template/            # copy this folder to start a new post
│   │   ├── index.html
│   │   ├── content.html      # starter HTML post body (delete if writing Markdown)
│   │   ├── content.md        # starter Markdown post body (delete if writing HTML)
│   │   └── hero.html         # optional hero illustration (delete to omit)
│   └── <slug>/
│       ├── index.html        # identical shared shell (copied verbatim, never edited)
│       ├── content.html OR content.md   # the post body — pick one format
│       └── hero.html         # optional hero illustration/diagram figure
├── assets/
│   ├── css/style.css        # styles (theme, article/TOC/diagram/table/mermaid styles)
│   └── js/
│       ├── main.js          # theme toggle
│       ├── home.js          # renders featured/grid/topic pills from posts.json
│       └── post.js          # renders a single post page (TOC, mermaid, content)
└── .github/workflows/static.yml  # GitHub Pages deploy workflow
```

## Adding a new post

Posts can be written as **HTML or Markdown** — both go through the same
rendering pipeline (shared header/footer, automatic Table of Contents built
from `<h2>`/`##` headings, and [Mermaid](https://mermaid.js.org/) diagram
support in both formats).

1. Copy `posts/_template/` to `posts/<your-slug>/`.
2. Delete whichever starter content file you don't need — keep
   `content.html` for an HTML post, or `content.md` for a Markdown post.
   Edit the one you kept. Delete `hero.html` if you don't want a hero
   illustration.
3. Add one entry to `posts/posts.json`:
   ```json
   {
     "slug": "your-slug",
     "title": "Your Post Title",
     "tag": "SomeTag",
     "date": "2026-09-20",
     "dateLabel": "Sep 20, 2026",
     "readTime": "5 min",
     "excerpt": "One sentence shown on the homepage card.",
     "format": "html",
     "featured": false
   }
   ```
   `format` must be `"html"` or `"md"` and must match the content file you
   kept. Set `"featured": true` on at most one post to control the homepage
   hero slot (the newest post wins if none is marked featured).
4. That's it — the homepage picks up the new post automatically (sorted by
   `date`), and `posts/<your-slug>/` renders it using the shared layout.

Don't edit `posts/<slug>/index.html` itself — it's the same file in every
post folder and just bootstraps `assets/js/post.js`, which reads the slug
from the URL and does the rendering.

## Local development

This site loads content via `fetch()`, so it needs to be served over HTTP —
opening `index.html` directly via `file://` won't work.

```bash
python3 -m http.server 8000
```

Then visit `http://localhost:8000`.

## Deployment

Pushing to `main` triggers the `Deploy static content to Pages` GitHub Actions
workflow, which publishes the repository root to GitHub Pages.
