---
name: new-post
description: Scaffold a new blog post for this site — asks for title, tag, date, format (HTML or Markdown), excerpt, read time, and whether it's featured, then clones posts/_template into posts/<slug>/ and adds an entry to posts/posts.json. Does NOT write any post body content — that's left for the user to fill in by hand afterward. Use when the user asks to create/add/scaffold a new post, or runs /new-post.
argument-hint: [title]
allowed-tools: Read, Write, Bash, AskUserQuestion
---

# /new-post — scaffold a new blog post

This repo's post pipeline is data-driven: `posts/posts.json` holds metadata
for every post, and `posts/<slug>/index.html` is an identical shared shell
(see `CLAUDE.md`/`README.md`) that fetches `content.html` or `content.md`
from its own folder based on the `format` field. This skill only creates
that scaffolding — folder, shell, empty content file, and the manifest
entry. **It must never write the actual post body.** The user writes that
part by hand after this skill finishes.

## Step 1 — gather context

Read `posts/posts.json` to see existing slugs (to avoid collisions) and
existing tags (to suggest reusing one instead of creating a near-duplicate,
e.g. "Backend" vs "backend").

## Step 2 — collect the required fields

If `$ARGUMENTS` was given, treat it as a starting guess for the title but
still confirm it. Ask for the following. Free-text fields can be asked as a
single plain chat message; use `AskUserQuestion` for the two closed-choice
fields (format, featured) since those directly change what files get
created.

- **Title** (free text, required).
- **Tag** (free text, required) — mention the existing tags found in Step 1
  as a hint so the user can reuse one on purpose rather than by accident.
- **Format** — HTML or Markdown (`AskUserQuestion`, required). This decides
  whether `content.html` or `content.md` is kept.
- **Excerpt** (free text, required) — one sentence shown on the homepage
  card.
- **Read time** (free text, e.g. "5 min") — required by the schema, but
  since there's no content yet this is just a placeholder estimate; make
  clear the user can correct it later.
- **Date** (free text) — default to today (`date +%Y-%m-%d`) if the user
  doesn't give one; also derive a human `dateLabel` like "Sep 20, 2026".
- **Featured?** — yes/no (`AskUserQuestion`, required). If yes and another
  post in `posts.json` already has `"featured": true`, tell the user and
  confirm whether to unset the old one (only one post should be featured
  at a time — `home.js` only honors the first match).

## Step 3 — derive the slug

Slugify the title the same way `assets/js/post.js` slugifies headings:
lowercase, strip anything that isn't `a-z0-9` or whitespace/hyphen, collapse
whitespace to single hyphens. If the resulting slug collides with an
existing `posts/<slug>/` folder, tell the user and ask for a different
title or an explicit slug — don't silently overwrite an existing post.

## Step 4 — scaffold the folder

```bash
mkdir -p posts/<slug>
cp posts/_template/index.html posts/<slug>/index.html
cp posts/_template/hero.html   posts/<slug>/hero.html
```

Then copy **only** the content file matching the chosen format — never
both:

- Format = html → `cp posts/_template/content.html posts/<slug>/content.html`
- Format = md → `cp posts/_template/content.md posts/<slug>/content.md`

Copy the template file byte-for-byte, including its placeholder example
content and HTML comments. **Do not edit, rewrite, summarize, or fill in
any of it** — the user asked explicitly to write real content themselves
afterward. Do not touch `index.html` at all (it's the shared shell, never
edited per-post).

## Step 5 — update posts.json

Append one new object to the JSON array in `posts/posts.json` with the
fields collected above: `slug`, `title`, `tag`, `date`, `dateLabel`,
`readTime`, `excerpt`, `format`, `featured`. If the user opted to swap the
featured post, flip the old entry's `featured` to `false` in the same edit.
Keep the file valid JSON (trailing commas will break `fetch().then(res =>
res.json())` on both `home.js` and `post.js`).

## Step 6 — report back

Tell the user, concisely:
- The new folder path.
- Which single content file needs their real writing (`content.html` or
  `content.md`), and that `hero.html` is optional (delete it if they don't
  want a hero illustration).
- That nothing else needs manual editing — `index.html` and the
  `posts.json` entry are already wired up, so the post will appear on the
  homepage and render correctly as soon as they replace the placeholder
  content.

Do not start a local server, open a browser, or otherwise try to preview
the post — there's no real content yet for that to be useful.
