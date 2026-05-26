# builtbyjoshstudio.com — Session Handoff

**Date:** 2026-05-26 (end of session; new Claude Code session starting fresh)
**Repo:** https://github.com/builtbyjoshstudio-cyber/builtbyjoshstudio
**Local path:** `C:\Users\jotra\builtbyjoshstudio`
**Host:** GitHub Pages — custom domain `builtbyjoshstudio.com` via CNAME → Fastly CDN
**HEAD (pushed):** `8055f13` on `main`, in sync with `origin/main`. Pages deployment confirmed live as of `26460285180` build (Phase 6 filter verified live; full Phase 1 → Phase 6 pass shipped).
**Latest backup tag:** `backup-after-phase-6` (`8055f13`). Pushed to origin. Working tree is clean (apart from the usual untracked: `.claude/`, `.netlify/`, dated `HANDOFF-*.md` archives, plus 7 per-phase utility scripts in `tools/`).

---

## 🧭 Session summary (plain language)

This session ran the full six-phase SEO optimization pass end-to-end on top of the post-LS-rollout baseline. We tightened the about page with a credentials section and richer Person schema, added `datePublished` / `dateModified` to every Product schema, added `<image:image>` entries to the sitemap for products and collections, audited every FAQ schema for visible-content match and remediated the six blog posts that drifted (five got new visible Q&A sections, one was a "What's" → "What is" contraction fix), extended the related-reading card blocks on all 34 blog posts with sideways cross-links and promoted their `<div class="related-posts-label">` to `<h2>` for proper heading hierarchy, and added a pure-vanilla client-side filter search on the blog index. Along the way we caught a build-blocker (Jekyll's Liquid parser choking on literal `{{` in HANDOFF.md) and unblocked it by adding a minimal `_config.yml` exclude. Every phase shipped, deployed cleanly, and was verified on the live site. The repo grew by seven small per-phase Python utilities (untracked, in `tools/_audit_*` / `tools/_phase*_*` style).

---

## 🔴 STANDING INSTRUCTIONS — read these first

These are the rules Josh has set through hard pushback over multiple sessions. Apply them by default; only deviate if Josh says so explicitly.

### 1. Communication style: terse, directive, no preamble.
Josh's style. No padding. Surface tradeoffs in 1–2 sentences and pick a default; don't ask a dozen questions. When you find real ambiguity worth confirming, ask ONE crisp question with a recommended default. Skip "Great, I'll start by…" preambles.

### 2. The site has NO template engine.
Every HTML page is standalone with its own inline `<style>` block, its own JSON-LD, its own nav, its own footer. The Python scripts in `tools/` are the closest thing to a template engine — they generate per-page HTML from manifests + hardcoded sign/animal data. When you need to change something site-wide (e.g., add a footer link, inject a schema block), either (a) edit the generators and regenerate, or (b) write a Python sweep that visits every `.html` file. There's no shared partial to update.

### 3. Lemon Squeezy IS the primary checkout for the zodiac art Collections. Etsy is a secondary reference only.
The full LS rollout is complete — all 77 buttons across 38 collection pages are live with real LS overlay URLs. Tynkr products use the existing key-based `data-checkout` + `CHECKOUT_CONFIG` infrastructure (see `js/checkout.js`, `js/checkout-config.js`). The Collection pages use the `.ls-checkout-btn` pattern with `data-checkout-url` populated and the click handler in `js/ls-checkout-btn.js`.

### 4. Sales-channel hierarchy on Collection pages
- **Primary CTA:** the LS button (sidebar + final CTA band on every Collection page; Western Landscapes also has a top-of-grid bundle CTA)
- **Secondary reference:** a muted "Looking for something different? Visit the Etsy shop →" block at the bottom of the sidebar. Smaller text, no button styling, courtesy link only. Does NOT compete with the primary CTA visually.
- **Footer:** Etsy link stays in the global footer alongside Refunds/Privacy/Terms/Legal — that's a directory listing, not a sales CTA.

### 5. Verify file content claims against actual source code/data, not against documentation or assumptions.
The PDFs, the brief, your own memory — none of these are authoritative. The actual asset files (the webps in `images/zodiac/...`, the source files at `OneDrive\...\Zodiac Collections\`), the manifest JSONs, and the live pages are. When the brief says X but the actual file count is Y, flag the discrepancy and use the accurate number with a note.

### 6. LS URL activation procedure (still applies for future Collections / re-runs)
For each `<button class="ls-checkout-btn"...>` element:
1. Paste the LS overlay URL into `data-checkout-url=""`
2. Remove the `disabled` attribute and swap the button text from `Buy the X Bundle — Coming Soon` to `Buy the X Bundle — $<price>`

Generators implement this via per-Collection `LS_URL_BY_SIGN` / `LS_URL` dicts + an `ls_button_state()` helper. To add a new URL, just populate the dict entry and regenerate.

### 7. Identity hygiene rules (site-wide):
- **Founder name:** "Josh" only on every public-facing surface. Never "Joshua Tran" or "Josh Tran" or just "Tran". Pen name "J. S. Warden" appears only on fiction-author schema (about.html `workExample` block).
- **City-level data:** state-level "Kansas" only on public pages. **Never any city** — not in copy, not in schema. The ONLY exception is the registered agent address (Wichita, KS) which appears solely on `/legal/index.html` as a legitimate compliance surface. Reinforced this session when the Phase 1 brief asked for "Wichita, Kansas" in the about-page Person schema's `occupationLocation` — Josh confirmed state-only.
- **`<meta name="keywords">`:** never. Already stripped from all 90+ HTML pages.

### 8. The site-wide Organization JSON-LD block is on every collection page, injected before `</head>`.
Stable `@id`: `https://builtbyjoshstudio.com/#organization`. Per-page Product/FAQ/etc. schemas `@id`-reference the Organization via `{"@id": "https://builtbyjoshstudio.com/#organization"}` for `manufacturer` and `seller`. Don't redefine the Organization inline elsewhere.

### 9. Schema rule for Collection pages: Product + FAQPage + BreadcrumbList + Organization per page.
- **Product schema** uses `@id: <page-url>#product` for stable referencing, SKU pattern `BBJ-<COL>-<SIGN>` (WS/WR/WL/CS/CR), `additionalProperty` block with the full file/design/format spec, single `Offer` at the bundle price `InStock`, `hasMerchantReturnPolicy: MerchantReturnNotPermitted`, plus `datePublished` + `dateModified` (added in Phase 2 of the optimization pass).
- **FAQPage schema** must mirror the visible FAQ text exactly. Use the shared `faq_data()` / `faq_schema_data()` pair in the generators so visible HTML and schema build from a single source. Use ASCII-safe substitutions in the schema (`20" × 30"` → `20 by 30 inches`, etc.). Phase 4 / 4.5 audit confirms all 62 FAQPage-bearing files now serve all schema questions visibly (445/445).
- **BreadcrumbList:** 4-level for per-sign pages (Home > Collections > <Collection> > <Bundle>), 3-level for single-bundle pages.
- **No `aggregateRating`** until product-specific reviews exist.

### 10. Use the Python generators in `tools/`, not direct HTML editing, for Collection pages.
The 5 generators encode the canonical structure (LS CTAs, License block, Quick Facts, sister nav, schemas). Direct editing risks divergence between the visible HTML and the schema, and between sister pages that should share structure. Update the generator, re-run, commit. The 5 generators and their outputs:

| Script | Outputs |
|---|---|
| `tools/build_western_signs_page.py` | 12 Western Signs (`<sign>-zodiac-art.html`) |
| `tools/build_realm_page_master.py` | 12 Western Realms (`<sign>-zodiac-realms.html`) |
| `tools/build_chinese_animal_pages.py` | 12 Chinese Signs (`<animal>-chinese-zodiac-art.html`) |
| `tools/build_chinese_realms_page.py` | 1 Chinese Realms single bundle |
| `tools/build_zodiac_landscapes_page.py` | 1 Western Landscapes single bundle |

Hand-written hub: `collections/chinese-zodiac-art.html` (CS hub — has 13 Product blocks: 1 top-level + 12 nested ItemList items; only ever edit the top-level one).

### 11. Schema for blog/tool posts (legacy rule — preserved, still active)
**Article + BreadcrumbList only.** No `WebApplication` schema. No `featureList`. No `applicationCategory`. The four pre-existing tool posts (Recipe Scaler, Reverse Roasting, Pan Swap, Pull Temp) still have their old WebApplication blocks — leave them alone unless content actually disagrees with the live app.

### 12. Antigravity owns the cooking apps. You write blog posts about them. Never apps.
App source for each tool lives at `C:\Users\jotra\.gemini\antigravity\scratch\<slug>\`. Cooking queue is currently empty.

### 13. GitHub Pages builds can fail on transient infrastructure issues. Check before assuming a deploy completed.
The `actions/jekyll-build-pages` action archive can fail to download from `codeload.github.com`. Commits push fine; Pages just silently fails to deploy. Recovery: `gh run rerun <run_id> --failed` OR push an empty commit (`git commit --allow-empty -m "Trigger Pages rebuild"`). Always check live content with `curl ?x=<timestamp>` against expected new strings after a push. `gh run list --workflow=pages-build-deployment --limit 5` shows recent build status.

### 14. Jekyll's Liquid parser will choke on literal `{{` in markdown — `_config.yml` excludes HANDOFF.md.
**Added this session:** `HANDOFF.md` documents Python f-string `{{` escapes, which Jekyll's Liquid templater tries to parse as variables and fails. The fix lives at `/_config.yml` (root) and excludes `HANDOFF.md` + `HANDOFF-*.md` from Jekyll processing. If you add any tracked top-level markdown that contains literal `{{` (e.g., another runbook or template-docs file), either (a) add it to the `exclude` list in `_config.yml`, or (b) wrap the offending region in `{% raw %}` ... `{% endraw %}`. The site itself has no Jekyll dependencies — all pages are hand-written HTML — so the exclude list is the cleaner option.

---

## 🟢 Status: live, clean — all six SEO optimization phases shipped

Working tree clean (only the usual untracked: `.claude/`, `.netlify/`, dated `HANDOFF-*.md` archives, and per-session utility scripts under `tools/_audit_*` / `tools/_phase*_*`). Cooking-stagger publish queue is empty (`tools/cooking-queue.json` = `[]`) and not in active use.

---

## First steps for the new session

```bash
cd /c/Users/jotra/builtbyjoshstudio
git status                                                  # clean (untracked: .claude/ .netlify/ HANDOFF*.md + a few _audit/_phase* scripts + _audit_output.md)
git log --oneline -10                                       # HEAD 8055f13
git tag -l 'backup-*' --sort=-creatordate | head -5         # backup-after-phase-6 newest
grep -c '<loc>' sitemap.xml                                 # 91
# Live deploy spot-checks (Phases 1, 2, 3, 4.5, 5, 6):
curl -fsS "https://builtbyjoshstudio.com/about.html?x=$(date +%s)" | grep -c "What I bring to the work"                          # 1
curl -fsS "https://builtbyjoshstudio.com/collections/aries-zodiac-art.html?x=$(date +%s)" | grep -c "datePublished"              # 1+
curl -fsS "https://builtbyjoshstudio.com/sitemap.xml?x=$(date +%s)" | grep -c "image:image"                                      # 94 (47 entries × 2 tags)
curl -fsS "https://builtbyjoshstudio.com/blog/why-solo-creators-stay-stuck-under-5k.html?x=$(date +%s)" | grep -c "Frequently Asked Questions"  # 1
curl -fsS "https://builtbyjoshstudio.com/blog/ultimate-budget-workbook.html?x=$(date +%s)" | grep -c '<h2 class="related-posts-label">'        # 1
curl -fsS "https://builtbyjoshstudio.com/blog.html?x=$(date +%s)" | grep -c 'id="blog-filter-input"'                             # 1
# Pages build status (only matters if a recent push isn't showing live):
gh run list --workflow=pages-build-deployment --limit 5
```

Expected: HEAD `8055f13`, 91 sitemap entries, working tree clean, last Pages build succeeded, every Phase 1–6 marker present on live.

---

## What this session accomplished

### Six-phase SEO optimization pass — shipped end-to-end

| Commit | Phase | What |
|---|---|---|
| `1297625` | 1 | About page gained "What I bring to the work" credentials section (5 sentences, 3 paragraphs, Josh's voice — cooking heritage, two novel series, LLC ops, dogfooding, solo-creator scope). Person JSON-LD enriched with `hasOccupation` (state-level Kansas, no city per Standing #7), `publishingPrinciples`, `award`, and `workExample` (Overlayed Echoes Book + Ebonspire Chronicles BookSeries, both authored by "J. S. Warden"). |
| `d0b66b3` | 2 | Added `datePublished` + `dateModified` = `2026-05-26` to all 47 Product-schema-bearing pages (8 product + 38 generator-output collection + 1 hand-written CS hub). Schema-only, no visible content changes. |
| `01f0496` | 3 | Added `<image:image>` entries (with `xmlns:image` namespace) to 47 `<url>` blocks in `sitemap.xml` — 8 product pages + 38 generator-output collections + 1 hand-written CS hub. Indexes (`/products/`, `/collections/`) skipped — no Product schema to pull image from. Blog posts deliberately not included this pass. |
| `3a8de69` | (unblock) | Added `_config.yml` with `exclude: [HANDOFF.md, HANDOFF-*.md]`. Necessary because HANDOFF.md contains literal `{{` and `}}` in markdown (documenting Python f-string escapes) which Jekyll's Liquid parser tries to interpret as template variables, failing the build. Pages had silently failed twice before this fix landed. See Standing Instruction #14. |
| `698b745` | 4 + 4.5 | Read-only FAQPage visibility audit (62 files, 445 questions): flagged 6 blog posts where schema questions weren't visibly on the page. Remediation: 5 posts got brand-new `<h2>Frequently Asked Questions</h2>` sections rendering Q&As verbatim from existing schema; 1 post (`first-time-homebuyer-mistakes`) had a `What's` → `What is` contraction fix on a visible `<h3>` to match the schema verbatim. Post-audit: 445/445 visible, 0 flagged. |
| `5519ed7` | 5 | Extended related-reading card blocks on all 34 blog posts with 5B additions (sideways topical neighbors, not currently linked, skewed away from same-product upsell) + 12 approved displacements (hub→domain-essay swaps, sibling-cluster breakups, free/lite closed-loop interventions). Simultaneously promoted `<div class="related-posts-label">` to `<h2 class="related-posts-label">` site-wide for proper heading hierarchy + a11y. CSS hook intact, visual rendering unchanged. Final card counts: 12 posts at 4 cards, 21 at 5, 1 at 6. Zero broken internal links. Hand-authored 7 card descriptions for slugs with no prior inbound card (stored in `tools/_phase5_related_reading.py` `LIBRARY_EXTENSIONS`). |
| `8055f13` | 6 | Client-side filter search on `/blog.html`. Pure vanilla, no deps, ES5-safe. `<input type="search" placeholder="Filter posts...">` placed between the section anchor nav and the first `.blog-section`. Live filter on `input` event, case-insensitive substring match against `.article-title` + `.article-excerpt`. Escape clears. Section auto-hides when all its cards are hidden. "No posts match that filter." paragraph shows when zero matches. Inline CSS uses existing `--bbj-*` palette vars. Filter placeholder uses the global `input::placeholder` rule (no italic — convention-correct). |

### Backup tag

- `backup-after-phase-6` → `8055f13` (pushed to origin)

---

## Pre-session → final state

| Aspect | Before this session (pre-`6273822`) | After this session (`8055f13`) |
|---|---|---|
| Working HEAD | `e6475a4` (empty-trigger commit) | `8055f13` (Phase 6) |
| About page | "Hi, I'm Josh" + Two Brands + Beyond + Where + Connect | + new "What I bring to the work" credentials section (Phase 1) |
| Person schema on about.html | Name + jobTitle + sameAs | + `hasOccupation` (state-level KS), `publishingPrinciples`, `award`, `workExample` × 2 (Phase 1) |
| Product schemas | `hasMerchantReturnPolicy` already present | + `datePublished` + `dateModified` on all 47 (Phase 2) |
| `sitemap.xml` | 91 `<loc>` entries, no image entries | 91 `<loc>` + 47 `<image:image>` entries, `xmlns:image` namespace (Phase 3) |
| Jekyll build | Silently failing on HANDOFF.md `{{` Liquid parse | `_config.yml` excludes HANDOFF.md; build healthy (unblock) |
| FAQ visibility | 419/445 visible across 62 schemas; 6 posts had drift | 445/445 visible; zero flagged (Phase 4 + 4.5) |
| Blog related-reading | 3 cards per post; div-styled label | 4–6 cards per post (sideways neighbors added, weak hub-to-hub links displaced); `<h2>` label across all 34 (Phase 5) |
| Blog index | Anchor nav only | Anchor nav + client-side filter input + auto-hide + empty-state (Phase 6) |
| Backup tag (newest) | `backup-after-ls-chinese-signs-activation` (`9cab5c0`) | `backup-after-phase-6` (`8055f13`) |

---

## What's live in production right now

### Phase-by-phase live markers
- `about.html` → "What I bring to the work" section + enriched Person schema
- All 47 Product-schema pages → `datePublished` / `dateModified: 2026-05-26`
- `sitemap.xml` → `xmlns:image` namespace + 47 `<image:image>` entries
- 62 FAQPage-bearing files → 445/445 schema questions visible (incl. 6 remediated blog posts)
- 34 blog posts → extended related-reading cards (4–6 per post) + `<h2 class="related-posts-label">`
- `/blog.html` → client-side filter input + "No posts match that filter." empty state

### Collection pages — 38 pages, all on master pattern, all checkout-ready

| Page type | URL pattern | Count | LS buttons per page | Price |
|---|---|---|---|---|
| Per-sign Western Signs | `/collections/<sign>-zodiac-art.html` | 12 | 2 (sidebar + final CTA) | $24.99 |
| Per-sign Western Realms | `/collections/<sign>-zodiac-realms.html` | 12 | 2 | $14.99 |
| Per-animal Chinese Signs | `/collections/<animal>-chinese-zodiac-art.html` | 12 | 2 | $14.99 |
| Chinese Realms single bundle | `/collections/chinese-zodiac-realms.html` | 1 | 2 | $29.99 |
| Western Landscapes single bundle | `/collections/zodiac-landscapes.html` | 1 | 3 (top-of-grid + sidebar + final CTA) | $19.99 |
| **Total** | | **38** | **77 buttons** | |

All 77 carry live `data-checkout-url`, no `disabled` attribute, button text reads `Buy the <X> Bundle — $<price>`. `js/ls-checkout-btn.js` script tag present on every page.

### Site-wide schema state

Every collection-page Product schema includes:
- `@id` reference to the canonical Organization
- `additionalProperty` block with the full file/design/format spec
- `hasMerchantReturnPolicy: MerchantReturnNotPermitted`
- `datePublished: 2026-05-26` + `dateModified: 2026-05-26`
- LS-overlay URL in `offers.url`

### `/legal/` hub
| URL | Status |
|---|---|
| `/legal/` (hub page) | Live, `noindex,follow`, 5 Collection blocks + universal terms + policies + about |
| 5 license PDFs + 5 print-guide PDFs at `/legal/<filename>.pdf` | All 200, all crawlable |

### Site-wide
- Organization JSON-LD on every HTML page (injected before `</head>`)
- `<meta name="keywords">` tag stripped everywhere
- "Legal" link in footer of every page
- "Joshua Tran" / "Josh Tran" / "Tran" / "Topeka" — 0 occurrences across HTML/MD/TXT
- Sitemap: 91 `<loc>` entries, 47 with `<image:image>` (products + collections), `xmlns:image` namespace
- `llms.txt` at root — includes free web utilities section
- Homepage OG image at `images/og/og-home.webp` (1200×630), referenced by `og:image` + `twitter:image`
- Jekyll Liquid build healthy via `_config.yml` excluding `HANDOFF.md`

### Homepage `index.html` sections (order):
1. `#tynkr` — Tynkr Tools
2. `#builtbyjosh` — Western Signs Zodiac Art (12 cards)
3. `#western-realms` — Western Realms (12 cards)
4. `#chinese-zodiac` — Chinese Signs (12 cards)
5. `#chinese-realms` — Chinese Realms (12 cards, anchor to single bundle)
6. `#landscapes` — Western Landscapes (12 cards, anchor to single bundle)
7. `#free-tools` — 7 cooking utilities

### About page (`about.html`) sections (order):
1. Hi, I'm Josh.
2. **What I bring to the work** (Phase 1)
3. The Two Brands
4. Beyond the Studio
5. Where the Studio Lives
6. Connect With the Studio

### Blog index (`blog.html`) — Phase 6 layout
1. Hero + Substack form
2. Section anchor nav (`Templates` / `Learning` / `Projects`)
3. **Filter input** (`.blog-filter` — `<input type="search" placeholder="Filter posts...">` + hidden `.blog-filter-empty` "No posts match that filter.")
4. `<section id="templates" class="blog-section">` — Templates section + 11 cards
5. `<section id="learning" class="blog-section">` — Learning section + ~16 cards
6. `<section id="projects" class="blog-section">` — Projects section + ~7 cards

(Sections auto-hide via the filter when all their cards are hidden.)

---

## Open items / pending work

### 🟡 Deferred from this session — carry forward

1. **OG images for the remaining ~22 blog posts.** Josh said he'd eventually do it but isn't actively sharing posts elsewhere, so the 7 tool-mapped + 6 cooking-personal posts that *would* have gotten OG images this round were also deferred. If/when this comes up again, the previously-written Phase 2 OG prompt is in conversation history.

2. **GA4 purchase event verification.** Outstanding from earlier discussion. `view_item`, `add_to_cart`, `begin_checkout` should be firing via the recently-added event code. The purchase event happening inside the Lemon Squeezy iframe is the unknown — needs either a manual $1 test purchase + GA4 Realtime check, OR a Lemon Squeezy dashboard config audit, OR confirmation that a webhook / thank-you-page redirect is wired up. Diagnostic prompt is in conversation history.

3. **CTA copy update on product + collection pages** to lead with "Buy Direct — Instant Download" and demote Etsy to secondary. Held off pending GA4 purchase verification (no point promoting native checkout traffic if the funnel can't capture the conversion). Once Item 2 is resolved, the CTA prompt is in conversation history.

4. **2 zodiac collections still Etsy-only** (Chinese Zodiac signs / Lunar Guardians + Zodiac Landscapes). Migration to Lemon Squeezy is in progress per Josh. When those flip live, the CTA update prompt needs to be re-run scoped to include them.

5. **Google Merchant Center setup.** Previously deprioritized; meaningfully more valuable now that native checkout is live with direct-purchase URLs. Desktop session needed.

6. **Optional FAQ template paired-generator pattern for blog posts.** The 6 blog posts that drifted out of FAQ visibility in Phase 4 were posts predating the `faq_data()` / `faq_schema_data()` pattern already used on product + collection pages. Retrofitting the blog template to use the same pattern would prevent future drift. Not urgent, but a real infrastructure-debt cleanup if the blog FAQ count keeps growing.

7. **Cooking blog `building-the-universal-recipe-scaler` description swap** — verified at session end: card block now includes `cook-the-way-you-want-to-cook` + `what-i-actually-keep-in-my-kitchen` (correct Phase 5 swap from biographical `how-i-learned-to-cook` to system/philosophy essays). 5 cards total, H2 promoted. ✅ done — kept in the open-items list for future audit reference.

### 🟢 Lower priority — pre-existing open items

- `tools/build_realm_pages.py` (Phase 2 legacy simpler Realms generator) is still in the repo. Can be deleted now that `build_realm_page_master.py` is canonical.
- 5+ dated handoff archives accumulated as `HANDOFF-*.md` — untracked, kept locally.
- The cooking-stagger publish queue (`tools/cooking-queue.json` = `[]`) is empty and inactive.

### Untracked utility scripts from this session

These are non-production scripts and audit outputs. Delete or keep — they don't affect the live site. Listed in chronological order of creation:

- `_audit_output.md` — 95 KB SEO audit report from earlier this session (initiated the 6-phase optimization brief)
- `tools/_audit_seo.py` — read-only SEO audit script
- `tools/_audit_addendum.py` — added the payhip/gumroad section + summary to the audit output
- `tools/_phase2_dates.py` — Phase 2: injected `datePublished` + `dateModified` into hand-written Product-schema pages
- `tools/_phase3_sitemap_images.py` — Phase 3: injected `<image:image>` entries into sitemap.xml
- `tools/_phase4_faq_audit.py` — Phase 4: read-only FAQPage visibility audit (re-runnable; reports per-file X-of-Y visible)
- `tools/_phase4_5_inject_faq.py` — Phase 4.5: injected new `<h2>Frequently Asked Questions</h2>` sections into 5 blog posts
- `tools/_phase5_related_reading.py` — Phase 5: extended related-reading cards + H2 promotion; contains `RECIPES` (per-post add/drop) + `LIBRARY_EXTENSIONS` (7 hand-authored card descriptions). Idempotent and re-runnable.

If you need to extend related-reading further, the easiest path is to edit `RECIPES` in `tools/_phase5_related_reading.py` and re-run — it's idempotent (de-dupes adds, no-ops on drops already gone).

---

## Critical configuration (unchanged from prior session)

| Item | Value |
|---|---|
| Legal entity | **Built by Josh Studio LLC** (Kansas) |
| Kansas Business ID | `10076138` |
| Registered Agent | Northwest Registered Agent LLC, 4601 E. Douglas Ave. STE 150, Wichita, KS 67218 (legal service only — only appears on `/legal/index.html`) |
| Email | `josh@builtbyjoshstudio.com` |
| Tynkr Tools & Co Etsy | `https://tynkrtoolsandco.etsy.com` |
| Zodiac (BBJ) Etsy | `https://www.etsy.com/shop/BuiltByJoshStudio` |
| LS store URL | `https://tynkrtoolsco.lemonsqueezy.com/` |
| **LS bundle URLs (Collection products)** | **All 38 live.** Spec lives in each generator's `LS_URL_BY_SIGN` / `LS_URL_BY_ANIMAL` / `LS_URL` dict. |
| GA4 Measurement ID | `G-QDSPBB7S9J` (inline in every page's `<head>`) |
| Pen name (fiction only) | **J. S. Warden** — appears only on `about.html` Person `workExample` schema |
| Books in author schema | `Overlayed Echoes` (Book, near-future LitRPG/SciFi/Metafiction, Amazon at `https://a.co/d/04YzP4o4`, expanding to 5-book series), `Ebonspire Chronicles` (BookSeries, Dark Fantasy / Urban Fantasy / Noir Detective Fiction) |
| Pricing model | Western Signs $24.99 · Western Realms $14.99 · Chinese Signs $14.99 · Chinese Realms $29.99 · Western Landscapes $19.99 — all 38 pages reflect these, all live LS overlay URLs in place |

### Asset inventory (unchanged this session)

| Section | Per-page designs | Hub thumb | Webps in repo |
|---|---|---|---|
| Western Signs | 24 (14 styles × 1–4 variants) | `images/zodiac/<sign>.webp` × 12 | 288 design + 12 hub |
| Western Realms | 8 (4 realms × 2 variants) | `images/zodiac/realms/<sign>.webp` × 12 | 96 design + 12 hub |
| Chinese Signs | 8 (4 hyper-realistic + 4 watercolor) | `images/zodiac/chinese/<animal>.webp` × 12 | 96 design + 12 hub |
| Chinese Realms | 2 per animal (single bundle, 24 total) | `images/zodiac/chinese-realms/<animal>.webp` × 12 | 24 design + 12 hub |
| Western Landscapes | 1 per sign | `images/zodiac/landscapes/<sign>.jpg` × 12 | 12 jpgs |

---

## Generators in `tools/` — current state

| Script | Purpose | Status |
|---|---|---|
| `build_western_signs_page.py` | 12 Western Signs per-sign pages | Master pattern; all 12 LS URLs live; `datePublished`/`dateModified` present |
| `build_realm_page_master.py` | 12 Western Realms per-sign pages | Master pattern; all 12 LS URLs live |
| `build_chinese_animal_pages.py` | 12 Chinese Signs per-animal pages | Master pattern; all 12 LS URLs live |
| `build_chinese_realms_page.py` | 1 Chinese Realms single-bundle page | Master pattern; LS URL live |
| `build_zodiac_landscapes_page.py` | 1 Western Landscapes single-bundle page | Master pattern; LS URL live; 3-button page |
| `build_realm_pages.py` | Phase 2 legacy simpler WR generator | **Obsolete** — safe to delete |
| `update_western_sign_pages.py` | Phase 5 surgical updater | Idempotent. Probably done. |
| `identity_cleanup.py` | Identity hygiene sweep | Idempotent. Has the canonical Organization schema embedded. |
| `phase3_apply.py`, `phase4_apply.py` | Phase atomic apply scripts | Already executed (older site phases, not this session's) |
| `publish_next_cooking.py`, `publish-next-cooking.ps1` | Cooking-stagger publish queue | Inherited. Queue empty. |
| `_audit_seo.py`, `_audit_addendum.py`, `_phase2_dates.py`, `_phase3_sitemap_images.py`, `_phase4_faq_audit.py`, `_phase4_5_inject_faq.py`, `_phase5_related_reading.py` | This-session utility scripts | Untracked. Delete or keep. |

### Master template
- `templates/collection-page-master.md` — internal documentation of the canonical Collection-page structure. Blocked from crawlers via `robots.txt`.

---

## Manifests

All in `images/zodiac/` — produced during Phase 2–5 webp generation:
- `western-signs-manifest.json` — 14 styles × 12 signs
- `realms/manifest.json` — 4 realms × 12 signs (each realm has variants)
- `chinese/manifest.json` — 2 styles × 12 animals
- `chinese-realms/manifest.json` — 1 realm × 12 animals (with 2 variants)

---

## Branches and tags

```
main                                          production — HEAD 8055f13 (pushed, clean, == origin/main)
cooking-stagger                               publish-script source branch (untouched this session)

backup-after-phase-6                          8055f13 (most recent — full 6-phase pass complete)
backup-pre-phase-3-handoff                    6273822 (pre-session checkpoint from prior session — handoff write)
backup-after-ls-chinese-signs-activation      9cab5c0 (site-wide LS rollout complete)
backup-after-ls-landscapes-activation         93e4bbf
backup-after-ls-western-signs-activation      6f2bbd9
backup-after-ls-realms-activation             a874693
backup-after-landscapes-msg-5e                0c559d6
backup-after-chinese-realms-msg-5d            4b9b524
backup-after-chinese-signs-msg-5c             efc1f1c
backup-after-western-realms-msg-5b            799bbfa
backup-after-western-signs-msg-5a             cf615cc
backup-after-western-signs-phase-5            0c98074 (pre-rollout 5A)
backup-before-zodiac-restructure              f7de811 (pre-restructure baseline)
...older tags below
```

**This session's commits above `backup-pre-phase-3-handoff` (`6273822`):**
- `01f0496` Phase 3 sitemap image entries
- `3a8de69` `_config.yml` Jekyll unblock
- `698b745` Phase 4 + 4.5 FAQ remediation
- `5519ed7` Phase 5 related-reading + H2 promotion
- `8055f13` Phase 6 blog filter

**Rollback options:**
- `git reset --hard backup-after-phase-6` — current state (no-op)
- `git reset --hard backup-pre-phase-3-handoff` — pre-session state (loses all 6 phases)
- `git reset --hard backup-after-ls-chinese-signs-activation` — pre-Phase 1 state (loses 6 phases + earlier Phase 1+2 commits)

---

## Important context (lessons reinforced this session)

- **GitHub Pages builds can silently fail two ways.** Standing #13 covers transient infrastructure (`actions/jekyll-build-pages` action download flake). New this session: Jekyll Liquid parser errors on tracked markdown content with literal `{{` — see Standing #14. Always verify live content via `curl` after a push.
- **Standing Instruction #7 (no city-level data) is hard-enforced.** When the Phase 1 brief asked to put "Wichita, Kansas" in the about-page Person schema, Josh confirmed the existing identity-hygiene rule still applies — state-level "Kansas" only, never any city on public pages. The brief is overridable by the standing instructions when there's a direct conflict.
- **Audit before editing.** Phase 4 was the read-only audit; Phase 4.5 was the remediation. The audit caught a real contraction-mismatch (`What's` vs `What is` on `first-time-homebuyer-mistakes.html`) that the user-supplied brief assumed was a missing Q&A. Asking ONE crisp question with a recommended default (Standing #1) saved adding a duplicate Q&A.
- **Preserve existing card HTML verbatim when slugs don't change.** The Phase 5 injector originally re-rendered EVERY card from a canonical library, which subtly changed unchanged-card descriptions. Fix: capture existing card chunks per-post and only render-from-library for new additions. The user caught this in the first sample diff.
- **Detect per-post indentation rather than hardcoding.** Phase 5 cards were at `block_indent + 2` in some posts (`50-30-20-rule...`) and `block_indent + 4` in others (`ultimate-budget-workbook.html`). Hardcoding broke one. Per-post detection via regex on the existing block solved it.
- **Match-the-site-conventions for small style choices.** Phase 6 originally added `font-style: italic` on `.blog-filter-input::placeholder`. The user flagged that the site's other inputs don't italicize their placeholders. Dropped the class-scoped rule entirely — the global `input::placeholder` rule already covered it. The kind of detail that keeps the site feeling cohesive.

### Build + deploy (unchanged from prior sessions)
- GitHub Pages → Fastly edge (10-min TTL). Pages build: 30s–2.5min when healthy.
- Claude sessions start in `C:\Users\jotra\.claude`; `cd /c/Users/jotra/builtbyjoshstudio` for git. The Bash tool's cwd resets between calls — always `cd`.
- `LF will be replaced by CRLF` warnings are benign for text files. Pre-commit hook in use (passing) — never `--no-verify`.
- Local preview: `mcp__Claude_Preview__preview_start name="static-site"` (python http.server :8080). Server stops between turns — just restart it.
- Untracked, keep untracked: `.claude/`, `.netlify/`, `HANDOFF*.md`.
- Python on Windows: use `python -X utf8` when reading manifests or files with non-ASCII content (default cp1252 will UnicodeDecodeError).

---

## Quick verification commands

```bash
cd /c/Users/jotra/builtbyjoshstudio
git status && git log --oneline -10

# Production spot-checks
curl -s -o /dev/null -w "%{http_code}\n" "https://builtbyjoshstudio.com/?x=$(date +%s)"                                       # 200
curl -s -o /dev/null -w "%{http_code}\n" "https://builtbyjoshstudio.com/about.html?x=$(date +%s)"                            # 200
curl -s -o /dev/null -w "%{http_code}\n" "https://builtbyjoshstudio.com/blog.html?x=$(date +%s)"                             # 200
curl -s -o /dev/null -w "%{http_code}\n" "https://builtbyjoshstudio.com/collections/aries-zodiac-art.html?x=$(date +%s)"     # 200

# Live Phase 1–6 markers
curl -fsS "https://builtbyjoshstudio.com/about.html?x=$(date +%s)" | grep -c "What I bring to the work"                                         # 1   Phase 1
curl -fsS "https://builtbyjoshstudio.com/collections/aries-zodiac-art.html?x=$(date +%s)" | grep -c "datePublished"                             # 1+  Phase 2
curl -fsS "https://builtbyjoshstudio.com/sitemap.xml?x=$(date +%s)" | grep -c "image:image"                                                     # 94  Phase 3
curl -fsS "https://builtbyjoshstudio.com/blog/why-solo-creators-stay-stuck-under-5k.html?x=$(date +%s)" | grep -c "Frequently Asked Questions"  # 1   Phase 4.5
curl -fsS "https://builtbyjoshstudio.com/blog/ultimate-budget-workbook.html?x=$(date +%s)" | grep -c '<h2 class="related-posts-label">'        # 1   Phase 5
curl -fsS "https://builtbyjoshstudio.com/blog.html?x=$(date +%s)" | grep -c 'id="blog-filter-input"'                                            # 1   Phase 6

# Pages build status
gh run list --workflow=pages-build-deployment --limit 5

# Sitemap entry count
curl -s "https://builtbyjoshstudio.com/sitemap.xml?x=$(date +%s)" | grep -c "<loc>"   # 91

# Card-count sanity across all 34 blog posts (Phase 5)
python -X utf8 -c "
import re
from pathlib import Path
for f in sorted(Path('blog').glob('*.html')):
    t = f.read_text(encoding='utf-8')
    n = len(re.findall(r'class=\"related-post-card\"', t))
    print(f'  {f.stem}: {n}')
"

# FAQ visibility audit (Phase 4 re-runnable)
python -X utf8 tools/_phase4_faq_audit.py | tail -5   # SUMMARY: 445 questions, 445 visible, 0 missing
```

---

**End of handoff.** State: live, clean — HEAD `8055f13` on `main`. Full Phase 1 → Phase 6 SEO optimization pass deployed and verified. Open items 1–6 carried forward; item 7 verified-and-noted. New session should start by reading this doc, running the "First steps" verification block, then awaiting Josh's instructions.
