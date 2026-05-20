// GA4 event listeners for builtbyjoshstudio.com
// Loaded as a separate shared block; does not modify the existing gtag init snippet.

(function () {
  // 1. Etsy outbound clicks
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

  // 2 + 3. Lemon Squeezy: checkout overlay opened + purchase complete.
  // LS uses the documented LemonSqueezy.Setup({ eventHandler }) callback API
  // (NOT a DOM event). The Setup call lives in /js/checkout.js, which forwards
  // every LS event to this handler. Payload shape: { event: 'Checkout.Success',
  // data: {...} } — accessed via event.event / event.data, not e.detail.
  //
  // Mapping (per Nuxt's LS registry typings, which mirror the LS API):
  //   Checkout.ViewCart  -> lemonsqueezy_checkout_open  (overlay opened on cart view)
  //   Checkout.Success   -> lemonsqueezy_purchase       (purchase completed)
  // Documented LS events not currently mapped: GA.ViewCart, PaymentMethodUpdate.*
  window.__ga4LemonSqueezyHandler = function (event) {
    if (!event || typeof gtag !== 'function') return;
    if (event.event === 'Checkout.ViewCart') {
      gtag('event', 'lemonsqueezy_checkout_open', {
        page_path: window.location.pathname
      });
    } else if (event.event === 'Checkout.Success') {
      gtag('event', 'lemonsqueezy_purchase', {
        page_path: window.location.pathname,
        product_name: event.data?.order?.data?.attributes?.first_order_item?.product_name || 'unknown',
        value: event.data?.order?.data?.attributes?.total_usd || 0
      });
    }
  };
})();
