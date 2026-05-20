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

  // 2 + 3. Lemon Squeezy checkout-open and purchase-complete
  // (single LemonSqueezy.Event listener, branched by event type)
  window.addEventListener('LemonSqueezy.Event', function (e) {
    if (!e.detail) return;
    if (typeof gtag !== 'function') return;
    if (e.detail.event === 'Checkout.ViewLoaded') {
      gtag('event', 'lemonsqueezy_checkout_open', {
        page_path: window.location.pathname
      });
    } else if (e.detail.event === 'Checkout.Success') {
      gtag('event', 'lemonsqueezy_purchase', {
        page_path: window.location.pathname,
        product_name: e.detail.data?.order?.data?.attributes?.first_order_item?.product_name || 'unknown',
        value: e.detail.data?.order?.data?.attributes?.total_usd || 0
      });
    }
  });
})();
