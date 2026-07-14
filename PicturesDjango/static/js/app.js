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
    initImageLoading();
  });
})();
