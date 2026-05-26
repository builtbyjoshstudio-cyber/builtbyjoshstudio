# builtbyjoshstudio.com — Session Handoff

**Date:** 2026-05-26 (end of session; new Claude Code session starting fresh)
**Repo:** https://github.com/builtbyjoshstudio-cyber/builtbyjoshstudio
**Local path:** `C:\Users\jotra\builtbyjoshstudio`
**Host:** GitHub Pages — custom domain `builtbyjoshstudio.com` via CNAME → Fastly CDN
**HEAD (pushed):** `e6475a4` on `main`, in sync with `origin/main`. Pages deployment confirmed live as of `26450198794` build (Phase 1 + Phase 2 verified on live site).
**Latest backup tag:** `backup-after-ls-chinese-signs-activation` (`9cab5c0`). Several commits sit on top of that tag — see "Branches and tags" below; tag a new checkpoint if substantial new work happens.

---

## 🔴 STANDING INSTRUCTIONS — read these first

These are the rules Josh has set through hard pushback over multiple sessions. Apply them by default; only deviate if Josh says so explicitly.

### 1. Communication style: terse, directive, no preamble.
Josh's style. No padding. Surface tradeoffs in 1–2 sentences and pick a default; don't ask a dozen questions. When you find real ambiguity worth confirming, ask ONE crisp question with a recommended default. Skip "Great, I'll start by…" preambles.

### 2. The site has NO template engine.
Every HTML page is standalone with its own inline `<style>` block, its own JSON-LD, its own nav, its own footer. The Python scripts in `tools/` are the closest thing to a template engine — they generate per-page HTML from manifests + hardcoded sign/animal data. When you need to change something site-wide (e.g., add a footer link, inject a schema block), either (a) edit the generators and regenerate, or (b) write a Python sweep that visits every `.html` file. There's no shared partial to update.

### 3. Lemon Squeezy IS the primary checkout for the zodiac art Collections. Etsy is a secondary reference only.
**As of this session, the entire LS rollout is complete — all 77 buttons across 38 collection pages are live with real LS overlay URLs.** Tynkr products use the existing key-based `data-checkout` + `CHECKOUT_CONFIG` infrastructure (see `js/checkout.js`, `js/checkout-config.js`). The Collection pages use the `.ls-checkout-btn` pattern with `data-checkout-url` populated and the click handler in `js/ls-checkout-btn.js` (added this session).

### 4. Sales-channel hierarchy on Collection pages
- **Primary CTA:** the LS button (sidebar + final CTA band on every Collection page; Western Landscapes also has a top-of-grid bundle CTA)
- **Secondary reference:** a muted "Looking for something different? Visit the Etsy shop →" block at the bottom of the sidebar. Smaller text, no button styling, courtesy link only. Does NOT compete with the primary CTA visually.
- **Footer:** Etsy link stays in the global footer alongside Refunds/Privacy/Terms/Legal — that's a directory listing, not a sales CTA.

### 5. Verify file content claims against actual source code/data, not against documentation or assumptions.
The PDFs, the brief, your own memory — none of these are authoritative. The actual asset files (the webps in `images/zodiac/...`, the source files at `OneDrive\...\Zodiac Collections\`), the manifest JSONs, and the live pages are. When the brief says "24 print-ready files" but the actual file count is 144, flag the discrepancy and use the accurate number with a note.

### 6. LS URL activation procedure (still applies for future Collections / re-runs)
For each `<button class="ls-checkout-btn"...>` element:
1. Paste the LS overlay URL into `data-checkout-url=""`
2. Remove the `disabled` attribute and swap the button text from `Buy the X Bundle — Coming Soon` to `Buy the X Bundle — $<price>`

Generators implement this via per-Collection `LS_URL_BY_SIGN` / `LS_URL` dicts + an `ls_button_state()` helper. To add a new URL, just populate the dict entry and regenerate.

### 7. Identity hygiene rules (site-wide):
- **Founder name:** "Josh" only on every public-facing surface. Never "Joshua Tran" or "Josh Tran" or just "Tran". Pen name "J. S. Warden" appears only on fiction-author schema (about.html `workExample` block).
- **City-level data:** state-level "Kansas" only on public pages. **Never any city** — not in copy, not in schema. The ONLY exception is the registered agent address (Wichita, KS) which appears solely on `/legal/index.html` as a legitimate compliance surface. Confirmed reinforced this session — when the Phase 1 brief asked for "Wichita, Kansas" in the about-page Person schema's `occupationLocation`, Josh confirmed state-only.
- **`<meta name="keywords">`:** never. Already stripped from all 90+ HTML pages. Search engines ignored these since 2009 and on this site they leaked identity terms.

### 8. The site-wide Organization JSON-LD block is on every collection page, injected before `</head>`.
Stable `@id`: `https://builtbyjoshstudio.com/#organization`. Per-page Product/FAQ/etc. schemas `@id`-reference the Organization via `{"@id": "https://builtbyjoshstudio.com/#organization"}` for `manufacturer` and `seller`. Don't redefine the Organization inline elsewhere.

### 9. Schema rule for Collection pages: Product + FAQPage + BreadcrumbList + Organization per page.
- **Product schema** uses `@id: <page-url>#product` for stable referencing, SKU pattern `BBJ-<COL>-<SIGN>` (WS/WR/WL/CS/CR), `additionalProperty` block with the full file/design/format spec, single `Offer` at the bundle price `InStock`, plus `hasMerchantReturnPolicy: MerchantReturnNotPermitted` (added this session — applicable to all 38 collection pages), plus `datePublished` + `dateModified` (added this session as Phase 2 of the optimization pass).
- **FAQPage schema** must mirror the visible FAQ text exactly. Use the shared `faq_data()` / `faq_schema_data()` pair in the generators so visible HTML and schema build from a single source. Use ASCII-safe substitutions in the schema (`20" × 30"` → `20 by 30 inches`, etc.).
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
(Carried over from prior sessions. App source for each tool lives at `C:\Users\jotra\.gemini\antigravity\scratch\<slug>\`. Cooking queue is currently empty.)

### 13. GitHub Pages builds can fail on transient infrastructure issues. Check before assuming a deploy completed.
**Confirmed this session:** the `actions/jekyll-build-pages` action archive failed to download from `codeload.github.com` on two consecutive builds. Commits push fine; Pages just silently fails to deploy. Recovery: `gh run rerun <run_id> --failed` OR push an empty commit (`git commit --allow-empty -m "Trigger Pages rebuild"`). Always check live content with `curl ?x=<timestamp>` against expected new strings after a push. `gh run list --workflow=pages-build-deployment --limit 5` shows recent build status.

---

## 🟢 Status: live, clean — Section 5 + LS rollout complete; Phases 1+2 of SEO optimization pass deployed

Working tree clean (only the usual untracked: `.claude/`, `.netlify/`, dated `HANDOFF-*.md` archives, plus a handful of utility scripts from this session — see "Untracked artifacts" below). Cooking-stagger publish queue is empty (`tools/cooking-queue.json` = `[]`) and not in active use.

---

## First steps for the new session

```bash
cd /c/Users/jotra/builtbyjoshstudio
git status                                                  # clean (untracked: .claude/ .netlify/ HANDOFF*.md + a few _audit/_phase2 scripts)
git log --oneline -10                                       # HEAD e6475a4
git tag -l 'backup-*' --sort=-creatordate | head -5         # backup-after-ls-chinese-signs-activation newest
grep -c '<loc>' sitemap.xml                                 # 91
# Live deploy spot-check (current commit is e6475a4):
curl -fsS "https://builtbyjoshstudio.com/about.html?x=$(date +%s)" | grep -c "What I bring to the work"      # 1
curl -fsS "https://builtbyjoshstudio.com/collections/aries-zodiac-art.html?x=$(date +%s)" | grep -c "datePublished"  # 1+
# Pages build status (if curl shows old content, check):
gh run list --workflow=pages-build-deployment --limit 5
```

Expected: HEAD `e6475a4`, 91 sitemap entries, working tree clean, Pages build succeeded, live site serves the Phase 1 + Phase 2 content.

---

## What this session accomplished (chronological)

### Section 5: Master-template rollout (5 commits + 5 backup tags)

| Brief | Commit | Tag | What |
|---|---|---|---|
| 5A | `cf615cc` | `backup-after-western-signs-msg-5a` | Replicated Aries WS pattern across all 11 sister WS pages (Taurus through Pisces). 154 per-sign style descriptions written. |
| 5B | `799bbfa` | `backup-after-western-realms-msg-5b` | Built all 12 Western Realms pages from master template. 48 realm descriptions written; real titles lifted from `images/zodiac/realms/manifest.json`. |
| 5C | `efc1f1c` | `backup-after-chinese-signs-msg-5c` | All 12 Chinese Signs per-animal pages converted to master pattern with cultural context (factual + respectful, no horoscope tropes). |
| 5D | `4b9b524` | `backup-after-chinese-realms-msg-5d` | Chinese Realms single-bundle page on master pattern. 144 files / 24 designs / $29.99 confirmed via manifest. |
| 5E | `0c559d6` | `backup-after-landscapes-msg-5e` | Western Landscapes refresh to LS-direct $19.99 bundle. Removed all 12 per-landscape Etsy CTAs. 12 landscape titles + descriptions lifted verbatim from prior page. Sitemap lastmod refreshed for 27 collection pages. |

### LS-direct activation rollout (5 commits + 5 backup tags) — site-wide LS go-live

| Commit | Tag | What |
|---|---|---|
| `a874693` | `backup-after-ls-realms-activation` | First batch — WR (12) + CR (1) + new `js/ls-checkout-btn.js` handler. Lazy-loads `lemon.js`, opens overlay via `LemonSqueezy.Url.Open(url)`, falls back to new-tab. Kept separate from `js/checkout.js` per Standing Instruction #6. |
| `6f2bbd9` | `backup-after-ls-western-signs-activation` | WS (12) activation. |
| `93e4bbf` | `backup-after-ls-landscapes-activation` | WL (1) activation — 3 buttons (grid-intro CTA + sidebar + final CTA). |
| `9cab5c0` | `backup-after-ls-chinese-signs-activation` | CS (12) activation — **completes the site-wide LS rollout**. 77 live LS buttons across 38 pages, 0 disabled. |

### Schema + content patches

| Commit | What |
|---|---|
| `7ae841d` | Added `hasMerchantReturnPolicy: MerchantReturnNotPermitted` to all 38 collection-page Product schemas + master template doc. Clears the Google Rich Results "non-critical issues" warning. |
| `90642fc` | Homepage: added OG image (`images/og/og-home.webp`, 1200×630 WebP, ~36 KB) + tightened LLM-citable opener paragraph + fixed two heading-typo false-positives + removed stale Gumroad HTML comment. |
| `60d202f` | `llms.txt`: added "Free web utilities" section listing the 7 cooking calculators. |
| `1297625` | **Phase 1 of the SEO optimization pass.** About page gained "What I bring to the work" credentials section (5 sentences, 3 paragraphs, in Josh's voice — covers cooking heritage, two novel series, LLC ops, dogfooding, solo-creator scope). Person JSON-LD enriched with `hasOccupation` (state-level Kansas, no city per Standing Instruction #7), `publishingPrinciples`, `award`, and `workExample` (Overlayed Echoes Book + Ebonspire Chronicles BookSeries, both authored by "J. S. Warden"). |
| `d0b66b3` | **Phase 2 of the SEO optimization pass.** Added `datePublished` + `dateModified` = `2026-05-26` to all 47 Product-schema-bearing pages (8 product + 38 generator-output collection + 1 CS hub). Schema-only, no visible content changes. |
| `e6475a4` | Empty trigger commit — Pages build had failed twice on a GitHub-side `jekyll-build-pages` action download issue. Empty commit kicked a fresh build that succeeded. |

---

## What's live in production right now

### Collection pages — 38 pages, all on master pattern, all checkout-ready

| Page type | URL pattern | Count | LS buttons per page | Price |
|---|---|---|---|---|
| Per-sign Western Signs | `/collections/<sign>-zodiac-art.html` | 12 | 2 (sidebar + final CTA) | $24.99 |
| Per-sign Western Realms | `/collections/<sign>-zodiac-realms.html` | 12 | 2 | $14.99 |
| Per-animal Chinese Signs | `/collections/<animal>-chinese-zodiac-art.html` | 12 | 2 | $14.99 |
| Chinese Realms single bundle | `/collections/chinese-zodiac-realms.html` | 1 | 2 | $29.99 |
| Western Landscapes single bundle | `/collections/zodiac-landscapes.html` | 1 | 3 (top-of-grid + sidebar + final CTA) | $19.99 |
| **Total** | | **38** | **77 buttons** | |

All 77 buttons carry live `data-checkout-url`, no `disabled` attribute, button text reads `Buy the <X> Bundle — $<price>`. `js/ls-checkout-btn.js` script tag present on every page; opens the LS overlay on click.

### Site-wide schema state

Every collection-page Product schema now includes:
- `@id` reference to the canonical Organization
- `additionalProperty` block with the full file/design/format spec
- `hasMerchantReturnPolicy: MerchantReturnNotPermitted` (added this session)
- `datePublished: 2026-05-26` + `dateModified: 2026-05-26` (added this session)
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
- Sitemap: 91 `<loc>` entries, lastmod refreshed for collection pages
- `llms.txt` at root — well-structured, includes free web utilities section
- Homepage OG image at `images/og/og-home.webp` (1200×630), referenced by `og:image` + `twitter:image`

### Homepage `index.html` sections (order):
1. `#tynkr` — Tynkr Tools
2. `#builtbyjosh` — Western Signs Zodiac Art (12 cards)
3. `#western-realms` — Western Realms (12 cards)
4. `#chinese-zodiac` — Chinese Signs (12 cards)
5. `#chinese-realms` — Chinese Realms (12 cards, anchor to single bundle)
6. `#landscapes` — Western Landscapes (12 cards, anchor to single bundle)
7. `#free-tools` — 7 cooking utilities

### About page (`about.html`)
Sections in order (since Phase 1 added section #2):
1. Hi, I'm Josh.
2. **What I bring to the work** (new — credentials section)
3. The Two Brands
4. Beyond the Studio
5. Where the Studio Lives
6. Connect With the Studio

---

## Open items / pending work

### 🔴 IN PROGRESS — Six-phase SEO optimization pass

Josh sent a six-phase brief earlier in this session. **Phases 1 + 2 are committed, pushed, and deployed.** Phases 3–6 are not started. Each phase has approval gates per the brief; show diff before every commit.

| Phase | Status | What |
|---|---|---|
| 1 — About page credentials section + enriched Person schema | ✅ shipped (commit `1297625`) | — |
| 2 — `datePublished` + `dateModified` on all Product schemas | ✅ shipped (commit `d0b66b3`) | — |
| **3 — Image entries to sitemap.xml** | 🔴 NOT STARTED | Add `<image:image>` entries (with `xmlns:image` namespace if missing) to every `<url>` block in `sitemap.xml` for products + collections. Each entry includes `<image:loc>` pointing to the page's Product-schema `image` field (typically `/images/products/*.webp` or `/images/zodiac/...`). NOT for blog posts in this pass. Show first 3 modified `<url>` blocks before committing. Commit message: `Add image entries to sitemap.xml for products and collections` |
| **4 — FAQPage schema visibility audit** | 🔴 NOT STARTED | Read-only audit. For every HTML file with FAQPage schema, check whether each Q&A pair appears as visible content (h2/h3/h4/details/summary/dt, or any element with class containing "faq"). Report `[file]: X of Y FAQ questions visible`. Flag any file where schema Q&As are NOT visibly on the page. **Do not modify anything.** |
| **5 — Blog post cross-linking** | 🔴 NOT STARTED | Three sub-steps with approval gates. 5A: inventory all blog posts with slug, H1, topical category tags. 5B: build "Related reading" recommendation matrix (2–3 sideways topical neighbors per post, not currently linked, skewed away from same-product upsell). Show matrix as markdown table, **wait for approval**. 5C: edit each post to add/merge a "Related reading" H2 section near end of post body. Show representative diff (`blog/zero-based-budget-excel.html`) before committing the full set. Commit message: `Add Related reading cross-links to all blog posts` |
| **6 — Client-side filter search on blog index** | 🔴 NOT STARTED | Pure HTML/CSS/JS, no external deps. Filter input above post list, placeholder `Filter posts...`, case-insensitive substring match against post title + visible excerpt, live filtering on each keystroke, Escape clears, "No posts match that filter." for zero matches. Show diff + placement description before committing. Commit message: `Add client-side filter search to blog index` |

**Rules for the optimization pass (carry these forward):**
- Pause for approval between phases where indicated
- Do not modify files outside the scope of each phase
- Do not modify `robots.txt` or `llms.txt` (handled separately)
- Do not modify the homepage `index.html` in any phase
- Show a diff before every commit
- If any phase fails or hits a blocker, stop and report — do not try to recover and continue to the next phase

### Lower priority — pre-existing open items

- `tools/build_realm_pages.py` (Phase 2 legacy simpler Realms generator) is still in the repo. Can be deleted now that `build_realm_page_master.py` is canonical for all 12 WR pages.
- 5+ dated handoff archives accumulated as `HANDOFF-*.md` — untracked, kept locally for reference.
- The cooking-stagger publish queue (`tools/cooking-queue.json` = `[]`) is empty and inactive. Inherited from prior sessions.

### Untracked artifacts left in repo from this session

These are non-production scripts and audit outputs. Delete or keep — they don't affect the live site.

- `_audit_output.md` — 95 KB SEO audit report from earlier this session (the one handed to web Claude that initiated the 6-phase optimization brief)
- `tools/_audit_seo.py` — read-only SEO audit script
- `tools/_audit_addendum.py` — added the payhip/gumroad section + summary to the audit output
- `tools/_phase2_dates.py` — utility that injected `datePublished` + `dateModified` into the 8 hand-written Product-schema pages

---

## Critical configuration (unchanged from prior session except where noted)

| Item | Value |
|---|---|
| Legal entity | **Built by Josh Studio LLC** (Kansas) |
| Kansas Business ID | `10076138` |
| Registered Agent | Northwest Registered Agent LLC, 4601 E. Douglas Ave. STE 150, Wichita, KS 67218 (legal service only — only appears on `/legal/index.html`) |
| Email | `josh@builtbyjoshstudio.com` |
| Tynkr Tools & Co Etsy | `https://tynkrtoolsandco.etsy.com` |
| Zodiac (BBJ) Etsy | `https://www.etsy.com/shop/BuiltByJoshStudio` |
| LS store URL | `https://tynkrtoolsco.lemonsqueezy.com/` |
| **LS bundle URLs (Collection products)** | **All 38 live now.** Spec lives in each generator's `LS_URL_BY_SIGN` / `LS_URL_BY_ANIMAL` / `LS_URL` dict. |
| GA4 Measurement ID | `G-QDSPBB7S9J` (inline in every page's `<head>`) |
| Pen name (fiction only) | **J. S. Warden** — appears only on `about.html` Person `workExample` schema |
| Books in author schema | `Overlayed Echoes` (Book, near-future LitRPG/SciFi/Metafiction, on Amazon at `https://a.co/d/04YzP4o4`, being expanded into 5-book series), `Ebonspire Chronicles` (BookSeries, Dark Fantasy / Urban Fantasy / Noir Detective Fiction) |
| Pricing model | Western Signs $24.99 · Western Realms $14.99 · Chinese Signs $14.99 · Chinese Realms $29.99 · Western Landscapes $19.99 — **all 38 pages reflect these, all live LS overlay URLs in place** |

### Asset inventory (unchanged this session — Section 5 was page rebuilds, not asset gen)

| Section | Per-page designs | Hub thumb | Webps in repo |
|---|---|---|---|
| Western Signs | 24 (14 styles × 1–4 variants) | `images/zodiac/<sign>.webp` × 12 | 288 design + 12 hub |
| Western Realms | 8 (4 realms × 2 variants) | `images/zodiac/realms/<sign>.webp` × 12 | 96 design + 12 hub |
| Chinese Signs | 8 (4 hyper-realistic + 4 watercolor) | `images/zodiac/chinese/<animal>.webp` × 12 | 96 design + 12 hub |
| Chinese Realms | 2 per animal (single bundle, 24 total) | `images/zodiac/chinese-realms/<animal>.webp` × 12 | 24 design + 12 hub |
| Western Landscapes | 1 per sign | `images/zodiac/landscapes/<sign>.jpg` × 12 (still jpg — pre-existing) | 12 jpgs |

---

## Generators in `tools/` — current state

| Script | Purpose | Status |
|---|---|---|
| `build_western_signs_page.py` | 12 Western Signs per-sign pages | Master pattern, has `STYLE_COPY_BY_SIGN` + `HERO_TAGLINE_BY_SIGN` + `PLANET_SYMBOL_TAIL_BY_SIGN` + `WHAT_MAKES_PARAS_BY_SIGN` + `LS_URL_BY_SIGN` (all 12 live) |
| `build_realm_page_master.py` | 12 Western Realms per-sign pages | Master pattern, has `REALM_COPY_BY_SIGN` + `ZODIAC_CONTEXT_PROSE` + `HERO_TAGLINE_BY_SIGN` + `LS_URL_BY_SIGN` (all 12 live) |
| `build_chinese_animal_pages.py` | 12 Chinese Signs per-animal pages | Master pattern (rewritten this session), has `ANIMAL_META` + `WHAT_MAKES_ANIMAL_PROSE` + `HERO_TAGLINE_BY_ANIMAL` + `LS_URL_BY_ANIMAL` (all 12 live) |
| `build_chinese_realms_page.py` | 1 Chinese Realms single-bundle page | Master pattern (rewritten this session), has `LS_URL` constant (live) |
| `build_zodiac_landscapes_page.py` | 1 Western Landscapes single-bundle page | Master pattern (created this session), has `LS_URL` constant (live) — 3-button page (grid-intro + sidebar + final CTA) |
| `build_realm_pages.py` | Phase 2 legacy simpler WR generator | **Obsolete** — `build_realm_page_master.py` covers all 12 now. Safe to delete. |
| `update_western_sign_pages.py` | Phase 5 surgical updater | Idempotent. Probably done. |
| `identity_cleanup.py` | Identity hygiene sweep | Idempotent. Has the canonical Organization schema embedded. |
| `phase3_apply.py`, `phase4_apply.py` | Phase atomic apply scripts | Already executed. |
| `publish_next_cooking.py`, `publish-next-cooking.ps1` | Cooking-stagger publish queue | Inherited. Queue empty. |
| `_audit_seo.py`, `_audit_addendum.py`, `_phase2_dates.py` | This-session utility scripts | Untracked. Delete or keep. |

### Master template
- `templates/collection-page-master.md` — internal documentation of the canonical Collection-page structure. Updated this session with the `hasMerchantReturnPolicy` requirement. Blocked from crawlers via `robots.txt`.

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
main                                          production — HEAD e6475a4 (pushed, clean, == origin/main)
cooking-stagger                               publish-script source branch (untouched this session)

backup-after-ls-chinese-signs-activation      9cab5c0 (most recent session tag — site-wide LS rollout complete)
backup-after-ls-landscapes-activation         93e4bbf
backup-after-ls-western-signs-activation      6f2bbd9
backup-after-ls-realms-activation             a874693
backup-after-landscapes-msg-5e                0c559d6
backup-after-chinese-realms-msg-5d            4b9b524
backup-after-chinese-signs-msg-5c             efc1f1c
backup-after-western-realms-msg-5b            799bbfa
backup-after-western-signs-msg-5a             cf615cc
backup-after-western-signs-phase-5            0c98074 (pre-session 5A)
backup-before-zodiac-restructure              f7de811 (pre-restructure baseline)
...older tags below
```

**6 commits sit above the most recent tag (`backup-after-ls-chinese-signs-activation`):**
- `7ae841d` schema: hasMerchantReturnPolicy
- `90642fc` homepage OG image + opener + headings + Gumroad cleanup
- `60d202f` llms.txt free utilities section
- `1297625` Phase 1 about page
- `d0b66b3` Phase 2 dates
- `e6475a4` Pages rebuild trigger

Worth tagging a new checkpoint before Phase 3 starts.

**Rollback options:**
- `git reset --hard backup-after-ls-chinese-signs-activation` — keeps the entire LS rollout, loses schema patches + homepage OG + llms.txt utilities + Phases 1+2
- `git reset --hard backup-after-landscapes-msg-5e` — keeps Section 5, loses ALL LS activation + everything after
- `git reset --hard backup-before-zodiac-restructure` — pre-restructure baseline (would lose months of work)

---

## Important context (hard-won lessons from this session)

- **GitHub Pages builds can silently fail** on transient infrastructure issues even when your code is fine. The fix is `gh run rerun <id> --failed` or an empty trigger commit. Always verify live content after a push if anything seems off. (See Standing Instruction #13.)
- **Standing Instruction #7 is hard-enforced:** when the Phase 1 brief asked to put "Wichita, Kansas" in the about-page Person schema, Josh confirmed the existing identity-hygiene rule still applies — state-level "Kansas" only, never any city on public pages. The brief is overridable by the standing instructions when there's a direct conflict.
- **JSON-LD with double-braces in f-strings** — all 5 generators use Python f-strings with `{{` and `}}` to escape literal braces. When making bulk edits, match the source-code pattern (`{{`), not the rendered HTML pattern (`{`).
- **The CS hub (`chinese-zodiac-art.html`) has 13 Product blocks** — 1 top-level Product, plus 12 nested inside an ItemList. Schema changes should only touch the top-level one unless explicitly intended otherwise.
- **The about page Person schema name field is "Josh"; the workExample author is "J. S. Warden".** That's deliberate — fiction is published under the pen name, everything else is "Josh".
- **Approach B is the default for collection-page changes:** edit the 5 generators, regenerate, validate. Never hand-edit one collection page and not the others — the visible-HTML / schema / sister-page drift will bite.
- **Per Standing Instruction #1**, surface real ambiguity as ONE crisp question with a recommended default. The Wichita question in Phase 1 was the right call — saved a revert.

### Build + deploy (unchanged from prior sessions)
- GitHub Pages → Fastly edge (10-min TTL). Pages build: 30s–1min when healthy.
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
curl -s -o /dev/null -w "%{http_code}\n" "https://builtbyjoshstudio.com/collections/aries-zodiac-art.html?x=$(date +%s)"     # 200

# Live content checks (Phase 1 + Phase 2)
curl -fsS "https://builtbyjoshstudio.com/about.html?x=$(date +%s)" | grep -c "What I bring to the work"                       # 1
curl -fsS "https://builtbyjoshstudio.com/collections/aries-zodiac-art.html?x=$(date +%s)" | grep -c "datePublished"           # 1+

# Pages build status (only matters if a recent push isn't showing live)
gh run list --workflow=pages-build-deployment --limit 5

# Sitemap entry count
curl -s "https://builtbyjoshstudio.com/sitemap.xml?x=$(date +%s)" | grep -c "<loc>"   # 91

# All 10 Collection PDF liveness (one-shot)
for f in license-western-signs license-western-realms license-western-landscapes license-chinese-signs license-chinese-realms print-guide-western-signs print-guide-western-realms print-guide-western-landscapes print-guide-chinese-signs print-guide-chinese-realms; do
  code=$(curl -s -o /dev/null -w "%{http_code}" "https://builtbyjoshstudio.com/legal/${f}.pdf?x=$(date +%s)")
  printf "  %-40s %s\n" "${f}.pdf" "$code"
done

# All 38 collection pages have hasMerchantReturnPolicy + dateModified
python -X utf8 -c "
import re
from pathlib import Path
pages = sorted([p for p in Path('collections').glob('*.html') if p.name not in ('chinese-zodiac-art.html','index.html')])
for p in pages:
    t = p.read_text(encoding='utf-8')
    print(p.name, 'mrp=', 'hasMerchantReturnPolicy' in t, 'date=', 'dateModified' in t)
" | grep -c "True True"   # 38
```

---

**End of handoff.** State: live, clean — HEAD `e6475a4` on `main`. Site-wide LS checkout is fully live across 38 collection pages. SEO optimization pass: Phases 1 + 2 deployed, Phases 3–6 pending. New session should start by reading this doc, running the "First steps" verification block, then awaiting Josh's instructions on Phase 3.
