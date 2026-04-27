/**
 * Tynkr Tools & Co — Checkout Wiring
 * ===================================
 * Reads window.CHECKOUT_CONFIG and wires every [data-checkout] element on the page.
 *
 * MARKUP CONTRACT
 * ---------------
 * <a data-checkout="ultimate-budget-bundle"
 *    href="https://www.etsy.com/listing/4482518408/..."  <-- Etsy fallback baked in
 *    target="_blank"
 *    rel="noopener">
 *   ...content...
 *   <span data-cta-label>Get the Bundle on Etsy ↗</span>  <-- optional dynamic label slot
 * </a>
 *
 * Optional override attributes on the element:
 *   data-cta-label-live    — label text to use when LS is live (defaults: "Buy Now")
 *
 * Optional parent wrapper:
 *   <section data-lite-section>...</section>
 *   Hides the whole section if all child [data-checkout] elements are hidden lite items.
 *
 * STATE LOGIC
 * -----------
 *   LIVE:         config.ls is a real URL  -> overlay checkout via lemon.js, on this domain
 *   PENDING-PAID: config.ls === "PENDING" AND config.etsy exists  -> leave HTML href alone
 *   PENDING-LITE: config.ls === "PENDING" AND no config.etsy      -> hide the element
 *
 * Pages without JS still work for paid items because the Etsy fallback is in static HTML.
 * Lite buttons are hidden by default in CSS to prevent flash-of-unavailable-button (FOUC).
 */

(function () {
  "use strict";

  function init() {
    var config = window.CHECKOUT_CONFIG;
    if (!config) {
      console.warn("[checkout] CHECKOUT_CONFIG not loaded — buy buttons will use static HTML hrefs only");
      // Still need to reveal lite-pending buttons that turned out not to need hiding
      return;
    }

    var elements = document.querySelectorAll("[data-checkout]");
    var needsLemonScript = false;

    elements.forEach(function (el) {
      var key = el.getAttribute("data-checkout");
      var product = config[key];

      if (!product) {
        console.warn('[checkout] No config entry for key="' + key + '"');
        hideElement(el);
        return;
      }

      var lsLive = product.ls && product.ls !== "PENDING";
      var hasEtsy = !!product.etsy;

      if (lsLive) {
        wireLemonSqueezy(el, product);
        needsLemonScript = true;
      } else if (hasEtsy) {
        // PENDING-paid: HTML href is already the Etsy URL, just confirm & reveal
        revealElement(el);
      } else {
        // PENDING-lite: hide the button (and its [data-lite-section] ancestor if any)
        hideElement(el);
      }
    });

    if (needsLemonScript) {
      loadLemonScript();
    }

    manageLiteSections();
  }

  function wireLemonSqueezy(el, product) {
    el.setAttribute("href", product.ls);
    el.setAttribute("target", "_self");
    el.removeAttribute("rel");
    el.classList.add("lemonsqueezy-button");

    var liveLabel = el.getAttribute("data-cta-label-live") || "Buy Now";
    setLabel(el, liveLabel);

    revealElement(el);
  }

  function setLabel(el, text) {
    var slot = el.querySelector("[data-cta-label]");
    if (slot) {
      slot.textContent = text;
    }
    // If no slot, the static HTML label remains. Caller can choose to use slots or not.
  }

  function hideElement(el) {
    el.style.display = "none";
    el.setAttribute("aria-hidden", "true");
    el.setAttribute("data-checkout-state", "hidden");
  }

  function revealElement(el) {
    el.style.removeProperty("display");
    el.removeAttribute("aria-hidden");
    el.setAttribute("data-checkout-state", "visible");
  }

  function manageLiteSections() {
    // [data-lite-section] wrappers default to style="display:none" in HTML so they
    // don't flash before JS runs. If any [data-checkout] inside becomes visible
    // (meaning that lite product went live on LS), un-hide the wrapper. If none
    // are visible, leave the wrapper hidden.
    var sections = document.querySelectorAll("[data-lite-section]");
    sections.forEach(function (section) {
      var visibleButtons = section.querySelectorAll(
        '[data-checkout][data-checkout-state="visible"]'
      );
      if (visibleButtons.length > 0) {
        section.style.removeProperty("display");
      } else {
        section.style.display = "none";
      }
    });
  }

  function loadLemonScript() {
    if (document.querySelector('script[src*="lemonsqueezy.com/js/lemon.js"]')) return;
    var s = document.createElement("script");
    s.src = "https://app.lemonsqueezy.com/js/lemon.js";
    s.defer = true;
    document.head.appendChild(s);
  }

  // Run on DOMContentLoaded, or immediately if DOM already parsed
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
