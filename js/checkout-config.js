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
 * GOING LIVE WITH LEMON SQUEEZY
 * -----------------------------
 * When LS account verification completes:
 *   1) Replace every "PENDING" with the corresponding LS overlay URL.
 *      Format: https://[storename].lemonsqueezy.com/buy/[product-uuid]
 *   2) Commit + deploy this file. No HTML changes required.
 *   3) Every buy button on the site flips to LS overlay simultaneously.
 *   4) Update Product schema offers.url on the 8 product pages (separate task).
 *   5) Submit the Merchant Center reconsideration request.
 *
 * NEVER hardcode a checkout URL outside this file. Every change goes through here.
 */

window.CHECKOUT_CONFIG = {

  // ============================================================
  // PAID PRODUCTS (8) — currently fall back to Etsy while PENDING
  // ============================================================

  "ultimate-budget-bundle": {
    name: "Ultimate Budget Workbook — Excel + Google Sheets Bundle",
    price: 34.99,
    ls: "PENDING",
    etsy: "https://www.etsy.com/listing/4482518408/budget-template-workbook-bundle-excel"
  },

  "home-buying-bundle": {
    name: "Home Buying & Mortgage Workbook — Excel + Google Sheets Bundle",
    price: 34.99,
    ls: "PENDING",
    etsy: "https://www.etsy.com/listing/4485295506/home-buying-mortgage-workbook-bundle"
  },

  "creator-business-os": {
    name: "Creator Business OS",
    price: 27,
    ls: "PENDING",
    etsy: "https://www.etsy.com/listing/4480399869/creator-business-os-notion-crm-template"
  },

  "creator-content-os": {
    name: "Creator Content OS",
    price: 27,
    ls: "PENDING",
    etsy: "https://www.etsy.com/listing/4480397323/creator-content-os-notion-management"
  },

  "creator-finance-os": {
    name: "Creator Finance OS",
    price: 27,
    ls: "PENDING",
    etsy: "https://www.etsy.com/listing/4480393057/notion-finance-template-creator-budget"
  },

  "creator-launch-os": {
    name: "Creator Launch OS",
    price: 27,
    ls: "PENDING",
    etsy: "https://www.etsy.com/listing/4480408446/creator-launch-os-notion-template-o"
  },

  "creator-product-os": {
    name: "Creator Product OS",
    price: 27,
    ls: "PENDING",
    etsy: "https://www.etsy.com/listing/4480423266/creator-product-os-notion-template-o"
  },

  "creator-os-full-stack": {
    name: "Creator OS Full Stack Bundle",
    price: 77,
    ls: "PENDING",
    etsy: "https://www.etsy.com/listing/4480755182/creator-os-notion-template-bundle"
  },

  // ============================================================
  // LITE PRODUCTS (8) — free with email, hidden until LS goes live
  // No Etsy fallback because these are new and only exist via LS
  // ============================================================

  "ultimate-budget-lite": {
    name: "Ultimate Budget Workbook — Free Lite Version",
    price: 0,
    ls: "PENDING"
  },

  "home-buying-lite": {
    name: "Home Buying & Mortgage Workbook — Free Lite Version",
    price: 0,
    ls: "PENDING"
  },

  "creator-business-os-lite": {
    name: "Creator Business OS — Free Lite Version",
    price: 0,
    ls: "PENDING"
  },

  "creator-content-os-lite": {
    name: "Creator Content OS — Free Lite Version",
    price: 0,
    ls: "PENDING"
  },

  "creator-finance-os-lite": {
    name: "Creator Finance OS — Free Lite Version",
    price: 0,
    ls: "PENDING"
  },

  "creator-launch-os-lite": {
    name: "Creator Launch OS — Free Lite Version",
    price: 0,
    ls: "PENDING"
  },

  "creator-product-os-lite": {
    name: "Creator Product OS — Free Lite Version",
    price: 0,
    ls: "PENDING"
  },

  "creator-os-full-stack-lite": {
    name: "Creator OS Full Stack — Free Lite Sampler",
    price: 0,
    ls: "PENDING"
  }

};
