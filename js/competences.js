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

(function () {
  // Délai de fermeture sur les dropdowns principaux
  document.querySelectorAll('.navbar .nav-item.dropdown').forEach(item => {
    let t;
    item.addEventListener('mouseenter', () => { clearTimeout(t); item.classList.add('is-hovered'); });
    item.addEventListener('mouseleave', () => { t = setTimeout(() => item.classList.remove('is-hovered'), 200); });
  });

  // Délai de fermeture sur le sous-menu Ingénierie cognitive
  document.querySelectorAll('.navbar .dropdown-submenu').forEach(li => {
    let t;
    li.addEventListener('mouseenter', () => { clearTimeout(t); li.classList.add('is-open'); });
    li.addEventListener('mouseleave', () => { t = setTimeout(() => li.classList.remove('is-open'), 200); });
  });
})();
