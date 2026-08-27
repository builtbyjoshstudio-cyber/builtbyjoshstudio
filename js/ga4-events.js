// GA4 event listeners for builtbyjoshstudio.com
// Loaded as a separate shared block; does not modify the existing gtag init snippet.

(function () {
  'use strict';

  // -- Helpers ----------------------------------------------------------------

  function pageSlug() {
    var path = window.location.pathname || '';
    var name = path.split('/').pop() || '';
    return name.replace('.html', '') || 'unknown';
  }

  // Slug → item_category mapping. Mirrors the per-page inline view_item
  // <script> blocks that Phase 3/4 add. Used as a fallback when a checkout
  // button doesn't carry data-item-category and as the canonical source of
  // truth for the LS handler (which fires off-page from the inline script).
  // The CS hub (chinese-zodiac-art) clusters with the 12 per-animal Chinese
  // zodiac pages for reporting purposes, so it maps to 'Chinese Zodiac Art
  // Bundle' alongside them.
  function slugToCategory(slug) {
    if (!slug) return 'Unknown';
    // Tynkr Notion templates
    if (slug === 'creator-os-full-stack') return 'Notion Template';
    if (/^creator-.+-os$/.test(slug)) return 'Notion Template';
    // Tynkr spreadsheets
    if (slug === 'ultimate-budget-workbook' || slug === 'home-buying-mortgage-workbook') return 'Spreadsheet';
    // Western zodiac art (12 per-sign pages)
    if (/^(aries|taurus|gemini|cancer|leo|virgo|libra|scorpio|sagittarius|capricorn|aquarius|pisces)-zodiac-art$/.test(slug)) return 'Zodiac Art Bundle';
    if (slug === 'chinese-zodiac-art') return 'Chinese Zodiac Art Bundle';
    // Western zodiac realms (12 per-sign pages)
    if (/^(aries|taurus|gemini|cancer|leo|virgo|libra|scorpio|sagittarius|capricorn|aquarius|pisces)-zodiac-realms$/.test(slug)) return 'Zodiac Realm Bundle';
    // Chinese zodiac art (12 per-animal pages)
    if (/^(rat|ox|tiger|rabbit|dragon|snake|horse|goat|monkey|rooster|dog|pig)-chinese-zodiac-art$/.test(slug)) return 'Chinese Zodiac Art Bundle';
    // Chinese realms single bundle
    if (slug === 'chinese-zodiac-realms') return 'Chinese Zodiac Realm Bundle';
    // Western landscapes single bundle
    if (slug === 'zodiac-landscapes') return 'Zodiac Landscape Bundle';
    return 'Unknown';
  }

  function slugify(name) {
    if (!name) return 'unknown';
    return String(name)
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-+|-+$/g, '') || 'unknown';
  }

  // Pull primary product context from the page's checkout button. Used by the
  // LS handler to fill in item_id / item_name / item_category / value when the
  // LS event payload doesn't already carry them.
  function readPageContext() {
    var slug = pageSlug();
    var fallbackCategory = slugToCategory(slug);

    // Collection pages (LS-direct overlay): .ls-checkout-btn with data-* attrs.
    var lsBtn = document.querySelector('.ls-checkout-btn');
    if (lsBtn) {
      return {
        item_id: lsBtn.getAttribute('data-item-id') || slug,
        item_name: lsBtn.getAttribute('data-product-name') || 'unknown',
        item_category: lsBtn.getAttribute('data-item-category') || fallbackCategory,
        value: parseFloat(lsBtn.getAttribute('data-product-price') || '0') || 0
      };
    }

    // Tynkr product pages: [data-checkout] keyed into window.CHECKOUT_CONFIG.
    var dcBtn = document.querySelector('[data-checkout]');
    if (dcBtn) {
      var key = dcBtn.getAttribute('data-checkout');
      var config = window.CHECKOUT_CONFIG && window.CHECKOUT_CONFIG[key];
      if (config) {
        return {
          item_id: slug,
          item_name: config.name || 'unknown',
          item_category: config.category || fallbackCategory,
          value: parseFloat(config.price || '0') || 0
        };
      }
    }

    return {
      item_id: slug,
      item_name: 'unknown',
      item_category: fallbackCategory,
      value: 0
    };
  }

  // -- 1. Etsy outbound clicks ------------------------------------------------
  document.addEventListener('click', function (e) {
    const link = e.target.closest('a');
    if (!link || !link.href) return;
    if (link.href.indexOf('etsy.com') === -1) return;
    if (typeof gtag === 'function') {
      gtag('event', 'etsy_click', {
        link_url: link.href,
        link_domain: 'etsy.com',
        link_text: (link.innerText || '').trim().substring(0, 100),
        outbound: true,
        transport_type: 'beacon'
      });
    }
  });

  // -- 1b. Redbubble outbound clicks (same pattern; RB's own GA hookup is dead
  //        Universal Analytics, so our side of the funnel is the measurable side)
  document.addEventListener('click', function (e) {
    const link = e.target.closest('a');
    if (!link || !link.href) return;
    if (link.href.indexOf('redbubble.com') === -1) return;
    if (typeof gtag === 'function') {
      gtag('event', 'redbubble_click', {
        link_url: link.href,
        link_domain: 'redbubble.com',
        link_text: (link.innerText || '').trim().substring(0, 100),
        outbound: true,
        transport_type: 'beacon'
      });
    }
  });

  // -- 2 + 3. Lemon Squeezy: begin_checkout + purchase -----------------------
  // LS uses the documented LemonSqueezy.Setup({ eventHandler }) callback API
  // (NOT a DOM event). __ga4SetupLemonSqueezy() below polls until the lemon.js
  // SDK is loaded, then wires this handler. Payload shape:
  //   { event: 'Checkout.Success', data: {...} }
  //
  // Mapping (replaces the prior custom lemonsqueezy_* names with the standard
  // GA4 e-commerce event names so the Monetization / Revenue reports populate):
  //   Checkout.ViewCart  -> begin_checkout
  //   Checkout.Success   -> purchase
  //
  // Documented LS events not currently mapped: GA.ViewCart, PaymentMethodUpdate.*
  window.__ga4LemonSqueezyHandler = function (event) {
    if (!event || typeof gtag !== 'function') return;

    if (event.event === 'Checkout.ViewCart') {
      var ctx = readPageContext();
      gtag('event', 'begin_checkout', {
        currency: 'USD',
        value: ctx.value,
        items: [{
          item_id: ctx.item_id,
          item_name: ctx.item_name,
          item_category: ctx.item_category,
          price: ctx.value,
          quantity: 1
        }]
      });
      return;
    }

    if (event.event === 'Checkout.Success') {
      var attrs = (event.data && event.data.order && event.data.order.data && event.data.order.data.attributes) || {};
      var firstItem = attrs.first_order_item || {};
      var pageCtx = readPageContext();
      var lsName = firstItem.product_name || pageCtx.item_name;
      var lsValue = typeof attrs.total_usd === 'number' ? attrs.total_usd : pageCtx.value;
      var txnId = attrs.identifier || attrs.order_number || ('order-' + Date.now());
      // Prefer the page slug for item_id (matches view_item / begin_checkout);
      // fall back to slugifying the LS product name if no page context exists.
      var itemId = pageCtx.item_id || slugify(lsName);
      gtag('event', 'purchase', {
        transaction_id: String(txnId),
        currency: 'USD',
        value: lsValue || 0,
        items: [{
          item_id: itemId,
          item_name: lsName,
          item_category: pageCtx.item_category,
          price: lsValue || 0,
          quantity: 1
        }]
      });
    }
  };

  // -- LS Setup callback wiring ----------------------------------------------
  // Polls until lemon.js exposes window.LemonSqueezy.Setup, then wires the
  // handler. Runs on every page that loads ga4-events.js (i.e. all 91 HTML
  // pages site-wide) — replaces the previous Setup call in js/checkout.js,
  // which only fired on the 8 Tynkr product pages.
  //
  // The guard flag prevents double-wiring if Setup is invoked from multiple
  // paths (e.g., a future js/checkout.js change accidentally re-adds it).
  function __ga4SetupLemonSqueezy() {
    var MAX_TRIES = 25;   // 25 * 200ms = 5s of polling
    var POLL_MS = 200;
    var tries = 0;

    function attempt() {
      if (window.__ga4LemonSqueezySetupDone) return;
      if (window.LemonSqueezy && typeof window.LemonSqueezy.Setup === 'function') {
        try {
          window.LemonSqueezy.Setup({ eventHandler: window.__ga4LemonSqueezyHandler });
          window.__ga4LemonSqueezySetupDone = true;
        } catch (err) {
          console.warn('[ga4-events] LemonSqueezy.Setup() failed:', err);
        }
        return;
      }
      tries++;
      if (tries < MAX_TRIES) {
        setTimeout(attempt, POLL_MS);
      }
    }

    attempt();
  }
  window.__ga4SetupLemonSqueezy = __ga4SetupLemonSqueezy;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', __ga4SetupLemonSqueezy);
  } else {
    __ga4SetupLemonSqueezy();
  }
})();
