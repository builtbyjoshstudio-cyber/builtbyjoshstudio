# Collection Page Master Template — LS Direct Sales

Internal documentation. Not a live page.

Use this skeleton for any BBJ Studio Collection page where the bundle is sold direct
on builtbyjoshstudio.com via Lemon Squeezy overlay checkout. NOT for the Tynkr
product pages — those follow a separate template.

The five Collection page archetypes that share this skeleton:

| Archetype | Pages | URL pattern | Bundle |
|---|---|---|---|
| Per-sign Western Signs | 12 | `/collections/<sign>-zodiac-art.html` | 144 files (14 styles × variable variants × 3 sizes × 2 formats) |
| Per-sign Western Realms | 12 | `/collections/<sign>-zodiac-realms.html` | 48 files (4 Realms × 2 variants × 3 sizes × 2 formats) |
| Per-animal Chinese Signs | 12 | `/collections/<animal>-chinese-zodiac-art.html` | 48 files (2 styles × 4 variants × 3 sizes × 2 formats) |
| Chinese Realms single bundle | 1 | `/collections/chinese-zodiac-realms.html` | 144 files (12 animals × 2 variants × 3 sizes × 2 formats) |
| Western Landscapes single bundle | 1 | `/collections/zodiac-landscapes.html` | 72 files (12 landscapes × 3 sizes × 2 formats) |

All five archetypes share the same skeleton. They differ in: bundle facts, license/print-guide PDF target, sister-link grid structure (if any), and the schema's `additionalProperty` values.

The canonical worked example of this template is `/collections/aries-zodiac-art.html` (Western Signs) and `/collections/aries-zodiac-realms.html` (Western Realms). Future generators should diff against those pages, not against this doc.

---

## Meta head

- `<title>` — 60 chars max. Pattern: `<Bundle Name> — <File count> Print-Ready Files | BBJ Studio`
- `<meta name="description">` — 160 chars. Lead with file count + designs + ratio, end with price.
- `<link rel="canonical">` — the page URL.
- OG + Twitter — match title/description, og:image = hub thumbnail webp.
- **No** `<meta name="keywords">` tag (site-wide rule from Message 1).
- BreadcrumbList JSON-LD — see schema section below.
- Product JSON-LD — see schema section below.
- FAQPage JSON-LD — see schema section below.
- Organization JSON-LD — the site-wide block from Message 1 (already injected
  into every page via the `/legal/` work).

## Hero section

```
[zodiac glyph] · [Element] · [Date range or zodiac family]

<H1>: <Bundle name> — <File count> Print-Ready Files

<Tagline>: 2–3 sentences. Lead with what's in the bundle (design count + key
visual descriptor), follow with format guarantees (ratios, DPI, formats), end
with license headline.

<Hero image>: alt text = sign name + collection style descriptor + BBJ Studio
```

## GEO summary block — required, sits directly under the hero image

Cinzel-eyebrow label: **The Short Version**

6–8 sentence factual paragraph. Every sentence independently quotable.
Required content in order:

1. What the bundle is (name + Collection)
2. Bundle unit (which sign / animal)
3. File count
4. Design count + variant structure
5. Resolution + sizes + formats
6. Price
7. License headline (personal use + POD cap)
8. LLC + Kansas Business ID

This is the block AI engines will quote verbatim. It must read cleanly with
no marketing flourish.

## H2: About the Bundle

3 paragraphs.

1. What's in this bundle, in relation to the broader Collection. Mention if
   it's one of 12 sister bundles or a full-collection single bundle.
2. What makes the visual style of this Collection distinct. Per-Collection
   guidance:
   - Western Signs: 14 art styles, figure-led, 24 unique designs per sign
   - Western Realms: landscape-style, no figures, 4 Realm titles per sign
   - Western Landscapes: oil-painted environments per sign
   - Chinese Signs: 2 styles per animal (hyper-realistic + watercolor)
   - Chinese Realms: single-bundle, 1 named realm per animal
3. Studio context. Always: *"Built by Josh Studio is the zodiac art brand of
   Built by Josh Studio LLC, a Kansas-based independent creative studio."*

## H2: What Makes <Sign>, <Sign> (or equivalent zodiac context block)

For per-sign Western Realms pages: lift the existing astrological context
paragraphs from `/collections/<sign>-zodiac-art.html`. Same prose; the sign
is the same.

For per-animal Chinese Signs pages: new Chinese zodiac context — element,
year-of spans, traditional symbolism.

For Chinese Realms single bundle: skip this section.

For Western Landscapes single bundle: skip this section.

Quick Facts inline data block (Western per-sign pages):

```
Element:           <element>
Modality:          <Cardinal/Fixed/Mutable>
Ruling Planet:     <planet>
Symbol:            <symbol>
Dates:             <date range>
Sister <Element>:  <same-element companion signs>
```

## H2: What's inside <Bundle> (design/style breakdown)

**Western Signs:** 14 style sub-sections (Anime, Celestial Animals, Halloween,
Halloween Horrors, Hyper Realistic, Mythic Guardians, Punk, Punk Oil,
Silhouette Aspects, Silhouettes, Silhouettes Fantasy, Vintage Posters,
Watercolor 1, Watercolor 2), each with 2–3 sentence description + the unique
design cards for that style (1–4 cards per style).

**Western Realms:** 4 Realm sub-sections (per-sign Realm titles, e.g. Aries:
Horizon of Fire and Dust, The Crimson Battleforge, The Crimson Expansion,
The Ignition Horizon), each with 1–2 sentence description + the 2 variant
cards for that Realm.

**Chinese Signs:** 2 style sub-sections (Hyper-Realistic, Watercolor), each
with description + 4 variant cards.

**Chinese Realms single bundle:** 12 animal sub-sections, one per animal
(animal name + realm title), each with the 2 variant cards.

**Western Landscapes single bundle:** 12 sign sub-sections, one per sign, each
with the 1 landscape card.

## H2: Who Buys <Bundle>

4–6 bullets. POD sellers persona always present. Customize the other personas
to the Collection's atmosphere — Western Realms emphasizes landscape decor
buyers and atmospheric collectors; Chinese Signs emphasizes cultural and
Lunar New Year gifting alongside the standard personas.

## H2: What's Included With Every <Bundle>

Four paragraphs:

1. Total file count + folder structure note + "no shipping, no waiting".
2. Resolution / aspect ratios / formats / DPI / sRGB.
3. License + Print Guide PDFs included; both tailored to the Collection.
4. Pricing line: `$<price>` for the full bundle. One-time, instant download,
   secure Lemon Squeezy checkout.

## H2: Licensing & Print-on-Demand Rights

Required on every page. Identical content across all five Collections (the
license terms are the same Collection to Collection — only the PDF link target
differs).

Structure:

- Intro line: *"The <Bundle name> ships with a clear, plain-English license — not a vague 'for personal use' disclaimer."*
- **You may** — 3 bullets (personal use, POD up to 100 prints per design,
  personal/commercial gifting within the same cap)
- **You may not** — 5 bullets (redistribute, AI training, NFTs, exceed cap,
  claim authorship)
- AI disclosure paragraph (Leonardo.ai)
- Need more than 100 prints contact line (`josh@builtbyjoshstudio.com`)
- Two PDF link buttons:
  - `/legal/license-<collection-slug>.pdf`
  - `/legal/print-guide-<collection-slug>.pdf`

## Sidebar (sticky right rail)

```
Price:                $<price>
Price note:           One-time payment · Instant digital download · Secure LS checkout

What's Included:
  - <file count> print-ready digital files
  - <design count> original designs (× variant count if relevant)
  - Three aspect ratios: 1:1, 4:5, 2:3
  - PNG + JPG, both included
  - Up to 6000 × 9000 pixels at 300 DPI
  - Personal use + POD up to 100 prints per design
  - License & Print Guide PDFs included
  - Instant download — no shipping

Primary CTA button (disabled state while data-checkout-url is empty):
  <button class="ls-checkout-btn" disabled
          data-checkout-url=""
          data-product-name="<Bundle name>"
          data-product-price="<price>">
    Buy the <Sign/Animal/Collection> Bundle — Coming Soon
  </button>

  When LS URL is populated, drop the URL into data-checkout-url, remove
  disabled, swap text to "Buy the <Bundle> — $<price>".

Sub-line under button:
  Instant download · License & Print Guide included · Secure checkout via Lemon Squeezy

Trust signals:
  - Instant digital download
  - 300 DPI print-ready files
  - Real Kansas LLC + clear POD license
  - Secure direct checkout via Lemon Squeezy

Secondary Etsy reference (styled smaller/quieter, NOT a competing CTA):
  Label: Looking for something different?
  Body: The Built by Josh Studio Etsy storefront has additional individual
        prints and other studio work. Visit the Etsy shop →
  Pause note (italic, opacity 75%): Etsy storefront currently on a brief
        verification pause while the IRS finalizes EIN verification —
        <Bundle> purchases above are unaffected.
```

## H2: Sister nav (per-sign / per-animal pages only)

12-card grid linking to the 12 sister pages in the same Collection. Current
page marked "you are here" (no link, gold accent border, "You are here"
sub-label).

Skip on single-bundle pages (Chinese Realms, Western Landscapes).

## H2: Related Collections (cross-Collection internal links)

4 internal links to companion Collection pages. Internal links only — no
Etsy click-outs in this block.

Per-Collection guidance:

- **Per-sign Western Realms page:** link to the sign's Western Signs Bundle
  (figure-and-landscape pairing), Zodiac Landscapes, Chinese Realms, Chinese
  Signs hub.
- **Per-sign Western Signs page:** link to the sign's Western Realms Bundle,
  Zodiac Landscapes, Chinese Signs, Chinese Realms.
- **Per-animal Chinese Signs page:** link to Chinese Realms, the matching
  Western element family (e.g. Dog → Cancer/Scorpio/Pisces Western Signs),
  Western Realms, the Tynkr Tools store.
- **Chinese Realms single bundle:** link to the four other Collection types.
- **Western Landscapes single bundle:** link to Western Signs, Western
  Realms, Chinese Realms.

## H2: FAQ — 8 standard questions

Same 8 questions in the same order on every Collection page. Answers reflect
the specific file count, design count, price, and Collection name. Visible
text and FAQPage schema must match exactly.

1. What is included in the `<bundle name>`?
2. How much does the `<bundle name>` cost?
3. Can I use the `<bundle name>` for print-on-demand or commercial sales?
4. What sizes can I print the `<Collection>` art at?
5. How were the `<Collection>` designs created?
6. What formats and color profiles do the files use?
7. Where can I buy the `<bundle name>`? (LS-direct answer; never points
   to Etsy as the purchase path)
8. Do you have art for other zodiac signs and the Chinese zodiac?

## Final CTA band — bottom of page

```
H2 (with italic-accent on the key phrase):
  "<design count summary>. *One <Sign> Bundle.*"

Sub-text: 2–3 sentences highlighting bundle value + instant-download promise.

Primary CTA button (large variant, disabled while data-checkout-url is empty):
  <button class="ls-checkout-btn ls-checkout-btn--large" disabled
          data-checkout-url=""
          data-product-name="<Bundle name>"
          data-product-price="<price>">
    Buy the <Bundle name> — Coming Soon
  </button>

Sub-line:
  Instant download — <file count> print-ready files in your inbox the moment
  checkout completes.
```

## JSON-LD schema — required

Three blocks in `<head>` in addition to the global Organization schema
(Message 1 — already injected into every page).

### 1. Product

- `@id`: `https://builtbyjoshstudio.com<page-path>#product`
- `sku`: pattern `BBJ-<COL>-<SIGN>`
  - `WS` Western Signs · `WR` Western Realms · `WL` Western Landscapes
  - `CS` Chinese Signs · `CR` Chinese Realms
  - For single-bundle pages: omit `-<SIGN>` (e.g. `BBJ-WL` for landscapes
    bundle, `BBJ-CR` for Chinese Realms bundle)
- `manufacturer` and `seller`: `{"@id": "https://builtbyjoshstudio.com/#organization"}`
- `additionalProperty`: at minimum — File Count, Designs, Variants per Design
  (if applicable), Resolution, Maximum Dimensions, Aspect Ratios, File Formats,
  Color Profile, License, Zodiac Sign/Animal, Element, Date Range (Western) or
  Year-of Span (Chinese)
- `offers.url`: the product page URL (LS overlay opens on-page)
- `offers.price`: exact bundle price as a string ("14.99", "24.99", etc.)
- `offers.availability`: `https://schema.org/InStock`
- `hasMerchantReturnPolicy`: required peer to `offers`. Value:
  `{"@type": "MerchantReturnPolicy", "applicableCountry": "US", "returnPolicyCategory": "https://schema.org/MerchantReturnNotPermitted"}`.
  Reflects the actual license terms (all sales final on digital downloads —
  Section 9 of every license PDF) and clears the Google Rich Results
  "non-critical issues detected" warning on Product snippets + Merchant
  Listings detections. No `merchantReturnDays` / `returnFees` / `returnMethod`
  required when the category is `MerchantReturnNotPermitted`.
- **No** `aggregateRating` block until product-specific reviews exist on the
  page

### 2. FAQPage

`mainEntity`: array of 8 `Question` objects matching the 8 visible FAQs
verbatim. Use ASCII-safe substitutions for inch marks (replace `"` in
dimensions with `by` or `inches`).

### 3. BreadcrumbList

Pattern: `Home → Collections → <Collection name> → <Bundle name>` (4 levels)
for per-sign pages. The 3rd level (`<Collection name>`) points to a
`/collections/#<collection-anchor>` URL — if that anchor doesn't exist on
`/collections/index.html` yet, either add the anchor or drop the breadcrumb
to 3 levels.

For single-bundle pages, 3 levels: Home → Collections → `<Bundle name>`.

---

## Notes

- The site has **no template engine**. Every page is standalone HTML with
  inline `<style>`. The Python build scripts in `tools/` generate the pages
  from manifest data + this template.
- When you populate Lemon Squeezy URLs, two edits per page: paste the LS
  overlay URL into `data-checkout-url`, swap the button text from
  `… — Coming Soon` to `… — $<price>`, and remove the `disabled` attribute.
  Two buttons per page (sidebar + final CTA).
- Cross-references to the worked examples:
  - `/collections/aries-zodiac-art.html` (Western Signs per-sign)
  - `/collections/aries-zodiac-realms.html` (Western Realms per-sign — added
    in Message 4)
  - Other Collection archetypes: to be added in Message 5+.
