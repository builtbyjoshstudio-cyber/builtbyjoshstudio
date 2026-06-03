# builtbyjoshstudio.com — Session Handoff

**Date:** 2026-06-03 (built + shipped the **`/free/` landing section** — new hub page, 99-page nav sweep, sitemap/llms, blog CTA · preceded by a large read-only source paste-back round that fed it)
**Repo:** https://github.com/builtbyjoshstudio-cyber/builtbyjoshstudio
**Local path:** `C:\Users\jotra\builtbyjoshstudio`
**Host:** GitHub Pages — custom domain `builtbyjoshstudio.com` via CNAME → Fastly CDN (~10-min edge TTL). **No CI workflow file in the repo**; GitHub's *default* `pages-build-deployment` fires on every push to `main` (~45–70s). **There is NO branch/PR workflow — `main` IS production; pushing `main` deploys live.** (A `/create-pr` style command can't open a PR `main`→`main`; don't try. Just commit on `main` and push when Josh says.)
**HEAD (pushed):** the `/free/` work `20458de` (+ prior `da05b24`) is **pushed to `origin/main`, live, post-deploy-verified**. This HANDOFF refresh is the commit on top — **push it too** (HANDOFF is Jekyll-excluded, no live effect). **Working tree clean** (usual untracked only).
**Latest backup tag:** `backup-pre-free-nav-sweep` (`da05b24`, taken right before the 99-page sweep `--write`). Also `backup-2026-06-03` (`bc0ed00`). (Backup tags are LOCAL — `git push` doesn't carry them.)

---

## 🧭 Session summary (plain language)

Shipped the **`/free/` landing section** — the build that was queued in the prior handoff. First did a big **read-only paste-back** round (checkout.js, checkout.css, the `tokens.css` glass system + a product page's glass, the homepage `#free-tools` section, `checkout-config.js` lite SKUs) to author it against real source.

1. **New `/free/` hub** — `free/index.html` (served at `/free/`). A CollectionPage listing the free **Lite** versions of the 5 Creator OS Notion templates + both budget spreadsheets (7 cards with **live `$0` Lemon Squeezy** download buttons), **plus the 7 free cooking web tools** (the homepage `#free-tools` set, root-absolute `/images/products/*.webp`). Tynkr-cream **glass-lite** cards (`rgba(255,255,255,.48)` / `blur(14px)`) over per-section `::before` washes; `<html data-theme="light" data-glass="prototype">`; loads `/css/tokens.css`+`checkout.css`+`mobile-nav.css` and `/js/checkout-config.js`+`checkout.js`+`mobile-nav.js`+`ga4-events.js`. **Josh built the file; I placed it byte-exact** (only edited its own nav item — see #2). Schema: BreadcrumbList + CollectionPage/ItemList + the site-wide Org node (no FAQPage — no visible Q&A).
2. **Nav sweep — "Free Tools" → "Free", repointed to `/free/`.** `tools/_free_nav_sweep.py` (untracked) replaced `<a href="…index.html#free-tools">Free Tools</a>` → `<a href="/free/">Free</a>` across **99 tracked chrome pages** (7 root · 91 `../` · 1 legal root-absolute `/`). The `/free/` page's own item was set to `<a href="/free/" class="active">Free</a>`. **The homepage `<section id="free-tools">` cooking-tools grid was NOT touched** (only `<a>` nav anchors matched).
3. **blog.html tools CTA repointed** — a non-nav content CTA (`<a href="…#free-tools" class="btn-etsy">See all the free tools →</a>`) → `/free/`. Caught by a **post-write grep** (the sweep's per-file reconciliation missed it because that page *also* had the nav anchor).
4. **sitemap.xml + llms.txt** — added a `FREE` `<url>` (`/free/`, priority 0.9) after RESOURCES; added `## Free — templates and web tools` to `llms.txt` above the existing `## Free web utilities` (external tool links kept).
5. **Shipped:** commit `20458de` (102 files: new page + 99 swept + sitemap + llms) → pushed with `da05b24` → `pages-build-deployment` success → `/free/` 200, all spot-checks pass (cache-busted).

**✅ Everything above is shipped, pushed, live, post-deploy-verified. Working tree clean. No work mid-flight.**

---

## 🔴 STANDING INSTRUCTIONS — read these first

Rules Josh has set through hard pushback. Apply by default; deviate only if Josh says so explicitly.

### 1. Communication: terse, directive, no preamble.
Surface tradeoffs in 1–2 sentences and pick a default. Real ambiguity → ONE crisp question with a recommended default. No "Great, I'll start by…".

### 2. Verify against source, never assume. (Josh's #1 recurring catch.)
ChatGPT/crawlers have been **wrong many times**. **Confirm against the repo (or live bytes) before changing anything.** When a brief's premise is off, **STOP and flag**. This bit me again this session: I asserted the lite SKUs were "all pending/hidden" from a *comment* in `checkout-config.js` — they're actually **live** (real `$0` LS URLs). **Verify config VALUES, not mechanism comments.**

### 3. The site has NO template engine — pages are standalone.
Every `.html` is a complete document with its own inline `<style>`, JSON-LD, nav, and footer. **No Jekyll layouts / includes / front matter.** Site-wide change = edit a `tools/` generator and regenerate, OR a Python sweep over every `.html`. **Exception:** `/css/tokens.css` (design tokens + the `data-glass` system) is loaded by all chrome pages.

### 4. Sweep mechanics (proven).
Detect per-page **depth prefix** (root `""`, nested `../`, `legal/` root-absolute `/`), preserve **active-state**, use **block-level** replacement (minified `collections/chinese-zodiac-art.html`), **exclude** bespoke pages. Sweep scripts live as untracked `tools/_*.py`; dry-run before `--write`; reconcile the tally. **This session: `tools/_free_nav_sweep.py`** (content-matches a single anchor regardless of href prefix; uses `git ls-files` so untracked files like the new `free/index.html` are auto-excluded; per-file diff + variant tally). **Reconciliation blind spot learned:** a per-file "token present?" check misses a SECOND occurrence on a page that also has the primary match (blog.html had the nav anchor AND a body CTA). **Always re-grep the whole tree AFTER `--write`,** not just trust the dry-run tally.

### 5. Commerce — Lemon Squeezy primary, Etsy secondary.
- **Single source of truth for checkout = `/js/checkout-config.js`** — `window.CHECKOUT_CONFIG`, **8 paid + 8 lite** SKUs, each `{name, price, category, ls:<LS URL ?embed=1>, etsy:<listing>}`. Buttons use `data-checkout="<key>"`; `/js/checkout.js` wires them: paid → LS overlay on-domain; **$0 lite → LS hosted checkout (new tab, strips `?embed=1`)**; pending-paid → static Etsy fallback href; pending-lite → hidden. **Never hardcode a checkout URL outside `checkout-config.js`.** Collections use `ls-checkout-btn.js` + `data-checkout-url`.
- **The 8 lite SKUs are LIVE now ($0 lead magnets).** They carry real `$0` LS hosted-checkout URLs (e.g. `creator-finance-os-lite` → `tynkrtoolsco.lemonsqueezy.com/checkout/buy/…?embed=1`, `price:0`). `checkout.js` reveals them via the `lsLive && isFree` `wireDirectLink` path. The "Get the Lite Version — Free" sections on product pages + the 7 cards on `/free/` show download buttons. The `[data-lite-section]` wrapper still carries **inline `style="display:none"`** as the FOUC guard (CSS does *not* hide it); `checkout.js` un-hides it once a child button resolves visible. (The header comment in `checkout.js` saying "hidden by default in CSS" is imprecise — it's inline HTML + JS.)
- Etsy is never the lead CTA. **Etsy brand split (footers):** zodiac collection pages → `etsy.com/shop/BuiltByJoshStudio`; everything else → `tynkrtoolsandco.etsy.com`. Visible price/copy is hardcoded per HTML + in JSON-LD Offer + the homepage `#tynkr` card → a price change touches **3+ places**.

### 6. Identity hygiene.
"Josh" only on every public surface (never the real surname, never "Joshua"). Pen name `J.S. Warden` — **no spaces** in copy/schema. City = state-level "Kansas" only (Wichita appears only on `/legal/index.html`). Never `<meta name="keywords">`.

### 7. Founding dates (keep consistent).
Studio **started 2025** (narrative), **incorporated as Built by Josh Studio LLC in 2026**. Schema `foundingDate` = `2026-05-13`. index.html's brand node carries `2025`, its Tynkr sub-org `2026`. No bare "founded 2025" that contradicts the schema.

### 8. Site-wide Organization JSON-LD (`@id https://builtbyjoshstudio.com/#organization`) — reference, don't redefine.
Cross-link fiction pages to canonical `@id`s: author `…/books.html#jswarden`, OE Book `…/books.html#overlayed-echoes`. **Reference existing `@id`s; never redefine or invent them.** Product pages + `/free/` carry the same site-wide Org node by design.

### 9. Schema rules.
Product/collection pages: Product + Offer + FAQPage + BreadcrumbList + Organization. Blog posts: **Article** + BreadcrumbList. Fiction dispatches: **BlogPosting** (`articleSection:"Fiction"`) — never FAQPage. **`/free/`: CollectionPage + ItemList + BreadcrumbList + Org** (no FAQPage). **FAQPage must mirror visible Q&A exactly.** No `aggregateRating`/`review` anywhere. No `ReadAction`, no affiliate `tag=` params in Offer URLs.

### 10. Collection pages: edit via `tools/` generators, not by hand.
~5 generators (`build_western_signs_page.py`, `build_realm_page_master.py`, `build_chinese_animal_pages.py`, `build_chinese_realms_page.py`, `build_zodiac_landscapes_page.py`). `collections/chinese-zodiac-art.html` is the hand-written **minified** hub — block-level edits only.

### 11. Antigravity owns the cooking apps. You write blog posts about them, never the apps.
The 7 free cooking utilities are external `builtbyjoshstudio-cyber.github.io/*` apps; the homepage "Free Tools" section, **`/free/`**, and `llms.txt` link out to them.

### 12. Pages build can fail on transient infra.
Recovery: `gh run rerun <id> --failed` OR push an empty commit. **Always verify live with a cache-busted request** (`?x=<ts>`) and confirm `pages-build-deployment` shows `completed/success` before trusting live checks. `gh run watch <id> --exit-status` blocks until done.

### 13. Jekyll excludes HANDOFF in `_config.yml`.
`HANDOFF.md` + `HANDOFF-*.md` are excluded. Any new tracked top-level markdown with `{{` needs the same.

### 14. GA4 (ID `G-QDSPBB7S9J`) — only analytics installed.
Inline `gtag` snippet in **every** `<head>` + `/js/ga4-events.js`: `etsy_click` (guarded to `etsy.com` hrefs only — outbound cooking-tool / `/free/` links fire **nothing**), `__ga4LemonSqueezyHandler`, `__ga4SetupLemonSqueezy()` polling, `slugToCategory()`. `checkout.js` also fires `add_to_cart` on any `[data-checkout]` click (so `/free/`'s lite buttons DO fire add_to_cart). `ls-checkout-btn.js` (collections) lazy-loads lemon.js then Setup (race fix `62b7b67` — don't reintroduce). **Amazon click-outs:** `book_amazon_click` with `outbound:true, transport_type:'beacon'` + `source_page`/`cta_position`.

### 15. Navigation & footer are STANDARDIZED — don't let them drift.
- **Header nav (every chrome page):** `Tynkr Tools · Zodiac Art · Blog · Resources · Free · About · Writing · Legal`. Depth-aware hrefs (`../` nested, `/`-absolute for `/books.html` `/legal/` `/free/` and assets); `class="active"` per section.
- **"Free" now → `/free/`** (root-absolute) on every chrome page — **was** "Free Tools" → `index.html#free-tools`. Repointed this session via `tools/_free_nav_sweep.py` (99 pages). **`/free/index.html` marks its own item `class="active"`; no other page sets Free-active** (a later sweep could add per-section active-state for Free if wanted).
- **Footer:** section-aware slot + Home/Blog/Resources/About/Writing/Legal/Etsy/Substack/Contact/Refunds/Privacy/Terms. Etsy brand-split per #5.
- **Bespoke (excluded from sweeps):** `index.html` (bespoke footer; nav IS standard — its Free nav item WAS swept), `overlayed-echoes-preview.html` (bespoke nav+footer — has no Free item). `free/index.html` is hand-authored (excluded from the sweep; its nav item was set by hand to the active `/free/` form).

### 16. The fiction layer = `/books.html` + preview + 6 dispatches + the `/writing/` index.
- **`books.html`** (root) — J.S. Warden hub; OE Book schema has **3 editions** (see #17); rich `@id`s.
- **`overlayed-echoes-preview.html`** (root, **bespoke — excluded from sweeps**) — free Chapters 1–2, **3 CTAs**: hero + mid (end of Ch.1) + end. Hero/end use `06ZWovoY` (paperback); **mid uses Kindle `026ie1Si`**.
- **`/writing/`** — `index.html` (dispatch hub) + 6 dispatches (BlogPosting, NO FAQPage). **Unlisted in nav by design.** Built by **`tools/_build_dispatches.py`** (re-run for Stage 2).

### 17. OE facts — **THREE editions (verified — use exactly).**
*Overlayed Echoes* = near-future **LitRPG**, 257-page novel, **Book 1 of a planned 5-book series**, on Kindle + paperback + hardcover + **Kindle Unlimited**. Set 2045. NOT noir (that's Ebonspire). Pub date **2025-09-01** (print). Author store `https://www.amazon.com/stores/J.-S.-Warden/author/B0FPQ3RWWF`.

| Edition | ASIN | ISBN-13 | Price | a.co short link |
|---|---|---|---|---|
| Kindle | `B0H3826V21` | — (ebook) | $5.99 (free on KU) | `https://a.co/d/026ie1Si` |
| Paperback | `B0H39RRSNF` | 979-8199065542 | $12.99 | `https://a.co/d/0cQASed2` |
| Hardcover | `B0H3Q66YH9` | 979-8199641265 | $23.99 | `https://a.co/d/03rhvH3N` |

- **`numberOfPages:257` on PRINT editions only** (paperback + hardcover); never on the Kindle node.
- **a.co caveat:** multiple short links resolve to the **same** ASIN — the site's "canonical" OE link **`https://a.co/d/06ZWovoY` = the PAPERBACK** (`B0H39RRSNF`). Visible Amazon CTAs all use `06ZWovoY` (paperback); the books.html *schema* uses `0cQASed2` for paperback. **Resolve any a.co link to its `/dp/ASIN` before using it** (Amazon 500s the product page but returns the redirect ASIN).
- **Ebonspire Chronicles:** dark-fantasy detective noir, **releases June 2026**, unreleased (no Offer, `datePublished 2026-06`). Separate world. Pre-release treatment intact.
- **Chinese-zodiac art bundles:** $14.99 each.

### 18. Architecture quick-reference.
**101 HTML files** (was 100; added `free/index.html`): root 8 · **free 1** · products 9 · blog 34 + `blog.html` index · collections 40 (generated) · writing 7 · resources 1 · legal 1 (+10 PDFs). **No build step.** **Sitemap is MANUAL** (101 `<url>`, hand-written section comments, field order `loc→lastmod→changefreq→priority`). Images: `/images/{products,zodiac,books,logo,og}/`, **webp primary**, `loading="lazy"`, root-absolute paths. CSS = per-page inline `<style>` + 4 shared (`tokens.css` tokens/glass, `checkout.css`, `gallery.css`, `mobile-nav.css`). JS = 6 files in `/js/` + `gallery.js`. Fonts: Syne / DM Sans / JetBrains Mono (+ Cinzel/Crimson Pro where the glass system loads them).
- **`/free/` (`free/index.html`):** light Tynkr-cream **glass-lite** page. Cards = `rgba(255,255,255,.48)` + `backdrop-filter:blur(14px) saturate(130%)` + bright border, over **per-section `.free-section::before` / `.home-tools::before` washes** (glass needs a wash behind it — see the glass notes below). Lite cards use `data-checkout="<slug>-lite"` + the shared `checkout-config.js`+`checkout.js`; `[data-lite-section]` wrappers carry inline `display:none` FOUC guards. 7 cooking tools reuse the homepage `.home-tool-*` markup with root-absolute webp.
- **Glass system reference (`css/tokens.css`):** two-layer — per-page inline `<style>` = flat base surfaces; `tokens.css` `[data-glass="prototype|cosmic|books"]` rules layer the frost on top (wins by specificity). `--glass-bg`/`--glass-border` tokens are **defined but unused** (surfaces hardcode rgba); only `--rim-light`/`--nav-bg`/`--nav-border` are consumed (by `.site-nav`). Flat-bg glass-lite cards (`#tynkr .card-tynkr` .48/14px, `.home-faq-item` .55/12px) **all sit over a section `::before` wash** — there's no glass-on-truly-flat anywhere (blog cards are solid `#ffffff`, deliberately).

---

## 🟢 Status: live, clean, nothing mid-flight

Working tree clean except the usual untracked: `.claude/`, `.netlify/`, dated `HANDOFF-*.md` archives, `SITE-OVERVIEW.md`, `_audit_output.md`, and per-session `tools/_*.py` scripts — **now including `tools/_free_nav_sweep.py` (the nav sweep), plus `tools/_build_dispatches.py` / `_verify_dispatches.py`.** None are tracked; leave them or clean up at will.

---

## First steps for the new session

```bash
cd /c/Users/jotra/builtbyjoshstudio
git status                                          # clean; HEAD == origin/main
git log --oneline -12
git tag -l 'backup-*' --sort=-creatordate | head -8

# Live spot-checks (cache-busted):
ts=$(date +%s)
curl -fsS -I "https://builtbyjoshstudio.com/free/?x=$ts" | head -1                          # 200 (new hub)
curl -fsS "https://builtbyjoshstudio.com/free/?x=$ts" | grep -c 'data-checkout='            # 7 (live lite buttons)
curl -fsS "https://builtbyjoshstudio.com/blog.html?x=$ts" | grep -c 'href="/free/"'         # 2 (nav + body CTA)
curl -fsS "https://builtbyjoshstudio.com/index.html?x=$ts" | grep -c 'id="free-tools"'      # 1 (homepage section intact)
curl -fsS -I "https://builtbyjoshstudio.com/writing/?x=$ts" | head -1                       # 200 (dispatch index, prior arc)

gh run list --workflow=pages-build-deployment --limit 5    # latest completed/success
```

Then take direction from Josh. Nothing is mid-flight.

---

## Open / deferred items (nothing blocking)

- **`/free/` follow-ups (minor, optional):** the 8th lite SKU (`creator-os-full-stack-lite` sampler) is **not** featured on `/free/` (by design — page shows 5 individual Creator OS + 2 spreadsheets); add a card if wanted. "Free" nav active-state is set only on `/free/` itself — a sweep could add per-section active-state across pages. No per-page OG card for `/free/` (uses `logo.webp`).
- **Stage 2 dispatches** — `tools/_build_dispatches.py` + the `/writing/` index pattern are ready; need markdown + a thematic slug.
- **Per-dispatch OG cards** — all 6 dispatches + the preview share `images/books/og-books.jpg`.
- **Inline-breaker rollout** — the `.inline-breaker` fiction tie-in shipped on one launch post; ready for other high-impression cooking/finance posts.
- **Organization schema non-critical warnings** — Google Rich Results Test flags non-critical issues on the site-wide Org node (pre-existing, non-blocking); fixing them is a site-wide sweep.
- **Ebonspire launch (June 2026)** — flip "releases June 2026" → "available now", add its own Book + Offer with verified ASIN, mirror the 3-edition pattern.
- **Carry-forwards:** OG images for ~22 blog posts; GA4 purchase verification in Realtime; "Buy Direct — Instant Download" lead-CTA treatment; Google Merchant Center; Ebonspire cover for books.html when ready.

---

## Branches and tags

```
main    production — HEAD == origin/main (pushed, clean, live)
```

**Backup tags this arc (newest first):** `backup-pre-free-nav-sweep` (`da05b24`, pre-99-page sweep) · `backup-2026-06-03` (`bc0ed00`). Earlier arc tags (`backup-pre-inline-breaker` `450dfff`, etc.) remain. (Backup tags are LOCAL.)

**This arc's commit:** `20458de` Add /free/ hub + repoint nav 'Free Tools' → 'Free' (/free/) — 102 files (new `free/index.html` + 99 swept nav pages + `sitemap.xml` + `llms.txt`). Below it: `da05b24` (prior HANDOFF refresh, also pushed this session) · `bc0ed00` (Field-Dispatches arc tip).

---

## Hard-won lessons this arc

- **Verify config VALUES, not comments.** I asserted the lite SKUs were "pending/hidden" based on a `checkout-config.js` header comment; the actual entries carry live `$0` LS URLs and `checkout.js` reveals every lite button. The local preview screenshot caught it (buttons were visible). Read the data, not the doc-comment.
- **Sweep reconciliation has a per-occurrence blind spot.** The dry-run's "token present but unmatched: 0" check is *per file* — it can't see a SECOND occurrence on a page that already matched once (blog.html: nav anchor swept + a body CTA missed). Always re-grep the whole tree AFTER `--write`.
- **`main` is production; there is no PR flow.** A `/create-pr`-style command can't open a PR `main`→`main`, and pushing `main` deploys live. When asked to "make a PR," clarify: this repo ships by committing on `main` and pushing (on Josh's go).
- **`/free/` glass needed a section wash.** The page's frosted cards only read as glass because `.free-section::before` / `.home-tools::before` paint blurred radial washes behind them — matching the homepage `#tynkr` pattern. Flat cream + no wash = no visible frost (which is why the blog uses solid-white cards instead).
- **Place "final" files byte-exact with `cp` + `cmp`, not Write.** Josh hands a finished HTML file → copy it, verify `cmp` byte-identical, don't retype (preserves the `𝗡`/`▦`/curly-quote/arrow glyphs). Edit only the one line he authorizes (the nav item).
- **a.co short links lie about format; ChatGPT re-flags the same false positives** (the `View Collection ↗` arrow, the blog "No posts match that filter" hidden element) — don't re-fix. Commit messages via PowerShell/bash: avoid literal double-quotes in `-m` (use a here-string / `-F -`).

---

**End of handoff.** State: live, clean, HEAD == origin/main, nothing mid-flight. The `/free/` landing section is built, swept (99 pages), shipped, and post-deploy-verified; `/free/` returns 200 with live lite download buttons. New session: read this doc, run the First-Steps block, then take direction from Josh.
