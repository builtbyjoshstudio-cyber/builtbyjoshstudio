# builtbyjoshstudio.com — Session Handoff

**Date:** 2026-06-03 (three arcs: **`/free/` landing section** · **blog-copy "no-email" cleanup** on the free-template posts · **Notion-OS blog buy-button + schema repoint** Etsy → on-site product pages, plus upgrade-code "on Etsy" prose neutralized)
**Repo:** https://github.com/builtbyjoshstudio-cyber/builtbyjoshstudio
**Local path:** `C:\Users\jotra\builtbyjoshstudio`
**Host:** GitHub Pages — custom domain `builtbyjoshstudio.com` via CNAME → Fastly CDN (~10-min edge TTL). **No CI workflow file in the repo**; GitHub's *default* `pages-build-deployment` fires on every push to `main` (~45–70s). **There is NO branch/PR workflow — `main` IS production; pushing `main` deploys live.** (A `/create-pr` style command can't open a PR `main`→`main`; don't try. Commit on `main`, push when Josh says.)
**HEAD:** all three arcs are **pushed to `origin/main`, live, post-deploy-verified** — last live commit **`945e528`** (Notion-OS repoint). This HANDOFF refresh is the commit on top — **unpushed** (HANDOFF is Jekyll-excluded, no live effect); first-steps will show `[ahead 1]`. **Ask Josh whether to push it.** Working tree otherwise clean (usual untracked only).
**Latest backup tag:** `backup-pre-free-nav-sweep` (`da05b24`) · `backup-2026-06-03` (`bc0ed00`). No new backup tags for the two blog-copy arcs (used dry-run scripts + git for safety). (Backup tags are LOCAL — `git push` doesn't carry them.)

---

## 🧭 Session summary (plain language)

Three shipped arcs, all live-verified. Each was preceded by careful read-only source paste-back, and Josh reviewed diffs before every commit.

**Arc 1 — `/free/` landing section (commit `20458de`, pushed with `da05b24`).**
1. New `free/index.html` (served `/free/`): CollectionPage of the free **Lite** versions (5 Creator OS + 2 budget spreadsheets, 7 cards with **live `$0` Lemon Squeezy** download buttons) **plus the 7 free cooking web tools**. Tynkr-cream **glass-lite** cards over per-section `::before` washes; `<html data-theme="light" data-glass="prototype">`. Josh built it; I placed it byte-exact (only edited its own nav item).
2. Nav sweep "Free Tools" → "Free" → `/free/` across **99 tracked chrome pages** via `tools/_free_nav_sweep.py` (untracked). The homepage `<section id="free-tools">` cooking grid was NOT touched.
3. `blog.html` tools CTA → `/free/`; `sitemap.xml` +FREE url; `llms.txt` +"## Free — templates and web tools".

**Arc 2 — blog "no-email" copy cleanup (commits `2196d80` + `1ba5b99`).** The `/free/` lite download is a **$0 LS purchase that captures an email** (Josh confirmed: email required for the *purchase* only; the free cooking tools need no email). So the four free-template posts' standing "no email / no signup / not behind an email gate / lead-capture form" body claims were **removed entirely** (not reworded) and pointed at `../free/` where relevant:
- `free-budget-spreadsheet-excel-google-sheets.html`, `free-home-buying-spreadsheet-mortgage-affordability.html`: FAQ "actually free?" answer → `../free/` link (visible `<p>` **and** the mirrored JSON-LD `acceptedAnswer.text` — #9), email-gate wording dropped; plus a missed body paragraph in free-home-buying (`No email gate. No lead capture…`) caught by the **live re-sweep**.
- `free-notion-templates-creators-no-email.html`: post-summary + intro stripped of no-email/no-signup; "How to Get" Lemon Squeezy bullet → `../free/`.
- `what-lite-actually-means.html`: stale "free on Lemon Squeezy once approved" → "free to download on this site".
- Related-post teaser cards across the four ("no signup required" / "no lead capture") also stripped.

**Arc 3 — Notion-OS blog buy-button + schema repoint (commit `945e528`).** Decision: blog-post buy buttons point to the **on-site `/products/<slug>.html`** pages (the product page's own buttons do the LS-overlay checkout). Applied via `tools/_etsy_repoint.py` (untracked, match-checked, 42 replacements / 11 files, 0 misses):
- **B:** the 6 Notion-OS posts' two buy anchors (`btn-inline-etsy`/`btn-etsy`) Etsy listing → `../products/<slug>.html` (dropped `target="_blank"`, relabeled **Get/View `<Product>`**); complete-notion's 5 "related templates" links repointed too.
- **C:** same 6 posts' JSON-LD Product + Offer `"url"` Etsy listing → `https://builtbyjoshstudio.com/products/<slug>.html`.
- **D:** `"35% off the full version on Etsy"` → `"…full version"` across free-budget/free-home-buying/free-notion/what-lite/30-minute (FAQ + JSON-LD mirrors synced); free-budget upgrade step → `"Apply it at checkout."`.
- **E:** 30-minute stale `"free on Lemon Squeezy once that store is live/approved"` → `"free on this site"`.

**✅ All three arcs shipped, pushed, live, post-deploy-verified. Working tree clean. No work mid-flight.** (Josh was doing a final manual click-through of the repointed buy buttons at session end — expected fine; the automated live re-sweep was all green.)

---

## 🔴 STANDING INSTRUCTIONS — read these first

Rules Josh has set through hard pushback. Apply by default; deviate only if Josh says so explicitly.

### 1. Communication: terse, directive, no preamble.
Surface tradeoffs in 1–2 sentences and pick a default. Real ambiguity → ONE crisp question with a recommended default. No "Great, I'll start by…".

### 2. Verify against source, never assume. (Josh's #1 recurring catch.)
**Confirm against the repo (or live bytes) before changing anything.** When a premise is off, **STOP and flag**. Bit me twice this session: (a) asserted the lite SKUs were "pending/hidden" from a `checkout-config.js` *comment* — they're **live** (real `$0` LS URLs); (b) told Josh the no-email claim "only sat on one bullet" — it was **page-wide** (title/H1/meta + intro). **Verify config VALUES and full coverage, not comments or first-read assumptions.** Also: when re-applying anything, prove the prior commit is actually live first (grep old strings → none; `git merge-base --is-ancestor <sha> origin/main`).

### 3. The site has NO template engine — pages are standalone.
Every `.html` is a complete document with its own inline `<style>`, JSON-LD, nav, footer. **No Jekyll layouts/includes/front matter.** Site-wide change = edit a `tools/` generator and regenerate, OR a Python sweep over every `.html`. **Exception:** `/css/tokens.css` (design tokens + the `data-glass` system) is loaded by all chrome pages.

### 4. Sweep mechanics (proven) — prefer a match-checked `tools/_*.py` script for multi-file edits.
Detect per-page depth prefix (root `""`, nested `../`, `legal/` root-absolute `/`); preserve active-state; block-level replacement (minified `collections/chinese-zodiac-art.html`); exclude bespoke pages. Sweep scripts live as **untracked `tools/_*.py`**; **dry-run before `--write`**; **reconcile the tally** (count replacements per old-string; 0 = MISS → fix). This session: `tools/_free_nav_sweep.py` (nav, 99 pages) and `tools/_etsy_repoint.py` (Notion-OS repoint, 42 replacements / 11 files, each old-string match-counted). **Always re-grep the WHOLE tree (and the LIVE site, cache-busted) AFTER `--write`** — a per-file "token present?" check misses a 2nd occurrence on a page (blog.html nav+CTA; free-home-buying:484 body paragraph both slipped a first pass and were caught by post-write/live greps).

### 5. Commerce — Lemon Squeezy primary, Etsy secondary.
- **Single source of truth for checkout = `/js/checkout-config.js`** — `window.CHECKOUT_CONFIG`, **8 paid + 8 lite** SKUs, each `{name, price, category, ls:<LS URL ?embed=1>, etsy:<listing>}`. Product-page buttons use `data-checkout="<key>"`; `/js/checkout.js` wires them: paid → LS overlay on-domain; **$0 lite → LS hosted checkout (new tab, strips `?embed=1`)**; pending → Etsy fallback or hidden. **Never hardcode a checkout URL outside `checkout-config.js`.** Collections use `ls-checkout-btn.js` + `data-checkout-url`.
- **The 8 lite SKUs are LIVE ($0 lead magnets) — and the $0 download CAPTURES AN EMAIL** (it's a $0 LS *purchase*; Josh: "email required for the purchase only"). The **free cooking tools need NO email**. So "no email" is true for the Notion-Marketplace path + the cooking tools, **but NOT for the on-site `/free/` lite download**. Don't write "no email" copy about the Lite downloads (cleaned this session — see Open items for the remaining metadata).
- **Blog-post buy buttons now point to the on-site `/products/<slug>.html` pages** (repointed this session, `945e528`) — NOT to Etsy, NOT directly to the LS overlay. The product page's own buttons run the LS-overlay checkout; the upgrade code is entered **in that overlay at checkout on-site, NOT on Etsy**. So blog/upgrade copy must say "Apply it at checkout" / "35% off the full version" (no platform named), never "…on Etsy".
- **`btn-etsy` / `btn-inline-etsy` is a shared orange-CTA style, NOT Etsy-only** — several posts use it for on-site `../products/…` links. Keep the class when repointing; don't assume the class implies an Etsy destination.
- Etsy is never the lead CTA. **Etsy brand split (footers):** zodiac collection pages → `etsy.com/shop/BuiltByJoshStudio`; everything else → `tynkrtoolsandco.etsy.com`. Visible price/copy is hardcoded per HTML + JSON-LD Offer + the homepage `#tynkr` card → a price change touches **3+ places**.

### 6. Identity hygiene.
"Josh" only (never the real surname, never "Joshua"). Pen name `J.S. Warden` — **no spaces** in copy/schema. City = state-level "Kansas" only (Wichita only on `/legal/index.html`). Never `<meta name="keywords">`.

### 7. Founding dates.
Studio **started 2025** (narrative), **incorporated as Built by Josh Studio LLC in 2026**. Schema `foundingDate` = `2026-05-13`. index.html brand node `2025`, Tynkr sub-org `2026`. No bare "founded 2025" contradicting the schema.

### 8. Site-wide Organization JSON-LD (`@id …/#organization`) — reference, don't redefine.
Cross-link fiction pages to canonical `@id`s: author `…/books.html#jswarden`, OE Book `…/books.html#overlayed-echoes`. **Reference existing `@id`s; never redefine/invent.** Product pages + `/free/` carry the same site-wide Org node by design.

### 9. Schema rules — and FAQ/Offer mirrors must stay in sync with visible copy.
Product/collection: Product + Offer + FAQPage + BreadcrumbList + Organization. Blog posts: **Article** + BreadcrumbList (+ a related Product/Offer). Fiction dispatches: **BlogPosting** — never FAQPage. **`/free/`: CollectionPage + ItemList + BreadcrumbList + Org.** No `aggregateRating`/`review`, no `ReadAction`, no affiliate `tag=`.
- **FAQPage `acceptedAnswer.text` mirrors the visible `<p>` byte-for-byte** — edit a visible FAQ answer and you MUST make the identical edit to the JSON-LD copy (the Edit tool's "Found 2 matches" is the tell). Same for any **Offer/Product `"url"`** that mirrors a visible buy link.

### 10. Collection pages: edit via `tools/` generators, not by hand.
~5 generators (`build_western_signs_page.py`, `build_realm_page_master.py`, `build_chinese_animal_pages.py`, `build_chinese_realms_page.py`, `build_zodiac_landscapes_page.py`). `collections/chinese-zodiac-art.html` = hand-written **minified** hub — block-level edits only.

### 11. Antigravity owns the cooking apps. You write blog posts about them, never the apps.
The 7 free cooking utilities are external `builtbyjoshstudio-cyber.github.io/*` apps; the homepage "Free Tools" section, **`/free/`**, and `llms.txt` link out to them. (These genuinely need **no email** — see #5.)

### 12. Pages build can fail on transient infra.
Recovery: `gh run rerun <id> --failed` OR push an empty commit. **Always verify live with a cache-busted request** (`?x=<ts>`) and confirm `pages-build-deployment` `completed/success` before trusting live checks. `gh run watch <id> --exit-status` blocks. (The Node-20-deprecation annotation on every run is benign — it's GitHub's default action infra, we have no workflow file.)

### 13. Jekyll excludes HANDOFF in `_config.yml`.
`HANDOFF.md` + `HANDOFF-*.md` excluded. Any new tracked top-level markdown with `{{` needs the same.

### 14. GA4 (ID `G-QDSPBB7S9J`) — only analytics installed.
Inline `gtag` in **every** `<head>` + `/js/ga4-events.js`: `etsy_click` (guarded to `etsy.com` hrefs only — cooking-tool/`/free/` and now the repointed blog→product links fire **nothing**), `__ga4LemonSqueezyHandler`, `__ga4SetupLemonSqueezy()` polling. `checkout.js` fires `add_to_cart` on any `[data-checkout]` click (product pages + `/free/` lite buttons). `ls-checkout-btn.js` (collections) race fix `62b7b67` — don't reintroduce. **Amazon click-outs:** `book_amazon_click` `outbound:true, transport_type:'beacon'`.

### 15. Navigation & footer are STANDARDIZED — don't let them drift.
- **Header nav (every chrome page):** `Tynkr Tools · Zodiac Art · Blog · Resources · Free · About · Writing · Legal`. Depth-aware hrefs; `class="active"` per section.
- **"Free" → `/free/`** (root-absolute) on every chrome page (was "Free Tools" → `index.html#free-tools`). `/free/index.html` marks its own item `class="active"`; no other page sets Free-active.
- **Footer:** section-aware slot + Home/Blog/Resources/About/Writing/Legal/Etsy/Substack/Contact/Refunds/Privacy/Terms. Etsy brand-split per #5.
- **Bespoke (excluded from sweeps):** `index.html` (bespoke footer; nav IS standard), `overlayed-echoes-preview.html` (bespoke nav+footer), `free/index.html` (hand-authored).

### 16. The fiction layer = `/books.html` + preview + 6 dispatches + the `/writing/` index.
- **`books.html`** — J.S. Warden hub; OE Book schema has **3 editions** (#17).
- **`overlayed-echoes-preview.html`** (bespoke, excluded) — free Ch.1–2, 3 CTAs (hero/end paperback `06ZWovoY`, mid Kindle `026ie1Si`).
- **`/writing/`** — index + 6 dispatches (BlogPosting, NO FAQPage), unlisted in nav, built by **`tools/_build_dispatches.py`**.

### 17. OE facts — **THREE editions (verified — use exactly).**
*Overlayed Echoes* = near-future **LitRPG**, 257-page, **Book 1 of a planned 5**, Kindle + paperback + hardcover + **KU**. Set 2045. NOT noir (that's Ebonspire). Print pub **2025-09-01**. Author store `https://www.amazon.com/stores/J.-S.-Warden/author/B0FPQ3RWWF`.

| Edition | ASIN | ISBN-13 | Price | a.co |
|---|---|---|---|---|
| Kindle | `B0H3826V21` | — | $5.99 (free on KU) | `https://a.co/d/026ie1Si` |
| Paperback | `B0H39RRSNF` | 979-8199065542 | $12.99 | `https://a.co/d/0cQASed2` |
| Hardcover | `B0H3Q66YH9` | 979-8199641265 | $23.99 | `https://a.co/d/03rhvH3N` |

- `numberOfPages:257` on PRINT editions only. **a.co caveat:** `https://a.co/d/06ZWovoY` = the PAPERBACK; visible Amazon CTAs use `06ZWovoY`, books.html schema uses `0cQASed2`. **Resolve any a.co → `/dp/ASIN` before use** (Amazon 500s the product page but returns the redirect ASIN).
- **Ebonspire Chronicles:** dark-fantasy detective noir, releases June 2026, unreleased (no Offer). Pre-release treatment intact.
- **Chinese-zodiac art bundles:** $14.99 each.

### 18. Architecture quick-reference.
**101 HTML files:** root 8 · free 1 · products 9 · blog 34 + `blog.html` · collections 40 (generated) · writing 7 · resources 1 · legal 1 (+10 PDFs). **No build step. Sitemap is MANUAL** (101 `<url>`, field order `loc→lastmod→changefreq→priority`). Images `/images/{products,zodiac,books,logo,og}/`, webp primary, root-absolute. CSS = per-page inline `<style>` + 4 shared (`tokens.css`, `checkout.css`, `gallery.css`, `mobile-nav.css`). JS = 6 in `/js/` + `gallery.js`. Fonts: Syne / DM Sans / JetBrains Mono (+ Cinzel/Crimson Pro under the glass system).
- **`/free/` (`free/index.html`):** light glass-lite page. Cards `rgba(255,255,255,.48)` + `blur(14px) saturate(130%)` over per-section `.free-section::before`/`.home-tools::before` washes. Lite cards use `data-checkout="<slug>-lite"` + shared `checkout-config.js`+`checkout.js`; `[data-lite-section]` wrappers carry inline `display:none` FOUC guards.
- **Glass system (`css/tokens.css`):** two-layer — per-page inline `<style>` = flat base; `tokens.css` `[data-glass="prototype|cosmic|books"]` layers the frost (wins by specificity). `--glass-bg`/`--glass-border` defined but **unused** (surfaces hardcode rgba); only `--rim-light`/`--nav-bg`/`--nav-border` consumed (by `.site-nav`). Flat-bg glass-lite cards ALL sit over a section `::before` wash — no glass-on-truly-flat (blog cards are solid `#ffffff`, deliberately).
- **Blog post structure (G8):** 2-col `.article-main` = `.article-body` + sticky `.article-sidebar-sticky` (solid white, NOT glass) product card; an `.inline-cta` (`btn-inline-etsy`) mid-article; a final `.cta-band` (`btn-etsy`); a `.related-posts` grid; FAQ `<h3>/<p>` mirrored in a FAQPage JSON-LD. Buy CTAs now → `/products/<slug>.html`.

---

## 🟢 Status: live, clean, nothing mid-flight

Working tree clean except the usual untracked: `.claude/`, `.netlify/`, dated `HANDOFF-*.md` archives, `SITE-OVERVIEW.md`, `_audit_output.md`, and per-session `tools/_*.py` scripts — **now including `tools/_free_nav_sweep.py` + `tools/_etsy_repoint.py`** (plus `_build_dispatches.py`/`_verify_dispatches.py`). None tracked; leave or clean up at will. **The only uncommitted/unpushed thing is this HANDOFF refresh** (commit it / push it per Josh).

---

## First steps for the new session

```bash
cd /c/Users/jotra/builtbyjoshstudio
git status                                          # this HANDOFF refresh may be [ahead 1], unpushed — ask Josh
git log --oneline -12
git tag -l 'backup-*' --sort=-creatordate | head -8

# Live spot-checks (cache-busted):
ts=$(date +%s)
curl -fsS -I "https://builtbyjoshstudio.com/free/?x=$ts" | head -1                                   # 200 (hub)
curl -fsS "https://builtbyjoshstudio.com/free/?x=$ts" | grep -c 'data-checkout='                     # 7 (live lite buttons)
curl -fsS "https://builtbyjoshstudio.com/blog/notion-finance-os-for-creators.html?x=$ts" | grep -c 'etsy.com/listing'   # 0 (buy buttons repointed)
curl -fsS "https://builtbyjoshstudio.com/blog/notion-finance-os-for-creators.html?x=$ts" | grep -c 'View Creator Finance OS'  # 1 (repointed label)
curl -fsS "https://builtbyjoshstudio.com/blog/free-budget-spreadsheet-excel-google-sheets.html?x=$ts" | grep -c '35% off the full version on Etsy'  # 0
curl -fsS "https://builtbyjoshstudio.com/blog/free-notion-templates-creators-no-email.html?x=$ts" | grep -c 'No email required. No signup form'  # 0 (body cleaned)

gh run list --workflow=pages-build-deployment --limit 5    # latest completed/success
```

Then take direction from Josh. Nothing is mid-flight.

---

## Open / deferred items (nothing blocking)

- **Metadata-honesty pass (the most-likely next ask).** Body "no email" copy is cleaned, but two **metadata** spots still claim it and need stripping: (a) `blog/free-notion-templates-creators-no-email.html` — "No Email Required"/"No email signup" in `<title>`, `<h1>`, meta description, OG+Twitter title/description, and schema `headline`/`description`/BreadcrumbList name; (b) `blog/what-lite-actually-means.html` — final CTA sub-line "…real systems, no email required." Also `blog.html`'s free-notion teaser excerpt ("…no signup wall") if you want consistency. **Leave URLs/slugs alone** (the `-no-email` slug stays). Reason: `/free/` lite downloads capture an email (#5). Kept-as-true: free-notion's "Notion Marketplace — No signup required" (that path IS no-signup).
- **`/free/` follow-ups (minor):** the 8th lite SKU (`creator-os-full-stack-lite` sampler) isn't featured on `/free/` (by design); "Free" nav active-state is only on `/free/` itself; no per-page OG card for `/free/`.
- **Stage 2 dispatches** — `tools/_build_dispatches.py` + the `/writing/` index pattern ready; need markdown + a thematic slug.
- **Per-dispatch OG cards** — all 6 dispatches + the preview share `images/books/og-books.jpg`.
- **Inline-breaker rollout** — `.inline-breaker` fiction tie-in shipped on one launch post; ready for other high-impression posts.
- **Organization schema non-critical warnings** — Rich Results Test flags non-critical Org-node issues (pre-existing, non-blocking); fix = site-wide sweep.
- **Ebonspire launch (June 2026)** — flip "releases June 2026" → "available now", add Book + Offer with verified ASIN, mirror the 3-edition pattern.
- **Carry-forwards:** OG images for ~22 blog posts; GA4 purchase verification in Realtime; "Buy Direct — Instant Download" lead-CTA; Google Merchant Center; Ebonspire cover for books.html.

---

## Branches and tags

```
main    production — HEAD == origin/main + this unpushed HANDOFF refresh on top
```

**Backup tags (newest first):** `backup-pre-free-nav-sweep` (`da05b24`) · `backup-2026-06-03` (`bc0ed00`) · earlier arc tags remain. (LOCAL only.)

**This session's commits (newest first, all pushed & live except this HANDOFF refresh):**
`945e528` Notion-OS buy-button + schema repoint (Etsy → /products/) · `1ba5b99` strip remaining no-email/no-signup/lead-capture copy · `2196d80` drop "no email" claims + add /free/ links · `891b854` HANDOFF /free/ shipped · `20458de` /free/ hub + nav sweep · `da05b24` prior HANDOFF refresh. Session-start tip was `bc0ed00` (Field-Dispatches arc).

---

## Hard-won lessons this session

- **The lite download captures an email; cooking tools don't.** This distinction drove the whole no-email cleanup. "No email" is true for Notion Marketplace + cooking tools, false for the `/free/` Lite download ($0 LS purchase). Don't editorialize "no email" about the Lite.
- **FAQ/Offer JSON-LD mirrors the visible copy byte-for-byte (#9).** Editing a visible FAQ answer or buy link without editing its JSON-LD twin breaks the mirror. The Edit tool's "Found 2 matches" error is the signal you forgot the schema copy.
- **Re-grep the LIVE site after every write.** A body residual (`free-home-buying:484` "No email gate. No lead capture") survived the first pass and was only caught by the cache-busted post-deploy sweep. Local grep + live grep both.
- **For heterogeneous multi-file edits, write a match-checked `tools/_*.py` script** (per-old-string count; 0 = MISS), dry-run, then `--write` — cleaner and more reconciled than dozens of hand edits (`tools/_etsy_repoint.py`, 42 replacements, 0 misses).
- **Prove a prior commit is live before re-touching it.** Josh asked me to grep the old strings (→ none) and confirm `merge-base --is-ancestor <sha> origin/main` before excluding an already-shipped section from a new commit. Good guardrail against re-applying done work.
- **`btn-etsy`/`btn-inline-etsy` ≠ Etsy.** It's a shared orange-CTA class reused for on-site `../products/` links. Don't let class names imply destinations.
- **Place "final" files byte-exact with `cp`+`cmp`, not Write** (preserves `𝗡`/`▦`/curly-quote/`→` glyphs); edit only the one line Josh authorizes. **Commit messages via here-doc `-F -`** to avoid literal-double-quote breakage. **`main` is production — no PR flow.**

---

**End of handoff.** State: live, clean, all three arcs (`/free/`, no-email cleanup, Notion-OS repoint) pushed & post-deploy-verified; HEAD == origin/main with this HANDOFF refresh unpushed on top. New session: read this doc, run the First-Steps block, ask Josh whether to push the HANDOFF refresh, then take direction.
