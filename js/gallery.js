/**
 * Product Gallery Lightbox
 * ========================
 * Wires the [data-gallery] thumbnail grid to the [data-lightbox] modal.
 * Click a thumb -> open lightbox with that image.
 * Keyboard: ESC = close, ArrowLeft = prev, ArrowRight = next.
 * Click outside the image, the close button, or backdrop = close.
 *
 * One gallery per page is expected. The script self-initializes on
 * DOMContentLoaded and is idempotent (safe to load twice).
 */
(function () {
  "use strict";

  function init() {
    var gallery = document.querySelector("[data-gallery]");
    var lightbox = document.querySelector("[data-lightbox]");
    if (!gallery || !lightbox) return;

    var thumbs = Array.prototype.slice.call(gallery.querySelectorAll(".gallery-thumb"));
    if (!thumbs.length) return;

    var img = lightbox.querySelector(".gallery-lightbox-image");
    var caption = lightbox.querySelector(".gallery-lightbox-caption");
    var counter = lightbox.querySelector(".gallery-lightbox-counter");
    var btnClose = lightbox.querySelector(".gallery-lightbox-close");
    var btnPrev = lightbox.querySelector(".gallery-lightbox-prev");
    var btnNext = lightbox.querySelector(".gallery-lightbox-next");

    var current = 0;
    var lastFocused = null;

    function show(index) {
      if (index < 0) index = thumbs.length - 1;
      if (index >= thumbs.length) index = 0;
      current = index;
      var t = thumbs[current];
      img.src = t.getAttribute("data-src");
      img.alt = t.getAttribute("data-caption") || "";
      if (caption) caption.textContent = t.getAttribute("data-caption") || "";
      if (counter) counter.textContent = (current + 1) + " / " + thumbs.length;
    }

    function open(index) {
      lastFocused = document.activeElement;
      show(index);
      lightbox.setAttribute("data-open", "true");
      document.body.style.overflow = "hidden";
      if (btnClose) btnClose.focus();
    }

    function close() {
      lightbox.setAttribute("data-open", "false");
      document.body.style.overflow = "";
      img.src = "";
      if (lastFocused && typeof lastFocused.focus === "function") {
        lastFocused.focus();
      }
    }

    thumbs.forEach(function (t, i) {
      t.addEventListener("click", function () { open(i); });
    });

    if (btnClose) btnClose.addEventListener("click", close);
    if (btnPrev) btnPrev.addEventListener("click", function () { show(current - 1); });
    if (btnNext) btnNext.addEventListener("click", function () { show(current + 1); });

    // Click on the dark backdrop (anywhere outside the inner) closes
    lightbox.addEventListener("click", function (e) {
      if (e.target === lightbox) close();
    });

    // Click on the image itself toggles closes (zoom-out)
    if (img) {
      img.addEventListener("click", function (e) {
        e.stopPropagation();
        close();
      });
    }

    document.addEventListener("keydown", function (e) {
      if (lightbox.getAttribute("data-open") !== "true") return;
      if (e.key === "Escape") { close(); }
      else if (e.key === "ArrowLeft") { show(current - 1); }
      else if (e.key === "ArrowRight") { show(current + 1); }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
