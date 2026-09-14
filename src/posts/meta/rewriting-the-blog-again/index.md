---
title: Why I Rewrote My Blog for the Fifth Time
date: 2026-09-12
tags: [static-sites, tooling, python]
summary: A short retrospective on over-engineering a static site, going all the way down to plain HTML, and landing on a build script small enough to read in one sitting.
cover: assets/cover.svg
---

## A brief history of bad decisions

Every year or so I get the urge to rewrite this blog. Not because the old
version was broken — it usually still rendered fine — but because I'd read one
blog post about a new build tool and suddenly felt like my setup was
*obviously* obsolete. This is the story of five versions, and how I finally
landed on the least interesting stack possible: Markdown files and one Python
script.

## Version 1: the Jekyll years

The first version was Jekyll, because that's what GitHub Pages supported
natively at the time. It worked. I wrote Markdown, Liquid templates turned it
into HTML, and I didn't think about it again for two years. In hindsight, "it
worked and I didn't think about it" was the correct end state — I just didn't
recognize it yet.

## Version 2: the React overreach

Then I decided a *blog* needed client-side routing, a component library, and
hot module reloading. I rebuilt the whole thing as a single-page React app with
a headless CMS behind it. Time-to-first-post went from "open a text editor" to
"configure a webhook, wait for a build, hope the CMS schema migration didn't
break the homepage query."

> The lesson I refused to learn here: a blog with twelve posts does not have a
> scaling problem.

## Version 3: the static site generator rabbit hole

Next came the "let's have my cake and eat it too" phase: a static site
generator that pre-rendered the React components into HTML at build time. This
was strictly better than v2, but it came with its own tax — a content-layer
GraphQL schema for querying my own Markdown files, and a plugin ecosystem I had
to keep pinned to exact versions or the build would quietly stop working.

<figure class="diagram">
  <svg viewBox="0 0 680 200" role="img" aria-labelledby="diagram1-title">
    <title id="diagram1-title">Build complexity across five blog versions</title>
    <line x1="40" y1="160" x2="640" y2="160" class="dg-line" />
    <line x1="40" y1="160" x2="40" y2="20" class="dg-line" />

    <rect x="60" y="120" width="90" height="30" rx="6" class="dg-box" />
    <text x="105" y="135" class="dg-text-sm">Jekyll</text>

    <rect x="175" y="70" width="90" height="30" rx="6" class="dg-box" />
    <text x="220" y="85" class="dg-text-sm">React SPA</text>

    <rect x="290" y="30" width="110" height="30" rx="6" class="dg-box" />
    <text x="345" y="45" class="dg-text-sm">SSG + GraphQL</text>

    <rect x="425" y="125" width="90" height="30" rx="6" class="dg-box" />
    <text x="470" y="140" class="dg-text-sm">Plain HTML</text>

    <rect x="540" y="110" width="100" height="30" rx="6" class="dg-box-accent" />
    <text x="590" y="125" class="dg-text-sm">build.py</text>

    <text x="20" y="20" class="dg-text-sm" transform="rotate(-90 20 20)">complexity</text>
    <text x="640" y="180" class="dg-text-sm">time</text>
  </svg>
  <figcaption>Complexity crept up for three versions, fell off a cliff, then came back up — just a little.</figcaption>
</figure>

## Version 4: just HTML

After the SSG, I overcorrected: no build step at all. The site was a handful
of static HTML files, one stylesheet, and a `posts.json` manifest. Each post
page was an identical HTML shell whose JavaScript read the slug from the URL,
fetched the post's content, and rendered Markdown in the browser with a library
loaded from a CDN.

It was genuinely pleasant to deploy — the GitHub Actions workflow uploaded the
repository as-is — but the cracks showed quickly:

- Every post had to be registered by hand in `posts.json`, and the homepage
  broke on a single trailing comma.
- Nothing rendered without JavaScript, including the list of posts.
- Every post shipped an HTML parser to the reader's browser to do work that
  could have happened once, on my machine.

I hadn't removed the build step. I'd moved it into every reader's browser and
run it on every page load.

## Version 5: one Python script

The current version — the one you're reading — puts the build step back, but
keeps it small enough to read in one sitting. Posts are Markdown files in
folders; the folder path *is* the category:

```text
.
├── src/
│   ├── posts/
│   │   └── meta/
│   │       └── rewriting-the-blog-again/
│   │           ├── index.md      # this post
│   │           └── assets/
│   ├── templates/                # base, post, homepage (Jinja2)
│   └── static/                   # style.css + two tiny scripts
├── build.py                      # src/ → dist/
└── requirements.txt              # four packages
```

`build.py` is about 400 lines of plain Python on top of python-markdown,
Pygments, Jinja2, and python-frontmatter. It finds every directory with an
`index.md`, renders it, and writes clean URLs into `dist/`. There's no manifest
to maintain — discovery is just a directory walk:

```python
def discover_post_dirs() -> list[Path]:
    post_dirs = sorted(p.parent for p in POSTS_DIR.rglob("index.md"))
    for post_dir in post_dirs:
        rel = post_dir.relative_to(POSTS_DIR).parts
        if len(rel) not in (2, 3):
            raise BuildError(f"{post_dir}: posts must live at posts/<category>/[<sub>/]<slug>/")
    return post_dirs
```

Everything the browser used to do now happens once, at build time: Markdown
rendering, syntax highlighting, and the homepage listing. Adding a post means
creating a folder and pushing; GitHub Actions runs `python build.py` and
publishes `dist/` to Pages. Extra `.md` files and Jupyter notebooks in a post's
folder become linked sub-pages automatically.

JavaScript is back to being optional: Mermaid diagrams load their script only
on pages that have one, and the homepage filters and the full-width toggle are
progressive extras. With JavaScript off, every page still reads fine.

## What I'd tell past me

- Match the tool to the actual traffic and update frequency, not the tool you
  want an excuse to use.
- A build step is a liability you're taking on — so keep it small enough that
  you can read all of it, and own all of it.
- "No build step" isn't free either: someone still does that work, and it's
  often your reader's browser.
- "Boring technology" is a compliment, especially for something that just needs
  to keep working.
