# 🟢 builtbyjoshstudio.com — Session Handoff (2026-06-23) — favicons (J + Tynkr-bear) · Little Acre Learning brand link (footer 118pp + Org schema + About card) · dark-footer contrast fix · **READ-ONLY SEO+GEO AUDIT of the 8 paid product pages + /free/ lite hub DONE — findings below; NEXT = the fix batch (un-hide + schema-encode the free tier)**

**This block is the current live state.** The 2026-06-16 block below (and the 06-15 / 06-08 / 06-07 / 06-05 / 06-04 blocks) remain valid for the **KINETIC token reference, the EOL byte-sweep workflow, and STANDING INSTRUCTIONS #1–#21** — only their STATE / first-steps are superseded here.

**STATE:** **Live = `origin/main` = `2c69918`** (in sync). Tracked tree clean (untracked only `.claude/`, `.netlify/`, this session's `tools/_*.py` scratch, `HANDOFF-*.md`). **`main` IS production** — push deploys live via GitHub Pages `pages-build-deployment` (~45–60s). Commit on `main`; push ONLY on Josh's explicit go; `git tag backup-pre-<x>` before each arc; after each push `gh run watch` then verify live cache-busted (`?x=<ts>`). **Separate TOOLS repo** (`builtbyjoshstudio-cyber/tools`, clone `C:\Users\jotra\tools`, serves tools.builtbyjoshstudio.com) is in sync at `f9aa01f`; Antigravity keeps a 2nd clone at `.gemini/antigravity/scratch/tools` (it must `git pull` before it pushes).

## ✅ SHIPPED THIS SESSION — 3 main commits + 1 tools commit (all live + edge-verified)
1. **`66e665f`** — **Site favicon (Built by Josh "J" icon).** favicon.ico (16/32/48) + 16/32 PNG + 180 apple-touch generated from the brand J icon, placed at site ROOT; standard `<head>` link block added to **all 120 pages** (root-absolute, EOL-preserving, idempotent). Replaces the browser-default globe. `backup-pre-favicon` (`921113d`).
2. **`66125b1`** — **Little Acre Learning brand link.** New sibling brand (littleacrelearning.com — children's coloring/activity books, ages 2–10), handled like Tynkr, **brand-attribution layer ONLY** (NOT the content layer — audience-mismatch rule). Footer line on **118 pages**: "Tynkr Tools & Co and `<a>Little Acre Learning</a>` are brands of Built by Josh Studio LLC" (only LAL linked, target=_blank rel=noopener). index.html FULLER Org node: LAL added to `subOrganization` (url + parentOrganization: Built By Josh Studio) + `brand`. about.html: 3rd `.brand-card` (logo-less, `#46604E` sage-green = LAL's real brand color) + H1/H2/two "distinct lines" copy → three brands. Slim ~99-page shared Org node UNTOUCHED. `backup-pre-littleacre-link` (`66e665f`).
3. **`2c69918`** — **Dark-footer contrast fix.** The attribution line + LAL link were near-invisible on the `#14130e` footers (homepage + legal + 40 collections). `css/tokens.css`: `[data-theme="dark"] .footer-legal` text → `rgba(255,255,255,0.66)`, link → `#cfe0f5` + underline, hover white (one shared edit covers legal + the 40 collections; loads after inline, wins by specificity). `index.html` inline: same rules (bespoke footer is NOT data-theme="dark"). Verified via computed styles (~7:1). `backup-pre-footer-contrast` (`66125b1`).
**TOOLS repo `f9aa01f`** — Tynkr planner-bear favicon set (from the brand `tynkr-icon.png`) at root + `<head>` block on all 17 tool pages. Live on tools.builtbyjoshstudio.com. (Backup tag in the tools repo: `backup-pre-favicon` @ `8e044e2`.)
*(Brand assets came from `C:\Users\jotra\Downloads\Website build prompt (2).zip` → extracted to `%TEMP%\brandzip\design_handoff_builtbyjosh\assets`. That zip also contained an UNDECLARED `support.js` — NOT used, left alone, flagged to Josh.)*

## 🔬 IN-FLIGHT — SEO + GEO AUDIT COMPLETE (read-only, NO commits) → NEXT = the fix batch
A 9-agent workflow audited the **8 paid product pages** (`products/{creator-content-os, creator-os-full-stack, creator-business-os, creator-finance-os, creator-launch-os, creator-product-os, ultimate-budget-workbook, home-buying-mortgage-workbook}.html`) + the **`/free/` lite hub**, through SEO + GEO (AI-answer-engine citation) lenses. Every load-bearing claim was re-verified against the files. **This section IS the fix-batch spec.** Josh is about to send a "big prompt" to start the fixes — it = this batch.

**LITE FOOTPRINT (verified):** NO standalone lite pages. The 8 lite versions are **$0 Lemon-Squeezy lead-magnet checkouts** (`js/checkout-config.js`, real `ls` URLs, `price:0`). SEO-visible lite surface = `/free/` hub + 7 homepage lite cards + per-paid-page lite CTAs. **BUT:** the per-paid-page free CTAs ship **`display:none`** (the `data-lite` blocks; gated "until LS lite goes live" — but the SKUs ARE live), so the only crawlable free path from a paid page is the nav "Free" link; every `/free/` "Free Lite Version" `ItemList` item's `url` points to the **PAID** product page; `/free/` lite CTAs have **no static `<a href>`** (JS-injected); homepage lite cards ARE static `<a href="products/<paid>.html">` (→ the PAID page; checkout.js adds the $0 LS overlay). **`$0` is in NO structured data anywhere** (each paid Product = ONE Offer at $27 / $34.99, no `price:0` / `AggregateOffer`). NET: **the free funnel is fully built but SEO/GEO-invisible; what IS crawlable points at paid pages.**

**VERDICT:** Paid on-page SEO ≈ **85% done** — mature, consistent template; the open work is low-sev polish + 3 medium bugs, NOT a rebuild. **The single biggest structural gap = the invisible free tier** (self-inflicted by display:none/JS gating — the content EXISTS in hidden markup; the win is making it crawlable + schema-visible, NOT writing more). GEO warrants a **narrow batch that overlaps the lite fix**.

**FIX BATCH (highest-return first, every item traceable to an audit finding):**
1. **Machine-readable `$0` on the paid Products** — add a 2nd `Offer` (`price:0`) / `AggregateOffer` to each Product JSON-LD + ONE static visible "a free Lite version is available" sentence. Unlocks "is there a free version of X?" / "best free Notion template for…" citations across 8 pages. **START with `creator-product-os`** (its lite LS URL is already live, yet the CTA still ships `display:none`/JS-only — flagged HIGH).
2. **Un-hide the paid-page lite CTA** — the `data-lite` `display:none` blocks → a static, descriptive in-content free anchor (flows link equity + makes the lite-vs-paid delta extractable, not buried).
3. **Fix the `/free/` name↔URL contradiction** — lite `ItemList` items say "Free Lite Version" but `url` = the $27 paid page; point them at a `/free/#<card>` fragment (or a real free target). Also give the 7 `/free/` download CTAs a real static `href`.
4. **Add a `/free/` FAQPage + visible Q&A** for free-intent queries ("any catch / really free?", "lite vs paid?", "need my email?") — the answers already exist in prose; shape them as Q&A.
5. **Reconcile contradictions:** `ultimate-budget-workbook` stale **`$24.99`** in BOTH visible FAQ + FAQPage schema (vs the $34.99 bundle Offer); `creator-content-os` module count "eight" (body) vs "seven" (FAQ/table/schema); `creator-business-os` "ten" (prose/schema) vs 11 visible cards; `Offer.url` = Lemon Squeezy but visible CTA = Etsy on `creator-launch-os` + `home-buying-mortgage-workbook`.

**LOW-SEV POLISH (optional, fold into the batch):** title↔H1 keyword alignment (move the higher-intent phrase into the title tail vs the brand token) on the 4 Creator-OS + both workbooks; visible breadcrumb href → `/products/` to byte-match schema (6 pages); two `Organization` JSON-LD nodes → stable `@id`, model Tynkr consistently as a Brand of the one LLC (5 Creator-OS); persona H2→H4 skip → H3 (full-stack, launch-os); terse one-word gallery `alt` → "[Product] [module]…" (all 8); undefined `--tynkr-orange` var on sidebar "Deep Dive" link → `--tynkr-accent` (finance, home-buying); `/free/` meta-desc 204→≤155, "Eleven free browser utilities" vs **15** tool cards, ItemList lists **7** lite vs the 8-lite footprint (is the 8th — full-stack-lite "sampler"/Client OS — intentionally absent?).

**ALREADY STRONG — DO NOT TOUCH:** paid single-H1 + gap-free hierarchy + self-canonical (absolute) + indexable; `Product`/`Offer` rich & accurate (`priceValidUntil`, `sku`, Offer name, return policy, shipping); `FAQPage`/`HowTo` byte-match visible copy; **complete 5-sibling interlink mesh** (each Creator-OS links all 5 siblings; workbooks correctly link finance siblings instead); descriptive anchors everywhere (zero "click here"); paid **GEO extractability is genuinely strong** (standalone definition openers, named modules + counts, named personas, question-shaped FAQ, quotable "vs a free Notion template" comparison table on every product); `/free/` fundamentals clean (keyword-first H1/title, all 15 images alt'd + lazy, strong lite-vs-paid prose framing).

**Important:** Josh is pulling **current GEO research from the web separately** before designing fixes — the audit deliberately prescribed NO external/from-memory GEO tactics; every "direction" above is grounded in an observed in-repo gap. Full per-surface audit objects were produced by the workflow (run `wf_00cc83ed-ec1`); this section is the distilled, verified spec.

## Backup tags this session (LOCAL only — `git push` doesn't carry tags)
`backup-pre-footer-contrast` (`66125b1`) · `backup-pre-littleacre-link` (`66e665f`) · `backup-pre-favicon` (`921113d`) + all prior. (Tools repo: `backup-pre-favicon` @ `8e044e2`.)

## First steps for the next session
```bash
cd /c/Users/jotra/builtbyjoshstudio
git log --oneline -6        # HEAD 2c69918 == origin/main; this session = 66e665f..2c69918 (+ tools f9aa01f). A HANDOFF refresh may sit on top [ahead 1] — ask Josh whether to push.
git status                  # tracked tree clean; untracked .claude/, .netlify/, tools/_*.py
# READ this top block + the 🔬 AUDIT section — that IS the fix-batch spec. Wait for Josh's "big prompt".
ts=$(date +%s)
curl -fsS "https://builtbyjoshstudio.com/products/creator-product-os.html?x=$ts" | grep -c 'display: none'        # lite CTA still hidden (fix #2 target; creator-product-os = HIGH)
curl -fsS "https://builtbyjoshstudio.com/free/?x=$ts" | grep -oE 'products/[a-z-]+\.html' | sort -u | head         # /free/ "Free Lite" items -> PAID pages (fix #3 target)
curl -fsS "https://builtbyjoshstudio.com/products/ultimate-budget-workbook.html?x=$ts" | grep -c '24.99'           # stale price still live (fix #5 target)
gh run list --workflow=pages-build-deployment --limit 3
```
Then take direction from Josh (the incoming "big prompt" = the fix batch). The audit is the only in-flight item; NO product-page edits made yet.

---

# 🟢 builtbyjoshstudio.com — Session Handoff (2026-06-16) — 5 commits LIVE: 4 money-tool blog posts + new "Money & Business" blog section/ItemList/nav button · Amazon links normalized to ONE Kindle dp URL (31 links / 21 files) · Overlayed Echoes book-trailer facade + VideoObject (preview + books) · related-card tokens.css fallback fix · GA4 book_amazon_click repair — ALL pushed + edge-verified

**This block is a PRIOR shipped state — superseded for STATE / first-steps by the 2026-06-23 block above.** The 2026-06-15 block below (and the 06-08 / 06-07 / 06-05 / 06-04 blocks) remain valid for the **KINETIC token reference, the EOL byte-sweep workflow, and STANDING INSTRUCTIONS #1–#21** — only their STATE / first-steps are superseded here.

**STATE:** **Live = `origin/main` = `1100023`** — **5 feature commits this session (`4fe8347`..`1100023`), all pushed + edge-verified (cache-busted `?x=<ts>`).** Tracked tree clean (untracked only: `.claude/`, this session's `tools/_*.py` scratch, `HANDOFF-*.md`, `SITE-OVERVIEW.md`, etc.). **`main` IS production** — push deploys live via GitHub Pages `pages-build-deployment` (~45–60s). **Commit on `main`; push ONLY on Josh's explicit go; `git tag backup-pre-<x>` before each arc; after each push `gh run watch` then verify live cache-busted.** *(This HANDOFF refresh is the commit on top — `[ahead 1]`, unpushed; HANDOFF is Jekyll-excluded, zero live effect — ask Josh whether to push it. The session START hit confusion from exactly this stale-ref state, so pushing it keeps origin clean.)*

## ✅ SHIPPED THIS SESSION — 5 commits on `main` (newest first, all live + edge-verified)
1. **`1100023`** — **Book-trailer VideoObject schema + GA4 `book_amazon_click` repair** (`overlayed-echoes-preview.html`). Added a 4th `VideoObject` JSON-LD block (name / description / thumbnailUrl / `uploadDate` / embedUrl / contentUrl + `publisher` `@id` → `#organization`). **`uploadDate` = `2026-06-18T18:00:11-07:00`** — pulled AUTHORITATIVELY from YouTube's served HTML (`curl -A Mozilla … watch?v=eYsgdcggow0 | grep -oE '"(uploadDate|publishDate)":"…"'`), NOT guessed. Also fixed the page's inline `book_amazon_click` handler: detect outbound Amazon by `'amazon.'` not `'a.co'` (the Amazon migration in `5b047de` had silently stopped that GA4 event firing on this page — it was the ONLY `a.co`-keyed handler in the repo; character/dispatch pages key on `data-*-cta` and were fine). Video confirmed public + embeddable (channel *Tales of Ink and Shadows*).
2. **`b7de58e`** — **Overlayed Echoes book-trailer facade (preview + books).** Click-to-load YouTube facade **reusing the existing `/js/lite-yt.js`** (NO YouTube/Google request until click — self-hosted poster + `data-ytid` only; served HTML has 0 `<iframe>` / 0 `ytimg`; the lone `youtube-nocookie` string is the inert VideoObject `embedUrl`). Video ID **`eYsgdcggow0`**, native `<button>` (keyboard), fires GA4 `video_start`. **Preview:** compact 16:9 trailer between hero & Chapter One ("Watch the trailer, then read the opening") — **chapter prose byte-untouched (`<p>` 199→199)**, pure additive. **Books:** supporting trailer inside the OE `.book-section`. New self-hosted poster `images/books/overlayed-echoes-trailer-poster.jpg` (1280×720, from YouTube maxres). `backup-pre-trailer-embed` (`5b047de`).
3. **`5b047de`** — **Amazon links normalized to ONE Kindle dp URL.** Replaced every `a.co/d/*` short link (`04nnjhjC`/`06ZWovoY`/`026ie1Si`/`0cQASed2`/`03rhvH3N`) → **`https://www.amazon.com/dp/B0H3826V21`** across **21 files / 31 occurrences** (books.html, preview, about, index, llms.txt, 5 character pages, 11 writing dispatches). **URL-only** (anchor text/labels/other JSON-LD fields byte-identical). **LEFT INTACT (deliberate):** the 3 `amazon.com/stores/author/B0FPQ3RWWF` author-store links (sameAs + visible "Follow J.S. Warden") — author page, not a book/dp link. **NOTE:** the 3 edition Offer `url`s in books.html (Kindle/Paperback/Hardcover) now all point to the Kindle dp (per Josh "any format/edition"; price/format fields unchanged). `a.co` is now gone repo-wide except HANDOFF historical narrative. `backup-pre-amazon-normalize` (`3b13ea5`).
4. **`3b13ea5`** — **"Money & Business" anchor-nav button.** Added to the blog category bar (`Templates · Learning · Projects` → `+ Money & Business`), `href="#money-business"`. Generic `.blog-nav a` styling + self-contained `--bbj-*` vars (no tokens.css fragility).
5. **`4fe8347`** — **4 money-tool blog posts + new "Money & Business" blog section/ItemList.** New `blog/{freelance-rate-calculator, debt-payoff-calculator, budget-calculator, invoice-generator}.html` — cloned BYTE-FOR-BYTE from `blog/yeast-converter.html` chrome (Article + BreadcrumbList + Organization trio; **NO** WebApplication/FAQPage). Built by a 4-agent workflow (one per post), then deterministically verified (JSON-LD parse, suffix-only-in-title, chrome byte-identical to yeast, related-card links resolve). New **"Money & Business" `<section>`** (4 cards) on blog.html + its **OWN ItemList JSON-LD** (strict 1:1 with the cards) placed AFTER Projects; **existing Projects section/ItemList untouched (still 15)**. `sitemap.xml` +4 (`monthly`, **`0.8`** to match sibling blog entries — NOT the spec's 0.7). Related-card CSS given **tokens.css-matching `var(--x, #fallback)` fallbacks** (see gotcha). `backup-pre-money-blog-posts` (`aa83809`).

## 🧰 KEY KNOWLEDGE / GOTCHAS THIS SESSION
- **`/js/lite-yt.js` is the canonical YouTube-facade system** (5 character pages since 2026-06-15; now also preview + books). Pattern: `<div class="yt-facade" data-ytid data-title data-source><button class="yt-facade-btn" aria-label><img class="yt-facade-poster" … alt=""><span class="yt-facade-play" aria-hidden></span></button></div>` + per-page inline CSS + `<script src="/js/lite-yt.js" defer>`. On click → `youtube-nocookie.com/embed/<id>?autoplay=1&rel=0&playsinline=1` iframe + GA4 `video_start`. **Self-host the poster** (no Google contact until click — matches the privacy.html "Embedded Video" disclosure); img `alt=""` + button `aria-label` (don't double-label). Books facade uses 16:9 (chars use 9:16).
- **Related-card tokens.css fragility (CARRY-FORWARD, partly fixed):** EVERY blog post's `.related-post-card` / `.related-link` uses bare tokens.css vars (`var(--surface/--line-2/--shadow/--accent/--accent-2)`); when `/css/tokens.css` isn't applied (local/no-tokens render) the cards lose bg/border and the "READ THE POST" button goes white-on-cream = invisible. **Only the 4 new money posts got `var(--x, #fallback)` fallbacks; the other ~35 posts still have the latent fragility** — a site-wide fallback sweep is the fix if wanted. Live look is unchanged either way (token wins when present).
- **VideoObject `uploadDate` = verify against YouTube, never guess** (method above). Fabricated dates are a structured-data accuracy violation (same rule as no-fake-ratings).
- **Money posts are NOT in the homepage free-tools list or llms.txt** — only blog.html (card + ItemList twin) + sitemap + sibling related-reading. The money TOOLS live at the subdomain ROOT (`tools.builtbyjoshstudio.com/<slug>/`).

## Backup tags this session (LOCAL only — `git push` doesn't carry tags)
`backup-pre-trailer-embed` (`5b047de`) · `backup-pre-amazon-normalize` (`3b13ea5`) · `backup-pre-money-blog-posts` (`aa83809`) + all prior tags.

## OPEN / DEFERRED (none blocking)
- **Site-wide related-card tokens.css fallback sweep** — the other ~35 blog posts share the invisible-button fragility (only the 4 money posts are fixed). Offered, not done.
- **Trailer date** — VideoObject `uploadDate` = YouTube's `2026-06-18`; Josh confirmed the video is up/public (RESOLVED).
- Carry-forwards still valid from prior blocks: title/meta CTR watch; OG images for ~22 older blog posts; Ebonspire June-2026 launch flip; logo recolor (`images/logo/*`); GSC recrawl. Books cluster stays self-contained.

## First steps for the next session
```bash
cd /c/Users/jotra/builtbyjoshstudio
git log --oneline -8        # HEAD 1100023 == origin/main (this session = 4fe8347..1100023, 5 commits); a HANDOFF refresh may sit on top [ahead 1] — ask whether to push
git status                  # tracked tree clean; untracked .claude/, tools/_*.py, HANDOFF-*.md
ts=$(date +%s)
curl -fsS "https://builtbyjoshstudio.com/blog.html?x=$ts" | grep -c 'id="money-business"'                                  # 1 (money section + nav button live)
curl -sS -o /dev/null -w "%{http_code}\n" "https://builtbyjoshstudio.com/blog/freelance-rate-calculator.html?x=$ts"        # 200
curl -fsS "https://builtbyjoshstudio.com/books.html?x=$ts" | grep -c 'a\.co/'                                              # 0 (Amazon normalized)
curl -fsS "https://builtbyjoshstudio.com/books.html?x=$ts" | grep -c 'amazon.com/dp/B0H3826V21'                            # 5
curl -fsS "https://builtbyjoshstudio.com/overlayed-echoes-preview.html?x=$ts" | grep -c 'data-ytid="eYsgdcggow0"'          # 1 (trailer facade)
curl -fsS "https://builtbyjoshstudio.com/overlayed-echoes-preview.html?x=$ts" | grep -c 'VideoObject'                      # 1
gh run list --workflow=pages-build-deployment --limit 3                                                                     # latest completed/success
```
Then take direction from Josh. Nothing mid-flight.

---

# 🟢 builtbyjoshstudio.com — Session Handoff (2026-06-15) — BIG session: YouTube facade on character pages · 2 new cooking tools + 4 money tools into free-tools · 5 Stage-2 OE dispatches + 3-group index · Amazon KU-link migration · GSC index fix · homepage Lite cards w/ inline $0 download — ALL SHIPPED + edge-verified · NEXT = wire the 4 money-tool blog posts

**This block is a PRIOR shipped state — superseded for STATE / first-steps by the 2026-06-16 block above (its NEXT-task, wiring the 4 money-tool blog posts, is DONE — see `4fe8347`).** The 2026-06-08 / 06-07 / 06-05 / 06-04 blocks below remain valid for the **KINETIC token-resolution reference, the EOL byte-sweep workflow, and STANDING INSTRUCTIONS #1–#21**.

**STATE:** **Live = `origin/main` = `f758dd6`** — **7 commits this session, all pushed + edge-verified (cache-busted `?x=<ts>`).** Tracked tree clean (untracked only: `.claude/`, this session's `tools/_*.py` scratch, `HANDOFF-*.md`, etc.). **`main` IS production** — push deploys live via GitHub Pages `pages-build-deployment` (~45–60s). **Commit on `main`; push ONLY on Josh's explicit go; `git tag backup-pre-<x>` before each arc; after each push `gh run watch` then verify live cache-busted.** *(This HANDOFF refresh is the commit on top — `[ahead 1]`, unpushed; HANDOFF is Jekyll-excluded, zero live effect — ask Josh whether to push it.)*

## ✅ SHIPPED THIS SESSION — 7 commits on `main` (newest first, all live + edge-verified)
1. **`f758dd6`** — **Money & Business Tools subsection (4 free tools).** New labeled "Money & Business Tools" subsection (own header *"Run the numbers, keep the money."* + 4-card grid, reusing `home-tools`/`home-tool-card` CSS, NO new CSS) on the **homepage + `/free/`** free-tools area: **Freelance Rate · Debt Payoff · Budget · Invoice Generator**. 4 new 1200×600 card webps at `images/products/<slug>.webp` (generated from each tool's live `og-preview.jpg`). `llms.txt` +4 + count→"fifteen". **Tools live at the subdomain ROOT** (`tools.builtbyjoshstudio.com/<slug>/`, NOT `/money/` — that's just a category hub). **NOT added to `#tynkr` templates** (per Josh). Placement = separate subsection (vs merge). `backup-pre-money-tools`.
2. **`56e9558`** — **Homepage Lite cards w/ inline $0 download.** 7 free **Lite ($0) cards** in the `#tynkr` templates grid (`.card-tynkr` style, blue "Free" badge + "Free" price) + new **"Free" filter tab** + loaded **`/js/checkout-config.js` + `/js/checkout.js`** on the homepage. Each lite `<a data-checkout="<slug>-lite">` statically links to the product page (fallback) and **checkout.js upgrades it to the Lemon-Squeezy $0 hosted checkout** (email capture). Verified post-JS DOM dump: 7 buttons→LS, lemon.js NOT loaded (free path). All 8 lite SKUs in `js/checkout-config.js` are live (`price:0`, real `ls`). `data-cat="lite notion|spreadsheet"`. `backup-pre-lite-homepage`.
3. **`c0f4720`** — **GSC indexing fix** (off two "new reasons" emails). `blog.html` was the ONLY page missing a canonical → added a self-canonical (resolves the 1-page "Duplicate, Google chose different canonical"). Removed the **noindex `/legal/` entry from `sitemap.xml`** (a noindex URL shouldn't be sitemapped → resolves the sitemap "Excluded by noindex" flag); `legal/` stays intentionally `noindex`. *(Bigger GSC picture from the coverage xlsx: 49 "Discovered – not indexed" + 8 "Crawled – not indexed" = authority/time, NOT a code bug.)* `backup-pre-seo-index-fix`.
4. **`9883262`** — **Amazon KU-link migration.** Current KU link = **`https://a.co/d/04nnjhjC`** (Josh-supplied; old `06ZWovoY` stale; the new dispatch markdown's `089qg3LF` was NEVER used). Repointed **all 15 VISIBLE `href="…06ZWovoY"` CTAs → `04nnjhjC`** across **13 files**: 6 dispatches + 5 character pages + `books.html` ×2 + `overlayed-echoes-preview.html` ×2-VISIBLE. **Left untouched (per Josh — separate identity/schema call):** the 6 JSON-LD `sameAs`/`"url"` `06ZWovoY` in `about.html`/`index.html`/`preview` (preview schema lines 57/72), + edition links (`026ie1Si`/`0cQASed2`/`03rhvH3N`). **Also still `06ZWovoY` (noted, out of scope):** `llms.txt`'s OE-novel link. `backup-pre-amazon-migrate`.
5. **`951456c`** — **5 Stage-2 OE field dispatches + index restructure.** New `writing/{seven-feet-of-silver, exactly-as-designed, the-dagger-flip, edge-of-my-chair, load-bearing-grin}.html` (Theo/Angela/Marcus/Lena/Kael, "the night after the first session"). Chrome **sliced byte-for-byte from `corruption-of-immersion.html`** (dispatch trio = BreadcrumbList + BlogPosting + Organization; `data-glass="books"`, Bricolage/Hanken). `source_page = dispatch-<full-slug>`, Amazon = `04nnjhjC`, preview link normalized to `../`. `/writing/index.html` → **3 groups**: "The calm before" (5 Stage-1) / **"The first session"** (5 new) / **"And later"** (relabeled from "And after"; corruption); dateline + framing updated for 11 dispatches. `sitemap.xml` +5 (priority 0.6), `llms.txt` +5. Generator `tools/_build_stage2.py` (the old `_build_dispatches.py` was stale — `DM Sans`/`preconnect`/blank-line bugs). `backup-pre-stage2-dispatches`.
6. **`983570d`** — **2 new cooking tools → main-site free-tools.** Added **Cookware & Pan Guide + Recipe Nutrition Calculator** cards to the homepage Free Web Tools grid + `/free/` + `llms.txt`; count "Nine"→"Eleven"; 2 new card webps (from subdomain og-previews). **The subdomain HUB was already fully done by Antigravity** (counter, cards, footer, sitemap) — I did only the main site. `backup-pre-new-tools`.
7. **`dfd0b7d`** — **Click-to-load YouTube facade on the 5 OE character pages.** Self-hosted poster (`images/characters/<slug>-reveal-poster.jpg`, 5 new) + a `<button>`; video ID in `data-ytid` (no YouTube URL in served HTML). New shared **`/js/lite-yt.js`** builds a `youtube-nocookie.com/embed/<id>` iframe ONLY on click. Per-page inline CSS. `privacy.html` gained an "Embedded Video (YouTube)" disclosure + last-updated bump. Verified: 0 `youtube-nocookie`/`ytimg`/`<iframe>` on the served pages until click. **Video IDs:** Kael `JZyBmOKNlcs` · Theo `zpQhOHdwSUk` · Angela `_-PIyLQ0FuA` · Marcus `VdDWx5DBnxQ` · Lena `2Zbq12kgaMY`. `backup-pre-yt-facade`.

**Also this session — SEPARATE Antigravity-owned tools repo (`builtbyjoshstudio-cyber/tools` @ `C:\Users\jotra\.gemini\antigravity\scratch\tools`, served at `tools.builtbyjoshstudio.com`, NOT this repo):** early-session I fixed the cooking-hub hero counter **"08"→"09"** (`4635f49`) + regenerated the hub `og-preview.jpg` from the corrected light-theme hero (`f61bcb2`), both pushed + live (remote `builtbyjoshstudio-cyber/tools`, own Pages deploy). Antigravity later took the hub to **11 tools** + built the **`/money/` hub + the 4 finance tools (live at the subdomain ROOT)** itself. **Antigravity owns that repo + deploys; I only touch the main site + consume the tool URLs.**

## 🔄 IN-FLIGHT / NEXT TASK — wire the 4 money-tool blog posts (split: Claude WRITES, this session WIRES)
Josh is having **a separate Claude session write 4 blog posts**, one per money tool: `blog/{freelance-rate-calculator, debt-payoff-calculator, budget-calculator, invoice-generator}.html`. **Full spec at `C:\Users\jotra\Downloads\money-tool-blog-post-spec.md`** (written this session from a read-only audit): clone `blog/yeast-converter.html` chrome byte-for-byte; **newer pattern = Article + BreadcrumbList + Organization JSON-LD only** (NOT the WebApplication/FAQPage variant the 4 oldest tool posts carry); fixed eyebrow "Projects · Software Utilities"; `<title>` carries " by Tynkr Tools &amp; Co" (H1/headline/breadcrumb un-suffixed); tool links ALWAYS absolute `https://tools.builtbyjoshstudio.com/<slug>/` + `target="_blank" rel="noopener"`; `.post-summary` "The Short Version"; mid-article `.inline-cta`; sticky tool-promo sidebar; `.related-posts` ×5; fixed `author-bio` + `studio-sig`; ISO `datePublished`.

**MY wiring job once the 4 post files land in `blog/` (Claude does NOT touch `sitemap.xml`/`blog.html`):**
1. `sitemap.xml` — +4 `<url>` entries (`<lastmod>` build date, `monthly`, `0.8`).
2. `blog.html` — +4 visible `<a class="article-card reveal">` cards in the **Projects** section (newest-first, position 1 each).
3. `blog.html` — +4 **Projects `ItemList` JSON-LD twins** at position 1, renumbering the rest. **STRICT 1:1 mirror** (visible cards == ItemList: same name/url/order — STANDING #9). Projects ItemList is currently 15 items.
Then verify (`json.loads` all JSON-LD, card-count == ItemList-count) → diff → Josh's go → push → `gh run watch` → cache-busted live-verify. Money tool URLs (root) + card/og images (`images/products/<slug>.webp`) already exist.

## Backup tags this session (LOCAL only — `git push` doesn't carry tags)
`backup-pre-money-tools` (`56e9558`) · `backup-pre-lite-homepage` (`c0f4720`) · `backup-pre-seo-index-fix` (`9883262`) · `backup-pre-amazon-migrate` (`951456c`) · `backup-pre-stage2-dispatches` (`983570d`) · `backup-pre-new-tools` (`dfd0b7d`) · `backup-pre-yt-facade` (`01c4353`) + all prior tags. (Tools repo, separate: `backup-pre-hub-count-fix`.)

## First steps for the next session
```bash
cd /c/Users/jotra/builtbyjoshstudio
git log --oneline -9        # HEAD f758dd6 == origin/main (this session = dfd0b7d..f758dd6, 7 commits); HANDOFF refresh may sit on top [ahead 1]
git status                  # tracked tree clean; untracked .claude/, tools/_*.py
ts=$(date +%s)
curl -fsS "https://builtbyjoshstudio.com/?x=$ts" | grep -c 'id="money-tools"'                                   # 1 (money subsection live)
curl -fsS "https://builtbyjoshstudio.com/?x=$ts" | grep -c 'data-cat="lite'                                     # 7 (homepage lite cards live)
curl -fsS "https://builtbyjoshstudio.com/writing/?x=$ts" | grep -c 'The first session'                          # 1 (Stage-2 dispatch group live)
curl -fsS "https://builtbyjoshstudio.com/writing/characters/theo.html?x=$ts" | grep -c '04nnjhjC'               # 1 (Amazon KU link migrated)
curl -fsS "https://builtbyjoshstudio.com/writing/characters/theo.html?x=$ts" | grep -cE 'youtube-nocookie|<iframe'   # 0 (facade: no YT until click)
gh run list --workflow=pages-build-deployment --limit 3                                                         # latest completed/success
```
Then: **if the 4 money-tool blog post files are present in `blog/`**, run the wiring pass (sitemap + blog.html cards + Projects ItemList twins, strict 1:1 mirror) → diff → Josh's go → push → live-verify. Otherwise take direction.

---

# 🟢 builtbyjoshstudio.com — Session Handoff (2026-06-08) — paid `/products/` SEO arc SHIPPED (FAQ-schema byte-fix + hub OG/social card + Creator-OS title standardization + content-os relevance/interlinks + full sibling interlink mesh + schema/sitemap completeness) — ON-PAGE ARC COMPLETE · then J.S. Warden book-pages schema/GEO pass

**This block is the current live state.** The 2026-06-07 (evening) block below — and the earlier 2026-06-07 / 2026-06-05 / 2026-06-04 blocks — remain valid for the **KINETIC token-resolution-by-zone reference, the EOL byte-sweep workflow, and STANDING INSTRUCTIONS #1–#21**; only their STATE / first-steps / "🔄 LATEST = likely-next" notes are superseded here. (That prior 🔄 LATEST — the read-only SEO intel report on the paid `/products/` pages — has now been **EXECUTED**; this is the implementation.)

**STATE:** **Live = `origin/main` = `b0bcaa3`** — the **5-commit on-page `/products/` SEO arc is COMPLETE**, plus a free-tools rename (`f140719`) and a **J.S. Warden book-pages schema/GEO pass (`b0bcaa3`; see 📚 LATEST below)**; all pushed + edge-verified (cache-busted `?x=<ts>`). Tracked tree clean (untracked only: `.claude/`, `.netlify/`, `tools/_*.py`, `tools/_fonts/`, `HANDOFF-*.md`, `SITE-OVERVIEW.md`, `_audit_output.md`, plus this session's `tools/_seo_*.py` / `_cos_*.py` / `_extract_cco.py` / `_build_products_hub_og.py` + `_cco_*`/`_cos_*` scratch). **`main` IS production** — push deploys live via GitHub Pages `pages-build-deployment` (~45–60s). **Commit on `main`; push ONLY on Josh's explicit go; backup-tag before each arc; verify live cache-busted after every push.** Nothing mid-flight.

## 📚 LATEST — J.S. Warden book pages: schema + GEO-hygiene pass (`b0bcaa3`) — LIVE
A SEPARATE fiction **hub-quality + GEO-hygiene** arc (NOT a ranking lever) on the 8 book pages: `books.html`, `overlayed-echoes-preview.html`, `writing/characters/index.html` (hub) + the 5 character pages (theo/angela/marcus/lena/kael). Same proven loop (backup-tag → EOL-preserving byte-sweep → JSON-LD-parse verification → diff → Josh's go → push → `gh run watch` → cache-busted live-verify). **`b0bcaa3` shipped + edge-verified:**
- **Genre triple aligned** — OE Book genre (books.html + preview) is now EXACTLY `["Dark LitRPG", "Progression Fantasy", "Survival Horror", "GameLit", "Science Fiction"]` (dropped "Metafiction"); visible genre copy (FAQ answer schema+visible #9 mirror, og/twitter image-alt, cover img-alt, book-subtitle) leads with the triple, keeps "near-future LitRPG / GameLit" as the mechanical descriptor. **Ebonspire genre UNTOUCHED.**
- **`"copyrightYear": 2025`** added to the OE Book node(s) (books.html + preview). Studio footer **© 2026 Built by Josh Studio LLC** left as-is (correct — that's the LLC, not the book ©).
- **Author entity consolidated** — Amazon URL standardized to the **short form `https://www.amazon.com/stores/author/B0FPQ3RWWF`** everywhere (schema + the visible "Follow J.S. Warden on Amazon" link); `books.html#jswarden` Person `sameAs` = `["…/about.html", "…/stores/author/B0FPQ3RWWF"]`; the preview's inline author Person replaced with a consolidated Person sharing the `books.html#jswarden` `@id` + the same 2-entry sameAs (self-contained, not a dangling cross-page ref).
- **Preview og/twitter completed** — added `og:image:alt` + `twitter:title`/`twitter:description`/`twitter:image` (was only `twitter:card`). **Chapter prose untouched (byte-for-byte sacred);** the new cluster link sits in the post-sample CTA section, not the prose.
- **Interlink cluster closed** — preview→characters-hub + hub→preview + each character page→hub (visible links). Books cluster stays **self-contained** — NO cross-links to Tynkr/cooking content (audience-mismatch rule, locked).
- **WebPage JSON-LD node** added to the 6 character pages + the hub (they lacked one; books.html/preview already had one).
- **Meta-desc trims ≤155:** books.html 175→146 · kael 190→131 · theo 181→133 · marcus 179→150 · lena 176→133. (angela/hub/preview already fine.)
- **Compliance preserved:** NO `aggregateRating`/`review` anywhere (book is "Not rated yet" — fabrication = violation); NO `<meta name="keywords">`; canonicals untouched (all self-referential; preview self-canonicals, NOT to books.html); character `<h1>` bare-name kept; books.html stays Book + BookSeries (NO ItemList/CollectionPage).

**LOCKED BOOK FACTS (verified live; keep exact):** genre triple above · author **`J.S. Warden`** (no spaces) in all text/schema — spaced "J. S. WARDEN" allowed ONLY inside cover-art image files · series = **Book 1 of a planned 5** · **AUDIOBOOK = the SHORTER ORIGINAL edition (~2h28m), NOT the expanded novel** — books.html FAQ states this correctly; never imply the audiobook is the full book · **©2025** book copyright (studio-LLC footer © 2026 is separate + correct) · Kansas-only if location arises, surname never appears · author `sameAs` = Amazon-only **short form** (there is NO Audible author page).

**Step-1 read-only audit output saved at `tools/_book_audit.txt`** (script: `tools/_book_audit.py`); apply/verify scripts: `tools/_books_apply.py` + `_books_verify.py`. Backup tag `backup-pre-books-schema` @ `dff0011`.

### Book-pages — candidate NEXT (not done; deliberately out of this pass):
- **`/writing/` dispatch layer (7 pages: `writing/index.html` + 6 dispatches) — NOT yet aligned.** Step-1 audit confirmed they carry **NO old labels** ("Science Fiction"/"Metafiction" absent; they already use "near-future LitRPG" + "Progression fantasy" in the visible pitch). A future pass could bring their **BlogPosting schema / og:image:alt / author sameAs** to genre-triple + short-form parity with the book pages, and add WebPage nodes. EXCLUDE Ebonspire.
- Optional: paste a book URL into Google's Rich Results Test (interactive — not headless-runnable here) to confirm Book/Person eligibility + the no-rating handling.

## ✅ SHIPPED THIS SESSION — the paid `/products/` SEO arc, 5 commits (all live + edge-verified)
Scope was STRICT: the 8 paid `/products/*.html` template pages + the `/products/` hub ONLY — **NOT** the free cooking tools on `tools.builtbyjoshstudio.com`, **NOT** the zodiac art in `/collections/`. Each commit ran the proven loop: backup-tag → EOL-preserving Python byte-sweep (tree is CRLF; `git diff --check` clean = proof) → verification gate (JSON-LD `json.loads`, byte-mirrors, og:image existence on disk) → diff shown → Josh's explicit go → push → `gh run watch` → cache-busted live-verify.

1. **`58cdcf2`** `seo(products): FAQ schema byte-match, hub social tags + OG image, title/meta rewrites` — **9 files (8 HTML + 1 new image)**:
   - **`ultimate-budget-workbook`** — FAQ #1 JSON-LD `acceptedAnswer.text` now **byte-matches the visible `<p>`** (the Excel/Sheets "buy either individually for $24.99 … bundle for $34.99" answer; **visible copy is canonical**). The other 47 FAQ entries already matched. (STANDING #9 mirror.)
   - **`products/index.html` (hub)** — added the missing **`og:image`** + the full **Twitter Card** block (matching the detail-page tag order); `<title>` / `og:title` / `twitter:title` → **`Notion Templates & Budget Spreadsheets — Built By Josh Studio`**. NEW asset **`images/products/products-hub.webp`** = 1200×630 on-brand Kinetic OG card (cream canvas · ink hard-offset panel · blue "TYNKR TOOLS & CO" eyebrow + orange accent · Bricolage-ExtraBold headline · "NOTION OS" / "EXCEL + SHEETS" chips), generated by **`tools/_build_products_hub_og.py`** (Pillow + `tools/_fonts/Bricolage.ttf` + `Hanken.ttf`). **NOTE: it was MISSING on disk → I stopped and got Josh's image decision before wiring (per his explicit "don't point og:image at a 404").**
   - **`creator-product-os` / `creator-business-os`** — `<title>` → `·` pattern; `og:title` + `twitter:title` mirror.
   - **meta descriptions trimmed ≤155** on 6 pages: creator-os-full-stack 175→127 · creator-finance-os 173→131 · home-buying-mortgage-workbook 173→150 · creator-product-os 164→153 · index 163→137 · creator-launch-os 161→135.
2. **`98842da`** `seo(creator-content-os): relevance/CTR pass — "Content OS for Creators" + 2 interlinks` — single page:
   - `<title>` / `og:title` / `twitter:title` → **`Creator Content OS · Notion Content OS for Creators`** (all three mirror); H1 accent span → `| The Notion Content OS for Creators` (kept the `<span class="italic-accent">` structure); eyebrow → `Notion · Creator Content OS`; "What Is" clause → `a Notion content OS for creators`.
   - **Related Creator OS Templates** row: added **Creator Finance OS + Creator Product OS** sibling cards (markup/classes/`View Product ↗` cloned exactly; card copy sourced verbatim from sibling Creator-OS pages) → row now **Full Stack · Business · Finance · Launch · Product** (3→5 cards). The 3 existing `/blog/` links untouched.
   - Pre-push: rendered H1 visually in the preview server — the italic-blue "The Notion Content OS for Creators" reads cleanly on the headline.
3. **`ce60556`** `seo(creator-os): title relevance alignment — 3 pages` — **title-layer ONLY** (each page: `<title>` = `og:title` = `twitter:title`, byte-for-byte) on creator-os-full-stack, creator-launch-os, creator-finance-os. No H1/eyebrow/body/meta-description/interlink changes.
4. **`282dd56`** `seo(creator-os): complete sibling interlink mesh — 10 cards across 5 pages` — workstream #2 sibling-card layer. Each of the 5 pages (full-stack, business, finance, launch, product) had its "Related Creator OS Templates" `related-grid` brought from **3 → 5 sibling cards** (now all 5 siblings). Cards **cloned VERBATIM** from existing live cards (Product/Launch/Business/Finance from `creator-content-os`; Content from `creator-launch-os`) — **no new copy**. **Purely additive (+70/−0 total; +14/−0 per file)** — only `<a class="related-card">` blocks appended inside `related-grid`; blog/Deep-Dive/JSON-LD/head/prices untouched. **Both gates passed** (deterministic Python + a 5-agent adversarial workflow: byte-identical-clone · collateral-clean · JSON-LD per page). Live + edge-verified.
5. **`62dde09`** `seo(products): schema completeness + sitemap lastmod` — Tier-2, **additive only** (no price/checkout/canonical changes; JSON-LD 6/6 still parse on all 8). Added **`priceValidUntil` "2026-12-31"** + **`sku` (= page slug)** to all **8** product Offers, and Offer **`name`** to the 6 Creator-OS Offers (`"<Product> — Notion Template"`; **Full Stack = "… Notion Template Bundle"**) — mirroring the 2 workbooks' existing `"… Excel + Google Sheets Bundle"` shape. All 8 Offers now carry **price · priceCurrency · priceValidUntil · sku · availability · name**. Bumped **all 9 sitemap `lastmod` → 2026-06-08** (were 04-10 / 05-06 / 05-12, predating today's commits) for recrawl; changefreq/priority unchanged. **Structural schema.org validation passed** — all Google-required product fields present so **the price now registers**; `review`/`aggregateRating` absent by design. Live + edge-verified.

**Also shipped this session — SEPARATE free-tools workstream, NOT part of the product-SEO arc:** `f140719` `content: rename tool to "Cooking Timeline Calculator" + fix zbbe ItemList title` — renamed the free **"Reverse Roasting Timeline Calculator" → "Cooking Timeline Calculator"** on the homepage + `/free/` cards + `llms.txt` + the blog WebApplication schema `name` (tool URL slug `reverse-roasting-calculator` **unchanged**; the blog POST kept its name/slug/title/H1/body); and reconciled the `zero-based-budget-excel` ItemList title to its post `<h1>` / card `<h3>` (`task_e92f425c`). Live + edge-verified.

## 🏷 Creator-OS title set — now STANDARDIZED across all six product pages
Format = **`[Product] · Notion [descriptor] for Creators`** (middle-dot `·` separator; `og:title` + `twitter:title` mirror each `<title>` byte-for-byte). Final LIVE titles:
- `creator-content-os` → **Creator Content OS · Notion Content OS for Creators**
- `creator-product-os` → **Creator Product OS · Notion Inventory for Creators**
- `creator-business-os` → **Creator Business OS · Notion CRM for Creators**
- `creator-finance-os` → **Creator Finance OS · Notion Finance for Creators**
- `creator-launch-os` → **Creator Launch OS · Notion Launch Planner for Creators**
- `creator-os-full-stack` → **Creator OS Full Stack · Notion Bundle for Creators**

(The `/products/` **hub** is intentionally separate: `Notion Templates & Budget Spreadsheets — Built By Josh Studio` — em-dash + brand suffix, NOT the Creator-OS product pattern. The two Excel/Sheets workbooks also keep their own `·`-pattern titles.)

## ⛔ Review / AggregateRating schema — STRUCK (not deferred)
There are **zero product-specific reviews** on any Tynkr product, so **no compliant `AggregateRating` / `review` schema is possible** (reinforces STANDING #9's "no aggregateRating/review"). **Do NOT implement review stars on any product page** until genuine, product-specific reviews **exist and are displayed visibly on the page first** (Google requires the visible review to back the markup). **Open question (flagged):** whether direct **Lemon Squeezy** sales can collect public reviews at all — if LS has no public-review mechanism for these SKUs, this lever stays permanently closed for LS-only products.

## 🔗 Interlinking cluster (workstream #2) — COMPLETE (sibling-card layer CLOSED)
**Full sibling mesh shipped (`282dd56`):** all **6** Creator-OS product pages now link **all 5 siblings** in their `related-grid` (`creator-content-os` was wired in `98842da`; the other 5 completed in `282dd56`). Symmetric, no self-links, verbatim cards. **Productivity-to-productivity ONLY** — free cooking tools + fiction/books stay OUT of this cluster.
**Blog-link layer — DELIBERATELY COMPLETE, not pending.** The Notion `/blog/` graph is intentionally **topical/asymmetric** with **hand-written contextual anchors** (~3 posts/page, matching the Content-OS model: `complete-os` + the page's own module post + 1 topical sibling). Densifying to a full 6-post mesh was **considered and explicitly DECLINED** — forcing anchors onto non-topical combinations adds noise, not signal. **Do NOT "fill this gap" in a future session — it is by design.** (6-post blog universe: `complete-notion-os-for-creator-business` + `notion-{content,product,business,finance,launch}-os-for-creators`.)

## 🏁 ON-PAGE `/products/` SEO ARC — COMPLETE
**Full session sequence (5 commits):** `58cdcf2` (FAQ fix + hub social + title/meta) → `98842da` (Content-OS relevance) → `ce60556` (Creator-OS title alignment) → `282dd56` (sibling interlink mesh) → `62dde09` (schema completeness + sitemap recrawl). **Every on-page lever the 2026-06-08 GSC data flagged as winnable is shipped — the site is as optimized as current data supports.**

### Tier-2 technical audit — verdict LOGGED (performance side judged SOUND)
A full read-only audit of all 8 product pages ran (LCP · images · `<head>` · CSS · schema · sitemap). **Performance is fundamentally sound:** text-LCP (no above-the-fold hero image), lazy galleries, `font-display:swap`, no own-goals. **Items ASSESSED and DELIBERATELY DECLINED — do NOT "fix" these in a future session (judged not worth the change, NOT overlooked):** **#4** font preload (swap makes it marginal) · **#5** gallery `srcset`/thumbnails (an asset-regen project for below-fold lazy images) · **#6** defer stylesheets · **#7** img `width`/`height` (CLS already handled by CSS `aspect-ratio`) · **#9** lite-tier in schema (muddies the rich result) · **#10** GA4/charset order. Only the Tier-2 schema/sitemap items (#1/#2/#3/#8) were worth shipping — done in `62dde09`.

### Next levers — BOTH off-page (NOT website / NOT Claude Code work)
(a) **Measure:** re-pull GSC **~2026-06-29** (2–3 wks) — did the Content-OS relevance pass (`98842da`) move **pos 14.3** toward page one, and did the title rewrites shift CTR? (b) **Reach/demand:** Substack cadence, social distribution, getting the **6 Notion blog posts** in front of an audience.

## Backup tags this session (LOCAL only — `git push` doesn't carry tags)
`backup-pre-books-schema` (`dff0011`) · `backup-pre-schema-sitemap` (`f140719`) · `backup-pre-tool-rename` (`e8a6e01`) · `backup-pre-ws2-interlinks` (`b554a35`) · `backup-pre-cos-titles` (`98842da`) · `backup-pre-content-os-relevance` (`58cdcf2`) · `backup-pre-products-seo` (`d2fc1d9`) + all prior tags.

## OPEN / DEFERRED (none blocking)
- **🆕 Social re-scrape (Josh, manual):** the hub gained a brand-new OG image and `og:title` changed on the 6 Creator-OS pages + `creator-product-os`/`creator-business-os` `twitter:title` — run the changed `/products/` URLs through the FB Sharing Debugger ("Scrape Again") + LinkedIn Post Inspector to refresh cached cards — **do this before next sharing those links.**
- ~~Interlinking workstream #2~~ — **DONE/CLOSED**: sibling mesh complete (all 6 pages × 5 siblings); blog layer deliberately complete (see above). No further interlink work on the Creator-OS pages.
- Carry-forwards still valid from prior blocks: title/meta CTR watch; OG images for ~22 older blog posts; Ebonspire June-2026 launch flip ("releases June 2026" → "available now"); logo recolor (`images/logo/*`); ~~the pre-existing `blog.html` `zero-based-budget-excel` card↔ItemList mismatch (`task_e92f425c`)~~ — **RESOLVED in `f140719`** (ItemList name reconciled to the post `<h1>` / card `<h3>`); GSC merchant re-crawl validation.

## First steps for the new session
```bash
cd /c/Users/jotra/builtbyjoshstudio
git status                                    # tracked tree clean; untracked .claude/, tools/_*.py, HANDOFF-*.md
git log --oneline -12                         # HEAD b0bcaa3 == origin/main (book pages on top); products arc = 58cdcf2..62dde09
ts=$(date +%s)
curl -fsS "https://builtbyjoshstudio.com/products/?x=$ts" | grep -c 'products-hub.webp'                              # 2 (hub og:image + twitter:image live)
curl -fsS "https://builtbyjoshstudio.com/products/creator-os-full-stack.html?x=$ts" | grep -c 'class="related-card"'  # 5 (full sibling mesh live)
curl -fsS "https://builtbyjoshstudio.com/products/creator-finance-os.html?x=$ts" | grep -oE '<title>[^<]*</title>'   # Creator Finance OS · Notion Finance for Creators
gh run list --workflow=pages-build-deployment --limit 3                                                              # latest completed/success
```
Then take direction from Josh. The paid `/products/` SEO arc is fully shipped + edge-verified; nothing mid-flight.

---

# 🟢 builtbyjoshstudio.com — Session Handoff (2026-06-07, evening) — merchant schema fix + homepage OG screenshot + FULL de-glass + 8 tool-image swaps + cost-per-serving & yeast blog posts + 9th free tool (Yeast Converter)

**This block is a PRIOR shipped state (2026-06-07 evening) — superseded for STATE / first-steps by the 2026-06-08 block above; its 🔄 LATEST SEO-intel report has since been EXECUTED (see that block).** The earlier 2026-06-07 block below (Kinetic unify + 8th tool) and the 2026-06-05 / 2026-06-04 blocks remain valid for the **KINETIC token-resolution-by-zone reference, the EOL byte-sweep workflow, and STANDING INSTRUCTIONS #1–#21** — only their STATE / first-steps / "glassmorphism still present" notes are superseded here.

**STATE:** **Live = `origin/main` = `4ec57f1`** — everything through the Yeast Converter blog post is live + deploy-verified. Local `main` runs a couple of HANDOFF-refresh commits ahead of origin (Jekyll-excluded, no live effect — push or leave per Josh). Tracked tree clean (untracked only: `.claude/`, `.netlify/`, `tools/_*.py`, `tools/_fonts/`, `HANDOFF-*.md`, `SITE-OVERVIEW.md`, `_audit_output.md`). **`main` IS production** — push deploys live via GitHub Pages `pages-build-deployment` (~45–60s). **Commit on `main`; push ONLY on Josh's explicit go; backup-tag before each arc; verify live cache-busted (`?x=<ts>`) after every push.** Nothing mid-flight.

## 🔄 LATEST — SEO intel report for the paid Tynkr Tools product pages (read-only, NO commits) — likely next: implement product-page SEO fixes
Josh is collaborating with **Claude (web)** on optimizing the **paid Tynkr Tools template product listings** — the 8 `/products/*.html` pages (6 Creator Notion-OS templates + the Ultimate Budget & Home-Buying Excel/Sheets workbooks) + the `/products/` hub. A complete read-only intel report was produced for that handoff:
- **Report file:** `C:\Users\jotra\Downloads\tynkr-paid-templates-seo-intel.md` (~300 KB / 4,266 lines) — per-page `<title>`/meta + char counts, full OG/Twitter, canonical, **49 verbatim JSON-LD dumps** (Product/Offer, FAQPage, BreadcrumbList, Organization), H1–H3 outlines, full body copy + FAQs, image tables (dims/format), internal links, pricing & purchase (paid + lite SKU, LS/Etsy), site/technical context, and a known-issues scan.
- **Scope (strict):** ONLY the paid Tynkr Tools templates in `/products/`. The free kitchen tools on `tools.builtbyjoshstudio.com` and the zodiac **art** collections in `/collections/` are OUT of scope.
- **Issues the report flagged (candidate fixes for the next pass):** `products/index.html` (hub) is **missing `og:image` + the entire Twitter Card block**; `ultimate-budget-workbook` **FAQ #1 JSON-LD `acceptedAnswer` ≠ the visible `<p>`** (rich-result risk — the other 47 FAQ entries byte-match); `<title>` over 60 chars on `index`(72) / `creator-product-os`(69) / `creator-business-os`(64); meta-description over 160 on 6 pages (full-stack 175, finance 173, home-buying 173, product 164, index 163, launch 161); **two competing `<title>` patterns** — 5 pages use `· …` (no brand), 3 use `| … — Tynkr Tools & Co` — and `og:title` diverges from `<title>` on the `|` pages. **Clean (no action):** prices agree across page / JSON-LD Offer / `js/checkout-config.js` / homepage `#tynkr` cards; canonicals self-reference correctly; all 8 product `og:image` files exist (no 404s); no `<meta name="keywords">`.
- **If asked to IMPLEMENT product-page SEO fixes:** the pages are **standalone HTML** (no template engine — edit each file individually; use the EOL byte-sweep, tree is CRLF). Checkout data is centralized in `js/checkout-config.js` (8 paid + 8 lite SKUs); product OG images are **1600×1600 webp** at `/images/products/<slug>.webp`. **Per the #9 FAQ-mirror rule, any FAQ JSON-LD `acceptedAnswer` edit MUST be matched byte-for-byte to the visible `<p>` (and vice-versa).** Standard hard rules apply: **never** touch prices, Lemon-Squeezy/Etsy URLs, GA4, canonicals, or identity copy unless Josh directs; commit on `main`, **push only on his explicit go**, backup-tag before each arc, verify live cache-busted after each push.

## ✅ SHIPPED THIS SESSION — 14 commits (`4c7f100`→`4ec57f1`), all live + deploy-verified, each with a LOCAL backup tag
1. `4c7f100` **Merchant-listings schema fix** — nested `shippingDetails` + `hasMerchantReturnPolicy` INSIDE each `offers` object on all **38 generated collection pages** (relocated the return policy up from Product level + added a $0 `OfferShippingDetails`, matching the product pages + the `chinese-zodiac-art` hub). Clears the GSC "Missing … (in offers)" warnings. JSON-LD only.
2. `c63985a` **Homepage OG image** — replaced `images/og/og-home.webp` (was a designed "Tools for your mind / Art for your space" card) with a **literal 1200×630 screenshot of the live split hero**. Same URL; image-only.
3. `cc373dd` **FULL de-glass → Kinetic** — removed the LAST glassmorphism remnants site-wide: `.home-tool-btn` (homepage + `/free/`) inset-sheen/glow/lift → ink border + `4px 4px 0` hard offset + press-down; `.home-tool-thumb` translucent border → solid `var(--line)`; blog-hub `.read-more` same glassy box-shadow → Kinetic; `/free/` nav translucency + white rim-light glow → solid; removed `/free/` vestigial blur washes. **Glassmorphism is now 0 site-wide.**
4–11. **8 cooking-tool card images swapped** (`40bffb2` recipe-scaler · `2aaa332` reverse-roasting · `966c2e4` pan-swap · `473edeb` perfect-roast · `0b0eb17` brine · `e0db0a1` meat-thawing · `010c397` dough-hydration · `48ae4b1` cost-per-serving) — each `images/products/<slug>.webp` regenerated from Josh's **Optimized OG Previews** (1200×630 JPG → q88 WEBP, cropped `(0,15,1200,615)` → **1200×600** to match the 2:1 card/sidebar ratio). Each verified title/description not clipped (esp. perfect-roast's 3-line desc).
12. `e3271c8` **Cost Per Serving blog post** — new `blog/cost-per-serving-calculator.html` + wired into `sitemap.xml` and `blog.html` (visible Projects card + ItemList twin at position 1).
13. `91a771b` **9th free tool: Yeast Converter** added to the main site — `.home-tool-card` on the homepage Free Tools section + `/free/`, count "Eight"→"Nine free browser utilities" (both pages), `llms.txt` entry, new `images/products/yeast-converter.webp` (1200×600 from its OG preview). Tool lives at `tools.builtbyjoshstudio.com/yeast-converter/`.
14. `4ec57f1` **Yeast Converter blog post** — new `blog/yeast-converter.html` + wired into `sitemap.xml` and `blog.html` (Projects card + ItemList twin at position 1). **All 9 free tools now have a blog post.**

## 🧰 KEY KNOWLEDGE THIS SESSION
- **Tool card images are SHARED — swap-once-updates-all.** `images/products/<slug>.webp` is the homepage card thumb + the `/free/` card thumb + (for the tools with a build-story/how-to post) that post's `og:image`/`twitter:image`/JSON-LD `image` + a `.sidebar-thumb`; `universal-recipe-scaler.webp` is also the sidebar promo across ~7 cooking posts. Replacing the file in place updates EVERY use — no HTML edits. Cards/sidebars display at `aspect-ratio:2/1` (1200×600).
- **Optimized OG Previews folder** = `C:\Users\jotra\Downloads\Optimized OG Previews\` — Josh's 1200×630 JPG per tool (+ a `hub-og-preview.jpg` that is NOT for this repo). Pipeline: **q88 WEBP, crop `(0,15,1200,615)` → 1200×600**; then VIEW the result and confirm the title + (sometimes long) description survive the 15px top/bottom trim.
- **Blog-post template + process (the cost-per-serving / yeast pattern).** Template from `blog/dough-hydration-calculator.html` (or brine) — the **newer/simpler** cooking-post pattern = `Article` + `BreadcrumbList` + `Organization` JSON-LD (NOT the older `WebApplication`/`Offer`/`FAQPage` variant the 4 oldest cooking posts carry). Generate via a read-and-replace `tools/_build_<x>_post.py` that keeps chrome (`<style>`, nav, footer, scripts, the Org node) **byte-identical**, swapping only head fields + the header/body/sidebar/cta-band region. Conventions: open the body with a `.post-summary` **"The Short Version"** block (6/7 siblings have it); `<title>`/`og:title`/`twitter:title` carry the **" by Tynkr Tools &amp; Co"** suffix while `headline`/breadcrumb-name/H1 stay **un-suffixed** (H1 has the italic `<span>` accent); inline tool links **absolute** `https://tools.builtbyjoshstudio.com/<slug>/` with `target="_blank" rel="noopener"` (root-relative would 404); eyebrow/card category "Projects · Software Utilities"; date today; read-time by word count.
- **Orphan-prevention wiring for a NEW blog post (mandatory — cooking posts are NOT on the homepage or in llms.txt; only sitemap + blog.html + sibling related-posts).** (a) `sitemap.xml`: add a `<url>` (lastmod today, `monthly`, `0.8`) after the previous post's entry. (b) `blog.html`: add BOTH a visible **Projects card** AND its **ItemList JSON-LD twin** at **position 1 (newest-first)**, renumbering existing positions. Rule #9 mirror: card count == ItemList count, 1:1 same order, positions sequential (no gaps/dupes). **Projects ItemList is now 15 items.** Verify before commit (an independent re-check workflow was used both times).
- **Free cooking tools are NOT in any JSON-LD ItemList** (the `/free/` ItemList = paid-product lite versions) — adding a tool card is no schema change. The free-tools count phrase ("Nine free browser utilities") lives on BOTH `index.html` and `free/index.html`; bump it when adding a tool.

## OPEN / DEFERRED (none blocking)
- **🆕 Social re-scrape (Josh, manual):** OG images changed on the **7 cooking blog posts** — `building-the-universal-recipe-scaler`, `reverse-roasting-timeline-calculator`, `baking-pan-swap-calculator`, `perfect-roast-pull-temp-calculator`, `brine-calculator`, `meat-thawing-planner`, `dough-hydration-calculator` — plus the **homepage** (`og-home.webp`). Run each URL through the FB Sharing Debugger ("Scrape Again") + LinkedIn Post Inspector. (cost-per-serving + yeast OG images are brand-new — no re-scrape needed.)
- **🆕 GSC merchant re-crawl:** the collection `shippingDetails`/`hasMerchantReturnPolicy` fix is live; Google needs ~1–3 weeks to re-crawl + clear the "14 missing (in offers)" warnings. Optional: hit "Validate Fix" on those two non-critical warnings (confirm the affected URLs are all `/collections/` first).
- **🆕 Pre-existing `blog.html` mismatch (task chip `task_e92f425c`):** the **Learning** section's `zero-based-budget-excel` has a card `<h3>` title ≠ its ItemList `name` (rule #9 mirror violation). NOT introduced this session; reconcile separately.
- **Antigravity:** cost-per-serving `og-preview.jpg` regen on the tools repo (carry-forward; the tools-repo OG is a dark AI mockup).
- Carry-forwards still valid: title/meta CTR watch; future-pass B (og/twitter/headline on the 6 title-changed pages); OG images for ~22 older blog posts; Ebonspire June-2026 launch ("releases June 2026" → "available now"); logo recolor (`images/logo/*`).
- **Backup tags this session (newest→oldest, LOCAL only — `git push` doesn't carry tags):** `backup-pre-yeast-post` · `-yeast-tool` · `-cost-post` · `-toolimg-cost-per-serving-calculator` · `-toolimg-dough-hydration-calculator` · `-toolimg-meat-thawing-planner` · `-toolimg-brine-calculator` · `-toolimg-perfect-roast-pull-temp-calculator` · `-toolimg-pan-swap-calculator` · `-toolimg-reverse-roasting-calculator` · `-toolimg-recipe-scaler` · `-deglass` · `-og-screenshot` · `-merchant-ship` + all prior tags.

## First steps for the new session
```bash
cd /c/Users/jotra/builtbyjoshstudio
git status                                    # tracked tree clean; untracked .claude/, tools/_*.py, HANDOFF-*.md
git log --oneline -16                         # HEAD 4ec57f1 == origin/main; this session = 4c7f100..4ec57f1
ts=$(date +%s)
curl -fsS "https://builtbyjoshstudio.com/?x=$ts" | grep -c 'Nine free browser'                                  # 1 (9th tool listed)
curl -sS -o /dev/null -w "%{http_code}\n" "https://tools.builtbyjoshstudio.com/yeast-converter/?x=$ts"           # 200 (tool live)
curl -sS -o /dev/null -w "%{http_code}\n" "https://builtbyjoshstudio.com/blog/yeast-converter.html?x=$ts"        # 200 (blog post live)
curl -sS -o /dev/null -w "%{http_code}\n" "https://builtbyjoshstudio.com/blog/cost-per-serving-calculator.html?x=$ts"  # 200
curl -fsS "https://builtbyjoshstudio.com/?x=$ts" | grep -c 'Bricolage Grotesque'                                # >0 (Kinetic live)
gh run list --workflow=pages-build-deployment --limit 3                                                          # latest completed/success
```
Then take direction from Josh. The site is fully Kinetic (zero glassmorphism), all 9 free tools are carded on the homepage + `/free/` with fresh 1200×600 images, all 9 have blog posts, and the collection merchant schema is fixed. Nothing mid-flight.

---

# 🟢 builtbyjoshstudio.com — Session Handoff (2026-06-07) — Kinetic card system unified SITE-WIDE + 8th free tool added

**This block is a PRIOR shipped state (2026-06-07 morning) — superseded for STATE/first-steps by the 2026-06-07 (evening) block above; kept for its KINETIC token-resolution-by-zone reference + history.** The 2026-06-05 block below = prior shipped state (its KINETIC quick-ref + the 2026-06-04 **STANDING INSTRUCTIONS #1–#21 still apply verbatim** — only its STATE/first-steps are superseded).

**STATE:** `main` HEAD = `fea55e3` = `origin/main` (in sync; all 11 commits this session pushed + deploy-verified). Tracked tree clean (untracked only: `.claude/`, `.netlify/`, `tools/_*.py`, `tools/_fonts/`, `HANDOFF-*.md`, `SITE-OVERVIEW.md`). **`main` IS production** — push deploys live via GitHub Pages `pages-build-deployment` (~45–60s). **Commit on `main`; push ONLY on Josh's explicit go; backup-tag before each arc; verify live cache-busted (`?x=<ts>`) after every push.** Nothing mid-flight.

## ✅ SHIPPED THIS SESSION — 11 commits, all live + each with a local backup tag
The Kinetic card chrome (`2px solid var(--line-2)` border · `14px` radius · `6px 6px 0 var(--shadow)` · press-down hover) is now on EVERY card/tile site-wide, plus an 8th free tool. Commits (oldest→newest):
1. `24a686d` **collection art tiles + heroes rounded** — folded `.design-card`+`.landscape-img` into the `[data-glass="cosmic"]` chrome rule + `border-radius:14px`, gave `.hero-image` the chrome (all 40 collection pages).
2. `605a165` **homepage zodiac cards** (`.card-bbj` ×60) → Kinetic (index.html inline; dark zone literal `#000` shadow).
3. `7017975` **homepage About brand cards** (`.about-brand-card`) → Kinetic; kept blue/orange top accents (hardcoded `#1d1b15`/`#2f2c24` — `#about` is NOT in the dark-zone token scope).
4. `55c1f49` **free-tool OG/thumbnail images** — regenerated the 7 `images/products/<tool>.webp` (1200×600) from current tool screenshots. These files ARE each cooking tool's og/twitter/JSON-LD image (via its blog post) + the `/free/`+homepage tiles.
5. `7a8a719` **collection-hero glow** (`.collection-hero::before`) → full-bleed `100vw` + softer falloff (was trapped in the centered 1200px hero); tokens.css cosmic override.
6. `be5de44` **collection starfield** (`.stars`) → `z-index:-1` (was twinkling through the static, non-positioned `.style-card` art tiles); tokens.css cosmic override.
7. `910dbf9` **Tynkr product-page tiles** → Kinetic: `gallery.css .gallery-thumb` (lightbox tiles) + `[data-glass="prototype"] .persona/.module-card/.step-card/.related-card` (8 product detail pages).
8. `861f866` **blog hero leftover orange glow removed** — `.article-header::before { background: none; }` (tokens.css; blog-only class, 35 posts).
9. `d443ba6` **remaining directory + secondary cards** → Kinetic: cosmic `.related-card/.review-card/.collection-card/.sister-card:not(.sister-card-current)` (active `.sister-card-current` keeps its orange accent + no-press) + **bare `.product-card`** (products HUB has NO `data-glass`).
10. `d093101` **fiction layer** (`data-glass="books"`): `.character-card` + `.stat-block` → Kinetic (selective — dispatches/bios/CTA links stay warm/literary; `.book-section` was already Kinetic).
11. `fea55e3` **NEW: Cost Per Serving Calculator added to the main site** — 8th `.home-tool-card` on homepage Free Tools + `/free/`, `llms.txt` entry, new `images/products/cost-per-serving-calculator.webp` (1200×600), "Seven"→"Eight". (No JSON-LD lists the cooking tools → no schema change; `/free/` ItemList = paid-product lite versions, untouched.)

## 🎨 KINETIC token-resolution BY ZONE (the #1 subtlety — get this right before adding any component)
- **Light pages:** `--line-2`=#14130e, `--shadow`=#14130e (crisp ink on white).
- **Dark zodiac collections** (`html[data-theme="dark"]`): `--line-2`=#3a362c, `--shadow`=#000.
- **Homepage dark zodiac zone** = a *scoped `--bbj-*` override* on `#builtbyjosh,#western-realms,#chinese-zodiac,#chinese-realms,#landscapes` (NOT a `data-theme` flip): `--bbj-surface`#1d1b15, `--bbj-border`#2f2c24; generic `--line-2/--shadow` stay light there → `.card-bbj`/`.about-brand-card` **hardcode** `#1d1b15`/`#000`.
- **`data-glass` map:** product DETAIL pages = `prototype`; collections incl. hub + `legal/index.html` = `cosmic`; **products HUB `/products/index.html` has NO data-glass** (use bare class rules — verify the class is page-unique first, e.g. `.product-card`/`.article-header` are); homepage = none (scoped override); fiction/`books.html`/`/writing/` = `books`. tokens.css loads AFTER each page's inline `<style>`, so equal/higher-specificity overrides win — most card restyles this session were tokens.css overrides, not per-page sweeps.

## 🧰 Tools subdomain (SEPARATE repo — NOT this one; new knowledge)
`tools.builtbyjoshstudio.com` = a consolidated GitHub-Pages repo living at **`C:\Users\jotra\.gemini\antigravity\scratch\tools\`** (Antigravity/Gemini's workspace — own git + CNAME + `kinetic.css`/`kinetic.js` at root + landing `index.html` hub + 8 tool subdirs). Spec: `scratch/tools/../tynkr-tools-spec.md`. Each tool = `index.html` + `styles.css`(`@import url("../kinetic.css")`) + `script.js` + `sitemap.xml` + `og-preview.jpg`; uses kinetic.css classes (`.glass`/`.glass-panel` cards, `.input-group`, `.btn`/`.btn.primary`, `.tynkr-unit-btn`, `.anatomy` breakdown rows, `.hero`, `.net-band`); 3 themes Light/Mist/Dark via `data-set-theme` + kinetic.js (`startViewTransition` circular-wipe). The **8th tool, Cost Per Serving Calculator, was built + deployed by Antigravity** (live, verified functioning — all calc cases + theme-switching correct). **Antigravity owns the tools repo + deploys; I only added the main-site links.** **Antigravity TODO (told to Josh):** regenerate the cost-per-serving `og-preview.jpg` — it's a dark AI mockup (emoji/glowing gauge/fake "Save Recipe") that misrepresents the real light tool + doesn't match the other tools' clean-screenshot OGs.

## 🛠 NEW gotchas this session
- **Preview-MCP screenshots HANG** on animated layers: the homepage/collection starfield, and the tools' `kx-marquee` + the `startViewTransition` theme-wipe. Freeze via eval (`canvas/.stars` → display:none, inject `*{animation:none}`, cancelAnimationFrame loop) or restart the renderer. **`preview_eval` computed-styles are the reliable check** (more than screenshots). Bust shared CSS then read computed in a SEPARATE eval (the clone-link load is async).
- **Tools-dir thumbnail capture = headless Chrome:** `"/c/Program Files/Google/Chrome/Application/chrome.exe" --headless --disable-gpu --hide-scrollbars --screenshot="<ABS>" --window-size=W,H "file:///..."` — use classic `--headless` (NOT `--headless=new`, which silently drops `--screenshot`). For light theme, temporarily flip the tool's `<html data-theme="dark">`→`"light"`, capture, revert.
- **Preview-MCP launch.json is cached/merged** (editing the repo's `.claude/launch.json` mid-session isn't picked up; its server list was `static-site, spreadsheet-mockup, zodiac-mockup`). To preview a non-repo dir: run `python -m http.server <port>` in bash (`run_in_background`) then `preview_eval(window.location.assign('http://127.0.0.1:<port>/...'))` on an existing preview tab — cross-port nav works.

## OPEN / DEFERRED (none blocking)
- **Antigravity:** cost-per-serving `og-preview.jpg` regen (above).
- Carry-forwards still valid: title/meta CTR watch; future-pass B (og/twitter/headline on 6 title-changed pages); OG images for ~22 older blog posts; Ebonspire June-2026 launch (flip "releases June 2026" → "available now"); **logo recolor** (`images/logo/*` bake navy/gold — Josh/external). Stale `kinetic-retheme` branch deletable; `overlayed-echoes-preview.html` intentionally bespoke.
- Backup tags this session (newest first, LOCAL only — `git push` doesn't carry tags): `backup-pre-costtool · -fiction · -dircards · -blogglow · -producttiles · -starsfix · -heroglow · -tool-og-images · -aboutcards · -home-cards · -zodiac-rounding` + prior `pre-kinetic-backup`(`39dc1e9`).

## First steps for the new session
```bash
cd /c/Users/jotra/builtbyjoshstudio
git status                                   # tracked tree clean; untracked .claude/, tools/_*.py, HANDOFF-*.md
git log --oneline -12                        # HEAD fea55e3 == origin/main; this session = 21a50d7..fea55e3
ts=$(date +%s)
curl -fsS "https://builtbyjoshstudio.com/?x=$ts" | grep -c 'Eight free browser'       # 1 (8th free tool listed)
curl -fsS "https://builtbyjoshstudio.com/?x=$ts" | grep -c 'Bricolage Grotesque'      # >0 (Kinetic live)
curl -sS -o /dev/null -w "%{http_code}\n" "https://tools.builtbyjoshstudio.com/cost-per-serving-calculator/?x=$ts"   # 200 (new tool live)
gh run list --workflow=pages-build-deployment --limit 3                               # latest completed/success
```
Then take direction from Josh. The card system is fully Kinetic-unified across the site (homepage, collections + hubs, products + hub, blog, fiction) and the 8th free tool is integrated. Nothing mid-flight.

---

# 🟢 builtbyjoshstudio.com — Session Handoff (2026-06-05) — Kinetic re-theme is LIVE + design unified

**This block is a PRIOR shipped state (superseded by the 2026-06-07 block above for STATE/first-steps; kept for its KINETIC quick-ref + history). The dated handoff below it (2026-06-04) is the prior shipped state — its STANDING INSTRUCTIONS (sections #1–#21) still apply verbatim. Ignore that block's stale "Status / First steps / Open items" — they predate the Kinetic flip.**

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
