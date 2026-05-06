/* ─────────────────────────────────────────────────────────────────
   MOBILE NAV — toggle behavior
   Adds a class to <body> when the hamburger is tapped. CSS handles
   the visual transition (drawer slide, hamburger → X). Closes the
   drawer on link click, ESC keypress, or backdrop tap.
   ───────────────────────────────────────────────────────────────── */
(function () {
  'use strict';

  function init() {
    var toggle = document.querySelector('.nav-toggle');
    if (!toggle) return;

    var body = document.body;
    var nav = document.querySelector('.site-nav');

    function open() {
      body.classList.add('nav-open');
      toggle.setAttribute('aria-expanded', 'true');
    }
    function close() {
      body.classList.remove('nav-open');
      toggle.setAttribute('aria-expanded', 'false');
    }
    function isOpen() {
      return body.classList.contains('nav-open');
    }

    toggle.addEventListener('click', function (e) {
      e.preventDefault();
      isOpen() ? close() : open();
    });

    // Close on any link click inside the drawer
    document.querySelectorAll('.site-nav .nav-links a').forEach(function (a) {
      a.addEventListener('click', close);
    });

    // Close on ESC
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && isOpen()) close();
    });

    // Close on resize past breakpoint (so the drawer state can't
    // get stuck if the user rotates or resizes the viewport)
    var mq = window.matchMedia('(min-width: 721px)');
    function handleMq(e) {
      if (e.matches && isOpen()) close();
    }
    if (mq.addEventListener) {
      mq.addEventListener('change', handleMq);
    } else if (mq.addListener) {
      mq.addListener(handleMq);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
