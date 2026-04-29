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
 * Deploying these URLs to main flips every buy button on the site to native overlay
 * checkout simultaneously. lemon.js is auto-loaded by /js/checkout.js when any LS URL
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
    ls: "https://tynkrtoolsco.lemonsqueezy.com/checkout/buy/bce39a70-63d8-48d6-a239-bc681b6792d4",
    etsy: "https://www.etsy.com/listing/4482518408/budget-template-workbook-bundle-excel"
  },

  "home-buying-bundle": {
    name: "Home Buying & Mortgage Workbook — Excel + Google Sheets Bundle",
    price: 34.99,
    ls: "https://tynkrtoolsco.lemonsqueezy.com/checkout/buy/99ab4dc9-9195-41cb-826e-4981359b5959",
    etsy: "https://www.etsy.com/listing/4485295506/home-buying-mortgage-workbook-bundle"
  },

  "creator-business-os": {
    name: "Creator Business OS",
    price: 27,
    ls: "https://tynkrtoolsco.lemonsqueezy.com/checkout/buy/c7e0a41d-e208-4d25-aa1f-e233ed2c97fc",
    etsy: "https://www.etsy.com/listing/4480399869/creator-business-os-notion-crm-template"
  },

  "creator-content-os": {
    name: "Creator Content OS",
    price: 27,
    ls: "https://tynkrtoolsco.lemonsqueezy.com/checkout/buy/92422468-0ad9-4717-9170-c469dc55c467",
    etsy: "https://www.etsy.com/listing/4480397323/creator-content-os-notion-management"
  },

  "creator-finance-os": {
    name: "Creator Finance OS",
    price: 27,
    ls: "https://tynkrtoolsco.lemonsqueezy.com/checkout/buy/eed4bb22-0bfd-46a6-8903-9bde3a3a865b",
    etsy: "https://www.etsy.com/listing/4480393057/notion-finance-template-creator-budget"
  },

  "creator-launch-os": {
    name: "Creator Launch OS",
    price: 27,
    ls: "https://tynkrtoolsco.lemonsqueezy.com/checkout/buy/aa63332c-03e4-4cef-9ecd-c70d85cd2508",
    etsy: "https://www.etsy.com/listing/4480408446/creator-launch-os-notion-template-o"
  },

  "creator-product-os": {
    name: "Creator Product OS",
    price: 27,
    ls: "https://tynkrtoolsco.lemonsqueezy.com/checkout/buy/9f7ab2b9-c8d4-4c25-842c-4cf517fba94b",
    etsy: "https://www.etsy.com/listing/4480423266/creator-product-os-notion-template-o"
  },

  "creator-os-full-stack": {
    name: "Creator OS Full Stack Bundle",
    price: 77,
    ls: "https://tynkrtoolsco.lemonsqueezy.com/checkout/buy/86efef37-2592-4285-93ef-7f766ce036c8",
    etsy: "https://www.etsy.com/listing/4480755182/creator-os-notion-template-bundle"
  },

  // ============================================================
  // LITE PRODUCTS (8) — $0 email-gated lead magnets via LS
  // ============================================================

  "ultimate-budget-lite": {
    name: "Ultimate Budget Workbook — Free Lite Version",
    price: 0,
    ls: "https://tynkrtoolsco.lemonsqueezy.com/checkout/buy/502d0998-c22a-474e-a9ff-00b2fd34c213"
  },

  "home-buying-lite": {
    name: "Home Buying & Mortgage Workbook — Free Lite Version",
    price: 0,
    ls: "https://tynkrtoolsco.lemonsqueezy.com/checkout/buy/5dd13171-4078-4784-9367-602736b80687"
  },

  "creator-business-os-lite": {
    name: "Creator Business OS — Free Lite Version",
    price: 0,
    ls: "https://tynkrtoolsco.lemonsqueezy.com/checkout/buy/d40e11ca-790f-4fc9-bd5e-48c19754c76c"
  },

  "creator-content-os-lite": {
    name: "Creator Content OS — Free Lite Version",
    price: 0,
    ls: "https://tynkrtoolsco.lemonsqueezy.com/checkout/buy/86ce1e9d-08a6-47d8-922a-d92d51086f35"
  },

  "creator-finance-os-lite": {
    name: "Creator Finance OS — Free Lite Version",
    price: 0,
    ls: "https://tynkrtoolsco.lemonsqueezy.com/checkout/buy/ccd676b6-cbe8-4f46-bfaf-0c224f3cc1a0"
  },

  "creator-launch-os-lite": {
    name: "Creator Launch OS — Free Lite Version",
    price: 0,
    ls: "https://tynkrtoolsco.lemonsqueezy.com/checkout/buy/ea059392-d50f-4d5e-912b-1d782ec0cdae"
  },

  "creator-product-os-lite": {
    name: "Creator Product OS — Free Lite Version",
    price: 0,
    ls: "https://tynkrtoolsco.lemonsqueezy.com/checkout/buy/fd1c1fa9-4dd6-4339-b694-3116a1585e49"
  },

  "creator-os-full-stack-lite": {
    name: "Creator OS Full Stack — Free Lite Sampler",
    price: 0,
    ls: "https://tynkrtoolsco.lemonsqueezy.com/checkout/buy/50713069-e8be-4947-aff6-0dc129106fb8"
  }

};
