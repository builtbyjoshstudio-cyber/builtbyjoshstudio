# inkpress

One manuscript in, three outputs: a drop-in site page, an EPUB 3, and a
print-ready interior for KDP.

```
parse -> structure -> typography -> validate -+-> site HTML
                                              +-> EPUB 3
                                              +-> print HTML -> PDF
```

Everything left of the fork runs exactly once. The site page and the book files
are rendered from the same in-memory document, so they cannot drift apart —
fix a typo once and all three outputs change together.

**Standard library only.** No pip install, no venv, no lockfile. Python 3.8+.

---

## Setup

```powershell
.\bootstrap-inkpress.ps1
```

Verifies Python, creates working folders, runs the test suite, and builds the
sample manuscript so you can see real output before pointing it at a draft.

## The app

Double-click **`inkpress-app.cmd`**.

Pick a manuscript, fill in anything its header is missing, tick the formats you
want, click Format. The details form prefills from the manuscript when it has a
header, and anything you type wins over what's in the file — so a plain `.md`
with no header at all still works.

You can also drag a manuscript onto `inkpress-app.cmd` to open it directly.

Tkinter ships with Python, so there is nothing extra to install. Builds run on a
worker thread, so the window stays responsive, and missing details are reported
as plain instructions ("Fill in the Author field above") rather than tracebacks.

The command line below does the same work and takes the same options — the app
is a window over the identical pipeline, not a reimplementation.

## Build from the command line

```powershell
.\inkpress.ps1 manuscripts\your-draft.md
```

```
inkpress 1.0.0 — The Lamplighter's Round
  2 chapters, 294 words
  wrote epub   build\epub\the-lamplighters-round.epub  [4.0KB]
  wrote print  build\print\the-lamplighters-round-interior.html  [4.4KB]
  wrote site   build\site\the-lamplighters-round.html  [8.3KB]
```

Useful flags:

| Flag | Effect |
| --- | --- |
| `--targets site` | build one target instead of all three (`site`, `epub`, `print`) |
| `--check` | parse and validate only, write nothing |
| `--dry-run` | report the paths it would write |
| `--chrome-from PAGE.html` | inherit nav, footer and stylesheets from a live site page |
| `--base-url URL` | override the canonical and schema base URL |
| `--path-prefix DIR` | site directory the page will live in (default `writing`) |
| `--print-css FILE` | replace the generated paged-media CSS entirely |

Exit codes: `0` success, `1` manuscript or validation error, `2` bad invocation.

---

## Manuscript format

A markdown file with front matter.

```markdown
---
title: The Lamplighter's Round
subtitle: A Short Passage
author: J.S. Warden
date: 2026-07-25
language: en
description: One sentence, under 160 characters, for search and social.
eyebrow: Field Dispatch · Overlayed Echoes
standfirst: The line under the headline.
logline: Recovered log · Mara · eleven years in.
trim: 6x9
margin: 0.75in
gutter: 0.25in
subjects:
  - Fiction
---

## Chapter One

Prose here.

* * *

Prose after a scene break.

### A section inside the chapter

> A pulled quote.
```

### Front matter

| Key | Required for | Notes |
| --- | --- | --- |
| `title` | all | |
| `author` | all | |
| `date` | all | `YYYY-MM-DD`, validated |
| `description` | site | warns over 160 characters |
| `language` | epub | BCP 47, e.g. `en` |
| `subtitle` | — | title page and `<title>` |
| `eyebrow`, `standfirst`, `logline` | — | site page header |
| `section`, `section_url` | — | breadcrumb, default `Writing` / `books.html` |
| `image` | — | absolute URL for OG and Twitter cards |
| `slug` | — | overrides the slug derived from the title |
| `url` | — | overrides the canonical URL |
| `trim`, `margin`, `gutter` | — | print geometry, default `6x9` / `0.75in` / `0.25in` |
| `publisher`, `subjects` | — | EPUB metadata |
| `uuid` | — | pins the EPUB identifier across editions |

### Body syntax

| Written | Becomes |
| --- | --- |
| `## Title` | chapter break |
| `### Title` | section heading |
| `* * *` or `---` | scene break |
| `> line` | blockquote |
| blank line | paragraph break |
| `**bold**`, `*italic*`, `_italic_` | `<strong>`, `<em>` |
| `` `code` `` | `<code>` |
| `[text](url)` | link |

A manuscript with no `##` headings becomes one implicit chapter — the normal
shape for a short dispatch.

### Typography

Applied automatically to prose, never to code spans or link targets:

| Typed | Set |
| --- | --- |
| `---` | — em dash |
| `--` | – en dash |
| `...` | … ellipsis |
| `"quoted"` | “quoted” |
| `'quoted'` | ‘quoted’ |
| `don't`, `'90s` | don’t, ’90s |

---

## Outputs

### `build/site/<slug>.html`

A complete page: title and description, canonical link, Open Graph and Twitter
cards, `BreadcrumbList` and `BlogPosting` JSON-LD, then an
`<article class="dispatch">` body matching the existing `writing/` pages.

Pass `--chrome-from` an existing page and inkpress lifts its stylesheet links,
analytics, `<nav class="site-nav">` and `<footer>` into the output, so the page
inherits whatever the live site currently uses instead of a hardcoded copy:

```powershell
.\inkpress.ps1 manuscripts\your-draft.md --targets site `
  --chrome-from ..\writing\the-things-i-let-go.html
```

Without a donor the page still renders, just with no nav or footer.

### `build/epub/<slug>.epub`

EPUB 3: one XHTML file per chapter, a nav document doubling as the table of
contents, and a package document. Assembled by hand because the ordering rules
are strict — `mimetype` must be the first entry and stored uncompressed.

Builds are reproducible. The publication UUID is derived from title + author
via uuid5 and every timestamp comes from front matter, so rebuilding an
unchanged manuscript produces a byte-identical archive.

### `build/print/<slug>-interior.html`

Paged-media HTML for a KDP interior: trim size from front matter, mirrored
gutters, running heads (author verso, title recto), drop-folio page numbers,
chapters starting recto, small-caps opening lines, orphan and widow control.

No PDF renderer is bundled, so the pipeline stays dependency-free. Use any of:

```powershell
weasyprint build\print\your-draft-interior.html your-draft.pdf   # pip install weasyprint
prince build\print\your-draft-interior.html -o your-draft.pdf
```

Or open it in a browser and use Print to PDF — set margins to None and enable
background graphics.

---

## Layout

```
inkpress/
  bootstrap-inkpress.ps1     setup + smoke test
  inkpress-app.cmd           double-click to open the app
  inkpress_app.py            the desktop app (Tkinter)
  inkpress.ps1               PowerShell wrapper
  inkpress.py                CLI
  inkpress_lib/
    manuscript.py            front matter + block parsing
    typography.py            punctuation
    inline.py                inline markdown -> HTML, escaping
    structure.py             blocks -> chapters -> Document
    validate.py              per-target checks
    body.py                  shared prose rendering
    render_site.py           site page + chrome extraction
    render_epub.py           EPUB 3 writer
    render_print.py          paged-media HTML
    pipeline.py              stage wiring and fan-out
  manuscripts/               source drafts
  tests/                     36 tests
  build/                     output (gitignored)
```

## Tests

```powershell
python -m unittest discover -s tests -t .
```

Covers each stage plus end-to-end builds: EPUB archive structure and
reproducibility, site metadata and chrome extraction, print paged-media rules,
and the validation failure modes.

---

## Adding a stage

Stages are plain functions over the `Document`. To add one — a
British/American spelling pass, a repeated-word check — write it in
`inkpress_lib/`, call it from `pipeline.build()` between `structure.build()`
and `validate.check()`, and all three outputs inherit it at once.
