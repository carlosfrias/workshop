# Wiki HTML Build

The markdown wiki is the source of truth. This directory builds a browser-friendly HTML version with React-based navigation.

## Why Two Outputs?

| Format | Best For | Tool |
|---------|----------|------|
| Markdown (.md) | Editing, Obsidian, git diffs | Any text editor |
| HTML | Browsing, sharing, non-technical users | Web browser |

The markdown files are never duplicated — the HTML is generated from them.

## Build

```bash
cd wiki/{project-name}/wiki-build
npm install
npm run build
```

Output goes to `wiki/{project-name}/wiki-build/dist/`. Open `dist/index.html` in any browser.

## Dev Server

```bash
cd wiki/{project-name}/wiki-build
npm run dev
```

Opens a local dev server with hot reload at `http://localhost:5173`.

## Architecture

Uses [VitePress](https://vitepress.dev) — a markdown-first static site generator built on Vite + Vue:

- Reads the same `.md` files the Obsidian wiki uses
- Generates React-style SPA navigation with sidebar, search, and breadcrumbs
- Produces static HTML (no server required — just open in a browser)
- Supports custom themes if you want to brand it

### Why VitePress?

| Option | Pros | Why Not |
|--------|------|---------|
| VitePress | Markdown-first, fast builds, nice defaults | Vue-based (not React) but produces identical UX |
| Docusaurus | React-based, mature | Heavier, more config, React JSX for customization |
| MkDocs | Simple, Python | Less polished UI, no SPA navigation |
| Custom React | Full control | You'd write the markdown parser, routing, and nav from scratch |
| mdBook | Rust-based, fast | Targets book format, not project wikis |

VitePress wins for a project wiki: it reads your existing markdown with zero modification, produces beautiful navigation, and builds in seconds. The Vue runtime is an implementation detail — the output looks and feels like a modern React SPA.

### Customization

Edit `wiki/{project-name}/wiki-build/.vitepress/config.js` to customize:
- Sidebar navigation
- Site title and theme
- Search configuration
- Custom CSS (brand colors, fonts)

## Directory Structure

```
wiki/
└── {project-name}/
    ├── Home.md                      # Domain index — wiki landing page
    ├── {domain1}/                   # Domain wiki — front and center
    │   └── Activity Log.md
    ├── {domain2}/                   # Domain wiki
    │   └── Activity Log.md
    ├── _meta/                       # Reference docs (reachable, non-central)
    │   ├── Architecture.md
    │   ├── Agent Definitions.md
    │   └── ...
    └── wiki-build/                  # HTML build (this directory)
        ├── .vitepress/
        │   └── config.js
        ├── package.json
        └── dist/                    # Generated HTML (gitignored)
```

The markdown source files live in the parent directory. VitePress reads from `.` (current directory) which contains all the `.md` files — no duplication.

## Git Ignore

Add to project root `.gitignore`:
```
wiki/{project-name}/wiki-build/dist/
wiki/{project-name}/wiki-build/node_modules/
```