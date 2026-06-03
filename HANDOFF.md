# builtbyjoshstudio.com — Session Handoff

**Date:** 2026-06-03 (Field Dispatches Stage 1 · products-hub workbooks · ChatGPT-audit fixes · preview mid-CTA · 3-edition Book schema · blog inline-breaker · + a read-only SEO/architecture audit prepping a `/free/` section)
**Repo:** https://github.com/builtbyjoshstudio-cyber/builtbyjoshstudio
**Local path:** `C:\Users\jotra\builtbyjoshstudio`
**Host:** GitHub Pages — custom domain `builtbyjoshstudio.com` via CNAME → Fastly CDN (~10-min edge TTL). **No CI workflow file in the repo**; GitHub's *default* `pages-build-deployment` fires on every push to `main` (~45–70s).
**HEAD (pushed):** `bc0ed00` on `main`, **in sync with `origin/main`**. All work committed, pushed, live, post-deploy-verified. **Working tree clean.**
**Latest backup tag:** `backup-pre-inline-breaker` (`450dfff`). Six checkpoint tags created this arc (see Branches & Tags). **Suggested:** tag `backup-2026-06-03` at `bc0ed00` before the next session's first edit. (Backup tags are LOCAL — `git push` doesn't carry them.)

---

## 🧭 Session summary (plain language)

Picked up from the prior handoff (`120148d`). Shipped **11 commits** — all committed, pushed, live, verified. Then ran several **read-only** audits (no file changes) to prep the next build.

1. **OE Field Dispatches — Stage 1 (fiction layer doubled).** Added **5 new dispatches** at `/writing/` — `directors-voice` (the game master / Kael), `counting-the-exits` (the guardian / Theo), `end-of-worry` (the medic / Angela), `no-footnotes-required` (the joker / Marcus), `the-things-i-let-go` (his sister / Lena) — five POVs of *the hour before the first session*. Built from markdown via a new generator **`tools/_build_dispatches.py`** (slices the chrome verbatim from `corruption-of-immersion.html`). Built a **`/writing/` index** grouping "The calm before" (5) / "And after" (1 = the original `corruption-of-immersion`) as two-line cards. Repointed the `books.html` OE card → `/writing/` ("From the world: field dispatches →"). Added all 6 dispatches + the index to `sitemap.xml`, and a **"Field Dispatches" section to `llms.txt`** (GEO). Commits `75dfdde · 67c5ad5 · 507d37c · 1862312`.
2. **Products hub completed + reframed.** `/products/` had listed only the 6 Creator OS Notion templates; **added the 2 spreadsheet workbooks** (Ultimate Budget, Home-Buying) as a "Spreadsheet Workbooks" section and **reframed the hub to the full Tynkr line** (eyebrow/H1/hero-sub/`<title>`/meta no longer "Notion only"). Hub workbook cards use flat **`$34.99`** to match the homepage `#tynkr` grid. Commit `8fd0fc2`.
3. **ChatGPT-audit fixes (only the verified-real subset).** Fixed **5 product-gallery typos** in visible caption + `alt` + `aria-label` + `data-caption` **and renamed the underlying `.webp` files**: `Campains→Campaigns`, `Content Caldendar→Content Calendar`, `Tax Esitmator→Tax Estimator` (the 5th — **we** caught it, ChatGPT didn't), `Sheets · First Yearpng→First Year`, `Sheets · Net Wrothpng→Net Worth`. Reframed the **products-hub Etsy-as-channel prose → buy-direct**. Cosmetics: sidebar price-note run-on `·` separator (6 creator pages), `Home Page→Homepage` (content + finance pages), Excel `Maintenance→Maintenance Reserve` (home-buying). Commits `a103f97 · af9c461 · 8bab088`.
4. **Preview mid-point CTA (Brief A Pt 1).** Added a 3rd CTA at the **end of Chapter 1** on `overlayed-echoes-preview.html` (`cta_position:"mid"`, the **Kindle** link `https://a.co/d/026ie1Si`, beacon). Extended the inline GA4 handler to honor `data-cta-position` (hero/end behavior byte-unchanged). Verified at gtag/dataLayer level. Commit `14632ef`.
5. **books.html Book schema → 3 editions (Brief B).** Replaced the single OE `Book`+`Offer` with a `Book` carrying **3 `workExample` editions** (Kindle/Paperback/Hardcover) + verified ASIN/ISBN/price. **Kept the canonical `#jswarden` author `@id`** (the brief proposed a new `#author` — rejected; would have orphaned every existing reference). Commit `450dfff`.
6. **Blog inline-breaker (Brief A Pt 2).** A native fiction case-study blockquote (`.inline-breaker`) in `blog/how-to-launch-digital-product-without-audience.html` → `/books.html`. Pattern proven, repeatable. Commit `bc0ed00`.
7. **Read-only audits (no changes):** debunked two **repeat** ChatGPT false-positives; clarified the `/products/` IA; produced a full **SEO/architecture audit** and pasted exact source files — all **prepping a planned `/free/` landing section** (the most likely next build). Also wrote `Downloads\overlayed-echoes-dispatches-briefing.md` (a context doc — NOT in the repo).

**✅ Everything above is shipped and live-verified. No work is mid-flight. Working tree clean.**

---

## 🔴 STANDING INSTRUCTIONS — read these first

Rules Josh has set through hard pushback. Apply by default; deviate only if Josh says so explicitly.

### 1. Communication: terse, directive, no preamble.
Surface tradeoffs in 1–2 sentences and pick a default. Real ambiguity → ONE crisp question with a recommended default. No "Great, I'll start by…".

### 2. Verify against source, never assume. (Josh's #1 recurring catch.)
ChatGPT/crawlers have been **wrong many times** (claimed a short nav that didn't exist; "Etsy-primary" buttons that JS-rewire to Lemon Squeezy; a "hidden character" before `View Collection ↗` that is just the arrow; a blog "No posts match that filter" that is a `hidden` element). **Confirm against the repo (or the live bytes) before changing anything.** When a brief's premise is off, **STOP and flag** — don't build on it.

### 3. The site has NO template engine — pages are standalone.
Every `.html` is a complete document with its own inline `<style>`, JSON-LD, nav, and footer. **No Jekyll layouts / includes / front matter** (Jekyll just passes files through). Site-wide change = edit a `tools/` generator and regenerate, OR a Python sweep over every `.html`. **Exception:** `/css/tokens.css` (design tokens + the `data-glass` system) is loaded by all chrome pages; cross-cutting CSS that doesn't collide with a per-page inline property can live there.

### 4. Sweep mechanics (proven).
Detect per-page **depth prefix** (root `""`, nested `../`, `legal/` uses root-absolute `/`), preserve per-page **active-state**, use **block-level** replacement (not line-based — minified `collections/chinese-zodiac-art.html`), **exclude** bespoke pages. Sweep scripts live as untracked `tools/_*.py`; dry-run before `--write`; reconcile the tally.

### 5. Commerce — Lemon Squeezy primary, Etsy secondary.
- **Single source of truth for checkout = `/js/checkout-config.js`** — `window.CHECKOUT_CONFIG`, **8 paid + 8 lite** SKUs, each `{name, price, category, ls:<LS overlay URL ?embed=1>, etsy:<listing>}`. Buttons use `data-checkout="<key>"`; `/js/checkout.js` wires them: paid → LS overlay on-domain; **$0 lite → LS hosted checkout (new tab, strips `?embed=1`)**; pending-paid → static Etsy fallback href; pending-lite → hidden. **Never hardcode a checkout URL outside `checkout-config.js`.** Collection pages use a parallel path (`ls-checkout-btn.js` + `data-checkout-url`).
- **Lite versions have NO standalone pages** — they're the "Get the Lite Version — Free" sections on each product page (`data-checkout="<slug>-lite"`, hidden via `data-lite-section`/`style=display:none` until live). (`blog/what-lite-actually-means.html` only *explains* the concept.)
- Etsy is never the lead CTA / never "sold on Etsy" as the channel. **Etsy brand split (footers):** zodiac collection pages → `etsy.com/shop/BuiltByJoshStudio`; everything else → `tynkrtoolsandco.etsy.com`. Visible price/copy is **also** hardcoded per HTML + in each page's JSON-LD Offer + the homepage `#tynkr` card → a price change touches **3+ places**.

### 6. Identity hygiene.
"Josh" only on every public surface (never the real surname, never "Joshua"). Pen name `J.S. Warden` — **no spaces** in copy/schema (cover art's spaced `J. S. Warden` is print-only). City = state-level "Kansas" only (Wichita appears only on `/legal/index.html`). Never `<meta name="keywords">`.

### 7. Founding dates (keep consistent).
Studio **started 2025** (narrative voice), **incorporated as Built by Josh Studio LLC in 2026**. Schema `foundingDate` = `2026-05-13`. index.html's brand node carries `2025`, its Tynkr sub-org `2026` — both correct. No bare "founded 2025" that contradicts the schema.

### 8. Site-wide Organization JSON-LD (`@id https://builtbyjoshstudio.com/#organization`) — reference, don't redefine.
Cross-link fiction pages to canonical `@id`s: author `https://builtbyjoshstudio.com/books.html#jswarden`, OE Book `…/books.html#overlayed-echoes`. **Reference existing `@id`s; never redefine or invent them.** (A brief this arc proposed a new `#author` — rejected, kept `#jswarden`.) Note: product pages carry a *separate, page-local* Org node (Tynkr Tools & Co with `parentOrganization` Built By Josh Studio) — that's by design, distinct from `#organization`.

### 9. Schema rules.
Product/collection pages: Product + Offer + FAQPage + BreadcrumbList + Organization. Blog posts: **Article** + BreadcrumbList (+ often a related Product Offer; legacy tool posts keep old WebApplication blocks — leave alone). Fiction dispatches: **BlogPosting** (`articleSection:"Fiction"`) — **never FAQPage**. **FAQPage must mirror visible Q&A exactly; never fake it.** No `aggregateRating`/`review` anywhere (no real reviews yet). No `ReadAction`, no affiliate `tag=` params in Offer URLs.

### 10. Collection pages: edit via `tools/` generators, not by hand.
~5 generators (`build_western_signs_page.py`, `build_realm_page_master.py`, `build_chinese_animal_pages.py`, `build_chinese_realms_page.py`, `build_zodiac_landscapes_page.py`). `collections/chinese-zodiac-art.html` is the hand-written **minified** hub — block-level edits only.

### 11. Antigravity owns the cooking apps. You write blog posts about them, never the apps.
The 7 free cooking utilities are external `builtbyjoshstudio-cyber.github.io/*` apps; the homepage "Free Tools" + `llms.txt` link out to them.

### 12. Pages build can fail on transient infra.
Recovery: `gh run rerun <id> --failed` OR push an empty commit. **Always verify live with a cache-busted request** (`?x=<ts>`) and confirm `pages-build-deployment` shows `completed/success` before trusting live checks. `gh run watch <id> --exit-status` blocks until done.

### 13. Jekyll excludes HANDOFF in `_config.yml`.
`HANDOFF.md` + `HANDOFF-*.md` are excluded (literal `{{` would choke Liquid). Any new tracked top-level markdown with `{{` needs the same.

### 14. GA4 (ID `G-QDSPBB7S9J`) — only analytics installed.
Inline `gtag` snippet in **every** `<head>` + `/js/ga4-events.js` (all pages): `etsy_click`, `__ga4LemonSqueezyHandler`, `__ga4SetupLemonSqueezy()` polling, `slugToCategory()`. `window.__ga4LemonSqueezySetupDone` guards double-wiring. `ls-checkout-btn.js` (collections) lazy-loads lemon.js then calls Setup before opening (race fix `62b7b67` — don't reintroduce). `checkout.js` (product pages) only calls `LemonSqueezy.Refresh()` + fires `add_to_cart`; product pages also have inline `view_item` + Etsy click-out scripts. **Funnel precedent:** outbound Amazon clicks → `book_amazon_click` with `outbound:true, transport_type:'beacon'` + a `source_page`/`cta_position` param.

### 15. Navigation & footer are STANDARDIZED — don't let them drift.
- **Header nav (every chrome page):** `Tynkr Tools · Zodiac Art · Blog · Resources · Free Tools · About · Writing · Legal`. Depth-aware hrefs (`../` nested, `/`-absolute for `/books.html` `/legal/` and assets); `class="active"` per section. **"Free Tools" currently → `index.html#free-tools`** (homepage anchor) on every page — repointing it is a ~93-page Python sweep.
- **Footer:** section-aware slot (collections→Collections, products→Products, resources/blog omit) + Home/Blog/Resources/About/Writing/Legal/Etsy/Substack/Contact/Refunds/Privacy/Terms. Etsy brand-split per #5.
- **Bespoke (excluded from sweeps):** `index.html` (bespoke footer; nav IS standard), `overlayed-echoes-preview.html` (bespoke nav+footer).

### 16. The fiction layer = `/books.html` + preview + 6 dispatches + the `/writing/` index.
- **`books.html`** (root) — J.S. Warden hub; OE Book schema now has **3 editions** (see #17); rich `@id`s (`#jswarden`/`#overlayed-echoes`/`#ebonspire-chronicles`).
- **`overlayed-echoes-preview.html`** (root, **bespoke — excluded from sweeps**) — free Chapters 1–2, 900px reader, Book-as-free-sample schema, **3 CTAs**: hero + **mid (end of Ch.1)** + end. Hero/end use `06ZWovoY` (paperback); **mid uses the Kindle `026ie1Si`** (mixed targets, intentional). Inline GA4 handler keys `cta_position` off `data-cta-position` then `.sample-end`.
- **`/writing/`** — `index.html` (the dispatch hub) + 6 dispatches. Each dispatch = books-glass skin, BlogPosting schema (NO FAQPage), unique GA4 `source_page=dispatch-<slug>`, soft diegetic CTAs. **Unlisted in nav by design.** Built by **`tools/_build_dispatches.py`** (the canonical generator; re-run for Stage 2 — edit `PAGES`/`GROUP_*` + drop markdown in `Downloads\Overlayed Echoes Dispatch Files Stage 1\`). The `corruption-of-immersion` dispatch is the original "after" piece; the other 5 are "the hour before."

### 17. OE facts — **THREE editions now (verified this arc — use exactly).**
*Overlayed Echoes* = near-future **LitRPG** (also GameLit / Science Fiction / Metafiction), 257-page novel, **Book 1 of a planned 5-book series**, on Kindle + paperback + hardcover + **Kindle Unlimited**. Set 2045; neural chips make tabletop RPG real. NOT noir (that's Ebonspire). Pub date **2025-09-01** (print). Author store `https://www.amazon.com/stores/J.-S.-Warden/author/B0FPQ3RWWF`.

| Edition | ASIN | ISBN-13 | Price | a.co short link |
|---|---|---|---|---|
| Kindle | `B0H3826V21` | — (ebook) | $5.99 (free on KU) | `https://a.co/d/026ie1Si` |
| Paperback | `B0H39RRSNF` | 979-8199065542 | $12.99 | `https://a.co/d/0cQASed2` |
| Hardcover | `B0H3Q66YH9` | 979-8199641265 | $23.99 | `https://a.co/d/03rhvH3N` |

- **`numberOfPages:257` on PRINT editions only** (paperback + hardcover); never on the Kindle node.
- **a.co caveat (bit us this arc):** multiple short links can resolve to the **same** ASIN — the site's long-standing "canonical" OE link **`https://a.co/d/06ZWovoY` = the PAPERBACK** (`B0H39RRSNF`, same product as `0cQASed2`). The site's *visible* Amazon CTAs (books.html, preview hero/end, dispatches, homepage) all use `06ZWovoY` (paperback); the books.html *schema* uses `0cQASed2` for paperback (same product, different short link). **Before using any a.co link in copy/schema, resolve it to its `/dp/ASIN`** (Amazon 500s on product-page fetch but returns the redirect ASIN — that's enough).
- **Ebonspire Chronicles:** dark-fantasy detective noir, **releases June 2026**, unreleased (no Offer, `datePublished 2026-06`). Separate world. **Not touched this arc** — pre-release treatment intact.
- **Chinese-zodiac art bundles:** $14.99 each.

### 18. Architecture quick-reference (from this arc's read-only SEO audit — for the `/free/` build).
100 HTML files: root 8 · products 9 (8 + index) · blog **34 real posts** · collections 40 (generated) · writing 7 · resources 1 · legal 1 (+10 PDFs). **No build step** (no package.json/netlify/Gemfile). **Sitemap is MANUAL** (100 `<url>`, hand-written section comments, field order `loc→lastmod→changefreq→priority`). Images: `/images/{products,zodiac,books,logo,og}/`, **webp primary** (product hero `/images/products/<slug>.webp` 1600², gallery `/images/products/additional/<slug>-<label>.webp`), `<picture>` webp+jpg on covers, `loading="lazy" decoding="async"`, alt inline, root-absolute paths. CSS = per-page big inline `<style>` + 4 shared (`tokens.css` design tokens/glass, `checkout.css`, `gallery.css`, `mobile-nav.css`); no framework; classes are page-type-specific. JS = 6 files in `/js/` (see #5/#14) + `gallery.js`. Fonts: Syne (display) / DM Sans (body) / JetBrains Mono (numerics).

---

## 🟢 Status: live, clean, nothing mid-flight

Working tree clean except the usual untracked: `.claude/`, `.netlify/`, dated `HANDOFF-*.md` archives, `SITE-OVERVIEW.md`, `_audit_output.md`, and per-session `tools/_*.py` scripts — **now including `tools/_build_dispatches.py` and `tools/_verify_dispatches.py` (the dispatch generator + validator — keep untracked per convention; they reproduce `/writing/`).** None are tracked; leave them or clean up at will.

---

## First steps for the new session

```bash
cd /c/Users/jotra/builtbyjoshstudio
git status                                          # clean; HEAD bc0ed00 == origin/main
git log --oneline -12
git tag -l 'backup-*' --sort=-creatordate | head -8

# Live spot-checks (cache-busted):
ts=$(date +%s)
curl -fsS -I "https://builtbyjoshstudio.com/writing/?x=$ts" | head -1                                  # 200 (dispatch index)
curl -fsS "https://builtbyjoshstudio.com/products/?x=$ts" | grep -c "Spreadsheet Workbooks"            # 1 (hub now has workbooks)
curl -fsS "https://builtbyjoshstudio.com/books.html?x=$ts" | grep -c "workExample"                     # 1 (3-edition OE schema)
curl -fsS "https://builtbyjoshstudio.com/overlayed-echoes-preview.html?x=$ts" | grep -c 'data-cta-position="mid"'  # 1 (mid CTA)
curl -fsS "https://builtbyjoshstudio.com/blog/how-to-launch-digital-product-without-audience.html?x=$ts" | grep -c "inline-breaker"  # 3

gh run list --workflow=pages-build-deployment --limit 5    # latest completed/success
```

Then take direction from Josh. **The most likely next build is a new `/free/` landing section** (see Open items) — this session's SEO/architecture audit + the pasted source of the clone base, a product page's lite/buy markup, `checkout-config.js` lite SKUs, a blog Article pattern, the sitemap structure, llms.txt, and both nav depth-variants were all gathered specifically to author it. Nothing is started or committed for `/free/` yet.

---

## Open / deferred items (nothing blocking)

- **`/free/` landing section (the queued next build).** Net-new section. **Create** `free/index.html` (clone `resources/index.html` for the shell; if it lists the free Lite products, use `data-checkout="<slug>-lite"` buttons + include `checkout-config.js`+`checkout.js`; the 8 lite keys are in #5). **Edit to wire it in:** `sitemap.xml` (+1 url), the **"Free Tools" nav item across ~93 pages** (Python sweep; repoint `index.html#free-tools` → `/free/`, root-absolute is simplest), `index.html` `#free-tools` section + homepage footer, `llms.txt`. No robots change needed (`/free/` allowed). Decide whether `/free/` replaces or supplements the external cooking-tool links.
- **Stage 2 dispatches** — `tools/_build_dispatches.py` + the index pattern are ready; new ones need markdown + a thematic slug (index would extend, maybe a 3rd group).
- **Per-dispatch OG cards** — all 6 dispatches + the preview share `images/books/og-books.jpg`.
- **Inline-breaker rollout** — the `.inline-breaker` fiction tie-in shipped on one launch post; ready for other high-impression cooking/finance posts (internal link → `/books.html`, first-person, no surname, claim capped at "launched on KU without a big list").
- **Organization schema non-critical warnings** — Google Rich Results Test flags non-critical issues on the site-wide Org node (pre-existing, non-blocking); fixing them is a site-wide sweep (the Org block is duplicated per page). (Note: Rich Results Test does **not** surface a generic `Book` — that's expected; use validator.schema.org to validate the OE Book + 3 editions.)
- **Ebonspire launch (June 2026)** — flip "releases June 2026" → "available now", add its own Book + Offer with verified ASIN, mirror the 3-edition pattern.
- **Carry-forwards (still open):** OG images for ~22 blog posts; GA4 purchase verification in Realtime; "Buy Direct — Instant Download" lead-CTA treatment; Google Merchant Center; Ebonspire cover for books.html when ready.

---

## Branches and tags

```
main    production — HEAD bc0ed00 (pushed, clean, == origin/main)
```

**Backup tags this arc (newest first):** `backup-pre-inline-breaker` (450dfff) · `backup-pre-book-schema-sweep` (14632ef) · `backup-pre-midpoint-cta` (8fd0fc2) · `backup-pre-products-workbooks` (8bab088) · `backup-pre-typo-fixes` (1862312) · `backup-2026-06-02` (120148d). Earlier arc tags (`backup-pre-footer-sweep`, etc.) remain. **Suggested:** tag `backup-2026-06-03` at `bc0ed00` before the next edit. (Backup tags are LOCAL.)

**11 commits this arc (newest first):** `bc0ed00` blog inline-breaker · `450dfff` 3-edition Book schema · `14632ef` preview mid-CTA · `8fd0fc2` products-hub workbooks + reframe · `8bab088` cosmetics (price-note run-on + label normalize) · `af9c461` hub Etsy→buy-direct · `a103f97` 5 gallery typos (rename webp + refs) · `1862312` llms Field Dispatches · `507d37c` /writing/ index redesign · `67c5ad5` /writing/ index copy polish · `75dfdde` Stage 1 dispatches + /writing/ index. (`120148d` HANDOFF refresh was the prior HEAD.)

---

## Hard-won lessons this arc

- **a.co short links lie about format.** Several short links resolve to the **same** ASIN, and the site's "canonical" OE link `06ZWovoY` is the **paperback**, not Kindle. Always resolve `a.co/d/X` → `/dp/ASIN` before trusting it (WebFetch returns the redirect ASIN even though Amazon 500s the product page).
- **ChatGPT re-flags the same false positives.** The `View Collection ↗` "hidden character" (just the U+2197 arrow; byte-verified clean ×48) and the blog "No posts match that filter" (a `hidden` element only shown on a zero-result filter) are **not real** and were re-flagged a second time. Don't re-fix. Conversely, **we** caught a typo ChatGPT missed (`Tax Esitmator`) — verify breadth; the crawler isn't exhaustive either.
- **Briefs carry wrong premises.** Stop-and-flag examples this arc: a new `#author` `@id` (would orphan refs → kept `#jswarden`); "two confirmed links" that were actually **three different ASINs**; a brief assuming homepage `#tynkr` cards had `data-checkout` when they're "View Product →" nav links. The premise being off is the discrepancy — flag before building.
- **Google Rich Results Test only shows rich-result-eligible types.** A valid schema.org `Book` won't appear (Google's only "Book" is the gated Book Actions program). FAQ/Breadcrumb/Org do. Use validator.schema.org for the rest.
- **Render-check before commit catches CSS bleed.** The preview's drop-cap rule (`.reader p:first-of-type::first-letter`) bled an oversized initial onto the inserted mid-CTA line; needed a higher-specificity `::first-letter` reset (the notebook block uses the same trick).
- **The preview MCP** (`preview_start`/`preview_eval`/`preview_screenshot`, server name `static-site` on :8080 from `.claude/launch.json`) is ideal for **gtag/dataLayer verification** (wrap `gtag`, dispatch a click, read params) and scroll-to-element screenshots — but it's **sandboxed to localhost** (can't navigate to the live domain; verify live via cache-busted `curl` instead).
- **Commit messages via PowerShell:** avoid literal double-quotes in `git commit -m` (use a bash here-string / `-F -`). Verification greps with parens/quotes can break the bash parser — keep them simple.

---

**End of handoff.** State: live, clean, HEAD `bc0ed00` == origin/main, nothing mid-flight. The Field-Dispatches Stage-1, products-hub-completion, audit-fix, preview-CTA, 3-edition-schema, and inline-breaker arcs are complete and verified. New session: read this doc, run the First-Steps block, then take direction from Josh — the queued next build is the `/free/` section.
