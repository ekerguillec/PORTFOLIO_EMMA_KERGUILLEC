(function () {
      const btns = document.querySelectorAll('.tool-chip-btn');

      function closeAll() {
        btns.forEach(b => {
          b.setAttribute('aria-expanded', 'false');
          b.closest('.tool-item').classList.remove('is-open');
        });
      }

      btns.forEach(btn => {
        const item = btn.closest('.tool-item');

        /* Focus clavier → affiche le tooltip */
        btn.addEventListener('focus', () => item.classList.add('is-focused'));
        btn.addEventListener('blur',  () => item.classList.remove('is-focused'));

        /* Clic → bascule ouvert/fermé */
        btn.addEventListener('click', () => {
          const isOpen = btn.getAttribute('aria-expanded') === 'true';
          closeAll();
          if (!isOpen) {
            btn.setAttribute('aria-expanded', 'true');
            item.classList.add('is-open');
          }
        });

        /* Souris qui quitte → ferme même si ouvert par clic */
        item.addEventListener('mouseleave', () => {
          btn.setAttribute('aria-expanded', 'false');
          item.classList.remove('is-open');
        });
      });

      /* Échap → ferme tout (WCAG 1.4.13) */
      document.addEventListener('keydown', e => {
        if (e.key === 'Escape') closeAll();
      });

      /* Clic en dehors → ferme tout */
      document.addEventListener('click', e => {
        if (!e.target.closest('.tool-item')) closeAll();
      });
    })();

// ── Scroll vers l'ancre initiale (cross-page) sans déclencher le verrou natif ──
(function () {
  var hash = window.__portfolioHash;
  if (!hash) return;
  delete window.__portfolioHash;

  document.addEventListener('DOMContentLoaded', function () {
    requestAnimationFrame(function () {
      requestAnimationFrame(function () {
        var target = document.getElementById(hash.slice(1));
        if (!target) return;
        var navH = parseInt(getComputedStyle(document.documentElement).scrollPaddingTop, 10) || 130;
        var top = target.getBoundingClientRect().top + window.pageYOffset - navH;
        window.scrollTo(0, Math.max(0, top));
        history.replaceState(null, '', hash);
      });
    });
  });
})();
