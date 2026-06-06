# 🟢 builtbyjoshstudio.com — Session Handoff (2026-06-05) — Kinetic re-theme is LIVE + design unified

**This block is the current live state. The dated handoff below it (2026-06-04) is the prior shipped state — its STANDING INSTRUCTIONS (sections #1–#21) still apply verbatim. Ignore that block's stale "Status / First steps / Open items" — they predate the Kinetic flip.**

**STATE:** `main` HEAD = `e330c46` = `origin/main` (in sync; everything pushed + live + deploy-verified). Tracked tree clean (untracked only: `.claude/`, `.netlify/`, `tools/_*.py` sweep scripts, `tools/_fonts/`, `HANDOFF-*.md`, `SITE-OVERVIEW.md`). **`main` IS production** — each push deploys live via GitHub Pages' default `pages-build-deployment` (~50–70s; no workflow file). **Commit on `main`; push ONLY on Josh's explicit go; verify live cache-busted (`?x=<ts>`) after every push.** Nothing mid-flight.

## ✅ SHIPPED THIS SESSION — all live, each with a local backup tag (instant rollback)
The Kinetic re-theme was flipped live, then the whole **card/tile system was unified across the site**. Commits (newest first):
1. `e330c46` **Homepage zodiac sections unified** — the 3 Chinese/Landscape section headers had an identical generic "Built By Josh Studio" eyebrow + plain title; converted to the Western **style-A** form (`.section-header-bbj reveal` + orange `<span>` accent on "Art Prints"), titles/subtitles preserved. Added the `::before` orange corner-glow to `#chinese-zodiac` + `#landscapes` (were missing it). `tools/_kinetic_zodiacheaders.py` + `_kinetic_zodiacglow.py`.
2. `f97c488` **Homepage "About the Studio" section layout** — was `display:flex` where the brand-cards' wide max-content crushed the text to ~3 words/line; now a 2-col grid (text `1.2fr` / brand cards `1fr`, cards stacked). `tools/_kinetic_aboutsection.py`.
3. `45ba749` **Related Reading cards** (35 posts) — `.related-post-card` → blog `.article-card` chrome + blue "Read" button; `text-decoration:none !important` beats the `.article-body a` underline. Regex-per-rule sweep `tools/_kinetic_relatedcards.py` (handles spaced + minified inline-CSS variants).
4. `884f126` **Homepage Tynkr product tiles** — `.card-tynkr` → Kinetic chrome. `tools/_kinetic_homeproducttiles.py`.
5. `f34b856` **Homepage free-tools tiles** — now BYTE-IDENTICAL to `/free/`'s `.home-tool-card`. `tools/_kinetic_homefreetiles.py`.
6. `bb68a92` **About page** — de-glassed; brand tiles two-tone (Tynkr light/blue, Built-By-Josh **dark "stardust"** CSS starfield + white shadow); Connect tiles → blog-tile chrome. `tools/_kinetic_about.py` + `_kinetic_about_bbj.py`.
7. `adf84c9` **Resources page** → matches `/free/` (centered de-glassed hero, mono orange eyebrow, uppercase title) + video tiles → Kinetic chrome (kept their size). `tools/_kinetic_resources.py`.
8. `1ad0ff1` **Blog** — post cards → Kinetic chrome + blue "Read More"; hero → Tynkr-style (left, blue dash-eyebrow, Kinetic subscribe form). `tools/_kinetic_blogcards.py` + `_kinetic_bloghero.py`.
9. `aca6ac3` **Denser full-page starfield** — collections use a `position:fixed` dense starfield (whole-page); homepage dark zodiac hero + all 5 dark zodiac sections got it too (light Tynkr zone stays starless). `tools/_kinetic_stars.py`.
10. `166ff2f` **KINETIC SITE-WIDE RE-THEME FLIPPED LIVE** — fast-forward merge of the (now-stale) `kinetic-retheme` branch → `main` + push. The whole site is Kinetic v5; theme-only conversion proven byte-identical on JSON-LD/meta/prices/commerce/identity. **Pre-flip rollback tag: `pre-kinetic-backup` = `39dc1e9`.**

## 🎨 KINETIC DESIGN SYSTEM (match future components to this)
- **Theme:** warm cream `--canvas`#f1eee6, white `--surface`#fff, ink `--ink`/`--line-2`#14130e, light line `--line`#e2ddd0, blue `--accent`#2438e8 (Tynkr/tools), orange `--accent-2`#ff5a30 (zodiac), `--shadow`#14130e, `--muted`#6d695d. Fonts self-hosted in `css/fonts/`: **Bricolage Grotesque** (display/h), **Hanken Grotesk** (UI/body), **JetBrains Mono** (labels). NO glassmorphism/backdrop-filter.
- **Single Light theme EXCEPT zodiac = DARK:** homepage zodiac zone + all 40 collections + collections hub + `legal/index.html` carry `html[data-theme="dark"]` → the tokens.css `[data-theme="dark"]` block flips canvas/surface/ink/etc. to warm-dark.
- **Standard card chrome** (used everywhere now): `background:var(--surface); border:2px solid var(--line-2); border-radius:14px; box-shadow:6px 6px 0 var(--shadow);` hover = `transform:translate(3px,3px); box-shadow:2px 2px 0 var(--shadow)` (press-down). Canonical refs: `blog.html .article-card`, `free/index.html .home-tool-card`. Buttons: blue `var(--accent)` (tools/blog "Read"), orange `var(--accent-2)` (zodiac/lite CTAs), uppercase Hanken.
- **tokens.css loads AFTER each page's inline `<style>`**, so its `:root` wins duplicate vars — the `--tynkr-*`/`--bbj-*`/`--body-read` legacy aliases there centrally drive most pages. But card/tile chrome is per-page inline CSS, so component restyles are per-file sweeps.
- **Dark "stardust"** (About BBJ tile, `tools/_kinetic_about_bbj.py`) = CSS multi-`radial-gradient` white dots (static, no JS). The real twinkling starfield (`.stars`+JS) is on the dark zodiac pages/sections.

## 🛠 WORKFLOW / GOTCHAS (this session's proven pattern)
- **EOL:** working tree is CRLF; Write/Edit tools emit LF. Do multi-file/inline-CSS edits as **EOL-preserving Python byte-sweeps** (`tools/_kinetic_*.py`: read bytes → detect CRLF → normalize to LF → str/regex replace → restore CRLF → write). Dry-run (no `--write`) reconciles match counts FIRST; **`git diff --check` clean = proof**. For inline-CSS that varies (spaced vs minified, rgba spacing), match a **regex per rule**: `\.selector\s*\{[^{}]*\}`.
- **THEME/VISUAL ONLY (hard rule):** never change JSON-LD (`<script type="application/ld+json">`), `<meta>`, prices, Lemon-Squeezy/Etsy URLs, GA4, canonicals, or identity copy ("Josh"/"J.S. Warden"/"Kansas"/"AI-crafted"; Etsy secondary). Prove it: `git diff | grep -E '^[+-]'` over changed lines contains **zero** protected tokens.
- **PREVIEW (preview-MCP `static-site` on :8080):** `preview_start` (reuse is fine — a prior process serving the repo; idles out between turns, just start again) → `preview_eval(window.location.assign('/<page>?v=N'))` → verify with `preview_eval(getComputedStyle(...))` (more reliable than screenshots for colors/fonts) + `preview_screenshot`. **Screenshot gotchas:** wide viewports (≥1280) sometimes render the capture tiny/top-left and don't reflect a programmatic scroll — use **~900–960px** width (`preview_resize`) for clean section shots; defeat the scroll-reveal with `document.querySelectorAll('.reveal.hidden,.hidden').forEach(e=>e.classList.remove('hidden'))`. **CSS cache:** inline per-page CSS busts via `?v=N` on nav; shared `/css/*.css` may be cached by the reused renderer (force-reload cloned `<link ...?bust=N>`) — the LIVE site always serves fresh.
- **Push protocol:** `git tag backup-pre-<x>` at live HEAD → `git add -u` (stages tracked mods only; sweep scripts stay untracked) → confirm scope (`git diff --cached --name-only`) → commit via `-F -` heredoc (end with `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`) → `git push origin main` → `gh run watch <id> --exit-status` → curl live `?x=<ts>` to verify. Rollback any arc: `git reset --hard <backup-tag> && git push --force origin main`.

## OPEN / DEFERRED (none blocking)
- **Logo recolor** (`images/logo/*` bitmaps bake navy/gold) — Josh/external. (The dark About "Built By Josh Studio" brand tile shows the logo on its own light tile, so it reads OK; a recolor would let it sit on pure dark.)
- Stale `kinetic-retheme` branch (`166ff2f`, merged) can be deleted. `overlayed-echoes-preview.html` intentionally bespoke (no tokens.css). `og-home.webp` is a designed Kinetic card.
- Backup tags this session (newest first): `backup-pre-zodiacfix` · `backup-pre-aboutfix` · `backup-pre-cardsweep` · `backup-pre-homefreetiles` · `backup-pre-about` · `backup-pre-resources` · `backup-pre-blogstyle` · `backup-pre-stars` · `pre-kinetic-backup` (`39dc1e9`, pre-flip). LOCAL only (`git push` doesn't carry tags).
- Older deferred items still valid from the dated handoff below: title/meta CTR watch, future-pass B (og/twitter/headline sync on 6 pages), Ebonspire June-2026 launch, OG images for ~22 older posts.

## First steps for the new session
```bash
cd /c/Users/jotra/builtbyjoshstudio
git status                                  # tracked tree clean (untracked .claude/, tools/_*.py, HANDOFF-*.md)
git log --oneline -11                       # HEAD e330c46; this session = 166ff2f..e330c46
git tag -l 'backup-pre-*' --sort=-creatordate | head
ts=$(date +%s)
curl -fsS "https://builtbyjoshstudio.com/?x=$ts" | grep -c 'Bricolage Grotesque'    # >0 = Kinetic live
curl -fsS "https://builtbyjoshstudio.com/?x=$ts" | grep -c 'Syne'                    # 0 = old glassmorphism gone
gh run list --workflow=pages-build-deployment --limit 3                              # latest completed/success
```
Then take direction from Josh. The site is fully Kinetic and the card/tile system is unified site-wide (homepage free-tools + Tynkr products, /free/, resources, about, blog hub + posts + related-reading). Nothing mid-flight.

---

# builtbyjoshstudio.com — Session Handoff

**Date:** 2026-06-04 (session: **executed Arc 6 — the tools-subdomain relink** (`c80810f`): 84 link/JSON-LD swaps across 16 live files → `tools.builtbyjoshstudio.com`, pushed + live; **decommissioned the 7 old tool repos** (Pages disabled → 404, repos archived/read-only); then an **SEO title/meta rewrite on 8 under-clicking pages** (`7af3ce1`, pushed + live). Prior session's OE character cluster + income post + no-email rename remain live.)
**Repo:** https://github.com/builtbyjoshstudio-cyber/builtbyjoshstudio
**Local path:** `C:\Users\jotra\builtbyjoshstudio`
**Host:** GitHub Pages — custom domain `builtbyjoshstudio.com` via CNAME → Fastly CDN (~10-min edge TTL). **No CI workflow file in the repo**; GitHub's *default* `pages-build-deployment` fires on every push to `main` (~45–70s). **There is NO branch/PR workflow — `main` IS production; pushing `main` deploys live.** Commit on `main`, push only when Josh says.
**HEAD:** everything this session is **pushed to `origin/main`, live, post-deploy-verified** — last live commit **`7af3ce1`** (title/meta SEO rewrite), with **`c80810f`** (tools-subdomain relink) under it. This HANDOFF refresh is the commit on top — **unpushed** (HANDOFF is Jekyll-excluded, no live effect); first-steps will show `[ahead 1]`. **Ask Josh whether to push it.** Working tree otherwise clean (usual untracked only).
**Latest backup tags (LOCAL only — `git push` doesn't carry them):** `backup-pre-title-meta` (`c80810f`) · `backup-pre-tools-relink` (`a4a72d9`) · `backup-pre-stage2` (`ef2ef68`) · `backup-pre-character-cluster` (`47faaa1`) · earlier arc tags remain.

---

## 🧭 Session summary (plain language)

This session ran **three shipped arcs** (all pushed, live, post-deploy-verified), each a gated canary→batch with backup tag, dry-run, diff-before-commit, and Josh's explicit go before every push and every destructive/outward-facing step.

**Arc 6 — tools-subdomain relink (`c80810f`).** Executed the previously-reviewed brief: blanket host swap `builtbyjoshstudio-cyber.github.io/<slug>/` → `tools.builtbyjoshstudio.com/<slug>/` across **16 live files** (index, free/, llms.txt, 13 cooking posts) — **84 occurrences / 81 lines** (hrefs + 4 JSON-LD `"url"` + the one blessed display-URL at `building-the-universal-recipe-scaler.html:469`). EOL-preserving binary `bytes.replace`; slugs/trailing-slashes preserved; anchor text untouched except 469. Verified: old host → **0** across all 16; live HTML serves the new host.

**Decommission of the 7 old tool repos (GitHub settings — no commits).** After Josh independently verified the live main site: **Pages disabled** on all 7 via `gh api -X DELETE …/pages` → old `github.io/<slug>/` URLs now **404**; then **archived** all 7 via `PATCH archived=true` → read-only (reversible, history preserved). Canary-first each time (`brine-calculator`), then batch; `tools` (new subdomain) + `builtbyjoshstudio` (main site) untouched — new URLs still 200.

**Title/meta SEO rewrite (`7af3ce1`).** Search Console: 8 pages earning impressions but few/zero clicks. Audited current vs proposed, **flagged 2 overpromises** (a "free template" with no free template on the page; an "actually used" case-study framing the post explicitly disavows), then applied **title and/or meta only** on 8 pages (7 budget/creator blog posts + `creator-content-os` product page) — **13 lines**. No body/headings/schema/structured-data. **CTR watch tracked in Open items** (baseline + read-date there, to avoid drift).

**✅ All three pushed, live, post-deploy-verified. 7 old tool repos archived + Pages-off (404). Working tree clean, nothing mid-flight.** (Prior session's OE character cluster + income post + no-email rename remain live at/under `17de766`.)

---

## 🔴 STANDING INSTRUCTIONS — read these first

Rules Josh has set through hard pushback. Apply by default; deviate only if Josh says so explicitly.

### 1. Communication: terse, directive, no preamble.
Surface tradeoffs in 1–2 sentences and pick a default. Real ambiguity → ONE crisp question with a recommended default. No "Great, I'll start by…".

### 2. Verify against source, never assume. (Josh's #1 recurring catch.)
**Confirm against the repo (or live bytes) before changing anything.** When a premise is off, **STOP and flag** (this session: the relink brief claimed a `/tools/` index + `/resources/` tool links — neither exists; and `theo-min.png` was a DejaVu *mock* with baked text, not a clean source — both caught by checking, not assuming). Verify config VALUES and full coverage, not comments or first-read assumptions. When re-applying anything, prove the prior commit is live first (grep old strings → none; `git merge-base --is-ancestor <sha> origin/main`).

### 3. The site has NO template engine — pages are standalone.
Every `.html` is a complete document with its own inline `<style>`, JSON-LD, nav, footer. **No Jekyll layouts/includes/front matter.** Site-wide change = edit a `tools/` generator and regenerate, OR a Python sweep over every `.html`. **Exception:** `/css/tokens.css` (design tokens + the `data-glass` system) is loaded by all chrome pages.

### 4. Sweep mechanics (proven) — prefer a match-checked `tools/_*.py` script for multi-file edits.
Detect per-page depth prefix (root `""`, nested `../`, 2-deep `../../`, root-absolute `/`); preserve active-state; exclude bespoke pages. Sweep scripts live as **untracked `tools/_*.py`**; **dry-run before `--write`**; **reconcile the tally** (count replacements per old-string; 0 = MISS → fix). **Be eol-preserving** (see #20). **Always re-grep the WHOLE tree (and the LIVE site, cache-busted) AFTER `--write`.**

### 5. Commerce — Lemon Squeezy primary, Etsy secondary.
- **Single source of truth for checkout = `/js/checkout-config.js`** — `window.CHECKOUT_CONFIG`, **8 paid + 8 lite** SKUs, each `{name, price, category, ls:<LS URL ?embed=1>, etsy:<listing>}`. Product-page buttons use `data-checkout="<key>"`; `/js/checkout.js` wires them: paid → LS overlay on-domain; **$0 lite → LS hosted checkout (new tab, strips `?embed=1`)**. **Never hardcode a checkout URL outside `checkout-config.js`.**
- **The 8 lite SKUs are LIVE ($0 lead magnets) — and the $0 download CAPTURES AN EMAIL** (a $0 LS *purchase*; "email required for the purchase only"). The **free cooking tools + the Notion-Marketplace path need NO email**. So "no email" is true for Notion-Marketplace + cooking tools, **NOT for the on-site `/free/` lite download.** Don't write "no email" copy about the Lite downloads.
- **Blog-post buy buttons point to on-site `/products/<slug>.html`** — NOT Etsy, NOT the LS overlay directly. Upgrade code is entered in the product page's overlay at checkout on-site. Blog/upgrade copy: "Apply it at checkout" / "35% off the full version" (no platform), never "…on Etsy".
- **`btn-etsy` / `btn-inline-etsy` is a shared orange-CTA style, NOT Etsy-only** — keep the class when repointing.
- Etsy is never the lead CTA. **Etsy brand split (footers):** zodiac collection pages → `etsy.com/shop/BuiltByJoshStudio`; everything else → `tynkrtoolsandco.etsy.com`. A price change touches **3+ places** (HTML + JSON-LD Offer + homepage `#tynkr` card).

### 6. Identity hygiene.
"Josh" only (never the real surname, never "Joshua"). Pen name `J.S. Warden` — **no spaces** in copy/schema. City = state-level "Kansas" only (Wichita only on `/legal/index.html`). Never `<meta name="keywords">`.

### 7. Founding dates.
Studio **started 2025** (narrative), **incorporated as Built by Josh Studio LLC in 2026**. Schema `foundingDate` = `2026-05-13`. index.html brand node `2025`, Tynkr sub-org `2026`.

### 8. Site-wide Organization JSON-LD (`@id …/#organization`) — reference, don't redefine.
Cross-link fiction pages to canonical `@id`s: author `…/books.html#jswarden`, OE Book `…/books.html#overlayed-echoes`. **Reference existing `@id`s; never redefine/invent.** (Minting a NEW `@id` for a NEW entity — e.g. a `…#theo` Person node — is correct, not a violation.) Product/`/free/`/character pages carry the same site-wide Org node by design.

### 9. Schema rules — and FAQ/Offer/ItemList mirrors must stay in sync with visible copy.
Product/collection: Product + Offer + FAQPage + BreadcrumbList + Organization. Blog posts: **Article** + BreadcrumbList (+ related Product/Offer). Fiction dispatches: **BlogPosting** — never FAQPage. `/free/`: CollectionPage + ItemList + BreadcrumbList + Org. Character pages: BreadcrumbList + **Person** + Org (NO FAQPage). No `aggregateRating`/`review`, no `ReadAction`, no affiliate `tag=`.
- **FAQPage `acceptedAnswer.text` mirrors the visible `<p>` byte-for-byte; an Offer/Product `"url"` mirrors its visible buy link; and `blog.html`'s ItemList `name`/`url` mirror each visible blog card 1:1** (every blog.html section has a parallel ItemList — add a card, add its position twin). The Edit tool's "Found 2 matches" is the tell you forgot the schema copy.

### 10. Collection pages: edit via `tools/` generators, not by hand.
~5 generators (`build_western_signs_page.py`, etc.). `collections/chinese-zodiac-art.html` = hand-written **minified** hub — block-level edits only.

### 11. Antigravity owns the cooking apps. You write blog posts about them, never the apps.
The 7 free cooking utilities are external apps, **now served from `tools.builtbyjoshstudio.com/<slug>/`** (the consolidated `tools` repo). **Arc 6 relink DONE (`c80810f`, live):** every main-site link — homepage "Free Tools", `/free/`, `llms.txt`, 13 cooking/build-story posts (16 files, 84 hits) — was repointed off the old `builtbyjoshstudio-cyber.github.io/<slug>/` host. The **7 old per-slug repos are now archived + Pages-disabled** (old URLs 404). (These tools genuinely need **no email** — see #5.)

### 12. Pages build can fail on transient infra.
Recovery: `gh run rerun <id> --failed` OR push an empty commit. **Always verify live with a cache-busted request** (`?x=<ts>`) and confirm `pages-build-deployment` `completed/success` first. `gh run watch <id> --exit-status` blocks. (The Node-20-deprecation annotation on every run is benign — GitHub default infra, no workflow file.)

### 13. Jekyll excludes HANDOFF in `_config.yml`.
`HANDOFF.md` + `HANDOFF-*.md` excluded. Any new tracked top-level markdown with `{{` needs the same. **The dated `HANDOFF-*.md` archives + this file still mention the old `…github.io/<slug>/` host in narrative — intentional (historical); the LIVE tree has 0 old-host refs after `c80810f`.**

### 14. GA4 (ID `G-QDSPBB7S9J`) — only analytics installed.
Inline `gtag` in **every** `<head>` + `/js/ga4-events.js`: `etsy_click` (guarded to `etsy.com` hrefs only — cooking-tool/`/free/`/blog→product links fire nothing). `checkout.js` fires `add_to_cart` on any `[data-checkout]`. **Amazon click-outs:** `book_amazon_click` (`outbound:true, transport_type:'beacon'`). **Character pages** carry an inline `data-char-cta` handler: amazon→`book_amazon_click`(beacon), preview/dispatch→`select_content`, card/`card-stage2`→`file_download` (per-character `file_name`, `source_page=character-<slug>`) — mirrors the `overlayed-echoes-preview.html` preview-PDF `file_download` pattern.

### 15. Navigation & footer are STANDARDIZED — don't let them drift.
- **Header nav (every chrome page):** `Tynkr Tools · Zodiac Art · Blog · Resources · Free · About · Writing · Legal`. Depth-aware hrefs; `class="active"` per section. **"Free" → `/free/`** (root-absolute).
- **Footer:** Home/Blog/Resources/About/Writing/Legal/Etsy/Substack/Contact/Refunds/Privacy/Terms. Etsy brand-split per #5.
- **Bespoke (excluded from sweeps):** `index.html` (bespoke footer; nav IS standard), `overlayed-echoes-preview.html` (bespoke), `free/index.html` (hand-authored). The `/writing/characters/` pages + hub are 2-deep (`../../` + root-absolute paths).

### 16. The fiction layer = `/books.html` + preview + 6 dispatches + `/writing/` index + **`/writing/characters/` (#19)**.
- **`books.html`** — J.S. Warden hub; OE Book schema **3 editions** (#17); now links "Meet the five friends →" → `/writing/characters/`.
- **`overlayed-echoes-preview.html`** (bespoke, excluded) — free Ch.1–2, 3 CTAs (hero/end paperback `06ZWovoY`, mid Kindle `026ie1Si`). Has the `file_download` pattern for `overlayed-echoes-sample.pdf`.
- **`/writing/`** — index + 6 dispatches (BlogPosting, NO FAQPage), unlisted in nav, built by `tools/_build_dispatches.py`.
- **`/writing/characters/` — the OE character cluster (5 pages + hub, Stage 1 + Stage 2). See #19.** Unlisted in nav; surfaced via books.html + cross-links.

### 17. OE facts — **THREE editions (verified — use exactly).**
*Overlayed Echoes* = near-future **LitRPG**, 257-page, **Book 1 of a planned 5**, Kindle + paperback + hardcover + **KU**. Set 2045. NOT noir (that's Ebonspire). Print pub **2025-09-01**. Author store `https://www.amazon.com/stores/J.-S.-Warden/author/B0FPQ3RWWF`.

| Edition | ASIN | ISBN-13 | Price | a.co |
|---|---|---|---|---|
| Kindle | `B0H3826V21` | — | $5.99 (free on KU) | `https://a.co/d/026ie1Si` |
| Paperback | `B0H39RRSNF` | 979-8199065542 | $12.99 | `https://a.co/d/0cQASed2` |
| Hardcover | `B0H3Q66YH9` | 979-8199641265 | $23.99 | `https://a.co/d/03rhvH3N` |

- `numberOfPages:257` on PRINT editions only. **a.co caveat:** `06ZWovoY` = the PAPERBACK; visible Amazon CTAs (incl. the character pages + dispatches) use `06ZWovoY`, books.html schema uses `0cQASed2`. Resolve a.co → `/dp/ASIN` before use.
- **The five friends:** Kael (game master), Theo (guardian), Angela (healer, Theo's sister), Marcus (trickster), Lena (mage, Kael's adopted sister). Sibling pairs: Theo↔Angela (blood), Kael↔Lena (adopted). Their Stage-2 fantasy selves + stats are in #19.
- **Ebonspire Chronicles:** dark-fantasy detective noir, releases June 2026, unreleased (no Offer). Pre-release treatment intact.
- **Chinese-zodiac art bundles:** $14.99 each.

### 18. Architecture quick-reference.
**~110 HTML files** (was 101): root 8 · free 1 · products 9 · blog 36 (+income post, +renamed free-notion, old slug now a redirect stub) + `blog.html` · collections 40 (generated) · writing 7 · **`/writing/characters/` 6 (5 + hub) NEW** · resources 1 · legal 1 (+10 PDFs). **No build step. Sitemap is MANUAL** (field order `loc→lastmod→changefreq→priority`) — now includes the income post + the 6 `/writing/characters/` urls (priority 0.6). Images `/images/{products,zodiac,books,logo,og,**characters NEW**}/`, webp primary, root-absolute. CSS = per-page inline `<style>` + 4 shared (`tokens.css`, `checkout.css`, `gallery.css`, `mobile-nav.css`). Fonts: Syne / DM Sans / JetBrains Mono (+ Cinzel/Crimson Pro under glass).
- **Glass system (`css/tokens.css`):** per-page inline `<style>` = flat base; `tokens.css` `[data-glass="prototype|cosmic|books"]` layers frost (wins by specificity). **G10 = `data-glass="books"`** (books.html + the character cluster): page-level orange/peach ambient wash (`body::before`), `.glass-lite` frosted cards. Books tokens: bg `#f7f6f2`, surface `#fff`, accent `#e8500a` (hover/bright `#ff6a2a`), text `#1c1c1c`, body `#3a3a3a`, muted `#6b6b6b`, border `#e0ddd8`.
- **Blog post structure (G8):** 2-col `.article-main` = `.article-body` + sticky `.article-sidebar-sticky` (solid white) product card; `.inline-cta` mid-article; `.cta-band`; `.related-posts` grid; FAQ `<h3>/<p>` mirrored in FAQPage JSON-LD. Buy CTAs → `/products/<slug>.html`.

### 19. The Overlayed Echoes character cluster = `/writing/characters/` (NEW this session).
- **5 character pages** (`theo/angela/marcus/lena/kael.html`) + a **hub** (`index.html`), 2 levels deep, dispatch chrome (`data-glass="books"`, Syne/DM Sans), depth-corrected `../../` + root-absolute.
- **Schema per character page:** BreadcrumbList (Home→Books→Characters→Name) + **Person** (`@id …#<slug>`, reciprocal `sibling`/`knows` graph, `subjectOf`→OE book, **`alternateName`** = the full Stage-2 fantasy name) + slim Org. **NO FAQPage.** Hub: BreadcrumbList + ItemList (the 5) + Org.
- **Two stages per page:** Stage 1 (real self — portrait, bio, relationships, "Stage One" marker) → **Stage 2** ("Stage Two · In the Game" — fantasy portrait, desc, 6-stat character-sheet block, "Download fantasy card ↓"). Hub = transformation grid: **"The friends"** row (Stage 1) + **"In the game"** row (Stage 2), same K-T-A-M-L order.
- **Stage-2 selves (fantasy=slug · class · stats Might/Agility/Intellect/Will/Charm/Perception):** Sir **Theron**=theo · Holy Warrior · 16/10/8/14/12/10 · Sister **Althea**=angela · Healer · 10/12/14/16/10/12 · **Varkis**=marcus · Trickster · 8/17/12/10/14/13 · **Elyra**=lena · Mage · 7/12/16/13/9/11 · **The Wanderer**=kael · (NPC enigma) · **`?`×6**. Share cards/hub use the SHORT name; prose + Person `alternateName` use the FULL (Sir Theron / Sister Althea / Varkis / Elyra / The Wanderer). Kael's name == class so the sheet header collapses to "The Wanderer".
- **Per-page `og:image` = the Stage-1 `<slug>-og.jpg`** (1200×630, canonical landscape share). Hub og = `characters-og.jpg`. Stage-2 tall cards are download/social only, NOT the og.
- **Generators (untracked `tools/`):** `_build_characters.py` (transforms approved `theo.html` → the other 4 + hub via match-checked span-swaps — **NOW SUPERSEDED: the live pages carry Package-2/Stage-2 wiring it doesn't reproduce; do NOT regenerate without re-wiring**); `_build_character_cards.py` (Pillow — see #21); `_wire_character_cards.py` / `_wire_card_ga4.py` / `_wire_stage2.py` / `_wire_stage2_alt.py` / `_wire_stage2_hub.py` (the og/download/GA4/section/schema/hub sweeps). All match-checked + eol-preserving.

### 20. Line endings — `core.autocrlf=true`. THE recurring gotcha this session (NEW).
- No `.gitattributes` text rules for html/txt/xml → tracked files are **LF in the repo, CRLF in the working tree** (`git ls-files --eol` = `i/lf w/crlf`). Files you *create* end up LF in the working tree; git stores them LF too (the `LF will be replaced by CRLF` warning on `git add` is benign/expected).
- **MSYS `grep -c $'\r'` falsely reports 0** even on CRLF files (it strips CR). Check eol with Python: `open(p,'rb').read().count(b'\r\n')`.
- **A naive `\n` regex will NOT match the CRLF working-tree bytes** (this aborted a sweep mid-session). Every `tools/_*.py` sweep must **read → normalize to LF → edit → write back in each file's ORIGINAL eol** (detect `'\r\n' in raw`; restore on write; new files stay LF). `git diff --check` clean = proof of no eol churn.

### 21. Image-card pipeline — Pillow + the REAL site fonts (NEW).
`tools/_build_character_cards.py` uses **Pillow** + the actual **Syne/DM Sans TTFs** fetched from Google Fonts' source (`google/fonts` GitHub) into **`tools/_fonts/`** (untracked): `Syne.ttf` (variable → `set_variation_by_name('ExtraBold')`), `DMSans.ttf` (variable → `'Bold'`). **Don't substitute DejaVu.** Josh's locked AI portraits arrive as `<slug>.webp` / `<slug>-stage2.webp` (800×1192); a provided `theo-min.png` was a *mock* with baked placeholder text — caught on render; always composite from the clean `.webp`. Tall card = portrait + bottom dark scrim (transparent→`rgba(12,9,7,~0.86)`) + Syne name (white, **auto-fits** long names like "The Wanderer") + DM Sans "OVERLAYED ECHOES" (`#ff6a2a` on dark scrim / `#e8500a` on cream og). og = cream `#f7f6f2` + orange/peach blurred bloom + floating portrait + dark name. Hub 5-up = title + 5 face-cropped rounded cards. Per-character scrim legibility verified on render (Kael lightest — held).

---

## 🟢 Status: live, clean, nothing mid-flight

Working tree clean except the usual untracked: `.claude/`, `.netlify/`, dated `HANDOFF-*.md` archives, `SITE-OVERVIEW.md`, `_audit_output.md`, **`tools/_fonts/`** (the fetched TTFs), and per-session **`tools/_*.py`** scripts — now also `_build_characters.py`, `_build_character_cards.py`, `_wire_character_cards.py`, `_wire_card_ga4.py`, `_wire_stage2.py`, `_wire_stage2_alt.py`, `_wire_stage2_hub.py`, `_wire_gumroad_post.py`, `_rename_no_email_post.py`, plus this session's `_tools_subdomain_relink.py`, `_audit_titles.py`, `_inspect_chars.py`, `_apply_title_meta.py`. None tracked; leave or clean up at will. Also untracked: `Downloads/main-site-relink-brief.md` + the `Downloads/_pkg*/` + `Downloads/files/` source assets (briefs, portraits) — outside the repo. **The only uncommitted/unpushed thing is this HANDOFF refresh.**

---

## First steps for the new session

```bash
cd /c/Users/jotra/builtbyjoshstudio
git status                                          # this HANDOFF refresh is [ahead 1], unpushed — ask Josh
git log --oneline -12                               # tip 7af3ce1 (title/meta), c80810f (relink) below the HANDOFF refresh
git tag -l 'backup-*' --sort=-creatordate | head -6

# Live spot-checks (cache-busted):
ts=$(date +%s)
curl -fsS "https://builtbyjoshstudio.com/?x=$ts" | grep -c 'builtbyjoshstudio-cyber.github.io'                              # 0 (relink live — old host gone)
curl -fsS "https://builtbyjoshstudio.com/?x=$ts" | grep -c 'tools.builtbyjoshstudio.com/'                                   # 7 (homepage Free-Tools repointed)
curl -sS -o /dev/null -w "%{http_code}\n" "https://tools.builtbyjoshstudio.com/brine-calculator/?x=$ts"                    # 200 (new subdomain serves all 7)
curl -sS -o /dev/null -w "%{http_code}\n" "https://builtbyjoshstudio-cyber.github.io/brine-calculator/?x=$ts"              # 404 (old repo Pages decommissioned)
curl -fsS "https://builtbyjoshstudio.com/blog/why-solo-creators-stay-stuck-under-5k.html?x=$ts" | grep -c '5K/mo'           # >=1 (title/meta rewrite live)
curl -sS -o /dev/null -w "%{http_code}\n" "https://builtbyjoshstudio.com/writing/characters/?x=$ts"                        # 200 (prior-session character hub still live)
gh run list --workflow=pages-build-deployment --limit 3    # latest completed/success
```

Then take direction from Josh. Nothing is mid-flight.

---

## Open / deferred items

- **🆕 Title/meta CTR watch (pending).** `7af3ce1` rewrote titles/metas on 8 under-clicking pages (live, baseline **2026-06-04**). Google needs ~1–3 weeks to re-crawl → **no CTR conclusions before ~2026-06-18**; expect day-to-day Search Console noise until then.
- **🆕 Future pass "B" — sync social/headline twins (low priority).** On the **6 title-changed pages** (`zero-based-budget-excel`, `how-to-launch-digital-product-without-audience`, `sinking-funds-explained`, `why-solo-creators-stay-stuck-under-5k`, `ultimate-budget-workbook`, `complete-notion-os-for-creator-business`): update `og:title` + `twitter:title` + JSON-LD `headline` to the new `<title>` wording. **Leave the `og:`/`twitter:` descriptions** (intentional independent variants — already diverged from `<title>` on 5/8 pages pre-rewrite, so NOT the #9 byte-mirrors). Own backup tag; diff-before-commit; no push w/o go. (`50-30-20` + `creator-content-os` were meta-only — skip.)
- **✅ DONE — Arc 6 relink + 7-repo decommission.** `c80810f` repointed 16 live files (84 hits) `builtbyjoshstudio-cyber.github.io/<slug>/` → `tools.builtbyjoshstudio.com/<slug>/`; the 7 old per-slug repos are Pages-disabled (404) + archived (read-only, reversible). Brief at `C:\Users\jotra\Downloads\main-site-relink-brief.md` (historical).
- **Field-dispatch Stage 2 (more `/writing/` dispatches)** — `tools/_build_dispatches.py` + the index pattern ready; need markdown + a thematic slug. (Distinct from the OE-characters Stage 2, which is DONE.)
- **Organization schema non-critical warnings** — Rich Results flags non-critical Org-node issues (pre-existing, non-blocking); fix = site-wide sweep.
- **Ebonspire launch (June 2026)** — flip "releases June 2026" → "available now", add Book + Offer with verified ASIN, mirror the 3-edition pattern.
- **Carry-forwards:** OG images for ~22 older blog posts; GA4 purchase verification in Realtime; "Buy Direct — Instant Download" lead-CTA; Google Merchant Center; Ebonspire cover for books.html. **`/free/` minor:** 8th lite SKU not featured (by design); no per-page OG card for `/free/`.

---

## Branches and tags

```
main    production — HEAD == origin/main (7af3ce1) + this unpushed HANDOFF refresh on top
```

**Backup tags (newest first, LOCAL only):** `backup-pre-title-meta` (`c80810f`) · `backup-pre-tools-relink` (`a4a72d9`) · `backup-pre-stage2` · `backup-pre-character-cards` · `backup-pre-hub-row` · `backup-pre-character-cluster` · earlier remain.

**This session's commits (newest first, ALL pushed & live except this HANDOFF refresh):**
`7af3ce1` title/meta SEO rewrite (8 pages, 13 lines) · `c80810f` tools-subdomain relink (16 files, 84 hits). **GitHub-settings-only (no commits):** 7 old tool repos Pages-disabled + archived. Session-start tip was `a4a72d9` (prior HANDOFF refresh, pushed early this session); under it `17de766` (prior-session Stage 2) + the OE character-cluster / income / no-email commits remain live.

---

## Hard-won lessons this session

- **Canary-then-batch for destructive/outward-facing infra.** Pages-disable and repo-archive each ran ONE repo first (`brine-calculator`), verified the effect (404 / `archived=true` + the live tool still 200), THEN batched the other six. Stop-and-report on any surprise; Josh's explicit go between phases.
- **Enumerate before you flip — never assume repo layout (#2).** `gh repo list` + per-repo `…/pages` proved 7 separate slug-named project repos (URL slug == repo name) plus the *separate* `tools` (new subdomain, cname `tools.builtbyjoshstudio.com`) + `builtbyjoshstudio` (main, cname) — so disabling/archiving the 7 couldn't touch the live surfaces. `CNAME` = `builtbyjoshstudio.com`; the only `github.com/…` refs are repo links in docs (different host, not matched by the relink).
- **Verify proposed copy against the page, not just the brief (#2).** The title/meta audit caught 2 overpromises — a "free template" (page only offers a paid workbook + a build-it-yourself walkthrough) and an "actually used" case study (the post explicitly says it isn't one). Dropped both before applying.
- **og/twitter/headline are NOT the #9 byte-mirrors.** They're independently authored and already diverged from `<title>` on 5/8 pages — so changing `<title>`/`<meta>` alone is fine; #9's strict twins are FAQ `acceptedAnswer`, Offer/Product `url`, and blog.html `ItemList` (none touched). Don't assume a "schema twin" without grepping.
- **EOL-preserving sweep = binary `bytes.replace` (#20).** Relink host string is pure ASCII (no newline bytes) → `git diff --check` clean; mixed CRLF (15 files) + LF (`free/index.html`) preserved automatically. Title/meta apply used text mode with `newline=''` for the same effect.
- **`main` is production (no PR flow); commit ≠ push (wait for Josh); backup-tag before each arc; commit msgs via `-F -` heredoc; verify live cache-busted after every push.**

---

**End of handoff.** State: live, clean. This session shipped the **tools-subdomain relink** (`c80810f`, 16 files / 84 hits) + **decommissioned the 7 old tool repos** (Pages-off → 404, archived/read-only) + an **SEO title/meta rewrite** (`7af3ce1`, 8 pages). Prior session's OE character cluster + income post + no-email rename remain live. `origin/main` == `7af3ce1`; this HANDOFF refresh is unpushed on top. New session: read this doc, run First-Steps, ask Josh whether to push the HANDOFF refresh, then take direction. **Most likely next: future-pass B (og/twitter/headline sync) and/or the title/meta CTR check (baseline + read-date in Open items).**
