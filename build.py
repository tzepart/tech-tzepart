#!/usr/bin/env python3
"""Build the blog: src/posts/**/*.md -> static HTML in dist/."""

from __future__ import annotations

import html
import re
import shutil
import sys
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path

import frontmatter
import markdown
from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
POSTS_DIR = SRC / "posts"
TEMPLATES_DIR = SRC / "templates"
STATIC_DIR = SRC / "static"
DIST = ROOT / "dist"

SITE_NAME = "tech.tzepart"
POST_ASSETS_DIRNAME = "assets"

MARKDOWN_EXTENSIONS = ["fenced_code", "tables", "codehilite"]
MARKDOWN_CONFIG = {"codehilite": {"css_class": "highlight", "guess_lang": False}}

MERMAID_FENCE = re.compile(r"^```mermaid[ \t]*\n(.*?)^```[ \t]*$", re.MULTILINE | re.DOTALL)
URL_ATTR = re.compile(r'(\s(?:href|src)=")([^"]*)(")')
URL_SCHEME = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")


class BuildError(Exception):
    pass


@dataclass
class ExtraPage:
    slug: str
    title: str
    order: int | None
    body: str
    has_mermaid: bool


@dataclass
class Post:
    rel: tuple[str, ...]
    src_dir: Path
    title: str
    date: date
    tags: list[str]
    summary: str | None
    body: str
    has_mermaid: bool
    pages: list[ExtraPage] = field(default_factory=list)

    @property
    def category(self) -> str:
        return self.rel[0]

    @property
    def subcategory(self) -> str | None:
        return self.rel[1] if len(self.rel) == 3 else None

    @property
    def breadcrumb(self) -> list[str]:
        return [humanize(part) for part in self.rel[:-1]]

    @property
    def url(self) -> str:
        return "posts/" + "/".join(self.rel) + "/"

    @property
    def date_label(self) -> str:
        return f"{self.date:%b} {self.date.day}, {self.date.year}"


def humanize(name: str) -> str:
    return re.sub(r"[-_]+", " ", name).strip().title()


def render_markdown(text: str) -> tuple[str, bool]:
    def to_mermaid_block(match: re.Match[str]) -> str:
        return f'\n\n<pre class="mermaid">{html.escape(match.group(1).rstrip())}</pre>\n\n'

    text, mermaid_count = MERMAID_FENCE.subn(to_mermaid_block, text)
    md = markdown.Markdown(extensions=MARKDOWN_EXTENSIONS, extension_configs=MARKDOWN_CONFIG)
    return md.convert(text), mermaid_count > 0


def rewrite_relative_urls(body: str, from_subpage: bool) -> str:
    """Map `foo.md` links to clean URLs; re-anchor relative URLs for sub-pages one level deeper."""

    def rewrite(url: str) -> str:
        if not url or url.startswith(("#", "/", "?")) or URL_SCHEME.match(url):
            return url
        path, sep, fragment = url.partition("#")
        if path.endswith(".md"):
            head, _, name = path[: -len(".md")].rpartition("/")
            path = (f"{head}/" if head else "") + ("" if name == "index" else f"{name}/")
        if from_subpage:
            path = "../" + path
        return (path or "./") + sep + fragment

    return URL_ATTR.sub(lambda m: m.group(1) + rewrite(m.group(2)) + m.group(3), body)


def read_markdown_file(path: Path) -> tuple[dict, str]:
    try:
        doc = frontmatter.load(path)
    except Exception as exc:
        raise BuildError(f"{path.relative_to(ROOT)}: invalid frontmatter ({exc})") from exc
    return dict(doc.metadata), doc.content


def parse_date(value: object, path: Path) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value.strip())
        except ValueError:
            pass
    raise BuildError(f"{path.relative_to(ROOT)}: 'date' is required and must be YYYY-MM-DD")


def discover_post_dirs() -> list[Path]:
    post_dirs = sorted(p.parent for p in POSTS_DIR.rglob("index.md"))
    post_dir_set = set(post_dirs)
    for post_dir in post_dirs:
        rel = post_dir.relative_to(POSTS_DIR).parts
        if len(rel) not in (2, 3):
            raise BuildError(
                f"{post_dir.relative_to(ROOT)}: posts must live at posts/<category>/<slug>/ "
                "or posts/<category>/<sub-category>/<slug>/"
            )
        nested_in = next((p for p in post_dir.parents if p in post_dir_set), None)
        if nested_in:
            raise BuildError(
                f"{post_dir.relative_to(ROOT)}: post directory is nested inside another post "
                f"({nested_in.relative_to(ROOT)})"
            )
    return post_dirs


def load_extra_page(path: Path) -> ExtraPage:
    meta, content = read_markdown_file(path)
    if path.stem == POST_ASSETS_DIRNAME:
        raise BuildError(f"{path.relative_to(ROOT)}: '{POST_ASSETS_DIRNAME}.md' clashes with the assets directory")
    order = meta.get("order")
    if order is not None and (isinstance(order, bool) or not isinstance(order, int)):
        raise BuildError(f"{path.relative_to(ROOT)}: 'order' must be an integer")
    title = meta.get("title")
    body, has_mermaid = render_markdown(content)
    return ExtraPage(
        slug=path.stem,
        title=title.strip() if isinstance(title, str) and title.strip() else humanize(path.stem),
        order=order,
        body=rewrite_relative_urls(body, from_subpage=True),
        has_mermaid=has_mermaid,
    )


def load_post(post_dir: Path) -> Post:
    index_path = post_dir / "index.md"
    meta, content = read_markdown_file(index_path)

    title = meta.get("title")
    if not isinstance(title, str) or not title.strip():
        raise BuildError(f"{index_path.relative_to(ROOT)}: 'title' is required")

    tags = meta.get("tags") or []
    if not isinstance(tags, list) or not all(isinstance(t, (str, int, float)) for t in tags):
        raise BuildError(f"{index_path.relative_to(ROOT)}: 'tags' must be a list")

    summary = meta.get("summary")
    body, has_mermaid = render_markdown(content)

    pages = [load_extra_page(p) for p in post_dir.glob("*.md") if p.name != "index.md"]
    pages.sort(key=lambda p: (p.order is None, p.order or 0, p.slug))

    return Post(
        rel=post_dir.relative_to(POSTS_DIR).parts,
        src_dir=post_dir,
        title=title.strip(),
        date=parse_date(meta.get("date"), index_path),
        tags=[str(t) for t in tags],
        summary=str(summary).strip() if summary else None,
        body=rewrite_relative_urls(body, from_subpage=False),
        has_mermaid=has_mermaid,
        pages=pages,
    )


def group_by_category(posts: list[Post]) -> list[dict]:
    newest_first = sorted(posts, key=lambda p: (-p.date.toordinal(), p.title))
    categories: dict[str, dict] = {}
    for post in newest_first:
        category = categories.setdefault(post.category, {"posts": [], "subcategories": {}})
        if post.subcategory:
            category["subcategories"].setdefault(post.subcategory, []).append(post)
        else:
            category["posts"].append(post)
    return [
        {
            "name": humanize(name),
            "posts": categories[name]["posts"],
            "subcategories": [
                {"name": humanize(sub), "posts": sub_posts}
                for sub, sub_posts in sorted(categories[name]["subcategories"].items())
            ],
        }
        for name in sorted(categories)
    ]


class Site:
    def __init__(self) -> None:
        self.env = Environment(
            loader=FileSystemLoader(TEMPLATES_DIR),
            autoescape=select_autoescape(["html"]),
            undefined=StrictUndefined,
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
        )

    def emit(self, parts: tuple[str, ...], template: str, **context: object) -> None:
        context.setdefault("description", None)
        context.setdefault("mermaid", False)
        root = "../" * len(parts) or "./"
        out = self.env.get_template(template).render(site_name=SITE_NAME, root=root, **context)
        out_path = DIST.joinpath(*parts, "index.html")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(out, encoding="utf-8", newline="\n")

    def emit_post(self, post: Post) -> None:
        parts = ("posts", *post.rel)
        self.emit(
            parts,
            "post.html",
            post=post,
            page=None,
            page_title=post.title,
            description=post.summary,
            body=post.body,
            nav=self.page_nav(post, current=None),
            mermaid=post.has_mermaid,
        )
        for page in post.pages:
            self.emit(
                (*parts, page.slug),
                "post.html",
                post=post,
                page=page,
                page_title=f"{page.title} · {post.title}",
                body=page.body,
                nav=self.page_nav(post, current=page),
                mermaid=page.has_mermaid,
            )
        assets = post.src_dir / POST_ASSETS_DIRNAME
        if assets.is_dir():
            shutil.copytree(assets, DIST.joinpath(*parts, POST_ASSETS_DIRNAME))

    @staticmethod
    def page_nav(post: Post, current: ExtraPage | None) -> list[dict]:
        if not post.pages:
            return []
        prefix = "../" if current else ""
        nav = [{"title": post.title, "href": None if current is None else prefix or "./"}]
        for page in post.pages:
            nav.append({"title": page.title, "href": None if page is current else f"{prefix}{page.slug}/"})
        return nav


def main() -> int:
    try:
        posts = [load_post(d) for d in discover_post_dirs()]
    except BuildError as exc:
        print(f"build failed: {exc}", file=sys.stderr)
        return 1

    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    shutil.copytree(STATIC_DIR, DIST / "static")

    site = Site()
    for post in posts:
        site.emit_post(post)
    site.emit((), "index.html", categories=group_by_category(posts))

    extra_count = sum(len(p.pages) for p in posts)
    print(f"Built {len(posts)} post(s) and {extra_count} extra page(s) into {DIST.relative_to(ROOT)}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
