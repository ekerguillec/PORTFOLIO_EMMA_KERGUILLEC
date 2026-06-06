/* ============================================================
   Gestion du thème clair / sombre
   ============================================================ */
(function () {
  const KEY   = 'portfolio-theme';
  const html  = document.documentElement;

  /* ── Préférence initiale ── */
  function getStored() {
    return localStorage.getItem(KEY);
  }

  function getDefault() {
    return window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
  }

  function currentTheme() {
    return html.classList.contains('light-mode') ? 'light' : 'dark';
  }

  /* ── Application du thème ── */
  function applyTheme(theme) {
    if (theme === 'light') {
      html.classList.add('light-mode');
    } else {
      html.classList.remove('light-mode');
    }
    localStorage.setItem(KEY, theme);
    updateButtons(theme);
  }

  /* ── Mise à jour des icônes ── */
  function updateButtons(theme) {
    document.querySelectorAll('.theme-toggle').forEach(function (btn) {
      var moon = btn.querySelector('.icon-moon');
      var sun  = btn.querySelector('.icon-sun');
      if (theme === 'light') {
        /* Mode clair actif → montrer lune (cliquer = aller en sombre) */
        if (moon) moon.style.display = 'block';
        if (sun)  sun.style.display  = 'none';
        btn.setAttribute('aria-label', 'Passer en mode sombre');
      } else {
        /* Mode sombre actif → montrer lune aussi (cliquer = aller en clair) */
        if (moon) moon.style.display = 'block';
        if (sun)  sun.style.display  = 'none';
        btn.setAttribute('aria-label', 'Passer en mode clair');
      }
    });
  }

  /* ── Initialisation DOM ── */
  document.addEventListener('DOMContentLoaded', function () {
    /* Appliquer le thème stocké (au cas où le script inline n'était pas là) */
    var stored = getStored() || getDefault();
    applyTheme(stored);

    /* Brancher le clic sur chaque bouton */
    document.querySelectorAll('.theme-toggle').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var next = currentTheme() === 'light' ? 'dark' : 'light';
        applyTheme(next);
      });
    });
  });

  /* ── Réagir aux changements système ── */
  window.matchMedia('(prefers-color-scheme: light)').addEventListener('change', function (e) {
    if (!getStored()) {
      applyTheme(e.matches ? 'light' : 'dark');
    }
  });
})();
