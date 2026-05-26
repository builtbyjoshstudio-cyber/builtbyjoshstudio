// js/ls-checkout-btn.js
// Click handler for the new LS-direct .ls-checkout-btn pattern used on the
// Collection pages (sign/realms/landscapes/chinese-signs bundles).
//
// Wires up a delegated click listener: on click of a non-disabled button with
// data-checkout-url set, opens the Lemon Squeezy overlay via lemon.js. The
// SDK is loaded lazily on first click so pages that never trigger checkout
// don't pay the network cost.
//
// This file is intentionally separate from js/checkout.js (which uses a
// key-based data-checkout attribute for the existing Tynkr products) per the
// site standing instruction — do not collapse the two.
(function () {
  'use strict';

  var LS_SDK_URL = 'https://assets.lemonsqueezy.com/lemon.js';
  var sdkLoading = false;
  var sdkReady = false;

  function isSdkAvailable() {
    return !!(window.LemonSqueezy && window.LemonSqueezy.Url && typeof window.LemonSqueezy.Url.Open === 'function');
  }

  function initLSIfNeeded() {
    // The lemon.js SDK exposes window.createLemonSqueezy() which sets up the
    // global window.LemonSqueezy object. Call it once after load.
    if (!isSdkAvailable() && typeof window.createLemonSqueezy === 'function') {
      try { window.createLemonSqueezy(); } catch (e) {}
    }
  }

  function loadLSSDK(then) {
    if (isSdkAvailable()) { then(); return; }
    if (sdkLoading) {
      // Another click is already loading — poll until ready (capped).
      var tries = 0;
      var iv = setInterval(function () {
        tries++;
        if (isSdkAvailable() || tries > 50) {
          clearInterval(iv);
          then();
        }
      }, 80);
      return;
    }
    sdkLoading = true;
    var s = document.createElement('script');
    s.src = LS_SDK_URL;
    s.async = true;
    s.onload = function () {
      initLSIfNeeded();
      sdkReady = true;
      then();
    };
    s.onerror = function () {
      // Loading failed — fall through to the navigation fallback in openCheckout.
      sdkLoading = false;
      then();
    };
    document.head.appendChild(s);
  }

  function openCheckout(url) {
    loadLSSDK(function () {
      initLSIfNeeded();
      if (isSdkAvailable()) {
        try {
          window.LemonSqueezy.Url.Open(url);
          return;
        } catch (e) {
          // Fall through to navigation fallback
        }
      }
      // Fallback: open in a new tab so the user still completes checkout.
      window.open(url, '_blank', 'noopener');
    });
  }

  document.addEventListener('click', function (e) {
    var btn = e.target.closest('.ls-checkout-btn');
    if (!btn) return;
    if (btn.disabled) return;
    var url = btn.getAttribute('data-checkout-url');
    if (!url) return;
    e.preventDefault();
    openCheckout(url);
    // GA4 events (best-effort, non-blocking). Standard add_to_cart event fires
    // first so the funnel order in GA4 reads naturally; the custom
    // ls_checkout_open then fires as complementary granular tracking. Both
    // wrapped in independent try/catch so a failure in one never blocks the
    // other.
    if (typeof gtag === 'function') {
      try {
        var price = parseFloat(btn.getAttribute('data-product-price') || '0');
        var slug = window.location.pathname.split('/').pop().replace('.html', '');
        gtag('event', 'add_to_cart', {
          currency: 'USD',
          value: price,
          items: [{
            item_id: slug,
            item_name: btn.getAttribute('data-product-name') || 'unknown',
            item_category: btn.getAttribute('data-item-category') || 'unknown',
            price: price,
            quantity: 1
          }]
        });
      } catch (e) {}
      try {
        gtag('event', 'ls_checkout_open', {
          product_name: btn.getAttribute('data-product-name') || 'unknown',
          product_price: btn.getAttribute('data-product-price') || 'unknown',
          source_page: window.location.pathname
        });
      } catch (e) {}
    }
  });
})();
