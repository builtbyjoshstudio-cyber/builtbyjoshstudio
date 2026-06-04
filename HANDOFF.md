# builtbyjoshstudio.com — Session Handoff

**Date:** 2026-06-04 (one big multi-package arc: the **Overlayed Echoes character cluster** built end-to-end — **Package 1** pages+hub+schema, **Package 2** share cards, **Stage 2** fantasy selves — plus an **Etsy/Gumroad income blog post** and a **no-email post rename → honest slug + redirect stub**. Ended on a **read-only review of the tools-subdomain relink brief** — reviewed, NOT executed.)
**Repo:** https://github.com/builtbyjoshstudio-cyber/builtbyjoshstudio
**Local path:** `C:\Users\jotra\builtbyjoshstudio`
**Host:** GitHub Pages — custom domain `builtbyjoshstudio.com` via CNAME → Fastly CDN (~10-min edge TTL). **No CI workflow file in the repo**; GitHub's *default* `pages-build-deployment` fires on every push to `main` (~45–70s). **There is NO branch/PR workflow — `main` IS production; pushing `main` deploys live.** Commit on `main`, push only when Josh says.
**HEAD:** everything this session is **pushed to `origin/main`, live, post-deploy-verified** — last live commit **`17de766`** (Stage 2). This HANDOFF refresh is the commit on top — **unpushed** (HANDOFF is Jekyll-excluded, no live effect); first-steps will show `[ahead 1]`. **Ask Josh whether to push it.** Working tree otherwise clean (usual untracked only).
**Latest backup tags (LOCAL only — `git push` doesn't carry them):** `backup-pre-stage2` (`ef2ef68`) · `backup-pre-character-cards` (`65b0d40`) · `backup-pre-hub-row` (`35b9896`) · `backup-pre-character-cluster` (`47faaa1`) · earlier arc tags remain.

---

## 🧭 Session summary (plain language)

Five shipped arcs (all live + post-deploy-verified) + one review-only. Careful read-only paste-back, backup tag per arc, dry-run-before-write sweeps, diff-before-commit, and **Josh approved a Theo-first prototype before each cluster build replicated to the other four.**

**Arc 1 — Etsy/Gumroad income post (`380bfa9`).** New `blog/track-etsy-gumroad-income-notion.html` (Josh authored offline, placed byte-exact). Parity-fixed to the finance-os template (restored box-drawing CSS comments + the inline Etsy click-out `<script>`). Wired into `sitemap.xml`, `llms.txt`, `blog.html` (visible Templates card **+ its ItemList position-13 twin** — #9 mirror), and a reciprocal related-reading card on `notion-finance-os-for-creators.html`.

**Arc 2 — no-email post rename (`72a3434` + `47faaa1`).** `blog/free-notion-templates-creators-no-email.html` → `…-for-creators.html` (honest slug). Old slug kept as a minimal **meta-refresh redirect stub** (no 404 / SEO loss). Stripped every "(No Email Required)"/"No email signup" claim from the new file's title/h1/meta/og/twitter/Article schema **and** the visible cards (blog.html card+ItemList, 5 related-card hosts) and the what-lite CTA. Repointed all internal refs. `dateModified`→`2026-06-03`. (llms.txt never referenced it. Kept-as-true: the "Notion Marketplace — No signup required" body line.)

**Arc 3 — OE character cluster · Package 1 (`35b9896` + `65b0d40`).** New `/writing/characters/` section: **5 character pages** (theo/angela/marcus/lena/kael) + a **hub** (`index.html`). Dispatch chrome (`data-glass="books"`), **Person** schema with reciprocal `sibling`/`knows` graph + `subjectOf`→OE book, 5 portraits. Wired `sitemap` (+6), `llms.txt` (`## Characters`), `books.html` ("Meet the five friends →"). Hub cards laid out **one row on desktop, reflow 5→2→1**.

**Arc 4 — OE character cluster · Package 2 share cards (`66b6ea5` + `ef2ef68`).** Per character: a **tall share card** (`<slug>-card.jpg`, 800×1192 — portrait + scrim + Syne name + "OVERLAYED ECHOES") + a **landscape og-fallback** (`<slug>-og.jpg`, 1200×630). **Hub 5-up** (`characters-og.jpg`). Per-page `og:image`/`twitter:image` swapped to the `-og.jpg`; a "Download character card ↓" link (the tall card) with **GA4 `file_download`**. Built with the **real Syne/DM Sans TTFs** (fetched to `tools/_fonts/`) via **Pillow**.

**Arc 5 — OE character cluster · Stage 2 fantasy selves (`17de766`).** Each page got a **"Stage Two · In the Game"** section: fantasy portrait (`<slug>-stage2.webp`) + canon desc + a 6-stat **character-sheet block** (Kael = `?`×6 enigma) + a "Download fantasy card ↓" link (`<slug>-stage2-card.jpg`) with GA4. Hub got a **second row** ("The friends" / "In the game" transformation grid). **`alternateName`** added to all 5 Person nodes. Fantasy→slug: **Theron**=theo (Holy Warrior), **Althea**=angela (Healer), **Varkis**=marcus (Trickster), **Elyra**=lena (Mage), **The Wanderer**=kael (NPC enigma).

**Arc 6 (REVIEW ONLY — not executed) — main-site tools-subdomain relink.** Reviewed `C:\Users\jotra\Downloads\main-site-relink-brief.md`. The 7 cooking tools are moving `builtbyjoshstudio-cyber.github.io/<slug>/` → `tools.builtbyjoshstudio.com/<slug>/` (same slugs). **The new subdomain is LIVE (all 7 → 200).** My audit + corrections are in **Open items** — this is the most-likely next task.

**✅ Arcs 1–5 shipped, pushed, live, post-deploy-verified. Arc 6 reviewed, awaiting Josh's go to execute. Working tree clean. Nothing mid-flight.**

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
The 7 free cooking utilities are external apps. **THEY ARE MOVING (Arc 6 / Open items): `builtbyjoshstudio-cyber.github.io/<slug>/` → `tools.builtbyjoshstudio.com/<slug>/`** — the new subdomain is **LIVE**, but main-site links still point at the OLD host pending the relink (reviewed, not yet executed). The homepage "Free Tools" section, `/free/`, `llms.txt`, and **~13 cooking/build-story blog posts** link out to them. (These genuinely need **no email** — see #5.)

### 12. Pages build can fail on transient infra.
Recovery: `gh run rerun <id> --failed` OR push an empty commit. **Always verify live with a cache-busted request** (`?x=<ts>`) and confirm `pages-build-deployment` `completed/success` first. `gh run watch <id> --exit-status` blocks. (The Node-20-deprecation annotation on every run is benign — GitHub default infra, no workflow file.)

### 13. Jekyll excludes HANDOFF in `_config.yml`.
`HANDOFF.md` + `HANDOFF-*.md` excluded. Any new tracked top-level markdown with `{{` needs the same. **HANDOFF.md still contains 1 old-host github.io reference (in this narrative) — exclude it from the Arc-6 relink rewrite AND from the Phase-4 "zero hits" grep.**

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

Working tree clean except the usual untracked: `.claude/`, `.netlify/`, dated `HANDOFF-*.md` archives, `SITE-OVERVIEW.md`, `_audit_output.md`, **`tools/_fonts/`** (the fetched TTFs), and per-session **`tools/_*.py`** scripts — now also `_build_characters.py`, `_build_character_cards.py`, `_wire_character_cards.py`, `_wire_card_ga4.py`, `_wire_stage2.py`, `_wire_stage2_alt.py`, `_wire_stage2_hub.py`, `_wire_gumroad_post.py`, `_rename_no_email_post.py`. None tracked; leave or clean up at will. Also untracked: `Downloads/main-site-relink-brief.md` + the `Downloads/_pkg*/` + `Downloads/files/` source assets (briefs, portraits) — outside the repo. **The only uncommitted/unpushed thing is this HANDOFF refresh.**

---

## First steps for the new session

```bash
cd /c/Users/jotra/builtbyjoshstudio
git status                                          # this HANDOFF refresh is [ahead 1], unpushed — ask Josh
git log --oneline -12                               # tip should be 17de766 (Stage 2) under the HANDOFF refresh
git tag -l 'backup-*' --sort=-creatordate | head -6

# Live spot-checks (cache-busted):
ts=$(date +%s)
curl -fsS -o /dev/null -w "%{http_code}\n" "https://builtbyjoshstudio.com/writing/characters/?x=$ts"                       # 200 (hub)
curl -fsS "https://builtbyjoshstudio.com/writing/characters/?x=$ts" | grep -c 'hub-row-label'                              # 4 (2 CSS rules + The friends / In the game)
curl -fsS "https://builtbyjoshstudio.com/writing/characters/theo.html?x=$ts" | grep -c 'character-stage2'                  # 1 (Stage 2 section)
curl -fsS "https://builtbyjoshstudio.com/writing/characters/theo.html?x=$ts" | grep -c 'Sir Theron'                        # >=1 (alternateName + sheet header + desc)
curl -fsS -o /dev/null -w "%{http_code}\n" "https://builtbyjoshstudio.com/images/characters/theo-stage2-card.jpg?x=$ts"    # 200
curl -fsS "https://builtbyjoshstudio.com/blog/free-notion-templates-for-creators.html?x=$ts" | grep -c 'No Email Required' # 0 (renamed honest)
curl -fsS -o /dev/null -w "%{http_code}\n" "https://tools.builtbyjoshstudio.com/brine-calculator/?x=$ts"                   # 200 (new tools subdomain — Arc 6 prereq, LIVE)
gh run list --workflow=pages-build-deployment --limit 3    # latest completed/success
```

Then take direction from Josh. Nothing is mid-flight.

---

## Open / deferred items

- **🔝 Tools-subdomain relink (Arc 6 — the most-likely next ask; REVIEWED, not executed).** Brief: `C:\Users\jotra\Downloads\main-site-relink-brief.md`. Goal: repoint every main-site link `builtbyjoshstudio-cyber.github.io/<slug>/` → `tools.builtbyjoshstudio.com/<slug>/`. **Prereq MET** (new subdomain LIVE, all 7 → 200). My review's corrections to apply:
  - **Scope = 16 LIVE files via grep, not the 7 build-story posts the brief names.** The old host appears in `index.html` (homepage Free-Tools ×7), `free/index.html` (×7), `llms.txt` (×7), the 7 build-story posts, **AND 6 other cooking posts** (`how-i-learned-to-cook`, `how-i-cook-rice-finger-method`, `why-home-cooks-should-batch-broths`, `what-i-actually-keep-in-my-kitchen`, `how-i-make-pho-two-day-method`, `cook-the-way-you-want-to-cook` — all link the Recipe Scaler). ~84 live hits.
  - **Method:** one blanket string replace `builtbyjoshstudio-cyber.github.io/` → `tools.builtbyjoshstudio.com/` cleanly handles hrefs + the **4 JSON-LD `"url"` fields** (baking-pan-swap, building-recipe-scaler, perfect-roast, reverse-roasting), preserving slugs + trailing slashes. All 7 slugs match the brief exactly.
  - **The one decision for the gate:** `blog/building-the-universal-recipe-scaler.html:469` shows the old host as **visible anchor text** (not just href). The blanket replace will (correctly) update the displayed URL too — bless this explicitly (it's the lone exception to "don't alter anchor text").
  - **Brief premises that are FALSE (don't chase):** no `/tools/` index exists; `/resources/` does NOT link the tools; `sitemap.xml` has zero tool URLs; no JS refs.
  - **Exclude `HANDOFF.md`** from the rewrite + the Phase-4 "zero hits" grep (it references the old host in narrative — intentional).
- **Field-dispatch Stage 2 (more `/writing/` dispatches)** — `tools/_build_dispatches.py` + the index pattern ready; need markdown + a thematic slug. (Distinct from the OE-characters Stage 2, which is DONE.)
- **Organization schema non-critical warnings** — Rich Results flags non-critical Org-node issues (pre-existing, non-blocking); fix = site-wide sweep.
- **Ebonspire launch (June 2026)** — flip "releases June 2026" → "available now", add Book + Offer with verified ASIN, mirror the 3-edition pattern.
- **Carry-forwards:** OG images for ~22 older blog posts; GA4 purchase verification in Realtime; "Buy Direct — Instant Download" lead-CTA; Google Merchant Center; Ebonspire cover for books.html. **`/free/` minor:** 8th lite SKU not featured (by design); no per-page OG card for `/free/`.

---

## Branches and tags

```
main    production — HEAD == origin/main (17de766) + this unpushed HANDOFF refresh on top
```

**Backup tags (newest first, LOCAL only):** `backup-pre-stage2` · `backup-pre-character-cards` · `backup-pre-hub-row` · `backup-pre-character-cluster` · `backup-pre-free-nav-sweep` · `backup-2026-06-03` · earlier remain.

**This session's commits (newest first, ALL pushed & live except this HANDOFF refresh):**
`17de766` Stage 2 fantasy selves · `ef2ef68` file_download GA4 on card downloads · `66b6ea5` Package-2 character share cards + og/twitter + downloads · `65b0d40` hub one-row layout · `35b9896` character cluster (5 pages + hub + Person schema + portraits + wiring) · `47faaa1` dateModified bump · `72a3434` no-email rename + redirect stub · `380bfa9` Etsy/Gumroad income post. Session-start tip was `945e528`; `227ced6` (prior HANDOFF) was pushed early this session.

---

## Hard-won lessons this session

- **`core.autocrlf=true` is a trap (#20).** Working tree is CRLF, repo is LF; MSYS grep hides CR; a `\n` regex won't match. Every sweep reads→normalizes→edits→writes-back-original-eol. `git diff --check` clean is the proof.
- **Prototype-first, then replicate.** Josh signs off a **Theo-first** page/card/section before each build fans out to the other four. Build the one, render it (preview screenshot + Read the JPG), get approval, THEN generalize into a match-checked generator/sweep.
- **`theo-min.png` was a mock, not a source (#2, #21).** It had baked DejaVu placeholder text; my first card doubled the text. Inspect provided assets before compositing — use the clean `.webp`.
- **Reproduce-byte-for-byte to validate a generator.** `_build_characters.py` transforms the *approved* `theo.html` into the others via match-checked span-swaps (each Theo span asserted to appear exactly N times) — so the approved prototype carries through untouched and a mismatch aborts loudly.
- **#9 mirror is broader than FAQ:** `blog.html`'s ItemList mirrors its visible cards 1:1; the character pages' Person `alternateName` mirrors the visible fantasy name. Edit the visible thing → edit its schema twin.
- **Review a brief by checking its premises against the repo (#2).** The relink brief named only 7 posts (there are 16 files), claimed a `/tools/` index + `/resources/` tool links (neither exists), and its "don't alter anchor text" rule collided with one display-URL — all surfaced by grepping, not by reading the brief alone.
- **Render share assets before trusting them.** Read the generated JPG + serve the page in the preview (`preview_start` → screenshot). Caught the mock-text doubling, confirmed scrim legibility (Kael), the long-name auto-fit (The Wanderer), and the hub two-row alignment.
- **Commit messages via here-doc `-F -`; `main` is production (no PR flow); commit ≠ push (wait for Josh).** Backup-tag before each arc.

---

**End of handoff.** State: live, clean; the full **Overlayed Echoes character cluster** (Package 1 pages+hub, Package 2 share cards, Stage 2 fantasy selves) + the income post + the no-email rename are all pushed & post-deploy-verified at `17de766`; the **tools-subdomain relink is reviewed but NOT executed** (Arc 6 / Open items — the likely next task, prereq met). HEAD == origin/main with this HANDOFF refresh unpushed on top. New session: read this doc, run the First-Steps block, ask Josh whether to push the HANDOFF refresh, then take direction.
