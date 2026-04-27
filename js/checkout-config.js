/**
 * Tynkr Tools & Co — Checkout Configuration
 * ==========================================
 * Single source of truth for all product checkout URLs across the site.
 *
 * HOW THIS WORKS
 * --------------
 * Every buy button on the site uses `data-checkout="<key>"` instead of a hardcoded href.
 * /js/checkout.js reads that attribute, looks up this config, and wires the button:
 *   - If `ls` is a real URL  -> opens Lemon Squeezy overlay checkout on this domain
 *   - If `ls` is "PENDING" and `etsy` exists  -> falls back to Etsy listing (paid items only)
 *   - If `ls` is "PENDING" and no `etsy`      -> hides the button (lite items, not yet released)
 *
 * LEMON SQUEEZY SETUP
 * -------------------
 * LS store URL:    https://tynkrtoolsco.lemonsqueezy.com/
 * Buy URL format:  https://tynkrtoolsco.lemonsqueezy.com/checkout/buy/<product-uuid>
 * Upgrade code:    UPGRADE35  (set up matching codes on LS AND Etsy so lite users
 *                  can redeem on either platform per the in-file upgrade prompt)
 * Lite pricing:    $0 lead magnet — LS captures email, delivers file, builds list
 *
 * When the LS store goes live, deploying these URLs from the ls-go-live branch
 * to main flips every buy button on the site to native overlay checkout
 * simultaneously. lemon.js is auto-loaded by /js/checkout.js when any LS URL
 * is detected, so no further code changes are required.
 *
 * NEVER hardcode a checkout URL outside this file. Every change goes through here.
 */

window.CHECKOUT_CONFIG = {

  // ============================================================
  // PAID PRODUCTS (8) — wired to Lemon Squeezy overlay checkout
  // ============================================================

  "ultimate-budget-bundle": {
    name: "Ultimate Budget Workbook — Excel + Google Sheets Bundle",
    price: 34.99,
    ls: "https://tynkrtoolsco.lemonsqueezy.com/checkout/buy/2b78fa15-d8b5-4697-a610-6e1bb9992715",
    etsy: "https://www.etsy.com/listing/4482518408/budget-template-workbook-bundle-excel"
  },

  "home-buying-bundle": {
    name: "Home Buying & Mortgage Workbook — Excel + Google Sheets Bundle",
    price: 34.99,
    ls: "https://tynkrtoolsco.lemonsqueezy.com/checkout/buy/afba6776-10ab-4b1d-8206-593d8f45240d",
    etsy: "https://www.etsy.com/listing/4485295506/home-buying-mortgage-workbook-bundle"
  },

  "creator-business-os": {
    name: "Creator Business OS",
    price: 27,
    ls: "https://tynkrtoolsco.lemonsqueezy.com/checkout/buy/1b20037b-5fdb-4939-9ebd-4347439113bd",
    etsy: "https://www.etsy.com/listing/4480399869/creator-business-os-notion-crm-template"
  },

  "creator-content-os": {
    name: "Creator Content OS",
    price: 27,
    ls: "https://tynkrtoolsco.lemonsqueezy.com/checkout/buy/2704ae67-f6e8-4c5d-8ab7-343e4e597e00",
    etsy: "https://www.etsy.com/listing/4480397323/creator-content-os-notion-management"
  },

  "creator-finance-os": {
    name: "Creator Finance OS",
    price: 27,
    ls: "https://tynkrtoolsco.lemonsqueezy.com/checkout/buy/65ab7d87-10d8-4716-bd74-3c39395e07f6",
    etsy: "https://www.etsy.com/listing/4480393057/notion-finance-template-creator-budget"
  },

  "creator-launch-os": {
    name: "Creator Launch OS",
    price: 27,
    ls: "https://tynkrtoolsco.lemonsqueezy.com/checkout/buy/20837a26-66b5-40cc-80f5-8dab282ee643",
    etsy: "https://www.etsy.com/listing/4480408446/creator-launch-os-notion-template-o"
  },

  "creator-product-os": {
    name: "Creator Product OS",
    price: 27,
    ls: "https://tynkrtoolsco.lemonsqueezy.com/checkout/buy/1d804a2b-61d2-4c99-88bf-2164fa2aa515",
    etsy: "https://www.etsy.com/listing/4480423266/creator-product-os-notion-template-o"
  },

  "creator-os-full-stack": {
    name: "Creator OS Full Stack Bundle",
    price: 77,
    ls: "https://tynkrtoolsco.lemonsqueezy.com/checkout/buy/2b2d7fb7-9a4a-467b-900f-2a8b20a76582",
    etsy: "https://www.etsy.com/listing/4480755182/creator-os-notion-template-bundle"
  },

  // ============================================================
  // LITE PRODUCTS (8) — $0 email-gated lead magnets via LS
  // ============================================================

  "ultimate-budget-lite": {
    name: "Ultimate Budget Workbook — Free Lite Version",
    price: 0,
    ls: "https://tynkrtoolsco.lemonsqueezy.com/checkout/buy/d281c623-1319-4219-a764-f819ef0e6064"
  },

  "home-buying-lite": {
    name: "Home Buying & Mortgage Workbook — Free Lite Version",
    price: 0,
    ls: "https://tynkrtoolsco.lemonsqueezy.com/checkout/buy/ff8fa47a-eaea-4452-a760-377c2caa017a"
  },

  "creator-business-os-lite": {
    name: "Creator Business OS — Free Lite Version",
    price: 0,
    ls: "https://tynkrtoolsco.lemonsqueezy.com/checkout/buy/367d07c0-d52f-439f-b896-254f502ebdde"
  },

  "creator-content-os-lite": {
    name: "Creator Content OS — Free Lite Version",
    price: 0,
    ls: "https://tynkrtoolsco.lemonsqueezy.com/checkout/buy/815250a3-7eae-4c0c-8299-3ca0e211c34c"
  },

  "creator-finance-os-lite": {
    name: "Creator Finance OS — Free Lite Version",
    price: 0,
    ls: "https://tynkrtoolsco.lemonsqueezy.com/checkout/buy/e5d59e33-53f6-4c73-add6-5a82c68706d4"
  },

  "creator-launch-os-lite": {
    name: "Creator Launch OS — Free Lite Version",
    price: 0,
    ls: "https://tynkrtoolsco.lemonsqueezy.com/checkout/buy/cc436629-0bc1-4f3e-afae-5fa39de1a8d4"
  },

  "creator-product-os-lite": {
    name: "Creator Product OS — Free Lite Version",
    price: 0,
    ls: "https://tynkrtoolsco.lemonsqueezy.com/checkout/buy/9f2b569b-6b3a-4a6d-b07f-64b9bb5eeb80"
  },

  "creator-os-full-stack-lite": {
    name: "Creator OS Full Stack — Free Lite Sampler",
    price: 0,
    ls: "https://tynkrtoolsco.lemonsqueezy.com/checkout/buy/455d09ff-dcfa-4de3-ab36-f06705c024ac"
  }

};
