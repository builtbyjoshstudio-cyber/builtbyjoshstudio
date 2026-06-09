/* ─────────────────────────────────────────────────────────────────
   LITE YT — click-to-load YouTube facade
   On page load: NOTHING from YouTube/Google is requested. The markup
   carries only a self-hosted poster image + a <button>; the video ID
   lives in data-ytid (not a URL). Only when a .yt-facade-btn is
   activated do we build a privacy-enhanced youtube-nocookie.com iframe
   and swap it in. A native <button> gives keyboard (Enter/Space)
   activation for free.
   ───────────────────────────────────────────────────────────────── */
(function () {
  'use strict';

  function activate(facade) {
    var id = facade && facade.getAttribute('data-ytid');
    if (!id || facade.querySelector('iframe')) return;

    var iframe = document.createElement('iframe');
    iframe.src = 'https://www.youtube-nocookie.com/embed/' + encodeURIComponent(id) +
                 '?autoplay=1&rel=0&playsinline=1';
    iframe.title = facade.getAttribute('data-title') || 'YouTube video player';
    iframe.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
    iframe.setAttribute('allowfullscreen', '');
    iframe.setAttribute('referrerpolicy', 'strict-origin-when-cross-origin');

    while (facade.firstChild) facade.removeChild(facade.firstChild);
    facade.appendChild(iframe);
    iframe.focus();

    if (typeof gtag === 'function') {
      gtag('event', 'video_start', {
        video_provider: 'youtube',
        video_title: facade.getAttribute('data-title') || '',
        source_page: facade.getAttribute('data-source') || ''
      });
    }
  }

  document.addEventListener('click', function (e) {
    var btn = e.target.closest('.yt-facade-btn');
    if (btn) { e.preventDefault(); activate(btn.closest('.yt-facade')); }
  });
})();
