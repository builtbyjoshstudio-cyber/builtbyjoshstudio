# builtbyjoshstudio.com — Session Handoff

**Date:** 2026-05-30 (Phase 2A shipped — book discoverability live)
**Repo:** https://github.com/builtbyjoshstudio-cyber/builtbyjoshstudio
**Local path:** `C:\Users\jotra\builtbyjoshstudio`
**Host:** GitHub Pages — custom domain `builtbyjoshstudio.com` via CNAME → Fastly CDN
**HEAD (pushed):** `8729226` on `main`, in sync with `origin/main`. All committed work is live and verified. **Working tree clean** (the handoff-update commit sits on top of `8729226`).
**Latest backup tag:** `backup-after-book-discoverability` (`8729226`, current live state). Earlier this arc: `backup-pre-phase-2a` (`720e3e7`), `backup-after-phase-6` (`8055f13`).

---

## 🧭 Session summary (plain language)

Since the last HANDOFF (`17c02db`, end of Phase 6), this session shipped five distinct feature groups:

1. **GA4 e-commerce instrumentation** — added the standard `view_item` / `add_to_cart` / `begin_checkout` / `purchase` events site-wide, consolidated the Lemon Squeezy Setup callback in `js/ga4-events.js` so it fires on every page (not just the 8 Tynkr product pages), added `category` field to every entry in `js/checkout-config.js`. Then caught a lazy-load race condition that prevented `begin_checkout`/`purchase` from firing on collection pages and fixed it with a 13-line patch to `js/ls-checkout-btn.js`. Live-verified all four standard events fire end-to-end on Aquarius.
2. **Zero-based-budget-excel SERP optimization** — pivoted `<title>` and meta description from tutorial-only to dual template+tutorial intent (`Zero-Based Budget Excel Template + How to Build One (2026)`), then aligned the visible H1, Article JSON-LD `headline`, in-body H2, all 5 inbound related-post-card titles, and the product-page sidebar inline link to match. Fully consistent end-to-end now.
3. **/books.html for J.S. Warden fiction** — created a new top-level books page with hero, two book sections (Overlayed Echoes + Ebonspire Chronicles), pen-name note. Added a "Writing" link to all 91 site footers (after the About link, root-absolute `/books.html` href). Updated About page mention paragraph. Standardized pen-name spelling on `J.S. Warden` (no spaces) across the site — the about.html schema's two `workExample` author fields got updated as part of this.
4. **Overlayed Echoes full-length launch** — Josh published the 257-page paperback+ebook of Overlayed Echoes (the original 85-page novella was pulled, new Amazon URL is `https://a.co/d/06ZWovoY`). Real cover image and OG share card images added at `images/books/`. All 7 instances of the old `04YzP4o4` URL across books.html, about.html, and index.html swapped. JSON-LD `workExample` updated with new url + bookFormat array (ebook + paperback) + image + numberOfPages 257 + isAccessibleForFree false. Stale "novella" / "85 pages" / "being expanded" copy removed.

5. **Phase 2A — book discoverability** — added "Writing → /books.html" to every page's `<ul class="nav-links">` (all 92 nav-bearing pages, incl. books.html's own nav as an intentional self-link); restructured the about.html connect-list "Amazon" entry → /books.html (eyebrow "Books by J.S. Warden", internal); added one `.footer-links { flex-wrap: wrap; }` rule to tokens.css. Commit `8729226`, live-verified (12/12).

**✅ SHIPPED:** All five groups are committed, pushed, and live. Working tree clean. Phase 2A specifics in the "COMPLETED: Phase 2A" section below.

---

## 🔴 STANDING INSTRUCTIONS — read these first

These are the rules Josh has set through hard pushback over multiple sessions. Apply them by default; only deviate if Josh says so explicitly.

### 1. Communication style: terse, directive, no preamble.
Josh's style. No padding. Surface tradeoffs in 1–2 sentences and pick a default; don't ask a dozen questions. When you find real ambiguity worth confirming, ask ONE crisp question with a recommended default. Skip "Great, I'll start by…" preambles.

### 2. The site has NO template engine.
Every HTML page is standalone with its own inline `<style>` block, its own JSON-LD, its own nav, its own footer. The Python scripts in `tools/` are the closest thing to a template engine — they generate per-page HTML from manifests + hardcoded sign/animal data. When you need to change something site-wide (e.g., add a footer link, inject a schema block), either (a) edit the generators and regenerate, or (b) write a Python sweep that visits every `.html` file. There's no shared partial to update. **Exception**: `/css/tokens.css` is loaded by all 92 HTML files — cross-cutting CSS fixes that don't conflict with per-page inline `<style>` properties can go there (the inline rules don't set every property, so tokens.css can fill gaps via cascade — see footer-flex-wrap precedent in Phase 2A audit).

### 3. Lemon Squeezy IS the primary checkout for the zodiac art Collections. Etsy is a secondary reference only.
Full LS rollout complete — all 77 buttons across 38 collection pages live with real LS overlay URLs. Tynkr products use the key-based `[data-checkout]` + `CHECKOUT_CONFIG` infrastructure (`js/checkout.js`, `js/checkout-config.js`). Collection pages use the `.ls-checkout-btn` pattern with `data-checkout-url` + click handler in `js/ls-checkout-btn.js`.

### 4. Sales-channel hierarchy on Collection pages
Primary: LS button. Secondary: muted Etsy reference at sidebar bottom. Footer: Etsy as directory listing only.

### 5. Verify file content claims against actual source code/data, not against documentation or assumptions.
When a brief says X but the actual count is Y, flag the discrepancy and use accurate numbers. **This session's biggest catch under this rule**: Phase 2A's "all-links page" doesn't exist as a separate page — it's the about.html `connect-list` section. Josh's URL screenshot showed `builtbyjoshstudio.com/al…` which was the truncated `about.html` in the browser URL bar.

### 6. LS URL activation procedure
For each `<button class="ls-checkout-btn">`: paste LS overlay URL into `data-checkout-url=""`, remove `disabled`, swap text to live price. Generators handle this via per-Collection `LS_URL_BY_SIGN` dicts + `ls_button_state()` helper.

### 7. Identity hygiene rules (site-wide):
- **Founder name:** "Josh" only on every public-facing surface. Never "Joshua Tran" / "Josh Tran" / "Tran" / "Joshua".
- **Pen name (fiction only):** `J.S. Warden` — **no spaces between initials**. The book cover itself uses `J. S. Warden` (with spaces) as a stylistic choice for the cover art; the site canonical is no-spaces. Standardized in commit `d9484c5`. Currently 0 spaced-form instances on public pages (HANDOFF.md mentions both for documentation).
- **City-level data:** state-level "Kansas" only on public pages. Never any city. Registered agent (Wichita, KS) appears only on `/legal/index.html`.
- **`<meta name="keywords">`:** never. Stripped from all pages.

### 8. The site-wide Organization JSON-LD block is on every HTML page, injected before `</head>`.
Stable `@id`: `https://builtbyjoshstudio.com/#organization`. Per-page Product/FAQ/etc. schemas `@id`-reference the Organization for `manufacturer` and `seller`. **books.html includes it too** (commit `d9484c5` flagged this as a 3rd block beyond the original 2-block spec, for site-wide consistency).

### 9. Schema rule for Collection pages: Product + FAQPage + BreadcrumbList + Organization per page.
Product schema uses `@id: <page-url>#product`, SKU `BBJ-<COL>-<SIGN>`, `additionalProperty` block, single `Offer` at bundle price `InStock`, `hasMerchantReturnPolicy: MerchantReturnNotPermitted`, `datePublished` + `dateModified`. FAQPage must mirror visible FAQ exactly (ASCII-safe substitutions in schema). 51/51 collection + 8/8 product pages have all schema questions visibly rendered (445/445 audited in Phase 4).

### 10. Use the Python generators in `tools/`, not direct HTML editing, for Collection pages.
5 generators (`build_western_signs_page.py`, `build_realm_page_master.py`, `build_chinese_animal_pages.py`, `build_chinese_realms_page.py`, `build_zodiac_landscapes_page.py`). Hand-written hub: `collections/chinese-zodiac-art.html` (13 Product blocks: 1 top-level + 12 nested ItemList items — only ever edit the top-level one).

### 11. Schema for blog/tool posts (legacy rule)
Article + BreadcrumbList only. No WebApplication / featureList / applicationCategory. Four pre-existing tool posts keep their old WebApplication blocks — leave alone.

### 12. Antigravity owns the cooking apps. You write blog posts about them. Never apps.

### 13. GitHub Pages builds can fail on transient infrastructure issues.
Recovery: `gh run rerun <run_id> --failed` OR push an empty commit. Always verify live content with `curl ?x=<timestamp>` after push.

### 14. Jekyll's Liquid parser will choke on literal `{{` in markdown — `_config.yml` excludes HANDOFF.md.
`/_config.yml` excludes `HANDOFF.md` + `HANDOFF-*.md` from Jekyll processing. If you add any tracked top-level markdown with literal `{{`, either add it to the `exclude` list or wrap in `{% raw %}` ... `{% endraw %}`.

### 15. GA4 instrumentation architecture (added this session)
- `js/ga4-events.js` is loaded on all 91 HTML pages via `<script defer>`. Contains: `etsy_click` listener, `__ga4LemonSqueezyHandler` (fires standard GA4 `begin_checkout` on `Checkout.ViewCart` and `purchase` on `Checkout.Success`), and `__ga4SetupLemonSqueezy()` polling-loop that wires the LS Setup callback site-wide.
- `js/checkout.js` (loaded on 8 Tynkr product pages) does NOT call `LemonSqueezy.Setup` — that wiring is centralized in ga4-events.js. checkout.js only calls `LemonSqueezy.Refresh()` to attach overlay click interception.
- `js/ls-checkout-btn.js` (loaded on 38 collection pages) lazy-loads lemon.js on first click, then explicitly invokes `window.__ga4SetupLemonSqueezy()` from its `s.onload` handler **before** opening the overlay — this is critical, otherwise the first `Checkout.ViewCart` event is lost (commit `62b7b67` fixed this race condition).
- `window.__ga4LemonSqueezySetupDone` is the guard flag preventing double-wiring.
- Slug → category mapping for items[] is centralized in `js/ga4-events.js` `slugToCategory()` and mirrored in per-page inline `view_item` scripts. CS hub (`chinese-zodiac-art`) maps to `Chinese Zodiac Art Bundle` (clusters with the 12 per-animal pages for reporting consistency).
- `js/checkout-config.js`: all 16 entries (8 paid + 8 lite) have `category` field — 12 `Notion Template`, 4 `Spreadsheet`.

### 16. /books.html is linked from nav (all 92 pages), 91 footers, and About.
Books page is a separate `/books.html` at root. **Phase 2A (commit `8729226`) added "Writing → /books.html" to every page's `<ul class="nav-links">` — all 92 nav-bearing pages, including books.html's own nav as an intentional self-link.** Footers carry it on 91 pages; **books.html's footer deliberately does NOT self-link** (commit `d9484c5`). About links it from the mention paragraph + the connect-list (restructured in Phase 2A → eyebrow "Books by J.S. Warden", internal `/books.html`). mobile-nav.js is pure toggle; drawer items come from each page's `.nav-links` markup.

---

## 🟢 Status: live, clean — Phase 2A read-only audit pending decisions

Working tree clean (only the usual untracked: `.claude/`, `.netlify/`, dated `HANDOFF-*.md` archives, per-session `_audit`/`_phase*` utility scripts in `tools/`).

---

## First steps for the new session

```bash
cd /c/Users/jotra/builtbyjoshstudio
git status                                                  # clean
git log --oneline -10                                       # HEAD e195a79
git tag -l 'backup-*' --sort=-creatordate | head -5         # backup-after-phase-6 newest (8 commits below HEAD)

# Live verification of recent feature deploys:
curl -fsS "https://builtbyjoshstudio.com/books.html?x=$(date +%s)" | grep -c "Zero surname" >/dev/null && echo "books.html serving" # 0 means no surname (good)
curl -fsS -I "https://builtbyjoshstudio.com/images/books/overlayed-echoes-cover.webp?x=$(date +%s)" | head -1  # 200
curl -fsS "https://builtbyjoshstudio.com/blog/zero-based-budget-excel.html?x=$(date +%s)" | grep -c "Zero-Based Budget Excel Template + How to Build One"  # 1+
curl -fsS "https://builtbyjoshstudio.com/?x=$(date +%s)" | grep -c "06ZWovoY"  # 2 (homepage sameAs arrays)
curl -fsS "https://builtbyjoshstudio.com/?x=$(date +%s)" | grep -c "04YzP4o4"  # 0 (no stragglers)

# Pages build status:
gh run list --workflow=pages-build-deployment --limit 5
```

---

## What this session accomplished (4 feature groups, 7 commits)

### Group 1 — GA4 e-commerce instrumentation (commits `9423a02` + `62b7b67`)

| Commit | What |
|---|---|
| `9423a02` | Added standard GA4 events (`view_item`, `add_to_cart`, `begin_checkout`, `purchase`) site-wide. Consolidated `LemonSqueezy.Setup({ eventHandler })` in `js/ga4-events.js` (was previously scoped to 8 product pages via checkout.js). Added inline `view_item` scripts to 8 product pages + 38 collection pages (CS hub deliberately skipped — no `.ls-checkout-btn` element). Added `data-item-category` to all 77 `.ls-checkout-btn` elements. Added `add_to_cart` firing in `js/ls-checkout-btn.js` and `js/checkout.js` click handlers. Added `category` field to all 16 `CHECKOUT_CONFIG` entries. 50 files / 1,475 insertions / 106 deletions. |
| `62b7b67` | **Bug fix**: collection-page `begin_checkout` / `purchase` weren't firing because lemon.js is lazy-loaded (on first click), but ga4-events.js's polling for SDK readiness ran at DOMContentLoaded and timed out 5s later — long before the user clicked. Patched `js/ls-checkout-btn.js` `s.onload` to invoke `window.__ga4SetupLemonSqueezy()` **after** the SDK initialises and **before** `then()` opens the overlay. 1 file / +13 lines. Verified live on Aquarius — full funnel now fires in correct order: `view_item` → `add_to_cart` → `ls_checkout_open` → `begin_checkout` → `purchase`. |

### Group 2 — Zero-based-budget-excel SERP rewrite (commits `fda6e0b` + `0921c2f`)

| Commit | What |
|---|---|
| `fda6e0b` | Rewrote `<title>` + meta description on `blog/zero-based-budget-excel.html` to dual template+tutorial intent: `Zero-Based Budget Excel Template + How to Build One (2026)`. Title 57 chars, description 160 chars. Internally consistent across SEO, OG, Twitter tags. H1 + Article schema `headline` left unchanged (deliberate split: SERP vs landing). 1 file / 6 insertions / 6 deletions. |
| `0921c2f` | Reversed the deliberate split — aligned visible H1, JSON-LD Article `headline`, in-body H2 ("How to Build One — The Walkthrough"), all 5 inbound related-post-card titles (blog.html + 4 blog posts), and the product-page sidebar inline link on `products/ultimate-budget-workbook.html` to the SERP title verbatim. Now fully aligned end-to-end. 7 files / 9/9. |

### Group 3 — /books.html + footer rollout (commits `d9484c5` + `27666ac`)

| Commit | What |
|---|---|
| `d9484c5` | Created `/books.html` (top-level books page for J.S. Warden fiction). Hero + 2 book sections + pen-name note. JSON-LD: BreadcrumbList + Person (J.S. Warden, workExample = both books) + Organization. Updated `about.html` "Beyond the Studio" paragraph mention (kept lines 488 + 559 untouched). Standardized pen-name spelling to `J.S. Warden` (no spaces) site-wide — small 2-string exception in about.html schema `workExample` author fields. Added "Writing" footer link across all 91 HTML pages (root-absolute `/books.html`, inserted after About `<li>`; handled the legal/index.html outlier with `/about.html` root-absolute About href separately). Added books.html sitemap entry. Added books.html to llms.txt under About section. 94 files / 571 insertions / 4 deletions. **books.html's own footer does NOT self-link** to Writing — deliberate per Josh's call. |
| `27666ac` | One-line follow-up: corrected books.html sitemap `lastmod` from `2026-05-26` (wrong by 3 days) to `2026-05-29` (actual deploy date). 1 file / 1/1. |

### Group 4 — Overlayed Echoes full-length launch (commit `e195a79`)

The 85-page Overlayed Echoes novella was pulled and replaced with a 257-page paperback+ebook full-length novel. New Amazon URL `https://a.co/d/06ZWovoY`. This commit fixed every stale URL + cover + copy reference site-wide. **Highest-risk** because the old URL was broken on visitor click-through and the cover/OG images were brand-new asset paths.

- Created `images/books/` directory with 4 new files (overlayed-echoes-cover.webp/jpg @ 600×900, og-books.webp/jpg @ 1200×630). All 4 HEAD-verified 200 on live.
- `books.html`: added `<picture>` element for the real cover (replacing the placeholder div). Added 7 `og:image`/`twitter:image` head tags. Twitter card upgraded `summary → summary_large_image`. JSON-LD `workExample` updated: url → `06ZWovoY`, bookFormat → `["…/EBook", "…/Paperback"]` (array), +image, +numberOfPages 257, +isAccessibleForFree false. Section body rewritten: subtitle "The first book of a five-book series", "Honest framing / 85 pages / expanding" paragraph removed. Added `.book-cover img` + mobile centering CSS (necessary completeness for visual parallelism with the kept Ebonspire placeholder).
- `about.html`: line 488 ("What I bring to the work") single-clause fix removing "being expanded into the full-length first volume." Line 511 ("Beyond the Studio") rewritten: "debut novella" → "debut novel", "currently on Amazon and being expanded into a five-book series" → "the first book of a five-book series, now on Amazon." JSON-LD `workExample` updated identically to books.html. 3 Amazon URL updates (sameAs line 76, workExample line 91, connect-list line 557).
- `index.html`: 2 stale `04YzP4o4` references in JSON-LD `sameAs` arrays (Person + Organization or similar) updated to `06ZWovoY`. Out of original scope per "don't touch homepage" — but stale-URL structured data on the highest-traffic page was strictly worse than touching it. Decision approved by Josh during audit.
- `sitemap.xml`: about.html `lastmod` 2026-04-28 → 2026-05-29 (books.html already today from the prior commit, so no change needed there). index.html lastmod deliberately untouched (only structured data changed, not content).

8 files / 41 insertions / 18 deletions + 4 new image assets. All 7 old-URL instances swapped, 0 stragglers. All 4 image HEAD checks 200. Live-verified end-to-end.

---

## ✅ COMPLETED: Phase 2A — Book discoverability + footer fixes

**Status:** Shipped in commit `8729226` (2026-05-30) — 93 files, 99 ins / 4 del, live-verified (12/12). Backup `backup-pre-phase-2a` (`720e3e7`) taken before edits; `backup-after-book-discoverability` (`8729226`) marks the result. All three decisions made (1: Option A / 92 files · 2: option b · 3: approved) and applied — mobile-nav Writing link across all 92 nav pages, about.html connect-list restructured, tokens.css flex-wrap rule added. CS hub `collections/chinese-zodiac-art.html` insert split a minified line (renders identically, left surgical). Sweep: `tools/_phase2a_nav_rollout.py` (untracked). _Original audit detail retained below for reference._

### Audit findings (current as of HANDOFF write — verify with quick re-grep if context unclear)

**1.1 Mobile hamburger nav** — `js/mobile-nav.js` (62 lines) is pure toggle (no hard-coded item list). The drawer items come from each page's own `<ul class="nav-links">` markup; CSS transforms the desktop nav into a drawer on narrow viewports. **4 nav-link variants** across 91 pages:

| Count | Variant (first label · ... · last label) |
|---|---|
| 44 | Templates · Zodiac Art · Blog · Resources · Free Tools · About · Legal |
| 39 | Templates · Zodiac Art · Blog · Resources · Free Tools · About |
| 7 | Tynkr Tools · Zodiac Art · Blog · Resources · Free Tools · About · Legal |
| 2 | Tynkr Tools · Zodiac Art · Blog · Resources · Free Tools · About *(about.html + books.html)* |

All 91 navs have an About link → universal anchor for `<li><a href="/books.html">Writing</a></li>` insertion (same pattern as the earlier footer rollout, scoped to `.nav-links` not `.footer-links`).

**⚠ Decision 1 needed:** roll Writing across all 91 navs OR exclude books.html / about.html / index.html per Josh's stated "don't touch... visible content" preservation rule (88 files only, leaves those 3 pages' mobile menus visibly missing Writing).

**1.2 "All-links page"** — does NOT exist as a separate page. The unique phrase "Overlayed Echoes — the novel" appears in exactly one file: **about.html** (the `<ul class="connect-list">` at line 528). The 4 entries Josh described (YouTube → Tales of Ink, Etsy → Tynkr, Etsy → BBJ Studio, Amazon → Overlayed Echoes) match this connect-list verbatim. The URL `builtbyjoshstudio.com/al…` was a truncated `/about.html` in the browser address bar.

**⚠ Decision 2 needed:** Josh's Step 2.2 wants the Amazon entry's href changed → `/books.html`, but the entry IS about.html visible content (forbidden by preservation rule). Three options:
- (a) Minimal: just swap href, keep "Amazon" eyebrow (semantically confusing — eyebrow says Amazon but link goes to /books.html)
- (b) **Restructure (recommended)**: eyebrow `Amazon` → `Books by J.S. Warden`, link text → `Overlayed Echoes — Book One of a Five-Book Series`, href → `/books.html`. Treats /books.html as canonical destination.
- (c) Honor preservation, skip entirely.

**1.3 Footer rendering** — root cause identified: about.html is the **only** page with `flex-wrap: wrap` on `.footer-links`. Other 90 pages have inline `.footer-links { display: flex; gap: 1.5rem; list-style: none; }` without flex-wrap. Their outer-footer mobile MQ stacks the outer flex column-wise, but the inner `<ul>` still tries to fit horizontally on narrow viewports → overflow.

**Fix scope:** 1 line in `/css/tokens.css` (loaded by 92/92 HTML pages, zero existing footer rules — clean slate). Add:
```css
.footer-links { flex-wrap: wrap; }
```
The inline `<style>` rules don't set `flex-wrap` (cascades per-property), so the tokens.css rule applies on all pages without being overridden. about.html is unaffected (already has flex-wrap).

**⚠ Decision 3 needed:** confirm the 1-line tokens.css fix.

**1.4 `J. S. Warden`** — only remaining instance: this HANDOFF (documentation). 0 public-facing pages have the spaced form. Clean.

### Phase 2A brief (for reference — supplied by Josh, embedded here verbatim)

> Phase 2A — Book discoverability fixes + footer audit. Multi-issue investigation. Read-only audit first, then proposed diff, then commit only after my approval.
>
> **Problem 1** — Mobile hamburger menu missing Writing link.
> **Problem 2** — "All-links page" (Josh's screenshot: builtbyjoshstudio.com/al…) shows YouTube/Etsy/Etsy/Amazon section; Amazon entry links direct to Amazon instead of /books.html.
> **Problem 3** — Footer rendering inconsistency. About page renders correctly on mobile; other pages may overflow / wrap differently.
>
> Preservation: Josh's last name MUST NOT appear anywhere. Don't touch books.html / about.html / index.html `<head>` or visible content. Don't break the footer rollout work done earlier today.

### When Josh provides Decision 1 / 2 / 3 answers, the next steps are:

- **Decision 1 fix path:** write a sweep script (similar to `_books_footer_rollout.py` from the prior task) scoped to `<ul class="nav-links">` instead of `<ul class="footer-links">`. Same "insert after About `<li>`" rule. Root-absolute `/books.html` href.
- **Decision 2 fix path (if restructure approved):** single-file Edit on about.html connect-list `<li>` for Amazon → change eyebrow span + link text + href.
- **Decision 3 fix path:** single-file Edit on `css/tokens.css` adding 1 line.

Commit message Josh proposed: `Improve book discoverability: add Writing to mobile nav, link all-links page to /books, fix footer rendering divergence` (adjust last clause based on actual footer fix).

---

## Pre-session → current state

| Aspect | Before this session (`17c02db`) | Current (`e195a79` + audit pending) |
|---|---|---|
| HEAD | `17c02db` (HANDOFF refresh) | `e195a79` (Overlayed Echoes launch) — 7 commits later |
| GA4 e-commerce events | only `etsy_click`, `click_out_to_etsy`, `ls_checkout_open`, `lemonsqueezy_*` (custom) | + standard `view_item`, `add_to_cart`, `begin_checkout`, `purchase` site-wide; LS Setup callback wired in ga4-events.js site-wide |
| zero-based-budget-excel | tutorial-only title/H1/headline | dual template+tutorial title across SERP, H1, schema, 5 inbound cards |
| /books.html | did not exist | live; J.S. Warden fiction page; linked from About + 91 footers (not in any `.nav-links` yet) |
| Pen name spelling site-wide | mixed `J.S.` / `J. S.` | standardized `J.S. Warden` (no spaces); 0 public-facing instances of spaced form |
| Overlayed Echoes status | 85-page novella, Amazon `04YzP4o4`, no cover image | 257-page paperback+ebook, Amazon `06ZWovoY`, real cover + OG card live |
| `images/books/` | did not exist | 4 image files (cover webp/jpg, og webp/jpg) |
| Footers (`.footer-links`) | 91 pages, no Writing link | 91 pages with Writing link after About |
| Mobile nav (`.nav-links`) | 91 pages, no Writing link | unchanged — still no Writing (Phase 2A Decision 1 target) |

---

## What's live in production right now

- **/books.html** with real Overlayed Echoes cover, OG share card, 257-page paperback+ebook structured data, link to new Amazon URL
- **about.html** updated mention paragraph, updated connect-list Amazon URL (NOT yet pointing to /books.html — that's Phase 2A Decision 2)
- **Homepage** index.html sameAs JSON-LD arrays updated to new Amazon URL (zero visible content change)
- **All 91 page footers** carry "Writing" link → `/books.html`
- **GA4 funnel** firing end-to-end: `view_item` on every product/collection page load, `add_to_cart` on every buy-button click, `begin_checkout` when LS overlay opens, `purchase` on checkout success (verified live on Aquarius)
- **Sitemap.xml** has /books.html entry (priority 0.7, lastmod 2026-05-29) and about.html lastmod 2026-05-29
- **llms.txt** has /books.html under About section

---

## Open items / pending work

### ✅ DONE this session — Phase 2A book discoverability (commit `8729226`, live)

### 🟡 Deferred from prior sessions — still carry forward

1. **OG images for the remaining ~22 blog posts.** Not actively shared elsewhere; deferred.
2. **GA4 purchase event verification in Realtime dashboard.** Code is fully wired and live-verified at the dataLayer level on collection pages (commit `62b7b67`). Josh still needs to confirm the events appear in the GA4 Realtime dashboard with a real test purchase or by inspecting dataLayer.
3. **CTA copy update on product + collection pages** to lead with "Buy Direct — Instant Download" and demote Etsy to secondary. Was held off pending GA4 purchase verification; that's now in better shape.
4. **2 zodiac collections still Etsy-only** (Chinese Zodiac signs / Lunar Guardians + Zodiac Landscapes — wait, these ARE on LS per Standing #3; this open item may be stale, verify against current LS_URL_BY_* dicts).
5. **Google Merchant Center setup.** Native checkout is live; meaningfully more valuable now.
6. **Optional FAQ template paired-generator pattern for blog posts.** 6 blog posts that drifted in Phase 4 / 4.5 predated the paired-generator pattern.
7. **Book cover for Ebonspire Chronicles** — when ready, replace the `.book-cover-placeholder` div in books.html with a `<picture>` matching the Overlayed Echoes pattern (commit `e195a79` for reference).

### Untracked utility scripts this session

In `tools/` (all untracked, follow `_audit_*` / `_phase*_` convention):
- Prior session: `_audit_seo.py`, `_audit_addendum.py`, `_phase2_dates.py`, `_phase3_sitemap_images.py`, `_phase4_faq_audit.py`, `_phase4_5_inject_faq.py`, `_phase5_related_reading.py`
- **This session**: `_phase3_view_item_products.py`, `_phase4_view_item_collections.py`, `_phase6_add_category_to_checkout_config.py` (GA4 instrumentation), `_books_footer_rollout.py` (footer Writing-link rollout). No new utility scripts created in the Phase 2A audit (read-only — used inline grep/python).

---

## Critical configuration (unchanged from prior sessions)

| Item | Value |
|---|---|
| Legal entity | Built by Josh Studio LLC (Kansas) |
| Kansas Business ID | `10076138` |
| Registered Agent | Northwest Registered Agent LLC, 4601 E. Douglas Ave. STE 150, Wichita, KS 67218 (`/legal/index.html` only) |
| Email | `josh@builtbyjoshstudio.com` |
| Tynkr Tools & Co Etsy | `https://tynkrtoolsandco.etsy.com` |
| Zodiac (BBJ) Etsy | `https://www.etsy.com/shop/BuiltByJoshStudio` |
| LS store URL | `https://tynkrtoolsco.lemonsqueezy.com/` |
| GA4 Measurement ID | `G-QDSPBB7S9J` |
| Pen name (canonical) | **`J.S. Warden`** (no spaces) |
| **Overlayed Echoes Amazon URL** | **`https://a.co/d/06ZWovoY`** (paperback + ebook, 257 pages, full-length Book 1 of 5-book series) |
| Books page | `https://builtbyjoshstudio.com/books.html` |
| Pricing model | Western Signs $24.99 · Western Realms $14.99 · Chinese Signs $14.99 · Chinese Realms $29.99 · Western Landscapes $19.99 |

---

## Branches and tags

```
main                                          production — HEAD 8729226 (pushed, clean, == origin/main)
backup-after-phase-6                          8055f13 (base tag; 9 commits below current HEAD 8729226)
```

**9 commits sit above `backup-after-phase-6`:**
- `9423a02` GA4 e-commerce events + LS Setup consolidation
- `62b7b67` Collection-page LS Setup race-condition fix
- `fda6e0b` zero-based-budget-excel SERP rewrite
- `0921c2f` zero-based-budget-excel H1 alignment
- `d9484c5` /books.html + footer Writing-link rollout
- `27666ac` books.html sitemap lastmod fix
- `e195a79` Overlayed Echoes full-length launch
- `720e3e7` HANDOFF refresh (4 groups shipped, Phase 2A audit pending)
- `8729226` Phase 2A book discoverability (nav + connect-list + footer flex-wrap) ← `backup-after-book-discoverability`

Backup checkpoints this arc: `backup-pre-phase-2a` (`720e3e7`, pre-edits) and `backup-after-book-discoverability` (`8729226`, current live state). Next checkpoint before the next session's first edits.

---

## Important context (hard-won lessons this session)

- **CSS cascade is per-property, not per-rule.** Adding a single property to a shared CSS file (`tokens.css`) can fix divergent inline-`<style>` pages **as long as none of them set that specific property**. This is how the Phase 2A footer fix collapses from a 90-file sweep to a 1-line CSS change. Inspect inline rules per-property before assuming "they all override the shared file."
- **Lazy-loaded SDKs need explicit post-load hooks.** ga4-events.js's polling assumed the SDK would arrive within 5s of DOMContentLoaded. On collection pages, the SDK only loads on first click (lazy) — long after polling timed out. The fix: explicitly invoke the Setup hook from the SDK's `s.onload` after init, before the overlay opens. This is documented as Standing Instruction #15 — don't reintroduce the race.
- **"Don't touch X" rules + content that lives in X can conflict.** Phase 2A surfaced two conflicts: (a) the "all-links page" turned out to be about.html content (preservation said don't touch about.html); (b) the mobile nav fix needs to touch `.nav-links` (the source of mobile drawer items, which is per-page visible content, including on about.html / index.html / books.html). Always flag the conflict and ask, don't silently pick one side.
- **URL screenshots can lie.** Browser address bar truncation made `/about.html` look like `/al…` in Josh's screenshot. Caught by grep ("Overlayed Echoes — the novel" → 1 file only = about.html). Trust grep, not URL fragments.
- **Per-property CSS verification before global rule.** Verify the global rule won't be overridden by inline `display`/`gap`/`list-style` *also being set on the same selector* (those would be a wash unless the global rule changes one of them too). For Phase 2A footer fix, `flex-wrap` is the only new property — no override risk.
- **Pen name canonical: `J.S. Warden` (no spaces).** Standardized this session in commit `d9484c5`. The book cover art uses spaced form as a stylistic choice — that's a print-only exception. All site copy + structured data must use no-spaces form.
- **books.html footer does NOT self-link to /books.html.** Deliberate per Josh in commit `d9484c5`. The 91-footer rollout counted 91 (every existing footer-bearing HTML file) + books.html (the new file, which authored its footer WITHOUT a Writing self-link). Don't "fix" this by adding self-link — Josh has explicitly thought about it.

### Build + deploy (unchanged)
- GitHub Pages → Fastly edge (10-min TTL). Pages build: 30s–2min typically.
- Claude sessions start in `C:\Users\jotra\.claude`; `cd /c/Users/jotra/builtbyjoshstudio` for git. Bash cwd resets between calls.
- `LF will be replaced by CRLF` warnings benign. Pre-commit hook in use (passing) — never `--no-verify`.
- Local preview: `mcp__Claude_Preview__preview_start name="static-site"` (python http.server :8080). Server stops between turns.
- Python on Windows: use `python -X utf8` when reading manifests / non-ASCII content.
- For piping curl into Python via heredoc: **don't** (heredoc + curl pipe both compete for stdin). Use `curl -o tempfile.html` then read the tempfile from Python. Filename like `_v_*.html` so it's caught by the `_*` untracked-ignore pattern.

---

**End of handoff.** State: live, clean — HEAD `e195a79` on `main`, 7 feature commits since the last tagged checkpoint, Phase 2A read-only audit complete with 3 decisions pending from Josh. New session should start by reading this doc, running the verification block, then either (a) handing Josh the 3 Phase 2A decisions to make, or (b) addressing whatever Josh raises next.
