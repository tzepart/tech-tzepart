# tech-tzepart

A personal tech blog, built as a plain static site and deployed to GitHub Pages.

**Live site:** https://tzepart.github.io/tech-tzepart/

## Status

The homepage currently ships with placeholder/dummy posts and copy while the
real content and design are still in progress.

## Stack

No build step — just static HTML, CSS, and vanilla JS.

```
.
├── index.html          # main page
├── assets/
│   ├── css/style.css   # styles (incl. light/dark theme)
│   └── js/main.js      # theme toggle
└── .github/workflows/static.yml  # GitHub Pages deploy workflow
```

## Local development

Open `index.html` directly in a browser, or serve the folder locally:

```bash
python3 -m http.server 8000
```

Then visit `http://localhost:8000`.

## Deployment

Pushing to `main` triggers the `Deploy static content to Pages` GitHub Actions
workflow, which publishes the repository root to GitHub Pages.
