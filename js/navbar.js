(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', function () {

    // ── Hamburger toggle ──────────────────────────────────────────────────
    document.querySelectorAll('.navbar-toggler').forEach(function (toggler) {
      var targetId = toggler.getAttribute('aria-controls');
      var collapse = targetId
        ? document.getElementById(targetId)
        : toggler.closest('.navbar').querySelector('.navbar-collapse');
      if (!collapse) return;

      toggler.addEventListener('click', function (e) {
        e.stopPropagation();
        var isOpen = collapse.classList.toggle('nav-open');
        toggler.classList.toggle('is-open', isOpen);
        toggler.setAttribute('aria-expanded', String(isOpen));
        if (!isOpen) closeAllDropdowns();
      });
    });

    // ── Dropdown toggle (clic sur caret — mobile et tactile) ─────────────
    document.querySelectorAll('.nav-caret').forEach(function (caret) {
      caret.addEventListener('click', function (e) {
        e.stopPropagation();
        var item = caret.closest('.nav-item.dropdown');
        if (!item) return;
        var isOpen = item.classList.toggle('mobile-open');
        caret.setAttribute('aria-expanded', String(isOpen));
        // Fermer les autres dropdowns du même niveau
        var navbar = item.closest('.navbar');
        if (navbar) {
          navbar.querySelectorAll('.nav-item.dropdown').forEach(function (other) {
            if (other !== item) {
              other.classList.remove('mobile-open');
              var otherCaret = other.querySelector('.nav-caret');
              if (otherCaret) otherCaret.setAttribute('aria-expanded', 'false');
            }
          });
        }
      });
    });

    // ── Sous-menu Ingénierie cognitive (clic sur mobile) ─────────────────
    document.querySelectorAll('.has-submenu').forEach(function (link) {
      link.addEventListener('click', function (e) {
        var submenu = link.closest('.dropdown-submenu');
        if (!submenu) return;
        if (window.innerWidth <= 991) {
          e.preventDefault();
          submenu.classList.toggle('is-open');
        }
      });
    });

    // ── Fermeture au clic hors du navbar ─────────────────────────────────
    document.addEventListener('click', function (e) {
      if (!e.target.closest('.navbar')) {
        document.querySelectorAll('.navbar-collapse.nav-open').forEach(function (c) {
          c.classList.remove('nav-open');
          var t = c.closest('.navbar');
          if (t) {
            var tog = t.querySelector('.navbar-toggler');
            if (tog) { tog.classList.remove('is-open'); tog.setAttribute('aria-expanded', 'false'); }
          }
        });
        closeAllDropdowns();
      }
    });

    // ── Touche Échap ─────────────────────────────────────────────────────
    document.addEventListener('keydown', function (e) {
      if (e.key !== 'Escape') return;
      document.querySelectorAll('.navbar-collapse.nav-open').forEach(function (c) {
        c.classList.remove('nav-open');
        var t = c.closest('.navbar');
        if (t) {
          var tog = t.querySelector('.navbar-toggler');
          if (tog) { tog.classList.remove('is-open'); tog.setAttribute('aria-expanded', 'false'); }
        }
      });
      closeAllDropdowns();
    });

    // ── Fermer le menu mobile en cliquant un lien ─────────────────────────
    document.querySelectorAll('.navbar-collapse .nav-link').forEach(function (link) {
      link.addEventListener('click', function () {
        var collapse = link.closest('.navbar-collapse');
        if (collapse && window.innerWidth <= 991) {
          collapse.classList.remove('nav-open');
          var navbar = collapse.closest('.navbar');
          if (navbar) {
            var tog = navbar.querySelector('.navbar-toggler');
            if (tog) { tog.classList.remove('is-open'); tog.setAttribute('aria-expanded', 'false'); }
          }
        }
      });
    });
  });

  function closeAllDropdowns() {
    document.querySelectorAll('.nav-item.dropdown.mobile-open').forEach(function (item) {
      item.classList.remove('mobile-open');
      var caret = item.querySelector('.nav-caret');
      if (caret) caret.setAttribute('aria-expanded', 'false');
    });
    document.querySelectorAll('.dropdown-submenu.is-open').forEach(function (sub) {
      sub.classList.remove('is-open');
    });
  }
})();
