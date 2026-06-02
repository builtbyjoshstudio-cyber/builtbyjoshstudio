# builtbyjoshstudio.com — Session Handoff

**Date:** 2026-06-02 (nav/footer standardization + first in-universe dispatch shipped)
**Repo:** https://github.com/builtbyjoshstudio-cyber/builtbyjoshstudio
**Local path:** `C:\Users\jotra\builtbyjoshstudio`
**Host:** GitHub Pages — custom domain `builtbyjoshstudio.com` via CNAME → Fastly CDN (~10-min edge TTL)
**HEAD (pushed):** `1f45278` on `main`, **in sync with `origin/main`**. All committed work is live and verified. **Working tree clean** (this handoff commit sits on top of `1f45278`).
**Latest backup tag:** `backup-pre-footer-sweep` (`7051efa`) is the newest *checkpoint* tag, but several `backup-pre-*` tags were created this arc (see Branches & Tags). Consider tagging `backup-2026-06-02` at the current HEAD before the next session's first edit.

---

## 🧭 Session summary (plain language)

Since the last handoff (`8729226`/`f8b6bed`, "Phase 2A shipped"), this session shipped **26 commits** across several arcs — all committed, pushed, live, and post-deploy-verified. Site totals now: **888 tracked files · 94 HTML pages · ~750 images.**

1. **Books / J.S. Warden fiction build-out** — added the Ebonspire cover image; a `data-glass="books"` glass treatment (G10) on books.html; a full copy + SEO/GEO pass on books.html (genre-keyword H1, "for readers who…" targeting lines, 6-Q FAQ + FAQPage parity, Person/Book×2/WebPage/Breadcrumb schema, Amazon author-store link); a **free preview page** (`overlayed-echoes-preview.html`, Chapters 1–2 + sample PDF) with GA4 funnel tracking, its own GEO pass (Book-as-free-excerpt schema, self-canonical), and a widened 900px reading column.
2. **Homepage** — hero rewrite (SEO/GEO, buy-direct positioning, dropped Etsy-as-channel, AI-crafted art disclosure, scoped updates claim); scoped the "free updates" FAQ; aligned remaining art descriptors ("AI-crafted", "oil-painting style"); OG/Twitter meta aligned to the new positioning; a **subordinate fiction band** below the hero (both covers → books.html); fixed book genres in the FAQ (OE = LitRPG not noir; Ebonspire June 2026).
3. **Founding-date reconciliation** — 2025 origin (narrative) vs 2026 LLC (`foundingDate 2026-05-13` in schema) made consistent across about.html + llms.txt; index.html's brand-node 2025 / Tynkr sub-org 2026 / LLC date all left correct.
4. **`llms.txt` refresh** — novella→novel, old Amazon URL `04YzP4o4`→`06ZWovoY`, LitRPG/noir genre framing.
5. **Navigation standardization (Phase 1 audit → Phase 2 sweep)** — canonical header nav on all 93 nav-bearing pages: `Tynkr Tools · Zodiac Art · Blog · Resources · Free Tools · About · Writing · Legal`, depth-aware hrefs, active-state preserved per page (+ books.html → Writing active). Preview page excluded (bespoke nav).
6. **CTA consistency (Phase 1 audit → Phase 2 fixes)** — converted the Chinese-zodiac **hub** page to buy-direct (price 11.99→14.99 to match live LS buttons, stripped Etsy offer-urls, reframed channel copy); reworded the "Purchase on Etsy" how-to step → channel-neutral on all 8 product pages (visible + JSON-LD).
7. **Footer standardization (Phase 1 audit → Phase 2 sweep)** — section-aware canonical footer on 91 pages (collections→Collections, products→Products, resources→Templates slot), added Legal/Substack/Contact everywhere, canonical order, depth-aware hrefs; **brand-aware Etsy link** (zodiac collections → BuiltByJoshStudio Etsy; everything else → Tynkr Etsy). index.html (bespoke) + preview (bespoke) excluded.
8. **First in-universe dispatch** — `/writing/corruption-of-immersion.html` ("The Glitch in the Soul"), a fiction-world blog post in the books-glass skin, BlogPosting schema cross-linked to the OE Book + jswarden Person `@id`s, soft diegetic CTAs (preview + Amazon, GA4-tracked), inbound links from the preview page + the books.html OE card.

**✅ Everything above is shipped and live-verified. No work is mid-flight. Working tree clean.**

---

## 🔴 STANDING INSTRUCTIONS — read these first

Rules Josh has set through hard pushback over many sessions. Apply by default; deviate only if Josh says so explicitly.

### 1. Communication: terse, directive, no preamble.
No padding. Surface tradeoffs in 1–2 sentences and pick a default. When there's real ambiguity, ask ONE crisp question with a recommended default. Skip "Great, I'll start by…".

### 2. Verify against source, never assume. (Josh's #1 recurring catch.)
ChatGPT/other crawlers have been **wrong multiple times** this arc (claimed a short nav that didn't exist; claimed Etsy-primary CTAs that were actually JS-rewired to Lemon Squeezy). **Always confirm against the repo before changing anything.** When a brief's premise is off, STOP and flag — don't build on a wrong assumption. Recent examples: the CTA "drift" was mostly a static-crawl artifact (buttons rewire to LS at runtime via `data-cta-label-live`); the CS-hub "convert to buy-direct" was really a stale-copy + stale-price fix on a pure hub.

### 3. The site has NO template engine.
Every HTML page is standalone — its own inline `<style>`, JSON-LD, nav, footer. Site-wide changes = either (a) edit the Python generators in `tools/` and regenerate, or (b) a Python sweep over every `.html`. **Exception:** `/css/tokens.css` is loaded by all 93 chrome-bearing pages — cross-cutting CSS that doesn't collide with per-page inline `<style>` properties can live there (cascade is per-property). This standalone model is the root cause of most "this page drifted" bugs.

### 4. Sweep mechanics (proven this arc).
For nav/footer/CTA sweeps: detect the per-page **depth prefix** (root `""`, nested `../`, `legal/` uses root-absolute `/`), preserve per-page **active-state**, use **block-level** replacement (not line-based) so the minified `collections/chinese-zodiac-art.html` isn't mangled, and **exclude** bespoke pages (see #16). Sweep scripts live as untracked `tools/_*.py`; dry-run before `--write`; reconcile the tally explicitly.

### 5. Commerce model — Lemon Squeezy primary, Etsy secondary.
LS overlay is the primary buy-direct channel for Tynkr products AND zodiac collections. Etsy is a deliberate **secondary** (sidebar reference + footer link), never the lead CTA, never "sold on Etsy" as the channel.
- **Tynkr products (8 pages):** `[data-checkout="<key>"]` → `js/checkout.js` reads `js/checkout-config.js`. All 8 paid keys have live `ls:` URLs, so buttons rewire to the LS overlay and swap label to `data-cta-label-live` at runtime. **The static HTML Etsy `href` + label is the no-JS fallback — do NOT remove it.** Never hardcode a checkout URL outside `checkout-config.js`.
- **Collection pages:** `.ls-checkout-btn` + `data-checkout-url` + `js/ls-checkout-btn.js`.
- **Etsy brand split (footer):** zodiac collection pages → `etsy.com/shop/BuiltByJoshStudio`; all other pages → `tynkrtoolsandco.etsy.com`. (Fixed this arc — don't homogenize it.)

### 6. Identity hygiene (site-wide):
- **Founder:** "Josh" only on every public surface. Never the real surname, never "Joshua".
- **Pen name (fiction):** `J.S. Warden` — **no spaces** in site copy + schema. Cover art uses spaced `J. S. Warden` (print-only exception). 0 spaced-form instances on public pages.
- **City:** state-level "Kansas" only. Registered-agent city (Wichita) appears only on `/legal/index.html`.
- **`<meta name="keywords">`:** never.

### 7. Founding dates (reconciled this arc — keep consistent):
Studio **started 2025** (narrative voice), **incorporated as Built by Josh Studio LLC in 2026**. Schema `foundingDate` = `2026-05-13` (the LLC legal date) on the site-wide Organization block. index.html's separate brand node carries `2025`, its Tynkr sub-org `2026` — both correct, leave them. No bare context-free "founded 2025" that contradicts the schema.

### 8. Site-wide Organization JSON-LD on every page (`@id: https://builtbyjoshstudio.com/#organization`).
Per-page Product/Book/etc. schemas `@id`-reference it. Cross-link fiction pages to the canonical entities: Person `@id` `https://builtbyjoshstudio.com/books.html#jswarden`, OE Book `@id` `https://builtbyjoshstudio.com/books.html#overlayed-echoes`. **Reference existing `@id`s; never redefine or invent them.**

### 9. Schema rules.
Collection pages: Product + FAQPage + BreadcrumbList + Organization. Blog posts: Article + BreadcrumbList (legacy tool posts keep their old WebApplication blocks — leave alone). **FAQPage must mirror the visible FAQ text exactly (parity).** **Never fake FAQPage** on content with no real Q&A (fiction dispatches use BlogPosting, not FAQPage). No aggregateRating/review schema anywhere (no real reviews yet).

### 10. Collection pages: edit via the `tools/` generators, not by hand.
5 generators (`build_western_signs_page.py`, `build_realm_page_master.py`, `build_chinese_animal_pages.py`, `build_chinese_realms_page.py`, `build_zodiac_landscapes_page.py`). `collections/chinese-zodiac-art.html` is the hand-written **minified** hub — handle with block-level edits, never line-based.

### 11. Antigravity owns the cooking apps. You write blog posts about them, never the apps.

### 12. GitHub Pages build can fail on transient infra.
Recovery: `gh run rerun <run_id> --failed` OR push an empty commit. **Always verify live with a cache-busted request after push** (`?x=<timestamp>`), and confirm the `pages-build-deployment` run shows `completed/success` before trusting live checks. Builds run ~45–70s; deploys occasionally queue a few min behind the push.

### 13. Jekyll excludes HANDOFF in `_config.yml`.
`HANDOFF.md` + `HANDOFF-*.md` are excluded (literal `{{` would choke Liquid). Any new tracked top-level markdown with `{{` needs the same treatment.

### 14. GA4 instrumentation architecture (ID `G-QDSPBB7S9J`).
- `js/ga4-events.js` (all pages): `etsy_click`, `__ga4LemonSqueezyHandler` (standard `begin_checkout`/`purchase`), `__ga4SetupLemonSqueezy()` polling-loop, `slugToCategory()`. `window.__ga4LemonSqueezySetupDone` guards double-wiring.
- `js/ls-checkout-btn.js` (collections) lazy-loads lemon.js on first click, then invokes `window.__ga4SetupLemonSqueezy()` from `s.onload` **before** opening the overlay — critical race fix (`62b7b67`); don't reintroduce the race.
- `js/checkout.js` (8 product pages) only calls `LemonSqueezy.Refresh()` (Setup is centralized in ga4-events.js).
- **Funnel tracking precedent:** outbound Amazon clicks use `book_amazon_click` with `outbound:true` + `transport_type:'beacon'` (survives page unload). Fiction pages use a `source_page` param (e.g. `dispatch-corruption`) to distinguish funnels. The dispatch page and preview page both follow this.

### 15. Navigation & footer are now STANDARDIZED (this arc — don't let them drift).
- **Header nav (93 pages):** `Tynkr Tools · Zodiac Art · Blog · Resources · Free Tools · About · Writing · Legal`. Depth-aware hrefs; `class="active"` on the current section per page (books.html → Writing active). Nav "Writing" → `/books.html`.
- **Footer (91 pages):** `Home · [section] · Blog · Resources · About · Writing · Legal · Etsy · Substack · Contact · Refunds · Privacy · Terms`. Section slot is contextual (collections→Collections, products→Products, resources→Templates, else omitted). Etsy brand-split per #5. books.html footer intentionally has **no Writing self-link**.
- **Exclusions:** `overlayed-echoes-preview.html` (bespoke nav + footer — NOT swept) and `index.html` (bespoke footer — excluded from the footer sweep; its nav IS standard).

### 16. The fiction layer (books + preview + dispatches).
- **`books.html`** (root) — J.S. Warden hub, `data-glass="books"`, two book cards, 6-Q FAQ + FAQPage, rich schema with the canonical `#jswarden`/`#overlayed-echoes`/`#ebonspire-chronicles` `@id`s.
- **`overlayed-echoes-preview.html`** (root, **bespoke chrome — excluded from sweeps**) — free Chapters 1–2 + `overlayed-echoes-sample.pdf`, Book-as-free-excerpt schema, self-canonical, GA4 funnel, 900px reader. Hero uplink cluster links to books.html + the dispatch.
- **`/writing/corruption-of-immersion.html`** — first in-universe dispatch, books-glass skin, BlogPosting schema (`isPartOf` OE Book, `author` jswarden, `articleSection:"Fiction"`, NO FAQPage), self-canonical, soft diegetic CTAs. **Unlisted in nav by design** — reachable only via its canonical + the two inbound links (preview hero uplink, books.html OE card "From the world: a field dispatch →"). The `/writing/` section has **no index/grid** yet (deliberate later-decision).

### 17. Facts (verified this arc — use exactly):
- **Overlayed Echoes:** near-future **LitRPG** (also GameLit; "Science Fiction" is the umbrella), 257-page full-length novel, **Book 1 of a planned 5-book series**, Amazon `https://a.co/d/06ZWovoY`, on Kindle + paperback + **Kindle Unlimited**. Original-edition audiobook exists; expanded-edition audiobook undecided. NOT a "noir" (that's Ebonspire). Set 2045, neural chips make tabletop RPG real.
- **Ebonspire Chronicles:** dark fantasy detective noir, **releases June 2026**, $? (unreleased — no Offer in schema, `datePublished 2026-06`). Completely separate world from Overlayed Echoes.
- **J.S. Warden author store:** `https://www.amazon.com/stores/J.-S.-Warden/author/B0FPQ3RWWF`.
- **Chinese-zodiac art bundles:** $14.99 each (the hub's old $11.99 was stale, fixed this arc).

---

## 🟢 Status: live, clean, nothing mid-flight

Working tree clean except the usual untracked: `.claude/`, `.netlify/`, dated `HANDOFF-*.md` archives, `SITE-OVERVIEW.md`, `builtbyjoshstudio-FULL-AUDIT.md`-style docs in Downloads (outside repo), and per-session `tools/_*.py` utility/sweep scripts. None are tracked; leave them or clean up at will.

---

## First steps for the new session

```bash
cd /c/Users/jotra/builtbyjoshstudio
git status                                          # clean; HEAD 1f45278 == origin/main
git log --oneline -12
git tag -l 'backup-*' --sort=-creatordate | head -8

# Live spot-checks (cache-busted):
ts=$(date +%s)
curl -fsS -I "https://builtbyjoshstudio.com/writing/corruption-of-immersion.html?x=$ts" | head -1   # 200 (new dispatch)
curl -fsS "https://builtbyjoshstudio.com/books.html?x=$ts" | grep -c "field dispatch"               # 1 (inbound link present)
curl -fsS "https://builtbyjoshstudio.com/collections/aries-zodiac-art.html?x=$ts" | grep -c "shop/BuiltByJoshStudio"  # >=1 (footer Etsy brand split)
curl -fsS "https://builtbyjoshstudio.com/llms.txt?x=$ts" | grep -c "novella"                         # 0 (refreshed)

gh run list --workflow=pages-build-deployment --limit 5    # confirm latest completed/success
```

---

## Open / deferred items (nothing blocking)

- **`/writing/` section infrastructure** — there's ONE dispatch, no index/grid/nav entry. If more dispatches are added, decide on a section index + whether to surface it in nav. Deliberately deferred.
- **A fiction-post generator** — if more than ~5–6 dispatches are planned, a small `tools/` generator (like the zodiac generators) beats hand-authoring standalone HTML. Briefing discussed; not built.
- **Per-post OG share cards** — most blog posts + the dispatch reuse a generic share image. The dispatch uses `images/books/og-books.jpg`; a bespoke dispatch card is a nice-to-have.
- **Carry-forwards from prior sessions** (still open): OG images for ~22 blog posts; GA4 purchase verification in the Realtime dashboard; CTA copy "Buy Direct — Instant Download" lead treatment; Google Merchant Center; Ebonspire cover for books.html when ready; Ebonspire launch tasks for June 2026 (add Amazon URL + Offer to its Book schema, flip "releases June 2026" → "available now").

---

## Branches and tags

```
main                              production — HEAD 1f45278 (pushed, clean, == origin/main)
```

**Backup tags created this arc (newest first):** `backup-pre-footer-sweep` (7051efa), `backup-pre-howto-reword`, `backup-pre-cs-hub-convert`, `backup-pre-nav-sweep`, `backup-pre-faq-genre-fix`, `backup-pre-homepage-books-band`, `backup-pre-og-meta`, `backup-pre-founding-dates`, `backup-pre-llms-txt`, `backup-pre-preview-widen`, `backup-pre-books-geo`, `backup-pre-art-descriptor-fix`, `backup-pre-updates-claim-fix`, `backup-pre-homepage-hero`, `backup-pre-preview-ga4`, `backup-pre-books-glass`, plus `backup-pre-dispatch-inbound` (27be51d). Earlier checkpoints: `backup-after-book-discoverability` (8729226), `backup-pre-phase-2a` (720e3e7), `backup-after-phase-6` (8055f13).
**Suggested:** tag `backup-2026-06-02` at `1f45278` before the next session's first edit. (Backup tags are LOCAL — `git push` doesn't carry them.)

**26 commits this arc (newest first):** `1f45278` dispatch inbound links · `27be51d` dispatch page · `ae32303` footer Etsy brand-split · `77cbf50` footer standardization · `7051efa` how-to reword · `235ef48` CS-hub buy-direct · `66294e5` nav standardization · `d1f464d` homepage genre fix · `523dbe7` homepage fiction band · `312e55a` homepage OG/Twitter meta · `2d2c853` founding dates · `c3ec0a3` llms.txt refresh · `7bce5fc` preview widen · `ca63e81` preview GEO · `fb0c1e5` OE alt text · `a8f21d8` books.html GEO · `bf85ed0` homepage art descriptors · `77eb13f` homepage updates FAQ · `713d9c3` homepage hero rewrite · `4245689` preview GA4 · `ce1cbd8` mobile drift fix · `1dcb53b` preview page + sample PDF · `c2275b5` Writing page copy/schema · `de71667` books G10 glass · `189d1b0` Ebonspire cover · (`8729226` Phase 2A was the prior handoff's HEAD).

---

## Hard-won lessons this arc
- **Static crawls lie about JS-driven CTAs.** Product buy buttons show an Etsy fallback in static HTML but rewire to the LS overlay at runtime. Audit the rendered state (or the config), not the raw HTML.
- **Section-aware > uniform** for footers — the Etsy link and the section slot are legitimately page-type-specific. Don't homogenize. (Caught when a uniform sweep wrongly pointed zodiac footers at the Tynkr Etsy.)
- **CSS cascade is per-property** — a single `tokens.css` rule fixes divergent inline-styled pages as long as none set that exact property (footer `flex-wrap`, the books-glass mobile overflow guard).
- **Verification-harness quirk (cosmetic):** the PowerShell→Python boundary mangles literal em-dash `—` / middot `·` in *comparison strings*, producing false "absent" results. The served bytes are fine — confirm by extracting/printing the actual served string (repr) rather than trusting an equality check on a dash/dot.
- **Commit messages: avoid literal double-quotes** in `git commit -m` via PowerShell — they break argument parsing (split into bogus pathspecs). Use a single-quoted here-string or drop the inner quotes.

---

**End of handoff.** State: live, clean, HEAD `1f45278` == origin/main, nothing mid-flight. The nav/footer/CTA standardization arc and the fiction layer (books → preview → first dispatch) are complete and verified. New session should read this doc, run the First-Steps verification block, then take direction from Josh.
