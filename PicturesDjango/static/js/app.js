(function () {
  "use strict";

  function normalize(value) {
    return (value || "")
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLowerCase()
      .trim();
  }

  function initFilters() {
    document.querySelectorAll("[data-filter-input]").forEach(function (input) {
      var selector = input.getAttribute("data-filter-target");
      var target = selector ? document.querySelector(selector) : null;
      if (!target) return;

      var emptySelector = input.getAttribute("data-empty-target");
      var counterSelector = input.getAttribute("data-counter-target");
      var emptyState = emptySelector ? document.querySelector(emptySelector) : null;
      var counter = counterSelector ? document.querySelector(counterSelector) : null;

      function applyFilter() {
        var query = normalize(input.value);
        var visibleCount = 0;
        target.querySelectorAll("[data-filter-item]").forEach(function (item) {
          var haystack = normalize(item.getAttribute("data-filter-value") || item.textContent);
          var visible = !query || haystack.indexOf(query) !== -1;
          item.hidden = !visible;
          if (visible) visibleCount += 1;
        });
        if (emptyState) emptyState.hidden = visibleCount !== 0;
        if (counter) counter.textContent = visibleCount;
      }

      input.addEventListener("input", applyFilter);
      applyFilter();
    });
  }

  function initDensityControls() {
    document.querySelectorAll("[data-density-group]").forEach(function (group) {
      var selector = group.getAttribute("data-density-target");
      var grid = selector ? document.querySelector(selector) : null;
      if (!grid) return;

      var storageKey = "pictures-density";
      var savedDensity = localStorage.getItem(storageKey) || "comfortable";

      function setDensity(density) {
        grid.setAttribute("data-density", density);
        group.querySelectorAll("[data-density]").forEach(function (button) {
          var active = button.getAttribute("data-density") === density;
          button.classList.toggle("is-active", active);
          button.setAttribute("aria-pressed", active ? "true" : "false");
        });
        localStorage.setItem(storageKey, density);
      }

      group.querySelectorAll("[data-density]").forEach(function (button) {
        button.addEventListener("click", function () {
          setDensity(button.getAttribute("data-density"));
        });
      });
      setDensity(savedDensity);
    });
  }

  function initGallery() {
    var gallery = document.querySelector("[data-gallery]");
    if (!gallery) return;

    var previous = gallery.querySelector("[data-gallery-prev]");
    var next = gallery.querySelector("[data-gallery-next]");
    var canvas = gallery.querySelector("[data-gallery-canvas]");
    var panelToggle = gallery.querySelector("[data-panel-toggle]");
    var panelClose = gallery.querySelector("[data-panel-close]");

    document.addEventListener("keydown", function (event) {
      if (event.target && /input|textarea|select/i.test(event.target.tagName)) return;
      if (event.key === "ArrowLeft" && previous) {
        event.preventDefault();
        previous.click();
      } else if (event.key === "ArrowRight" && next) {
        event.preventDefault();
        next.click();
      } else if (event.key === "i" && panelToggle) {
        event.preventDefault();
        panelToggle.click();
      }
    });

    if (canvas) {
      var touchStartX = null;
      canvas.addEventListener("touchstart", function (event) {
        touchStartX = event.changedTouches[0].clientX;
      }, { passive: true });
      canvas.addEventListener("touchend", function (event) {
        if (touchStartX === null) return;
        var delta = event.changedTouches[0].clientX - touchStartX;
        touchStartX = null;
        if (Math.abs(delta) < 55) return;
        if (delta > 0 && previous) previous.click();
        if (delta < 0 && next) next.click();
      }, { passive: true });
    }

    function setPanel(open) {
      if (window.matchMedia("(max-width: 991.98px)").matches) {
        gallery.classList.toggle("details-open", open);
      } else {
        gallery.classList.toggle("details-hidden", !open);
      }
      if (panelToggle) panelToggle.setAttribute("aria-expanded", open ? "true" : "false");
    }

    if (panelToggle) {
      panelToggle.addEventListener("click", function () {
        var open = window.matchMedia("(max-width: 991.98px)").matches
          ? !gallery.classList.contains("details-open")
          : gallery.classList.contains("details-hidden");
        setPanel(open);
      });
    }
    if (panelClose) panelClose.addEventListener("click", function () { setPanel(false); });
  }

  function initEditPanels() {
    document.querySelectorAll("[data-edit-toggle]").forEach(function (button) {
      var selector = button.getAttribute("data-edit-toggle");
      var panel = selector ? document.querySelector(selector) : null;
      if (!panel) return;
      button.addEventListener("click", function () {
        var open = panel.hasAttribute("hidden");
        panel.toggleAttribute("hidden", !open);
        button.setAttribute("aria-expanded", open ? "true" : "false");
        if (open) {
          var field = panel.querySelector("input, textarea, select");
          if (field) field.focus();
        }
      });
    });
  }

  function initPhotoShare() {
    // HTTP : le lien <a target="_blank"> ouvre la photo sans JS.
    // HTTPS : prefetch + share() synchrone au clic (Android invalide le geste après fetch).
    if (!window.isSecureContext || typeof navigator.share !== "function") {
      return;
    }

    var shareCache = new WeakMap();

    function getCacheEntry(link) {
      var entry = shareCache.get(link);
      if (!entry) {
        entry = {};
        shareCache.set(link, entry);
      }
      return entry;
    }

    function buildFile(link, blob) {
      var filename = link.getAttribute("data-share-filename") || "photo.jpg";
      return new File([blob], filename, { type: blob.type || "image/jpeg" });
    }

    function prefetchShareAsset(link) {
      var entry = getCacheEntry(link);
      if (entry.file || entry.loading) {
        return entry.promise;
      }

      entry.loading = true;
      entry.promise = fetch(link.href, { credentials: "same-origin" })
        .then(function (response) {
          if (!response.ok) throw new Error("Image unavailable");
          return response.blob();
        })
        .then(function (blob) {
          entry.blob = blob;
          entry.file = buildFile(link, blob);
          return entry;
        })
        .catch(function () {
          return entry;
        })
        .finally(function () {
          entry.loading = false;
        });
      return entry.promise;
    }

    function sharePhoto(link) {
      var url = link.href;
      var title = link.getAttribute("data-share-title") || "";
      var entry = getCacheEntry(link);

      link.setAttribute("aria-busy", "true");

      function finish() {
        link.removeAttribute("aria-busy");
      }

      function fallback() {
        window.open(url, "_blank", "noopener,noreferrer");
      }

      if (entry.file) {
        navigator.share({ files: [entry.file], title: title })
          .catch(function (error) {
            if (error && error.name === "AbortError") return;
            return navigator.share({ title: title, url: url }).catch(fallback);
          })
          .finally(finish);
        return;
      }

      navigator.share({ title: title, url: url })
        .catch(function (error) {
          if (error && error.name === "AbortError") return;
          fallback();
        })
        .finally(finish);
    }

    function prefetchFromVisibleImage(link) {
      var root = link.closest("[data-gallery], .photo-detail-layout");
      var image = root ? root.querySelector(".viewer-image, .detail-media img") : null;
      if (!image || !image.complete || !image.naturalWidth) return;

      var entry = getCacheEntry(link);
      if (entry.file || entry.loading) return;

      entry.loading = true;
      entry.promise = fetch(image.currentSrc || image.src, { credentials: "same-origin" })
        .then(function (response) {
          if (!response.ok) throw new Error("Image unavailable");
          return response.blob();
        })
        .then(function (blob) {
          entry.blob = blob;
          entry.file = buildFile(link, blob);
          return entry;
        })
        .catch(function () {
          return prefetchShareAsset(link);
        })
        .finally(function () {
          entry.loading = false;
        });
    }

    document.querySelectorAll("a[data-share-photo]").forEach(function (link) {
      prefetchShareAsset(link);

      var root = link.closest("[data-gallery], .photo-detail-layout");
      var image = root ? root.querySelector(".viewer-image, .detail-media img") : null;
      if (image) {
        if (image.complete) prefetchFromVisibleImage(link);
        else image.addEventListener("load", function () { prefetchFromVisibleImage(link); }, { once: true });
      }

      link.addEventListener("pointerdown", function () {
        prefetchShareAsset(link);
        prefetchFromVisibleImage(link);
      }, { passive: true });

      link.addEventListener("click", function (event) {
        event.preventDefault();
        sharePhoto(link);
      });
    });
  }

  function copyText(text) {
    if (navigator.clipboard && typeof navigator.clipboard.writeText === "function") {
      return navigator.clipboard.writeText(text);
    }

    return new Promise(function (resolve, reject) {
      var field = document.createElement("textarea");
      field.value = text;
      field.setAttribute("readonly", "");
      field.style.position = "fixed";
      field.style.left = "-9999px";
      document.body.appendChild(field);
      field.select();
      try {
        if (!document.execCommand("copy")) {
          throw new Error("copy failed");
        }
        resolve();
      } catch (error) {
        reject(error);
      } finally {
        document.body.removeChild(field);
      }
    });
  }

  function initCopyButtons() {
    document.querySelectorAll("[data-copy]").forEach(function (button) {
      var idleLabel = button.getAttribute("data-copy-label") || button.getAttribute("aria-label") || "";
      var copiedLabel = button.getAttribute("data-copied-label") || "";
      var resetTimer = null;

      function markCopied() {
        button.classList.add("is-copied");
        if (copiedLabel) {
          button.setAttribute("aria-label", copiedLabel);
          button.setAttribute("title", copiedLabel);
        }
        window.clearTimeout(resetTimer);
        resetTimer = window.setTimeout(function () {
          button.classList.remove("is-copied");
          if (idleLabel) {
            button.setAttribute("aria-label", idleLabel);
            button.setAttribute("title", idleLabel);
          }
        }, 1600);
      }

      button.addEventListener("click", function () {
        var text = button.getAttribute("data-copy") || "";
        if (!text) return;
        copyText(text).then(markCopied).catch(function () {});
      });
    });
  }

  function initImageLoading() {
    document.querySelectorAll("img").forEach(function (image) {
      if (image.complete) image.classList.add("is-loaded");
      image.addEventListener("load", function () { image.classList.add("is-loaded"); });
      image.addEventListener("error", function () {
        var media = image.closest("[data-media]");
        if (media) media.classList.add("media-fallback");
      });
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    initFilters();
    initDensityControls();
    initGallery();
    initEditPanels();
    initPhotoShare();
    initCopyButtons();
    initImageLoading();
  });
})();
